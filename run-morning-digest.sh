#!/usr/bin/env bash
# Runs the morning digest prompt via Claude Code and logs output.
# Scheduled daily at 5:00 AM Mountain Time via cron.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/logs/morning-digest.log"
PROMPT_FILE="$SCRIPT_DIR/prompts/morning-digest.md"
CLAUDE="/opt/node22/bin/claude"

mkdir -p "$SCRIPT_DIR/logs"

echo "======================================" >> "$LOG_FILE"
echo "Run started: $(date '+%Y-%m-%d %H:%M:%S %Z')" >> "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"

"$CLAUDE" \
  --print \
  --permission-mode bypassPermissions \
  --output-format text \
  "$(cat "$PROMPT_FILE")" \
  >> "$LOG_FILE" 2>&1

echo "Run finished: $(date '+%Y-%m-%d %H:%M:%S %Z')" >> "$LOG_FILE"
