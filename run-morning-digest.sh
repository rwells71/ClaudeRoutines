#!/usr/bin/env bash
# Daily morning digest — runs at 5:00 AM Mountain Time via cron.
# Requires: claude CLI configured with Gmail and Google Calendar MCP servers.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPT_FILE="$SCRIPT_DIR/prompts/morning-digest.md"
LOG_FILE="$SCRIPT_DIR/logs/morning-digest.log"

mkdir -p "$SCRIPT_DIR/logs"

echo "=== Morning Digest $(date '+%Y-%m-%d %H:%M:%S %Z') ===" >> "$LOG_FILE"

/opt/node22/bin/claude \
  --model claude-sonnet-4-6 \
  -p "$(cat "$PROMPT_FILE")" \
  --allowedTools "mcp__Gmail__search_threads,mcp__Gmail__get_thread,mcp__Gmail__create_draft,mcp__Gmail__label_message,mcp__Google-Calendar__list_events" \
  2>&1 | tee -a "$LOG_FILE"

echo "=== Done $(date '+%Y-%m-%d %H:%M:%S %Z') ===" >> "$LOG_FILE"
