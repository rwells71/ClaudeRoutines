#!/usr/bin/env python3
"""Run this ONCE locally to generate your GOOGLE_TOKEN_JSON secret for GitHub Actions.

Usage:
  1. Download your OAuth2 credentials from Google Cloud Console and save as credentials.json
  2. pip install google-auth-oauthlib
  3. python scripts/generate_google_token.py
  4. Copy the printed JSON into a GitHub Actions secret named GOOGLE_TOKEN_JSON
  5. Copy the contents of credentials.json into a secret named GOOGLE_CREDENTIALS_JSON
"""

import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.readonly",
]

flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
creds = flow.run_local_server(port=0)

token_data = {
    "token": creds.token,
    "refresh_token": creds.refresh_token,
    "token_uri": creds.token_uri,
    "client_id": creds.client_id,
    "client_secret": creds.client_secret,
    "scopes": list(creds.scopes),
}

print("\n=== Copy this entire JSON block as your GOOGLE_TOKEN_JSON secret ===")
print(json.dumps(token_data, indent=2))
print("\n=== Copy credentials.json contents as your GOOGLE_CREDENTIALS_JSON secret ===")
with open("credentials.json") as f:
    print(f.read())
