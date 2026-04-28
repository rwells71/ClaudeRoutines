# Daily 5 AM Briefing

Sends a daily email to `richardlwells@gmail.com` at 5 AM with:
- **Top 10 action items** from the last 7 days of Gmail
- **Noteworthy calendar events** from the next 14 days

## One-time setup

### 1. Google Cloud credentials

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create or select a project
3. Enable **Gmail API** and **Google Calendar API**
4. Go to **APIs & Services → Credentials → Create OAuth 2.0 Client ID**
   - Application type: **Desktop app**
5. Download the JSON and save it to:
   ```
   ~/.config/daily_briefing/credentials.json
   ```

### 2. Authorise (interactive, run once)

```bash
python3 /home/user/ClaudeRoutines/daily_briefing/briefing.py --setup
```

A browser window will open. Sign in with richardlwells@gmail.com.  
The refresh token is saved to `~/.config/daily_briefing/token.json` — subsequent runs are fully unattended.

### 3. Anthropic API key

Create `/home/user/ClaudeRoutines/daily_briefing/.env`:

```
ANTHROPIC_API_KEY=sk-ant-...your-key-here...
```

Or export it in your shell profile:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### 4. Install Python dependencies (if not already installed)

```bash
pip3 install google-auth google-auth-oauthlib google-api-python-client anthropic
```

### 5. Set up the 5 AM cron job

```bash
crontab -e
```

Add this line (adjust path if needed):

```
0 5 * * * /usr/bin/python3 /home/user/ClaudeRoutines/daily_briefing/briefing.py >> /var/log/daily_briefing.log 2>&1
```

## Test run

```bash
python3 /home/user/ClaudeRoutines/daily_briefing/briefing.py
```

## Customisation

Edit the constants at the top of `briefing.py`:

| Variable | Default | Description |
|---|---|---|
| `RECIPIENT_EMAIL` | richardlwells@gmail.com | Where to send the briefing |
| `EMAIL_LOOKBACK_DAYS` | 7 | Days of email history to scan |
| `CALENDAR_LOOKAHEAD_DAYS` | 14 | Days ahead to check calendar |
| `CLAUDE_MODEL` | claude-sonnet-4-6 | Claude model to use |
