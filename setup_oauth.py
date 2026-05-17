#!/usr/bin/env python3
"""
One-time setup script to get a Google OAuth refresh token.
Run this locally (not in CI) to generate the secrets for GitHub Actions.

Steps:
  1. Go to https://console.cloud.google.com/
  2. Create a project (or use an existing one)
  3. Enable: Gmail API and Google Calendar API
  4. Create OAuth 2.0 credentials (Desktop app type)
  5. Download the JSON as 'credentials.json' in this directory
  6. Run:  python setup_oauth.py
  7. A browser window will open — log in as rwells71@gmail.com and grant access
  8. Copy the printed values into your GitHub repository secrets
"""

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]

flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
creds = flow.run_local_server(port=0)

print("\n=== Add these as GitHub Repository Secrets ===")
print(f"RECIPIENT_EMAIL:      rwells71@gmail.com")
print(f"GMAIL_CLIENT_ID:      {creds.client_id}")
print(f"GMAIL_CLIENT_SECRET:  {creds.client_secret}")
print(f"GMAIL_REFRESH_TOKEN:  {creds.refresh_token}")
print(f"ANTHROPIC_API_KEY:    <your key from https://console.anthropic.com>")
print("==============================================\n")
print("To add secrets: GitHub repo → Settings → Secrets and variables → Actions → New repository secret")
