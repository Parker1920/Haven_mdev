# Haven Control Room User Edition - Quick Start Guide

## What You Have

✅ **Fully Functional User Edition EXE**
- Location: `dist/HavenControlRoom_User/HavenControlRoom.exe`
- Size: 41.2 MB (includes all dependencies)
- Status: Tested and working

## How to Use

### 1. **Launch the Application**
```
Double-click: HavenControlRoom.exe
```

### 2. **You'll See Three Buttons**

| Button | Function |
|--------|----------|
| **System Entry Wizard** | Add/edit/remove systems in the galaxy |
| **Generate Map** | Create a 3D map from your system data |
| **Open Latest Map** | View the map in your web browser |

### 3. **Add a System (Wizard)**
- Click "System Entry Wizard"
- Enter system name, position (x, y, z), and other details
- Click "Save System"
- Data automatically saves to `files/data.json`

### 4. **Generate a 3D Map**
- Click "Generate Map"
- App processes your systems
- Creates `VH-Map.html` in `files/maps/`

### 5. **View Your Map**
- Click "Open Latest Map"
- Map opens in your default web browser
- **Rotate**: Click and drag with mouse
- **Zoom**: Mouse wheel or pinch
- **Pan**: Right-click and drag

## File Structure

```
HavenControlRoom_User/
├── HavenControlRoom.exe ← Click to launch
└── files/
    ├── data.json ← Your system data (automatic)
    ├── data.json.bak ← Auto backup (automatic)
    ├── maps/
    │   ├── VH-Map.html ← Current map (regenerate each time)
    │   └── static/ ← Map resources (CSS, JavaScript)
    ├── logs/ ← Operation logs
    ├── photos/ ← Your custom images
    └── backups/ ← Backup files
```

## Key Features

✅ **Standalone** - Works completely offline, no internet required  
✅ **Portable** - Move the entire folder anywhere, it still works  
✅ **Safe** - Automatic backups before each save  
✅ **Fast** - Map generates in under 1 second  
✅ **Interactive** - 3D visualization with full mouse controls  

## What's Currently In the Data

**3 Sample Systems:**
1. **APOLLO PRIME** - Position: (0.5, -0.8, 1.2)
2. **ARTEMIS** - Position: (-1.8, 1.1, 2.4)
3. **ATLAS** - Position: (varies)

You can modify these or add new ones using the wizard.

## Verified Working ✅

- [x] EXE launches cleanly
- [x] Wizard opens and saves data
- [x] Map generates with system data
- [x] 3D visualization renders
- [x] All 3 sample systems display correctly
- [x] Data persists between sessions
- [x] Backups created automatically

## If You Need to Reset

**To restore the sample data:**
1. Delete `files/data.json`
2. Rename `files/data.json.bak` to `files/data.json`
3. Relaunch the app

## Technical Details

- **Python Version**: 3.13.9 (embedded)
- **UI Framework**: CustomTkinter
- **3D Rendering**: Three.js
- **Data Format**: JSON
- **Browser Support**: Chrome, Edge, Firefox (modern versions)

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Map doesn't load in browser | Ensure JavaScript is enabled in browser |
| 3D doesn't render | Use Chrome/Edge/Firefox, not Internet Explorer |
| Can't save systems | Check that `files/` folder is writable |
| Lost data | Check `files/data.json.bak` for previous version |

## Support Notes

- All features are self-contained within the EXE
- No external servers or internet connection needed
- Data stored locally in JSON format
- Completely portable - copy the entire folder anywhere

---

**Version**: 1.0 (November 5, 2025)  
**Status**: ✅ Production Ready
