# Chapter 6: Exporting Applications

## Overview

Haven Control Room can create standalone applications for users who don't have Python installed. Export options include Windows executables, macOS app bundles, and iOS Progressive Web Apps (PWAs).

## Export Methods

### Quick Summary

| Platform | Output | Python Required | File Size | Installation |
|----------|--------|----------------|-----------|--------------|
| **Windows** | `.exe` file | No | ~35 MB | Double-click |
| **macOS** | `.app` bundle | No | ~40 MB | Drag to Applications |
| **iOS/iPad** | `.html` PWA | No | ~50-500 KB | Add to Home Screen |

All exports are **fully portable** and work offline once installed.

## Windows Executable (.exe)

### Creating a Windows EXE

1. **Open Control Room** (from source, not from an existing EXE)
   ```bash
   python src/control_room.py
   ```

2. **Click "📦 Export App (EXE/.app)"**
   - Select **Windows** from platform dropdown
   - Choose output folder (e.g., `Desktop/Haven_Exports`)
   - Click **Export**

3. **Wait for build** (2-5 minutes)
   - Progress shows in Control Room log window
   - PyInstaller bundles Python + all dependencies
   - Creates `HavenControlRoom.exe`

4. **Output files:**
   ```
   Haven_Exports/
   ├── HavenControlRoom.exe           # Standalone executable
   └── HavenControlRoom_Windows_<timestamp>.zip  # Distribution package
   ```

### Distributing the Windows EXE

**For yourself:**
- Copy `HavenControlRoom.exe` anywhere
- Double-click to run
- Creates `data/`, `logs/`, and `dist/` folders next to itself

**For friends/users:**
1. Send them `HavenControlRoom_Windows_<timestamp>.zip`
2. They extract the ZIP
3. Double-click `HavenControlRoom.exe`
4. That's it - no Python needed!

### Windows SmartScreen Warning

Windows may show a "Unknown Publisher" warning on first run:

**To bypass:**
1. Click "More info"
2. Click "Run anyway"

**Why this happens:**
- Windows requires code signing certificates ($$$)
- Your EXE isn't signed
- This is normal for open-source software

**Prevention (advanced):**
- Purchase a code signing certificate
- Sign the EXE with `signtool`
- Or distribute as ZIP and let users trust you

### Technical Details

**Build process:**
```bash
# What happens under the hood:
pyinstaller --onefile --windowed \
    --name HavenControlRoom \
    --hidden-import system_entry_wizard \
    --hidden-import Beta_VH_Map \
    src/control_room.py
```

**Included:**
- Python 3.x runtime
- All dependencies (customtkinter, pandas, etc.)
- Source code (compiled)
- Icons and themes

**NOT included:**
- User data (`data/` created at runtime)
- Logs (`logs/` created at runtime)
- Generated maps (`dist/` created at runtime)

## macOS Application (.app)

### Creating a macOS App

#### On macOS (Direct Build)

1. **Open Control Room** (from source)
   ```bash
   python src/control_room.py
   ```

2. **Export App**
   - Click "📦 Export App (EXE/.app)"
   - Select **macOS**
   - Choose output folder
   - Click **Export**

3. **Wait for build** (3-7 minutes)
   - Creates `HavenControlRoom.app` bundle

4. **Install:**
   ```bash
   # Move to Applications folder
   cp -R HavenControlRoom.app /Applications/
   ```

#### On Windows/Linux (Build Kit)

If you're not on macOS, Haven creates a **Mac Build Kit**:

1. **Export as macOS** from Control Room
   - Choose macOS platform
   - Gets a ZIP file: `HavenControlRoom_Mac_BuildKit_<timestamp>.zip`

2. **Transfer to Mac**
   - Email, USB, or cloud transfer the ZIP to a Mac

3. **On Mac, extract and build:**
   ```bash
   unzip HavenControlRoom_Mac_BuildKit_*.zip
   cd Haven_Mac_BuildKit

   # Install PyInstaller
   python3 -m pip install pyinstaller

   # Build the app
   python3 -m PyInstaller --noconfirm --clean --windowed --onefile \
       --name HavenControlRoom \
       --hidden-import system_entry_wizard \
       --hidden-import Beta_VH_Map \
       src/control_room.py
   ```

4. **Output:** `dist/HavenControlRoom.app`

### Distributing macOS Apps

**For yourself:**
- Drag `HavenControlRoom.app` to Applications
- Launch from Launchpad or Spotlight

**For others:**
1. **Create DMG (optional but professional):**
   ```bash
   # Using create-dmg (install with homebrew)
   brew install create-dmg
   create-dmg --volname "Haven Control Room" \
              --window-size 600 400 \
              --app-drop-link 400 100 \
              HavenControlRoom.dmg \
              HavenControlRoom.app
   ```

2. **Or just ZIP it:**
   ```bash
   zip -r HavenControlRoom_macOS.zip HavenControlRoom.app
   ```

