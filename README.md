# dataisbeautiful-bot

A Reddit bot for [r/dataisbeautiful](https://www.reddit.com/r/dataisbeautiful/) that automatically rewards OC (Original Content) posters with flair and a sticky comment linking to their citations.

This is a maintained fork of [r-dataisbeautiful/dataisbeautiful-bot](https://github.com/r-dataisbeautiful/dataisbeautiful-bot).

## What it does

1. Scans the 100 newest posts in r/dataisbeautiful
2. Finds approved posts with `[OC]` in the title that haven't been processed yet
3. Looks for the OP's root-level comment (where they post their data source/citation)
4. Updates their OC flair (e.g. `OC: 5`)
5. Posts a sticky distinguished comment linking to their citation

## Running via GitHub Actions (recommended)

The bot runs automatically once a day at 06:07 UTC via GitHub Actions — no server needed.

### Setup

1. Go to **Settings → Secrets and variables → Actions** in your repo and add three secrets:
   - `CLIENT_ID` — your Reddit app client ID
   - `CLIENT_SECRET` — your Reddit app client secret
   - `ACCT_PASSWD` — the bot account's password
2. Go to the **Actions** tab and enable workflows
3. The bot will run daily, or trigger it manually via **Run workflow**

### Creating Reddit API credentials

- Go to https://www.reddit.com/prefs/apps (logged in as the bot account)
- Click **create another app** → type: **script**
- Redirect URI: `http://localhost:8080`
- Copy the client ID (shown under the app name) and client secret

## Running locally

```bash
pip install -r requirements.txt

export CLIENT_ID="your_client_id"
export CLIENT_SECRET="your_client_secret"
export ACCT_PASSWD="bot_account_password"

python app.py
```
