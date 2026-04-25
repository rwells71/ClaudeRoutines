# ClaudeRoutines

Automated daily email digest: top-10 action items from your Gmail + notable
calendar events, delivered at 5 AM every morning via GitHub Actions.

---

## What it does

Every morning the workflow:
1. Fetches your last 7 days of Gmail (excluding Promotions / Social)
2. Fetches calendar events for the next 14 days
3. Asks Claude (Opus) to distil a **Top 10 Action Items** list and flag any
   **Notable Calendar Events**
4. Emails the digest to you

---

## One-time setup

### 1. Create a Google Cloud project & OAuth credentials

1. Go to <https://console.cloud.google.com/> → **New Project**
2. Enable **Gmail API** and **Google Calendar API**
   (APIs & Services → Library → search each → Enable)
3. APIs & Services → **Credentials** → **Create Credentials** → **OAuth client ID**
   - Application type: **Desktop app** (easiest for getting a refresh token)
   - Download the JSON — note `client_id` and `client_secret`
4. APIs & Services → **OAuth consent screen** → add your Gmail address as a
   **Test user** (required while the app is in "Testing" mode)

### 2. Get a refresh token (one-time browser flow)

Run this locally (Python 3.9+, needs `google-auth-oauthlib`):

```bash
pip install google-auth-oauthlib
python - <<'EOF'
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.readonly",
]

flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
creds = flow.run_local_server(port=0)
print("CLIENT_ID    :", creds.client_id)
print("CLIENT_SECRET:", creds.client_secret)
print("REFRESH_TOKEN:", creds.refresh_token)
EOF
```

Copy the three printed values — you'll need them in the next step.

### 3. Add GitHub Secrets

In your GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**:

| Secret name            | Value                                        |
|------------------------|----------------------------------------------|
| `ANTHROPIC_API_KEY`    | Your Anthropic API key                       |
| `GOOGLE_CLIENT_ID`     | OAuth client ID from step 2                  |
| `GOOGLE_CLIENT_SECRET` | OAuth client secret from step 2              |
| `GOOGLE_REFRESH_TOKEN` | Refresh token from step 2                    |
| `RECIPIENT_EMAIL`      | The address to send the digest to (your Gmail)|

### 4. Adjust the send time (optional)

The workflow runs at **5:00 AM UTC**. Edit `.github/workflows/daily-digest.yml`
and change the cron hour:

| Your timezone | UTC offset | Cron hour |
|---------------|------------|-----------|
| US Eastern    | −5 / −4    | `10` / `9`|
| US Central    | −6 / −5    | `11` / `10`|
| US Pacific    | −8 / −7    | `13` / `12`|
| UK (GMT)      | 0 / +1     | `5` / `4` |
| CET           | +1 / +2    | `4` / `3` |

### 5. Test it manually

GitHub → **Actions** → **Daily Morning Digest** → **Run workflow** → **Run workflow**.
Check your inbox in ~1 minute.

---

## Files

| File | Purpose |
|------|---------|
| `gmail_digest.py` | Main script — fetch, summarise, send |
| `requirements.txt` | Python dependencies |
| `.github/workflows/daily-digest.yml` | Scheduled GitHub Actions job |
