# Haven Keeper Bot - Quick Start Guide

## 🚀 First Time Setup (One-time)

### 1. Install Python Dependencies
```bash
pip install flask flask-cors aiohttp
```

### 2. Install ngrok
- Download from: https://ngrok.com/download
- Run: `ngrok config add-authtoken YOUR_TOKEN`
- Get token from: https://dashboard.ngrok.com/get-started/your-authtoken

### 3. Generate API Key
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Save this key - you'll need it for Railway!

---

## 🎮 Daily Usage (Every Time)

### Step 1: Start Local API Server
**Double-click:** `start_local_api.bat`

Or manually:
```bash
python local_sync_api.py
```

✅ You should see: `Running on http://0.0.0.0:5000`

### Step 2: Start ngrok Tunnel
**Double-click:** `start_ngrok.bat`

Or manually:
```bash
ngrok http 5000
```

✅ Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### Step 3: Update Railway (if ngrok URL changed)
1. Go to https://railway.app/
2. Open your project
3. Click **Variables** tab
4. Update `HAVEN_SYNC_API_URL` to: `https://YOUR-NEW-URL.ngrok.io/api`
5. Save (Railway will auto-restart bot)

### Step 4: Test in Discord
```
/discovery-report
```

---

## 📊 How to Check If It's Working

### ✅ Local API Health Check
Open in browser: `http://localhost:5000/health`

Should show:
```json
{
  "status": "healthy",
  "database_accessible": true
}
```

### ✅ ngrok Tunnel Check
Open in browser: `https://your-url.ngrok.io/health`

Should show the same response.

### ✅ Bot Status Check
In Discord:
```
/discovery-report
```

Should show your 5 Haven systems in dropdown!

### ✅ Full Integration Check
1. Submit a test discovery via `/discovery-report`
2. Check Railway logs: "Discovery queued for sync"
3. Check local API logs: "POST /api/discoveries"
4. Open Haven Control Room → View Discoveries
5. Your test discovery should appear!

---

## 🛑 Stopping Everything

1. Close `start_local_api.bat` window (or press Ctrl+C)
2. Close `start_ngrok.bat` window (or press Ctrl+C)
3. Railway bot stays online but can't sync to VH-Database

---

## ⚠️ Common Issues

### "Haven star map integration unavailable"

**Cause:** Bot can't reach local API

**Fix:**
1. ✅ Local API running? Check `start_local_api.bat`
2. ✅ ngrok running? Check `start_ngrok.bat`
3. ✅ Railway `HAVEN_SYNC_API_URL` correct?
4. ✅ Railway `HAVEN_API_KEY` matches local key?

### "Discovery not syncing to VH-Database"

**Check Railway Logs:**
```
🔄 Processing 1 pending discoveries for sync
❌ Failed to write discovery: Connection refused
```

**Fix:**
1. Verify ngrok URL is correct in Railway
2. Test ngrok URL in browser
3. Check local API is receiving requests

### ngrok URL changed

**This happens every time you restart ngrok (free tier)**

**Fix:**
1. Copy new ngrok URL
2. Update Railway `HAVEN_SYNC_API_URL`
3. Add `/api` to the end!

**Permanent Solution:** Upgrade ngrok to paid ($8/month) for reserved domain

---

## 📁 File Structure

```
Haven_mdev/
├── local_sync_api.py          ← Flask API server
├── start_local_api.bat        ← Double-click to start API
├── start_ngrok.bat            ← Double-click to start ngrok
├── test_bot_locally.bat       ← Test bot on your PC
│
├── Procfile                   ← Railway deployment config
├── requirements.txt           ← Python dependencies
├── .env.railway               ← Railway environment template
│
├── data/
│   └── VH-Database.db         ← Your master database
│
└── docs/guides/Haven-lore/keeper-bot/
    └── src/
        ├── main.py            ← Bot entry point
        └── core/
            └── haven_integration_http.py  ← HTTP API integration
```

---

## 🎯 Architecture Summary

```
[Your PC]                    [Internet]              [Railway Cloud]
  │                              │                         │
  ├─ VH-Database.db             │                    ┌─────────┐
  │                              │                    │ Keeper  │
  ├─ local_sync_api.py ─────────┼───────────────────>│  Bot    │
  │  (port 5000)                 │                    └─────────┘
  │                              │                         │
  └─ ngrok tunnel ──────────────┘                         │
     (https://abc.ngrok.io)                                │
                                                    Stores to keeper.db
                                                    Syncs every 30s
```

**Data Flow:**
1. User runs `/discovery-report` in Discord
2. Railway bot shows systems from HTTP API
3. User submits discovery → saved to keeper.db (instant)
4. Sync worker queues for VH-Database sync
5. Every 30s: HTTP POST to your local API
6. Local API writes to VH-Database.db
7. You see discovery in Haven Control Room!

---

## 📞 Need Help?

1. **Bot issues:** Check Railway logs
2. **API issues:** Check local_sync_api.py output
3. **Integration issues:** Read RAILWAY_OPTION_B_GUIDE.md
4. **Still stuck:** Create GitHub issue

---

**Quick Reference:**
- Local API: `http://localhost:5000`
- Health Check: `http://localhost:5000/health`
- Railway Dashboard: https://railway.app/
- ngrok Dashboard: https://dashboard.ngrok.com/

---

**Last updated:** 2025-11-13
