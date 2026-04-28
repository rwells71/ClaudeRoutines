#!/usr/bin/env python3
"""
Daily 5 AM briefing: fetches Gmail + Google Calendar data, calls Claude
to summarize, and sends the result to RECIPIENT_EMAIL.

First-time setup
----------------
1. Create a Google Cloud project with Gmail API + Calendar API enabled.
2. Create OAuth 2.0 Desktop credentials, download as credentials.json,
   and place it at ~/.config/daily_briefing/credentials.json.
3. Run once interactively to authorise and save token.json:
       python3 briefing.py --setup
4. Set ANTHROPIC_API_KEY in the environment (or in a .env file next to
   this script).
5. Add to cron:  0 5 * * * /usr/bin/python3 /path/to/briefing.py >> /var/log/daily_briefing.log 2>&1
"""

import argparse
import base64
import datetime
import json
import os
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import anthropic
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ── Configuration ────────────────────────────────────────────────────────────

RECIPIENT_EMAIL = "richardlwells@gmail.com"
SENDER_EMAIL    = "richardlwells@gmail.com"

CONFIG_DIR     = Path.home() / ".config" / "daily_briefing"
CREDENTIALS    = CONFIG_DIR / "credentials.json"
TOKEN_FILE     = CONFIG_DIR / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.readonly",
]

CLAUDE_MODEL = "claude-sonnet-4-6"
EMAIL_LOOKBACK_DAYS = 7
CALENDAR_LOOKAHEAD_DAYS = 14

# ── Google Auth ───────────────────────────────────────────────────────────────

def get_google_credentials() -> Credentials:
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS.exists():
                sys.exit(
                    f"ERROR: Google credentials not found at {CREDENTIALS}\n"
                    "Download OAuth 2.0 Desktop credentials from Google Cloud Console\n"
                    "and place them there, then run:  python3 briefing.py --setup"
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS), SCOPES)
            creds = flow.run_local_server(port=0)

        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(creds.to_json())

    return creds


# ── Gmail helpers ─────────────────────────────────────────────────────────────

def fetch_emails(service, days: int = EMAIL_LOOKBACK_DAYS) -> list[dict]:
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y/%m/%d")
    query  = f"after:{cutoff} -category:promotions -category:social"

    result  = service.users().messages().list(userId="me", q=query, maxResults=60).execute()
    msg_ids = [m["id"] for m in result.get("messages", [])]

    emails = []
    for mid in msg_ids:
        msg = service.users().messages().get(
            userId="me", id=mid, format="metadata",
            metadataHeaders=["Subject", "From", "Date"]
        ).execute()
        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        emails.append({
            "subject": headers.get("Subject", "(no subject)"),
            "from":    headers.get("From", ""),
            "date":    headers.get("Date", ""),
            "snippet": msg.get("snippet", ""),
        })
    return emails


# ── Calendar helpers ──────────────────────────────────────────────────────────

