# 🌐 HOSTING OPTIONS FOR THE KEEPER BOT

## Current Issue
The bot is running on your local PC, which means:
- ❌ Computer must stay on 24/7
- ❌ Bot goes offline when you close your computer
- ❌ Internet interruptions affect the bot
- ✅ Free and immediate (good for testing)

## Better Hosting Options

---

### 🎯 **Option 1: Replit (Easiest Free Option)**

**Pros:**
- ✅ 100% Free tier available
- ✅ Easy setup (no complex config)
- ✅ Built-in code editor
- ✅ Auto-restarts on crashes
- ✅ Good for small communities

**Cons:**
- ⚠️ Bot may sleep after inactivity (can use UptimeRobot to keep it awake)
- ⚠️ Limited resources on free tier

**Setup Steps:**
1. Go to https://replit.com
2. Sign up (free)
3. Create new Repl → Import from GitHub
4. Enter your repo: `Parker1920/Haven-lore`
5. Add Secrets (your .env variables)
6. Click Run

**Monthly Cost:** FREE

---

### 🎯 **Option 2: Railway.app (Best for Growing Communities)**

**Pros:**
- ✅ $5 free credit per month (usually enough)
- ✅ Very reliable uptime
- ✅ Easy deployment
- ✅ Auto-scaling
- ✅ GitHub integration

**Cons:**
- ⚠️ After $5 credit, costs ~$5-10/month
- ⚠️ Requires credit card for verification

**Setup Steps:**
1. Go to https://railway.app
2. Sign up with GitHub
3. New Project → Deploy from GitHub
4. Select Haven-lore repo
5. Add environment variables
6. Deploy

**Monthly Cost:** $0-10 depending on usage

---

### 🎯 **Option 3: Fly.io (Solid Middle Ground)**

**Pros:**
- ✅ Free tier for small bots
- ✅ 3 shared VMs free
- ✅ Good performance
- ✅ CLI deployment

**Cons:**
- ⚠️ Requires credit card for verification
- ⚠️ More technical setup

**Monthly Cost:** FREE (with limits)

---

### 🎯 **Option 4: DigitalOcean Droplet (Most Control)**

**Pros:**
- ✅ Full VPS control
- ✅ Can host multiple bots
- ✅ Very reliable
- ✅ Predictable pricing

**Cons:**
- ⚠️ Costs money ($4-6/month minimum)
- ⚠️ More technical (need to manage Linux)
- ⚠️ Requires SSH/server knowledge

**Monthly Cost:** $6/month

---

### 🎯 **Option 5: PebbleHost Bot Hosting**

**Pros:**
- ✅ Specifically for Discord bots
- ✅ Easy setup
- ✅ 24/7 uptime
- ✅ Support team

**Cons:**
- ⚠️ Costs money (~$1-3/month)
- ⚠️ Limited free trial

**Monthly Cost:** $1-3/month

---

## 📊 Comparison Table

| Service | Free Tier | Setup Difficulty | Best For |
|---------|-----------|------------------|----------|
| **Replit** | Yes (with sleep) | ⭐ Easy | Testing/Small servers |
| **Railway.app** | $5/month credit | ⭐⭐ Medium | Growing communities |
| **Fly.io** | Yes (limited) | ⭐⭐ Medium | Small-medium bots |
| **DigitalOcean** | No ($6/month) | ⭐⭐⭐ Hard | Large/multiple bots |
| **PebbleHost** | Trial only | ⭐ Easy | Convenience |

---

## 🎯 My Recommendation

**For Your Use Case (Voyagers' Haven):**

### **Start with Replit (Free)**
- Test your bot and community features
- See how much usage you get
- Zero cost to start

### **Upgrade to Railway.app if:**
- Your community grows past ~50 active users
- You need 100% uptime
- The $5/month credit isn't enough (then it's ~$5-10/month)

---

## 🚀 Quick Start: Replit Setup

1. **Create Replit Account:** https://replit.com/signup
2. **Import Repository:**
   - Click "Create Repl"
   - Select "Import from GitHub"
   - URL: `https://github.com/Parker1920/Haven-lore`
   - Root directory: `keeper-bot`

3. **Add Secrets:**
   - Click "Secrets" (lock icon)
   - Add:
     - `BOT_TOKEN` = your bot token
     - `GUILD_ID` = your server ID
     - `DATABASE_PATH` = `./data/keeper.db`
     - `DEBUG_MODE` = `True`

4. **Configure Run Command:**
   - In `.replit` file:
     ```
     run = "cd keeper-bot && python src/main.py"
     ```

5. **Click Run** - Bot goes live!

6. **Keep Alive (Optional):**
   - Use https://uptimerobot.com (free)
   - Monitor your Replit URL
   - Pings every 5 minutes to prevent sleep

---

## 🆘 Current Local Hosting - Quick Fixes

While you decide on hosting, here are immediate fixes for local hosting:

### **Issue: "Application did not respond"**

This means commands aren't synced. Fix:
1. Stop bot (Ctrl+C)
2. Re-authorize bot with this URL:
   ```
   https://discord.com/api/oauth2/authorize?client_id=1436510971446427720&permissions=274878294016&scope=bot%20applications.commands
   ```
3. Restart bot
4. Wait 30 seconds

### **Keep Local Bot Running:**
- Don't close PowerShell window
- Computer must stay on
- Good for testing before moving to cloud

---

## 💡 Next Steps

1. **Immediate:** Fix the command sync (restart after re-auth)
2. **This Week:** Test locally, make sure everything works
3. **When Ready:** Move to Replit (free) or Railway (better uptime)

Need help setting up any of these hosting options? Let me know!
