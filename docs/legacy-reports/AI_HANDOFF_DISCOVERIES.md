# AI Handoff: Discovery System Implementation

**Date**: November 10, 2025  
**Status**: ✅ COMPLETE - Discoveries imported and displayable on map  
**Session Focus**: Debug and fix Keeper Discord bot discovery imports + add UI for viewing discoveries

---

## What Was Fixed

### 1. **Discovery Import System** (src/migration/import_json.py)
**Problem**: Keeper bot discoveries weren't importing into the database. Errors showed:
- "database is locked" (first 4 discoveries)
- "'NoneType' object has no attribute 'strip'" (rest of discoveries)

**Solution**: 
- Added `_is_keeper_format()` to auto-detect Keeper bot JSON format
- Added `_import_keeper_discoveries()` with exponential backoff retry logic (2s, 4s, 8s) for locked databases
- Added `_convert_keeper_discovery()` to map Keeper fields → Haven database schema:
  - Converts lists (`tags[]`, `metadata[]`) to JSON strings for SQLite
  - Maps field names: `type` → `discovery_type`, `location` → `discovery_name`, `evidence_url` → `photo_url`
  - Looks up `system_id` and `planet_id` by name in database
  - Handles None values safely (no more `.strip()` on None)
  - Sets defaults: `location_type='planet'`, `analysis_status='pending'`

**Result**: Successfully imported 17 discoveries from Keeper backup file

---

### 2. **Database Connection Improvements** (src/common/database.py)
**Problem**: Control Room keeps persistent connection, imports fail with "database locked"

**Solution**:
- Added `timeout=10.0` to sqlite3.connect() → waits 10 seconds for lock to clear
- Added `PRAGMA journal_mode=WAL` → enables Write-Ahead Logging for concurrent access

---

### 3. **Discovery UI in System View** (src/static/js/map-viewer.js)
**Problem**: Imported discoveries weren't visible in system view - no button to see them on planets

**Solution**:
- Added discovery detection for planets: checks if `window.DISCOVERIES_DATA` contains discoveries for that planet
- Added **"📍 View X Discoveries" button** in planet info panel when discoveries exist
- Button shows all discoveries for that planet with:
  - Discovery type (⚙️, 🦴, 📖, etc.)
  - Full description
  - Discoverer name
  - Discovery date
  - Back button to return to planet details
