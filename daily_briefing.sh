#!/usr/bin/env bash
# Daily briefing script — runs at 5am via cron
# Reads Gmail + Google Calendar, generates top-10 action list, creates a Gmail draft

set -euo pipefail

TODAY=$(date +"%A, %B %-d, %Y")
WEEK_AGO=$(date -d "7 days ago" +"%Y/%m/%d")
CLAUDE_BIN="/opt/node22/bin/claude"
LOG_DIR="$HOME/ClaudeRoutines/logs"

mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/briefing_$(date +%Y%m%d).log"

echo "[$(date)] Starting daily briefing..." >> "$LOG_FILE"

"$CLAUDE_BIN" --dangerously-skip-permissions -p "
Today is $TODAY.

Please do the following in sequence:

1. Use the mcp__Gmail__search_threads tool to search for emails from the last 7 days
   with query: 'newer_than:7d'. Fetch up to 50 threads.

2. Use the mcp__Google-Calendar__list_events tool to get calendar events for the next
   14 days (from today through 2 weeks out).

3. Analyze all the emails and events. Identify the top 10 most important action items
   the user (Richard Wells, richardlwells@gmail.com) needs to address. Prioritize:
   - Deadlines and time-sensitive items (bills due, school notices, expiring accounts)
   - Family events and obligations (kids activities, spouse requests, anniversaries)
   - Work or professional items (webinars, meetings, invitations)
   - Household tasks (maintenance reminders, recurring to-dos)
   Ignore newsletters, promotional emails, and routine automated notifications
   unless they contain an urgent action item.

4. Also flag any calendar events that are out of the ordinary (one-time events,
   performances, special occasions, anything not a routine recurring event).

5. Use the mcp__Gmail__create_draft tool to create an HTML-formatted draft email
   addressed to richardlwells@gmail.com with subject:
   'Daily Briefing — Top 10 Action Items | $TODAY'
   The email should have:
   - A numbered top-10 action item list with brief context for each item
   - A section for notable upcoming calendar events in a clean table
   - Clean, readable HTML formatting
   Do not explain what you are doing — just perform the steps and confirm when the
   draft has been created.
" >> "$LOG_FILE" 2>&1

echo "[$(date)] Daily briefing complete." >> "$LOG_FILE"
