#!/usr/bin/env python3
"""Daily morning email briefing — reads Gmail & Google Calendar, summarizes with Claude, sends email."""

import base64
import json
import os
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import anthropic
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

RECIPIENT_EMAIL = os.environ["RECIPIENT_EMAIL"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
GMAIL_CLIENT_ID = os.environ["GMAIL_CLIENT_ID"]
GMAIL_CLIENT_SECRET = os.environ["GMAIL_CLIENT_SECRET"]
GMAIL_REFRESH_TOKEN = os.environ["GMAIL_REFRESH_TOKEN"]

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]


def get_credentials() -> Credentials:
    creds = Credentials(
        token=None,
        refresh_token=GMAIL_REFRESH_TOKEN,
        client_id=GMAIL_CLIENT_ID,
        client_secret=GMAIL_CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


def fetch_recent_emails(service, days: int = 7, max_results: int = 50) -> list[dict]:
    """Fetch metadata for email threads from the past N days, excluding drafts and sent."""
    query = f"newer_than:{days}d -in:draft -in:sent"
    result = (
        service.users()
        .threads()
        .list(userId="me", q=query, maxResults=max_results)
        .execute()
    )
    threads = result.get("threads", [])

    emails = []
    for thread in threads[:40]:
        t = (
            service.users()
            .threads()
            .get(
                userId="me",
                id=thread["id"],
                format="metadata",
                metadataHeaders=["Subject", "From", "Date"],
            )
            .execute()
        )
        messages = t.get("messages", [])
        if not messages:
            continue
        msg = messages[-1]
        headers = {
            h["name"]: h["value"]
            for h in msg.get("payload", {}).get("headers", [])
        }
        emails.append(
            {
                "subject": headers.get("Subject", "(no subject)"),
                "from": headers.get("From", ""),
                "date": headers.get("Date", ""),
                "snippet": msg.get("snippet", ""),
            }
        )
    return emails


def fetch_upcoming_events(service, days_ahead: int = 14) -> list[dict]:
    """Fetch calendar events for the next N days from the primary calendar."""
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=days_ahead)
    result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now.isoformat(),
            timeMax=end.isoformat(),
            maxResults=60,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = []
    for e in result.get("items", []):
        start = e.get("start", {})
        start_dt = start.get("dateTime", start.get("date", ""))
        events.append(
            {
                "summary": e.get("summary", "(no title)"),
                "start": start_dt,
                "recurring": bool(e.get("recurringEventId")),
                "organizer": e.get("organizer", {}).get("email", ""),
                "attendee_status": _my_rsvp(e, RECIPIENT_EMAIL),
                "description": (e.get("description") or "")[:200],
            }
        )
    return events


def _my_rsvp(event: dict, my_email: str) -> str:
    for a in event.get("attendees", []):
        if a.get("email", "").lower() == my_email.lower() or a.get("self"):
            return a.get("responseStatus", "unknown")
    return "owner"


def generate_summary(emails: list[dict], events: list[dict], today_str: str) -> str:
    """Call Claude to analyze emails and calendar and return an HTML email body."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""Today is {today_str}. You are generating a personalized morning email briefing for Richard Wells.

RECENT EMAILS (last 7 days — snippets only):
{json.dumps(emails, indent=2)}

UPCOMING CALENDAR EVENTS (next 14 days):
{json.dumps(events, indent=2)}

Produce:
1. TOP 10 ACTION ITEMS — ranked by urgency. Focus on things requiring Richard to act: reply, attend, review, fix, or follow up. Skip pure marketing/promotions unless there is a deadline or financial implication. Include financial alerts, family/school needs, urgent notifications, and tasks from messages.
2. NOTEWORTHY CALENDAR EVENTS — only non-routine events: one-time events, special occasions, RSVPs still marked needsAction, or events with an unusual time. Skip daily recurring reminders.

Format your response as a complete HTML email body (no outer html/head tags). Use:
- Greeting: "Good Morning, Richard!"
- Numbered list for action items with bold titles and 1-2 sentence explanations
- A simple table for calendar highlights: Date | Event | Why it's notable
- Subtle inline color styling (blue headings, light row shading)
- Footer: "This briefing was automatically generated from your Gmail & Google Calendar."
"""

    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def send_email(service, sender: str, recipient: str, subject: str, html_body: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(html_body, "html"))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()


def main() -> None:
    creds = get_credentials()
    gmail = build("gmail", "v1", credentials=creds)
    calendar_svc = build("calendar", "v3", credentials=creds)

    today_str = datetime.now().strftime("%A, %B %-d, %Y")

    print("Fetching emails...")
    emails = fetch_recent_emails(gmail)
    print(f"  {len(emails)} email threads found")

    print("Fetching calendar events...")
    events = fetch_upcoming_events(calendar_svc)
    print(f"  {len(events)} events found")

    print("Generating summary with Claude...")
    html_body = generate_summary(emails, events, today_str)

    subject = f"Daily Morning Briefing — {today_str}"
    print(f"Sending to {RECIPIENT_EMAIL}...")
    send_email(gmail, RECIPIENT_EMAIL, RECIPIENT_EMAIL, subject, html_body)
    print("Done!")


if __name__ == "__main__":
    main()
