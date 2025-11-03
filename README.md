# Haven Control Room — Quick Start

Welcome! This is the Haven star mapping system with a modern GUI and 3D map viewer.

## Setup (Python Required)

1. **Install Python 3.10+** from [python.org](https://www.python.org/downloads/)
2. **Open terminal/cmd in the Haven_Mdev folder**
3. **Create virtual environment:**
   ```bash
   python -m venv .venv
   ```
4. **Activate it:**
   - Windows: `.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`
5. **Install dependencies:**
   ```bash
   pip install -r config/requirements.txt
   ```
6. **Launch Control Room:**
   - Windows (no console): Double-click `scripts/Haven Control Room.pyw`
   - Windows (legacy): `Haven Control Room.bat`
   - Mac/Linux: Double-click `haven_control_room_mac.command`

## What You Can Do

- **System Entry GUI**: Add/edit star systems with coordinates and custom fields
- **3D Galaxy Map**: Generate interactive Three.js visualizations (opens in browser)
- **Data Management**: All data stored in `data/data.json` with schema validation
- **Export Standalone App**: Build a single-file Windows EXE or a macOS app (Build Kit) from the Control Room

### Recommended entry flow

- Use the two‑page System Entry Wizard for adding complete star systems with planets and moons:
   - From Control Room: click “Launch System Entry (Wizard)”
   - Standalone: `python src/system_entry_wizard.py`
- The classic single‑page UI is still available as “Launch Classic (Phase 1)” for reference.
   - See `docs/system_entry_wizard_guide.md` for tips.

### Control Room — Full Guide

For an in-depth manual of all features, workflows, exports, and troubleshooting, see:
- `docs/Comprehensive_User_Guide.md` (highly detailed, with visuals)

## File Structure

- `data/` — Your star system data (`data.json`)
- `dist/` — Generated maps and built executables
- `logs/` — Application and map generation logs
- `src/` — Source code (GUI, map generator, Control Room)
- `config/` — Requirements, icons, settings
- `docs/` — Full documentation

## Troubleshooting

- **Missing modules**: Activate venv and run `pip install -r config/requirements.txt`
- **Map won't open**: Check `logs/` for errors; ensure data.json is valid
- **Browser logs**: Map HTML includes a "Download Logs" button for diagnostics

## Exporting and Sharing the App

You can create standalone applications for users who don't have Python installed — now including **iOS support**!

### Desktop (Windows/macOS)

1. Open the Control Room.
2. Click "Export App (EXE/.app)".
3. Choose a platform (Windows, macOS, or iOS) and select an output folder.
4. **Windows export** creates:
   - `HavenControlRoom.exe` — runs offline, creates its own Data/Logs/dist next to itself
   - A ZIP with the EXE and README for easy sharing
5. **macOS export**:
   - From Windows: creates a "Mac Build Kit" ZIP with build instructions
   - On macOS: builds the actual `.app` bundle
6. Older `.exe` files inside this repo are cleaned up automatically during export.

Notes:
- Windows SmartScreen may warn about an unknown publisher on first run. Click "More info" → "Run anyway".
- The standalone EXE/app stores data and outputs next to itself so it's fully portable.

### iOS (iPhone/iPad)

1. Open the Control Room.
2. Click "Export App (EXE/.app)".
3. Choose **iOS** from the platform dropdown.
4. Select output folder (e.g. Desktop\Haven_Exports).
5. You'll get a ZIP bundle with:
   - `Haven_Galaxy_iOS.html` — Complete PWA (Progressive Web App)
   - Installation guide with step-by-step instructions

Optional: choose “iOS (Offline)” in Export to embed the 3D library so it works with no internet at all.

To enable true offline embedding, place a local copy of Three.js here before exporting:
- `config/vendor/three.r128.min.js` (preferred)
- or `config/vendor/three.min.js`

Tip: After exporting, the offline HTML should be several hundred KB or more. If it’s ~50–60 KB, the embed file wasn’t found and it will still try online CDNs.
   
**To install on iOS:**
1. Email the HTML file to your iOS device
2. Open it in **Safari** (not Chrome)
3. Tap Share → "Add to Home Screen"
4. Launch from home screen like a native app!

**iOS Features:**
- 📱 Touch-optimized 3D galaxy map (pinch zoom, swipe rotate, tap systems)
- 🧭 Two views: Galaxy view (all systems) and System view (star + planets)
- ✏️ Full data entry form with all System Entry fields
- 💾 Local storage — all data saved on device
- 📤 Import/export JSON for backup and sharing
- ✈️ Works completely offline after first load
- 🏠 Installs to home screen like a native app

The iOS PWA is a single HTML file (~40KB) that includes everything: 3D map viewer, data entry, local storage, and offline support. Share it via email, Dropbox, or any file transfer — recipients can open it in Safari and install to their home screen!

Need more help? See `docs/README.md` for detailed instructions and advanced features.
