# Chapter 5: 3D Galaxy Map Generation

## Overview

The Haven 3D Galaxy Map is an interactive Three.js-powered visualization that transforms your collected star system data into an explorable 3D space. The map runs entirely in your web browser and supports touch controls for mobile devices.

## Key Features

### Two View Modes
1. **Galaxy View** - Overview of all star systems and regions
   - Region centroids displayed as colored spheres
   - Systems grouped by region
   - Click any region to zoom into detailed system view

2. **System View** - Detailed view of individual systems
   - Individual star systems as nodes
   - Planet and moon orbits
   - System metadata display on hover
   - Click to view full system information

### Interactive Controls
- **Desktop**:
  - **Left-click + drag**: Rotate view
  - **Right-click + drag**: Pan camera
  - **Scroll wheel**: Zoom in/out
  - **Click system**: Show detailed info panel

- **Mobile/Touch**:
  - **Single finger swipe**: Rotate view
  - **Two finger pinch**: Zoom in/out
  - **Tap system**: Show detailed info panel
  - **Double-tap**: Reset view

### Visual Features
- **Color-coded regions**: Each region has a unique color
- **Coordinate grid**: Optional 3D grid for spatial reference
- **Glow effects**: Systems with special attributes glow
- **Info panels**: Detailed system data on selection
- **Animated transitions**: Smooth camera movements
- **Photo integration**: Portal/base photos display in info panels

## Generating Maps

### From Control Room

1. **Open Control Room**
   ```bash
   # macOS/Linux
   ./haven_control_room_mac.command

   # Windows
   Haven Control Room.bat
   ```

2. **Generate Map**
   - Click "🗺️ Generate Map" button
   - Wait for generation to complete (10-30 seconds)
   - Status updates appear in the log window

3. **Open in Browser**
   - Click "🌐 Open Latest Map" to view
   - Map opens in your default browser
   - Or manually open `dist/VH-Map.html`

### From Command Line

Generate map without opening:
```bash
python src/Beta_VH_Map.py --no-open
```

Generate with custom output file:
```bash
python src/Beta_VH_Map.py --out my_galaxy_map.html
```

View generated map:
```bash
# macOS
open dist/VH-Map.html

# Linux
xdg-open dist/VH-Map.html

# Windows
start dist/VH-Map.html
```

## Map Output Location

All generated maps are saved to the `dist/` folder:
- `VH-Map.html` - Main galaxy map
- `system_<name>.html` - Individual system views
- Maps are self-contained HTML files (no external dependencies)

## Understanding the Map Interface

### Top Bar Controls

**View Selector**
- Switch between Galaxy View and System View
- Dropdown menu to select specific systems

**Toggle Buttons**
- **Grid**: Show/hide coordinate grid
- **Labels**: Show/hide system name labels
- **Photos**: Enable/disable photo thumbnails

**Reset Button**
- Returns camera to default position
- Useful if you get lost navigating

### Info Panel

When you click a system, the info panel displays:
- System name and region
- Coordinates (x, y, z)
- Sentinel level
- Fauna and flora counts
- Available materials
- Base location (if any)
- Portal photo (if available)
- Planet list with details

### Logs Button

Download map generation logs for troubleshooting:
- Click "📄 Download Logs" in bottom-right
- Saves a text file with render information
- Useful for debugging visual issues

## Data-Driven Rendering

The map automatically displays any fields present in your `data.json`:

### Standard Fields
```json
{
  "name": "OOTLEFAR V",
  "x": 3,
  "y": 2,
  "z": 1,
  "region": "Adam",
  "fauna": "1",
  "flora": "None",
  "sentinel": "Low",
  "materials": "Magnetized ferrite, Gold, Cadmium",
  "base_location": "VH (+3.86, -129.37)",
  "photo": "photos/oot-portal.png"
}
```

### Custom Fields
Add any custom fields to your JSON and they'll appear in info panels:
```json
{
  "economy": "Trading",
  "conflict_level": "Peaceful",
  "discovered_by": "PlayerName",
  "notes": "Beautiful planet with blue grass"
}
```

All fields are automatically rendered in the system info display!

## Performance Optimization

### For Large Datasets

If you have 100+ systems, consider these optimizations:

1. **Region Filtering**
   - Use Galaxy View to explore one region at a time
   - Each region loads separately

2. **Browser Selection**
   - Chrome/Edge: Best WebGL performance
   - Firefox: Good compatibility
   - Safari: Works but may be slower on complex maps

3. **Quality Settings**
   - Modern devices: Full quality with glow effects
   - Older devices: Map automatically reduces quality
   - Mobile: Touch-optimized with simplified rendering

### Memory Management

The map uses client-side rendering, so performance depends on:
- **Number of systems**: <50 = excellent, 50-200 = good, >200 = may slow down
- **Photo count**: Photos are loaded on-demand
- **Browser**: Modern browsers (2020+) handle it best

