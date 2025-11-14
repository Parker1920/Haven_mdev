# NGROK 401 UNAUTHORIZED ERROR - FIX GUIDE

## Problem Summary
The Discord bot hosted on Railway was getting 401 Unauthorized errors when trying to write discoveries to the local VH-Database through the ngrok tunnel.

## Root Cause
**API Key Mismatch:**
- Railway bot was sending: `b14191847f8d166c3ddc3ec0d55fa1a86c644511ffb187ddaf7a8ec68de94aeb`
- Local API server was expecting: `your-secret-key-here-change-me` (default placeholder)

## Solution Applied

### 1. Created `.env` file in Haven_mdev root
**File:** `C:\Users\parke\OneDrive\Desktop\Haven_mdev\.env`

Contains:
```env
HAVEN_API_KEY=b14191847f8d166c3ddc3ec0d55fa1a86c644511ffb187ddaf7a8ec68de94aeb
```

### 2. Updated `local_sync_api.py` to load .env file
Added `python-dotenv` import and `load_dotenv()` call to automatically load environment variables from `.env` file.

**Changed lines 15-26:**
```python
import os
import json
import sqlite3
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
```

---

## How to Start the System

### Step 1: Start Local API Server
Open **Terminal 1** (Command Prompt or PowerShell):
```bash
cd C:\Users\parke\OneDrive\Desktop\Haven_mdev
start_local_api.bat
```

**Expected Output:**
```
========================================
  Haven Local Sync API Server
========================================

Starting Flask API server on port 5000...
This server exposes VH-Database.db to Railway bot

KEEP THIS WINDOW OPEN while using the bot!

========================================

 * Serving Flask app 'local_sync_api'
 * Debug mode: on
API Key: b14191847... (use this in Railway environment)
 * Running on http://127.0.0.1:5000
```

**IMPORTANT:** Look for the line that says `API Key: b14191847...` - this confirms the .env file is being loaded correctly!

### Step 2: Start ngrok Tunnel
Open **Terminal 2** (Command Prompt or PowerShell):
```bash
ngrok http 5000
```

