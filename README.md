# ClaudeRoutines

Automated routines powered by [Claude Code Action](https://github.com/anthropics/claude-code-action).

## Prerequisites

Add the following secret to your repository (**Settings → Secrets and variables → Actions**):

| Secret | Description |
|---|---|
| `CLAUDE_CODE_OAUTH_TOKEN` | OAuth token for Claude Code (required by all workflows) |

Claude Code Action also needs access to your **Gmail** and **Google Calendar** MCP integrations, configured in your Claude Code account.

---

## Morning Email & Calendar Digest

**Workflow**: `.github/workflows/morning-digest.yml`
**Prompt**: `prompts/morning-digest.md`

Runs automatically at **5:00 AM Mountain Time** every day (DST-aware). You can also trigger it manually via **Actions → Morning Email & Calendar Digest → Run workflow**.

### What it does

1. **Email summary** — searches Gmail for all non-promotional, non-automated threads from the last 24 hours. For each sender, produces:
   - Subject line
   - 2–4 key-point bullets
   - Action items (when present)

2. **Calendar events** — lists today's Google Calendar events and keeps only **one-time (non-recurring)** events, shown with time, title, location, and description.

3. **Digest delivery** — creates an HTML email addressed to you and places it directly in your inbox (draft + `INBOX` label, since the Gmail MCP has no send API).

### Filters applied

- Skips Gmail categories: Promotions, Social, Updates
- Skips senders with `noreply@`, `no-reply@`, `donotreply@`, or `notifications@` addresses
- Skips messages with a `List-Unsubscribe` header
- Drops any calendar event that has a `recurringEventId` or `recurrence` field

---

## Claude Code (issue & PR assistant)

**Workflow**: `.github/workflows/claude.yml`

Tag `@claude` in any issue or PR comment to invoke Claude for code assistance.

## Claude Code Review

**Workflow**: `.github/workflows/claude-code-review.yml`

Automatically reviews every pull request using the `code-review` plugin.
