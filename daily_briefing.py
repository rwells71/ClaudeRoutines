#!/usr/bin/env python3
"""
Daily morning briefing: fetches Gmail + Google Calendar data,
asks Claude to rank the top 10 action items, and emails the summary.

Required environment variables / GitHub Secrets:
  ANTHROPIC_API_KEY        - Anthropic API key
  GOOGLE_TOKEN_JSON        - Contents of token.json (OAuth2 refresh token)
  GOOGLE_CREDENTIALS_JSON  - Contents of credentials.json (OAuth2 client secrets)
  RECIPIENT_EMAIL          - Address to send the briefing to (e.g. richardlwells@gmail.com)
"""

import os
import json
import base64
import datetime
import zoneinfo
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

MOUNTAIN = zoneinfo.ZoneInfo("America/Denver")


def get_google_creds() -> Credentials:
    token_data = json.loads(os.environ["GOOGLE_TOKEN_JSON"])
    creds_data = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])

    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data["refresh_token"],
        token_uri=creds_data["installed"]["token_uri"],
        client_id=creds_data["installed"]["client_id"],
        client_secret=creds_data["installed"]["client_secret"],
        scopes=SCOPES,
    )
    if creds.expired:
        creds.refresh(Request())
    return creds


def fetch_recent_emails(service, days: int = 7) -> list[dict]:
    after = (datetime.date.today() - datetime.timedelta(days=days)).strftime("%Y/%m/%d")
    query = f"newer_than:{days}d -in:draft -in:sent -category:promotions -category:social"

    results = (
        service.users()
        .threads()
        .list(userId="me", q=query, maxResults=50)
        .execute()
    )
    threads = results.get("threads", [])

    summaries = []
    for t in threads[:50]:
        thread = (
            service.users().threads().get(userId="me", threadId=t["id"], format="metadata",
                metadataHeaders=["Subject", "From", "Date"]).execute()
        )
        msgs = thread.get("messages", [])
        if not msgs:
            continue
        first = msgs[0]
        headers = {h["name"]: h["value"] for h in first.get("payload", {}).get("headers", [])}
        summaries.append({
            "subject": headers.get("Subject", "(no subject)"),
            "from": headers.get("From", ""),
            "date": headers.get("Date", ""),
            "snippet": first.get("snippet", ""),
        })
    return summaries


def fetch_upcoming_events(service, days_ahead: int = 7) -> list[dict]:
    now = datetime.datetime.now(tz=MOUNTAIN)
    end = now + datetime.timedelta(days=days_ahead)

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now.isoformat(),
            timeMax=end.isoformat(),
            singleEvents=True,
            orderBy="startTime",
            maxResults=50,
        )
        .execute()
    )
    events = events_result.get("items", [])

    summaries = []
    for e in events:
        start = e.get("start", {})
        start_str = start.get("dateTime", start.get("date", ""))
        summaries.append({
            "title": e.get("summary", "(no title)"),
            "start": start_str,
            "description": (e.get("description") or "")[:200],
            "location": e.get("location", ""),
        })
    return summaries


def build_prompt(emails: list[dict], events: list[dict], today: str) -> str:
    email_block = "\n".join(
        f"- [{e['date'][:16]}] FROM: {e['from'][:60]} | SUBJECT: {e['subject'][:80]} | SNIPPET: {e['snippet'][:150]}"
        for e in emails
    )
    event_block = "\n".join(
        f"- [{e['start'][:16]}] {e['title'][:80]}" + (f" @ {e['location'][:60]}" if e["location"] else "")
        for e in events
    )

    return f"""Today is {today}. You are a personal assistant helping Richard Wells start his day.

Below are his recent Gmail threads (last 7 days) and upcoming Google Calendar events (next 7 days).

=== EMAILS ===
{email_block or "(none)"}

=== CALENDAR EVENTS (next 7 days) ===
{event_block or "(none)"}

Your task:
1. Identify the TOP 10 items Richard needs to act on today or this week.
   Prioritize: fraud/security alerts, deadlines, family obligations, professional duties, expiring items.
   Skip pure marketing/promotional emails unless there's a real action (e.g. expiring rewards).

2. Flag any calendar events that are NON-ROUTINE or out of the ordinary (one-time events, unusual timing, events needing prep).

Format your response as clean HTML suitable for an email body (no <html>/<body> tags needed — just the inner content).
Use a numbered list for the action items. Include a short calendar section below.
Keep it concise — one or two sentences per item. Use emoji sparingly for scannability."""


def generate_briefing(prompt: str) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def send_email(gmail_service, recipient: str, subject: str, html_body: str):
    full_html = f"""<html><body style="font-family:Arial,sans-serif;max-width:680px;margin:0 auto;color:#222;">
<h2 style="border-bottom:2px solid #4A90D9;padding-bottom:8px;color:#4A90D9;">{subject}</h2>
{html_body}
<p style="margin-top:24px;font-size:11px;color:#aaa;">Generated by your Claude morning briefing assistant.</p>
</body></html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["To"] = recipient
    msg.attach(MIMEText(full_html, "html"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    gmail_service.users().messages().send(userId="me", body={"raw": raw}).execute()


def main():
    creds = get_google_creds()
    gmail = build("gmail", "v1", credentials=creds)
    calendar = build("calendar", "v3", credentials=creds)

    today = datetime.date.today().strftime("%A, %B %-d, %Y")
    subject = f"🌅 Daily Briefing — {today}"
    recipient = os.environ.get("RECIPIENT_EMAIL", "richardlwells@gmail.com")

    print("Fetching emails...")
    emails = fetch_recent_emails(gmail)
    print(f"  Found {len(emails)} threads")

    print("Fetching calendar events...")
    events = fetch_upcoming_events(calendar)
    print(f"  Found {len(events)} events")

    print("Generating briefing with Claude...")
    prompt = build_prompt(emails, events, today)
    html_content = generate_briefing(prompt)

    print(f"Sending to {recipient}...")
    send_email(gmail, recipient, subject, html_content)
    print("Done.")


if __name__ == "__main__":
    main()
