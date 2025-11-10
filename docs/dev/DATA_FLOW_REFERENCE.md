# Haven Data Flow Reference
**Single Source of Truth: VH-Database.db**

---

## Overview

The Haven system uses a three-tier architecture with **VH-Database.db** as the authoritative master database. JSON files are used only as an export format for portability.

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      MASTER EDITION (You)                       │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              VH-Database.db (SQLite)                     │  │
│  │  • Primary production database                           │  │
│  │  • Billion-scale capability                              │  │
│  │  • Automatic backups on startup                          │  │
│  │  • Transaction safety with rollback                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↑  ↓                                 │
│                       Import  Export                            │
│                        JSON    JSON                             │
└─────────────────────────────────────────────────────────────────┘
                              ↑  ↓
                  ┌───────────┘  └───────────┐
                  │                           │
         ┌────────▼────────┐         ┌───────▼────────┐
         │  EXE Edition    │         │  Mobile PWA     │
         │  (Users)        │         │  (Browser)      │
         │                 │         │                 │
         │  data.json      │         │  data.json      │
         │  (Portable)     │         │  (LocalStorage) │
         └─────────────────┘         └─────────────────┘
```

---

## Tier 1: Master Edition (Your Version)

### Database: VH-Database.db

**Location:** `data/VH-Database.db`

**Purpose:**
- THE authoritative source of truth for all production data
- Designed for billion-scale system storage
- Used exclusively by you (the developer) for data management

**Capabilities:**
- Full database operations (CRUD)
- Spatial queries for finding nearby systems
- Advanced filtering and search
- Database statistics
- Automatic schema management

**Backup System:**
- Creates backup on every Control Room launch
- Keeps last 10 backups in `data/backups/`
- Format: `VH-Database_backup_YYYYMMDD_HHMMSS.db`

**Import/Export:**
- **Import:** Can import JSON files from EXE/Mobile users
  - Via Control Room: "Import JSON File" button
  - Uses atomic writes for safety
  - Validates data before import
- **Export:** Can export to JSON for sharing
  - Via Control Room: "Export JSON" button
  - Creates portable JSON file

---

## Tier 2: EXE Edition (Distributed to Users)

### Data: data.json

**Location:** `files/data.json` (relative to EXE location)

**Purpose:**
- Portable data file for users without Python/database knowledge
- Runs on any Windows machine
- Easy to share and backup

**Limitations:**
- Practical limit: ~1,000-10,000 systems
- Performance degrades with large datasets
- No advanced database features

**Workflow:**
1. User discovers star systems in No Man's Sky
2. User enters data via System Entry Wizard
3. Data saved to `data.json`
4. User exports JSON file
5. **User sends JSON to you**
6. **You import into Master VH-Database.db**

**Export Process:**
- User clicks "Export Data" in EXE
- Creates timestamped JSON file: `haven_export_YYYYMMDD.json`
- User emails/shares this file with you

---

## Tier 3: Mobile PWA (Browser-Based)

### File: Haven_Mobile_Explorer.html

**Location:** `dist/Haven_Mobile_Explorer.html`

**Purpose:**
- View star systems on mobile devices
- Single-file HTML (54.5 KB)
- Works offline after first load
- No installation required

**Data Storage:**
- Browser LocalStorage (temporary)
- Can export to JSON for backup

**Workflow:**
1. User opens HTML file in browser
2. Data loaded from LocalStorage or imported JSON
3. User browses systems, planets, moons
4. User can export to JSON
5. **User sends JSON to you**
6. **You import into Master VH-Database.db**

---

## Data Import Process (Master Edition)

### When to Import

You import JSON files when:
1. EXE users send you their discoveries
2. Mobile users send you their data
3. You're consolidating data from multiple sources
4. You're migrating from old JSON-based system

### How to Import

**Via Control Room GUI:**
1. Click "📥 Import JSON File" in sidebar
2. Select JSON file to import
3. Choose options:
   - ☐ Allow updates to existing systems
   - ☑ Skip duplicate systems (default)
4. Click "Import"
5. Review import summary
6. Data is now in VH-Database.db ✅

**Import Safety Features:**
- ✅ Atomic writes (rollback on error)
- ✅ Data validation before import
- ✅ Duplicate detection
- ✅ Transaction safety
- ✅ Automatic backup before import

### Import Validation

The importer checks:
- Valid JSON format
- Required fields present (name, x, y, z, region)
- Coordinate ranges valid
- No duplicate system names (unless updates allowed)

---

## Data Export Process (Master Edition)

### When to Export

You export JSON when:
1. Sharing data with EXE users
2. Creating backups
3. Distributing data to community
4. Migrating to another system

### How to Export

**Via Control Room GUI:**
1. Click "Export Data" (if available) or use sync dialog
2. Choose export location
3. Select systems to export:
   - All systems
   - Specific region
   - Filtered selection
4. Click "Export"
5. JSON file created ✅

**Export Format:**
- Same format as EXE/Mobile JSON
- Compatible with all Haven versions
- Human-readable (formatted with indent=2)

---

## Single Source of Truth

### What This Means

**VH-Database.db is the ONLY authoritative database**

- All production data lives here
- JSON files are **exports only**, not primary storage
- EXE/Mobile users work in JSON temporarily
- Master consolidates all data into VH-Database.db

### Data Flow Rules

1. **Master → Export → JSON**
   - You export from VH-Database.db
   - JSON sent to users
   - Users view/edit in EXE/Mobile

2. **EXE/Mobile → Export → JSON → Import → Master**
   - Users discover new systems
   - Users export JSON
   - You import JSON into VH-Database.db
   - Master database updated ✅

3. **Never:** JSON ↔ JSON (always through Master)
   - Don't merge JSON files manually
   - Always import into Master first
   - Let Master handle deduplication

---

## Data Sync Status

The Control Room shows sync status between JSON and database:

**Status Messages:**
- ✅ "Data sync OK: JSON and database both have X systems"
  - Both backends in sync
  - Safe to use either

- ⚠️ "Data out of sync: JSON has X systems, Database has Y systems"
  - Backends have different data
  - Use sync dialog to resolve

**Sync Options:**
1. **JSON → Database** - Import JSON data into database
2. **Database → JSON** - Export database to JSON
3. **Two-way sync** - Merge both (advanced)

---

## Database Schema

### Systems Table
```sql
CREATE TABLE systems (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    x REAL NOT NULL,
    y REAL NOT NULL,
    z REAL NOT NULL,
    region TEXT NOT NULL,
    fauna TEXT,
    flora TEXT,
    sentinel TEXT,
    materials TEXT,
    base_location TEXT,
    photo TEXT,
    attributes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Related Tables
- **planets** - Planet data (linked to systems)
- **moons** - Moon data (linked to planets)
- **space_stations** - Station data (linked to systems)
- **_metadata** - Database metadata

### Indexes
- `idx_systems_name` - Fast lookup by name
- `idx_systems_region` - Fast filtering by region
- `idx_systems_coords` - Spatial queries (x, y, z)

---

## JSON Format

### Structure
```json
{
    "_meta": {
        "version": "1.0",
        "created": "2025-11-10T12:00:00",
        "last_modified": "2025-11-10T14:00:00",
        "system_count": 100
    },
    "SYS_ADAM_001": {
        "id": "SYS_ADAM_001",
        "name": "OOTLEFAR V",
        "x": 123.45,
        "y": 67.89,
        "z": -101.23,
        "region": "Adam",
        "fauna": "High",
        "flora": "Medium",
        "sentinel": "Low",
        "planets": [
            {
                "name": "Planet Alpha",
                "sentinel": "Low",
                "fauna": "High",
                "flora": "Medium"
            }
        ]
    }
}
```

---

## File Locations

### Master Edition
```
Haven_mdev/
├── data/
│   ├── VH-Database.db          ← MASTER DATABASE ✨
│   ├── data.json               ← Template/temporary JSON
│   ├── clean_data.json         ← Empty template
│   └── backups/
│       └── VH-Database_backup_*.db
├── config/
│   └── settings.py             ← Points to VH-Database.db
└── src/
    └── control_room.py         ← Main application
```

### EXE Edition
```
HavenControlRoom.exe
files/
├── data.json                    ← User's data (portable)
└── settings.json                ← User settings
```

### Mobile PWA
```
Haven_Mobile_Explorer.html       ← Single file (54.5 KB)
  + LocalStorage in browser      ← Temporary data
```

---

## Best Practices

### For Master Edition (You)

1. **Always keep VH-Database.db backed up**
   - Automatic backups happen on startup ✅
   - Manual backup: Copy VH-Database.db to safe location
   - Keep backups in multiple locations

2. **Import workflow:**
   - Receive JSON from users
   - Import via Control Room GUI
   - Verify data looks correct
   - Original JSON becomes backup

3. **Export workflow:**
   - Export from VH-Database.db
   - Send JSON to users
   - Keep copy of exported JSON

### For EXE Users

1. **Regular exports:**
   - Export data frequently
   - Keep multiple timestamped backups
   - Send exports to Master periodically

2. **Backup strategy:**
   - Copy data.json regularly
   - Keep old exports
   - Don't rely on single copy

### For Mobile Users

1. **LocalStorage is temporary:**
   - Export to JSON for backup
   - Browser data can be lost
   - Re-import JSON if needed

---

## Troubleshooting

### "Database is locked"
- Another process has VH-Database.db open
- Close all Haven applications
- Restart Control Room

### "Import failed - duplicate system"
- System name already exists in database
- Check "Allow updates" to overwrite
- Or rename system in JSON before import

### "JSON file invalid"
- Check JSON syntax
- Verify required fields present
- Use data.schema.json for validation

### "Out of sync"
- Use Sync Data dialog
- Choose direction: JSON→DB or DB→JSON
- Review changes before confirming

---

## Summary

**Remember:**
- VH-Database.db = Master database (single source of truth)
- JSON = Export format for portability
- EXE/Mobile → JSON → Master
- Always import user data into Master
- Master consolidates all discoveries

**Data flows up to Master, exports flow down to users.**

This ensures data integrity and prevents conflicts! ✅
