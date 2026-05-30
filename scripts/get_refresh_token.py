#!/usr/bin/env python3
"""
One-time setup: generates a Gmail/Calendar OAuth2 refresh token.
Run this locally ONCE, then store the printed values as GitHub Secrets.

Usage:
  1. pip install google-auth-oauthlib
  2. python scripts/get_refresh_token.py
  3. Follow the browser prompt
  4. Copy the printed CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN into GitHub Secrets
"""

import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]

# Paste your OAuth2 client credentials here (from Google Cloud Console)
# Project -> APIs & Services -> Credentials -> Create OAuth 2.0 Client ID (Desktop app)
CLIENT_CONFIG = {
    "installed": {
        "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
        "client_secret": "YOUR_CLIENT_SECRET",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
    }
}

if __name__ == "__main__":
    flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
    creds = flow.run_local_server(port=0)

    print("\n=== Add these as GitHub Repository Secrets ===")
    print(f"GMAIL_CLIENT_ID      = {creds.client_id}")
    print(f"GMAIL_CLIENT_SECRET  = {creds.client_secret}")
    print(f"GMAIL_REFRESH_TOKEN  = {creds.refresh_token}")
    print("\nAlso add:")
    print("ANTHROPIC_API_KEY    = your key from console.anthropic.com")
