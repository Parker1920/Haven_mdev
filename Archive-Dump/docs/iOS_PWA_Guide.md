# Haven Galaxy iOS Progressive Web App

## Overview

The Haven Galaxy iOS PWA is a complete, self-contained web application that brings the full Haven star mapping system to iPhone and iPad. It's a single HTML file (~40KB) that works offline, stores data locally, and installs to the home screen like a native app.

## What's a PWA?

A Progressive Web App (PWA) is a modern web application that:
- **Works offline** after initial load
- **Installs to home screen** without App Store
- **Feels native** with full-screen experience
- **Stores data locally** on your device
- **Updates automatically** when you reload

## Features

### 3D Galaxy Map Viewer
- **Touch-optimized** Three.js 3D map with full gesture support
- **Pinch to zoom** in and out
- **Swipe to rotate** the galaxy view
- **Tap systems** to view detailed information
- **Reset view** button to return to default position
- **Toggle grid** for coordinate reference
- **Responsive** — adapts to phone and tablet screens
- **Glow effects** on star systems for easy identification

### Data Entry & Management
- **Complete form** with all System Entry fields:
  - System name (required)
  - Region classification
  - X, Y, Z coordinates (required)
  - Planet names (comma-separated)
  - Fauna count
  - Flora count
  - Sentinel level
  - Materials list
  - Base location
- **Add/Edit/Delete** systems with touch-friendly UI
- **Validation** — ensures required fields are filled
- **Auto-save** — data persists even if Safari is closed

### Local Storage
- All data stored securely in browser's IndexedDB/localStorage
- Survives Safari restarts and updates
- No cloud dependency — fully private
- **Export to JSON** for backup and sharing
- **Import from JSON** to restore or merge data

### Offline Capability
- **Works without internet** after first load
- Three.js library cached for offline use
- All features available without connection
- Perfect for field work or low-connectivity areas

### Installation
- **Add to Home Screen** creates app icon
- **Full-screen launch** hides Safari UI
- **Native feel** with smooth animations
- **Safe area support** for iPhone notch/Dynamic Island

## Installation Guide

### Step 1: Transfer the File
Choose one of these methods to get the HTML file to your iOS device:

**Option A: Email**
1. Email `Haven_Galaxy_iOS.html` to yourself
2. Open the email on your iPhone/iPad
3. Tap the HTML attachment

**Option B: Cloud Storage**
1. Upload to iCloud Drive, Dropbox, or Google Drive
2. Open the file in Safari on your device

**Option C: AirDrop** (Mac → iPhone)
1. Right-click the HTML file on Mac
2. Share → AirDrop → [Your iPhone]
3. Accept on iPhone and tap to open

### Step 2: Open in Safari
⚠️ **Important**: Must use Safari (not Chrome, Firefox, or Edge)
- Tap the HTML file to open
- If it opens in wrong browser, long-press → Share → Open in Safari

### Step 3: Add to Home Screen
1. Tap the **Share** button (square with up arrow)
2. Scroll down and tap **"Add to Home Screen"**
3. Choose a name (default: "Haven Galaxy")
4. Tap **"Add"** in top right

### Step 4: Launch the App
1. Find the "Haven Galaxy" icon on your home screen
2. Tap to launch
3. App opens full-screen without browser bars
4. Loading screen appears briefly, then you're ready!

## Using the App

### Tab Navigation
Switch between Map and Data views using the top-right tabs:

**Map Tab**
- Shows 3D galaxy with all your systems
- Touch controls for navigation
- Tap systems to see details
- Control panel at bottom

**Data Tab**
- System entry form at top
- Your systems list below
- Import/Export buttons

### Map Controls

**Navigation Gestures:**
- **Single finger swipe** → Rotate view
- **Pinch** → Zoom in/out
- **Tap system** → View info panel
- **Tap empty space** → Hide info panel

**Control Buttons:**
- **Reset View** — Return to default camera position
- **Grid** — Toggle coordinate grid on/off

**Info Panel:**
- Appears when you tap a system
- Shows name, region, coordinates
- Lists planets, fauna, flora
- Displays sentinel level
- Auto-hides when tapping elsewhere

### Adding Systems

1. Switch to **Data tab**
2. Fill in the form:
   - **Name** and **Coordinates** are required (red if missing)
   - Other fields are optional
   - For planets: use commas (e.g., "Terra, Mars, Venus")
3. Tap **Save** button
4. New system appears in the list below
5. Switch to Map tab to see it in 3D

