# Testing Guide - Haven Control Room User Edition

## What Was Fixed

The frozen EXE had three critical bundling issues that have now been resolved:

### Issue 1: Missing Pandas Module ✅ FIXED
- **Error was**: `ModuleNotFoundError: No module named 'pandas'`
- **Root cause**: Pandas submodules weren't included in PyInstaller configuration
- **Fix**: Updated `config/pyinstaller/HavenControlRoom_User.spec` to include all pandas submodules

### Issue 2: Template Files Not Found ✅ FIXED
- **Error was**: `FileNotFoundError: Template not found`
- **Root cause**: Only individual template file was bundled, not the entire directory
- **Fix**: Changed to bundle entire `templates/` directory structure

### Issue 3: Static Files Missing ✅ FIXED  
- **Error was**: `Static source directory not found`
- **Root cause**: `static/` directory was never added to bundle at all
- **Fix**: Added `static/` directory to PyInstaller datas

## How to Test

### Test 1: Launch the Application
```
1. Navigate to: dist\HavenControlRoom_User\
2. Double-click: HavenControlRoom.exe
3. Expected: Control Room window opens with UI fully functional
```

### Test 2: Generate Map
```
1. In Control Room, click: "Generate Map" button
2. Expected: 
   - Map generation completes without errors
   - Console shows "Map generated successfully!"
   - dist/VH-Map.html is updated
   - No ModuleNotFoundError for pandas
   - No template file errors
```

### Test 3: View Generated Map
```
1. Click: "Open Latest Map" button
2. Expected:
   - Browser opens with themed 3D map visualization
   - All 3 sample systems visible (rotating spheres)
   - Interactive controls work (mouse drag to rotate, scroll to zoom)
   - Map displays with proper styling (not plain HTML)
```

### Test 4: System Entry (Optional)
```
1. In Control Room, click: "System Entry" button
2. Expected:
   - Entry wizard opens
   - Can add/edit systems
   - Data persists to data.json
```

## Expected Results

### ✅ Successful Indicators

- **Console**: No error messages about missing modules, templates, or files
- **Map Generation**: Completes quickly (< 5 seconds for 3 systems)
- **Map Display**: Shows interactive 3D visualization
- **Theming**: Map uses dark theme with proper styling
- **Interaction**: Mouse controls work smoothly
- **Data**: Wizard can read/write system data

### ❌ Failure Indicators (if you see these, something is still wrong)

- `ModuleNotFoundError: No module named 'pandas'` → Bundle incomplete
- `FileNotFoundError: Template not found` → Templates not bundled correctly
- `Static source directory not found` → Static files not bundled
- Browser opens blank white page → CSS/JS not loading
- Map shows only text, no 3D visuals → Static files missing or broken

## Debug Info

If you encounter issues, check these files:
- **EXE Location**: `dist/HavenControlRoom_User/HavenControlRoom.exe`
- **Error Logs**: `logs/error_logs/` folder
- **Map Output**: `dist/VH-Map.html` (should be ~65 MB)
- **Test Results**: Run `python test_user_edition_simple.py`

## Build Details

- **Build Date**: 2025-11-05
- **Python Version**: 3.13.9
- **PyInstaller Version**: 6.16.0
- **EXE Size**: 39.29 MB
- **Dependencies Bundled**:
  - pandas 2.3.3
  - numpy 2.3.4
  - customtkinter (GUI framework)
  - webbrowser (map display)
  - json, logging, pathlib (Python standard lib)

## Next Steps

1. **Run the application** using the guide above
2. **Test all features** - data entry, map generation, map viewing
3. **Report results** - let me know if you see any errors
4. **If issues occur** - check the error logs and share the output

---

**Note**: This build includes all previously fixed features:
- ✅ Correct data file path (reads from bundled data.json)
- ✅ Correct map file opening (opens VH-Map.html, not system_*.html)
- ✅ Complete PyInstaller bundling (all resources included)
- ✅ Proper theming in generated maps
