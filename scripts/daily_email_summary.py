#!/usr/bin/env python3
"""Daily email summary — fetches Gmail + Calendar, summarizes via Claude, sends at 5am MDT."""

import os
import json
import base64
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import anthropic
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.readonly",
]


def get_google_credentials():
    token_data = json.loads(os.environ["GOOGLE_TOKEN_JSON"])
    creds_data = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
    client = creds_data.get("installed") or creds_data.get("web")

    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client["client_id"],
        client_secret=client["client_secret"],
        scopes=SCOPES,
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds


def fetch_recent_emails(gmail_service, days=7):
    results = gmail_service.users().threads().list(
        userId="me",
        q=f"newer_than:{days}d -in:sent -in:draft",
        maxResults=50,
    ).execute()

    summaries = []
    for thread in results.get("threads", [])[:40]:
        data = gmail_service.users().threads().get(
            userId="me",
            id=thread["id"],
            format="metadata",
            metadataHeaders=["Subject", "From", "Date"],
        ).execute()
        latest = (data.get("messages") or [{}])[-1]
        headers = {h["name"]: h["value"] for h in latest.get("payload", {}).get("headers", [])}
        labels = latest.get("labelIds", [])
        summaries.append({
            "subject": headers.get("Subject", "(no subject)"),
            "from": headers.get("From", "unknown"),
            "date": headers.get("Date", ""),
            "snippet": latest.get("snippet", "")[:250],
            "unread": "UNREAD" in labels,
            "important": "IMPORTANT" in labels,
            "inbox": "INBOX" in labels,
        })
    return summaries


def fetch_calendar_events(calendar_service, days_ahead=14):
    now = datetime.datetime.utcnow()
    time_max = now + datetime.timedelta(days=days_ahead)
    result = calendar_service.events().list(
        calendarId="primary",
        timeMin=now.isoformat() + "Z",
        timeMax=time_max.isoformat() + "Z",
        singleEvents=True,
        orderBy="startTime",
        maxResults=60,
    ).execute()

    events = []
    for e in result.get("items", []):
        start = e.get("start", {})
        events.append({
            "summary": e.get("summary", "(no title)"),
            "start": start.get("dateTime", start.get("date", "")),
            "description": (e.get("description") or "")[:100],
            "is_recurring": bool(e.get("recurringEventId")),
            "location": e.get("location", ""),
        })
    return events


def generate_summary_html(emails, events):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    today = datetime.date.today().strftime("%A, %B %d, %Y")

    prompt = f"""Today is {today}. You are helping Richard Wells start his day with a focused briefing.

RECENT EMAILS (last 7 days):
{json.dumps(emails, indent=2)}

UPCOMING CALENDAR EVENTS (next 14 days):
{json.dumps(events, indent=2)}

Produce a daily briefing as clean, readable HTML (no <html>/<head>/<body> tags — just the inner content).

Structure:
1. A short friendly opening line (1 sentence).
2. **TOP 10 ACTION ITEMS** — a numbered <ol> of the 10 most important things requiring Richard's attention from the emails. For each: include who it's from, what action is needed, and a one-word urgency tag (URGENT / TODAY / THIS WEEK). Skip pure spam, marketing, and automated notifications that need no action.
3. **NOTABLE CALENDAR EVENTS** — a <ul> of upcoming one-time or unusual events in the next 14 days (skip daily/weekly recurring items like "Log all food" or "Family Dinner"). Highlight anything requiring preparation or that is time-sensitive.

Keep the tone warm and direct. Use inline styles for readability. Total length: scannable in under 2 minutes.
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def send_email(gmail_service, to_email, subject, html_body):
    msg = MIMEMultipart("alternative")
    msg["to"] = to_email
    msg["subject"] = subject
    msg.attach(MIMEText(html_body, "html"))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    gmail_service.users().messages().send(userId="me", body={"raw": raw}).execute()
    print(f"Sent to {to_email}")


def main():
    user_email = os.environ.get("USER_EMAIL", "richardlwells@gmail.com")
    creds = get_google_credentials()
    gmail = build("gmail", "v1", credentials=creds)
    calendar = build("calendar", "v3", credentials=creds)

    print("Fetching emails...")
    emails = fetch_recent_emails(gmail)
    print(f"  {len(emails)} threads found")

    print("Fetching calendar events...")
    events = fetch_calendar_events(calendar)
    print(f"  {len(events)} events found")

    print("Generating summary with Claude...")
    html_body = generate_summary_html(emails, events)

    today_str = datetime.date.today().strftime("%a %b %d, %Y")
    subject = f"Daily Summary — {today_str}"
    send_email(gmail, user_email, subject, html_body)
    print("Done.")


if __name__ == "__main__":
    main()
