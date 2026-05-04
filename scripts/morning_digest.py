#!/usr/bin/env python3
"""
Morning digest: fetches Gmail + Calendar via Google APIs, asks Claude to
rank the top-10 action items for the day, and sends the result as an email.

Required environment variables:
  ANTHROPIC_API_KEY       - Anthropic API key
  GOOGLE_CLIENT_ID        - OAuth2 client ID from Google Cloud Console
  GOOGLE_CLIENT_SECRET    - OAuth2 client secret
  GOOGLE_REFRESH_TOKEN    - Refresh token (run setup_google_auth.py once)
  OWNER_EMAIL             - Address to send the digest to (default: auto-detected)
"""

import base64
import datetime
import json
import os
import re
import sys
import zoneinfo
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import anthropic
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ── Constants ────────────────────────────────────────────────────────────────

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.readonly",
]

MOUNTAIN_TZ = zoneinfo.ZoneInfo("America/Denver")
MODEL = "claude-sonnet-4-6"

# ── Google auth ───────────────────────────────────────────────────────────────


def get_google_creds() -> Credentials:
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


# ── Gmail ─────────────────────────────────────────────────────────────────────


def fetch_emails(gmail, max_results: int = 75) -> list[dict]:
    """Return message metadata + snippets from the last 7 days."""
    query = (
        "newer_than:7d "
        "-category:promotions -category:social -category:updates "
        "-from:noreply@ -from:no-reply@ -from:donotreply@ "
        "-from:notifications@"
    )
    response = gmail.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()

    messages = response.get("messages", [])
    emails: list[dict] = []

    for msg in messages:
        detail = gmail.users().messages().get(
            userId="me",
            id=msg["id"],
            format="metadata",
            metadataHeaders=["Subject", "From", "To", "Cc", "Date"],
        ).execute()

        headers = {
            h["name"]: h["value"]
            for h in detail.get("payload", {}).get("headers", [])
        }
        sender = headers.get("From", "")

        # Skip obvious automated senders not caught by the query
        if re.search(r"list-unsubscribe|@bounce\.|mailer-daemon", sender, re.I):
            continue

        emails.append(
            {
                "id": msg["id"],
                "date": headers.get("Date", ""),
                "from": sender,
                "to": headers.get("To", ""),
                "cc": headers.get("Cc", ""),
                "subject": headers.get("Subject", "(no subject)"),
                "snippet": detail.get("snippet", ""),
            }
        )

    return emails


def detect_owner_email(emails: list[dict]) -> str:
    """Find the most common 'To' address — that's almost certainly the owner."""
    from collections import Counter

    counter: Counter = Counter()
    for e in emails:
        for addr in re.findall(r"[\w.+-]+@[\w.-]+\.\w+", e.get("to", "")):
            counter[addr.lower()] += 1

    if counter:
        return counter.most_common(1)[0][0]
    return os.environ.get("OWNER_EMAIL", "")


# ── Calendar ──────────────────────────────────────────────────────────────────


def fetch_nonrecurring_events(calendar, days_ahead: int = 14) -> list[dict]:
    """Return one-time events for the next `days_ahead` days (Mountain Time)."""
    now_mt = datetime.datetime.now(tz=MOUNTAIN_TZ)
    start = now_mt.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + datetime.timedelta(days=days_ahead)

    response = calendar.events().list(
        calendarId="primary",
        timeMin=start.isoformat(),
        timeMax=end.isoformat(),
        maxResults=100,
        singleEvents=True,
        orderBy="startTime",
        timeZone="America/Denver",
    ).execute()

    events: list[dict] = []
    for ev in response.get("items", []):
        # Drop recurring events — they are routine, not out-of-the-ordinary
        if "recurringEventId" in ev or "recurrence" in ev:
            continue

        start_raw = ev.get("start", {})
        end_raw = ev.get("end", {})
        events.append(
            {
                "summary": ev.get("summary", "(no title)"),
                "start": start_raw.get("dateTime", start_raw.get("date", "")),
                "end": end_raw.get("dateTime", end_raw.get("date", "")),
                "location": ev.get("location", ""),
                "description": (ev.get("description", "") or "")[:300],
                "organizer": ev.get("organizer", {}).get("email", ""),
            }
        )

    return events


# ── Claude ────────────────────────────────────────────────────────────────────

