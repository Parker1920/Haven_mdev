# Haven System Entry - User Guide

**Version:** 2.0  
**Last Updated:** November 2, 2025

---

## Table of Contents
1. [Getting Started](#getting-started)
2. [Interface Overview](#interface-overview)
3. [Adding a New System](#adding-a-new-system)
4. [Field Reference](#field-reference)
5. [Advanced Features](#advanced-features)
6. [Keyboard Shortcuts](#keyboard-shortcuts)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Launching System Entry

**From Control Room:**
1. Open Haven Control Room
2. Click "System Entry" button
3. The System Entry window will open

**Standalone:**
```bash
python src/system_entry_modern.py
```

### First Time Setup

On first launch, the app will:
- Load existing systems from `data/data.json`
- Apply your saved theme (if any)
- Show the main entry form

---

## Interface Overview

The System Entry interface has three main sections:

### 1. Left Sidebar (Actions)
- **💾 Save System** - Save current entry to data.json
- **⚙️ Manage Fields** - Add/remove custom fields
- **🔄 Clear Form** - Reset all fields
- **🛠️ Settings** - Change theme (Dark/Light/Cosmic/Haven)
- **Auto-regenerate map** - Toggle automatic map refresh after save
- **Large text (A11y)** - Accessibility font scaling
- **Statistics** - Shows current region/system count

### 2. Center Form (Scrollable)
Main data entry area with organized cards:
- 📝 Basic Information
- 🎯 Coordinates
- 🛰️ Environment & Conditions
- 🪐 Planets
- 🔮 Properties
- ⚗️ Resources & Materials
- 🏠 Base & Photo
- ✨ Custom Fields (if any)

### 3. Right Panel (Help)
Contextual help that updates when you focus on a field:
- Field-specific guidance
- Schema validation rules
- Example values
- Keyboard shortcuts reference

---

## Adding a New System

### Step-by-Step Example

Let's add a system called "ZENITH PRIME" in the "Core" region:

#### 1. Basic Information
```
System Name: ZENITH PRIME
Region: Core
```
- **System Name** is the display name (required)
- **Region** groups systems on the galaxy map (required)

#### 2. Coordinates
```
X: 5.2
Y: -3.8
Z: 1.0
```
- Enter numeric values (decimals allowed)
- **Validation:** Red border appears if non-numeric
- Press Tab to move between fields

#### 3. Environment & Conditions
Use the dropdowns to select:
```
Sentinel Level: Medium
Fauna: 5
Flora: High
```
- Choose the closest match from dropdown
- Select "N/A" if unknown

#### 4. Planets
Add planets one at a time:
1. Type planet name: "Zenith Alpha"
2. Click "➕ Add Planet" or press Enter
3. Planet appears as a chip below
4. Click ✖ on chip to remove

Example:
```
Planets: [Zenith Alpha] [Zenith Beta] [Zenith Gamma]
```

#### 5. Properties
Freeform text for notable features:
```
Properties: Trade hub with 3 space stations. Excellent mineral deposits. Popular waypoint for travelers.
```

#### 6. Resources & Materials
List important resources:
```
Materials: Activated Indium, Gold, Silver, Chromatic Metal
```

#### 7. Base & Photo

**Base Location:**
```
Base Location: Zenith Alpha (+12.34, -56.78)
```
Format: `PlanetName (longitude, latitude)` or "N/A"

**Photo:**
1. Click "📂 Choose from photos/" to pick existing image
2. Or click "🖼️ Browse…" to select from anywhere
   - File will auto-copy to `photos/` folder
   - Relative path saved automatically

#### 8. Save
- Click "💾 Save System" or press Ctrl+S
- Success animation appears
- Form clears automatically
- Map regenerates (if enabled)

---

## Field Reference

### Required Fields (marked with *)
| Field | Type | Format | Example |
|-------|------|--------|---------|
| System Name | Text | Any | ZENITH PRIME |
| Region | Text | Any | Core |
| X Coordinate | Number | Decimal | 5.2 |
| Y Coordinate | Number | Decimal | -3.8 |
| Z Coordinate | Number | Decimal | 1.0 |

### Optional Fields
| Field | Type | Options/Format |
|-------|------|----------------|
| Sentinel Level | Dropdown | None, Low, Medium, High, Aggressive, N/A |
| Fauna | Dropdown | None, Low, Mid, High, 0-10, N/A |
| Flora | Dropdown | None, Low, Mid, High, N/A |
| Planets | List | Free text, multiple entries |
| Properties | Text | Free text |
| Materials | Text | Comma-separated recommended |
| Base Location | Text | Format: `Planet (coords)` or N/A |
| Photo | File | PNG/JPG/WEBP, auto-copied to photos/ |

### Custom Fields
Add your own fields via "⚙️ Manage Fields":
- Click "Add Field" tab
- Enter field name (e.g., "Population", "Tech Level")
- Field appears in "✨ Custom Fields" card
- Values persist across all systems

---

## Advanced Features

### Validation System

**Real-time Validation:**
- Coordinates validate on every keypress
- Invalid entries show:
  - Red border around field
  - Inline error message below
  - Example: "Enter a valid number (e.g., 42 or -13.5)"

**Pre-Save Validation:**
- Save button checks all required fields
- Blocks save if validation fails
- Shows error dialog listing problems

### Draft Autosave

**How it works:**
- Every 30 seconds, form state saved to `data/.draft_system.json`
- Includes: all fields, planets list, photo path
- Draft deleted after successful save

**Restore Draft:**
- On next launch, prompt appears: "A draft system entry was found. Would you like to restore it?"
- Click "Yes" to restore all fields
- Click "No" to discard draft

### Undo/Redo

**Undo (Ctrl+Z):**
- Reverts form to previous state
- Multiple levels supported
- Stack cleared after save

**Redo (Ctrl+Y):**
- Reapplies undone changes
- Only available after undo

### Theme Switching

**Available Themes:**
1. **Dark** - Default dark mode
2. **Light** - Light background
3. **Cosmic** - Green accent theme
4. **Haven (Cyan)** - Sci-fi cyan theme (recommended)

**To Change:**
1. Click "🛠️ Settings"
2. Select theme radio button
3. Theme applies immediately
4. Some elements update on next launch

### Photo Management

**Workflow:**
1. Click "📂 Choose from photos/" - browse `photos/` folder only
2. Or "🖼️ Browse…" - select from anywhere
   - App copies file to `photos/` folder
   - Handles name collisions (adds `_1`, `_2`, etc.)
   - Stores relative path: `photos/filename.png`

**Supported Formats:**
- PNG (recommended)
- JPG/JPEG
- WEBP

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Ctrl+S** | Save current system |
| **Ctrl+Z** | Undo last change |
| **Ctrl+Y** | Redo undone change |
| **Ctrl+N** | Clear form (new entry) |
| **Tab** | Navigate to next field |
| **Shift+Tab** | Navigate to previous field |
| **Enter** | Add planet (when planet input focused) |
| **Esc** | Close dialogs |

---

## Troubleshooting

### Common Issues

**Problem: "Coordinates must be valid numbers"**
- **Cause:** Non-numeric input in X, Y, or Z field
- **Fix:** Enter only numbers and decimal points (e.g., `5.2`, `-3`, `0`)

**Problem: Save button does nothing**
- **Cause:** Validation errors present
- **Fix:** Look for red borders, fix invalid fields
- Check System Name and Region are not empty

**Problem: Draft not restoring**
- **Cause:** Draft file missing or corrupt
- **Fix:** Draft only saved if you had unsaved changes; start fresh entry

**Problem: Photo not appearing in map**
- **Cause:** Photo path incorrect or file moved
- **Fix:** Use "Browse…" button to let app copy file; don't manually edit paths

**Problem: Custom field disappeared**
- **Cause:** Field removed via Manage Fields
- **Fix:** Re-add field in "⚙️ Manage Fields" → "Add Field" tab

**Problem: Theme not applying**
- **Cause:** Some elements require restart
- **Fix:** Close and reopen System Entry app

### Data Location

**System data:** `data/data.json`  
**Draft file:** `data/.draft_system.json`  
**Photos:** `photos/` (relative to project root)  
**Logs:** `logs/gui-YYYY-MM-DD.log`  
**Settings:** `settings.json` (project root)

### Backup & Recovery

**Manual Backup:**
```bash
# Backup data
copy data\data.json data\data.json.backup

# Backup photos
xcopy photos photos_backup /E /I
```

**Restore from Backup:**
- App automatically creates `.bak` file on each save
- Located at: `data/data.json.bak`

---

## Tips & Best Practices

### Data Entry Tips
1. **Be Consistent:** Use same naming conventions (e.g., always "N/A", not "n/a" or "N.A.")
2. **Use Decimals:** Coordinates can be precise (e.g., `1.23`, `-4.56`)
3. **Describe Resources:** In Materials, list primary resources first
4. **Tag Planets:** Use recognizable names for quick reference
5. **Photo Names:** Use descriptive names before adding (e.g., `zenith-station.png`)

### Organization
- **Regions:** Group related systems (by sector, storyline, etc.)
- **Custom Fields:** Add fields like "Discovered Date", "Notes", "Difficulty"
- **Properties:** Include station info, trader presence, missions

### Performance
- **Large Datasets:** App tested with 100+ systems, no lag
- **Photo Size:** Keep images < 5MB for faster loading
- **Auto-regen:** Disable if map generation is slow; manual regen available in Control Room

---

## Examples

### Example 1: Exploration System
```
Name: WANDERER'S REST
Region: Outer Rim
X: 12.5, Y: -8.3, Z: 2.1
Sentinel: None
Fauna: 10
Flora: High
Planets: Haven's Gate, Serenity, Nomad's End
Properties: Peaceful system, ideal for base building. Three lush planets.
Materials: Oxygen, Sodium, Carbon
Base: Haven's Gate (-14.23, +42.67)
Photo: wanderers-rest-portal.png
```

### Example 2: Trading Hub
```
Name: COMMERCE NEXUS
Region: Core
X: 0.0, Y: 0.0, Z: 0.0
Sentinel: Low
Fauna: 2
Flora: None
Planets: Trade Station Alpha
Properties: Major trade hub. 5 stations. High ship traffic. Economy: Trading.
Materials: Chromatic Metal, Platinum, Gold
Base: N/A
Photo: commerce-nexus-station.png
```

### Example 3: Hostile System
```
Name: CRIMSON VOID
Region: Danger Zone
X: -15.7, Y: 6.2, Z: -3.9
Sentinel: Aggressive
Fauna: 0
Flora: None
Planets: Scorched Prime, Ash Beta
Properties: Extreme conditions. High sentinel activity. Valuable deposits.
Materials: Activated Cadmium, Uranium, Storm Crystals
Base: N/A (too dangerous)
Photo: crimson-void-warning.png
```

---

## FAQ

**Q: Can I edit existing systems?**  
A: Yes! Enter the exact same name and region, click Save, and choose "Overwrite" when prompted.

**Q: What happens to old data when I save?**  
A: Automatic backup created as `data.json.bak` before each save.

**Q: Can I add systems to multiple regions?**  
A: Each system belongs to one region, but you can create as many regions as needed.

**Q: How do I delete a system?**  
A: Currently: edit `data/data.json` manually. Delete feature coming in future update.

**Q: Does the map update automatically?**  
A: Yes, if "Auto-regenerate map" is checked. Otherwise, use Control Room → "Generate Map".

**Q: Can I use this on multiple computers?**  
A: Yes! Copy entire project folder. All data is in `data/` and `photos/`.

---

## Support & Feedback

**Issues?** Check `logs/` folder for error details.  
**Feature Requests?** Document in project README or issues tracker.  
**Data Schema:** See `data/data.schema.json` for validation rules.

---

**Version History:**
- v2.0 (Nov 2025): Complete overhaul - validation, autosave, schema hints, Haven theme
- v1.0 (Initial): Basic system entry with custom fields

**Related Documentation:**
- [UX Spec](system_entry_ux_spec.md) - Design decisions and wireframes
- [QA Report](qa_system_entry_report.md) - Testing and validation details
- [Main README](README.md) - Project overview and setup
