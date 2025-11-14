# Phase 2/3 Features - User Guide

## What's New in Phase 2 & 3?

### Phase 2: Control Room Database Backend
Your Control Room can now handle **billions of systems** using a database instead of just JSON files.

**New Features You'll See:**
1. **Backend Indicator** - Shows whether you're using DATABASE or JSON mode
2. **System Count** - Shows total systems in your database
3. **Database Statistics** - New button to view database info

### Phase 3: System Entry Wizard Database Backend
The System Entry Wizard now saves directly to the database for better performance.

**New Features You'll See:**
1. **Backend Indicator** - Shows current backend mode in header
2. **System Count** - Shows total systems
3. **Faster Saves** - Systems save to database (faster for large datasets)

---

## How to See These Features

### 1. Launch Control Room
Double-click: **Haven Control Room.bat**

You should see in the sidebar:
```
Backend: DATABASE
Systems: 9
```

### 2. Launch System Entry
Click the **"System Entry"** button in Control Room

You should see in the header:
```
Backend: DATABASE    Systems: 9
```

### 3. Check Database Statistics
In Control Room, scroll down to **Advanced Tools** section and click:
```
📊 Database Statistics
```

This shows:
- Total Systems
- Total Planets
- Total Moons
- Database Size
- Last Modified

---

## Configuration

### Current Settings (config/settings.py):
```python
USE_DATABASE = True          # Using database backend
SHOW_BACKEND_STATUS = True   # Show backend indicator
SHOW_SYSTEM_COUNT = True     # Show system count
ENABLE_DATABASE_STATS = True # Enable statistics button
```

### To Switch Back to JSON Mode:
Edit `config/settings.py` and change:
```python
USE_DATABASE = False  # Use JSON files instead of database
```

**Note:** JSON mode is fine for < 1,000 systems. Database mode is required for larger datasets.

---

## What Files Are Used?

### Database Mode (Current):
- **Data:** `data/haven.db` (SQLite database)
- **Backups:** `data/backups/haven_backup_*.db`

### JSON Mode:
- **Data:** `data/data.json`
- **Backups:** `data/data.json.bak`

---

## Troubleshooting

### "I don't see Backend: DATABASE"
1. Check logs: `logs/control-room-2025-11-05.log`
2. Look for: `"Using DATABASE data provider"`
3. If missing, the import may have failed
4. Try running: `py src/control_room.py` directly to see errors

### "Database Statistics button is missing"
- Make sure `USE_DATABASE = True` in `config/settings.py`
- Make sure `ENABLE_DATABASE_STATS = True`
- Restart Control Room

### "System count shows 0"
- Check if `data/haven.db` exists
- Check if database has data: `py -c "from src.common.data_provider import DatabaseDataProvider; db = DatabaseDataProvider('data/haven.db'); print(db.get_total_count())"`

---

## Benefits of Database Backend

### For Small Datasets (< 1,000 systems):
✓ Fast loading
✓ Easy editing
✓ Human-readable
→ **JSON mode is fine**

### For Large Datasets (> 1,000 systems):
✓ Instant search (indexed)
✓ Efficient memory use
✓ Fast queries
✓ Handles millions of systems
→ **Database mode required**

---

## Migration Notes

Don't worry! Your existing data is safe:
- Old data.json is preserved
- Database is created from JSON automatically
- You can switch between modes anytime
- Both files stay in sync

---

## Support

If you see any issues:
1. Check `logs/control-room-*.log`
2. Check `logs/error_logs/` for errors
3. Make sure Python 3.10+ is installed
4. Make sure all packages are installed: `pip install -r config/requirements.txt`

---

**Updated:** November 5, 2025  
**Applies To:** Phase 2 & 3 Complete