_SYSTEM = """\
You are an expert personal assistant writing a concise morning briefing email.
Your job is to read the raw email and calendar data provided and produce a
top-10 action-item list plus a section for out-of-the-ordinary calendar events.

Rules:
- Rank items by urgency: security/financial alerts first, then required actions,
  then upcoming events to prepare for.
- Skip routine automated notifications (bank statements, app updates, marketing).
- Use concrete, specific action language ("Reply to X confirming Y", not "Follow up").
- Output ONLY the inner HTML body — no <html>, <head>, or <body> tags.
- Use the colour scheme described in the user prompt.
"""


def generate_digest_html(emails: list[dict], events: list[dict], today_str: str) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    user_prompt = f"""Today is {today_str} (Mountain Time).

## Emails from the last 7 days (JSON):
```json
{json.dumps(emails, indent=2)}
```

## Upcoming one-time calendar events (next 14 days, JSON):
```json
{json.dumps(events, indent=2)}
```

Generate the digest HTML body with two sections:

### Section 1 — Top 10 Action Items
Produce exactly 10 numbered items. Each item is a <div> styled as:
  style="margin-bottom:14px; padding:12px; background:{bg}; border-left:4px solid {border};"
Colour guide:
  - Urgent (security/health/financial anomaly): bg=#fde8e8, border=#e74c3c
  - Important action required:                  bg=#fff3cd, border=#e67e22
  - Action needed (lower urgency):              bg=#f0f7ff, border=#4A90D9
  - Upcoming event to plan for:                 bg=#e8f8e8, border=#27AE60

Inside each div:
  <p style="margin:0"><strong>#N — {emoji} {Title}</strong></p>
  <p style="margin:6px 0 0 0;">{1–2 sentence description with the specific action}</p>

### Section 2 — Out-of-Ordinary Calendar Events
A <h3> heading, then a <div> per event styled bg=#f0f7ff, border=#27AE60:
  <p style="margin:0"><strong>{Day, Date — Start–End MT}</strong> — {Event Title}</p>
  <p style="margin:4px 0 0 18px; color:#555;">📍 {location if any} / {brief note}</p>

If there are no one-time events, output:
  <p><em>No out-of-the-ordinary calendar events in the next 14 days.</em></p>
"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=_SYSTEM,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return response.content[0].text


# ── Email sending ─────────────────────────────────────────────────────────────


def send_digest(gmail, owner_email: str, today_str: str, inner_html: str) -> None:
    subject = f"Daily Action Summary — {today_str}"

    full_html = f"""<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif; max-width:700px; margin:auto; color:#222;">
  <h2 style="border-bottom:2px solid #4A90D9; padding-bottom:8px;">
    Daily Action Summary &mdash; {today_str}
  </h2>
  <p style="color:#666; font-size:0.9em;">
    Generated at 5:00 AM Mountain Time &mdash; top 10 items from the past 7 days
  </p>
  {inner_html}
  <hr style="margin-top:32px;"/>
  <p style="font-size:0.8em; color:#999;">Automated daily digest &mdash; ClaudeRoutines</p>
</body>
</html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = owner_email
    msg["To"] = owner_email
    msg.attach(MIMEText(full_html, "html"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    gmail.users().messages().send(userId="me", body={"raw": raw}).execute()
    print(f"Digest sent to {owner_email}: {subject}")


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    for var in ("ANTHROPIC_API_KEY", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REFRESH_TOKEN"):
        if not os.environ.get(var):
            sys.exit(f"Error: environment variable {var!r} is not set.")

    creds = get_google_creds()
    gmail = build("gmail", "v1", credentials=creds)
    calendar = build("calendar", "v3", credentials=creds)

    emails = fetch_emails(gmail)
    events = fetch_nonrecurring_events(calendar)

    owner_email = os.environ.get("OWNER_EMAIL") or detect_owner_email(emails)
    if not owner_email:
        sys.exit("Error: could not determine owner email. Set OWNER_EMAIL.")

    now_mt = datetime.datetime.now(tz=MOUNTAIN_TZ)
    today_str = now_mt.strftime("%A, %B %-d, %Y")

    print(f"Fetched {len(emails)} emails and {len(events)} one-time events.")
    inner_html = generate_digest_html(emails, events, today_str)
    send_digest(gmail, owner_email, today_str, inner_html)


if __name__ == "__main__":
    main()
