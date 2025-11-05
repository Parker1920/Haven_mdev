# Data Synchronization Feature

## Overview

The Control Room now automatically checks if your JSON and database backends are in sync on startup, and provides tools to sync them manually if needed.

---

## Automatic Sync Check

**When:** Every time the Control Room starts  
**What:** Checks if `data/data.json` and `data/haven.db` have the same systems  
**Where:** Check `logs/control-room-*.log` for sync status

### Log Messages

**When in sync:**
```
[INFO] Data sync OK: JSON and database both have 9 systems
```

**When out of sync:**
```
[WARNING] Data sync issue detected: 2 systems only in JSON, 1 systems differ
```

---

## Manual Sync Tool

### Accessing the Sync Tool

1. Launch Control Room
2. Scroll to **"ADVANCED TOOLS"** section (only visible when running from source, not in EXE)
3. Click **"🔄 Sync Data (JSON ↔ DB)"**

### Sync Dialog

The sync dialog shows:
- **JSON File:** Number of systems in data.json
- **Database:** Number of systems in haven.db
- **In Both:** Systems that exist in both
- **Status:** Whether data is in sync
- **Issues:** Any systems only in one backend or with differences

### Sync Options

#### JSON → Database
- **What it does:** Copies systems from JSON file to database
- **Safe:** Keeps existing database systems
- **Use when:** You added systems to JSON and want them in database

**Example:**
```
Before:  JSON has 10 systems, Database has 9 systems
After:   JSON has 10 systems, Database has 10 systems
```

#### Database → JSON
- **What it does:** Copies systems from database to JSON file
- **Caution:** Overwrites data.json (but creates backup: data.json.bak)
- **Use when:** You added systems to database and want to update JSON

**Example:**
```
Before:  Database has 10 systems, JSON has 9 systems
After:   Database has 10 systems, JSON has 10 systems
```

---

## Command Line Tool

You can also check/sync from command line:

### Check Sync Status
```bash
py src/migration/sync_data.py --mode check
```

**Output:**
```
======================================================================
DATA SYNC STATUS CHECK
======================================================================

JSON File: C:\...\data\data.json
Database: C:\...\data\haven.db

JSON systems: 9
Database systems: 9
In both: 9

✓ DATA IS IN SYNC

Recommended Actions:
  → No action needed
```

### Sync JSON to Database
```bash
py src/migration/sync_data.py --mode json-to-db
```

Options:
- `--overwrite` : Update existing systems in database

### Sync Database to JSON
```bash
py src/migration/sync_data.py --mode db-to-json
```

Options:
- `--no-backup` : Skip creating backup

---

## When Do I Need to Sync?

### Scenario 1: Switching from JSON to Database Mode
You were using JSON mode, now switching to database mode.

**Solution:**
```bash
# First time: Migrate all data
py src/migration/json_to_sqlite.py

# Later updates: Use sync tool
py src/migration/sync_data.py --mode json-to-db
```

### Scenario 2: Switching from Database to JSON Mode
You were using database mode, now switching to JSON mode.

**Solution:**
```bash
py src/migration/sync_data.py --mode db-to-json
```

### Scenario 3: Working on Multiple Machines
You edit JSON on one machine, database on another.

**Solution:**
- On Machine A (JSON edits): Sync JSON → Database
- Copy database file to Machine B
- On Machine B: Database is now up to date

### Scenario 4: Backup/Restore
You want to backup database to JSON for safe keeping.

**Solution:**
```bash
# Backup: Export database to JSON
py src/migration/sync_data.py --mode db-to-json

# Restore: Import JSON to database
py src/migration/sync_data.py --mode json-to-db --overwrite
```

---

## Understanding Backend Modes

### JSON Mode (`USE_DATABASE = False`)
- **File:** `data/data.json`
- **Good for:** < 1,000 systems, easy editing
- **Backup:** `data/data.json.bak`

### Database Mode (`USE_DATABASE = True`)
- **File:** `data/haven.db` (SQLite)
- **Good for:** > 1,000 systems, fast queries
- **Backup:** `data/backups/haven_backup_*.db`

**Both modes work with same data - just different storage!**

---

## Best Practices

### 1. Always Check Sync Status After Switching
```bash
# After changing USE_DATABASE in config/settings.py
py src/migration/sync_data.py --mode check
```

### 2. Keep Backups
- JSON: Automatic backup before overwrites (`.json.bak`)
- Database: Use Control Room backup feature

### 3. Use Version Control for JSON
```bash
# JSON is text, works great with git
git add data/data.json
git commit -m "Added 5 new systems"

# Database is binary, harder to track
# Use JSON exports for version control
```

### 4. Regular Sync Schedule
If working with both backends:
- **Daily:** Check sync status
- **Before backup:** Sync to ensure both are current
- **After major edits:** Sync immediately

---

## Troubleshooting

### "Data is out of sync" message on startup

**Check what's different:**
```bash
py src/migration/sync_data.py --mode check
```

**Fix it:**
```bash
# If JSON is correct:
py src/migration/sync_data.py --mode json-to-db

# If Database is correct:
py src/migration/sync_data.py --mode db-to-json
```

### Sync button missing in Control Room

**Causes:**
- Running from EXE (Advanced Tools hidden in EXE)
- Phase 2 not enabled

**Solution:**
- Run from source: `py src/control_room.py`
- Check `PHASE2_ENABLED = True` in logs

### Sync fails with error

**Check logs:**
```
logs/control-room-*.log
```

**Common issues:**
- File locked (close any programs using data.json or haven.db)
- Permissions (run as admin if needed)
- Corrupted data (restore from backup)

---

## Technical Details

### Sync Algorithm

**JSON → Database:**
1. Read all systems from JSON
2. For each system:
   - Check if ID exists in database
   - If not exists: Add to database
   - If exists and overwrite=True: Update in database
3. Does NOT delete systems only in database

**Database → JSON:**
1. Create backup of JSON (data.json.bak)
2. Read all systems from database
3. Build new JSON structure with all systems
4. Overwrite data.json
5. Completely replaces JSON content

### Files Modified

**Source Files:**
- `src/control_room.py` - Added sync check on startup, sync button, sync dialog
- `src/migration/sync_data.py` - New sync utility (created)

**Data Files:**
- `data/data.json` - JSON storage
- `data/haven.db` - SQLite database
- `data/data.json.bak` - JSON backup (auto-created)

---

## FAQ

**Q: Will syncing lose my data?**  
A: No. JSON → Database never deletes. Database → JSON creates backup first.

**Q: How often should I sync?**  
A: Only when switching backends or working across multiple machines.

**Q: Which backend should I use?**  
A: JSON for < 1,000 systems. Database for > 1,000 systems.

**Q: Can I use both backends at the same time?**  
A: No. Pick one in `config/settings.py` with `USE_DATABASE = True/False`.

**Q: What if sync shows differences?**  
A: Choose which is correct (JSON or Database) and sync from that one.

---

**Updated:** November 5, 2025  
**Version:** Phase 2/3 Complete
