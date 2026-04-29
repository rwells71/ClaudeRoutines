#!/usr/bin/env bash
# Runs the Top 10 Daily Briefing via Claude Code and delivers it to Gmail.
# Scheduled via cron at 5:00 AM America/Denver every day.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
PROMPT_FILE="$REPO_DIR/prompts/top10-briefing.md"
LOG_DIR="$REPO_DIR/logs"
LOG_FILE="$LOG_DIR/daily-briefing-$(date +%Y-%m-%d).log"

CLAUDE=/opt/node22/bin/claude

# Rotate logs older than 30 days
find "$LOG_DIR" -name "daily-briefing-*.log" -mtime +30 -delete 2>/dev/null || true

echo "=== Daily Briefing started at $(date) ===" | tee -a "$LOG_FILE"

"$CLAUDE" \
  --print \
  --no-interactive \
  --model claude-sonnet-4-6 \
  "$(cat "$PROMPT_FILE")" \
  >> "$LOG_FILE" 2>&1

echo "=== Daily Briefing finished at $(date) ===" | tee -a "$LOG_FILE"
