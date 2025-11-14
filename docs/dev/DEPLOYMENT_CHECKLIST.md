# Haven Control Room - User Edition Deployment Checklist

Use this checklist before distributing the User Edition to end users.

---

## Pre-Build Checklist

### ✅ Code Review
- [ ] `src/control_room_user.py` is complete and tested
- [ ] `config/settings_user.py` has correct paths
- [ ] All imports are correct (no missing modules)
- [ ] No hardcoded development paths
- [ ] Error handling is user-friendly

### ✅ Data Files
- [ ] `dist/clean_data.json` exists and is valid JSON
- [ ] `dist/example_data.json` has exactly 50 systems
- [ ] Example data is high quality (no test/garbage data)
- [ ] `_meta` sections are properly formatted

### ✅ Documentation
- [ ] `dist/README_USER.md` is complete
- [ ] `dist/QUICK_START.txt` is clear and concise
- [ ] Contact information is up-to-date
- [ ] Version numbers are correct
- [ ] All file paths in documentation are accurate

---

## Build Process

### ✅ Environment Setup
- [ ] Virtual environment is activated
- [ ] All dependencies installed: `pip install -r config/requirements.txt`
- [ ] PyInstaller is latest version: `pip install --upgrade pyinstaller`

### ✅ Execute Build
```batch
build_user_exe.bat
```

- [ ] Build script completes without errors
- [ ] EXE is created in `dist/`
- [ ] Distribution folder is created: `dist/HavenControlRoom_User/`
- [ ] ZIP archive is created with timestamp

### ✅ Verify Build Output

**Check folder structure:**
```
HavenControlRoom_User/
├── HavenControlRoom.exe
├── clean_data.json
├── example_data.json
├── README.md
├── QUICK_START.txt
└── files/
    ├── logs/
    ├── photos/
    ├── maps/
    └── backups/
```

- [ ] All files present
- [ ] EXE size is reasonable (~50-150MB)
- [ ] JSON files are not corrupted
- [ ] Documentation files are readable

---

## Testing

### ✅ Initial Launch Test

**Fresh Install Simulation:**
1. [ ] Extract ZIP to a clean folder (no existing data)
2. [ ] Double-click `HavenControlRoom.exe`
3. [ ] Startup dialog appears
4. [ ] All three options work:
   - [ ] Start Fresh
   - [ ] Load Example
   - [ ] Browse
5. [ ] Application launches without errors

### ✅ Example Data Test

**Starting with examples:**
1. [ ] Launch EXE
2. [ ] Choose "Load Example Data"
3. [ ] Application opens
4. [ ] System count shows 50
5. [ ] Generate map
6. [ ] Map shows all 50 systems
7. [ ] Map is interactive (rotate, zoom, click)

### ✅ System Entry Test

**Adding new systems:**
1. [ ] Click "Launch System Entry (Wizard)"
2. [ ] Wizard window opens
3. [ ] Add a test system with:
   - [ ] Basic info (name, coords, region)
   - [ ] 2 planets
   - [ ] 1 moon on first planet
   - [ ] 1 space station
4. [ ] Save system
5. [ ] Return to Control Room
6. [ ] System count increments
7. [ ] Generate map
8. [ ] New system appears on map

### ✅ Photo Upload Test

**Adding photos:**
1. [ ] Launch wizard
2. [ ] Add/edit a planet
3. [ ] Click "Add Photo"
4. [ ] Select an image file
5. [ ] Photo appears in wizard
6. [ ] Save planet
7. [ ] Check `files/photos/` folder
8. [ ] Image file is copied there

### ✅ File Management Test

**Testing file operations:**
1. [ ] Click "Open Data Folder"
   - [ ] Explorer opens to `files/` folder
2. [ ] Click "Open Logs Folder"
   - [ ] Explorer opens to `files/logs/` folder
3. [ ] Click "Open Photos Folder"
   - [ ] Explorer opens to `files/photos/` folder
4. [ ] Click "Load Different File"
   - [ ] File dialog opens
   - [ ] Can select a different JSON file
   - [ ] File loads successfully

### ✅ Data Persistence Test

**Verifying data saves:**
1. [ ] Add several systems
2. [ ] Close application
3. [ ] Relaunch application
4. [ ] System count is correct
5. [ ] Generate map
6. [ ] All systems appear

### ✅ Error Handling Test

**Testing edge cases:**
1. [ ] Try to load invalid JSON file
   - [ ] Error message is user-friendly
2. [ ] Delete `data.json` while running
   - [ ] Application handles gracefully
3. [ ] Fill wizard with invalid coordinates
   - [ ] Validation works or saves anyway
4. [ ] Generate map with 0 systems
   - [ ] Shows helpful message

### ✅ Performance Test

**With larger datasets:**
1. [ ] Load example data (50 systems)
2. [ ] Application is responsive
3. [ ] Map generation completes in <2 minutes
4. [ ] Map is smooth and interactive
5. [ ] No crashes or freezes

---

## Cross-Environment Testing

### ✅ Windows 10
- [ ] EXE launches
- [ ] All features work
- [ ] No DLL errors

