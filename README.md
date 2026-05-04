# ClaudeRoutines

Automated Claude Code routines that run on a schedule via GitHub Actions.

---

## Morning Email & Calendar Digest

Every morning at **5:00 AM Mountain Time**, Claude reads your Gmail and Google Calendar and emails you a structured digest.

### What it does

1. **Fetches the last 24 hours of email** — skips marketing, newsletters, and automated no-reply messages; keeps everything human-sent or transactional.
2. **Summarizes each email** — subject line, 2–4 key-point bullets, and a separate Action Items list when concrete tasks are required.
3. **Groups summaries by sender** — one heading per sender, with all their emails listed beneath it.
4. **Fetches today's non-recurring calendar events** — one-time events only; recurring series are excluded.
5. **Delivers the digest to your inbox** — creates an HTML email and places it directly in your Gmail inbox so it arrives like a normal message.

### Schedule

| Period | Cron (UTC) | Local time |
|---|---|---|
| Mar – Oct (MDT, UTC-6) | `0 11 * 3-10 *` | 5:00 AM MDT |
| Nov – Feb (MST, UTC-7) | `0 12 * 1,2,11,12 *` | 5:00 AM MST |

You can also trigger it manually from **Actions → Morning Email & Calendar Digest → Run workflow**.

### Required secret

| Secret | Description |
|---|---|
| `CLAUDE_CODE_OAUTH_TOKEN` | OAuth token for Claude Code (needed for MCP access to Gmail and Google Calendar) |

Set this in **Settings → Secrets and variables → Actions**.

### Files

| File | Purpose |
|---|---|
| `.github/workflows/morning-digest.yml` | GitHub Actions workflow — schedule, permissions, allowed MCP tools |
| `prompts/morning-digest.md` | Step-by-step prompt Claude follows at runtime |

---

## Adding a new routine

1. Add a prompt file under `prompts/`.
2. Add a workflow under `.github/workflows/` that reads the prompt and passes it to `anthropics/claude-code-action@v1`.
3. List only the MCP tools your prompt needs in `allowed_tools`.
