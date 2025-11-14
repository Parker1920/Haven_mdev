# Haven Starmap — Comprehensive User Guide

Welcome to the all-in-one guide for Haven Control Room, System Entry, the 3D Galaxy Map, and the iOS PWA. This document goes deep: what each part does, how they fit together, and how to troubleshoot when things go sideways.

> Tip: If you just need a quick start, see the root `README.md`. This guide is intended as a thorough reference.

---

## 1) Overview

Haven is a star mapping and data collection toolkit with:
- Control Room (desktop): central launcher, logs, exports, and quick actions
- System Entry (desktop): add/edit your star systems and related details
- 3D Galaxy Map (browser): interactive visualization of your systems
- iOS PWA (mobile): single-file “app” for Safari with map + data entry

Your data lives in `data/data.json`. Everything else (logs, built maps, exports) lives alongside it for portability.

![Portal example 1](../photos/New-portal.png)

> Visuals in this doc are thematic. Exact UI may vary slightly across versions.

---

## 2) Control Room

The Control Room is your mission control.

### Launching
- Windows (no console): double‑click `scripts/Haven Control Room.pyw`
- Windows (legacy): `Haven Control Room.bat`
- Mac/Linux: `haven_control_room_mac.command`

### Layout
- Quick Actions: launch System Entry, generate map, open latest map
- File Management: shortcuts to Data, Logs, and Documentation
- Advanced Tools (hidden in EXE): dependency updates and export dialog
- Status + Logs: live running log inside the Control Room

![Portal example 2](../photos/Lep-portal.png)

### Quick Actions
- Launch System Entry: opens the data entry GUI
- Generate Map: builds a fresh 3D map HTML into `dist/`
- Open Latest Map: opens the newest HTML map in your default browser

### File Management
- Data Folder: view `data/data.json` and related files
- Logs Folder: check logs when something fails (map generation or exports)
- Documentation: opens the `docs/` folder

### Advanced Tools (when running from source)
- Update Dependencies: runs `pip install -r config/requirements.txt`
- Export App (EXE/.app): see full export section below

---

## 3) System Entry (Desktop)

System Entry lets you add and edit the systems you track.

### Key Fields (typical)
- Name (required)
- Region (optional)
- Coordinates: X, Y, Z (required)
- Planets (comma‑separated list)
- Fauna / Flora counts
- Sentinel level (None, Low, Medium, High, Aggressive)
- Materials (free text)
- Base location (free text)

### Workflow
1. Launch Control Room → “Launch System Entry”
2. Enter system details → Save
3. Repeat for additional systems
4. Data is written to `data/data.json`

> Tip: Keep coordinates within a practical range so they render well on the map.

![Portal example 3](../photos/oot-portal.png)

---

## 4) 3D Galaxy Map (Browser)

The map is an interactive Three.js visualization you open in your browser.

### How to generate
- From Control Room → “Generate Map”
- Output: `dist/VH-Map.html` (or the newest map under `dist/`)

### How to open
- Control Room → “Open Latest Map” (recommended), or
- Open `dist/VH-Map.html` in your browser manually

### Views
- Galaxy view: all systems appear as markers in 3D space
- System view: star + orbit rings + planets for the selected system

### Controls
- Mouse: drag to rotate, wheel to zoom
- Mobile: swipe to rotate; pinch to zoom; tap system to select
- Buttons: Reset View, Grid toggle

### Data overlay
- Tapping/clicking a system shows details: name, region, coordinates, planets, fauna/flora, sentinel, etc.

![Portal example 4](../photos/Wos-portal.png)

---

## 5) iOS PWA (Mobile)

A single HTML file that provides both the 3D map and the data entry form, designed for Safari on iPhone/iPad.

### Exporting
1. Control Room → Export App (EXE/.app)
2. Platform: iOS
3. Choose output directory
4. You’ll get a ZIP with `Haven_Galaxy_iOS.html` plus an install guide

### Installing to Home Screen
1. Email `Haven_Galaxy_iOS.html` to your device
2. Open in Safari
3. Share → Add to Home Screen
4. Launch from your home screen (full‑screen app-like experience)

### Features
- Map + Data Entry in one page
- Local storage on the device (persists between sessions)
- Import/export JSON for backups and sharing
- Offline capable after first load
- Diagnostics: on‑screen error details, retry, and “Skip Map” fallback

