#!/bin/bash
# Runs the morning digest prompt via Claude Code CLI and logs output.
# Scheduled daily at 5:00 AM Mountain Time via cron.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/logs/morning-digest.log"
PROMPT_FILE="$SCRIPT_DIR/prompts/morning-digest.md"
CLAUDE_BIN="/opt/node22/bin/claude"

mkdir -p "$SCRIPT_DIR/logs"

echo "=== Morning Digest run: $(date) ===" >> "$LOG_FILE"

"$CLAUDE_BIN" \
  --print \
  --dangerously-skip-permissions \
  -p "$(cat "$PROMPT_FILE")" \
  >> "$LOG_FILE" 2>&1

echo "=== Done: $(date) ===" >> "$LOG_FILE"
