#!/usr/bin/env python3
"""
One-time setup: authorise morning_digest.py to access your Gmail and Calendar.

Steps:
  1. Create a Google Cloud project at https://console.cloud.google.com
  2. Enable the Gmail API and Google Calendar API
  3. Create OAuth 2.0 credentials (type: Desktop app)
  4. Download the JSON and note your client_id and client_secret
  5. Run:
       GOOGLE_CLIENT_ID=<id> GOOGLE_CLIENT_SECRET=<secret> python scripts/setup_google_auth.py
  6. Copy the printed GOOGLE_REFRESH_TOKEN into your GitHub repo secrets
     (Settings → Secrets and variables → Actions → New repository secret)
"""

import os
import sys

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    sys.exit("Run: pip install google-auth-oauthlib")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.readonly",
]

client_id = os.environ.get("GOOGLE_CLIENT_ID")
client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")

if not client_id or not client_secret:
    sys.exit("Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET before running.")

client_config = {
    "installed": {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
creds = flow.run_local_server(port=0)

print("\n✅ Authorization complete!\n")
print("Add these as GitHub Actions secrets (Settings → Secrets → Actions):\n")
print(f"  GOOGLE_CLIENT_ID     = {client_id}")
print(f"  GOOGLE_CLIENT_SECRET = {client_secret}")
print(f"  GOOGLE_REFRESH_TOKEN = {creds.refresh_token}")
print(f"\n  ANTHROPIC_API_KEY    = <your key from https://console.anthropic.com>")
print(f"  OWNER_EMAIL          = <your Gmail address>")
