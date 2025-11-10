# Haven Control Room - First Run Startup Dialog

## When You Launch the EXE for the First Time

You'll see this dialog:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Haven Control Room - First Run
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Welcome to Haven Control Room!

Choose your starting data:

• YES - Start with 3 example systems (recommended)
• NO - Start with empty data

You can load your own file later from the app.

[ YES ]  [ NO ]
```

---

## What Each Option Does

### IF YOU CLICK "YES" ✅

Your data will be initialized with 3 pre-configured example systems:

1. **APOLLO PRIME**
   - Coordinates: (0.5, -0.8, 1.2)
   - Region: Core
   - Fauna: High | Flora: High
   - Materials: Carbon, Oxygen, Ferrite
   - Sentinel Level: Low
   - Description: "Starter system with abundant resources"

2. **ARTEMIS**
   - Coordinates: (-1.8, 1.1, 2.4)
   - Region: Outer Rim
   - Fauna: Medium | Flora: Low
   - Materials: Sodium, Gold, Silver
   - Sentinel Level: Medium
   - Description: "Mining Outpost Delta - Rich in precious metals"

3. **ATLAS**
   - Coordinates: (2.3, -1.5, -0.7)
   - Region: Frontier
   - Fauna: Low | Flora: Medium
   - Materials: Platinum, Copper, Chromium
   - Sentinel Level: High
   - Description: "Unexplored frontier system with rare elements"

**Perfect for:** Learning the system, seeing how data is structured, testing features

---

### IF YOU CLICK "NO" ❌

Your data will start completely empty (blank template) with only the metadata structure:

```json
{
  "_meta": {
    "version": "1.0.0",
    "description": "Empty Haven galaxy data - start fresh"
  }
}
```

**Perfect for:** Building your custom galaxy from scratch, starting with a clean slate

---

## After You Choose

### The Control Room Will:

1. Create your working data file at: `dist/files/data.json`
2. Launch the main Control Room interface
3. Show you the home screen with options to:
   - 📋 System Entry Wizard (add/edit systems)
   - 🗺️ Generate Map (create 3D visualization)
   - ⚙️ Settings

---

## Can You Change Your Mind?

**YES!** You can:

1. **Import Different Data:** Use File menu to load a different JSON file
2. **Start Over:** Delete `dist/files/data.json` and restart the app
3. **Export Current Data:** Save your work as a backup file

---

## File Locations

- **Clean Template:** `data/clean_data.json` (in EXE)
- **Example Template:** `data/example_data.json` (in EXE)
- **Your Working Data:** `dist/files/data.json` (created after you choose)

---

**Recommendation:** Start with "YES" (example systems) first to learn the system, then create a new profile with "NO" for your actual data!
