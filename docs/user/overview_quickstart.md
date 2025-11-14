# Chapter 1: Overview & Quick Start

## What is Haven Control Room?

**Haven Control Room** is a complete star mapping toolkit designed specifically for No Man's Sky explorers who want to catalog, visualize, and share their discoveries. Unlike generic mapping tools, Haven is built from the ground up for the unique needs of NMS data collection and 3D visualization.

## Key Features

### 🛰️ Complete System Entry
- **Two-page wizard** for adding star systems with full metadata
- **Planet and moon support** with nested data structures
- **Photo integration** with automatic file management
- **Custom fields** for any additional data you want to track
- **Real-time validation** ensures data quality

### 🌌 Interactive 3D Galaxy Maps
- **Three.js-powered** visualizations that run in any modern browser
- **Touch-optimized** for mobile devices (iOS PWA)
- **Multiple view modes**: Galaxy overview and detailed system views
- **Data-driven rendering**: Any field in your JSON automatically displays
- **Offline capability** with embedded libraries

### 📱 Cross-Platform Experience
- **Desktop GUI** built with CustomTkinter (modern, responsive interface)
- **iOS Progressive Web App** that installs to home screen like a native app
- **Standalone executables** for Windows/macOS (no Python required)
- **Browser-based viewing** works on any device with WebGL

### 🔧 Professional Tooling
- **Schema validation** ensures data consistency
- **Automatic migrations** handle legacy data formats
- **Comprehensive logging** for troubleshooting
- **Backup system** prevents data loss
- **Theme customization** with multiple visual styles

## What Makes Haven Different?

### Data-Driven Architecture
Most mapping tools require you to work within their predefined structure. Haven reads **everything** from your JSON data:
- Add new object types without code changes
- Any JSON field automatically appears in info panels
- Visual styling adapts to your data structure
- No artificial limits on what you can track

### Built for No Man's Sky
- **Portal coordinates** as primary navigation system
- **System metadata** (sentinel levels, fauna/flora counts, materials)
- **Planet/moon hierarchies** with full detail tracking
- **Photo integration** for portal and base documentation
- **Region classification** for galactic organization

### Zero-Configuration Setup
- Single-folder deployment (copy anywhere, works immediately)
- No database setup or complex configuration
- Automatic dependency management
- Portable data format (JSON with schema validation)

## Quick Start (5 Minutes)

### Prerequisites
- **Python 3.10 or higher** (download from [python.org](https://www.python.org/downloads/))
- **Modern web browser** (Chrome, Firefox, Safari, or Edge)
- **4GB RAM** recommended for large datasets

### Step 1: Environment Setup
```bash
# Open terminal/command prompt in the Haven_Mdev folder
cd /path/to/Haven_Mdev

# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# or on Windows: .venv\Scripts\activate

# Install dependencies
pip install -r config/requirements.txt
```

### Step 2: Launch Control Room
```bash
# Windows
Haven Control Room.bat

# macOS
./haven_control_room_mac.command

# Linux / Manual
python src/control_room.py
```

### Step 3: Add Your First System
1. Click **"🛰️ Launch System Entry (Wizard)"**
2. **Page 1**: Enter system basics (name, region, coordinates)
3. **Page 2**: Add planets and moons with full details
4. Click **"💾 Finish & Save"**

### Step 4: Generate Your Map
1. Click **"🗺️ Generate Map"** (wait for completion)
2. Click **"🌐 Open Latest Map"** to view in browser

### Step 5: Explore & Customize
- **Touch/drag** to rotate the galaxy
- **Scroll/pinch** to zoom in and out
- **Click systems** to see detailed information
- **Add more systems** and regenerate maps as you explore

## Basic Workflow

```
Discover System → Portal Coordinates → Take Photo → Enter Data → Generate Map → Share Results
     ↓               ↓                    ↓            ↓            ↓            ↓
   Explore        Use Scanner          Screenshot   Wizard Form   Control Room  Export iOS
```

## Data Flow

1. **Collection**: Use System Entry Wizard to input discovery data
2. **Storage**: Data saved to `data/data.json` with automatic validation
3. **Processing**: Map generator reads JSON and creates 3D visualization
4. **Output**: HTML files in `dist/` folder, viewable in any browser
5. **Sharing**: Export as standalone apps or iOS PWA for others

## File Organization

Your data and outputs are organized for portability:

- **`data/data.json`**: Your complete star system database
- **`dist/VH-Map.html`**: Main galaxy visualization
- **`dist/system_*.html`**: Individual system detail views
- **`photos/`**: Screenshots and reference images
- **`logs/`**: Application logs for troubleshooting

## Getting Help

- **Control Room Logs**: Check the status panel for real-time feedback
- **Log Files**: Detailed logs in `logs/` folder
- **Documentation**: See other chapters for detailed guides
- **Data Validation**: Schema errors reported automatically

## Next Steps

Now that you understand the basics:
- [Chapter 2](installation_setup.md) covers detailed installation options
- [Chapter 3](control_room_guide.md) explains the Control Room interface
- [Chapter 4](system_entry_wizard_guide.md) provides complete data entry guide