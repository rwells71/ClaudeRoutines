#!/usr/bin/env bash
# Runs the morning digest via the Claude CLI and logs output.
# Designed to be called by cron at 5:00 AM Mountain Time.
# Cron entry (edit with: crontab -e):
#   0 5 * * * TZ=America/Denver /home/user/ClaudeRoutines/run-morning-digest.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPT_FILE="$SCRIPT_DIR/prompts/morning-digest.md"
LOG_FILE="$SCRIPT_DIR/logs/digest-$(date +%Y-%m-%d).log"

mkdir -p "$SCRIPT_DIR/logs"

echo "=== Morning Digest $(date '+%Y-%m-%d %H:%M:%S %Z') ===" >> "$LOG_FILE"

claude \
  --print \
  --no-interactive \
  -p "$(cat "$PROMPT_FILE")" \
  >> "$LOG_FILE" 2>&1

echo "=== Done $(date '+%Y-%m-%d %H:%M:%S %Z') ===" >> "$LOG_FILE"
