# Chapter 8: Troubleshooting & Support

## Overview

This chapter covers common issues, diagnostic procedures, and solutions for Haven Control Room. Most problems can be resolved by checking logs and following the steps below.

## Quick Diagnostic Checklist

Before diving into specific issues, run this quick checklist:

- [ ] Python 3.10+ installed: `python --version` or `python3 --version`
- [ ] Virtual environment activated (if using one): `which python` shows `.venv`
- [ ] Dependencies installed: `pip list | grep customtkinter`
- [ ] Data file exists: `ls data/data.json`
- [ ] Data file is valid JSON: `python -m json.tool data/data.json`
- [ ] Logs folder exists and is writable: `ls -la logs/`

If any item fails, start there before investigating specific errors.

---

## Installation Issues

### Python Not Found

**Symptoms:**
```bash
python: command not found
```

**Solutions:**

**macOS/Linux:**
```bash
# Try python3 instead
python3 --version

# Or install Python
# macOS:
brew install python3

# Linux (Ubuntu/Debian):
sudo apt-get install python3 python3-pip
```

**Windows:**
```batch
REM Download from https://www.python.org/downloads/
REM During install: Check "Add Python to PATH"
```

### Wrong Python Version

**Symptoms:**
```bash
python --version
Python 2.7.18  # Too old!
```

**Solutions:**
```bash
# Use python3 explicitly
python3 --version  # Should be 3.10+

# Create venv with specific version
python3 -m venv .venv

# Update system Python (if needed)
# macOS with Homebrew:
brew upgrade python3
```

### pip Not Found

**Symptoms:**
```bash
pip: command not found
```

**Solutions:**
```bash
# Use python -m pip instead
python -m pip --version

# Or install pip
python -m ensurepip --upgrade

# macOS/Linux:
sudo apt-get install python3-pip  # Linux
brew install python3-pip          # macOS
```

### Dependencies Won't Install

**Symptoms:**
```bash
ERROR: Could not install packages due to an OSError
```

**Solutions:**

1. **Check permissions:**
   ```bash
   # Use venv (recommended)
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
   pip install -r config/requirements.txt
   ```

2. **Update pip:**
   ```bash
   python -m pip install --upgrade pip
   ```

3. **Install one by one:**
   ```bash
   pip install pandas
   pip install customtkinter
   pip install jsonschema
   pip install pyinstaller
   ```

4. **Check internet connection:**
   ```bash
   ping pypi.org
   ```

### Virtual Environment Issues

**Problem: venv won't activate**

**Windows:**
```batch
REM PowerShell execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

REM Then activate
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
# Check venv exists
ls .venv/bin/python

# Activate
source .venv/bin/activate

# Verify
which python  # Should show .venv/bin/python
```

---

## Control Room Issues

### Control Room Won't Launch

**Symptoms:**
- Double-clicking launcher does nothing
- Terminal shows "ModuleNotFoundError"
- Window appears then disappears

**Diagnostic:**
```bash
# Run from terminal to see errors
python src/control_room.py
```

**Common Causes:**

1. **Missing customtkinter:**
   ```bash
   pip install customtkinter
   ```

2. **Display/GUI issues:**
   ```bash
   # macOS: Install XQuartz if using SSH
   # Linux: Install tkinter
   sudo apt-get install python3-tk
   ```

3. **Corrupted config:**
   ```bash
   # Reset theme settings
   rm settings.json
   python src/control_room.py
   ```

### Buttons Don't Work

**Symptoms:**
- Clicking buttons does nothing
- Console shows errors
- Frozen UI

**Solutions:**

1. **Check logs:**
   ```bash
   # View latest log
   ls -lt logs/ | head -5
   cat logs/control-room-<date>.log
   ```

2. **Restart Control Room:**
   - Close completely (Cmd+Q / Alt+F4)
   - Relaunch

3. **Clear cache:**
   ```bash
   # Remove Python bytecode
   find . -name "*.pyc" -delete
   find . -name "__pycache__" -type d -delete
   ```

### System Entry Wizard Won't Open

**Symptoms:**
- "Launch System Entry" button does nothing
- Error in logs: "system_entry_wizard not found"

**Solutions:**

1. **Verify file exists:**
   ```bash
   ls src/system_entry_wizard.py
   ```

2. **Check for syntax errors:**
   ```bash
   python -m py_compile src/system_entry_wizard.py
   ```

3. **Run directly:**
   ```bash
   python src/system_entry_wizard.py
   ```

---

## Data Entry Issues

### Can't Save System

**Symptoms:**
- "Save" button grayed out
- Validation errors
- "Invalid JSON" message

