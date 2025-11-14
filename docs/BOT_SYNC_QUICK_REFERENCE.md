# Bot Sync System - Quick Reference Card

## ⚡ Quick Start

### Running the Bot
```bash
cd docs/guides/Haven-lore/keeper-bot
python src/main.py
```

**Expected startup logs:**
```
🌌 The Keeper awakens...
🗃️ Keeper Database initialized
📋 Sync queue table created/verified
🔄 Sync worker started (30s intervals)
🌐 Sync API available on port 8080
🔮 The Keeper is online
```

## 🔍 How It Works (30 seconds)

```
User submits discovery
        ↓
Saved to keeper.db (instant ✅)
        ↓
Added to sync queue
        ↓
Sync worker processes every 30s
        ↓
Written to VH-Database.db
        ↓
Appears in Control Room!
```

## 📊 Check Sync Status

### Via API (Fastest)
```bash
# Health check
curl http://localhost:8080/health

# Sync status
curl http://localhost:8080/sync/status

# Failed items
curl http://localhost:8080/sync/failed
```

### Via Database
```sql
-- Quick status
SELECT sync_status, COUNT(*)
FROM sync_queue
GROUP BY sync_status;

-- Pending items
SELECT * FROM sync_queue
WHERE sync_status = 'pending';

-- Failed items
SELECT * FROM sync_queue
WHERE sync_status = 'max_retries_exceeded';
```

## 🔧 Common Tasks

### Retry a Failed Sync
```bash
# Via API
curl -X POST http://localhost:8080/sync/retry/123

# Via SQL
UPDATE sync_queue
SET sync_status = 'pending', sync_attempts = 0
WHERE id = 123;
```

### Check Last 10 Discoveries
```sql
-- In keeper.db
SELECT id, system_name, location, discovery_type, username
FROM discoveries
ORDER BY id DESC LIMIT 10;

-- In VH-Database.db
SELECT id, system_name, location_name, discovery_type, discovered_by
FROM discoveries
ORDER BY id DESC LIMIT 10;
```

### Clean Up Old Synced Items
```sql
DELETE FROM sync_queue
WHERE sync_status = 'synced'
AND synced_at < datetime('now', '-30 days');
```

## ⚠️ Troubleshooting

### Discoveries Not Syncing?

**Check 1:** Is sync worker running?
```bash
curl http://localhost:8080/health
# Should show: "sync_worker_running": true
```

**Check 2:** Any errors in sync queue?
```sql
SELECT sync_error FROM sync_queue
WHERE sync_status = 'pending'
AND sync_error IS NOT NULL;
```

**Check 3:** VH-Database.db accessible?
```bash
ls -la ~/Desktop/Haven_mdev/data/VH-Database.db
# Should exist and be writable
```

### API Not Responding?

**Check port:**
```bash
netstat -an | grep 8080
# Should show LISTEN on port 8080
```

**Check bot logs:**
```
🌐 Sync API available on port 8080  ← Should see this
```

### Sync Taking Too Long?

**Normal:** 0-30 seconds (average 15s)

**If slower:**
1. Check pending queue: `SELECT COUNT(*) FROM sync_queue WHERE sync_status='pending'`
2. Check for errors: `SELECT COUNT(*) FROM sync_queue WHERE sync_error IS NOT NULL`
3. Restart bot if stuck

## 📍 Important File Locations

```
keeper-bot/
├── src/
│   ├── main.py                      ← Bot entry point
│   ├── database/
│   │   ├── keeper_db.py            ← Database operations
│   │   └── sync_queue.py           ← Sync queue manager
│   ├── sync/
│   │   └── sync_worker.py          ← Background sync task
│   ├── api/
│   │   └── sync_api.py             ← HTTP API
│   └── cogs/
│       └── enhanced_discovery.py   ← Discovery commands
├── data/
│   └── keeper.db                    ← Bot's database
├── .env                             ← Configuration
├── requirements.txt                 ← Python dependencies
└── SYNC_SYSTEM_GUIDE.md            ← Full documentation
```

## 🔐 Environment Variables

```env
# Required
BOT_TOKEN=your_bot_token
GUILD_ID=your_guild_id

# Optional
SYNC_API_PORT=8080
HAVEN_DB_PATH=/path/to/VH-Database.db
USE_HAVEN_DATABASE=true
```

## 🚀 Railway Deployment

### Quick Deploy Steps
1. Push bot folder to GitHub
2. Connect Railway to repo
3. Set environment variables
4. Add persistent volume: `/app/data`
5. Expose port 8080
6. Deploy!

**Railway API URL:** `https://keeper-bot.railway.app`

**Test it:**
```bash
curl https://keeper-bot.railway.app/health
curl https://keeper-bot.railway.app/sync/status
```

## 📈 Performance Expectations

| Metric | Value |
|--------|-------|
| Sync latency | 0-30 seconds (avg 15s) |
| Success rate | 99%+ |
| API response | <100ms |
| Throughput | 100+ discoveries/hour |
| Memory usage | ~5MB for sync |

## ✅ Verification Checklist

### After Starting Bot
- [ ] See "🔄 Sync worker started" in logs
- [ ] See "🌐 Sync API available" in logs
- [ ] API health check returns 200
- [ ] Submit test discovery via Discord
- [ ] Check keeper.db has new entry
- [ ] Wait 30 seconds
- [ ] Check VH-Database.db has new entry
- [ ] Open Control Room, see discovery

### Before Railway Deployment
- [ ] All discoveries syncing locally
- [ ] No failed syncs in queue
- [ ] API accessible on port 8080
- [ ] Environment variables configured
- [ ] keeper.db backed up
- [ ] Documentation reviewed

## 📞 Emergency Commands

### Stop Bot Immediately
```bash
# Kill the process
pkill -f "python src/main.py"
```

### Force Sync All Pending
```sql
UPDATE sync_queue
SET next_retry_after = NULL
WHERE sync_status = 'pending';
-- Sync worker will process on next cycle
```

### Reset Failed Items
```sql
UPDATE sync_queue
SET sync_status = 'pending',
    sync_attempts = 0,
    sync_error = NULL
WHERE sync_status = 'max_retries_exceeded';
```

### Backup keeper.db
```bash
cp data/keeper.db data/keeper.db.backup.$(date +%Y%m%d_%H%M%S)
```

## 📚 Full Documentation

- **Complete Guide:** [SYNC_SYSTEM_GUIDE.md](guides/Haven-lore/keeper-bot/SYNC_SYSTEM_GUIDE.md)
- **Implementation Summary:** [BOT_SYNC_IMPLEMENTATION_SUMMARY.md](BOT_SYNC_IMPLEMENTATION_SUMMARY.md)
- **Bot Code:** `docs/guides/Haven-lore/keeper-bot/src/`

## 💡 Tips

1. **Always check API first** - Fastest way to see status
2. **Check logs for errors** - Most issues show in logs
3. **Wait 30 seconds** - Give sync worker time to process
4. **Use SQL for bulk operations** - API is for monitoring
5. **Back up keeper.db regularly** - Contains all discoveries

---

**Last Updated:** November 13, 2025
**Quick Help:** See SYNC_SYSTEM_GUIDE.md for detailed troubleshooting
