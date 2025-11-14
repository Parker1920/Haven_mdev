# Railway Deployment - START HERE (Action Plan)

**Read this first.** Then follow the numbered steps.

---

## The Problem (Why You're Here)

```
ERROR: "error creating build plan with pailpack"

Translation: Railway doesn't know what to run
```

---

## The Solution (30 Seconds)

**You need to tell Railway: "Run the Discord bot"**

This takes 3 files:
1. `Procfile` - Tells Railway what to run
2. `requirements.txt` - Tells Railway what to install
3. `.env.example` - Documents your config

---

## Step-by-Step Action Plan

### ⏱️ 5 MINUTES: Create Critical Files

**STEP 1: Create `Procfile`**
- Location: `c:\Users\parke\OneDrive\Desktop\Haven_mdev\Procfile`
- Content (exactly):
  ```
  web: python keeper-bot/src/main.py
  ```
- Save and done! ✅

**STEP 2: Create `requirements.txt` at PROJECT ROOT**
- Location: `c:\Users\parke\OneDrive\Desktop\Haven_mdev\requirements.txt`
- Copy this (consolidates all dependencies):
  ```txt
  discord.py>=2.3.0
  aiofiles>=23.2.0
  aiosqlite>=0.19.0
  asyncio-throttle>=1.0.2
  python-dotenv>=1.0.0
  colorama>=0.4.6
  rich>=13.0.0
  psycopg2-binary>=2.9.0
  pillow>=10.0.0
  pandas>=2.0
  jsonschema>=4.0
  flask>=2.3.0
  flask-cors>=4.0.0
  werkzeug>=2.3.0
  ```
- Save ✅

**STEP 3: Create `.env.example`**
- Location: `c:\Users\parke\OneDrive\Desktop\Haven_mdev\.env.example`
- Copy this:
  ```bash
  DISCORD_BOT_TOKEN=your_discord_bot_token_here
  DATABASE_URL=postgresql://user:password@host/database
  FLASK_ENV=production
  USE_DATABASE=true
  DATA_JSON_PATH=./data/data.json
  LOG_LEVEL=INFO
  ```
- Save ✅

### ⏱️ 5 MINUTES: Fix Bot Imports

**STEP 4: Edit `keeper-bot/src/main.py`**
- Open: `c:\Users\parke\OneDrive\Desktop\Haven_mdev\keeper-bot\src\main.py`
- Find the imports at the top (around line 1-20)
- ADD THIS at the very beginning (before existing imports):
  ```python
  # ============================================
  # RAILWAY COMPATIBILITY: Fix import paths
  # ============================================
  import sys
  from pathlib import Path
  
  # Handle both local and Railway execution
  KEEPER_BOT_DIR = Path(__file__).parent.parent
  PROJECT_ROOT = KEEPER_BOT_DIR.parent
  sys.path.insert(0, str(KEEPER_BOT_DIR))
  sys.path.insert(0, str(PROJECT_ROOT))
  ```
- Save ✅

### ⏱️ 5 MINUTES: Test Locally

**STEP 5: Verify it Works**
- Open Terminal/PowerShell in `Haven_mdev` folder
- Run:
  ```bash
  python keeper-bot/src/main.py
  ```
- You should see: `The Keeper awakens...` ✅
- If you see that, you're good!
- Close with: `Ctrl+C`

### ⏱️ 2 MINUTES: Push to GitHub

**STEP 6: Commit Changes**
```bash
cd Haven_mdev
git add Procfile requirements.txt .env.example keeper-bot/src/main.py
git commit -m "feat: prepare Haven for Railway deployment"
git push origin main
```

### ⏱️ 5 MINUTES: Configure Railway

**STEP 7: Go to Railway Dashboard**
- URL: https://railway.app/project/20eb29de-a6f6-4076-8bb5-f7cf34d0a8ec
- Click: "New" or "Create Service"
- Choose: "Deploy from GitHub"
- Select: `Haven_mdev` repository
- Click: "Deploy"

**STEP 8: Railway Auto-Detects**
- Railway finds `Procfile` ✅
- Reads: `web: python keeper-bot/src/main.py`
- Installs: Dependencies from `requirements.txt`
- Starts: Discord bot

**STEP 9: Add PostgreSQL**
- In Railway dashboard, click: "Add Service"
- Choose: "PostgreSQL"
- Railway auto-injects `DATABASE_URL` ✅

