# Haven Control Room - Project Organization

**Date Organized:** 2025-11-03
**Status:** Clean and Organized ✅

---

## Root Level Structure

The root level has been cleaned to contain only essential items for users:

### Files at Root:
```
Haven_Mdev/
├── .DS_Store                          # macOS system file (kept for cross-platform compatibility)
├── Haven Control Room.bat              # Windows launcher - users click this to run
├── haven_control_room_mac.command      # Mac launcher - users click this to run
└── README.md                           # Main developer README
```

### Folders at Root:
```
Haven_Mdev/
├── Archive-Dump/      # Archived old content (not touched during organization)
├── config/            # Configuration files and dependencies
├── data/              # User data and schemas
├── dist/              # Distribution files (.exe, generated HTML maps)
├── docs/              # All documentation (organized by audience)
├── logs/              # Application log files
├── photos/            # User-uploaded discovery photos
├── scripts/           # Build and utility scripts
├── src/               # Source code
├── tests/             # Test suites
└── themes/            # UI theme configurations
```

---

## Documentation Organization

Documentation has been reorganized by audience and purpose:

### docs/user/ - End User Documentation
Documentation for users who run the .exe or iOS app:

- `USER_README.md` - Main user guide (START HERE)
- `control_room_guide.md` - Control room interface guide
- `galaxy_map_guide.md` - Interactive map usage
- `iOS_PWA_Guide.md` - iOS web app guide
- `iOS_Testing_Guide.md` - iOS testing instructions
- `overview_quickstart.md` - Quick start guide
- `system_entry_wizard_guide.md` - System entry tutorial
- `wizard_quick_reference.md` - Quick reference card

**Purpose:** Simple, user-friendly guides for non-technical users

### docs/dev/ - Developer Documentation
Documentation for developers working on the codebase:

- `FOLDER_STRUCTURE.md` - Project structure overview
- `installation_setup.md` - Development environment setup
- `troubleshooting_guide.md` - Common issues and solutions
- `data_structure_guide.md` - Data format specifications
- `exporting_applications.md` - Building .exe and iOS exports
- `ORGANIZATION.md` - This file (project organization)

**Purpose:** Technical documentation for contributors and maintainers

### docs/testing/ - Test Documentation
Documentation related to testing and QA:

- `TEST_RESULTS.md` - Comprehensive functionality test results
- `FIXES_APPLIED.md` - Bug fixes and improvements log

**Purpose:** Testing reports, QA documentation, and fix logs

---

## Key Design Principles

### 1. Clean Root Level
- Only launcher files and main README at root
- Easy for users to find and run the application
- No clutter or confusion

### 2. Audience-Specific Documentation
- **Users** get simplified guides in `docs/user/`
- **Developers** get technical docs in `docs/dev/`
- **QA/Testing** gets reports in `docs/testing/`

### 3. Cross-Platform Support
- Both Windows (.bat) and Mac (.command) launchers at root
- .DS_Store kept for Mac compatibility
- Documentation covers both platforms

### 4. Logical Folder Structure
- Source code separated from data
- Build artifacts in dedicated `dist/` folder
- User content (photos, data) easily accessible
- Logs isolated for troubleshooting

---

## File Distribution by Purpose

### For End Users (Distribution Package)
When packaging for distribution, include:
```
Haven_Control_Room_Package/
├── Haven Control Room.bat (Windows)
├── haven_control_room_mac.command (Mac)
├── dist/
│   └── HavenControlRoom.exe
├── docs/user/
│   └── USER_README.md (and other user docs)
├── data/
├── photos/
├── themes/
└── config/
```

### For Developers (GitHub Repository)
Full repository structure:
```
Haven_Mdev/
├── All folders and files (complete project)
├── README.md (developer guide)
└── docs/dev/ (technical documentation)
```

---

## Navigation Guide

### I'm a User - Where Do I Start?
1. Click `Haven Control Room.bat` (Windows) or `haven_control_room_mac.command` (Mac)
2. Read `docs/user/USER_README.md` for instructions
3. Check other user guides in `docs/user/` as needed

### I'm a Developer - Where Do I Start?
1. Read `README.md` at root level
2. Review `docs/dev/FOLDER_STRUCTURE.md` for project layout
3. Follow `docs/dev/installation_setup.md` to set up environment
4. Check `docs/testing/` for test results and known issues

### I'm Testing/QA - Where Do I Look?
1. Review `docs/testing/TEST_RESULTS.md` for test coverage
2. Check `docs/testing/FIXES_APPLIED.md` for recent fixes
3. Run tests from `tests/` directory
4. Report issues with reference to test documentation

---

## Maintenance Notes

### Adding New Documentation
- User guides → `docs/user/`
- Technical docs → `docs/dev/`
- Test reports → `docs/testing/`

### Root Level Policy
Only add to root level if:
- It's a launcher file users need to click
- It's the main README for developers
- It's a critical configuration file

Everything else belongs in a folder.

### Archive Policy
- `Archive-Dump/` contains historical content
- Don't modify archive unless cleaning up
- New files should never go in Archive-Dump

---

## Benefits of This Organization

✅ **User-Friendly:** Clear entry points for end users
✅ **Developer-Friendly:** Technical docs separated and easy to find
✅ **Maintainable:** Logical structure that scales well
✅ **Professional:** Clean, organized presentation
✅ **Documented:** Clear guidelines for future changes

---

## Quick Reference

**For Users:**
- Launch: `Haven Control Room.bat` or `haven_control_room_mac.command`
- Help: `docs/user/USER_README.md`

**For Developers:**
- Guide: `README.md`
- Structure: `docs/dev/FOLDER_STRUCTURE.md`
- Setup: `docs/dev/installation_setup.md`

**For Testing:**
- Results: `docs/testing/TEST_RESULTS.md`
- Fixes: `docs/testing/FIXES_APPLIED.md`

---

*This organization was implemented on 2025-11-03 to improve project clarity and usability.*
