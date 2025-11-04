# Chapter 3: Control Room Interface

## Overview

The **Control Room** is Haven's central command center - a desktop application that provides access to all major functions through an intuitive interface. Think of it as mission control for your star mapping operations.

## Launching the Control Room

### Windows
- **Double-click** `Haven Control Room.bat` in the main folder
- Or run: `python src/control_room.py`

### macOS
- **Double-click** `haven_control_room_mac.command`
- Or run: `python src/control_room.py`

### Linux
- Run: `python src/control_room.py`

### Standalone Executables
If you've exported standalone versions:
- Windows: Run `HavenControlRoom.exe`
- macOS: Run `HavenControlRoom.app`

## Interface Layout

The Control Room uses a two-panel layout optimized for efficiency:

### Left Panel: Quick Actions Sidebar
A dark glassmorphic panel with categorized buttons:

```
✨ HAVEN CONTROL ROOM
══════════════════════

QUICK ACTIONS
🛰️ Launch System Entry (Wizard)
🗺️ Generate Map
🌐 Open Latest Map
📱 Generate iOS PWA

FILE MANAGEMENT
📁 Data Folder
🧭 Logs Folder
📖 Documentation

ADVANCED TOOLS (dev mode)
🔧 Update Dependencies
📦 Export App (EXE/.app)
```

### Right Panel: Status & Content Area
Dynamic content area showing:
- **Status messages** from operations
- **Live log output** for monitoring progress
- **Modal dialogs** for exports and settings

## Quick Actions

### 🛰️ Launch System Entry (Wizard)
- Opens the two-page System Entry Wizard
- Allows adding/editing complete star systems
- Data saved automatically to `data/data.json`

### 🗺️ Generate Map
- Runs `Beta_VH_Map.py` to create 3D visualizations
- Generates `dist/VH-Map.html` and system-specific HTML files
- Shows progress in the status panel

### 🌐 Open Latest Map
- Opens the most recently generated map in your default browser
- Automatically finds the newest HTML file in `dist/`
- Handles different browsers appropriately

### 📱 Generate iOS PWA
- Creates a single HTML file for iOS devices
- Embeds all data and can include 3D libraries for offline use
- Output: `dist/Haven_Galaxy_iOS.html`

## File Management

### 📁 Data Folder
- Opens `data/` folder in system file explorer
- Contains your `data.json` and schema files
- Use this to backup or manually edit data

### 🧭 Logs Folder
- Opens `logs/` folder for troubleshooting
- Contains timestamped log files from all operations
- Essential for diagnosing issues

### 📖 Documentation
- Opens `docs/` folder containing all guides
- Access detailed help and reference materials

## Advanced Tools (Development Mode)

These tools only appear when running from source code (not standalone EXE):

### 🔧 Update Dependencies
- Runs `pip install -r config/requirements.txt --upgrade`
- Updates all Python packages to latest compatible versions
- Shows progress and any errors in status panel

### 📦 Export App (EXE/.app)
- Opens export dialog for creating standalone applications
- Choose platform: Windows, macOS, or iOS
- Select output folder for generated files

## Status Monitoring

### Real-time Status Updates
The status label shows current operation:
- "Ready." - Waiting for user action
- "Generating map..." - Map generation in progress
- "System Entry Wizard launched." - External window opened

### Log Output Panel
- Shows detailed progress and any warnings/errors
- Auto-scrolls to show latest messages
- Color-coded for different message types
- Copy/paste log content for sharing

### Background Operations
Long-running tasks (map generation, exports) run in background threads:
- UI remains responsive
- Progress shown in status area
- Cancel with application close

## Export Dialog

### Platform Selection
- **Windows**: Creates `.exe` installer with embedded Python
- **macOS**: Generates `.app` bundle or build kit
- **iOS**: Creates Progressive Web App HTML file
- **iOS (Offline)**: Embeds Three.js for no-internet operation

### Output Folder Selection
- Browse to choose destination folder
- Defaults to `dist/` folder
- Creates subfolders as needed

### Export Process
1. Select platform and output folder
2. Click "Export"
3. Monitor progress in status panel
4. Find results in output folder

## Theme & Appearance

### Built-in Themes
The Control Room uses the same theme system as other components:
- **Dark**: Default professional appearance
- **Light**: Alternative light color scheme
- **Cosmic**: Enhanced dark theme
- **Haven (Cyan)**: Signature blue/cyan theme

### Theme Configuration
Themes are configured in the System Entry Wizard:
1. Launch System Entry Wizard
2. Click "⚙️ Settings" button
3. Select theme from dropdown
4. Changes apply immediately

## Error Handling

### Common Issues
- **"Python not found"**: Ensure virtual environment is activated
- **"Module not found"**: Run dependency update
- **"Permission denied"**: Check file/folder permissions
- **"Map generation failed"**: Check logs for detailed errors

### Recovery Procedures
1. Check status panel for error messages
2. Review log files in `logs/` folder
3. Verify data integrity in `data/data.json`
4. Try restarting the Control Room
5. Check disk space and permissions

## Keyboard Shortcuts

- **Ctrl+C**: Copy selected log text
- **Ctrl+A**: Select all log text
- **Escape**: Close modal dialogs
- **Enter**: Confirm dialog actions

## Performance Considerations

### Memory Usage
- Control Room: ~50-100MB RAM
- Map Generation: ~200-500MB additional
- iOS Export: ~100-200MB additional

### Background Processing
- Long operations don't block the UI
- Multiple operations can run simultaneously
- Progress monitoring prevents user uncertainty

## Integration with Other Components

### System Entry Wizard
- Launched as separate process to avoid Tkinter conflicts
- Data changes reflected immediately in Control Room
- Wizard handles all data validation

### Map Generator
- Runs as subprocess with redirected output
- Progress parsing shows meaningful status updates
- Error detection and user-friendly messages

### iOS PWA Generator
- Python script integration
- Data embedding and offline options
- File size reporting and validation

## Troubleshooting

### Control Room Won't Start
```
Check logs/control-room-*.log for errors
Verify Python installation and virtual environment
Try: python src/control_room.py --help
```

### Buttons Not Responding
```
Check if background operations are running
Restart Control Room
Verify file permissions on data/ and dist/ folders
```

### Export Failures
```
Check available disk space
Verify write permissions on output folder
Review detailed logs for specific error messages
```

## Advanced Usage

### Command Line Options
```bash
python src/control_room.py --help
```

### Custom Configuration
- Themes: Modify `themes/haven_theme.json`
- Settings: Edit `settings.json` (created automatically)

### Development Integration
- Source code modifications auto-detected
- Debug mode available with additional logging
- Test integration with pytest framework

## Next Steps

With the Control Room mastered:
- [Chapter 4](system_entry_wizard_guide.md) covers data entry in detail
- [Chapter 5](galaxy_map_guide.md) explains map generation and viewing
- [Chapter 6](exporting_applications.md) covers creating distributable apps