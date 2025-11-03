# Haven Galaxy Project - Folder Structure

## Root Directory View
When you open the Haven_Mdev folder, you'll see:

```
📁 Haven_Mdev/
├── 🚀 Haven Control Room.bat          (Windows launcher - DOUBLE CLICK THIS)
├── 🚀 haven_control_room_mac.command  (macOS launcher - DOUBLE CLICK THIS)
├── 📁 config/                         (Configuration files)
├── 📁 data/                           (Your system data)
├── 📁 dist/                           (Generated HTML maps)
├── 📁 docs/                           (Documentation)
├── 📁 logs/                           (Application logs)
├── 📁 photos/                         (System screenshots)
├── 📁 scripts/                        (Helper scripts)
└── 📁 src/                            (Python source code)
```

## Folder Purposes

### 🚀 **Control Room Launchers** (Root)
- **Haven Control Room.bat** - Windows: Menu to open GUI, build map, or update
- **haven_control_room_mac.command** - macOS: Same menu for Mac users

### 📁 **config/**
Configuration and setup files:
- requirements.txt - Python dependencies
- .gitignore - Git ignore rules
- .vscode/ - VS Code settings

### 📁 **data/**
Your star system data:
- data.json - All your systems, regions, moons, stations
- data.schema.json - Validation schema

### 📁 **dist/**
Generated output (auto-created):
- VH-Map.html - Galaxy overview
- system_*.html - Individual system views

### 📁 **docs/**
Documentation:
- README.md - Complete usage guide

### 📁 **logs/**
Application logs (auto-created):
- gui-*.log - GUI application logs
- map-*.log - Map generation logs
- map-regen-*.log - Map regeneration logs

### 📁 **photos/**
Your system screenshots:
- Store portal/system photos here
- Reference them in data.json

### 📁 **scripts/**
Individual launcher scripts:
- Galactic Archive Terminal - Opens data entry GUI
- Atlas Array - Generates 3D maps
- Holo-Net Update - Updates repo and dependencies
- (Both Windows .bat and macOS .command versions)

### 📁 **src/**
Python source code:
- Beta_VH_Map.py - 3D map generator
- system_entry_modern.py - Data entry GUI

## Quick Start

1. **First time?** Double-click the Control Room launcher (Windows or Mac version)
2. **Choose option 1** to open the data entry GUI
3. **Add your systems** - fill in coordinates, materials, etc.
4. **Choose option 2** to generate the 3D map
5. **Open dist/VH-Map.html** in your browser to explore!

---

**The Control Room is your command center** - all functionality accessible from one simple menu.
