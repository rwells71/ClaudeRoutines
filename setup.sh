#!/usr/bin/env bash
# One-time setup for the Morning Briefing automation.
# Run this script once, then add the cron job from crontab_entry.txt.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Morning Briefing Setup ==="
echo ""

# 1. Install Python dependencies
echo "[1/4] Installing Python dependencies..."
pip3 install -q -r requirements.txt
echo "      Done."

# 2. Check for credentials.json
if [ ! -f "credentials.json" ]; then
  echo ""
  echo "[2/4] credentials.json NOT FOUND."
  echo ""
  echo "  You need to create Google OAuth 2.0 credentials:"
  echo "  1. Go to https://console.cloud.google.com/"
  echo "  2. Create a project (or select an existing one)."
  echo "  3. Enable these APIs:"
  echo "       - Gmail API"
  echo "       - Google Calendar API"
  echo "  4. Go to 'APIs & Services' > 'Credentials'."
  echo "  5. Click 'Create Credentials' > 'OAuth client ID'."
  echo "  6. Application type: Desktop app."
  echo "  7. Download the JSON file and save it as:"
  echo "       $SCRIPT_DIR/credentials.json"
  echo ""
  echo "  Then re-run this script."
  exit 1
else
  echo "[2/4] credentials.json found."
fi

# 3. Check / create .env
if [ ! -f ".env" ]; then
  echo ""
  echo "[3/4] Creating .env file..."
  read -rp "  Enter your Anthropic API key: " api_key
  echo "ANTHROPIC_API_KEY=${api_key}" > .env
  chmod 600 .env
  echo "      Saved to .env"
else
  echo "[3/4] .env already exists — skipping."
fi

# 4. Run OAuth flow
echo ""
echo "[4/4] Running Google OAuth flow (a browser window will open)..."
python3 morning_briefing.py --setup
echo ""
echo "=== Setup complete! ==="
echo ""
echo "To enable the daily 5am email, add the cron job:"
echo ""
cat crontab_entry.txt
echo ""
echo "Run:  crontab -e   and paste the line above."
