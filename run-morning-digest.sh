#!/usr/bin/env bash
# Runs the morning digest via Claude CLI and logs output.
# Designed to be called from cron at 5:00 AM Mountain Time.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPT_FILE="$SCRIPT_DIR/prompts/morning-digest.md"
LOG_FILE="$SCRIPT_DIR/logs/morning-digest.log"
CLAUDE="/opt/node22/bin/claude"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] $*" >> "$LOG_FILE"
}

log "Starting morning digest"

if [[ ! -f "$PROMPT_FILE" ]]; then
  log "ERROR: Prompt file not found at $PROMPT_FILE"
  exit 1
fi

"$CLAUDE" \
  --dangerously-skip-permissions \
  --print \
  -p "$(cat "$PROMPT_FILE")" \
  >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

if [[ $EXIT_CODE -eq 0 ]]; then
  log "Morning digest completed successfully"
else
  log "ERROR: claude exited with code $EXIT_CODE"
fi

exit $EXIT_CODE