### Editing Systems

1. In **Data tab**, find the system in the list
2. Tap the system card
3. Tap **Edit** button
4. Form fills with current values
5. Make changes
6. Tap **Save** to update

### Deleting Systems

1. Tap system card in the list
2. Tap **Delete** button
3. Confirm deletion
4. System removed from map and list

### Exporting Data

**To backup or share your systems:**
1. Go to **Data tab**
2. Scroll to bottom
3. Tap **Export JSON**
4. File downloads to your device
5. Share via email, AirDrop, etc.

The JSON file is compatible with the desktop Haven system!

### Importing Data

**To load systems from a file:**
1. Have a valid Haven JSON file ready
2. Go to **Data tab**
3. Tap **Import JSON**
4. Select the JSON file
5. Data merges with existing systems
6. Toast notification confirms import

## Technical Details

### Storage
- **Primary**: Browser localStorage (persistent)
- **Capacity**: ~10MB typical (thousands of systems)
- **Format**: JSON array of system objects
- **Persistence**: Survives Safari restarts, iOS updates, and history clearing

### Network Requirements
- **First load**: Requires internet to download Three.js library (~500KB)
- **After that**: Fully offline
- **Updates**: Reload HTML file in Safari to get new version

### Browser Compatibility
- **Safari iOS 12.2+** — Full support
- **Chrome iOS** — Works but can't install to home screen
- **Safari macOS** — Works for testing/preview
- **Other browsers** — Map works, installation unavailable

### Performance
- **iPhone 8+** — Smooth 60fps
- **iPad** — Enhanced for larger screens
- **Older devices** — Map simplified for performance
- **Battery impact** — Low (static map, no continuous rendering)

### Security & Privacy
- **No tracking** — Zero analytics or telemetry
- **No cloud sync** — All data stays on device
- **No permissions** — Doesn't access camera, location, etc.
- **Secure storage** — Browser's encrypted storage API

## Troubleshooting

### App Won't Install

**Symptom**: "Add to Home Screen" option missing

**Solutions**:
- Ensure you're using **Safari** (not Chrome)
- Update iOS to 12.2 or later
- Check Settings → Screen Time → Content Restrictions → Web Content → Allow
- Restart Safari and try again

### Data Not Saving

**Symptom**: Systems disappear after closing app

**Solutions**:
- Check Safari settings:
  - Settings → Safari → Block All Cookies → **OFF**
  - Settings → Safari → Advanced → Website Data → Check storage
- Don't use Private Browsing mode
- Ensure sufficient device storage
- Export JSON regularly as backup

### Map Not Loading

**Symptom**: Black screen or "Loading..." never completes

**Solutions**:
- **First use**: Requires internet for Three.js download
- Check WiFi/cellular connection
- Try reloading: pull down to refresh
- Clear Safari cache: Settings → Safari → Clear History and Data
- Re-download the HTML file (may be corrupted)

### Touch Controls Not Working

**Symptom**: Can't zoom, rotate, or tap systems

**Solutions**:
- Make sure you're in **Map tab** (not Data tab)
- Try double-tapping to wake the view
- Restart the app (swipe up → close → relaunch)
- Check for iOS accessibility settings that interfere with gestures

### Slow Performance

**Symptom**: Laggy map or delayed inputs

**Solutions**:
- Close other apps to free memory
- Restart your device
- Reduce system count (export, delete some, test)
- Update iOS to latest version
- On older devices, disable Stats if visible

### Can't Import JSON

**Symptom**: Import button does nothing or shows error

**Solutions**:
- Verify JSON file is valid (test in desktop app)
- Check file format: must be array or `{"data": [...]}`
- Try exporting first, then re-importing (to test file picker)
- Ensure file isn't corrupted
- Use Safari's file picker (Files app integration)

### App Icon Disappeared

**Symptom**: Home screen icon vanished after iOS update

**Solutions**:
- This is a known iOS PWA bug
- Re-add to home screen (data is still there!)
- Bookmark the HTML file as backup
- Report to Apple (Settings → [Your Name] → Feedback)

## Sharing & Distribution

### Sending to Others

**Best methods:**
1. **Email** — Attach HTML file directly
2. **AirDrop** — Fast for nearby users
3. **Cloud link** — Upload to Dropbox/Drive, share link
4. **USB** — Transfer via iTunes File Sharing (older method)

**Include with HTML:**
- Installation guide (iOS_INSTALLATION_GUIDE.txt)
- Quick start instructions
- Sample data if applicable