**Solutions:**

1. **Check required fields:**
   - System name (required)
   - Coordinates x, y, z (required)
   - Region (required)

2. **Check coordinate format:**
   ```json
   "x": 3,      // ✓ Correct (number)
   "x": "3",    // ✗ Wrong (string)
   "x": "three" // ✗ Wrong (text)
   ```

3. **Check JSON syntax:**
   ```bash
   python -m json.tool data/data.json
   ```

4. **If corrupted, restore backup:**
   ```bash
   # Check for backup
   ls data/*.bak

   # Restore if needed
   cp data/data.json.bak data/data.json
   ```

### Photos Won't Attach

**Symptoms:**
- Photo field shows error
- File browser doesn't open
- Photos don't appear in map

**Solutions:**

1. **Check photos folder exists:**
   ```bash
   mkdir -p photos
   ```

2. **Check file permissions:**
   ```bash
   chmod 755 photos/
   chmod 644 photos/*.png
   ```

3. **Check file format:**
   - Supported: PNG, JPG, JPEG, GIF
   - Recommended: PNG for best quality

4. **Check file path:**
   ```json
   {
     "photo": "photos/system1.png"  // ✓ Relative path
     "photo": "/Users/.../photos/system1.png"  // ✗ Absolute path
   }
   ```

### Data Validation Errors

**Symptoms:**
- Red error messages in form
- Can't save despite filling fields
- "Schema validation failed"

**Solutions:**

1. **Check schema file:**
   ```bash
   ls data/data.schema.json
   python -m json.tool data/data.schema.json
   ```

2. **Review error message:**
   - Usually indicates specific field issue
   - Check data type (number vs string)

3. **Test with minimal data:**
   ```json
   {
     "_meta": {"version": "1.0.0"},
     "TEST_SYSTEM": {
       "id": "SYS_TEST",
       "name": "TEST_SYSTEM",
       "x": 0,
       "y": 0,
       "z": 0,
       "region": "Test",
       "planets": []
     }
   }
   ```

---

## Map Generation Issues

### Map Won't Generate

**Symptoms:**
- "Generate Map" does nothing
- Error in logs
- Black screen in browser

**Diagnostic:**
```bash
# Run map generator directly
python src/Beta_VH_Map.py --no-open

# Check logs
cat logs/map-<date>.log
```

**Common Causes:**

1. **Invalid data:**
   ```bash
   # Validate JSON
   python -m json.tool data/data.json

   # Check for missing coordinates
   grep -E '"x"|"y"|"z"' data/data.json
   ```

2. **Missing pandas:**
   ```bash
   pip install pandas
   ```

3. **Insufficient disk space:**
   ```bash
   df -h .  # Check free space
   ```

### Map Displays Incorrectly

**Symptoms:**
- Systems in wrong positions
- Missing systems
- Garbled text

**Solutions:**

1. **Verify coordinate data:**
   ```python
   import json
   with open('data/data.json') as f:
       data = json.load(f)
       for name, sys in data.items():
           if name != '_meta':
               x, y, z = sys.get('x'), sys.get('y'), sys.get('z')
               print(f"{name}: ({x}, {y}, {z})")
   ```

2. **Clear browser cache:**
   - Chrome: Ctrl+Shift+Delete (Windows) / Cmd+Shift+Delete (macOS)
   - Safari: Cmd+Option+E
   - Firefox: Ctrl+Shift+Delete

3. **Regenerate map:**
   ```bash
   rm dist/VH-Map.html
   python src/Beta_VH_Map.py
   ```

4. **Try different browser:**
   - Chrome (best compatibility)
   - Firefox
   - Safari (may be slower)

### Map Performance Issues

**Symptoms:**
- Slow rotation
- Laggy controls
- Browser freezes

**Solutions:**

1. **Reduce system count:**
   - Archive old systems
   - Generate region-specific maps

2. **Close other tabs:**
   - Free up browser memory
   - Disable browser extensions

3. **Update browser:**
   ```bash
   # Check browser version
   # Chrome: chrome://version
   # Firefox: about:support
   ```

4. **Check system resources:**
   ```bash
   # macOS
   top -o mem | head -15

   # Linux
   free -h
   htop

   # Windows
   # Task Manager → Performance tab
   ```

---

## Export Issues

### Build Fails

**Symptoms:**
- "Export App" fails
- PyInstaller errors
- Incomplete executable

**Solutions:**

1. **Check PyInstaller:**
   ```bash
   pip install --upgrade pyinstaller
   pyinstaller --version  # Should be 6.0+
   ```

