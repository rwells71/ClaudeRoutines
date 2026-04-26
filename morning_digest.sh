#!/bin/bash
# Runs daily at 5 AM Mountain Time via cron.
# Invokes claude headless with the morning-digest prompt, which uses the Gmail
# and Google Calendar MCP tools to build and deliver the digest to the inbox.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/morning_digest_$(date +%Y%m%d).log"

echo "=== Morning Digest started at $(date) ===" >> "$LOG_FILE"

/opt/node22/bin/claude \
  --print \
  --allowedTools "mcp__Gmail__search_threads,mcp__Gmail__get_thread,mcp__Gmail__create_draft,mcp__Gmail__label_message,mcp__Gmail__list_labels,mcp__Google-Calendar__list_events,mcp__Google-Calendar__get_event" \
  "$(cat "$SCRIPT_DIR/prompts/morning-digest.md")" \
  >> "$LOG_FILE" 2>&1

echo "=== Morning Digest finished at $(date) ===" >> "$LOG_FILE"
