#!/usr/bin/env python3
"""
One-time setup: authorize this app with Google and print the base64-encoded
secrets you need to add to your GitHub repository.

Usage:
  1. Go to https://console.cloud.google.com/
  2. Create a project, enable Gmail API + Google Calendar API.
  3. Create OAuth 2.0 credentials (Desktop app), download as credentials.json.
  4. Run:  python setup_google_auth.py credentials.json
  5. Copy the printed secrets into GitHub → Settings → Secrets and variables → Actions.
"""

import base64
import json
import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.insert",
    "https://www.googleapis.com/auth/calendar.readonly",
]


def main():
    if len(sys.argv) < 2:
        print("Usage: python setup_google_auth.py <path/to/credentials.json>")
        sys.exit(1)

    creds_path = Path(sys.argv[1])
    if not creds_path.exists():
        print(f"File not found: {creds_path}")
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
    creds = flow.run_local_server(port=0)

    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes),
    }

    creds_b64 = base64.b64encode(creds_path.read_bytes()).decode()
    token_b64 = base64.b64encode(json.dumps(token_data).encode()).decode()

    print("\n" + "=" * 60)
    print("Add these 4 secrets to your GitHub repo:")
    print("  Settings → Secrets and variables → Actions → New secret")
    print("=" * 60)
    print(f"\nSecret name:  GOOGLE_CREDENTIALS_JSON")
    print(f"Secret value: {creds_b64}")
    print(f"\nSecret name:  GOOGLE_TOKEN_JSON")
    print(f"Secret value: {token_b64}")
    print(f"\nSecret name:  ANTHROPIC_API_KEY")
    print(f"Secret value: <your Anthropic API key from console.anthropic.com>")
    print(f"\nSecret name:  OWNER_EMAIL")
    print(f"Secret value: richardlwells@gmail.com")
    print("\n" + "=" * 60)
    print("Done! Run the workflow manually first to verify it works:")
    print("  GitHub → Actions → Morning Digest → Run workflow")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