def fetch_calendar_events(service, days: int = CALENDAR_LOOKAHEAD_DAYS) -> list[dict]:
    now    = datetime.datetime.utcnow().isoformat() + "Z"
    until  = (datetime.datetime.utcnow() + datetime.timedelta(days=days)).isoformat() + "Z"

    result = service.events().list(
        calendarId="primary",
        timeMin=now,
        timeMax=until,
        maxResults=50,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = []
    for e in result.get("items", []):
        start = e["start"].get("dateTime", e["start"].get("date", ""))
        events.append({
            "summary":  e.get("summary", "(no title)"),
            "start":    start,
            "location": e.get("location", ""),
            "attendees": len(e.get("attendees", [])),
            "recurring": bool(e.get("recurringEventId")),
        })
    return events


# ── Claude summariser ─────────────────────────────────────────────────────────

def build_summary(emails: list[dict], events: list[dict]) -> tuple[str, str]:
    """Returns (plain_text_summary, html_summary)."""
    today = datetime.date.today().strftime("%A, %B %-d, %Y")

    email_blob = "\n".join(
        f"- [{e['date'][:16]}] FROM: {e['from']} | SUBJECT: {e['subject']} | SNIPPET: {e['snippet'][:200]}"
        for e in emails
    )

    event_blob = "\n".join(
        f"- [{e['start'][:16]}] {e['summary']}"
        + (f" @ {e['location']}" if e['location'] else "")
        + (" [RECURRING]" if e['recurring'] else " [ONE-TIME]")
        for e in events
    )

    prompt = f"""Today is {today}. You are a personal assistant for Richard Wells.

EMAILS FROM THE LAST {EMAIL_LOOKBACK_DAYS} DAYS:
{email_blob or 'None found.'}

UPCOMING CALENDAR EVENTS (next {CALENDAR_LOOKAHEAD_DAYS} days):
{event_blob or 'None found.'}

Your task:
1. Identify and rank the TOP 10 most important action items Richard needs to address from the emails.
   Focus on: deadlines, requests requiring response, financial alerts, family/school issues, work items.
   Ignore pure marketing/promotional emails unless there is a real deadline.
2. Highlight any calendar events that are OUT OF THE ORDINARY (non-recurring, special occasions,
   unusual timing, or events needing preparation). Skip routine recurring events.

Return your response in two sections:
### TOP 10 ACTION ITEMS
(numbered list, each item: bold title + 1–2 sentence explanation)

### NOTEWORTHY CALENDAR EVENTS
(bulleted list with date, event name, and why it stands out)

Be concise and direct. No pleasantries."""

    client  = anthropic.Anthropic()
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    plain = message.content[0].text

    # Convert markdown-ish plain text to a clean HTML email
    html = _plain_to_html(plain, today)
    return plain, html


def _plain_to_html(plain: str, today: str) -> str:
    lines  = plain.split("\n")
    items  = []
    in_top = False
    in_cal = False
    top10  = []
    cal    = []

    for line in lines:
        if line.startswith("### TOP 10"):
            in_top, in_cal = True, False
            continue
        if line.startswith("### NOTEWORTHY"):
            in_top, in_cal = False, True
            continue
        if in_top and line.strip():
            top10.append(line.strip())
        elif in_cal and line.strip():
            cal.append(line.strip())

    top_rows = ""
    colors   = ["#fce8e6", "#fff8e1", "", "#e8f5e9", "#e3f2fd",
                "#fce8e6", "#fff8e1", "", "#e8f5e9", "#e3f2fd"]
    icons    = ["🚨","⏰","📌","📅","💳","💬","🏫","📎","🎓","🔔"]

    for idx, item in enumerate(top10[:10]):
        bg   = f'background:{colors[idx]};' if colors[idx] else ""
        icon = icons[idx]
        # Bold first clause up to first —, :, or end
        text = item.lstrip("0123456789. ")
        top_rows += (
            f'<tr style="{bg}">'
            f'<td style="padding:12px;border-bottom:1px solid #ddd;width:36px;font-size:18px;vertical-align:top;">{icon}</td>'
            f'<td style="padding:12px;border-bottom:1px solid #ddd;">{text}</td>'
            f'</tr>\n'
        )

    cal_rows = ""
    for item in cal:
        cal_rows += (
            f'<tr>'
            f'<td style="padding:10px;border-bottom:1px solid #ddd;">📆 {item.lstrip("- ")}</td>'
            f'</tr>\n'
        )

    return f"""<html><body style="font-family:Arial,sans-serif;max-width:700px;margin:0 auto;color:#333;">
<div style="background:#1a73e8;color:white;padding:20px;border-radius:8px 8px 0 0;">
  <h1 style="margin:0;font-size:22px;">📋 Daily Briefing — {today}</h1>
  <p style="margin:5px 0 0;opacity:.9;font-size:14px;">Last {EMAIL_LOOKBACK_DAYS} days of email · Generated 5:00 AM MDT</p>
</div>
<div style="border:1px solid #ddd;border-top:none;border-radius:0 0 8px 8px;padding:20px;">
<h2 style="color:#1a73e8;border-bottom:2px solid #1a73e8;padding-bottom:8px;">🔔 Top 10 Action Items</h2>
<table style="width:100%;border-collapse:collapse;">
{top_rows if top_rows else '<tr><td style="padding:12px;">No urgent items found.</td></tr>'}
</table>
<h2 style="color:#0f9d58;border-bottom:2px solid #0f9d58;padding-bottom:8px;margin-top:28px;">📆 Noteworthy Calendar Events</h2>
<table style="width:100%;border-collapse:collapse;">
{cal_rows if cal_rows else '<tr><td style="padding:12px;">No unusual events found.</td></tr>'}
</table>
<div style="margin-top:24px;padding:12px;background:#f5f5f5;border-radius:6px;font-size:12px;color:#777;">
Auto-generated daily briefing. Covers emails from the past {EMAIL_LOOKBACK_DAYS} days and upcoming {CALENDAR_LOOKAHEAD_DAYS} days of calendar.
</div>
</div>
</body></html>"""


# ── Gmail send ────────────────────────────────────────────────────────────────

def send_email(service, plain: str, html: str):
    today   = datetime.date.today().strftime("%A, %B %-d, %Y")
    subject = f"📋 Daily Briefing — {today}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECIPIENT_EMAIL
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html,  "html"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()
    print(f"Briefing sent to {RECIPIENT_EMAIL}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Daily email briefing generator")
    parser.add_argument("--setup", action="store_true",
                        help="Run OAuth setup flow (interactive)")
    args = parser.parse_args()

    if args.setup:
        print("Running OAuth setup — a browser window will open for authorisation.")
        get_google_credentials()
        print(f"Token saved to {TOKEN_FILE}. You can now run the script unattended.")
        return

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        # Try loading from .env in the same directory
        env_file = Path(__file__).parent / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("ANTHROPIC_API_KEY="):
                    os.environ["ANTHROPIC_API_KEY"] = line.split("=", 1)[1].strip().strip('"')
                    break
        if not os.environ.get("ANTHROPIC_API_KEY"):
            sys.exit("ERROR: ANTHROPIC_API_KEY not set. Add it to your environment or to a .env file next to this script.")

    creds          = get_google_credentials()
    gmail_service  = build("gmail",    "v1",  credentials=creds)
    cal_service    = build("calendar", "v3",  credentials=creds)

    print("Fetching emails...")
    emails = fetch_emails(gmail_service)
    print(f"  {len(emails)} messages found")

    print("Fetching calendar events...")
    events = fetch_calendar_events(cal_service)
    print(f"  {len(events)} events found")

    print("Generating summary with Claude...")
    plain, html = build_summary(emails, events)

    print("Sending email...")
    send_email(gmail_service, plain, html)


if __name__ == "__main__":
    main()