**STEP 10: Set Discord Token**
- Go to: Service → Variables
- Add: `DISCORD_BOT_TOKEN=<your_actual_token>`
- (Get token from: https://discord.com/developers/applications)

**STEP 11: Deploy**
- Railway auto-deploys from git push
- Check: Service → Logs
- Look for: "The Keeper awakens..." ✅

---

## You're Done! 🎉

Your Discord bot is now running 24/7 on Railway.

**Total time: 30 minutes**

---

## If Something Goes Wrong

### Bot didn't come online?
- Check Railway → Logs tab
- Look for errors
- Fix locally: `python keeper-bot/src/main.py`
- Re-test, then push to GitHub

### "Procfile not found" error?
- Make sure `Procfile` is at **project root**
- Not in subfolder
- Check spelling exactly

### "ModuleNotFoundError"?
- You added sys.path fix in main.py? ✅
- If not, add it again
- Test locally before pushing

### "DATABASE_URL not found"?
- Did you add PostgreSQL service? ✅
- It takes 30 seconds to initialize
- Railway auto-injects it

### Still stuck?
- Read: `RAILWAY_QUICK_START.md` → Common Issues section
- Or: `RAILWAY_DEPLOYMENT_PLAN.md` → Troubleshooting section

---

## Optional Next Steps (After Bot Works)

**Want more features?**

1. **Expose Map Generator as API** (20 min)
   - Follow: `RAILWAY_FILES_TO_CREATE.md` → File 6: api_server.py
   
2. **Test Locally with Docker** (20 min)
   - Follow: `RAILWAY_FILES_TO_CREATE.md` → File 5: docker-compose.yml
   - Run: `docker-compose up`

3. **Migrate Data to PostgreSQL** (30 min)
   - Follow: `RAILWAY_FILES_TO_CREATE.md` → File 7: migration script

4. **Full Documentation** (60 min)
   - Read: `RAILWAY_DEPLOYMENT_PLAN.md` (complete strategy)
   - Study: `RAILWAY_ARCHITECTURE.md` (system design)

---

## What Happened?

### Before (Local Only)
```
Your Computer
└── Haven (runs manually)
    └── Bot offline when PC sleeps
```

### After (Railway Cloud) ✅
```
Railway (24/7)
└── Haven Bot
    ├── Always online
    ├── Auto-restart if crashes
    ├── PostgreSQL database
    └── Git push = auto-deploy
```

---

## Important Notes

⚠️ **Don't forget:**
- Replace `<your_actual_token>` with your actual Discord bot token
- Get token from: https://discord.com/developers/applications
- Keep token secret! Don't commit to GitHub

📌 **Good practices:**
- Test locally before pushing
- Check Railway logs if things fail
- Keep `.env.example` in version control (without actual secrets)
- Add secrets only in Railway dashboard

🚀 **You're all set!**

The Discord bot is about to go live. Here's what happens:

1. **You push code** → GitHub gets update
2. **GitHub notifies Railway** → "New code!"
3. **Railway builds** → Installs dependencies, reads Procfile
4. **Railway runs** → `python keeper-bot/src/main.py`
5. **Bot comes online** → Discord shows "The Keeper is online"
6. **Success!** → Bot is live 24/7 ✅

---

## Just the Commands (Copy & Paste)

```bash
# Test locally
python keeper-bot/src/main.py

# Commit to GitHub
git add Procfile requirements.txt .env.example keeper-bot/src/main.py
git commit -m "feat: prepare Haven for Railway deployment"
git push origin main

# That's it! Railway deploys automatically from GitHub
```

---

## Estimated Results

After following these steps:

- ⏱️ **Time spent:** 30 minutes
- 💰 **Cost:** ~$5-12/month (less than a coffee!)
- 📊 **Uptime:** 99.5%+ (Railway's reliability)
- 🎯 **Availability:** Your bot is online 24/7

---

## Need More Details?

- 📖 Full documentation: Read `RAILWAY_INDEX.md`
- 🔧 Exact code: See `RAILWAY_FILES_TO_CREATE.md`
- 📚 Deep dive: Study `RAILWAY_DEPLOYMENT_PLAN.md`
- 🎨 Visual guide: Check `RAILWAY_QUICK_START.md`
- 🏗️ Architecture: Review `RAILWAY_ARCHITECTURE.md`

---

## Questions?

**Before you ask, check:**
1. Your DISCORD_BOT_TOKEN is set in Railway Variables ✅
2. PostgreSQL add-on is created ✅
3. Procfile is at project root ✅
4. requirements.txt is at project root ✅
5. Bot works locally ✅

If all that's true, most issues fix themselves. Give it 5 minutes, check the logs again.

---

## You've Got This! 🚀

Everything is ready. Just follow the 11 steps above.

**Let's go!** ⚡

---

**Quick Reference:**
- Procfile: 1 line
- requirements.txt: ~20 lines (copy-paste)
- .env.example: ~10 lines (copy-paste)
- main.py fix: 10 lines added

**Total new code:** ~40 lines  
**Time to write:** 5 minutes  
**Time to test:** 2 minutes  
**Time to deploy:** 5 minutes  
**Time to live:** 20 minutes max

**Let's make Haven live on Railway!** 🌟
