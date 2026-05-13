#!/usr/bin/env python3
"""
Morning Digest — fetches Gmail + Google Calendar, generates a top-10 summary
via Claude API, and delivers it to the inbox as an unread draft.

Required environment variables (or entries in ~/.claude/morning_digest.env):
  ANTHROPIC_API_KEY        — Claude API key
  GOOGLE_CLIENT_ID         — OAuth2 client ID
  GOOGLE_CLIENT_SECRET     — OAuth2 client secret
  GOOGLE_REFRESH_TOKEN     — long-lived refresh token (see setup.py)
  DIGEST_TO_EMAIL          — recipient address (e.g. richardlwells@gmail.com)

Optional:
  CLAUDE_MODEL             — defaults to claude-sonnet-4-6
  TIMEZONE_OFFSET          — e.g. "-06:00" for MDT (default), "-07:00" for MST
"""

import base64
import json
import os
import sys
import textwrap
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------

def _load_env_file(path: str) -> None:
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except FileNotFoundError:
        pass


def _require(name: str) -> str:
    v = os.environ.get(name, "").strip()
    if not v:
        sys.exit(f"[morning_digest] Missing required env var: {name}\n"
                 f"Set it in ~/.claude/morning_digest.env or export it before running.")
    return v


# ---------------------------------------------------------------------------
# Google OAuth2 — exchange refresh token for access token (no heavy deps)
# ---------------------------------------------------------------------------

def _google_access_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["access_token"]


# ---------------------------------------------------------------------------
# Minimal Google API helpers (urllib only — no google-auth library needed)
# ---------------------------------------------------------------------------

def _gapi_get(url: str, token: str, params: dict | None = None) -> dict:
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def _gapi_post(url: str, token: str, body: dict) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


# ---------------------------------------------------------------------------
# Gmail helpers
# ---------------------------------------------------------------------------

def _fetch_threads(token: str, query: str, max_results: int = 50) -> list[dict]:
    """Return a flat list of thread dicts (id + messages[])."""
    threads = []
    page_token = None
    base = "https://gmail.googleapis.com/gmail/v1/users/me/threads"
    while True:
        params: dict = {"q": query, "maxResults": min(max_results, 50)}
        if page_token:
            params["pageToken"] = page_token
        resp = _gapi_get(base, token, params)
        for t in resp.get("threads", []):
            # fetch full thread to get sender / subject / snippet
            detail = _gapi_get(f"{base}/{t['id']}", token,
                               {"format": "metadata",
                                "metadataHeaders": ["Subject", "From", "To", "Date"]})
            threads.append(detail)
            if len(threads) >= max_results:
                return threads
        page_token = resp.get("nextPageToken")
        if not page_token or len(threads) >= max_results:
            break
    return threads


def _extract_header(message: dict, name: str) -> str:
    for h in message.get("payload", {}).get("headers", []):
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def _thread_summary(thread: dict) -> dict:
    """Return a lean dict describing the thread."""
    msgs = thread.get("messages", [])
    if not msgs:
        return {}
    first = msgs[0]
    last = msgs[-1]
    return {
        "subject": _extract_header(first, "Subject"),
        "from": _extract_header(last, "From"),
        "date": _extract_header(last, "Date"),
        "snippet": last.get("snippet", ""),
        "message_count": len(msgs),
    }


def _create_gmail_draft(token: str, to: str, subject: str, html_body: str) -> str:
    """Create a Gmail draft and return its message ID."""
    msg = MIMEMultipart("alternative")
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    resp = _gapi_post(
        "https://gmail.googleapis.com/gmail/v1/users/me/drafts",
        token,
        {"message": {"raw": raw}},
    )
    return resp.get("message", {}).get("id", resp.get("id", ""))


def _move_draft_to_inbox(token: str, message_id: str) -> None:
    """Add INBOX + UNREAD labels so the digest appears as a new email."""
    _gapi_post(
        f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}/modify",
        token,
        {"addLabelIds": ["INBOX", "UNREAD"]},
    )


# ---------------------------------------------------------------------------
# Calendar helpers
# ---------------------------------------------------------------------------

def _fetch_nonrecurring_events(token: str, tz_offset: str) -> list[dict]:
    """Return today's non-recurring calendar events."""
    today = datetime.now(timezone(timedelta(hours=_offset_hours(tz_offset))))
    start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end = today.replace(hour=23, minute=59, second=59, microsecond=0)

    iso_start = start.isoformat()
    iso_end = end.isoformat()

    resp = _gapi_get(
        "https://www.googleapis.com/calendar/v3/calendars/primary/events",
        token,
        {
            "timeMin": iso_start,
            "timeMax": iso_end,
            "singleEvents": "true",
            "orderBy": "startTime",
            "maxResults": 100,
            "timeZone": "America/Denver",
        },
    )
    events = []
    for ev in resp.get("items", []):
        if ev.get("recurringEventId") or ev.get("recurrence"):
            continue
        events.append(ev)
    return events


def _offset_hours(tz_offset: str) -> float:
    """Convert e.g. '-06:00' to -6.0."""
    sign = 1 if tz_offset[0] == "+" else -1
    parts = tz_offset.lstrip("+-").split(":")
    return sign * (int(parts[0]) + int(parts[1]) / 60)