### ✅ Windows 11
- [ ] EXE launches
- [ ] All features work
- [ ] No DLL errors

### ✅ Different User Accounts
- [ ] EXE works for non-admin user
- [ ] Files/ folder is writable
- [ ] Logs are created successfully

### ✅ Antivirus Test
- [ ] Windows Defender doesn't block
- [ ] SmartScreen shows warning (expected)
- [ ] "Run anyway" option works

---

## Documentation Review

### ✅ README.md
- [ ] Table of contents is complete
- [ ] All sections are filled out
- [ ] Code examples are correct
- [ ] Screenshots/images are included (if applicable)
- [ ] Contact information is current
- [ ] Version number is correct

### ✅ QUICK_START.txt
- [ ] First-time setup is clear
- [ ] Quick workflow is accurate
- [ ] Keyboard shortcuts are correct
- [ ] File paths match actual structure

---

## Distribution Package

### ✅ ZIP Archive
- [ ] ZIP file is created with date: `HavenControlRoom_User_YYYYMMDD.zip`
- [ ] ZIP extracts correctly
- [ ] All files are present
- [ ] Folder structure is intact
- [ ] ZIP size is reasonable (~50-200MB)

### ✅ Checksums (Optional)
- [ ] Generate SHA256 checksum
- [ ] Include in release notes
- [ ] Users can verify integrity

---

## Release Preparation

### ✅ Version Information
- [ ] Update version in README
- [ ] Update version in QUICK_START
- [ ] Update version in application title (if applicable)
- [ ] Update changelog/release notes

### ✅ Release Notes
Create release notes with:
- [ ] Version number
- [ ] Release date
- [ ] New features
- [ ] Bug fixes
- [ ] Known issues
- [ ] Installation instructions
- [ ] Download links

### ✅ Upload Locations
Determine where to host:
- [ ] Google Drive / Dropbox
- [ ] GitHub Releases
- [ ] Discord file share
- [ ] Community website
- [ ] Other: _______________

---

## User Communication

### ✅ Announcement
Prepare announcement with:
- [ ] What is Haven Control Room
- [ ] What's new in this version
- [ ] How to download
- [ ] How to get started
- [ ] Where to get help
- [ ] Call for contributions

### ✅ Support Channels
Set up support:
- [ ] Discord channel ready
- [ ] Email address monitored
- [ ] FAQ document prepared
- [ ] Video tutorial (optional)

---

## Post-Release

### ✅ Monitor Initial Feedback
- [ ] Watch for common issues
- [ ] Respond to user questions
- [ ] Update documentation if needed
- [ ] Prepare hotfix if critical bugs found

### ✅ Track Usage
- [ ] Number of downloads
- [ ] User feedback
- [ ] Bug reports
- [ ] Feature requests

### ✅ Plan Updates
- [ ] Schedule next release
- [ ] Prioritize bug fixes
- [ ] Evaluate new features
- [ ] Improve documentation

---

## Final Sign-Off

### Before releasing to users:

**Build Quality:**
- [ ] All tests passed
- [ ] No critical bugs
- [ ] Performance is acceptable
- [ ] Documentation is complete

**Ready for Distribution:**
- [ ] ZIP file is ready
- [ ] Upload location confirmed
- [ ] Announcement drafted
- [ ] Support channels ready

**Authorized Release:**
- [ ] Reviewed by: _______________
- [ ] Date: _______________
- [ ] Approved: Yes / No

---

## Quick Commands Reference

### Build
```batch
build_user_exe.bat
```

### Test Fresh Install
```batch
# Extract to test folder
cd test_folder
HavenControlRoom.exe
```

### Generate Checksums
```batch
certutil -hashfile HavenControlRoom_User_20251105.zip SHA256
```

### Package for Upload
```batch
# Already done by build script
# ZIP is in: dist\HavenControlRoom_User_YYYYMMDD.zip
```

---

## Emergency Procedures

### If Critical Bug Found After Release

1. **Immediate Actions:**
   - [ ] Post warning in all channels
   - [ ] Remove download links (if possible)
   - [ ] Document the issue clearly

2. **Fix and Rebuild:**
   - [ ] Identify root cause
   - [ ] Implement fix
   - [ ] Test thoroughly
   - [ ] Rebuild with new version number

3. **Hotfix Release:**
   - [ ] Increment version (e.g., 3.0 → 3.0.1)
   - [ ] Clear release notes explaining fix
   - [ ] Upload new version
   - [ ] Announce hotfix to all users

4. **Post-Mortem:**
   - [ ] Document what went wrong
   - [ ] Update testing procedures
   - [ ] Prevent recurrence

---

## Notes

**Build Date:** _____________

**Build Version:** _____________

**Tested By:** _____________

**Issues Found:**
_____________________________________________
_____________________________________________
_____________________________________________

**Resolution:**
_____________________________________________
_____________________________________________
_____________________________________________

**Final Status:** ✅ APPROVED / ❌ NOT READY

---

*Use this checklist for every release to ensure quality and consistency.*
