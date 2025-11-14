# 🔧 FIX: Slash Commands Not Showing

## Problem
The bot is online but slash commands are not visible in Discord because it was invited without the `applications.commands` scope.

## Solution

### Step 1: Re-authorize the Bot

**Click or copy this URL and open it in your browser:**

```
https://discord.com/api/oauth2/authorize?client_id=1436510971446427720&permissions=274878294016&scope=bot%20applications.commands
```

### Step 2: Authorize in Discord

1. A Discord authorization page will open
2. Select your server: **Voyagers' Haven** (or your server name)
3. Click **"Continue"**
4. Review the permissions
5. Click **"Authorize"**

Discord will say "Bot already added" but will UPDATE its permissions to include slash commands.

### Step 3: Restart the Bot

After authorizing, stop the current bot (Ctrl+C in the terminal) and restart it:

```powershell
cd C:\Users\parke\Haven-lore\keeper-bot
.venv\Scripts\python.exe src\main.py
```

### Step 4: Wait 30 seconds

After the bot restarts, wait about 30 seconds for Discord to register the commands.

### Step 5: Test

In any channel, type `/` and you should see The Keeper's commands:
- `/discovery-report`
- `/archive-search`
- `/setup-channels`
- etc.

## Why This Happened

When you first created the bot invite URL, you likely selected only the "bot" scope but not the "applications.commands" scope. Both are required for slash commands to work.

The new invite URL includes both:
- `scope=bot` - Basic bot functionality
- `scope=applications.commands` - Slash commands

## Troubleshooting

### If commands still don't show after 5 minutes:

1. **Check bot role position:**
   - In Discord Server Settings → Roles
   - Make sure "The Keeper" role is above "@everyone"

2. **Check bot permissions in the channel:**
   - Right-click the channel → Edit Channel → Permissions
   - Check that The Keeper can:
     - ✅ View Channel
     - ✅ Send Messages
     - ✅ Use Application Commands

3. **Try kicking and re-inviting:**
   - Right-click the bot → Kick
   - Use the invite URL above again
   - This does a "clean" re-invite

4. **Clear Discord cache (last resort):**
   - Close Discord completely
   - Press `Windows + R`
   - Type: `%appdata%\discord\Cache`
   - Delete everything in that folder
   - Restart Discord

## Alternative: Manual Command Registration

If the above doesn't work, you can manually sync commands by adding a sync command to the bot. Let me know if you need this option.

---

**After following these steps, your slash commands should appear instantly!**