def _fmt_event_time(ev: dict, tz_offset: str) -> str:
    start = ev.get("start", {})
    end = ev.get("end", {})
    if "dateTime" in start:
        s = datetime.fromisoformat(start["dateTime"])
        e = datetime.fromisoformat(end["dateTime"])
        return f"{s.strftime('%-I:%M %p')} – {e.strftime('%-I:%M %p')} MT"
    return "All day"


# ---------------------------------------------------------------------------
# Claude API — generate top-10 digest
# ---------------------------------------------------------------------------

def _call_claude(api_key: str, model: str, prompt: str) -> str:
    import requests  # available in this environment
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


def _build_prompt(threads: list[dict], events: list[dict],
                  today_str: str, tz_offset: str) -> str:
    thread_text = ""
    for i, t in enumerate(threads):
        s = _thread_summary(t)
        if not s:
            continue
        thread_text += (
            f"\n[{i+1}] From: {s['from']}\n"
            f"     Subject: {s['subject']}\n"
            f"     Date: {s['date']}\n"
            f"     Snippet: {s['snippet']}\n"
        )

    event_text = ""
    for ev in events:
        event_text += (
            f"\n- {_fmt_event_time(ev, tz_offset)}: {ev.get('summary','(no title)')}"
        )
        if ev.get("location"):
            event_text += f"\n  Location: {ev['location']}"
        if ev.get("description"):
            event_text += f"\n  Desc: {ev['description'][:200]}"
    if not event_text:
        event_text = "\n(none)"

    return textwrap.dedent(f"""
        You are a personal assistant generating a morning briefing email.
        Today is {today_str} (Mountain Time).

        ## Emails received in the last 24 hours
        {thread_text or "(none)"}

        ## Non-recurring calendar events today
        {event_text}

        ## Your task
        Produce a **Top 10 Action Items** list. Rules:
        - Rank by urgency: deadlines today > financial alerts > requests awaiting your reply >
          upcoming events requiring prep > lower-priority items.
        - Each item must be a concrete action ("Reply to X about Y", "Approve Z transaction
          at [site]"), not a vague note.
        - Include up to 3 notable non-recurring calendar items at the end if they are
          genuinely out of the ordinary (one-time events, unusual timing, etc.).
        - Format the output as HTML (no outer <html>/<body> tags; just the inner content).
          Use numbered list tags <ol><li>...</li></ol>.
          Bold the first phrase of each item with <strong>.
          Use a colored section divider <h3> to separate urgency tiers.
        - Do NOT include marketing emails, newsletters, or purely automated notifications
          (e.g. credit card cashback credits) unless they require action.
        - Keep the total email under 600 words.
    """)


# ---------------------------------------------------------------------------
# HTML email template
# ---------------------------------------------------------------------------

def _wrap_html(body: str, today_str: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">
<h2 style="border-bottom: 2px solid #4A90D9; padding-bottom: 8px;">
  📋 Daily Briefing &mdash; {today_str}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time</p>
{body}
<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines · <a href="https://github.com/rwells71/clauderoutines">rwells71/clauderoutines</a></p>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # Load optional env file
    _load_env_file(os.path.expanduser("~/.claude/morning_digest.env"))

    api_key = _require("ANTHROPIC_API_KEY")
    client_id = _require("GOOGLE_CLIENT_ID")
    client_secret = _require("GOOGLE_CLIENT_SECRET")
    refresh_token = _require("GOOGLE_REFRESH_TOKEN")
    to_email = _require("DIGEST_TO_EMAIL")
    model = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
    tz_offset = os.environ.get("TIMEZONE_OFFSET", "-06:00")  # MDT default

    print("[morning_digest] Obtaining Google access token…")
    gtoken = _google_access_token(client_id, client_secret, refresh_token)

    print("[morning_digest] Fetching emails…")
    threads = _fetch_threads(
        gtoken,
        "newer_than:1d -category:promotions -category:social -in:sent -in:draft",
        max_results=50,
    )
    print(f"[morning_digest]   {len(threads)} threads fetched.")

    print("[morning_digest] Fetching calendar events…")
    events = _fetch_nonrecurring_events(gtoken, tz_offset)
    print(f"[morning_digest]   {len(events)} non-recurring events today.")

    today_local = datetime.now(timezone(timedelta(hours=_offset_hours(tz_offset))))
    today_str = today_local.strftime("%A, %B %-d, %Y")

    print("[morning_digest] Calling Claude to generate digest…")
    prompt = _build_prompt(threads, events, today_str, tz_offset)
    digest_html = _call_claude(api_key, model, prompt)

    full_html = _wrap_html(digest_html, today_str)
    subject = f"📋 Daily Briefing — {today_str}"

    print("[morning_digest] Creating Gmail draft…")
    msg_id = _create_gmail_draft(gtoken, to_email, subject, full_html)

    if msg_id:
        print(f"[morning_digest] Draft created (id={msg_id}). Moving to Inbox…")
        _move_draft_to_inbox(gtoken, msg_id)
        print("[morning_digest] Done — digest delivered to inbox.")
    else:
        print("[morning_digest] Warning: draft created but no message ID returned.")


if __name__ == "__main__":
    main()
