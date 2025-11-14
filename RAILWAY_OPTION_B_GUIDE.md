# Railway Deployment Guide - Option B (Hybrid Architecture)

## Overview

This guide helps you deploy the Keeper Discord Bot to Railway while keeping your VH-Database.db on your local computer.

**Architecture:**
```
[Railway Cloud]
  ├─ Keeper Bot (24/7)
  ├─ keeper.db (discoveries storage)
  └─ HTTP Client
       ↓
   [Internet via ngrok]
       ↓
[Your Local Computer]
  ├─ local_sync_api.py (Flask server)
  └─ VH-Database.db (master database)
```

## Prerequisites

1. ✅ Python 3.8+ installed
2. ✅ Discord bot token (from Discord Developer Portal)
3. ✅ Railway account (free tier works)
4. ✅ ngrok account (free tier works) - Download from https://ngrok.com/download

---

## Step 1: Setup Local Sync API Server

### 1.1 Install Flask dependencies

```bash
cd c:\Users\parke\OneDrive\Desktop\Haven_mdev
pip install flask flask-cors
```

### 1.2 Generate a secure API key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output (e.g., `a1b2c3d4e5f6...`) - you'll need this later.

### 1.3 Update local_sync_api.py with your API key

Open `local_sync_api.py` and change line 32:

```python
API_KEY = os.getenv('HAVEN_API_KEY', 'PUT-YOUR-API-KEY-HERE')
```

Or set it as an environment variable:

```bash
set HAVEN_API_KEY=your-api-key-here
```

### 1.4 Test the local API server

```bash
python local_sync_api.py
```

You should see:
```
====================================== Haven Local Sync API Server
Database: C:\Users\parke\OneDrive\Desktop\Haven_mdev\data\VH-Database.db
Database exists: True
API Key: a1b2c3d4e5... (use this in Railway environment)

Next steps:
1. Keep this server running on your computer
2. Run: ngrok http 5000
3. Copy the ngrok URL (e.g., https://abc123.ngrok.io)
...
====================================
 * Running on http://0.0.0.0:5000
```

**Keep this terminal window open!**

---

## Step 2: Expose Local Server with ngrok

### 2.1 Install ngrok

Download from https://ngrok.com/download and follow install instructions.

### 2.2 Authenticate ngrok (one-time setup)

```bash
ngrok config add-authtoken YOUR_NGROK_AUTH_TOKEN
```

Get your auth token from https://dashboard.ngrok.com/get-started/your-authtoken

### 2.3 Start ngrok tunnel

```bash
ngrok http 5000
```

You'll see output like:
```
Session Status                online
Account                       your@email.com
Forwarding                    https://abc123xyz.ngrok.io -> http://localhost:5000
```

**Copy the HTTPS URL** (e.g., `https://abc123xyz.ngrok.io`) - you'll need it for Railway!

**Keep this terminal window open too!**

### 2.4 Test the tunnel

Open your browser and visit:
```
https://abc123xyz.ngrok.io/health
```

You should see:
```json
{
  "status": "healthy",
  "database_accessible": true,
  "timestamp": "2025-11-13T..."
}
```

✅ If you see this, your local API is working!

---

## Step 3: Deploy Bot to Railway

### 3.1 Create Railway project

1. Go to https://railway.app/
2. Click "Start a New Project"
3. Choose "Deploy from GitHub repo"
4. Connect your GitHub account
5. Select your Haven_mdev repository

### 3.2 Configure Environment Variables

In Railway dashboard, go to **Variables** tab and add:

```bash
# Discord Configuration
BOT_TOKEN=MTQzNjUxMDk3MTQ0NjQyNzcyMA.GEGA-B.2ejU-aQHsggtJcvA1qFZzKNNuAE2jWVgdCOaxU
GUILD_ID=1423941004230135851

# Haven Sync API (CRITICAL!)
HAVEN_SYNC_API_URL=https://abc123xyz.ngrok.io/api
HAVEN_API_KEY=your-api-key-from-step-1.2

# Database Config
DATABASE_PATH=./data/keeper.db
USE_HAVEN_DATABASE=false
DEBUG_MODE=false

# Discord Channels
DISCOVERY_CHANNEL_ID=1436451765032849468
ARCHIVE_CHANNEL_ID=1436451809915834479
INVESTIGATION_CHANNEL_ID=1436451896494653520
LORE_DISCUSSION_CHANNEL_ID=1436451932846948392

# Admin Role
ADMIN_ROLE_ID=1436890437909610618

# Pattern Recognition
MIN_DISCOVERIES_FOR_PATTERN=3
AUTO_PATTERN_THRESHOLD=0.75
PATTERN_SIMILARITY_THRESHOLD=0.6
```

⚠️ **Important:**
- Replace `https://abc123xyz.ngrok.io` with YOUR ngrok URL from Step 2.3
- Replace the API key with YOUR key from Step 1.2
- The ngrok URL will change every time you restart ngrok (free tier). See Step 5 for permanent solution.

### 3.3 Deploy

Railway will automatically:
1. Detect `Procfile`
2. Install dependencies from `requirements.txt`
3. Run the bot with `python src/main.py`

Check the **Logs** tab to see:
```
The Keeper awakens...
✅ Haven integration initialized
🔄 Sync worker started (interval: 30s)
Logged in as The Keeper#1234
```

✅ **If you see this, your bot is live on Railway!**

---