## Sharing Maps

### Options for Sharing

1. **Send HTML File**
   - Email `dist/VH-Map.html` to friends
   - They open it in any browser
   - Works offline (no internet required)

2. **Host on Web Server**
   - Upload to GitHub Pages, Netlify, or any host
   - Share the URL
   - Updates automatically when you regenerate

3. **Include Photos**
   - Copy entire `dist/` and `photos/` folders
   - Maintain relative paths
   - Photos will display correctly

4. **iOS PWA** (recommended for mobile)
   - See Chapter 6: Exporting Applications
   - Full touch-optimized experience
   - Installs to home screen

## Troubleshooting

### Map Won't Generate

**Check logs folder:**
```bash
# View latest map generation log
cat logs/map-<date>.log
```

**Common causes:**
- Invalid JSON in `data/data.json`
- Missing coordinate values (x, y, z)
- Python dependencies not installed

**Solution:**
```bash
# Validate data format
python -m json.tool data/data.json

# Reinstall dependencies
pip install -r config/requirements.txt
```

### Map Looks Broken in Browser

**Symptoms**: Black screen, missing systems, console errors

**Fixes:**
1. **Clear browser cache**: Ctrl+F5 (Windows) or Cmd+Shift+R (macOS)
2. **Try different browser**: Chrome usually most reliable
3. **Check console**: F12 → Console tab for error messages
4. **Regenerate map**: May be corrupted, regenerate from Control Room

### Systems Not Appearing

**Checklist:**
- [ ] System has x, y, z coordinates in data.json
- [ ] Coordinates are valid numbers (not text)
- [ ] System is in the correct region
- [ ] Map generation completed without errors

**Verify data:**
```python
import json
with open('data/data.json') as f:
    data = json.load(f)
    for name, system in data.items():
        if name != '_meta':
            print(f"{name}: x={system.get('x')}, y={system.get('y')}, z={system.get('z')}")
```

### Photos Not Showing

**Requirements:**
- Photo path in JSON: `"photo": "photos/filename.png"`
- Photo file exists in `photos/` folder
- Relative path is correct

**Check paths:**
```bash
# List all photos
ls -1 photos/

# Verify JSON references match filenames
grep "photo" data/data.json
```

### Performance Issues

**Symptoms**: Slow rotation, laggy controls, browser freezes

**Solutions:**
1. **Reduce system count**: Archive old systems to separate JSON files
2. **Disable effects**: Toggle off grid and labels
3. **Close other browser tabs**: Free up memory
4. **Use desktop browser**: Mobile browsers have less power
5. **Update browser**: Ensure you're on latest version

## Advanced Customization

### Modifying Visual Appearance

The map template is embedded in `src/Beta_VH_Map.py`. Advanced users can customize:

**Colors and Styling** (lines ~199-300):
- Background color
- Grid color and opacity
- System node colors
- Glow effect intensity

**Camera Settings** (lines ~500-600):
- Default camera position
- Zoom limits
- Pan speed
- Rotation sensitivity

### Creating Multiple Map Views

Generate separate maps for different purposes:

```bash
# Full galaxy map
python src/Beta_VH_Map.py --out galaxy_full.html

# Region-specific map (edit data.json to filter first)
python src/Beta_VH_Map.py --out region_adam.html

# Development map (with debug info)
python src/Beta_VH_Map.py --out debug_map.html
```

## Integration with Other Tools

### Exporting Map Data

The map reads from `data/data.json`, which can be:
- Edited manually in any text editor
- Generated from spreadsheets (CSV → JSON)
- Updated via the System Entry Wizard
- Synced with external databases

### API Integration

Since maps are static HTML files, you can:
- Embed in websites via iframe
- Generate programmatically in scripts
- Batch-process multiple datasets
- Automate map updates with cron jobs

## Next Steps

- **Chapter 6**: Learn to create iOS PWA and standalone exports
- **Chapter 7**: Understand the data structure for advanced customization
- **Chapter 8**: Troubleshooting guide for common issues

## Quick Reference

### Essential Commands
```bash
# Generate map
python src/Beta_VH_Map.py

# Generate without opening
python src/Beta_VH_Map.py --no-open

# Custom output location
python src/Beta_VH_Map.py --out path/to/map.html
```

### Essential Controls
| Action | Desktop | Mobile |
|--------|---------|--------|
| Rotate view | Left-click drag | Swipe |
| Zoom | Scroll wheel | Pinch |
| Pan | Right-click drag | Two-finger drag |
| Select system | Click | Tap |
| Reset view | Reset button | Double-tap |
| Show info | Click system | Tap system |

### File Locations
- **Maps**: `dist/VH-Map.html`
- **Logs**: `logs/map-<date>.log`
- **Photos**: `photos/`
- **Data**: `data/data.json`