### Known iOS considerations
- First load requires internet to fetch the 3D library
- Content blockers or poor network can delay/stop load
- Built‑in diagnostics will show retry/skip options

---

## 6) Data, Files, and Folders

- `data/data.json`: your saved systems
- `dist/`: generated HTML map(s) and exports
- `logs/`: application and build logs
- `config/`: requirements, icons, pyinstaller settings
- `src/`: Python sources (Control Room, System Entry, PWA generator)
- `docs/`: documentation (this file, guides, build notes)

### Portability
- The standalone EXE places Data/Logs/dist next to itself, so you can carry it on a USB drive and keep everything together.

### JSON format
- Simple array of system objects, or an object with a `data` key
- Typical schema:
```json
[
  {
    "name": "Kepler‑442",
    "region": "Orion Arm",
    "x": 12.5,
    "y": -7.2,
    "z": 30.0,
    "planets": ["Terra", "Mars"],
    "fauna": 12,
    "flora": 25,
    "sentinel": "Low",
    "materials": "Copper, Sodium",
    "base_location": "Planet 2, 123,456"
  }
]
```

---

## 7) Exporting Apps

### Windows (EXE)
- From Control Room (running from source): Export App → Windows
- Generates `HavenControlRoom.exe` in your chosen folder
- Also creates a ZIP for email distribution
- Data/Logs/dist folders sit next to the EXE at runtime (portable)

### macOS
- From Windows: Export App → macOS
  - Produces a "Mac Build Kit" ZIP with instructions
- From macOS: builds the actual `.app` bundle via PyInstaller

### iOS PWA
- Generates `Haven_Galaxy_iOS.html` + installation guide
- Share via email/cloud and install on Safari

---

## 8) Common Workflows

- Add systems on desktop → Generate map → View in browser → Export to iOS for field use
- Use iOS PWA in the field to add/update systems → Export JSON → Import on desktop
- Build Windows EXE for teammates without Python → Share the EXE ZIP

---

## 9) Troubleshooting

### Control Room won’t launch
- On Windows, use `scripts/Haven Control Room.pyw` for no‑console launch
- Ensure Python 3.10+ is installed if running from source
- Check `logs/` for detailed errors

### Missing modules
- Activate your virtual environment and run:
```powershell
pip install -r config/requirements.txt
```

### Map generation fails
- Inspect the latest `logs/map-gen-*.log`
- Validate your `data/data.json` (look for trailing commas, invalid numbers)

### iOS PWA stuck on “INITIALIZING…”
- Requires network on first load (fetches 3D library)
- Disable content blockers for Safari temporarily
- Use on‑screen Retry or “Skip Map” (data entry only) and continue working offline

### EXE build issues (Windows)
- Close apps that might lock the build folder (OneDrive can lock files)
- Re‑try export; see `logs/export-windows-*.log` for details

---

## 10) Privacy & Storage

- Data is stored locally on your machine/device
- Nothing is uploaded unless you choose to share the JSON or HTML
- For backups: regularly export JSON from desktop and/or iOS

---

## 11) FAQs

- Q: Can I change the look of the map?
  - A: Yes, edit `src/Beta_VH_Map.py` and regenerate the map.
- Q: Do I need internet to use the iOS PWA?
  - A: First load needs internet to fetch the 3D library. After that, it works offline.
- Q: Where are logs stored?
  - A: Under `logs/`, with timestamps in filenames.
- Q: Can I share my data with a friend?
  - A: Export JSON (desktop or iOS) and send the file. They can import it on their side.

---

## 12) Versioning & Updates

- Keep your environment current by running dependency updates from Control Room (when not in the EXE), or run:
```powershell
pip install -r config/requirements.txt
```
- New releases may enhance iOS performance, add fields, or refine export flows.

---

## 13) Where to Get Help

- Check `docs/` for topic‑specific guides:
  - iOS Testing Guide: `docs/iOS_Testing_Guide.md`
  - iOS PWA Guide: `docs/iOS_PWA_Guide.md`
  - Building EXE: `docs/BUILDING_EXE.md`
  - Folder Structure: `docs/FOLDER_STRUCTURE.md`
- Still stuck? Review logs in `logs/` and share the error snippet when asking for help.

---

Built with ❤️ for the Haven Galaxy community.