2. **Check disk space:**
   ```bash
   df -h .  # Need ~500MB free
   ```

3. **Review build logs:**
   ```bash
   cat logs/export-windows-<timestamp>.log
   cat logs/export-macos-<timestamp>.log
   ```

4. **Try manual build:**
   ```bash
   # Windows
   pyinstaller --onefile --windowed --name HavenControlRoom src/control_room.py

   # macOS
   pyinstaller --onefile --windowed --name HavenControlRoom src/control_room.py
   ```

### Executable Won't Run

**Windows:**
```batch
REM Check Windows Defender / Antivirus
REM May need to whitelist EXE

REM Run from command prompt to see errors
HavenControlRoom.exe
```

**macOS:**
```bash
# Remove quarantine
xattr -cr HavenControlRoom.app

# Check for errors
./HavenControlRoom.app/Contents/MacOS/HavenControlRoom
```

### iOS PWA Issues

**See Chapter 6: Exporting Applications → iOS PWA Troubleshooting**

Common iOS-specific fixes:
- Must use Safari (not Chrome)
- Enable JavaScript in Safari settings
- Use "iOS (Offline)" export for true offline
- Clear Safari cache and retry

---

## Log File Analysis

### Where Logs Are Stored

```
logs/
├── control-room-<date>.log      # Control Room activity
├── gui-<date>.log               # System Entry Wizard
├── map-<date>.log               # Map generation
├── export-windows-<date>.log    # Windows EXE builds
└── export-macos-<date>.log      # macOS app builds
```

### Reading Logs

**View latest log:**
```bash
# Control Room
tail -f logs/control-room-*.log

# Map generation
tail -f logs/map-*.log
```

**Search for errors:**
```bash
grep -i "error" logs/*.log
grep -i "exception" logs/*.log
grep -i "failed" logs/*.log
```

**Common error patterns:**

```
ModuleNotFoundError: No module named 'X'
→ Solution: pip install X

PermissionError: [Errno 13] Permission denied
→ Solution: Check file permissions or run with proper privileges

JSONDecodeError: Expecting value
→ Solution: Fix JSON syntax in data.json

KeyError: 'x'
→ Solution: Add missing coordinate fields to system data
```

### Enable Debug Logging

Edit `src/control_room.py`:
```python
# Line ~70
logger.setLevel(logging.DEBUG)  # Change from INFO to DEBUG
```

Provides more detailed output for troubleshooting.

---

## Data Recovery

### Corrupted data.json

**Symptoms:**
- App crashes on launch
- "Invalid JSON" errors
- Can't open System Entry

**Recovery steps:**

1. **Check for backup:**
   ```bash
   ls -lt Archive-Dump/data/
   ls -lt data/*.bak
   ```

2. **Restore backup:**
   ```bash
   # From Archive-Dump
   cp Archive-Dump/data/data.json.bak data/data.json

   # Or from .bak file
   cp data/data.json.bak data/data.json
   ```

3. **Validate restored file:**
   ```bash
   python -m json.tool data/data.json
   ```

4. **If no backup exists, recreate:**
   ```json
   {
     "_meta": {
       "version": "1.0.0",
       "last_modified": "2025-01-01T00:00:00Z"
     }
   }
   ```

### Lost Systems

**If systems disappeared after bad save:**

1. **Check system logs:**
   ```bash
   grep "Saved system" logs/gui-*.log
   ```

2. **Look for autosave:**
   ```bash
   find . -name "*.json.tmp" -o -name "*.autosave"
   ```

3. **Check Archive-Dump:**
   ```bash
   ls Archive-Dump/data/
   ```

4. **Reconstruct from screenshots:**
   - Check photos/ folder
   - Recreate system entries manually

### Manual JSON Repair

If JSON is corrupted:

1. **Find syntax error:**
   ```bash
   python -m json.tool data/data.json
   # Error message shows line number
   ```

2. **Common JSON mistakes:**
   ```json
   // ✗ Trailing comma
   {
     "name": "System1",
     "x": 1,  ← Remove this comma
   }

   // ✗ Missing quotes
   {
     name: "System1"  ← Need quotes: "name"
   }

   // ✗ Single quotes
   {
     'name': 'System1'  ← Use double quotes
   }
   ```

3. **Use online validator:**
   - https://jsonlint.com/
   - Paste JSON, fix errors
   - Save corrected version

---

## Performance Optimization

### Slow Startup

**Causes:**
- Large data file (1000+ systems)
- Slow disk (HDD vs SSD)
- Low RAM (<4GB)