- Button styling: cyan background (#00CED1), clearly visible and clickable

---

## How Discoveries Work End-to-End (UPDATED)

```
Keeper Discord Bot
    ↓ (/discovery-report command)
DUAL-WRITE to both databases:
    - keeper.db (bot's internal database)
    - VH-Database.db (Haven Master database) ✅ NEW
    ↓ (map generator reads discoveries from VH-Database)
src/Beta_VH_Map.py generates VH-Map.html
    ↓ (JavaScript loads DISCOVERIES_DATA)
Browser: src/static/js/map-viewer.js
    ↓ (NO 3D markers - only "View X Discoveries" button in planet details)
User clicks planet → clicks "View X Discoveries" button → sees all discoveries

BACKUP: /haven-export in Discord creates JSON backup files
```

---

## What the Code Does Now

### UPDATED: Discovery Submission Path (Discord Bot)
1. User runs `/discovery-report` in Discord
2. Bot shows system selector (loads from VH-Database.db)
3. User selects system, location (planet/moon), and discovery type
4. User fills modal with discovery details
5. `enhanced_discovery.py` calls `haven.write_discovery_to_database()`
6. Discovery is written to BOTH:
   - keeper.db (bot internal database)
   - VH-Database.db (Haven Master database) ✅ DUAL-WRITE
7. Bot confirms success in Discord channel

### Display Path (map-viewer.js)
1. System view loads with DISCOVERIES_DATA array
2. Lines 698-705: Discovery data is loaded but NOT rendered as 3D markers ✅ CHANGED
3. Lines 1039-1055: When planet clicked, info panel shows planet details
4. Lines 1274-1289: If discoveries exist for planet, shows "View X Discoveries" button
5. Lines 1301-1335: Button click displays all discoveries with back button

### Control Room Discovery Viewer (NEW)
1. User opens System Entry Wizard
2. Loads system and views planet/moon details
3. Clicks "🔍 Discoveries" button on planet or moon card
4. `discoveries_window.py` opens showing all discoveries for that location
5. Supports filtering by discovery type
6. Displays full discovery details with metadata

---

## Key Files Modified

| File | Lines | What Changed |
|------|-------|--------------|
| `src/migration/import_json.py` | 25, 180-265, 268-425 | Added Keeper format detection, conversion, retry logic |
| `src/common/database.py` | 44-50 | Added timeout=10.0 and WAL mode to __enter__() |
| `src/static/js/map-viewer.js` | 1274-1335 | Added discovery button in planet details + click handler |

---

## Testing the Fix

### Step 1: Verify Database
```python
# Check discoveries were imported
import sqlite3
conn = sqlite3.connect('data/VH-Database.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM discoveries;")
print(cursor.fetchone()[0])  # Should show 17
cursor.execute("SELECT discovery_type, planet_id FROM discoveries LIMIT 5;")
print(cursor.fetchall())  # Shows sample discoveries
```

### Step 2: Regenerate Map
```powershell
python src/Beta_VH_Map.py --no-open
```

### Step 3: Test in Browser
1. Open `dist/VH-Map.html`
2. Click on "The Diamond In The Rough" system
3. In system view, click on "The Oyster" planet
4. Planet details panel should show: **"📍 View X Discoveries"** button
5. Click button → see all discoveries for that planet
6. Click "← Back" → return to planet details

---

## If Something Breaks

### Discoveries still not showing on planet?
1. Verify discoveries in DB: `SELECT COUNT(*) FROM discoveries;`
2. Check if planet_id matches: `SELECT planet_id, system_id FROM discoveries LIMIT 1;`
3. Verify planet exists: `SELECT id, name FROM planets;`
4. Check browser console for JavaScript errors

### Import still fails?
1. Check error message - if "database is locked", close Control Room first
2. Check if Keeper file is valid JSON: `python -m json.tool keeper_discoveries_backup_*.json`
3. Look for "NoneType" errors - means a field is None (check conversion logic)
4. Check logs: `tail -f logs/*.log`

### Button appears but no discoveries show?
1. Check DISCOVERIES_DATA in browser console: `console.log(DISCOVERIES_DATA)`
2. Verify discovery has correct planet_id or planet_name matching
3. Check map-viewer.js discovery filtering logic (line 1284-1287)

---

## Next Steps / Future Work

- [ ] Add ability to edit/delete discoveries in UI
- [ ] Add discovery photos/images to gallery in planet view
- [ ] Add filtering by discovery type in system view
- [ ] Add discovery metadata display (condition, significance, mystery tier)
- [ ] Add discovery location on moon/station (currently only planet-based)
- [ ] Add discovery search/filter across all systems

---

## Reference: Discovery Database Schema

```sql
CREATE TABLE discoveries (
    id INTEGER PRIMARY KEY,
    discovery_type TEXT,
    description TEXT,
    location_type TEXT,  -- 'planet', 'moon', 'space', 'deep_space'
    system_id TEXT,      -- FK to systems.id
    planet_id INTEGER,   -- FK to planets.id
    moon_id INTEGER,     -- FK to moons.id
    discovery_name TEXT,
    location_name TEXT,
    coordinates TEXT,
    condition TEXT,
    significance TEXT,
    discovered_by TEXT,
    discord_user_id TEXT,
    discord_guild_id TEXT,
    tags TEXT,           -- JSON string
    metadata TEXT,       -- JSON string
    analysis_status TEXT,
    pattern_matches INTEGER,
    mystery_tier INTEGER,
    photo_url TEXT,
    submission_timestamp DATETIME
);
```

---

## Code Snippets for Reference

### Keeper Format Detection
```python
def _is_keeper_format(self, data: dict) -> bool:
    # Has "discoveries" key = Keeper format
    if 'discoveries' in data:
        return True
    # Missing system fields = Keeper format
    return not any(k in data for k in ['name', 'x', 'y', 'z', 'region', 'systems'])
```

### Field Conversion
```python
# Maps Keeper → Haven database
type → discovery_type
location → discovery_name/location_name
evidence_url → photo_url
username → discovered_by
user_id → discord_user_id
guild_id → discord_guild_id
tags[] → json.dumps(tags)
metadata[] → json.dumps(metadata)
```

### Discovery Button HTML
```javascript
// Added to planet details when discoveries exist
<button id="view-discoveries-btn" style="...">
    📍 View ${count} Discover${plural ? 'ies' : 'y'}
</button>
```

---

## Summary

✅ **Discoveries now fully functional:**
- Import from Keeper bot without errors
- Store in database properly
- Display on system view with interactive button
- Show full details when clicked
- Handle database locking gracefully
- Safe None/null value handling

The discovery system is complete and ready for extended features (editing, photos, advanced filtering, etc.)
