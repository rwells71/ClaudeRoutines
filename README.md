# ClaudeRoutines

Automated Claude Code routines that run on a schedule via GitHub Actions.

---

## Morning Email & Calendar Digest

**File**: `prompts/morning-digest.md`  
**Workflow**: `.github/workflows/morning-digest.yml`

Runs every day at **5:00 AM Mountain Time** (DST-aware). It:

1. Fetches all non-promotional emails from the last 24 hours
2. Fetches today's non-recurring Google Calendar events
3. Summarizes each email with key points and action items, grouped by sender
4. Sends an HTML digest email to yourself via Gmail

### How it works

The workflow uses `anthropics/claude-code-action@v1` with a `claude_code_oauth_token`.
When this token belongs to a Claude.ai account that has **Gmail** and **Google Calendar**
connected (via Settings → Integrations), the action inherits those MCP integrations and
can read/write on your behalf.

### One-time setup

1. **Get your Claude.ai OAuth token**
   - Open [claude.ai/code](https://claude.ai/code), open your browser DevTools → Application → Cookies
   - Copy the value of the `sessionKey` cookie (starts with `sk-ant-...`)

2. **Add the token as a GitHub secret**
   - Go to your repo → **Settings → Secrets and variables → Actions**
   - Create a secret named `CLAUDE_CODE_OAUTH_TOKEN` with that value

3. **Confirm your Google integrations are connected**
   - In Claude.ai → **Settings → Integrations**, verify Gmail and Google Calendar are authorized

4. **Test it manually**
   - Go to **Actions → Morning Email & Calendar Digest → Run workflow**

### Schedule

| Months | Cron | Reason |
|--------|------|--------|
| March – October | `0 11 * 3-10 *` | 5 AM MDT (UTC−6) |
| November – February | `0 12 * 1,2,11,12 *` | 5 AM MST (UTC−7) |
