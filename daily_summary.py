#!/usr/bin/env python3
"""
Daily Morning Digest
Fetches Gmail + Google Calendar data, generates a top-10 action summary
via the Claude API, and delivers the result directly to the inbox.

Required environment variables:
  ANTHROPIC_API_KEY       - Anthropic API key
  GOOGLE_CREDENTIALS_JSON - base64-encoded OAuth2 client credentials JSON
  GOOGLE_TOKEN_JSON       - base64-encoded OAuth2 token JSON (includes refresh token)
  OWNER_EMAIL             - recipient address (e.g. richardlwells@gmail.com)
"""

import base64
import json
import os
from datetime import datetime, timedelta

import anthropic
import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

MOUNTAIN_TZ = pytz.timezone("America/Denver")
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.insert",
    "https://www.googleapis.com/auth/calendar.readonly",
]
SKIP_SENDERS = ("noreply", "no-reply", "donotreply", "notifications@", "mailer-daemon")
MAX_THREADS = 40


# ── Google auth ──────────────────────────────────────────────────────────────

def get_google_creds() -> Credentials:
    token_data = json.loads(base64.b64decode(os.environ["GOOGLE_TOKEN_JSON"]))
    client_data = json.loads(base64.b64decode(os.environ["GOOGLE_CREDENTIALS_JSON"]))
    installed = client_data.get("installed") or client_data.get("web", {})

    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data["refresh_token"],
        token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=installed["client_id"],
        client_secret=installed["client_secret"],
        scopes=SCOPES,
    )
    if creds.expired:
        creds.refresh(Request())
    return creds


# ── Gmail helpers ─────────────────────────────────────────────────────────────

def _header(msg: dict, name: str) -> str:
    for h in msg.get("payload", {}).get("headers", []):
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def fetch_emails(gmail, days: int = 7) -> list[dict]:
    query = (
        f"newer_than:{days}d "
        "-category:promotions -category:social -in:draft -in:sent"
    )
    result = gmail.users().threads().list(userId="me", q=query, maxResults=MAX_THREADS).execute()
    raw_threads = result.get("threads", [])

    details = []
    for t in raw_threads:
        detail = gmail.users().threads().get(
            userId="me",
            id=t["id"],
            format="metadata",
            metadataHeaders=["Subject", "From", "To", "Date"],
        ).execute()
        details.append(detail)
    return details


def format_thread(thread: dict) -> str | None:
    messages = thread.get("messages", [])
    if not messages:
        return None
    msg = messages[-1]
    sender = _header(msg, "From")
    if any(s in sender.lower() for s in SKIP_SENDERS):
        return None
    subject = _header(msg, "Subject") or "(no subject)"
    snippet = msg.get("snippet", "")[:300]
    return f"From: {sender}\nSubject: {subject}\nSnippet: {snippet}"


# ── Calendar helpers ──────────────────────────────────────────────────────────

def fetch_one_time_events(calendar, window_days: int = 14) -> list[dict]:
    now = datetime.now(MOUNTAIN_TZ)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=window_days)

    result = calendar.events().list(
        calendarId="primary",
        timeMin=start.isoformat(),
        timeMax=end.isoformat(),
        singleEvents=True,
        orderBy="startTime",
        maxResults=100,
    ).execute()

    return [
        e for e in result.get("items", [])
        if "recurringEventId" not in e and "recurrence" not in e
    ]


def format_event(event: dict) -> str:
    start = event.get("start", {})
    end = event.get("end", {})
    start_str = start.get("dateTime", start.get("date", "?"))
    end_str = end.get("dateTime", end.get("date", "?"))
    location = event.get("location", "")
    desc = (event.get("description") or "")[:200]
    parts = [
        f"Event: {event.get('summary', '(no title)')}",
        f"Start: {start_str}  End: {end_str}",
    ]
    if location:
        parts.append(f"Location: {location}")
    if desc:
        parts.append(f"Description: {desc}")
    return "\n".join(parts)


# ── Claude API ────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are an executive assistant generating a concise daily morning briefing email.
Respond with a complete HTML snippet (no <html>/<head> wrapper needed) using
clean inline CSS, a blue/grey palette, and max-width 680px.
"""

USER_TEMPLATE = """\
Today is {today}. The recipient's email is {email}.

=== EMAILS FROM THE LAST 7 DAYS ===
{emails}

=== ONE-TIME CALENDAR EVENTS (next 14 days) ===
{events}

Generate a morning digest with:
1. A warm greeting header.
2. A **Top 10 Items to Address** numbered list (most urgent first).
   Each item: bold title + 1-2 sentences of context. Pull from both emails
   and one-time calendar events. Skip purely informational newsletters.
3. A **Out-of-the-Ordinary Calendar Events** section highlighting anything
   unusual or one-time on the calendar.
4. A small footer noting this was auto-generated.

Be specific and actionable. Do not invent information not present in the data.
"""


def generate_html(client: anthropic.Anthropic, emails: list[str], events: list[str],
                  owner_email: str, today_str: str) -> str:
    emails_block = "\n\n".join(emails) if emails else "No qualifying emails this week."
    events_block = "\n\n".join(events) if events else "No one-time events in the next 14 days."

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": USER_TEMPLATE.format(
                today=today_str,
                email=owner_email,
                emails=emails_block,
                events=events_block,
            ),
        }],
    )
    return response.content[0].text


# ── Delivery ──────────────────────────────────────────────────────────────────

def deliver_to_inbox(gmail, owner_email: str, subject: str, html_body: str) -> str:
    mime = "\r\n".join([
        f"To: {owner_email}",
        f"From: {owner_email}",
        f"Subject: {subject}",
        "Content-Type: text/html; charset=utf-8",
        "MIME-Version: 1.0",
        "",
        html_body,
    ])
    raw = base64.urlsafe_b64encode(mime.encode()).decode()

    result = gmail.users().messages().insert(
        userId="me",
        body={"raw": raw, "labelIds": ["INBOX", "UNREAD"]},
    ).execute()
    return result["id"]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    owner_email = os.environ.get("OWNER_EMAIL", "richardlwells@gmail.com")
    now_mt = datetime.now(MOUNTAIN_TZ)
    today_str = now_mt.strftime("%A, %B %-d, %Y")

    print(f"[morning-digest] {today_str} — starting for {owner_email}")

    creds = get_google_creds()
    gmail = build("gmail", "v1", credentials=creds)
    calendar = build("calendar", "v3", credentials=creds)
    claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    threads = fetch_emails(gmail, days=7)
    email_texts = [t for t in (format_thread(th) for th in threads) if t]
    print(f"[morning-digest] {len(email_texts)} actionable email threads")

    events = fetch_one_time_events(calendar, window_days=14)
    event_texts = [format_event(e) for e in events]
    print(f"[morning-digest] {len(event_texts)} one-time calendar events")

    html_body = generate_html(claude, email_texts, event_texts, owner_email, today_str)

    subject = f"☀️ Morning Digest — {today_str}"
    msg_id = deliver_to_inbox(gmail, owner_email, subject, html_body)
    print(f"[morning-digest] delivered — Gmail message ID: {msg_id}")


if __name__ == "__main__":
    main()
