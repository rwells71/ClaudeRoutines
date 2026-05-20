#!/usr/bin/env python3
"""
One-time setup: generates the GOOGLE_OAUTH_CREDENTIALS secret value.

Run this locally once to authorize the app and obtain a refresh token:
    pip install google-auth-oauthlib
    python scripts/get_google_token.py

Then paste the printed JSON into your GitHub repo secret:
    Settings → Secrets and variables → Actions → New repository secret
    Name: GOOGLE_OAUTH_CREDENTIALS
    Value: (paste the JSON output)

Required scopes (request in Google Cloud Console / OAuth consent screen):
    https://www.googleapis.com/auth/gmail.readonly
    https://www.googleapis.com/auth/gmail.send
    https://www.googleapis.com/auth/calendar.readonly

Steps to create a Google OAuth client:
  1. Go to https://console.cloud.google.com
  2. Create a project (or reuse one)
  3. Enable the Gmail API and Google Calendar API
  4. OAuth consent screen → add the scopes above
  5. Credentials → Create OAuth client ID → Desktop app
  6. Download the JSON → save as client_secret.json in this directory
"""

import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.readonly",
]

flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
creds = flow.run_local_server(port=0)

output = {
    "access_token": creds.token,
    "refresh_token": creds.refresh_token,
    "client_id": creds.client_id,
    "client_secret": creds.client_secret,
    "token_uri": creds.token_uri,
}

print("\n=== Copy the JSON below into your GOOGLE_OAUTH_CREDENTIALS GitHub Secret ===\n")
print(json.dumps(output, indent=2))
