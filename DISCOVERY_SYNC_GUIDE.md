# Discovery Integration: Current State & How To Sync

## The Situation

You submitted a discovery ("Technological Signature Detected") via the Discord bot, and it was successfully archived in **The Keeper Bot's database**.

However, discoveries are stored in **two separate locations**:
1. **The Keeper Bot's Database** (`keeper.db`) - where the bot stores discoveries for its own archive
2. **Haven Database** (`VH-Database.db`) - where the map reads discoveries from

Currently, discoveries submitted via the bot are NOT automatically synced to the Haven database.

---

## Architecture Diagram

```
User submits discovery via Discord
    ↓
The Keeper Bot receives /discovery-report
    ↓
Bot stores in keeper.db (bot's archive)
    ↓
??? (nothing happens automatically)
    ↓
Haven map generates from VH-Database.db
    ↓
Discovery doesn't appear on map ❌
```

---

## Solution: Use `/haven-export` Command

The bot has a built-in command to export discoveries:

**Command:** `/haven-export`

**What it does:**
1. Gathers all discoveries from the bot's archive
2. Exports them in Haven-compatible format
3. Writes them to `VH-Database.db`
4. Creates a backup JSON file

**How to use:**
```
In Discord:
/haven-export system_name: [optional - leave empty for all systems]
```

---

## Step-by-Step: Make Discoveries Appear on Map

### Step 1: Export Discoveries from Bot
In Discord, run:
```
/haven-export
```

The bot will:
- Show you a summary of exported discoveries
- Write them to the Haven database
- Create a backup JSON file

### Step 2: Regenerate the Map
In Haven Control Room:
- Click "Generate Map" button
- OR run: `python src/Beta_VH_Map.py`

The map will now:
- Load discoveries from the database ✅
- Render them as colored markers ✅
- Make them clickable for details ✅

---

## Current Implementation Status

### ✅ What's Working
- Bot archives discoveries in keeper.db
- Haven database schema supports discoveries
- Map generator includes discovery rendering code
- JavaScript displays discoveries with:
  - Type-specific colors
  - Interactive markers
  - Info panels on click
  - Hover details

### ⚠️ What Needs Sync
- Discoveries in keeper.db are NOT automatically mirrored to VH-Database.db
- User must explicitly run `/haven-export` to sync

### 🔧 Future Enhancement
To make this fully automatic:
- Modify bot to write discoveries to **both** databases simultaneously
- OR set up periodic sync job
- OR create a management dashboard for syncing

---

## Technical Details

### The Keeper Bot Code Flow

```python
# In enhanced_discovery.py
async def process_discovery_submission():
    # Saves to bot's keeper.db
    await self.db.add_discovery(discovery_data)
    
    # OPTIONALLY writes to Haven database
    if discovery_data.get('haven_data'):
        haven_discovery_id = self.haven.write_discovery_to_database(enhanced_data)
```

### Haven Integration Code
Location: `docs/guides/Haven-lore/keeper-bot/src/core/haven_integration.py`

Method: `write_discovery_to_database()`
- Resolves system/planet/moon IDs
- Inserts into VH-Database.db
- Handles foreign keys properly

---

## Manual Database Sync (Advanced)

If `/haven-export` isn't working, you can manually sync discoveries:

```sql
-- In keeper.db, export discoveries:
SELECT * FROM discoveries;

-- Then insert into VH-Database.db:
INSERT INTO discoveries (
    system_id, planet_id, moon_id, discovery_type,
    location_type, location_name, description,
    discovered_by, submission_timestamp, mystery_tier
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
```

---

## Map Rendering Features

Once discoveries are synced to the Haven database and the map is regenerated, you'll see:

### Visual Markers
- **Tetrahedral mesh** for each discovery
- **Color-coded** by discovery type:
  - 🦴 Bones → Tan
  - 📜 Logs → Green
  - 🏛️ Ruins → Orange
  - ⚙️ Tech → Cyan
  - 🌿 Flora → Lime Green
  - 🦁 Fauna → Hot Pink
  - ⚡ Energy → Red
  - 📡 Signal → Purple

### Interactive Features
- **Click** any discovery marker
- **Info panel** shows:
  - Discovery type
  - Full description
  - Explorer's name
  - Date discovered
  - Condition
  - Significance level
  - Mystery tier (if applicable)

---

## Summary

**Your discovery IS saved** ✅ - It's in the bot's archive

**To make it appear on the map:**
1. Run `/haven-export` in Discord
2. Regenerate the map in Haven Control Room
3. Discovery markers will appear on the 3D map!

---

## Need Help?

- Check bot logs for export errors
- Verify database paths in bot config
- Ensure Haven database file exists
- See `DISCOVERIES_FIX_REPORT.md` for technical details
