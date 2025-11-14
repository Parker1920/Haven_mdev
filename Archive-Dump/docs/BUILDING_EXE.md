# Building Standalone Executables

## For Distribution to Friends Without Python

If your friends don't have Python installed, you can create standalone `.exe` files that bundle everything they need.

### Step 1: Install PyInstaller (One-Time Setup)

Run this command in your terminal:
```powershell
.venv\Scripts\python.exe -m pip install pyinstaller
```

Or simply run:
```powershell
.\scripts\Build Standalone EXE.bat
```

### Step 2: Build the Executables

Run the build script:
```powershell
.\scripts\Build Standalone EXE.bat
```

This creates two standalone applications in the `dist/` folder:
- **Galactic Archive Terminal.exe** - The data entry GUI
- **Atlas Array.exe** - The map generator

### Step 3: Share With Friends

**Option A: Share Individual Apps**
1. Zip the entire folder: `dist/Galactic Archive Terminal/`
2. Send to your friend
3. They extract and run `Galactic Archive Terminal.exe`

**Option B: Share Complete Package**
Create a distribution package with:
- The executable folders from `dist/`
- The `data/` folder (with data.json)
- The `photos/` folder (with screenshots)
- A simple README

Your friend extracts everything and runs the `.exe` - no Python installation needed!

### File Sizes

Expect each `.exe` bundle to be around:
- GUI: ~100-150 MB (includes Python + CustomTkinter + all dependencies)
- Map Generator: ~80-120 MB (includes Python + Pandas)

Large file size is normal - it's Python + all libraries bundled together.

### Important Notes

1. **Build on Windows** - The `.exe` files only work on Windows. For Mac users, they still need Python.
2. **Antivirus warnings** - Some antivirus software flags PyInstaller executables as suspicious. This is a false positive. Your friends may need to allow the program.
3. **First run is slower** - The bundled app unpacks on first run, so startup takes a few seconds.

### Updating

When you update your code:
1. Run the build script again
2. Share the new `dist/` folders with your friends
3. They replace their old folders with the new ones

---

**Once built, your friends can use the app without any technical setup!**
