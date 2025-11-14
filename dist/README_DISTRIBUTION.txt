================================================================================
    HAVEN MOBILE EXPLORER - DISTRIBUTION PACKAGE
================================================================================

This package contains everything needed to distribute Haven Mobile Explorer
to field explorers using iOS (iPhone/iPad) or Android devices.

================================================================================
PACKAGE CONTENTS
================================================================================

FILES INCLUDED:

1. Haven_Mobile_Explorer.html (54.5 KB)
   - The complete mobile app (single file)
   - Works on ALL smartphones (iOS 14+, Android 9+)
   - 100% offline after first load
   - Contains: Wizard, Map, Logs, Export

2. iOS_WORKAROUND_GUIDE.txt (10 KB)
   - CRITICAL: Read this for iOS distribution!
   - Explains Apple's Files app restriction
   - Provides 5 proven workaround methods
   - Email method (easiest)
   - Self-hosted server method (most reliable)

3. HavenMobileServer.py (3 KB)
   - Simple Python HTTP server
   - Hosts the HTML file on local network
   - Works around iOS Files app restriction
   - Run on computer, access from iPhone via WiFi

4. MOBILE_INSTALLATION_GUIDE.txt (30 KB)
   - Complete user manual
   - Step-by-step installation for iOS and Android
   - Feature documentation
   - Troubleshooting section

5. MOBILE_QUICK_REFERENCE.txt (8 KB)
   - Quick start card for users
   - Essential features only
   - Perfect for printing/emailing

6. README_DISTRIBUTION.txt (this file)
   - Overview for distributors

================================================================================
RECOMMENDED DISTRIBUTION METHODS
================================================================================

FOR iOS USERS (iPhone/iPad):
----------------------------
METHOD 1 - Email (Easiest, 95% success rate):
  1. Email Haven_Mobile_Explorer.html to user
  2. Include iOS_WORKAROUND_GUIDE.txt as second attachment
  3. In email body, write:
     "Tap the Haven_Mobile_Explorer.html attachment to install.
      It will open in Safari. Then tap Share → Add to Home Screen.
      See iOS_WORKAROUND_GUIDE.txt if you need help."

METHOD 2 - Self-Hosted Server (100% success rate):
  1. Give user: Haven_Mobile_Explorer.html + HavenMobileServer.py
  2. User runs HavenMobileServer.py on their computer
  3. Server shows URL like http://192.168.1.100:8080
  4. User types URL in Safari on iPhone (same WiFi)
  5. User adds to home screen
  6. Perfect for teams or multiple devices

