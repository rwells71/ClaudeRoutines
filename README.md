# ClaudeRoutines

Automated daily routines powered by [Claude Code on the Web](https://code.claude.com/docs/en/claude-code-on-the-web) and GitHub Actions.

---

## Morning Email & Calendar Digest

Runs every day at **5:00 AM Mountain Time** and delivers a personalized digest to your inbox.

### What it does

| Requirement | Implementation |
|---|---|
| Runs at 5:00 AM Mountain daily | DST-aware cron in `morning-digest.yml` (UTC 11 summer / UTC 12 winter) |
| Last 24 hours of email | `newer_than:1d` Gmail query, filters out promotions/social/updates |
| Summarize key points + action items | 2–4 bullets per email; concrete action items in a separate section |
| Group by sender | One heading per sender address |
| Styled HTML digest | Blue/green card layout |
| Delivered as email-to-self | `create_draft` → `label_message` with `INBOX + UNREAD + IMPORTANT` |
| Non-recurring calendar events only | Filters out events with `recurringEventId` or `recurrence` fields |

### Files

- `prompts/morning-digest.md` — the step-by-step prompt Claude follows each morning
- `.github/workflows/morning-digest.yml` — GitHub Actions workflow that triggers Claude

### Setup

1. Add a repository secret named `CLAUDE_CODE_OAUTH_TOKEN` (your Claude Code OAuth token).
2. Ensure the Gmail and Google Calendar MCP integrations are authorized in your Claude Code account.
3. Push this repo to GitHub — the workflow runs automatically on schedule, or trigger it manually via **Actions → Morning Email & Calendar Digest → Run workflow**.

### Manual trigger

Go to **Actions → Morning Email & Calendar Digest → Run workflow** to run it immediately and verify the digest arrives in your inbox.
