# iOS PWA Testing Guide

## What I Fixed

The iOS PWA wasn't loading on iPhone Safari due to several compatibility issues:

### Issues Addressed:
1. **Three.js CDN Loading** - Added `crossorigin="anonymous"` attribute for iOS compatibility
2. **WebGL Renderer Settings** - iOS-friendly settings with performance optimization
3. **Service Worker** - Disabled for now (iOS Safari has strict requirements)
4. **Error Handling** - Comprehensive error messages to diagnose loading issues
5. **Variable Declarations** - Changed `let`/`const` to `var` for older iOS versions
6. **Arrow Functions** - Replaced with regular functions for better compatibility

### Added Diagnostics:
- Loading screen now shows step-by-step progress
- Error messages display on screen (not just console)
- Detailed error info for troubleshooting

## How to Test on iPhone

### Method 1: Email the File
1. Email the generated iOS HTML (e.g., `Haven_Galaxy_iOS.html`) to yourself
2. On iPhone, open the email and tap the attachment
3. If it opens in an in-app preview and stays blank, use the Share button and choose "Open in Safari" or "Save to Files" first, then open from the Files app
4. Avoid opening inside third‑party in‑app browsers (Gmail/Outlook). Always use Safari

### Method 2: Cloud Storage
1. Upload the HTML to iCloud Drive / Dropbox / Google Drive
2. In the Files or cloud app, tap the file and choose "Open in Safari" if prompted
3. If it previews in-app, use the Share button → "Open in Safari"

### Method 3: Local Web Server (Best for Development)
If you have Python installed on your computer:

```powershell
# In the Haven_Mdev directory
cd dist
python -m http.server 8000
```

Then on your iPhone (connected to same WiFi):
1. Find your computer's IP address (run `ipconfig` on Windows)
2. In Safari, go to: `http://YOUR_IP_ADDRESS:8000/Haven_iOS.html`

## What to Look For

### On First Load:
Watch the loading screen - it should show:
- "Loading 3D library..."
- "Loading data..."
- "Checking 3D library..."
- "Initializing 3D map..."
- "Ready!"

### If It Works:
- Loading screen disappears after a few seconds
- You see the Haven Galaxy header
- Map tab shows 3D galaxy view
- Data tab shows entry form

### If It Gets Stuck or Won't Show At All:
**If you see "INITIALIZING..." for more than 10 seconds:**
- The 3D library is taking too long to load
- After 10 seconds, you'll see "ERROR: 3D Library Timeout"
- Two buttons will appear:
  - **"Retry"** - Reload the page and try again (works if connection improved)
  - **"Skip Map, Use Data Entry Only"** - Go straight to the data entry form (works offline!)

### Error Messages:
- **"ERROR: 3D library failed to load"** → Internet connection issue; Three.js CDN blocked
  - **Solution:** Use "Skip Map" button to use data entry without the 3D map
- **"ERROR: 3D Library Timeout"** → CDN is slow or blocked
  - **Solution:** Try "Retry" button or use "Skip Map" button
**If the file never visibly opens (blank preview):**
- Save the file to the Files app first, then open it there so it launches Safari proper
- Ensure you're not viewing inside Gmail/Outlook in‑app browser
- Disable Safari content blockers temporarily and retry

**Offline build check:**
- If you exported the Offline PWA, the HTML file size should be > 300 KB (includes the 3D library)
- If it’s ~50–60 KB, it’s not the offline-embedded file and will still try online CDNs
- **"ERROR: Map container not found"** → HTML structure issue (rare)
- **"ERROR: [other message]"** → Check the detailed error text below the main message

## Troubleshooting

### Three.js Won't Load
- Make sure you have internet connection on first load
- Try reloading the page (pull down to refresh)
- Check if Safari content blockers are enabled (Settings → Safari)
 - We now attempt multiple CDNs automatically (jsDelivr, unpkg, cdnjs). If all fail, use "Skip Map" to continue with data entry only

### Ensure you truly opened in Safari
- In attachment viewers (Mail, Discord, Gmail), use Share → Open in Safari
- Or tap Share → Save to Files → open from the Files app (which launches Safari)

### Black/Blank Screen
- This usually means WebGL is disabled or not supported
- Check Settings → Safari → Advanced → Experimental Features
- Make sure "WebGL" is enabled

### Controls Don't Work
- Make sure you're tapping and not long-pressing
- Try pinch-to-zoom in the map area
- Switch between Map and Data tabs

### Still Not Working?
1. Take a screenshot of the error message
2. Open Safari → Develop → [Your iPhone] → Web Inspector (on Mac)
3. Or share the screenshot - I can diagnose from the error

## Performance Tips

For best performance on iPhone:
- Close other Safari tabs
- Restart Safari if it's been open a long time
- Ensure iOS is up to date (iOS 13+ recommended, iOS 15+ ideal)

## Installing to Home Screen

Once it loads successfully:
1. Tap the Share button (square with arrow)
2. Scroll down and tap "Add to Home Screen"
3. Name it "Haven Galaxy"
4. Tap "Add"

The icon will appear on your home screen and will work offline after first load!

## Skip Map Mode (NEW!)

**If the 3D map won't load, you can still use the app!**

When you see the error screen with "Skip Map, Use Data Entry Only" button:
1. Tap "Skip Map, Use Data Entry Only"
2. The app will load without the 3D map
3. You'll go straight to the Data tab
4. All features work: Add/Edit/Delete systems, Import/Export JSON
5. Local storage still works - your data is saved
6. You can use the app completely offline in this mode

**This is perfect for:**
- Using the app offline after first download
- When internet is slow or CDN is blocked
- If you just want to enter data without viewing the map
- Testing on older iPhones with WebGL issues

## Known iOS Limitations

- First load requires internet (to fetch Three.js library) - OR use "Skip Map" mode
- Older iPhones (iPhone 6s and earlier) may have performance issues - use "Skip Map" mode
- Safari private mode may not persist data between sessions
- Some iOS content blockers may interfere with loading - use "Skip Map" mode

## Need More Help?

If the diagnostic messages don't make sense or you need more help debugging, let me know what message you see and I can provide more specific fixes!
