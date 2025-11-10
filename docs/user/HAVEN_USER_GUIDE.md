# Haven Control Room - User Guide

**Version:** 1.0  
**Last Updated:** November 5, 2025

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Main Features](#main-features)
3. [Creating & Editing Systems](#creating--editing-systems)
4. [Generating Maps](#generating-maps)
5. [Exporting Applications](#exporting-applications)
6. [System Test Suite](#system-test-suite)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

1. **Run the application:** Double-click `HavenControlRoom.exe`
2. **Wait for startup:** The app may take 10-15 seconds to initialize
3. **Choose your action** from the buttons in the left sidebar

That's it! The app is designed to be intuitive with clear buttons for each action.

---

## ✨ Main Features

### 📊 System Management
**Manage your star systems database**

- **Add Systems:** Create new star systems with coordinates, planets, and moons
- **Edit Systems:** Modify existing systems anytime
- **View Database:** See all systems in your current data source
- **Search:** Find systems by name or attributes

### 🗺️ Map Generation
**Create beautiful 3D galaxy maps**

- **Generate Galaxy Map:** Creates an interactive 3D visualization of all your systems
- **System Views:** Individual 3D views for each system showing planets and orbital mechanics
- **Real-time Updates:** Map updates automatically when you modify systems
- **Export as HTML:** Share maps by sending the HTML file to others

### 📦 Application Export
**Build standalone applications**

- **Windows EXE:** Create a standalone Windows executable your friends can run
- **macOS App:** Generate a macOS application bundle
- **Automatic Packaging:** Includes all necessary data and resources

### 🧪 System Testing
**Validate your data and system integrity**

- **Validation Tests:** Check data structure and schema compliance
- **Security Tests:** Verify input sanitization and protection against attacks
- **Unit Tests:** Test individual system components
- **Stress Tests:** Performance testing with large datasets (100K+ systems)
- **Run Multiple Tests:** Select and run multiple tests simultaneously

### 📁 File Management
**Easy access to your data**

- **Data Folder:** Quick access to your systems database
- **Logs Folder:** View application logs for debugging
- **Documentation:** Open built-in user guides and technical docs

---

## 🌟 Creating & Editing Systems

### Starting the Wizard
Click **"✏️ System Entry Wizard"** to add or edit systems.

### Page 1: System Information
Enter basic system details:
- **System Name:** Unique identifier (e.g., "Alpha Centauri")
- **Region:** Which galactic region (e.g., "Outer Rim", "Core")
- **Coordinates:** X, Y, Z positions in space
- **Attributes:** Special notes about the system

### Page 2: Planets & Moons
Add celestial bodies:
- **➕ Add Planet:** Creates a new planet
- **Edit/Remove:** Modify or delete planets
- **Add Moons:** Each planet can have multiple moons with orbital parameters
- **Planet Details:**
  - Name, sentinel level, flora/fauna presence
  - Materials available
  - Base location coordinates
  - Photos and notes

### Advanced Options
- **Space Station:** Add a trading station to the system
- **Toggle Data Source:** Switch between production and test data during editing

### Saving
When finished, click **"💾 Save System"**. The wizard will validate your data and create a backup.

---

## 🗺️ Generating Maps

### Quick Generation
1. Click **"🗺️ Generate Galaxy Map"**
2. Wait for processing (usually 10-30 seconds)
3. The map opens automatically in your browser

### What You Can Do in the Map

**Galaxy View:**
- View all systems as dots in 3D space
- Click systems for details
- Use mouse to rotate/zoom the view
- Toggle grid and labels

**System View:**
- Click a system name to see its detailed 3D view
- See planets orbiting the star
- View moons orbiting planets with realistic orbital mechanics
- Read system and celestial body information

**Controls:**
- **Drag Mouse:** Rotate the view
- **Scroll Mouse:** Zoom in/out
- **Buttons:** Toggle grid, labels, auto-rotation, screenshot
- **Settings (⚙️):** Show/hide UI elements

### Output
The map is saved as an HTML file that you can:
- Share via email or cloud storage
- Open in any web browser
- View offline (no internet required)

---

## 📦 Exporting Applications

### Create a Windows EXE
1. Click **"📦 Export App (EXE/.app)"**
2. Select "Windows" from the dropdown
3. Choose output folder
4. Click "Export"
5. Wait for the build to complete (3-5 minutes)

**Output:**
- `HavenControlRoom.exe` - Standalone executable
- `HavenControlRoom_Windows_[date].zip` - Packaged version for sharing

**Use:** Your friends can run this EXE without installing Python or anything else.

### Create a macOS App
1. Click **"📦 Export App (EXE/.app)"**
2. Select "macOS" from the dropdown
3. Choose output folder
4. Click "Export"

**Note:** Building on Windows creates a "Build Kit" for macOS. You'll need macOS to complete the build.

---

## 🧪 System Test Suite

### Running Tests
1. Click **"🧪 System Test"** button
2. **Select Tests:**
   - "Select All" - Run every test
   - "Clear All" - Deselect all
   - "Validation Only" - Schema and data structure tests
   - "Security Only" - Input validation and attack prevention tests
   - Or check individual tests

3. Click **"Run Tests"**
4. View results with pass/fail status

### Test Categories

**Validation Tests (✅)**
- Check data structure validity
- Verify coordinate ranges
- Ensure required fields are present
- Validate schema compliance

**Unit Tests (🔬)**
- Test individual components
- Verify calculations
- Check data transformations

**Security Tests (🔒)**
- Test XSS attack prevention
- SQL injection prevention
- Path traversal prevention
- Input sanitization

**Stress Tests (⚡)**
- Performance with 100K systems
- Memory optimization
- Large dataset handling

---

## 🔧 Advanced Features

### Backend Selection
The app automatically uses the best storage backend:
- **Small datasets (< 1,000 systems):** JSON file storage
- **Large datasets (> 1,000 systems):** SQLite database

You can view which backend is active in the System Entry Wizard.

### Data Synchronization
- Systems are automatically synced between storage formats
- Backups are created before major operations
- File locks prevent concurrent access issues

### Themes
The app includes professional dark theme with customizable appearance (advanced settings).

### Logging
Application logs are saved for troubleshooting:
- Located in the `logs/` folder
- Automatically rotated to manage disk space
- View errors in `error_logs/` subfolder

---

## ❓ Troubleshooting

### Map Won't Generate
**Solution:** 
- Ensure you have systems in your database
- Check the Data Folder to verify data.json exists
- Check Logs Folder for error messages
- Try regenerating

### Wizard Won't Save
**Possible Issues:**
- Invalid coordinates (must be numbers)
- Missing required fields
- Duplicate system name
- Check error dialog for specific message

### Export Failed
**Solution:**
- Ensure output folder has write permissions
- Close any running Haven applications
- Check available disk space (need ~500MB for build)
- View logs for specific errors

### Slow Performance
**Solution:**
- Close other applications to free RAM
- Reduce system count in map generation
- Use database backend for 1,000+ systems
- Try restarting the application

### Can't Open Data Files
**Solution:**
- Right-click the folder button and "Open as administrator"
- Ensure Windows Explorer is not locked
- Try accessing from File Explorer directly

---

## � Need More Help?

- **Documentation Folder:** Click "📖 Documentation" for detailed guides
- **Log Files:** Check logs for error details
- **System Test Suite:** Run tests to validate your setup
- **Built-in Hints:** Hover over UI elements for tooltips

---

## 🎯 Common Workflows

### Workflow 1: Create Your First Galaxy
1. Open Haven Control Room
2. Click "✏️ System Entry Wizard"
3. Add 3-5 star systems with different coordinates
4. Add planets and moons to a few systems
5. Click "🗺️ Generate Galaxy Map"
6. Explore your galaxy in the browser!

### Workflow 2: Share Your Galaxy with Friends
1. Generate your galaxy map
2. Export it as Windows EXE (sends them the app)
3. Or share the `dist/VH-Map.html` file (just the map)

### Workflow 3: Backup Your Data
1. Click "📁 Data Folder"
2. Copy the entire folder to an external drive or cloud storage
3. Your data (data.json or haven.db) is now backed up

### Workflow 4: Test Your System
1. Click "🧪 System Test"
2. Select "Select All" or specific test categories
3. Run tests to ensure everything is working
4. Fix any issues if tests fail

---

## 💡 Tips & Tricks

- ✨ **Unique Names:** Give each system a unique, memorable name
- 📍 **Realistic Coordinates:** Use reasonable X/Y/Z values for better map layout
- 🌍 **Add Details:** More planet details make the map more interesting
- 📸 **Photos:** Include planet photos to make the galaxy come alive
- 🔄 **Regular Backups:** Use the Data Folder to backup regularly
- 🧪 **Validate Often:** Run tests during development to catch issues early

---

## ⚙️ System Requirements

- **Windows 10 or higher** (for EXE version)
- **At least 2 GB RAM** (more for 100K+ systems)
- **500 MB disk space** (for app + data)
- **Modern web browser** (Chrome, Edge, Firefox for map viewing)

---

**Enjoy creating your galactic universe!** 🚀✨
- Map automatically opens in your browser
- **Browser Controls:**
  - **Mouse:** Click & drag to rotate view
  - **Scroll:** Zoom in/out
  - **Click System:** View detailed system page with planets/moons
  - **Settings (⚙️):** Toggle UI elements on/off

**Map Features:**
- ✨ Galaxy Overview: See all systems as 3D plot
- 🪐 System View: Click any system to see detailed solar layout
- 🌙 Moon Orbits: Moons orbit planets with realistic mechanics
- 📍 Coordinates: Exact X, Y, Z positions displayed
- 📋 Legend: Color-coded by region/type
- 🎯 Info Panel: Click objects for detailed information
- 📸 Screenshot: Capture map views

**Output:** Map saved to `dist/VH-Map.html` (opens automatically)

---

### 📦 **Export App** - Package for Distribution

**Purpose:** Create standalone Windows or Mac versions you can share.

**How to Use:**
- Click **"📦 Export App (EXE/.app)"**
- Choose platform:
  - **Windows:** Creates .exe file
  - **macOS:** Creates .app bundle (requires Mac to build)
- Select output folder
- Click **"Export"** - wait for build to complete
- **Windows:** Receives .exe and optional .zip with instructions
- **macOS:** Receives build kit with instructions

**Result:** Standalone application others can run without Python!

---

### 🧪 **System Test** - Run Quality Checks

**Purpose:** Verify all features are working correctly.

**How to Use:**
- Click **"🧪 System Test"**
- Interactive menu appears with test categories:
  - **Validation Tests** ✅ - Data structure checks
  - **Unit Tests** 🔬 - Core functionality
  - **Security Tests** 🔒 - Input validation & attack prevention
  - **Stress Tests** ⚡ - Large dataset performance
- **Quick Selection:**
  - "Select All" - Run everything (comprehensive)
  - "Clear All" - Deselect all
  - "Validation Only" - Fast data checks only
  - "Security Only" - Verify input safety
- Click **"Run Tests"** to execute
- **Results Show:**
  - ✅ Passed tests in green
  - ❌ Failed tests in red with error details
  - Summary: "X passed, Y failed"

**When to Use:** Before shipping, after major changes, or to verify integrity

---

### 📁 **File Management**

**Available Folders:**

| Button | Purpose |
|--------|---------|
| **📁 Data Folder** | Contains all saved system data (data.json) |
| **🧭 Logs Folder** | Debug logs and error reports |
| **📖 Documentation** | Help files and guides |

**How to Use:** Click any folder button to open it in Windows Explorer

---

### 🔧 **Advanced Tools** (Development Only)

**These appear only when running from source code, not the EXE:**

| Button | Purpose |
|--------|---------|
| **🔧 Update Dependencies** | Install/upgrade Python packages |
| **📦 Export App (EXE/.app)** | Build standalone applications |

---

## Data Storage

### Where Your Data Lives

```
Haven_Mdev/
├── data/
│   ├── data.json          ← All system/planet/moon data
│   ├── haven.db           ← Database backup
│   └── data.json.bak      ← Automatic backups
├── dist/
│   └── VH-Map.html        ← Generated 3D map
└── logs/
    └── control-room-*.log ← Activity logs
```

### Backups

- **Automatic:** data.json backed up to data.json.bak before each save
- **Manual:** Copy data/ folder to USB/cloud for safety
- **Recovery:** Restore data.json.bak if needed

---

## System Information Display

**Top-Right Status Panel Shows:**
- 📡 **System Status:** Current operation status
- 🔄 **Data Source:** Production (data.json) or Testing
- 📊 **Real-time Logs:** Live activity feed

**Toggle Data Source:**
- Switch between Production and Testing data
- Useful for trying features without affecting real data

---

## Common Workflows

### 🌟 Workflow 1: Add a New System

1. Click **"🛸 System Entry Wizard"**
2. Leave "New System" selected
3. Enter system name, region, coordinates
4. Click **Next** → Add planets (optional)
5. Click **Save System**
6. ✅ System saved to database

### 🗺️ Workflow 2: View Your Galaxy Map

1. Click **"🗺️ Generate Map"**
2. Wait 5-10 seconds for generation
3. Map opens in browser automatically
4. Click systems to zoom in and see planets
5. Use mouse to rotate/explore

### 📤 Workflow 3: Share Your App

1. Click **"📦 Export App (EXE/.app)"**
2. Choose Windows or macOS
3. Select output folder
4. Click Export
5. Wait 2-3 minutes for build
6. Send .exe/.zip file to others
7. They double-click to run!

### ✅ Workflow 4: Verify Everything Works

1. Click **"🧪 System Test"**
2. Click "Select All"
3. Click "Run Tests"
4. Review results (should mostly pass)
5. Green ✅ = good, Red ❌ = issue found

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Escape | Close dialogs/windows |
| Enter | Confirm/save in dialogs |
| Alt+F4 | Close application |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **Map won't generate** | Click "🗺️ Generate Map" again; check logs folder |
| **Wizard won't save** | Verify all required fields (✱) are filled |
| **EXE won't start** | Try "Run as Administrator" |
| **No planets showing** | Regenerate map after adding planets |
| **Map is slow** | Reduce system count or zoom out |

---

## Tips & Tricks

✨ **Pro Tips:**

1. **Save Regularly** - Data persists between sessions
2. **Organize Regions** - Use consistent region names for grouping
3. **Take Screenshots** - Use map's 📸 button to capture exploration
4. **Monitor Logs** - Check logs folder if something goes wrong
5. **Backup Data** - Copy data/ folder monthly to external drive
6. **Test Before Share** - Run System Test before exporting

---

## Features by Category

### 🎨 **Data Entry**
- Multi-step wizard for systems
- Batch planet/moon addition
- Auto-save drafts
- Duplicate detection

### 🖥️ **Visualization**
- 3D galaxy map with Three.js
- Real-time orbit rendering
- Interactive system views
- Screenshot capture

### 🔒 **Data Protection**
- Automatic backups (.bak files)
- File locking (no corruption)
- Data validation
- Security testing

### 📊 **Analytics**
- System count tracking
- Region statistics
- Performance monitoring
- Debug logging

### 🚀 **Distribution**
- One-click EXE building
- Mac app support
- Cross-platform compatible
- No Python required for end users

---

## File Formats

### data.json Structure
```json
{
  "System Name": {
    "name": "...",
    "region": "...",
    "x": 1.0, "y": 2.0, "z": 3.0,
    "planets": [
      {
        "name": "Planet Name",
        "fauna": "...",
        "flora": "...",
        "moons": [...]
      }
    ]
  }
}
```

### Map Output
- **File:** `dist/VH-Map.html`
- **Format:** Interactive HTML/JavaScript
- **Size:** 2-5 MB typically
- **Browser:** Any modern browser (Chrome, Firefox, Edge, Safari)

---

## Getting Help

📖 **Documentation:**
- Check `docs/` folder for detailed guides
- Read error messages in log window (they're helpful!)

🐛 **Found a Bug?**
- Check logs folder for error details
- Run System Test to identify issues
- Take screenshot of error

💾 **Data Questions?**
- All data saved to `data/data.json`
- Backups in `data/data.json.bak`
- Database copy in `data/haven.db`

---

## Keyboard Shortcuts (Advanced)

When running from source code:

```bash
# Launch System Entry Wizard directly
python src/system_entry_wizard.py

# Generate map without opening browser
python src/Beta_VH_Map.py --no-open

# Run all tests
python -m pytest tests/ -v
```

---

## Summary

Haven Control Room is your **all-in-one galaxy management system**:

- ✅ **Add Systems** - Multi-step wizard with planet/moon support
- ✅ **View Galaxy** - Interactive 3D maps with orbital mechanics
- ✅ **Export Apps** - Share standalone Windows/Mac versions
- ✅ **Test Quality** - 25+ automated tests verify everything
- ✅ **Manage Data** - Safe storage with automatic backups

**Start exploring!** 🚀

---

## Version Info

- **Application:** Haven Control Room v1.0
- **Built with:** Python 3.13 + CustomTkinter + Three.js
- **Platform:** Windows & Mac
- **Release Date:** November 2025