### macOS Gatekeeper

macOS may show "unidentified developer" warning:

**To bypass:**
1. Right-click `HavenControlRoom.app`
2. Select "Open"
3. Click "Open" in dialog
4. Or: `xattr -cr HavenControlRoom.app`

**Why this happens:**
- Apple requires developer certificates ($99/year)
- Same as Windows SmartScreen
- Normal for open-source apps

## iOS Progressive Web App (PWA)

### What is an iOS PWA?

A Progressive Web App (PWA) is a special HTML file that:
- **Installs to iOS home screen** like a native app
- **Works completely offline** after first load
- **Includes all data and code** in one HTML file
- **Touch-optimized** with mobile-specific controls

**Perfect for:**
- Field use (exploring in-game)
- Sharing with iOS-only users
- Lightweight distribution (50KB vs 35MB EXE)

### Quick iOS Export

1. **Open Control Room**
2. **Click "📱 Generate iOS PWA"** (quick action button)
3. **Output:** `dist/Haven_iOS_PWA_<timestamp>.zip`

### Advanced iOS Export (with options)

1. **Click "📦 Export App (EXE/.app)"**
2. **Select iOS or iOS (Offline)**:
   - **iOS**: Requires internet on first load (downloads Three.js)
   - **iOS (Offline)**: Fully offline (embeds Three.js ~500KB)

3. **Choose output folder**
4. **Click Export**

5. **Output bundle:**
   ```
   Haven_iOS_PWA_<timestamp>.zip
   ├── Haven_Galaxy_iOS.html          # The PWA (50KB or 500KB)
   ├── iOS_INSTALLATION_GUIDE.txt      # Step-by-step instructions
   └── README.txt                       # Quick start
   ```

### Installing on iPhone/iPad

#### Method 1: Email (Easiest)

1. **Email yourself** `Haven_Galaxy_iOS.html`
2. **On iOS:** Open email, tap attachment
3. **Opens in Safari** (not Chrome!)
4. **Tap Share button** (square with arrow)
5. **Scroll and tap "Add to Home Screen"**
6. **Name it** (e.g., "Haven Galaxy")
7. **Tap "Add"**
8. **Launch** from home screen!

#### Method 2: AirDrop

1. **On Mac:** Right-click `Haven_Galaxy_iOS.html`
2. **Select "Share" → "AirDrop"**
3. **Select your iPhone/iPad**
4. **On iOS:** File appears in Files app
5. **Tap to open in Safari**
6. **Follow steps 4-8 above**

#### Method 3: iCloud Drive

1. **Save to iCloud Drive** from Mac/PC
2. **On iOS:** Open Files app
3. **Navigate to file**
4. **Tap to open**
5. **Follow Safari steps above**

### iOS PWA Features

Once installed, the PWA includes:

**📱 Full Data Entry**
- Add/edit/delete star systems
- Planet and moon support
- All fields from desktop version
- Real-time validation

**🗺️ 3D Map Viewer**
- Touch-optimized controls (pinch, swipe, tap)
- Galaxy view and system view
- Smooth animations
- Photo display

**💾 Local Storage**
- All data saved on device
- Survives app closes and restarts
- Independent from desktop data

**📤 Import/Export**
- Export to JSON file
- Import JSON from email/cloud
- Backup and sync with desktop

**✈️ Offline Mode**
- Works with no internet (after first load)
- iOS (Offline) version needs NO internet ever

### Syncing iOS PWA with Desktop

**Desktop → iOS:**
1. Export from desktop: `data/data.json`
2. Email to yourself
3. In iOS PWA: Tap "Import JSON"
4. Select emailed file

**iOS → Desktop:**
1. In iOS PWA: Tap "Export JSON"
2. Email file to yourself
3. On desktop: Save as `data/data.json`
4. Regenerate map

### iOS PWA Troubleshooting

**Problem: Won't install**
- Must use Safari (not Chrome/Firefox)
- Some enterprise iOS configs disable PWAs
- Try different iOS device

**Problem: Data not saving**
- Check Safari settings: Settings → Safari → Advanced
- Enable JavaScript
- Allow website data

**Problem: Map won't load**
- Standard version needs internet on first load
- Use "iOS (Offline)" export for true offline
- Clear Safari cache and retry

**Problem: Controls laggy**
- Close other Safari tabs
- Restart iPhone/iPad
- Reduce complexity (fewer systems)

## Embedded Three.js for Full Offline

### Why Embed Three.js?

Standard iOS PWA downloads Three.js (~200KB) from CDN on first use:
- ✅ Smaller initial file size (50KB)
- ❌ Requires internet on first launch

Embedded iOS PWA includes Three.js in the HTML:
- ✅ Zero internet dependency
- ✅ Works in airplane mode
- ❌ Larger file size (500KB)

### How to Enable Full Offline

