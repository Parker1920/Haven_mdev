# Keeper Bot Discoveries Format Support

**Date**: November 10, 2025  
**Status**: ADDED TO IMPORT SYSTEM

---

## Problem

The Keeper Discord bot exports discoveries in a **different JSON format** than the Haven system export format. The original import code only recognized the Haven format (systems at top level), so Keeper discoveries were being rejected with:

```
⚠️  WARNING: No systems found in keeper_discoveries_backup_20251107_230617.json
```

---

## Solution

Added automatic format detection and dual-path import system:

### 1. Keeper Format Detection (`_is_keeper_format()`)
- Checks if JSON has a `"discoveries"` array
- Checks if it lacks standard system fields (name, x, y, z, region)
- Returns `True` if it appears to be Keeper format

### 2. Keeper Discoveries Import (`_import_keeper_discoveries()`)
- Extracts the `"discoveries"` list from the JSON
- Imports each discovery to the database using `add_discovery()`
- Sets default values for required fields if missing
- Reports success/failure count

### 3. Automatic Routing
- `import_file()` now detects the format
- Routes to `_import_keeper_discoveries()` for Keeper format
- Routes to standard system import for Haven format

---

## Supported Formats

### Haven Format (System Export)
```json
{
  "_meta": { "version": "1.0", "system_count": 2 },
  "System Name": {
    "id": "SYS_REGION_...",
    "name": "System Name",
    "x": 0, "y": 0, "z": 0,
    "region": "Euclid",
    "planets": [...],
    "discoveries": [...]  // Optional
  }
}
```

### Keeper Format (Discovery Export)
```json
{
  "discoveries": [
    {
      "discovery_type": "artifact",
      "description": "Ancient structure found",
      "location_type": "planet",
      "location_name": "The Oyster",
      "discovered_by": "PinkPlasma6083",
      "coordinates": "1.5, 2.3, 3.1",
      "tags": ["rare", "ancient"]
    },
    {...}
  ],
  "metadata": {
    "exported_at": "2025-11-07T23:06:17.000Z",
    "bot_version": "1.0"
  }
}
```

---

## How to Use

### Importing Keeper Discoveries

1. **Restart Control Room**
2. Click **"📥 Import JSON File"**
3. Select your **keeper_discoveries_backup_YYYYMMDD_HHMMSS.json** file
4. Click **Import**

**Expected Output:**
```
IMPORTING: keeper_discoveries_backup_20251107_230617.json
Detected Keeper discoveries format
✓ Found X discoveries to import
✓ Keeper discoveries imported: X
```

### Importing Haven System Export

Same process - the format is automatically detected and routed appropriately.

---

## Technical Details

### Discovery Data Mapping

When importing Keeper discoveries, the system maps fields:

```python
# Required (with defaults if missing)
- discovery_type → 'unknown'
- description → ''
- location_type → 'planet'

# Optional (preserved as-is)
- location_name
- coordinates
- condition
- time_period
- significance
- discovered_by
- discord_user_id
- discord_guild_id
- tags
- metadata
```

### Database Integration

Uses existing `HavenDatabase.add_discovery()` method:
```python
with HavenDatabase(DATABASE_PATH) as db:
    db.add_discovery(disc_data)  # Stores in discoveries table
```

---

## Verification

After importing Keeper discoveries, verify they're in the database:

```python
import sqlite3

conn = sqlite3.connect('data/VH-Database.db')
cursor = conn.cursor()

# Count total discoveries
cursor.execute("SELECT COUNT(*) FROM discoveries;")
total = cursor.fetchone()[0]
print(f"Total discoveries in database: {total}")

# View some discoveries
cursor.execute("SELECT discovery_type, description FROM discoveries LIMIT 5;")
for disc_type, desc in cursor.fetchall():
    print(f"  [{disc_type}] {desc[:50]}...")

conn.close()
```

---

## Error Handling

If a discovery fails to import:
- ⚠️ Warning is logged
- Failed count incremented
- Import continues with remaining discoveries
- Report shows import count vs failed count

---

## Next Steps

To use this with The Oyster planet:

1. Make sure your Keeper backup file is in `data/imports/`
2. Restart Control Room
3. Import the file - it will now be recognized as Keeper format
4. Discoveries will be stored in the database
5. Generate map and look for "🔍 View Discoveries" button on planets

---

## Files Modified

- `src/migration/import_json.py`
  - Added: `_is_keeper_format()` method
  - Added: `_import_keeper_discoveries()` method
  - Modified: `import_file()` to detect and route formats

