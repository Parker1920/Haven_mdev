# Haven Galaxy - Beta VH Map

A **fully data-driven** Three.js-based interactive 3D star map visualization system.

## What Does This Do?

This tool creates professional 3D interactive visualizations of stellar systems from JSON data:
- **Galaxy View**: Overview showing all regions as clickable markers
- **System View**: Detailed view of individual systems within each region
- **Fully Data-Driven**: Add any fields to your JSON - they'll automatically appear in info panels
- **Flexible Types**: Systems, moons, stations, or custom object types you define
- **Beautiful Rendering**: Professional lighting, rotating diamond icons, animated stars, and smooth interactions

### Key Innovation: 100% Data-Driven Architecture

Unlike traditional visualization tools, this system reads **everything** from your JSON data (`data.json`):
- ✅ Add new object types without modifying code
- ✅ Any JSON field automatically displays in info panels
- ✅ If data isn't present, it simply isn't rendered
- ✅ Visual styling via easy-to-edit configuration object in `Beta_VH_Map.py`

## First Time Setup (5 Minutes)

### Step 1: Install Python Requirements

Open PowerShell in this folder and run:

```powershell
pip install -r requirements.txt
```

That's it! You're ready to go.

## Daily Use - Simple 3-Step Workflow

### Step 1: Add Your System

Run the data entry tool:

```powershell
python system_entry_modern.py
```

A window opens - just fill in the blanks like you're taking notes:
- **Name**: OOTLEFAR V
- **Region**: Pick from dropdown (Adam or Star)
- **Coordinates**: X, Y, Z numbers from your portal address
- **Fauna/Flora/Sentinel**: Just type what you see
- **Materials**: Type them one per line (or comma-separated)
- **Photo**: Click Browse and pick your screenshot
- **Custom Fields**: Add your own fields using the "⚙ Manage Fields" button!

Click **Save to JSON** - done! The tool auto-generates the system ID.

#### 🆕 Managing Custom Fields

Click **"⚙ Manage Fields"** in the top-right to:
- **Add Field**: Create new custom fields (e.g., "water_coverage", "economy_type")
- **Rename Field**: Change field names across all existing records
- **Remove Field**: Delete fields from all records (with backup)
- **View All**: See every field in your data with usage counts

Fields you add appear immediately in the form and are saved with each system!

### Step 2: Generate Your Map

```powershell
python Beta_VH_Map.py
```

This creates the HTML files with your 3D visualization.

> **Note**: Older versions (e.g., `json_test.py` for Plotly, `json_test_threejs.py` for earlier Three.js) are deprecated. Use `system_entry_modern.py` for data entry and `Beta_VH_Map.py` for map generation.

### Step 3: View and Explore

The map opens automatically in your browser!
- **Overview**: Click any region dot to zoom in
- **Region view**: Click any planet to see its info panel on the right
- Rotate, zoom, and explore in 3D
- If something looks off in the browser, use the "Download Logs" button (bottom-right) to save a diagnostics file you can share.

That's the whole workflow! Repeat Step 1-3 whenever you find a new system.

## Quick Tips

### Taking System Screenshots

1. Go to a portal in No Man's Sky
2. Take a screenshot (save to `photos/` folder)
3. Rename it with the first 3 letters of the system name (e.g., `Oot-portal.png`)
4. Use Browse button in the data entry tool to select it

### Understanding Coordinates

- **X, Y, Z** are just numbers that position the system in 3D space
- You can use whole numbers (1, 2, 3) or decimals (1.5, -0.9)
- Negative numbers are fine!
- The tool converts them to orbit around a central sun automatically

### Materials Entry Made Easy

All three ways work the same:

```
One per line:
Magnetized Ferrite
Gold
Cadmium

Comma-separated:
Magnetized Ferrite, Gold, Cadmium

With dashes:
-Magnetized Ferrite
-Gold
-Cadmium
```

Type it however is easiest for you!

## Common Questions

**Q: Do I need to know Python or coding?**  
A: Nope! Just follow the 3 steps above. The GUI does everything for you.

