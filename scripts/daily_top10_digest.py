#!/usr/bin/env python3
"""Daily top-10 morning briefing: Gmail (last 7 days) + Calendar (next 14 days) + Claude."""

import base64
import json
import os
import sys
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo

import anthropic
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TZ = ZoneInfo("America/Denver")
RECIPIENT = os.environ.get("RECIPIENT_EMAIL", "richardlwells@gmail.com")
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.readonly",
]


def get_credentials() -> Credentials:
    raw = os.environ.get("GOOGLE_OAUTH_CREDENTIALS")
    if not raw:
        sys.exit("ERROR: GOOGLE_OAUTH_CREDENTIALS environment variable is not set.")
    d = json.loads(raw)
    creds = Credentials(
        token=d.get("access_token", ""),
        refresh_token=d["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=d["client_id"],
        client_secret=d["client_secret"],
        scopes=SCOPES,
    )
    if not creds.valid:
        creds.refresh(Request())
    return creds


def fetch_emails(svc) -> list[dict]:
    after = (datetime.now(TZ) - timedelta(days=7)).strftime("%Y/%m/%d")
    query = f"after:{after} -in:draft -in:sent -in:spam -category:promotions"
    resp = svc.users().threads().list(userId="me", q=query, maxResults=50).execute()
    threads = resp.get("threads", [])
    emails = []
    for t in threads:
        data = svc.users().threads().get(
            userId="me",
            threadId=t["id"],
            format="metadata",
            metadataHeaders=["Subject", "From", "Date"],
        ).execute()
        for msg in data.get("messages", [])[:1]:
            hdrs = {
                h["name"]: h["value"]
                for h in msg.get("payload", {}).get("headers", [])
            }
            emails.append(
                {
                    "subject": hdrs.get("Subject", "(no subject)"),
                    "from": hdrs.get("From", ""),
                    "date": hdrs.get("Date", ""),
                    "snippet": msg.get("snippet", "")[:300],
                    "labels": msg.get("labelIds", []),
                }
            )
    return emails


def fetch_one_time_events(svc) -> list[dict]:
    now = datetime.now(TZ)
    tmin = now.isoformat()
    tmax = (now + timedelta(days=14)).isoformat()
    resp = (
        svc.events()
        .list(
            calendarId="primary",
            timeMin=tmin,
            timeMax=tmax,
            maxResults=100,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    # Keep only non-recurring events
    return [e for e in resp.get("items", []) if "recurringEventId" not in e]


def build_prompt(emails: list[dict], events: list[dict]) -> str:
    today = datetime.now(TZ).strftime("%A, %B %d, %Y")
    email_block = "\n".join(
        f"- [{e['date'][:16]}] FROM: {e['from']}\n  SUBJECT: {e['subject']}\n  SNIPPET: {e['snippet']}"
        for e in emails
    )
    event_block = "\n".join(
        f"- {e.get('summary', '(no title)')} | "
        f"Start: {e.get('start', {}).get('dateTime', e.get('start', {}).get('date', ''))} | "
        f"Location: {e.get('location', '')} | "
        f"Description: {(e.get('description') or '')[:100]}"
        for e in events
    )
    return f"""Today is {today}. You are Richard Wells's personal executive assistant.

EMAILS (last 7 days, promotions excluded):
{email_block or 'No emails found.'}

UPCOMING ONE-TIME CALENDAR EVENTS (next 14 days, non-recurring only):
{event_block or 'No one-time events found.'}

Generate a morning briefing as clean HTML body content (no <html>/<body> wrapper).

**Section 1 — TOP 10 ACTION ITEMS**: A numbered <ol> list. Rank by urgency + importance.
Focus on: replies needed, financial alerts, deadlines, school/family obligations with dates,
medical follow-ups, commitments to others. One concise sentence per item.
Skip pure newsletters with no action required.

**Section 2 — UNUSUAL CALENDAR EVENTS**: Upcoming one-time events that are out of the
ordinary — not routine daily reminders. Show date, time (MT), event name, location, and a
brief note. Highlight any canceled events that may need rescheduling.

Start with a friendly good-morning greeting. Keep the whole briefing scannable on mobile."""


def generate_briefing(emails: list[dict], events: list[dict]) -> str:
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2048,
        system="You are a concise, helpful executive assistant. Generate clean, mobile-friendly HTML.",
        messages=[{"role": "user", "content": build_prompt(emails, events)}],
    )
    return response.content[0].text


def send_email(svc, html: str) -> None:
    today = datetime.now(TZ).strftime("%B %d, %Y")
    subject = f"Morning Briefing — Top 10 Items | {today}"
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["To"] = RECIPIENT
    msg["From"] = "me"
    msg.attach(MIMEText(html, "html"))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    svc.users().messages().send(userId="me", body={"raw": raw}).execute()
    print(f"Sent to {RECIPIENT}: {subject}")


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ERROR: ANTHROPIC_API_KEY environment variable is not set.")

    creds = get_credentials()
    gmail = build("gmail", "v1", credentials=creds)
    cal = build("calendar", "v3", credentials=creds)

    print("Fetching emails (last 7 days)...")
    emails = fetch_emails(gmail)
    print(f"  {len(emails)} threads.")

    print("Fetching one-time calendar events (next 14 days)...")
    events = fetch_one_time_events(cal)
    print(f"  {len(events)} one-time events.")

    print("Calling Claude to generate briefing...")
    html_body = generate_briefing(emails, events)

    print("Sending email...")
    send_email(gmail, html_body)
    print("Done!")


if __name__ == "__main__":
    main()
