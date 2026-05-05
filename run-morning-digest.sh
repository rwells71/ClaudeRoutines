#!/usr/bin/env bash
# Daily morning digest runner — executes at 5:00 AM Mountain Time (11:00 UTC in MDT, 12:00 UTC in MST)
# Invokes Claude Code CLI in non-interactive mode with the morning-digest prompt.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPT_FILE="$SCRIPT_DIR/prompts/morning-digest.md"
LOG_FILE="$SCRIPT_DIR/logs/morning-digest.log"

mkdir -p "$SCRIPT_DIR/logs"

echo "=== Morning digest started at $(date -u '+%Y-%m-%d %H:%M:%S UTC') ===" >> "$LOG_FILE"

claude \
  --print \
  --no-update-check \
  "$(cat "$PROMPT_FILE")" \
  >> "$LOG_FILE" 2>&1

echo "=== Morning digest finished at $(date -u '+%Y-%m-%d %H:%M:%S UTC') ===" >> "$LOG_FILE"
