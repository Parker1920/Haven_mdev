# Master Program - Clean Slate Setup

## ✅ Your Clean Data File is Ready!

**File Location:** `data/master_clean.json`  
**Size:** 306 bytes  
**Status:** Ready to use

---

## What You Have Now

### Current Master Data
- **File:** `data/data.json`
- **Status:** ✅ Reset to clean/blank state
- **Backup:** `data/data.json.bak` (contains previous data)

### Available Templates

| File | Size | Purpose | Status |
|------|------|---------|--------|
| `master_clean.json` | 306 B | 📝 Blank master template (NEW) | ✅ Ready |
| `data.json` | 306 B | 🔧 Current working file | ✅ Clean |
| `example_data.json` | 1.53 KB | 📚 3 sample systems | Available |
| `clean_data.json` | 150 B | 🎯 User edition blank | Available |

---

## How to Use

### Option 1: Start Building Right Now
Your `data.json` is already clean and ready! Just:

1. Launch the Control Room (master program)
2. Open System Entry Wizard
3. Click "New System" to start adding your systems
4. Your data saves automatically to `data.json`

### Option 2: Load a Different Template
If you want to switch templates:

**In Control Room UI:**
1. Go to File menu → Import Data
2. Choose any `.json` file
3. System loads that data as your working set

**Command Line (manual):**
```powershell
# Replace current data with example
Copy-Item "data/example_data.json" -Destination "data/data.json" -Force

# Restore from backup
Copy-Item "data/data.json.bak" -Destination "data/data.json" -Force

# Go back to clean slate
Copy-Item "data/master_clean.json" -Destination "data/data.json" -Force
```

### Option 3: Use Database Instead
The master program also supports database storage:

1. Launch Control Room
2. Data automatically syncs with `data/haven.db`
3. Database is source of truth for master program

---

## Your Clean State

Here's exactly what's in your `data.json` right now:

```json
{
  "_meta": {
    "version": "1.0.0",
    "description": "Haven Control Room - Clean Master Template",
    "note": "Start with this blank template and add your star systems using the System Entry Wizard.",
    "created_at": "2025-11-06T00:00:00",
    "last_modified": "2025-11-06T00:00:00"
  }
}
```

**That's it!** Just metadata. No systems. Ready for you to build.

---

## Building Your Galaxy

### Step 1: Launch Control Room
```bash
python src/control_room.py
```

### Step 2: Add First System
- Click "New System" in the System Entry Wizard
- Enter system name (e.g., "My Star System")
- Set coordinates (X, Y, Z)
- Set properties (fauna, flora, sentinel level, materials)
- Click "Save"

### Step 3: Keep Adding
- Repeat for each system you want
- Add planets to each system
- Upload photos if desired
- Everything saves automatically

### Step 4: Generate Map
- Click "Generate Map"
- 3D visualization created
- Opens in your browser

---

## Backup & Recovery

### Your Backup
**File:** `data/data.json.bak`
- Contains the previous master data
- Created automatically before reset
- Use if you need to restore old data

### How to Restore
```powershell
Copy-Item "data/data.json.bak" -Destination "data/data.json" -Force
```

---

## Files Saved

As you build, files are created/updated:

| Path | What's Stored | Auto-Created |
|------|---------------|--------------|
| `data/data.json` | Your working systems | Yes |
| `data/data.json.bak` | Previous version | Yes |
| `data/haven.db` | Database copy | Yes |
| `logs/` | System logs | Yes |
| `dist/` | Generated maps | On demand |

---

## Ready to Build! 🚀

Your clean slate is set up. Just launch the Control Room and start adding systems!

**Date:** November 6, 2025  
**Version:** Clean Master Template v1.0