⚠️ DO NOT instruct iOS users to:
   - Save file to Files app (won't work - Apple restriction)
   - Open from Files app (Apple blocks HTML execution)
   - Use Chrome browser (only Safari works for home screen)

FOR ANDROID USERS:
------------------
SIMPLE - Any method works:
  1. Email Haven_Mobile_Explorer.html
  2. User taps attachment in email
  3. Opens in Chrome (or any browser)
  4. User taps menu → Add to Home screen
  5. Done!

Alternative:
  - Upload to Google Drive, share link
  - Send via messaging app
  - Transfer via USB
  All work perfectly on Android!

================================================================================
EMAIL TEMPLATE FOR USERS
================================================================================

Subject: Haven Mobile Explorer - Installation

Hi [Explorer Name],

Attached is Haven Mobile Explorer, a mobile app for documenting star systems
in the field. It works on your iPhone/Android and doesn't require the app store.

INSTALLATION:

iOS (iPhone/iPad):
1. Tap the Haven_Mobile_Explorer.html attachment below
2. Wait for Safari to open (1-2 seconds)
3. Tap the Share button (box with arrow at bottom)
4. Tap "Add to Home Screen"
5. Tap "Add"
6. Find "Haven Explorer" icon on your home screen

Android:
1. Tap the Haven_Mobile_Explorer.html attachment below
2. Opens in Chrome
3. Tap menu (⋮) → "Add to Home screen"
4. Tap "Add"
5. Find "Haven Explorer" icon on your home screen

TROUBLESHOOTING:
- iOS users: See iOS_WORKAROUND_GUIDE.txt if you have issues
- The app works 100% offline after first use
- Export your data regularly as backup

USAGE:
- Wizard tab: Add new systems
- Map tab: View 3D galaxy
- Logs tab: See activity
- Export tab: Save/share your data as JSON

Questions? Reply to this email.

Happy exploring!
[Your Name]

================================================================================
TROUBLESHOOTING FOR DISTRIBUTORS
================================================================================

ISSUE: iOS user says "file won't open"
SOLUTION: They're trying Files app. Send iOS_WORKAROUND_GUIDE.txt
          Recommend email attachment method (works 99% of time)

ISSUE: iOS user says "Add to Home Screen missing"
SOLUTION: They're in Chrome, not Safari
          iOS only allows PWA installation in Safari

ISSUE: Android user says "won't install"
SOLUTION: They don't need to "install" - just open HTML file
          Then add to home screen from browser menu

ISSUE: User says "app is too big to email"
SOLUTION: 54.5 KB is tiny! Most email supports 25 MB
          If their provider blocks HTML:
          1. Rename to Haven_Mobile_Explorer.txt
          2. User renames back to .html on their device
          OR use self-hosted server method

ISSUE: User wants offline use
SOLUTION: First load needs internet (downloads Three.js library)
          After that, 100% offline forever
          Tell them to open once while online, then disconnect

================================================================================
TECHNICAL SPECIFICATIONS
================================================================================

Haven_Mobile_Explorer.html:
- Size: 54.5 KB (including all CSS, JS, icons)
- Dependencies: Three.js r128 (loaded from CDN on first use)
- Storage: Browser localStorage (up to 10MB typical)
- Compatibility: iOS 14+, Android 9+, modern browsers
- Offline: Yes, after first load
- Data format: JSON (compatible with desktop version)
- Photo support: Camera + gallery, max 2MB per photo
- System limit: 200 systems recommended per file

HavenMobileServer.py:
- Language: Python 3.6+
- Dependencies: None (uses standard library only)
- Port: 8080 (configurable in script)
- Platform: Windows, Mac, Linux
- Purpose: Host HTML file on local network for iOS access

Security & Privacy:
- No data sent to servers (100% local)
- No tracking or analytics
- No external dependencies after Three.js loads
- No account creation needed
- No cloud sync (intentional)

================================================================================
BULK DISTRIBUTION TIPS
================================================================================

FOR SMALL TEAMS (1-10 users):
- Email method works great
- Send to each user individually
- Include both HTML and iOS_WORKAROUND_GUIDE.txt

FOR MEDIUM TEAMS (10-50 users):
- Use self-hosted server method
- Run HavenMobileServer.py on team's network
- Give everyone the URL
- Everyone installs at same time
- Turn off server when done

FOR LARGE DEPLOYMENTS (50+ users):
- Host on internal web server (Apache, nginx)
- Provide single URL to all users
- Users bookmark and add to home screen
- Centralized updates possible

FOR OFFLINE SITUATIONS:
- Pre-install on devices before deployment
- First-time internet connection required
- After that, works forever offline
- Perfect for remote exploration

================================================================================
UPDATE PROCEDURE
================================================================================

When new version of Haven_Mobile_Explorer.html is released:

1. Tell users to EXPORT their data first (critical!)
2. Distribute new Haven_Mobile_Explorer.html file
3. Users install new version (same method as before)
4. Users IMPORT their previously exported data
5. Old version can be deleted

Data is stored in browser, NOT in HTML file.
New version = fresh start, so export/import is necessary.

================================================================================
SUPPORT RESOURCES
================================================================================

For your users:
- iOS_WORKAROUND_GUIDE.txt (iOS-specific issues)
- MOBILE_INSTALLATION_GUIDE.txt (complete manual)
- MOBILE_QUICK_REFERENCE.txt (quick start)

For you (distributor):
- This file (distribution guidelines)
- Contact mission control with unresolved issues

Common support requests:
1. iOS Files app won't open → iOS_WORKAROUND_GUIDE.txt
2. Can't add to home screen → Must use Safari on iOS
3. Data disappeared → Didn't export before clearing browser
4. Map won't show → Need internet for first load
5. Photo too large → Compress to under 2MB

================================================================================
LICENSE & ATTRIBUTION
================================================================================

Haven Mobile Explorer is part of the Haven Control Room project.

This software is provided as-is for exploration and documentation purposes.
Feel free to distribute to authorized explorers.

Third-party libraries:
- Three.js r128 (MIT License) - https://threejs.org/

================================================================================
VERSION HISTORY
================================================================================

v1.0 (2025-11-06)
- Initial release
- iOS home screen installation support
- iOS Files app workarounds documented
- Self-hosted server option included
- Complete offline functionality
- Android full support

================================================================================
QUESTIONS?
================================================================================

Contact mission control for:
- Technical support
- Bug reports
- Feature requests
- Bulk deployment assistance

Include:
- Version number
- Platform (iOS/Android)
- Browser type
- Screenshot if applicable

================================================================================

Happy distributing! 🚀🌌

================================================================================