### Corporate/Team Deployment

For organizations deploying to many users:
1. Host HTML on internal web server
2. Share URL to team
3. Users bookmark or add to home screen
4. Centralized updates (just replace HTML on server)

**Security considerations:**
- Use HTTPS if hosting on server
- Validate JSON imports from untrusted sources
- Consider pre-loading data vs. user entry

### Custom Branding

To customize the app:
1. Open HTML in text editor
2. Edit at top of `<head>`:
   - `<title>` — Changes app name
   - `<meta name="apple-mobile-web-app-title">` — Home screen name
3. Edit in `<style>`:
   - `#app-title` text — Header text
   - Color variables (search for color codes like `#00d9ff`)
4. Save and test in browser

## Data Format

Systems are stored as JSON objects with this structure:

```json
{
  "name": "Kepler-442",
  "region": "Orion Arm",
  "x": 12.5,
  "y": -3.2,
  "z": 8.7,
  "planets": ["Terra Prime", "Aqualis"],
  "fauna": 15,
  "flora": 23,
  "sentinel": "Low",
  "materials": "Iron, Carbon, Gold",
  "base_location": "Planet 1, Coordinates 45.2, -12.8"
}
```

**Required fields:** `name`, `x`, `y`, `z`

**Optional fields:** All others (can be null or omitted)

**Compatible with:** Desktop Haven system (same JSON schema)

## Advanced Usage

### Developer Console

To view browser logs for debugging:
1. Connect iPhone to Mac
2. Open Safari on Mac
3. Develop → [Your iPhone] → [Haven Galaxy]
4. Console shows all logs and errors

### Exporting Browser Logs

The app includes a "Download Logs" feature:
1. Open Map tab
2. Look for small "Download Logs" button (if visible)
3. Tap to download diagnostics
4. Share log file when reporting issues

### Manual Data Backup

To manually backup data:
1. Open Safari Developer menu (Mac)
2. Select your device → Haven Galaxy
3. Storage tab → Local Storage
4. Find `haven_systems_data` key
5. Copy the JSON value
6. Save to file for archival

### Clearing All Data

To reset the app (delete all systems):
1. Settings → Safari → Advanced → Website Data
2. Find Haven Galaxy entry
3. Swipe left → Delete
4. Or use Clear All Website Data (resets all sites!)

Alternatively, just export your data, then import an empty `[]` JSON.

## Comparison: iOS vs Desktop

| Feature | iOS PWA | Desktop App |
|---------|---------|-------------|
| **Installation** | Add to home screen | Python + dependencies |
| **File size** | 40KB (single HTML) | ~100MB (EXE) |
| **Offline** | Yes (after first load) | Yes (fully standalone) |
| **Data entry** | Touch-optimized form | Desktop GUI with keyboard |
| **Map viewer** | Touch gestures | Mouse controls |
| **Data storage** | Browser localStorage | Local JSON file |
| **Import/Export** | Built-in JSON | Built-in JSON + CSV |
| **Updates** | Reload HTML file | Re-download EXE |
| **Platform** | iOS only | Windows/macOS |
| **Photos** | Not supported | Image attachments |
| **Advanced tools** | Not available | Full feature set |

**When to use iOS:**
- Field data collection on mobile
- Sharing with non-technical users
- Quick installation without setup
- View-only with occasional edits

**When to use Desktop:**
- Bulk data entry
- Advanced features (photos, reports)
- Larger datasets
- Primary development system

## Future Enhancements

Planned features for future versions:
- [ ] Photo upload support (camera integration)
- [ ] Cloud sync option (optional)
- [ ] Augmented reality star finder
- [ ] Collaborative editing (multi-user)
- [ ] Voice input for data entry
- [ ] Dark/light theme toggle
- [ ] Advanced search/filter
- [ ] Statistics dashboard
- [ ] Custom color schemes per region

Suggest features by contacting the Haven development team!

## Support

**For installation help:**
- Review this guide's Troubleshooting section
- Check iOS version (12.2+ required)
- Verify you're using Safari (not Chrome)

**For bugs or issues:**
- Export and save your data first (backup!)
- Note iOS version and device model
- Describe steps to reproduce
- Include console logs if possible

**For feature requests:**
- Explain use case and benefit
- Suggest UI/UX approach
- Mention if blocker or nice-to-have

**Contact:** Haven development team

---

**Built with ❤️ for the Haven Galaxy community**

*Progressive Web App technology powered by Three.js, modern JavaScript, and the Web Storage API*
