#!/bin/bash
# morning_briefing.sh
# Generates a daily top-10 email briefing from Gmail + Google Calendar.
# Designed to run at 5am via cron:
#   0 5 * * * /home/user/ClaudeRoutines/scripts/morning_briefing.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/../logs"
LOG_FILE="$LOG_DIR/morning_briefing.log"
CLAUDE_BIN="/opt/node22/bin/claude"
RECIPIENT="rwells71@gmail.com"

mkdir -p "$LOG_DIR"

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "$LOG_FILE"
}

log "========== Morning Briefing Started =========="

TODAY_LONG=$(date '+%A, %B %-d, %Y')
TODAY_SHORT=$(date '+%a %b %-d, %Y')
NEXT_2_WEEKS=$(date -d '+14 days' '+%Y-%m-%dT00:00:00')
TODAY_ISO=$(date '+%Y-%m-%dT00:00:00')

PROMPT="Today is ${TODAY_LONG}.

Your job is to generate a morning email briefing for Richard Wells. Follow these steps exactly:

STEP 1 - Fetch recent emails:
Use mcp__Gmail__search_threads with query: newer_than:7d -in:sent -in:draft -category:promotions -category:social
Get up to 50 threads.

STEP 2 - Fetch upcoming calendar events:
Use mcp__Google-Calendar__list_events with startTime '${TODAY_ISO}' and endTime '${NEXT_2_WEEKS}', orderBy startTime, pageSize 50.

STEP 3 - Analyze and rank:
From the email threads and calendar events, identify the TOP 10 most important items Richard needs to act on. Prioritize by:
- Urgency (deadlines today or this week rank highest)
- Health/safety alerts
- Financial actions required
- School/family events needing response
- Church/leadership responsibilities pending
- Upcoming events needing preparation

STEP 4 - Identify unusual calendar events:
Flag any calendar events that appear out of the ordinary: cancellations, all-day projects, unusual timing, special one-off events (not recurring daily/weekly habits).

STEP 5 - Draft the email:
Use mcp__Gmail__create_draft to create an HTML email to ${RECIPIENT} with:
- Subject: 'Morning Briefing - Top 10 Action Items & Calendar — ${TODAY_SHORT}'
- A numbered top-10 list with emoji indicators for priority/category
- A section for unusual/notable calendar events
- Clean HTML formatting using inline styles (max-width 680px, Arial font)
- A small footer noting the email was auto-generated

Do NOT include calendar notifications (calendar-notification@google.com emails) in the email analysis — those are noise. Focus on human-sent or service-alert emails.

Complete all 5 steps now."

log "Running Claude with briefing prompt..."

"$CLAUDE_BIN" \
  --no-color \
  --print \
  --allowedTools "mcp__Gmail__search_threads,mcp__Gmail__get_thread,mcp__Gmail__create_draft,mcp__Google-Calendar__list_events" \
  -p "$PROMPT" \
  >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  log "Morning briefing draft created successfully."
else
  log "ERROR: Claude exited with code $EXIT_CODE. Check log for details."
fi

log "========== Morning Briefing Finished =========="
exit $EXIT_CODE
