# Chapter 2: Installation & Setup

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, macOS 10.15+, Linux (Ubuntu 18.04+)
- **Python Version**: 3.10 or higher (3.11+ recommended)
- **RAM**: 2GB minimum, 4GB recommended
- **Disk Space**: 2GB free space for installation and generated files
- **Web Browser**: Any modern browser with WebGL support

### Recommended Setup
- **Python 3.11+** for best performance
- **8GB RAM** for large datasets (100+ systems)
- **SSD storage** for faster map generation
- **Chrome or Firefox** for best WebGL performance

## Python Installation

### Windows
1. Visit [python.org/downloads](https://www.python.org/downloads/)
2. Download **Python 3.11.x** (Windows installer)
3. Run installer as administrator
4. **Important**: Check "Add Python to PATH" during installation
5. Verify installation: `python --version` in Command Prompt

### macOS
1. Visit [python.org/downloads](https://www.python.org/downloads/)
2. Download **Python 3.11.x** (macOS installer)
3. Run the .pkg installer
4. Verify installation: `python3 --version` in Terminal

### Linux (Ubuntu/Debian)
```bash
# Update package list
sudo apt update

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip

# Verify installation
python3 --version
```

## Virtual Environment Setup

Virtual environments keep Haven's dependencies isolated from your system Python.

### Windows
```cmd
# Navigate to Haven_Mdev folder
cd C:\path\to\Haven_Mdev

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Your prompt should now show (.venv)
```

### macOS/Linux
```bash
# Navigate to Haven_Mdev folder
cd /path/to/Haven_Mdev

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Your prompt should now show (.venv)
```

### Deactivating Virtual Environment
```bash
# When done working
deactivate
```

## Dependency Installation

With virtual environment activated:

```bash
# Install all required packages
pip install -r config/requirements.txt

# Verify installation
python -c "import customtkinter, json, pathlib; print('Dependencies installed successfully')"
```

### Manual Installation (Alternative)
```bash
# Core dependencies
pip install customtkinter
pip install pyinstaller  # For building standalone executables

# Verify CustomTkinter works
python -c "import customtkinter as ctk; print('CustomTkinter version:', ctk.__version__)"
```

## First-Time Setup Verification

### Test Control Room Launch
```bash
# With virtual environment activated
python src/control_room.py
```

**Expected Result**: Control Room window opens with sidebar and status panel.

### Test Map Generation
```bash
# Generate a test map
python src/Beta_VH_Map.py --no-open
```

**Expected Result**: Map files created in `dist/` folder without errors.

### Test iOS PWA Generation
```bash
# Generate iOS PWA
python src/generate_ios_pwa.py
```

**Expected Result**: `Haven_Galaxy_iOS.html` created in `dist/` folder.

## Configuration Files

### Theme Setup
Haven includes multiple UI themes. The default theme is loaded from:
```
themes/haven_theme.json
```

To change themes:
1. Launch Control Room
2. Click "🛰️ Launch System Entry (Wizard)"
3. In the wizard, click "⚙️ Settings" button
4. Select your preferred theme

### Settings Persistence
User settings are stored in:
```
settings.json (created automatically)
```

This includes:
- Selected theme
- Window positions
- User preferences

## Folder Structure Setup

After installation, your Haven_Mdev folder should contain:

```
Haven_Mdev/
├── .venv/                 # Virtual environment (created)
├── src/                   # Python source code
├── data/                  # Data storage (created on first use)
├── dist/                  # Generated files (created on map generation)
├── logs/                  # Log files (created on first run)
├── photos/                # Image storage (created when adding photos)
├── docs/                  # Documentation
├── config/                # Configuration files
├── themes/                # UI themes
├── scripts/               # Helper scripts
└── Archive-Dump/          # Legacy files
```

## Troubleshooting Installation

### "python not found" Error
- **Windows**: Reinstall Python and ensure "Add to PATH" was checked
- **macOS**: Use `python3` instead of `python`
- **Linux**: Install python3-pip package

### Virtual Environment Issues
```bash
# Delete and recreate virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r config/requirements.txt
```

### CustomTkinter Import Error
```bash
# Force reinstall CustomTkinter
pip uninstall customtkinter
pip install customtkinter --upgrade
```

### Permission Errors
- **Windows**: Run Command Prompt as Administrator
- **macOS/Linux**: Use `sudo` only for system packages, not pip installs

## Advanced Setup Options

### Development Mode
For developers modifying the source code:
```bash
# Install additional development dependencies
pip install pytest black flake8

# Run tests
pytest -q tests/

# Format code
black src/
```

### Custom Python Installation
If you have multiple Python versions:
```bash
# Specify exact Python version
python3.11 -m venv .venv
source .venv/bin/activate
python --version  # Should show 3.11.x
```

### Portable Installation
To run Haven from USB drives or shared folders:
1. Use relative paths (Haven handles this automatically)
2. Keep all files in the same folder structure
3. Virtual environment can be copied between machines

## Updating Haven

### Minor Updates
```bash
# Pull latest changes (if using git)
git pull

# Update dependencies
pip install -r config/requirements.txt --upgrade
```

### Major Version Updates
1. Backup your `data/data.json` file
2. Follow migration guides in documentation
3. Test with sample data before using production data

## Network Requirements

### Online Features
- **Map Generation**: Requires internet for Three.js library (unless using offline embed)
- **iOS PWA Export**: Can embed libraries for offline use
- **Updates**: Check for new versions manually

### Offline Operation
- **Data Entry**: Fully offline
- **Map Viewing**: Works offline after initial load
- **iOS PWA**: Can be configured for complete offline operation

## Performance Optimization

### For Large Datasets
- Use SSD storage for faster map generation
- Close other applications during map generation
- Consider splitting large datasets into regions

### Memory Usage
- Map generation uses ~500MB-1GB RAM for typical datasets
- iOS PWA generation is memory-efficient
- Control Room uses minimal resources when idle

## Next Steps

With installation complete:
- [Chapter 3](control_room_guide.md) covers the Control Room interface
- [Chapter 4](system_entry_wizard_guide.md) teaches data entry
- [Chapter 8](troubleshooting_guide.md) helps with any issues