**Q: What if I make a mistake?**  
A: No problem! The data entry tool validates your input. If something's wrong, it tells you before saving.

**Q: Can I edit a system after adding it?**  
A: Yes - open `data.json` in a text editor, make your change, and re-run `python Beta_VH_Map.py`.

**Q: Photo not showing up?**  
A: Make sure the photo is in the `photos/` folder and you selected it with the Browse button.

**Q: What are the colored dots in the overview?**  
A: Each color is a different region (Adam, Star, etc.). Click one to see all systems in that region.

**Q: Can I add more regions besides Adam and Star?**  
A: Yes! Just type a new region name in the dropdown and it automatically creates one.

## Saving Your Work (Git)

Your project is already set up with Git to track changes!

### Basic: Save Your Progress

After adding systems or making changes:

```powershell
git add *FileName*
git commit -m "Added 5 new systems to Adam region"
```

That's it! Your changes are saved locally with a description.

### View History

```powershell
git log --oneline
```

Shows all your saves with descriptions.

### First-Time GitHub Setup (Your Personal Backup)

If you downloaded this from someone else's GitHub, you need to create YOUR OWN repository to save your changes:

1. **Create your own repository:**
   - Go to https://github.com/new
   - Name it `haven-starmap` (or whatever you want)
   - Make it Public or Private (your choice)
   - **Important**: Don't check "Initialize with README"
   - Click "Create repository"

