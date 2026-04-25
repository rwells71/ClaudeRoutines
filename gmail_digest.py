#!/usr/bin/env python3
"""Daily Gmail & Calendar digest — fetches the past week of email and upcoming
calendar events, asks Claude to distil a top-10 action list, then emails the
result to RECIPIENT_EMAIL.

Required environment variables (store as GitHub Secrets):
    ANTHROPIC_API_KEY
    GOOGLE_CLIENT_ID
    GOOGLE_CLIENT_SECRET
    GOOGLE_REFRESH_TOKEN
    RECIPIENT_EMAIL
"""

import base64
import os
import sys
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import anthropic
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.readonly",
]

MAX_EMAILS = 60       # cap to keep prompt size manageable
MAX_EVENTS = 40


def _get_google_credentials() -> Credentials:
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


def fetch_recent_emails(service, days: int = 7) -> list[dict]:
    """Return metadata + snippet for emails in the past `days` days."""
    after = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y/%m/%d")
    # Exclude bulk promotional / social mail
    query = f"after:{after} -category:promotions -category:social -category:updates"

    results = service.users().messages().list(
        userId="me", q=query, maxResults=MAX_EMAILS
    ).execute()

    messages = results.get("messages", [])
    emails = []
    for msg in messages:
        detail = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="metadata",
            metadataHeaders=["Subject", "From", "Date"],
        ).execute()
        headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
        emails.append(
            {
                "subject": headers.get("Subject", "(no subject)"),
                "from": headers.get("From", ""),
                "date": headers.get("Date", ""),
                "snippet": detail.get("snippet", ""),
            }
        )
    return emails


def fetch_calendar_events(service, days_back: int = 2, days_forward: int = 14) -> list[dict]:
    """Return events from all calendars spanning the look-back / look-ahead window."""
    now = datetime.now(timezone.utc)
    time_min = (now - timedelta(days=days_back)).isoformat()
    time_max = (now + timedelta(days=days_forward)).isoformat()

    cal_list = service.calendarList().list().execute()
    events: list[dict] = []
    seen: set[str] = set()

    for cal in cal_list.get("items", []):
        if cal.get("accessRole") not in ("owner", "writer", "reader"):
            continue
        result = service.events().list(
            calendarId=cal["id"],
            timeMin=time_min,
            timeMax=time_max,
            maxResults=MAX_EVENTS,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        for event in result.get("items", []):
            eid = event.get("id", "")
            if eid not in seen:
                seen.add(eid)
                events.append(event)

    return events


def _format_emails(emails: list[dict]) -> str:
    lines = []
    for i, e in enumerate(emails, 1):
        lines.append(
            f"{i}. Date: {e['date']}\n"
            f"   From: {e['from']}\n"
            f"   Subject: {e['subject']}\n"
            f"   Preview: {e['snippet']}"
        )
    return "\n\n".join(lines) or "(no emails)"


def _format_events(events: list[dict]) -> str:
    lines = []
    for e in events:
        start = e.get("start", {})
        start_str = start.get("dateTime", start.get("date", "unknown"))
        title = e.get("summary", "(no title)")
        desc = (e.get("description") or "")[:200]
        attendees = ", ".join(
            a.get("email", "") for a in (e.get("attendees") or [])[:5]
        )
        lines.append(
            f"- {title}\n"
            f"  Start: {start_str}\n"
            + (f"  Attendees: {attendees}\n" if attendees else "")
            + (f"  Notes: {desc}" if desc else "")
        )
    return "\n\n".join(lines) or "(no events)"


def build_digest(emails: list[dict], events: list[dict]) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    today = datetime.now().strftime("%A, %B %d, %Y")
    email_block = _format_emails(emails)
    event_block = _format_events(events)

    system = (
        "You are a sharp executive assistant. Your job is to read a batch of emails "
        "and calendar events and produce a concise, scannable morning briefing. "
        "Be specific, avoid filler, and focus on what actually needs the person's attention."
    )

    user_prompt = f"""Today is {today}.

=== EMAILS (past 7 days) ===
{email_block}

=== CALENDAR EVENTS (past 2 days + next 14 days) ===
{event_block}

=== YOUR TASK ===
Produce a morning digest with exactly these two sections:

**TOP 10 ACTION ITEMS**
Number each item 1–10. Each item should be one concise sentence describing:
  • what needs to be done
  • who it involves or which email/event it came from
  • any deadline or urgency signal

Prioritise: replies overdue, decisions requested, deadlines approaching, unresolved threads.

**NOTABLE CALENDAR EVENTS**
Bullet-list only events that are unusual, new, high-stakes, time-sensitive, or involve important external parties in the next 14 days.
Skip routine recurring meetings unless something looks different (different time, extra attendees, etc.).

Keep the whole digest under 400 words. Write in plain text suitable for an email body."""

    # Use prompt caching for the large email/calendar blocks
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": system,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
            }
        ],
    )
    return response.content[0].text


def send_email(service, to: str, subject: str, body: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = "me"
    msg["To"] = to
    msg.attach(MIMEText(body, "plain"))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()


def main() -> None:
    missing = [
        v for v in (
            "ANTHROPIC_API_KEY",
            "GOOGLE_CLIENT_ID",
            "GOOGLE_CLIENT_SECRET",
            "GOOGLE_REFRESH_TOKEN",
            "RECIPIENT_EMAIL",
        )
        if not os.environ.get(v)
    ]
    if missing:
        print(f"ERROR: missing environment variables: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    recipient = os.environ["RECIPIENT_EMAIL"]
    creds = _get_google_credentials()
    gmail = build("gmail", "v1", credentials=creds)
    calendar = build("calendar", "v3", credentials=creds)

    print("Fetching emails…")
    emails = fetch_recent_emails(gmail)
    print(f"  {len(emails)} emails found.")

    print("Fetching calendar events…")
    events = fetch_calendar_events(calendar)
    print(f"  {len(events)} events found.")

    print("Generating digest with Claude…")
    digest = build_digest(emails, events)

    today_str = datetime.now().strftime("%A, %B %d")
    subject = f"Morning Digest — {today_str}"

    print(f"Sending digest to {recipient}…")
    send_email(gmail, recipient, subject, digest)
    print("Done.")


if __name__ == "__main__":
    main()
