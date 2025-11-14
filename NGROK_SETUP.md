# ngrok Setup Guide for Windows

## Problem
ngrok is a **command-line tool**, not a regular Windows application. You can't just double-click it!

---

## Step-by-Step Setup

### Step 1: Extract ngrok

1. Find your downloaded file (probably in `Downloads` folder)
2. Look for: `ngrok-v3-stable-windows-amd64.zip` (or similar)
3. **Right-click** the ZIP file → **Extract All...**
4. Extract to: `C:\ngrok\` (create this folder if needed)
5. You should now have: `C:\ngrok\ngrok.exe`

---

### Step 2: Add ngrok to System PATH (Makes it work from anywhere)

#### Option A: Automatic (Easy Way)

1. Press **Windows Key** + **R**
2. Type: `cmd` and press **Enter**
3. Copy and paste this command:

```cmd
setx PATH "%PATH%;C:\ngrok"
```

4. Press **Enter**
5. Close the command prompt and open a **NEW** one
6. Type: `ngrok version`
7. You should see: `ngrok version 3.x.x`

✅ **If you see the version, it works! Skip to Step 3.**

#### Option B: Manual (If automatic didn't work)

1. Right-click **This PC** → **Properties**
2. Click **Advanced system settings** (left sidebar)
3. Click **Environment Variables** button
4. Under "User variables", find **Path**, click **Edit**
5. Click **New**
6. Type: `C:\ngrok`
7. Click **OK** on all windows
8. **Close all command prompts** and open a new one
9. Type: `ngrok version` to test

---

### Step 3: Authenticate ngrok (One-time)

1. Go to: https://dashboard.ngrok.com/get-started/your-authtoken
2. Sign up/Login (free account)
3. **Copy your authtoken** (looks like: `2abc123def456ghi789jkl012mno345_pqr678stu901vwx234yz`)
4. Open **Command Prompt** (press Windows Key, type `cmd`, press Enter)
5. Paste this command (replace with YOUR token):

```cmd
ngrok config add-authtoken YOUR_TOKEN_HERE
```

Example:
```cmd
ngrok config add-authtoken 2abc123def456ghi789jkl012mno345_pqr678stu901vwx234yz
```

6. Press **Enter**
7. You should see: `Authtoken saved to configuration file`

✅ **ngrok is now configured!**

---

### Step 4: Test ngrok

1. Open **Command Prompt**
2. Type:

```cmd
ngrok http 5000
```

3. You should see:

```
ngrok

Session Status                online
Account                       your@email.com
Forwarding                    https://abc123xyz.ngrok.io -> http://localhost:5000
```

4. Press **Ctrl+C** to stop it

✅ **If you see this, ngrok is working perfectly!**

---

## Using ngrok with Haven Bot

### Method 1: Use the Batch File (Easiest)

1. **First**, make sure you extracted ngrok to `C:\ngrok\`
2. **Double-click:** `start_ngrok.bat` (in Haven_mdev folder)
3. You should see the ngrok interface with your HTTPS URL

### Method 2: Manual Command

1. Open **Command Prompt**
2. Type:

```cmd
cd C:\Users\parke\OneDrive\Desktop\Haven_mdev
ngrok http 5000
```

3. Look for the **Forwarding** line:
   ```
   Forwarding    https://abc123xyz.ngrok.io -> http://localhost:5000
   ```

4. **Copy the HTTPS URL** (e.g., `https://abc123xyz.ngrok.io`)

---

## What to Do With the ngrok URL

Once you have the URL (e.g., `https://abc123xyz.ngrok.io`):

1. Add `/api` to the end: `https://abc123xyz.ngrok.io/api`
2. Use this in Railway environment variables as `HAVEN_SYNC_API_URL`

**Example:**
```
HAVEN_SYNC_API_URL=https://abc123xyz.ngrok.io/api
```

---

## Common Issues

### "ngrok: command not found" or "ngrok is not recognized"

**Cause:** ngrok not in PATH

**Fix:**
1. Make sure you did Step 2 (Add to PATH)
2. **Close all command prompts** and open a new one
3. Try again

### Can't extract the ZIP file

**Cause:** Windows blocked the download

**Fix:**
1. Right-click `ngrok.zip`
2. Click **Properties**
3. Check **Unblock** at the bottom
4. Click **OK**
5. Extract again

### ngrok closes immediately when I double-click it

**Cause:** ngrok is a command-line tool!

**Fix:**
- Don't double-click `ngrok.exe` directly
- Use the batch file: `start_ngrok.bat`
- Or run from Command Prompt: `ngrok http 5000`

### "Failed to validate account"

**Cause:** Not authenticated

**Fix:**
1. Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken
2. Run: `ngrok config add-authtoken YOUR_TOKEN`

---

## Quick Reference

### Important Commands

```cmd
# Check if ngrok is installed
ngrok version

# Add your authtoken (one-time)
ngrok config add-authtoken YOUR_TOKEN

# Start tunnel for Haven API
ngrok http 5000

# Test if tunnel is working (visit in browser)
https://your-url.ngrok.io/health
```

### Important Paths

- **ngrok executable:** `C:\ngrok\ngrok.exe`
- **Config file:** `C:\Users\YOUR_USERNAME\.ngrok2\ngrok.yml`
- **Batch file:** `C:\Users\parke\OneDrive\Desktop\Haven_mdev\start_ngrok.bat`

---

## Visual Guide

### What you should see when ngrok is working:

```
ngrok

Build better APIs with ngrok. Early access: ngrok.com/early-access

Session Status                online
Account                       your@email.com (Plan: Free)
Version                       3.5.0
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123xyz.ngrok.io -> http://localhost:5000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**The URL you need is in the "Forwarding" line!**

---

## Next Steps After ngrok is Working

1. ✅ ngrok running with HTTPS URL
2. Start local API: `python local_sync_api.py` (in another command prompt)
3. Test in browser: `https://your-url.ngrok.io/health`
4. Should see: `{"status": "healthy", "database_accessible": true}`
5. Copy URL and add `/api` for Railway
6. Deploy to Railway!

---

## Still Having Issues?

### Try this step-by-step test:

1. Open **Command Prompt**
2. Type: `cd C:\ngrok`
3. Type: `ngrok.exe version`
4. Do you see a version number?
   - **YES** → ngrok is installed! Just need to run `ngrok http 5000`
   - **NO** → Extract the ZIP file to `C:\ngrok\` and try again

### Alternative: Run ngrok from Downloads folder

If you can't get PATH working:

1. Open **Command Prompt**
2. Type: `cd C:\Users\parke\Downloads` (or wherever you extracted ngrok)
3. Type: `ngrok.exe http 5000`
4. This should work even without PATH setup

---

**Need more help? Let me know what error message you're seeing!**
