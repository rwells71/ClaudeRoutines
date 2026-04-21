#!/usr/bin/env python3
"""
Daily Morning Briefing — runs at 5am via cron.

Reads Gmail (last 24h) + Calendar (next 7 days), asks Claude to build a
Top-10 action list with unusual calendar highlights, then drafts or sends
the summary email to RECIPIENT_EMAIL.

First-run setup:
  1. Create a Google Cloud project, enable Gmail API + Google Calendar API.
  2. Create OAuth 2.0 Desktop credentials → download as credentials.json
     and place it next to this script.
  3. Set ANTHROPIC_API_KEY in your environment (or in .env).
  4. Run once interactively:  python3 morning_briefing.py --setup
     A browser window opens; authenticate and approve access.
     A token.json is saved — future runs are fully headless.
  5. Add the cron job (see crontab_entry.txt).
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

# ── configuration ──────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent.resolve()
CREDENTIALS_FILE = SCRIPT_DIR / "credentials.json"
TOKEN_FILE = SCRIPT_DIR / "token.json"
LOG_FILE = SCRIPT_DIR / "briefing.log"

RECIPIENT_EMAIL = "richardlwells@gmail.com"
ANTHROPIC_MODEL = "claude-sonnet-4-6"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.readonly",
]
# ───────────────────────────────────────────────────────────────────────────────


def log(msg: str) -> None:
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def get_google_creds(interactive: bool = False):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not interactive:
                raise RuntimeError(
                    "No valid token found. Run:  python3 morning_briefing.py --setup"
                )
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"credentials.json not found at {CREDENTIALS_FILE}. "
                    "Download it from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())

    return creds


def fetch_gmail_threads(service, hours: int = 24) -> list[dict]:
    after = int(
        (datetime.datetime.utcnow() - datetime.timedelta(hours=hours)).timestamp()
    )
    result = (
        service.users()
        .threads()
        .list(userId="me", q=f"after:{after}", maxResults=50)
        .execute()
    )
    threads = result.get("threads", [])
    summaries = []
    for t in threads[:40]:
        data = (
            service.users()
            .threads()
            .get(userId="me", threadId=t["id"], format="metadata",
                 metadataHeaders=["Subject", "From", "Date"])
            .execute()
        )
        msgs = data.get("messages", [])
        if not msgs:
            continue
        first = msgs[0]
        headers = {h["name"]: h["value"] for h in first.get("payload", {}).get("headers", [])}
        snippet = first.get("snippet", "")[:200]
        summaries.append({
            "subject": headers.get("Subject", "(no subject)"),
            "from": headers.get("From", ""),
            "date": headers.get("Date", ""),
            "snippet": snippet,
        })
    return summaries


def fetch_calendar_events(service, days_ahead: int = 7) -> list[dict]:
    now = datetime.datetime.utcnow().isoformat() + "Z"
    end = (
        datetime.datetime.utcnow() + datetime.timedelta(days=days_ahead)
    ).isoformat() + "Z"
    result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            timeMax=end,
            singleEvents=True,
            orderBy="startTime",
            maxResults=50,
        )
        .execute()
    )
    events = []
    for e in result.get("items", []):
        start = e["start"].get("dateTime", e["start"].get("date", ""))
        events.append({
            "summary": e.get("summary", "(no title)"),
            "start": start,
            "description": (e.get("description", "") or "")[:200],
            "recurrence": bool(e.get("recurringEventId")),
        })
    return events


def build_prompt(emails: list[dict], events: list[dict], today: str) -> str:
    email_block = json.dumps(emails, indent=2)
    event_block = json.dumps(events, indent=2)
    return f"""Today is {today}.

Below is a JSON list of emails received in the last 24 hours, followed by
calendar events for the next 7 days.

Your job: produce a daily morning briefing in clean HTML with:
1. A numbered Top-10 list of the most important action items from the emails
   (skip newsletters, marketing, and automated notifications unless they
   require a response or a decision). Mark urgent items with 🔴, medium with
   🟡, and informational with 🟢.
2. A short section titled "Unusual Calendar Events" listing only non-routine,
   one-off, or otherwise noteworthy events (not recurring daily reminders).
   Include the date/time and a one-sentence note on why it stands out.

Keep the tone concise and professional. Return only the HTML body content
(no <html> or <body> wrapper tags — the script wraps it).

=== EMAILS (last 24 h) ===
{email_block}

=== CALENDAR EVENTS (next 7 days) ===
{event_block}
"""


def ask_claude(prompt: str, api_key: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def send_email(service, to: str, subject: str, html_body: str) -> None:
    today = datetime.date.today().strftime("%B %-d, %Y")
    full_html = f"""<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;max-width:650px;margin:0 auto;color:#222;">
<h2 style="color:#1a73e8;border-bottom:2px solid #1a73e8;padding-bottom:8px;">
  ☀️ Daily Morning Briefing &mdash; {today}
</h2>
{html_body}
<hr style="border:1px solid #eee;margin:20px 0;">
<p style="color:#888;font-size:12px;">
  Auto-generated by ClaudeRoutines · {today} · 5:00 AM MDT
</p>
</body>
</html>"""

    msg = MIMEMultipart("alternative")
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(full_html, "html"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()


def main(interactive: bool = False) -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        env_file = SCRIPT_DIR / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("ANTHROPIC_API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not api_key:
        log("ERROR: ANTHROPIC_API_KEY not set. Add it to the environment or .env file.")
        sys.exit(1)

    log("Authenticating with Google...")
    creds = get_google_creds(interactive=interactive)

    from googleapiclient.discovery import build
    gmail_svc = build("gmail", "v1", credentials=creds)
    cal_svc = build("calendar", "v3", credentials=creds)

    log("Fetching Gmail threads (last 24h)...")
    emails = fetch_gmail_threads(gmail_svc, hours=24)
    log(f"  Found {len(emails)} threads.")

    log("Fetching Calendar events (next 7 days)...")
    events = fetch_calendar_events(cal_svc, days_ahead=7)
    log(f"  Found {len(events)} events.")

    today_str = datetime.date.today().strftime("%A, %B %-d, %Y")
    log("Asking Claude to generate briefing...")
    prompt = build_prompt(emails, events, today_str)
    html_body = ask_claude(prompt, api_key)

    subject = f"☀️ Morning Briefing — {today_str}"
    log(f"Sending email to {RECIPIENT_EMAIL}...")
    send_email(gmail_svc, RECIPIENT_EMAIL, subject, html_body)
    log("Done — briefing sent successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Daily Morning Briefing")
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run interactive OAuth setup (required on first use).",
    )
    args = parser.parse_args()
    main(interactive=args.setup)