**Solutions:**
1. Split data into multiple files
2. Archive old systems
3. Upgrade to SSD
4. Close other applications

### High Memory Usage

**Symptoms:**
- Computer slows down
- App becomes unresponsive
- "Out of memory" errors

**Solutions:**
```bash
# Check memory usage
# macOS/Linux:
ps aux | grep python

# Reduce dataset size
# Archive systems you don't use frequently
```

### Disk Space

**Check space:**
```bash
# macOS/Linux
df -h .

# Windows
dir
```

**Clean up:**
```bash
# Remove old logs (older than 30 days)
find logs/ -name "*.log" -mtime +30 -delete

# Remove old map files
rm dist/system_*.html  # Keep VH-Map.html

# Clean Python cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -delete
```

---

## Getting Help

### Before Asking for Help

1. **Check logs:**
   ```bash
   cat logs/control-room-<date>.log
   ```

2. **Try simple test:**
   ```bash
   python -c "import customtkinter; print('OK')"
   ```

3. **Document your environment:**
   ```bash
   python --version
   pip list
   uname -a  # macOS/Linux
   systeminfo  # Windows
   ```

### Creating a Bug Report

Include:
1. **What you tried to do**
2. **What happened instead**
3. **Error messages** (full text)
4. **Log files** (attach relevant logs)
5. **System info:**
   ```bash
   python --version
   pip list | grep -E "customtkinter|pandas|jsonschema"
   ```

### Community Support

- **GitHub Issues**: [Haven repository] (if public)
- **Documentation**: Check all chapters in docs/
- **Stack Overflow**: Tag `python`, `customtkinter`, `three.js`

### Self-Diagnosis Tools

**Run system check:**
```python
# check_system.py
import sys
import subprocess

print(f"Python: {sys.version}")
print(f"Platform: {sys.platform}")

try:
    import customtkinter
    print(f"customtkinter: {customtkinter.__version__}")
except ImportError:
    print("customtkinter: NOT INSTALLED")

try:
    import pandas
    print(f"pandas: {pandas.__version__}")
except ImportError:
    print("pandas: NOT INSTALLED")

try:
    import jsonschema
    print(f"jsonschema: {jsonschema.__version__}")
except ImportError:
    print("jsonschema: NOT INSTALLED")

# Check paths
from pathlib import Path
print(f"\nData file exists: {Path('data/data.json').exists()}")
print(f"Photos folder exists: {Path('photos').exists()}")
print(f"Logs folder exists: {Path('logs').exists()}")
```

Run: `python check_system.py`

---

## Emergency Reset

If nothing works and you want to start fresh:

### Backup Current State
```bash
# Create backup
mkdir ~/Haven_backup_$(date +%Y%m%d)
cp -R data logs photos ~/Haven_backup_$(date +%Y%m%d)/
```

### Reset Environment
```bash
# Remove venv
rm -rf .venv

# Clear cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -delete

# Reinstall
python3 -m venv .venv
source .venv/bin/activate
pip install -r config/requirements.txt
```

### Reset Data (last resort)
```bash
# Backup first!
cp data/data.json data/data.json.old

# Reset to minimal data
echo '{
  "_meta": {"version": "1.0.0"}
}' > data/data.json
```

### Verify
```bash
python src/control_room.py
# Should launch without errors
```

---

## Quick Reference

### Most Common Fixes

| Problem | Quick Fix |
|---------|-----------|
| Can't launch Control Room | `pip install customtkinter` |
| Map won't generate | `python -m json.tool data/data.json` |
| Slow performance | Archive old systems, close tabs |
| Can't save system | Check x/y/z are numbers |
| Export fails | `pip install --upgrade pyinstaller` |
| iOS PWA won't install | Use Safari, not Chrome |
| Python not found | Try `python3` instead of `python` |
| Corrupted data | Restore from `Archive-Dump/data/` |

### Essential Commands

```bash
# Check everything
python --version
pip list
python -m json.tool data/data.json

# View logs
tail -f logs/control-room-*.log
grep -i error logs/*.log

# Reset environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r config/requirements.txt

# Backup data
cp data/data.json data/data.json.backup_$(date +%Y%m%d)
```

### When to Archive and Start Fresh

Consider creating a new Haven project if:
- 1000+ systems (performance degrades)
- Exploring new galaxy/region
- Testing major changes
- Sharing subset of data

Copy `data/data.json` to a new folder and start clean.

---

## Next Steps

- **Chapter 1**: Return to Overview & Quick Start
- **Chapter 7**: Learn about Data Structure & Schema
- **Chapter 5**: Galaxy Map Generation details
