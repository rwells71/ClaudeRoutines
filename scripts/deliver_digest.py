#!/usr/bin/env python3
"""
Deliver the most-recent morning digest draft to the inbox.

After the Claude step creates the digest draft, this script:
  1. Authenticates with Gmail using a refresh token (gmail.modify scope)
  2. Finds the latest digest draft addressed to the owner
  3. Moves it to the INBOX so it arrives like a normal email

Required environment variables:
  GOOGLE_CLIENT_ID
  GOOGLE_CLIENT_SECRET
  GOOGLE_REFRESH_TOKEN   (must include gmail.modify scope)
  RECIPIENT_EMAIL        (the address Claude addressed the draft to)
"""

import os
import sys
import json
import urllib.request
import urllib.parse


RECIPIENT_EMAIL = os.environ["RECIPIENT_EMAIL"]
CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["GOOGLE_REFRESH_TOKEN"]

DIGEST_SUBJECT_KEYWORDS = [
    "morning digest",
    "daily briefing",
    "daily summary",
    "daily action",
    "morning briefing",
    "morning brief",
    "daily morning",
]


# ── OAuth ─────────────────────────────────────────────────────────────────────

def get_access_token():
    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=data,
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        resp = json.loads(r.read())
    if "access_token" not in resp:
        print(f"Token refresh failed: {resp}", file=sys.stderr)
        sys.exit(1)
    return resp["access_token"]


# ── Gmail API helpers ─────────────────────────────────────────────────────────

def gmail_get(token, path, params=None):
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def gmail_post(token, path, body):
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def get_header(msg, name):
    for h in msg.get("payload", {}).get("headers", []):
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    token = get_access_token()
    print("Authenticated with Gmail.")

    # List recent drafts
    data = gmail_get(token, "drafts", {"maxResults": 30})
    drafts = data.get("drafts", [])
    if not drafts:
        print("No drafts found — nothing to deliver.")
        return

    # Find today's digest draft: subject matches keywords, addressed to owner
    target_msg_id = None
    for d in drafts:
        draft_detail = gmail_get(token, f"drafts/{d['id']}")
        msg = draft_detail.get("message", {})
        subject = get_header(msg, "Subject").lower()
        to_header = get_header(msg, "To").lower()

        is_digest = any(kw in subject for kw in DIGEST_SUBJECT_KEYWORDS)
        is_to_owner = RECIPIENT_EMAIL.lower() in to_header

        if is_digest and is_to_owner:
            target_msg_id = msg.get("id")
            print(f"Found digest draft: '{get_header(msg, 'Subject')}' (message id: {target_msg_id})")
            break

    if not target_msg_id:
        print(
            f"No digest draft found addressed to {RECIPIENT_EMAIL}. "
            "Check that the Claude step ran and created a draft.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Move to INBOX and remove DRAFT label
    result = gmail_post(token, f"messages/{target_msg_id}/modify", {
        "addLabelIds": ["INBOX"],
        "removeLabelIds": ["DRAFT"],
    })
    labels = result.get("labelIds", [])
    if "INBOX" in labels:
        print(f"Digest delivered to inbox (labels: {labels})")
    else:
        print(f"Unexpected label state after modify: {labels}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