2. **Link your local project to YOUR repository:**
   ```powershell
   # Remove the original repository link (if it exists)
   git remote remove origin
   
   # Add YOUR repository (replace YOUR-USERNAME with your GitHub username)
   git remote add origin https://github.com/YOUR-USERNAME/haven-starmap.git
   
   # Push your work to YOUR repository
   git push -u origin Main
   ```
   
  # Haven Galaxy – Data-Driven 3D Starmap

  An easy, modern workflow to enter star systems and generate interactive 3D maps.

  ## TL;DR Quick Start

  1) Install requirements

  ```powershell
  pip install -r requirements.txt
  ```

  2) One‑click run (Windows/macOS)

  - Windows: double‑click `scripts/Haven Control Room.bat` (menu: GUI / Build / Update)
  - macOS: double‑click `scripts/haven_control_room_mac.command` (you may need to allow it in Security & Privacy the first time)

  3) Enter or edit systems (beautiful modern GUI)

  ```powershell
  python system_entry_modern.py
  ```

  4) Generate the 3D map

  ```powershell
  python Beta_VH_Map.py
  ```

  Outputs: `dist/VH-Map.html` (Galaxy View) and `dist/system_<Region>.html` pages (System Views).

  ---

  ## What’s Included

  - system_entry_modern.py – Modern glassmorphism GUI for adding/editing systems
  - Beta_VH_Map.py – Three.js-based 3D map generator (data-driven)
  - data.json – Your data, in a simple wrapper structure
  - data.schema.json – JSON Schema for optional validation
  - photos/ – Put screenshots here (referenced by data.json)
  - .vscode/tasks.json – One-click VS Code build task for map generation

  ## The Data: Simple and Flexible

  Top-level object with metadata and a flat `data` array:

  ```json
  {
    "_meta": { "version": "1.0.0", "last_modified": "2025-11-02T00:00:00Z" },
    "data": [
      { "type": "region", "region": "Adam", "x": 0.15, "y": 0.0, "z": 0.0 },
      { "type": "region", "region": "Star", "x": 0.0, "y": 0.0, "z": 0.0 },
      { "id": "SYS_ADAM_1", "name": "OOTLEFAR V", "region": "Adam", "x": 3, "y": 2, "z": 1, "materials": "Magnetized ferrite, Gold, Cadmium" }
    ]
  }
  ```

  - Region markers: `{ "type": "region", "region": "…", "x": …, "y": …, "z": … }`
  - Systems: `{ "id", "name", "region", "x", "y", "z", ...any other fields }`
  - Add any custom fields you want; the map info panel shows them automatically.

  ## Entering Data: Modern GUI Highlights

  Run:

  ```powershell
  python system_entry_modern.py
  ```

  Features:

  - Clean, futuristic UI (CustomTkinter + glassmorphism)
  - Theme switching (Settings → choose theme)
  - Inline validation for required fields and coordinates
  - Undo/Redo and keyboard shortcuts
    - Ctrl+S Save
    - Ctrl+N New/Clear
    - Ctrl+Z Undo
    - Ctrl+Y Redo
  - “Manage Fields” dialog
    - Add new custom fields globally
    - Rename existing fields across all records
    - Remove fields from all records
    - View all fields in your data
  - Auto region marker creation
    - If you type a new region, a region marker is created automatically
  - Safe saves with backup behavior and JSON kept in a consistent structure

  Tip: Put screenshots in `photos/` and store the relative path in a `photo` field.

  ## Generating the Map

  ```powershell
  python Beta_VH_Map.py
  ```

  Flags you can use:

  ```powershell
  python Beta_VH_Map.py --no-open
  python Beta_VH_Map.py --out MyGalaxy.html
  ```

  What it generates:

  - `dist/VH-Map.html`: Galaxy View with one marker per region
  - `dist/system_<Region>.html`: System View pages with all systems for each region

  How to use:

  - Galaxy → Click a region marker to see its systems
  - System View → Click a system to open its details (info panel lists every field from your data)
  - Rotate, pan, and zoom in 3D; lighting and animations included

  ## VS Code One-Click Build

  Use the preconfigured task:

  - Command Palette → “Run Task” → “Build starmap pages”
  - It runs: `python Beta_VH_Map.py --no-open`

  You can adjust the task in `.vscode/tasks.json`.

  ## One‑Click Scripts (No IDE needed)

  - Windows
    - `scripts/Haven Control Room.bat` → simple menu to open GUI, build map, or run update
    - `scripts/Galactic Archive Terminal.bat` → launches the GUI (auto‑creates venv, installs deps if needed)
    - `scripts/Atlas Array.bat` → generates the map and opens your browser
    - `scripts/Holo-Net Update.bat` → updates repo (git pull) and installs dependencies
  - macOS
    - `scripts/haven_control_room_mac.command` → menu launcher
    - `scripts/run_haven_mac.command` → launches the GUI
    - `scripts/build_map_mac.command` → generates the map
    - `scripts/holo_net_update_mac.command` → update helper

  All scripts log to the `logs/` folder.

  ## Validation (Optional, Recommended)

  We ship `data.schema.json`. If you want to validate your data:

  ```powershell
  python - <<'PY'
  import json, pathlib
  from jsonschema import validate
  root = pathlib.Path('.')
  instance = json.loads((root/'data.json').read_text('utf-8'))
  schema = json.loads((root/'data.schema.json').read_text('utf-8'))
  validate(instance=instance, schema=schema)
  print('Schema validation: PASS')
  PY
  ```

  ## Tips & Troubleshooting

  - “ModuleNotFoundError: customtkinter” → run `pip install -r requirements.txt`
  - Photos not showing? Verify the relative path (e.g., `photos/your-image.png`).
  - New region not appearing? The entry app auto-creates region markers on save.
  - Want to rebuild without opening the browser? Use `--no-open`.
  - Windows SmartScreen or macOS Gatekeeper warning on first run? Use the right‑click → Open flow, or run via Terminal once. We can add code‑signed builds later.

  ## Logs

  - App logs are written to `logs/` with readable timestamps (e.g., `gui-YYYY-MM-DD.log`, `map-YYYY-MM-DD.log`).
  - Map regeneration output is captured to `logs/map-regen-YYYY-MM-DD_HHMMSS.log`.
  - If something goes wrong, share the latest files from `logs/`—they include both standard output and error details.
  - In the browser, click the "Download Logs" button (bottom-right) on any map page to save a text file with console output and errors captured during your session.

  ## Git Basics (Optional)

  Save your changes locally:

  ```powershell
  git add .
  git commit -m "Add new systems and regenerate map"
  ```

  If you want to push to your own GitHub repo, create one and set it as `origin`, then push the `Main` branch.

  ## Notes

  - Older scripts like `json_test.py` / `json_test_threejs.py` are deprecated. Use `system_entry_modern.py` for entry and `Beta_VH_Map.py` for maps.
  - Outputs (`dist/VH-Map.html`, `dist/system_<Region>.html`) are generated in the `dist/` folder.
  ---
  Enjoy exploring your galaxy!