## Step 4: Test the Integration

### 4.1 Test discovery command

In Discord:
```
/discovery-report
```

You should see:
1. ✅ System dropdown with your 5 Haven systems
2. ✅ Planet/location dropdown
3. ✅ Discovery type selection
4. ✅ Modal for discovery details

### 4.2 Submit a test discovery

Complete the form and submit. Check:

1. **Railway logs:** Should show discovery saved to keeper.db
2. **Local API logs:** Should show HTTP POST request received
3. **VH-Database.db:** Open Haven Control Room → View Discoveries
   - Your test discovery should appear!

✅ **If all 3 work, you're fully integrated!**

---

## Step 5: Make ngrok URL Permanent (Optional but Recommended)

**Problem:** Free ngrok URLs change every restart.

**Solution:** Upgrade to ngrok paid plan ($8/month) for permanent domain:
- Go to https://dashboard.ngrok.com/cloud-edge/domains
- Create a reserved domain (e.g., `haven-sync.ngrok.io`)
- Update Railway's `HAVEN_SYNC_API_URL` once
- Done! URL never changes again.

**Alternative (Free):** Use a free dynamic DNS service like No-IP or Duck DNS, but this is more complex.

---

## Step 6: Daily Operations

### Starting Everything

**Every time you boot your computer:**

1. **Terminal 1:** Start local API
   ```bash
   cd c:\Users\parke\OneDrive\Desktop\Haven_mdev
   python local_sync_api.py
   ```

2. **Terminal 2:** Start ngrok
   ```bash
   ngrok http 5000
   ```

3. **If ngrok URL changed:** Update Railway's `HAVEN_SYNC_API_URL` variable

4. **Railway bot:** Automatically restarts and reconnects

### Stopping Everything

- Close both terminal windows
- Railway bot will lose connection to VH-Database (but stays online)
- Discoveries will queue and sync when you restart local API

---

## Troubleshooting

### Bot says "Haven star map integration unavailable"

**Cause:** Bot can't reach your local API

**Fix:**
1. Check local API is running (Terminal 1)
2. Check ngrok is running (Terminal 2)
3. Check Railway `HAVEN_SYNC_API_URL` matches current ngrok URL
4. Check Railway `HAVEN_API_KEY` matches local API key
5. Check ngrok URL in browser: `https://your-url.ngrok.io/health`

### Discoveries don't appear in VH-Database

**Cause:** Sync queue is failing

**Check Railway logs for:**
```
❌ Failed to write discovery to VH-Database: Connection refused
```

**Fix:**
1. Verify ngrok URL is correct
2. Verify API key matches
3. Check local API logs for incoming requests
4. Use `/haven-export` command to manually export

### ngrok URL keeps changing

**Temporary fix:** Update Railway environment variable after each restart

**Permanent fix:** Upgrade to ngrok paid plan ($8/month) for reserved domain

---

## Cost Breakdown

| Service | Plan | Cost |
|---------|------|------|
| Railway | Hobby (500 hrs/month) | $5-10/month |
| ngrok (temp URL) | Free | $0 |
| ngrok (permanent) | Basic | $8/month |
| **Total (temp URL)** | | **$5-10/month** |
| **Total (permanent)** | | **$13-18/month** |

---

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│         Discord Users                    │
│  /discovery-report, /search, etc.       │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│      Railway Cloud (24/7)               │
│  ┌─────────────────────────────────┐   │
│  │  Keeper Discord Bot              │   │
│  │  - Receives commands             │   │
│  │  - Stores to keeper.db          │   │
│  │  - Queues for sync              │   │
│  └──────────────┬──────────────────┘   │
│                 │                        │
│  ┌──────────────▼──────────────────┐   │
│  │  Sync Worker (every 30s)        │   │
│  │  - Reads queue                  │   │
│  │  - HTTP POST to local API       │   │
│  └──────────────┬──────────────────┘   │
└─────────────────┼───────────────────────┘
                  │ HTTPS
                  ▼
┌─────────────────────────────────────────┐
│      ngrok.io (Tunnel)                  │
│  https://abc123.ngrok.io → localhost    │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  Your Local Computer (must stay on)    │
│  ┌─────────────────────────────────┐   │
│  │  local_sync_api.py (Flask)      │   │
│  │  - Receives HTTP POST           │   │
│  │  - Writes to VH-Database.db     │   │
│  │  - Returns success              │   │
│  └──────────────┬──────────────────┘   │
│                 │                        │
│  ┌──────────────▼──────────────────┐   │
│  │  VH-Database.db (Master)        │   │
│  │  - Systems, planets, moons      │   │
│  │  - Discoveries                  │   │
│  └─────────────────────────────────┘   │
│                 │                        │
│  ┌──────────────▼──────────────────┐   │
│  │  Haven Control Room (GUI)       │   │
│  │  - View discoveries             │   │
│  │  - Generate maps                │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## Next Steps

1. ✅ Complete this setup guide
2. ✅ Test with a few discoveries
3. ✅ Invite friends to your Discord server
4. ✅ Monitor Railway logs for issues
5. ✅ Consider upgrading ngrok for permanent URL
6. 📖 Read the bot docs for advanced features

---

## Support

- Bot not working? Check Railway logs
- API issues? Check local_sync_api.py logs
- Need help? Create an issue on GitHub

---

**Last updated:** 2025-11-13
**Version:** Option B - Hybrid Architecture
