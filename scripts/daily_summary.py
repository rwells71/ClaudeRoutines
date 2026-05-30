#!/usr/bin/env python3
"""Daily email summary: fetches Gmail + Google Calendar, generates top-10 digest via Claude, sends it."""

import base64
import datetime
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import anthropic
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]

TO_EMAIL = os.environ.get("TO_EMAIL", "richardlwells@gmail.com")


def get_google_creds():
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GMAIL_REFRESH_TOKEN"],
        client_id=os.environ["GMAIL_CLIENT_ID"],
        client_secret=os.environ["GMAIL_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


def fetch_recent_emails(gmail_service):
    results = (
        gmail_service.users()
        .messages()
        .list(
            userId="me",
            q="newer_than:7d -in:sent -category:promotions -category:social",
            maxResults=60,
        )
        .execute()
    )
    messages = results.get("messages", [])

    summaries = []
    for msg in messages:
        detail = (
            gmail_service.users()
            .messages()
            .get(
                userId="me",
                id=msg["id"],
                format="metadata",
                metadataHeaders=["Subject", "From", "Date"],
            )
            .execute()
        )
        headers = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}
        summaries.append(
            {
                "subject": headers.get("Subject", "(no subject)"),
                "from": headers.get("From", ""),
                "date": headers.get("Date", ""),
                "snippet": detail.get("snippet", "")[:250],
            }
        )
    return summaries


def fetch_calendar_events(calendar_service):
    now = datetime.datetime.utcnow()
    end = now + datetime.timedelta(days=7)

    results = (
        calendar_service.events()
        .list(
            calendarId="primary",
            timeMin=now.isoformat() + "Z",
            timeMax=end.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime",
            maxResults=50,
        )
        .execute()
    )
    return results.get("items", [])


def generate_summary_html(emails, calendar_events):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    emails_text = "\n".join(
        f"- [{e['date']}] From: {e['from']} | Subject: {e['subject']} | Preview: {e['snippet']}"
        for e in emails
    )

    cal_text = "\n".join(
        "- {}: {}{}".format(
            e.get("start", {}).get("dateTime", e.get("start", {}).get("date", "TBD")),
            e.get("summary", "(no title)"),
            f" | {e['description'][:120]}" if e.get("description") else "",
        )
        for e in calendar_events
    )

    today = datetime.date.today().strftime("%A, %B %-d, %Y")

    prompt = f"""You are a personal assistant for Richard Wells. Today is {today}.

Analyze his recent emails (last 7 days) and upcoming calendar events (next 7 days).
Produce a daily digest with two sections:

SECTION 1 — TOP 10 ACTION ITEMS
Prioritize items needing actual decisions, responses, payments, verifications, or time-sensitive
action. Skip pure newsletters/promotions unless they require action. Mark URGENT items clearly.
Each item: bold title + 1-2 sentence description with the key detail (amount, date, person, etc.).

SECTION 2 — NOTABLE CALENDAR EVENTS (next 7 days)
Only non-routine, one-time, or unusual events. Skip daily recurring reminders like "Log all food"
or "Family Dinner." Highlight: special meetings, appointments, social events, deadlines.

Format as clean, self-contained HTML with inline CSS (must render well in Gmail).
Design: white background, #1a73e8 blue accent, clean sans-serif font, left-border colored cards
for action items (red=#d93025 for urgent, orange=#f9ab00 for medium, green=#34a853 for info).
Include today's date prominently at the top. Keep it scannable — this is a morning briefing.

Return ONLY the inner HTML (no <html>/<head>/<body> tags).

RECENT EMAILS:
{emails_text}

UPCOMING CALENDAR EVENTS:
{cal_text}"""

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def send_email(gmail_service, html_body):
    today = datetime.date.today().strftime("%A, %B %-d, %Y")
    subject = f"Your Daily Digest - {today}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = TO_EMAIL
    msg["To"] = TO_EMAIL
    msg.attach(MIMEText("Open in an HTML-capable email client to view your daily digest.", "plain"))
    msg.attach(MIMEText(html_body, "html"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    gmail_service.users().messages().send(userId="me", body={"raw": raw}).execute()
    print(f"Sent: {subject} -> {TO_EMAIL}")


def main():
    creds = get_google_creds()
    gmail = build("gmail", "v1", credentials=creds)
    calendar = build("calendar", "v3", credentials=creds)

    print("Fetching emails...")
    emails = fetch_recent_emails(gmail)
    print(f"  {len(emails)} emails found")

    print("Fetching calendar events...")
    events = fetch_calendar_events(calendar)
    print(f"  {len(events)} upcoming events found")

    print("Generating digest with Claude...")
    html = generate_summary_html(emails, events)

    print("Sending email...")
    send_email(gmail, html)
    print("Done.")


if __name__ == "__main__":
    main()
