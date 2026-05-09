#!/usr/bin/env bash
# Runs the morning digest via Claude CLI and logs output.
# Intended to be executed by cron at 5:00 AM Mountain Time.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPT_FILE="$SCRIPT_DIR/prompts/morning-digest.md"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/briefing-$(date +%Y-%m-%d).log"

mkdir -p "$LOG_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting morning digest..." >> "$LOG_FILE"

/opt/node22/bin/claude \
  --print \
  --dangerously-skip-permissions \
  "$(cat "$PROMPT_FILE")" \
  >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Digest complete." >> "$LOG_FILE"
