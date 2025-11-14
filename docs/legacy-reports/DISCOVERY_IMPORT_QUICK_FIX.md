# DISCOVERY IMPORT FIX - QUICK SUMMARY

## What Was Wrong
The import system was importing systems and planets, but **NOT importing discovery information** from the JSON files. This is why you couldn't see the discovery button on The Oyster planet in the map view.

## What I Fixed
Modified `src/migration/import_json.py` to:
1. **Extract discovery data** from the imported JSON (both system-level and planet-level)
2. **Import discoveries** into the database using the existing `add_discovery()` method
3. **Link discoveries** to the correct planets using their database IDs

## Code Changes
- **File**: `src/migration/import_json.py`
- **Added**: `logging` import
- **Added**: `_extract_and_import_discoveries()` method (handles discovery extraction and import)
- **Modified**: `_import_system()` method (now calls discovery import after system is added)

## How to Use It
1. **Restart Control Room**
2. **Import your JSON file** with the "📥 Import JSON File" button
3. **Generate the map** with "🗺️ Generate Map"
4. **View the map** and look for **"🔍 View Discoveries"** buttons on planets that have discoveries

## Supported Discovery Formats
The import now supports discoveries nested in two ways:

### System-level discoveries
```json
{
  "System Name": {
    "discoveries": [
      { "discovery_type": "...", "description": "..." }
    ]
  }
}
```

### Planet-level discoveries
```json
{
  "System Name": {
    "planets": [
      {
        "name": "Planet Name",
        "discoveries": [
          { "discovery_type": "...", "description": "..." }
        ]
      }
    ]
  }
}
```

## Full Documentation
See `DISCOVERY_IMPORT_FIX.md` for detailed technical information.

## Next Steps
1. Test with your Keeper bot discoveries import
2. Check that discoveries appear on the map
3. Report any issues with specific discovery formats

