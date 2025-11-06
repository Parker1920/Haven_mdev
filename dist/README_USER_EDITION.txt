================================================================================
    HAVEN CONTROL ROOM - USER EDITION (Explorer's Version)
================================================================================

Version: 1.1
Build Date: November 6, 2025
Status: FULLY FUNCTIONAL - All issues resolved

================================================================================
WHAT THIS IS
================================================================================

This is the standalone "Explorer's Edition" of Haven Control Room.

It's designed for explorers in the field to:
- Add new star systems they discover
- Generate 3D maps of the galaxy
- Export their data back to you

NO Python installation required!
NO complex setup!
Just double-click and go!

================================================================================
QUICK START (30 seconds)
================================================================================

1. LAUNCH THE APP
   - Double-click: HavenControlRoom.exe

2. CHOOSE YOUR STARTING DATA
   - First launch: Pick "Example Data" (3 sample systems) OR "Clean" (start empty)
   - Click YES for examples, NO for clean start

3. YOU'LL SEE THE CONTROL ROOM
   Three main buttons:

   [Launch System Entry (Wizard)] - Add/edit star systems
   [Generate Map] - Create 3D visualization
   [Open Latest Map] - View map in browser

4. START EXPLORING!

================================================================================
MAIN FEATURES
================================================================================

1. SYSTEM ENTRY WIZARD
   - Add new systems with coordinates (x, y, z)
   - Record planets and moons
   - Track resources, fauna, flora
   - Attach photos
   - All data auto-saves to JSON

2. MAP GENERATOR
   - Creates interactive 3D galaxy map
   - Click and drag to rotate
   - Mouse wheel to zoom
   - All systems appear as glowing points

3. MAP VIEWER
   - Opens in your web browser
   - Fully interactive controls
   - Shows system details on click

4. DATA EXPORT
   - Your data saves to: files/data.json
   - Send this file back for master map integration
   - Easy email attachment

5. LOGS & FOLDERS
   - View logs for troubleshooting
   - Access photos folder
   - All organized in "files" subdirectory

================================================================================
FILE STRUCTURE
================================================================================

After first launch, you'll have:

HavenControlRoom.exe         <- The application (double-click to run)
└── files/                   <- All your data (auto-created)
    ├── data.json           <- Your star systems (THIS IS WHAT YOU SEND BACK)
    ├── logs/               <- Operation logs
    ├── maps/               <- Generated 3D maps
    │   └── VH-Map.html    <- Main galaxy map
    ├── photos/             <- Your custom images
    └── backups/            <- Auto-backups

================================================================================
HOW TO USE
================================================================================

ADDING A NEW SYSTEM:
1. Click "Launch System Entry (Wizard)"
2. Click "Add New System"
3. Fill in:
   - System Name (required)
   - X, Y, Z coordinates (required)
   - Region (required)
   - Fauna, Flora, Resources (optional)
4. Add planets/moons if needed
5. Click "Save System"
6. Done! Data auto-saved

GENERATING A MAP:
1. Click "Generate Map"
2. Wait 1-5 seconds
3. Map created in files/maps/VH-Map.html

VIEWING THE MAP:
1. Click "Open Latest Map"
2. Browser opens with 3D visualization
3. Controls:
   - Left-click drag: Rotate
   - Mouse wheel: Zoom
   - Right-click drag: Pan

EXPORTING YOUR DATA:
1. Close the app (saves automatically)
2. Navigate to: files/data.json
3. Email/send this file to mission control
4. Done!

================================================================================
TROUBLESHOOTING
================================================================================

PROBLEM: "Failed to initialize data file" error
SOLUTION: This is FIXED in version 1.1! If you still see it:
          - Delete the "files" folder
          - Restart the exe
          - Choose example or clean data again

PROBLEM: Map won't generate
SOLUTION: - Make sure you've added at least one system
          - Check logs folder for errors
          - Ensure x, y, z are numbers (not text)

PROBLEM: Wizard won't open
SOLUTION: - Close and relaunch the control room
          - Check logs/control-room-*.log for errors

PROBLEM: Can't save systems
SOLUTION: - Make sure all required fields are filled:
            * System name
            * X, Y, Z coordinates (must be numbers)
            * Region

PROBLEM: Windows SmartScreen warning
SOLUTION: 1. Click "More info"
          2. Click "Run anyway"
          (This is normal for unsigned open-source software)

================================================================================
WHAT'S FIXED IN VERSION 1.1
================================================================================

Previous version had a critical bug where:
- Template data files weren't bundled in exe
- Startup would fail with "Failed to initialize data file"
- Control room would never open

VERSION 1.1 FIXES:
✅ Template files now bundled correctly
✅ Startup file selection works perfectly
✅ Clean and Example data both functional
✅ All paths work in frozen exe mode
✅ File structure auto-creates properly
✅ Single source of truth architecture maintained

================================================================================
TECHNICAL DETAILS
================================================================================

- Platform: Windows 10/11 (64-bit)
- Size: ~40 MB (includes Python runtime + all dependencies)
- Data Format: JSON (human-readable, easy to merge)
- Offline: Works completely offline (no internet required)
- Portable: Copy entire folder anywhere, still works

================================================================================
SENDING DATA BACK
================================================================================

To send your discoveries back:

1. Find the file: files/data.json
2. Email it as attachment
3. Or upload to shared drive
4. Include your explorer name in email

Your data will be merged into the master galaxy map!

================================================================================
TIPS & BEST PRACTICES
================================================================================

- BACKUP: The app auto-backs up to files/backups/ before each save
- PHOTOS: Put images in files/photos/ before linking in wizard
- NAMING: Use clear system names (e.g., "ALPHA-7432" not "System 1")
- COORDINATES: Double-check x/y/z values for accurate positioning
- REGIONS: Use consistent region names for better organization

================================================================================
SUPPORT
================================================================================

If you encounter issues:
1. Check files/logs/control-room-*.log for errors
2. Try restarting the application
3. Delete "files" folder and restart (will prompt for data again)
4. Contact mission control with:
   - Screenshot of error
   - Log file from files/logs/
   - Description of what you were doing

================================================================================
VERSION HISTORY
================================================================================

v1.1 (2025-11-06)
- FIXED: Startup data file initialization
- FIXED: Template files bundled correctly
- TESTED: All features working (wizard, map, export, logs)

v1.0 (2025-11-05)
- Initial release
- Basic functionality
- Known issue with startup (fixed in v1.1)

================================================================================

Happy exploring! 🚀🌌

Questions? Contact mission control.