**Expected Output:**
```
ngrok                                                               (Ctrl+C to quit)

Session Status                online
Account                       [your account]
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://[random-string].ngrok-free.app -> http://localhost:5000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**COPY THE FORWARDING URL!** You'll need this for Railway.

---

## Configuration Check

### Local Configuration (Haven_mdev)
**File:** `C:\Users\parke\OneDrive\Desktop\Haven_mdev\.env`
```env
HAVEN_API_KEY=b14191847f8d166c3ddc3ec0d55fa1a86c644511ffb187ddaf7a8ec68de94aeb
```

### Railway Configuration (keeper-discord-bot-main)
**Required Environment Variables on Railway:**

Go to Railway Dashboard → Your Project → Variables:

```env
BOT_TOKEN=MTQzNjUxMDk3MTQ0NjQyNzcyMA.GGCdyg.TsFhnSMtbpUj_fZQLhndqufAsud6JhlhBEh0LU
GUILD_ID=1423941004230135851
HAVEN_SYNC_API_URL=https://[your-ngrok-url].ngrok-free.app
HAVEN_API_KEY=b14191847f8d166c3ddc3ec0d55fa1a86c644511ffb187ddaf7a8ec68de94aeb
USE_HAVEN_DATABASE=true
DEBUG_MODE=true
```

**IMPORTANT:** The `HAVEN_SYNC_API_URL` must match your current ngrok URL!

### Current Expected ngrok URL
Based on the keeper-bot configuration, Railway expects:
```
HAVEN_SYNC_API_URL=https://bleachable-unwieldy-luciano.ngrok-free.dev
```

**If your ngrok URL changed:**
1. Copy the new URL from ngrok terminal
2. Update Railway environment variable `HAVEN_SYNC_API_URL`
3. Restart the Railway deployment

---

## Testing Authentication

### Test 1: Health Check (Local)
In **Terminal 3**, test the local API with the correct API key:

```bash
curl -H "X-API-Key: b14191847f8d166c3ddc3ec0d55fa1a86c644511ffb187ddaf7a8ec68de94aeb" http://localhost:5000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-14T..."
}
```

### Test 2: Health Check (Through ngrok)
Test through the ngrok tunnel:

```bash
curl -H "X-API-Key: b14191847f8d166c3ddc3ec0d55fa1a86c644511ffb187ddaf7a8ec68de94aeb" https://[your-ngrok-url].ngrok-free.app/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-14T..."
}
```

### Test 3: Systems Endpoint (Verify Database Access)
```bash
curl -H "X-API-Key: b14191847f8d166c3ddc3ec0d55fa1a86c644511ffb187ddaf7a8ec68de94aeb" http://localhost:5000/api/systems
```

**Expected Response:**
```json
{
  "systems": [
    {
      "id": 1,
      "name": "Venture",
      "abbreviation": "VT",
      ...
    },
    ...
  ]
}
```

### Test 4: Test with WRONG API Key (Should Fail)
```bash
curl -H "X-API-Key: wrong-key-123" http://localhost:5000/health
```

**Expected Response (401 Unauthorized):**
```json
{
  "error": "Unauthorized"
}
```

---

## PowerShell Test Commands

If using PowerShell instead of curl:

### Test Local API:
```powershell
$headers = @{
    "X-API-Key" = "b14191847f8d166c3ddc3ec0d55fa1a86c644511ffb187ddaf7a8ec68de94aeb"
}
Invoke-RestMethod -Uri "http://localhost:5000/health" -Headers $headers -Method Get
```

### Test ngrok Tunnel:
```powershell
$headers = @{
    "X-API-Key" = "b14191847f8d166c3ddc3ec0d55fa1a86c644511ffb187ddaf7a8ec68de94aeb"
}
Invoke-RestMethod -Uri "https://[your-ngrok-url].ngrok-free.app/health" -Headers $headers -Method Get
```

---

## Troubleshooting

### Issue: Still getting 401 Unauthorized

**Check 1: Verify .env file exists**
```bash
dir C:\Users\parke\OneDrive\Desktop\Haven_mdev\.env
```

**Check 2: Verify API key in .env**
```bash
type C:\Users\parke\OneDrive\Desktop\Haven_mdev\.env
```
Should show: `HAVEN_API_KEY=b14191847f8d166c3ddc3ec0d55fa1a86c644511ffb187ddaf7a8ec68de94aeb`

**Check 3: Restart local API server**
- Stop the `start_local_api.bat` terminal (Ctrl+C)
- Run `start_local_api.bat` again
- Look for the startup message showing the API key

**Check 4: Verify Railway environment variables**
- Log into Railway Dashboard
- Go to your project → Variables tab
- Verify `HAVEN_API_KEY` matches local `.env` file
- Verify `HAVEN_SYNC_API_URL` matches current ngrok URL

### Issue: ngrok URL keeps changing

**Solution:** Use ngrok's static domain feature (requires paid plan) OR update Railway environment variable each time you restart ngrok.

**Quick Update Script** (PowerShell):
```powershell
# After starting ngrok, get the URL and update this variable:
$ngrokUrl = "https://your-new-ngrok-url.ngrok-free.app"

# Then manually update Railway environment variable HAVEN_SYNC_API_URL
Write-Host "Update Railway HAVEN_SYNC_API_URL to: $ngrokUrl"
```

### Issue: Railway bot can't reach ngrok

**Check 1: ngrok is running**
- Terminal 2 should show ngrok forwarding status
- Visit http://127.0.0.1:4040 to see ngrok web interface

**Check 2: Firewall**
- Ensure ngrok can accept incoming connections
- Check Windows Firewall settings

**Check 3: ngrok account limits**
- Free ngrok accounts have connection limits
- Check ngrok dashboard for any issues

### Issue: Database errors

**Check 1: Database path**
Verify the database exists:
```bash
dir C:\Users\parke\OneDrive\Desktop\Haven_mdev\data\VH-Database.db
```

**Check 2: Database permissions**
Make sure the database file is not locked by another process.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│  Railway (Cloud)                            │
│  ┌───────────────────────────────────┐      │
│  │ Discord Bot                       │      │
│  │ - Receives /discovery commands    │      │
│  │ - Uses HAVEN_API_KEY in headers   │      │
│  │ - Sends POST to ngrok URL         │      │
│  └───────────┬───────────────────────┘      │
└──────────────┼──────────────────────────────┘
               │
               │ HTTPS (X-API-Key header)
               ▼
┌─────────────────────────────────────────────┐
│  ngrok Tunnel                               │
│  https://[random].ngrok-free.app            │
│  → http://localhost:5000                    │
└──────────────┬──────────────────────────────┘
               │
               │ HTTP (forwards headers)
               ▼
┌─────────────────────────────────────────────┐
│  Local Computer                             │
│  ┌───────────────────────────────────┐      │
│  │ local_sync_api.py                 │      │
│  │ - Loads .env file                 │      │
│  │ - Verifies X-API-Key header       │      │
│  │ - Returns 401 if mismatch         │      │
│  │ - Returns 200 + data if match     │      │
│  └───────────┬───────────────────────┘      │
│              │                               │
│              ▼                               │
│  ┌───────────────────────────────────┐      │
│  │ VH-Database.db                    │      │
│  │ - Stores discoveries              │      │
│  │ - Stores system data              │      │
│  └───────────────────────────────────┘      │
└─────────────────────────────────────────────┘
```