**Beta VH Map** - Built for the Haven community to map No Man's Sky star systems with professional 3D visualization. Happy exploring! 🚀

---

## 📘 Data-Driven Architecture - Developer Reference

### Core Concept

**Everything is driven by your JSON data.** The visualization system reads object types, properties, and coordinates from `data.json` and renders them according to the `VISUAL_CONFIG` object in `Beta_VH_Map.py`.

### Benefits

✅ **No code changes needed** - just update JSON  
✅ **Any field displays automatically** - add custom properties anytime  
✅ **Missing data handled gracefully** - empty fields are simply skipped  
✅ **Extensible** - add new object types with config-only changes

### Minimal Required Fields

Every object needs:
```json
{
  "type": "system",    // Object type (determines visual style)
  "region": "Adam",    // Which region it belongs to
  "x": 1.0,           // Position
  "y": 2.0,
  "z": 3.0
}
```

### Data Flow

```
data.json
    ↓
load_systems() - Load and normalize
    ↓
prepare_region_data() - Calculate region centroids (galaxy view)
prepare_system_data() - Process all objects (system view)
    ↓
write_galaxy_and_system_views() - Generate HTML
    ↓
Template embeds JSON + VISUAL_CONFIG
    ↓
Three.js renders based on type → config mapping
```

### Info Panel Display Rules

Fields are shown in this order:

1. **Priority fields**: `type`, `id`, `region`, `system`
2. **All other fields** (dynamically, excluding coordinates)
3. **Special arrays**: `planets` list
4. **Links**: `photo` as clickable link

Fields automatically formatted:
- `base_location` → "Base Location"
- `space_station` → Not shown (rendered as separate object)
- Empty/null values → Skipped

### Troubleshooting

**Object not appearing?**
1. Check JSON has required fields: `type`, `region`, `x`, `y`, `z`
2. Verify `type` matches a key in `VISUAL_CONFIG`
3. Ensure view mode matches object type (regions in galaxy, others in system)

**Field not showing in info panel?**
- Special fields skipped: `x`, `y`, `z`, `moons`, `space_station`, `planets` (shown separately), `photo` (shown as link)
- Empty/null values are hidden automatically

**Visual appearance wrong?**
- Check `VISUAL_CONFIG` for your object's type in `Beta_VH_Map.py`
- Color is hex without `#` prefix: `0xFF6600` not `"#FF6600"`
- Size is in Three.js units (typical range: 0.3 to 2.0)

### Example: Complete System Entry

```json
{
  "name": "Oceanic Paradise",
  "type": "system",
  "region": "Adam",
  "x": -1.5,
  "y": 3.2,
  "z": 0.8,
  "water_coverage": "95%",
  "fauna": "Abundant",
  "space_station": {
    "name": "Trade Hub Omega",
    "x": -1.3,
    "y": 3.5,
    "z": 1.0,
    "services": "Trading, Repairs"
  },
  "moons": [
    {
      "name": "Tidally Locked Moon",
      "x": -1.8,
      "y": 3.0,
      "z": 0.6,
      "temperature": "Extreme"
    }
  ]
}
```

### Performance Tips

- **Large datasets** (>1000 objects): Consider splitting into more regions
- **Photo sizes**: Keep under 2MB each for fast loading
- **Grid visibility**: Toggle off for better FPS with many objects
- **Stats panel**: Use Controls → Stats to monitor performance

