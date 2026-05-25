#!/usr/bin/env python3
"""
One-time helper: obtain a Google OAuth2 refresh token with gmail.modify scope.

Run this locally ONCE, then store the printed refresh token as a GitHub secret
named GOOGLE_REFRESH_TOKEN.

Usage:
  pip install google-auth-oauthlib
  python scripts/setup_oauth.py

You'll need a Google Cloud OAuth 2.0 Desktop App client. Download the
client_secret JSON from https://console.cloud.google.com/apis/credentials
and point the script at it via CLIENT_SECRET_FILE below (or env var).
"""

import os
import json

CLIENT_SECRET_FILE = os.environ.get("GOOGLE_CLIENT_SECRET_FILE", "client_secret.json")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar.readonly",
]


def main():
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("Run: pip install google-auth-oauthlib")
        return

    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f"Client secret file not found: {CLIENT_SECRET_FILE}")
        print("Download it from https://console.cloud.google.com/apis/credentials")
        return

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    print("\n" + "=" * 60)
    print("Add these as GitHub repository secrets:")
    print("=" * 60)
    with open(CLIENT_SECRET_FILE) as f:
        secret = json.load(f)
    info = secret.get("installed", secret.get("web", {}))
    print(f"GOOGLE_CLIENT_ID     = {info.get('client_id', '???')}")
    print(f"GOOGLE_CLIENT_SECRET = {info.get('client_secret', '???')}")
    print(f"GOOGLE_REFRESH_TOKEN = {creds.refresh_token}")
    print(f"RECIPIENT_EMAIL      = <your email address>")
    print("=" * 60)


if __name__ == "__main__":
    main()