---

## Quick Start Checklist

- [ ] **Terminal 1:** Run `start_local_api.bat` in Haven_mdev folder
- [ ] **Verify:** API startup shows correct API key (`b14191847...`)
- [ ] **Terminal 2:** Run `ngrok http 5000`
- [ ] **Copy:** ngrok forwarding URL (e.g., `https://xyz.ngrok-free.app`)
- [ ] **Railway:** Update `HAVEN_SYNC_API_URL` environment variable with ngrok URL
- [ ] **Railway:** Verify `HAVEN_API_KEY` matches local `.env` file
- [ ] **Railway:** Restart deployment if environment variables changed
- [ ] **Test:** Run health check with curl/PowerShell (should return 200 OK)
- [ ] **Test:** Try a discovery command in Discord
- [ ] **Verify:** Discovery appears in VH-Database.db

---

## Security Notes

### API Key Security
- The current API key is: `b14191847f8d166c3ddc3ec0d55fa1a86c644511ffb187ddaf7a8ec68de94aeb`
- This is a 64-character hexadecimal string (256-bit security)
- **DO NOT commit this key to public repositories**
- Store it only in:
  - Local `.env` file (add to `.gitignore`)
  - Railway environment variables (encrypted by Railway)

### Regenerating the API Key
If you need to generate a new API key:

**Python:**
```python
import secrets
new_key = secrets.token_hex(32)  # 64 hex characters
print(f"New API Key: {new_key}")
```

**PowerShell:**
```powershell
$bytes = New-Object Byte[] 32
[Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
$newKey = [BitConverter]::ToString($bytes) -replace '-', ''
Write-Host "New API Key: $($newKey.ToLower())"
```

Then update:
1. `.env` file in Haven_mdev
2. Railway environment variable `HAVEN_API_KEY`
3. Restart both local API and Railway deployment

---

## File Locations Reference

### Local Machine (Haven_mdev)
```
C:\Users\parke\OneDrive\Desktop\Haven_mdev\
├── .env                          # ← API key configuration (CREATED)
├── local_sync_api.py            # ← Local API server (UPDATED)
├── start_local_api.bat          # ← Startup script
├── requirements.txt             # ← Python dependencies (includes python-dotenv)
└── data\
    └── VH-Database.db          # ← Main Haven database
```

### Railway Deployment (keeper-discord-bot-main)
```
C:\Users\parke\OneDrive\Desktop\keeper-discord-bot-main\
├── .env                         # ← Local copy (NOT deployed to Railway)
├── Procfile                    # ← Railway entry point
├── railway.json                # ← Railway configuration
├── requirements.txt            # ← Python dependencies
└── src\
    ├── main.py                 # ← Bot entry point
    └── core\
        └── haven_integration_http.py  # ← HTTP API integration
```

### Environment Variables Priority
1. **Railway Environment Variables** (highest priority for deployed bot)
2. **Local .env file** (for local API server)
3. **Hardcoded defaults** (fallback - should never be used)

---

## Success Indicators

### Local API Server Running Successfully
```
✓ Terminal shows: "Running on http://127.0.0.1:5000"
✓ Startup message shows: "API Key: b14191847..."
✓ Health check returns 200 OK
✓ Systems endpoint returns JSON data
```

### ngrok Tunnel Running Successfully
```
✓ Terminal shows: "Session Status: online"
✓ Forwarding URL displayed: "https://[random].ngrok-free.app -> http://localhost:5000"
✓ Web interface accessible at: http://127.0.0.1:4040
✓ Health check through ngrok returns 200 OK
```

### Discord Bot Working Successfully
```
✓ Railway deployment status: "Active"
✓ Bot online in Discord server
✓ /discovery command responds
✓ Discovery submissions succeed (no 401 errors)
✓ Discoveries appear in VH-Database.db
```

---

## Next Steps

1. **Start the servers** using the Quick Start Checklist above
2. **Test authentication** using the test commands
3. **Try a discovery** in Discord to verify end-to-end functionality
4. **Monitor logs** in both terminals for any errors

If you continue to get 401 errors after following this guide, check:
- API key matches exactly in both places (no extra spaces, quotes, or newlines)
- Both servers (local API and ngrok) are running
- Railway environment variables are set correctly and deployment was restarted after changes
