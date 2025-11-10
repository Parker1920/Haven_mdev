# Haven Control Room - Startup Options

## First Run Experience

When you launch the Control Room EXE for the first time, you'll be prompted to choose your starting data:

### Option 1: Start with Example Data (Recommended)
- **Choice:** YES
- **Includes:** 3 sample systems pre-configured
  - APOLLO PRIME - Central Trading Hub
  - ARTEMIS - Mining Outpost Delta  
  - ATLAS - Frontier System
- **Use Case:** Get familiar with the features, see how data is structured
- **File:** `example_data.json` (bundled in EXE)

### Option 2: Start with Clean/Blank Data
- **Choice:** NO
- **Includes:** Empty template with just metadata
- **Use Case:** Build your galaxy from scratch
- **File:** `clean_data.json` (bundled in EXE)

## Files Available

Both starter files are bundled inside the frozen EXE:

| File | Location | Size | Purpose |
|------|----------|------|---------|
| `clean_data.json` | `data/` | ~300 bytes | Blank template |
| `example_data.json` | `data/` | ~2 KB | 3 sample systems |
| `data.json` | `dist/files/` | Auto-created | Your working data |

## Using the System Entry Wizard

Once you've selected your starting data, you can:

1. **Add Systems** - Click "New System" to create custom systems
2. **Edit Systems** - Click existing systems to modify their details
3. **Add Planets** - Each system can have multiple planets
4. **Generate Maps** - Click "Generate Map" to create 3D visualization

## Data Persistence

- Your data is saved to: `dist/files/data.json`
- Backups are created automatically
- You can export/import data files anytime

## Resetting to Start Fresh

If you want to start over:
1. Delete `dist/files/data.json`
2. Restart the Control Room
3. Choose your starting option again

---

**Last Updated:** November 6, 2025  
**Version:** User Edition 1.0
