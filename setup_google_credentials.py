#!/usr/bin/env python3
"""
One-time setup script: runs the OAuth2 flow and prints the token JSON
so you can paste it into the GOOGLE_TOKEN_JSON GitHub secret.

Usage:
  1. Download OAuth2 credentials from Google Cloud Console:
       APIs & Services → Credentials → Create → OAuth 2.0 Client ID → Desktop app
       Download as credentials.json in this directory.
  2. Run:  python setup_google_credentials.py
  3. Complete the browser auth flow.
  4. Copy the printed JSON into your GitHub secret GOOGLE_TOKEN_JSON.
  5. Copy credentials.json content into GitHub secret GOOGLE_CREDENTIALS_JSON.
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

print("\n=== GOOGLE_TOKEN_JSON (paste this into your GitHub secret) ===")
print(json.dumps(token_data, indent=2))
print("\n=== Done. Also paste credentials.json into GOOGLE_CREDENTIALS_JSON ===")
