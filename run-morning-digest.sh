#!/usr/bin/env bash
# Daily morning digest — runs at 5:00 AM MT via cron.
# Invokes the Claude CLI with the morning-digest prompt so it can read Gmail
# and Google Calendar via the configured MCP servers and deliver the digest.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPT_FILE="$SCRIPT_DIR/prompts/morning-digest.md"
LOG_FILE="$SCRIPT_DIR/logs/morning-digest.log"

mkdir -p "$SCRIPT_DIR/logs"

echo "=== Morning digest started: $(date) ===" >> "$LOG_FILE"

/opt/node22/bin/claude \
  --print \
  --dangerously-skip-permissions \
  "$(cat "$PROMPT_FILE")" \
  >> "$LOG_FILE" 2>&1

echo "=== Morning digest finished: $(date) ===" >> "$LOG_FILE"