1. **Download Three.js r128**:
   ```bash
   # From CDN
   curl -o config/vendor/three.r128.min.js \
   https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js
   ```

2. **Create vendor folder if needed**:
   ```bash
   mkdir -p config/vendor
   ```

3. **Export iOS (Offline)**:
   - Select "iOS (Offline)" in Export dialog
   - Haven auto-detects `three.r128.min.js`
   - Embeds it in HTML

4. **Verify**:
   - Check file size: ~500KB = embedded ✓
   - Check file size: ~50KB = not embedded, will use CDN

## Cleaning Up Old Executables

Haven automatically archives old EXE/app files during export:
- Previous builds moved to `Archive-Dump/dist/`
- Prevents confusion about which version is current
- Keeps project folder tidy

**Manual cleanup:**
```bash
# Remove all old executables
find . -name "*.exe" -not -path "*/Archive-Dump/*" -delete
find . -name "*.app" -not -path "*/Archive-Dump/*" -delete
```

## Distribution Best Practices

### For Windows Users

**Recommended:** Create a release package
```
Haven_Control_Room_v1.0/
├── HavenControlRoom.exe
├── README.txt (simple instructions)
└── example_data.json (optional sample data)
```

**ZIP it:**
```bash
zip -r Haven_Control_Room_v1.0.zip Haven_Control_Room_v1.0/
```

### For macOS Users

**Recommended:** Create DMG
```bash
create-dmg --volname "Haven Control Room" \
           --app-drop-link 400 100 \
           HavenControlRoom.dmg \
           HavenControlRoom.app
```

### For iOS Users

**Recommended:** Email HTML + Instructions
```
Subject: Haven Galaxy - Star Map App for iOS

Attached is the Haven Galaxy app for your iPhone/iPad.

Installation (30 seconds):
1. Open this email on your iPhone/iPad
2. Tap the HTML file attachment
3. When Safari opens, tap Share
4. Tap "Add to Home Screen"
5. Launch from home screen!

All your data is stored locally and works offline.
```

## Advanced: Custom Branding

### Custom Icons

**Windows:**
```bash
# Create .ico file (256x256 recommended)
# Place in config/icons/custom.ico

# Edit control_room.py export function:
icon = config_dir() / 'icons' / 'custom.ico'
```

**macOS:**
```bash
# Create .icns file (512x512 recommended)
# Place in config/icons/custom.icns

# Edit control_room.py export function:
icon = config_dir() / 'icons' / 'custom.icns'
```

**iOS PWA:**
```html
<!-- Edit generate_ios_pwa.py template -->
<link rel="apple-touch-icon" href="data:image/png;base64,...">
```

### Custom App Name

Edit export functions in `src/control_room.py`:

```python
# Line ~365 (Windows export)
name = 'YourAppName'

# Line ~478 (macOS export)
name = 'YourAppName'
```

## Troubleshooting Exports

### Build Fails: "PyInstaller not found"

```bash
# Install PyInstaller
pip install pyinstaller

# Or reinstall all dependencies
pip install -r config/requirements.txt
```

### Build Fails: "hidden-import" errors

```bash
# Manually install missing packages
pip install customtkinter pandas jsonschema

# Then retry export
```

### EXE is 100+ MB

**Cause:** PyInstaller includes everything

**Solutions:**
- Use `--onefile` (already default)
- Use UPX compression (already enabled)
- Accept the size - modern apps are large

### macOS app won't open: "damaged"

```bash
# Remove quarantine attribute
xattr -cr HavenControlRoom.app

# If still fails, rebuild on the target macOS version
```

### iOS PWA map renders black screen

**Fixes:**
1. Use "iOS (Offline)" export with embedded Three.js
2. Test in Safari (not Chrome)
3. Clear Safari cache
4. Check browser console for errors (F12)

## Next Steps

- **Chapter 7**: Understand data structure for customization
- **Chapter 8**: Troubleshooting guide for common issues
- **iOS_PWA_Guide.md**: Detailed iOS-specific documentation

## Quick Reference

### Export Commands

```bash
# From Control Room GUI (recommended)
python src/control_room.py
# Then click "📦 Export App"

# Windows EXE
# Select "Windows" → Choose folder → Export

# macOS App (on Mac)
# Select "macOS" → Choose folder → Export

# iOS PWA
# Select "iOS" or "iOS (Offline)" → Choose folder → Export
# OR click "📱 Generate iOS PWA" for quick export
```

### File Locations

**Output folders:**
- Windows: `<chosen folder>/HavenControlRoom.exe`
- macOS: `<chosen folder>/HavenControlRoom.app`
- iOS: `<chosen folder>/Haven_iOS_PWA_<timestamp>.zip`

**Build logs:**
- `logs/export-windows-<timestamp>.log`
- `logs/export-macos-<timestamp>.log`

**Archived exports:**
- `Archive-Dump/dist/` (old builds preserved here)
