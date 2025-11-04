# Haven System Entry Wizard - User Guide

## Overview

The **System Entry Wizard** is a two-page interface for adding complete star systems with full planet and moon data to the Haven starmap database.

### What's New?

- **Two-Page Workflow**: System information (Page 1) → Planets builder (Page 2)
- **Rich Planet/Moon Data**: Each planet/moon includes sentinel, fauna, flora, properties, materials, base location, photo, and notes
- **Nested Moons**: Each planet can have multiple moons with full data
- **Upload List**: Visual panel showing all planets with moon counts
- **Edit Mode**: Load and modify existing systems
- **Backward Compatible**: Works with existing data format

---

## Getting Started

### Launch the Wizard

```bash
python src/system_entry_wizard.py
```

The wizard opens with **Page 1: System Information**.

---

## Page 1: System Information

### Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| **System Name** | Unique identifier for the system | `ZENITH PRIME` |
| **Region** | Galactic region containing the system | `Core Worlds` |
| **X, Y, Z Coordinates** | 3D position in galaxy space | `100.5, -42.3, 15.0` |

### Attributes (Optional)

Provide a single, flexible field for any custom descriptors you want the star system to be known for.

| Field | Description | Example |
|-------|-------------|---------|
| **Attributes** | Freeform tags/notes | `Trade hub; Rare resources; Pirate activity` |

### Edit Mode

**Load Existing System:**
1. Click the dropdown at the top: `(New System)` ▼
2. Select an existing system name
3. Form auto-fills with existing data
4. Planets appear in upload list (Page 2)
5. Make changes and save to overwrite

### Navigation

- Click **Next ➡** to proceed to Page 2 (validates required fields)
- System data is saved internally; you can return to Page 1 with **⬅ Back**

---

## Page 2: Planets & Moons

### Adding a Planet

1. Click **➕ Add Planet**
2. Planet editor dialog opens

#### Planet Editor Fields

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| **Name** | ✅ Yes | Planet identifier | `Terra Prime` |
| **Sentinel Level** | No | Security presence | Low, Medium, High, etc. |
| **Fauna** | No | Wildlife count/level | 0-10, Low, Mid, High, N/A |
| **Flora** | No | Vegetation level | None, Low, Mid, High, N/A |
| **Properties** | No | Planet characteristics | `Lush forests, mild climate` |
| **Materials** | No | Harvestable resources | `Gold, Carbon, Oxygen` |
| **Base Location** | No | Coordinates or description | `(+12.34, -56.78)` or `N/A` |
| **Photo** | No | Screenshot path | `photos/terra_prime.jpg` |
| **Notes** | No | Additional observations | `Great for farming` |

**Photo Picker:**
- Click **📂 Choose Photo**
- Select image file (PNG, JPG, JPEG, WebP)
- Photo is automatically copied to `photos/` folder
- Path is saved relative to project root

#### Adding Moons

1. In planet editor, click **➕ Add Moon**
2. Moon editor opens (same fields as planet)
3. Enter moon data and click **💾 Save**
4. Moon appears in planet's moon list
5. Repeat for additional moons

**Moon Management:**
- ✏️ **Edit** — Re-open moon editor to modify
- ✖ **Remove** — Delete moon from planet

3. Click **💾 Save** to add planet to upload list

### Upload List Panel

Located on the right side of Page 2, the upload list displays all planets added to the system.

**Planet Card Format:**
```
🪐 Planet Name           🌙 2 moons
[✏️ Edit]  [✖ Remove]
```

**Actions:**
- **✏️ Edit** — Re-open planet editor with existing data
- **✖ Remove** — Delete planet from system (with confirmation)

### Validation Rules

- **Unique Planet Names**: Cannot add duplicate planet names within a system
- **Unique Moon Names**: Cannot add duplicate moon names within a planet
- **No Limits**: Add unlimited planets per system, unlimited moons per planet

### Navigation

- **⬅ Back** — Return to Page 1 (planets retained)
- **💾 Finish & Save** — Save entire system with all planets/moons

---

## Saving the System

### Save Process

1. Click **💾 Finish & Save** on Page 2
2. Wizard validates coordinates
3. Checks for duplicate system name:
   - **New System**: Adds to database
   - **Duplicate Found**: Prompts to overwrite
4. Creates backup (`data.json.bak`)
5. Saves system with:
   - All system-level fields
   - Planets as rich objects with all fields
   - Moons nested within planets
   - Legacy `planets_names` array for compatibility
6. Success message shows planet count
7. Form clears and returns to Page 1

### Data Structure

**Saved Format (data.json):**
```json
{
  "_meta": {"version": "2.0.0"},
  "data": [
    {
      "id": "SYS_CORE_WORLDS_1234567890",
      "name": "ZENITH PRIME",
      "region": "Core Worlds",
      "x": 100.5,
      "y": -42.3,
      "z": 15.0,
      "sentinel": "Low",
      "fauna": "Mid",
      "flora": "High",
      "properties": "Trade hub, 3 stations",
      "materials": "Activated Indium, Gold",
      "base_location": "Station Alpha",
      "notes": "Discovered 2024-03-15",
      "planets": [
        {
          "name": "Terra Prime",
          "sentinel": "Low",
          "fauna": "8",
          "flora": "High",
          "properties": "Lush forests, mild climate",
          "materials": "Gold, Carbon, Oxygen",
          "base_location": "(+12.34, -56.78)",
          "photo": "photos/terra_prime.jpg",
          "notes": "Great for farming",
          "moons": [
            {
              "name": "Luna",
              "sentinel": "None",
              "fauna": "0",
              "flora": "None",
              "properties": "Barren rock",
              "materials": "Iron, Copper",
              "base_location": "N/A",
              "photo": "N/A",
              "notes": "Mining outpost"
            }
          ]
        }
      ],
      "planets_names": ["Terra Prime"]
    }
  ]
}
```

**Legacy Compatibility:**
- `planets_names` array ensures old map code continues working
- New code reads `planets` objects for rich data
- Both formats coexist in same file

---

## Map Integration

### How the Map Displays Planets

**Beta_VH_Map.py** automatically detects and renders both formats:

**Legacy Format (String Array):**
```
Planets:
• Terra Prime
• Oceanus
```

**New Format (Object Array with Moons):**
```
Planets:
• Terra Prime (2 moons)
• Oceanus (1 moon)
• Vulcan (no moons)
```

**Info Panel:**
- Click any system in the map
- Planet list appears with moon counts
- Photo links work for system-level photos
- Future: Clickable planets to view moon details

---

## Example Workflow

### Scenario: Adding a Complete Star System

**Goal:** Add the "HAVEN NEXUS" system in the "Outer Rim" region with 3 planets:
1. **Haven Core** (capital planet, 2 moons)
2. **Haven Beta** (mining world, 1 moon)
3. **Haven Gamma** (research station, no moons)

#### Step-by-Step

**Page 1: System Information**

1. Launch wizard: `python src/system_entry_wizard.py`
2. Fill required fields:
   - System Name: `HAVEN NEXUS`
   - Region: `Outer Rim`
   - X: `250.0`, Y: `-100.0`, Z: `50.0`
3. Attributes (optional): `Capital system; 3 habitable planets; Main hub`
4. Click **Next ➡**

**Page 2: Add First Planet (Haven Core)**

5. Click **➕ Add Planet**
6. Planet editor opens:
   - Name: `Haven Core` ✅
   - Sentinel Level: `Low`
   - Fauna: `10`
   - Flora: `High`
   - Properties: `Urban centers, lush wilderness`
   - Materials: `Gold, Silver, Platinum`
   - Base Location: `Capital City (+45.12, -23.67)`
   - Click **📂 Choose Photo** → Select `haven_core.jpg`
   - Notes: `Population center, primary settlement`
7. In "Moons" section, click **➕ Add Moon**:
   - Moon #1:
     - Name: `Core Alpha`
     - Sentinel Level: `None`
     - Fauna: `2`
     - Flora: `Low`
     - Properties: `Small research outpost`
     - Materials: `Iron, Copper`
     - Notes: `Orbital research station`
   - Click **💾 Save**
8. Click **➕ Add Moon** again:
   - Moon #2:
     - Name: `Core Beta`
     - Sentinel Level: `None`
     - Fauna: `0`
     - Flora: `None`
     - Properties: `Barren rock`
     - Materials: `Uranium, Emeril`
     - Notes: `Mining operations`
   - Click **💾 Save**
9. Click **💾 Save** (planet editor)
10. Upload list shows: **🪐 Haven Core** 🌙 **2 moons**

**Add Second Planet (Haven Beta)**

11. Click **➕ Add Planet**
12. Planet editor:
    - Name: `Haven Beta`
    - Sentinel Level: `Medium`
    - Fauna: `5`
    - Flora: `Mid`
    - Properties: `Rocky terrain, mining operations`
    - Materials: `Activated Indium, Gold, Silver`
    - Base Location: `Mining Hub Sigma`
    - Notes: `Primary mining world`
13. Add Moon:
    - Name: `Beta Moon`
    - Properties: `Ore deposits`
    - Materials: `Iron, Copper, Gold`
14. Click **💾 Save** (planet and moon)
15. Upload list shows:
    - **🪐 Haven Core** 🌙 **2 moons**
    - **🪐 Haven Beta** 🌙 **1 moon**

**Add Third Planet (Haven Gamma)**

16. Click **➕ Add Planet**
17. Planet editor:
    - Name: `Haven Gamma`
    - Sentinel Level: `Low`
    - Fauna: `1`
    - Flora: `None`
    - Properties: `Frozen ice world, research station`
    - Materials: `Oxygen, Nitrogen, Carbon`
    - Base Location: `Research Dome Gamma`
    - Notes: `Scientific outpost, extreme cold`
18. No moons (skip moon section)
19. Click **💾 Save**
20. Upload list shows:
    - **🪐 Haven Core** 🌙 **2 moons**
    - **🪐 Haven Beta** 🌙 **1 moon**
    - **🪐 Haven Gamma**

**Save the System**

21. Click **💾 Finish & Save**
22. Success message: "System 'HAVEN NEXUS' saved with 3 planet(s)!"
23. Form clears, ready for next system

**View in Map**

24. Run: `python src/Beta_VH_Map.py`
25. Click "Outer Rim" region
26. Click "HAVEN NEXUS" system
27. Info panel displays:
    ```
    HAVEN NEXUS
    Region: Outer Rim
    Coordinates: (250.0, -100.0, 50.0)
    Sentinel: Medium
    Fauna: Mid
    Flora: High
    Properties: Capital system, 3 habitable planets
    Notes: Main hub for Outer Rim exploration
    
    Planets:
    • Haven Core (2 moons)
    • Haven Beta (1 moon)
    • Haven Gamma
    ```

---

## Editing an Existing System

### Modify System

1. Launch wizard
2. Page 1 → Click dropdown: `(New System)` ▼
3. Select **HAVEN NEXUS**
4. Form auto-fills with system data
5. Click **Next ➡**
6. Upload list shows all 3 planets with moon counts
7. Click **✏️ Edit** on "Haven Beta"
8. Change fauna from `5` to `7`
9. Add second moon:
   - Name: `Beta Moon 2`
   - Properties: `Gas deposits`
10. Click **💾 Save**
11. Upload list updates: **🪐 Haven Beta** 🌙 **2 moons**
12. Click **💾 Finish & Save**
13. Confirm overwrite: **Yes**
14. System updated with new data

### Remove Planet

1. Load system in edit mode
2. Page 2 → Click **✖ Remove** on unwanted planet
3. Confirm deletion: **Yes**
4. Planet removed from upload list
5. Click **💾 Finish & Save** to persist changes

---

## Troubleshooting

### Common Issues

**Problem: "System Name is required!"**
- **Cause**: Page 1 missing required field
- **Fix**: Fill System Name, Region, and all three coordinates

**Problem: "Planet '[name]' already exists!"**
- **Cause**: Duplicate planet name within system
- **Fix**: Use unique names for each planet

**Problem: "Invalid coordinates!"**
- **Cause**: Non-numeric coordinate values
- **Fix**: Enter valid numbers (integers or decimals)

**Problem: Moon editor shows planet fields**
- **Expected**: Moon editor has same fields as planet (except moons section)
- **Fix**: This is by design; moons have full data like planets

**Problem: Photo doesn't appear in map**
- **Cause**: System-level photos only (planet photos not yet in map)
- **Fix**: Add photo at system level (Page 1) for map display

---

## Tips & Best Practices

### Organization

- **Consistent Naming**: Use clear, descriptive planet/moon names
- **N/A for Unknown**: Use "N/A" for fields without data (not blank)
- **Coordinates Format**: Base locations can be coordinates `(+12.34, -56.78)` or names `North Pole Base`

### Performance

- **No Limits**: Add as many planets/moons as needed
- **Backup Created**: Every save creates `data.json.bak`
- **Validation**: Wizard prevents duplicate names and invalid data

### Workflow Efficiency

1. **Batch Systems**: Add multiple systems in one session
2. **Edit Mode**: Load → Modify → Save (faster than manual JSON editing)
3. **Photo Picker**: Auto-copies photos to correct folder
4. **Upload List**: Visual verification before saving

---

## Keyboard Navigation

- **Tab**: Move between fields
- **Enter**: Confirm dialogs
- **Esc**: Close editors (no save)

---

## Data Schema Reference

### Planet/Moon Object Schema

```json
{
  "name": "string (required)",
  "sentinel": "string (default: N/A)",
  "fauna": "string (default: N/A)",
  "flora": "string (default: N/A)",
  "properties": "string (default: N/A)",
  "materials": "string (default: N/A)",
  "base_location": "string (default: N/A)",
  "photo": "string (default: N/A)",
  "notes": "string (default: N/A)",
  "moons": ["array of moon objects (planets only)"]
}
```

### System Schema

```json
{
  "id": "string (auto-generated)",
  "name": "string (required)",
  "region": "string (required)",
  "x": "number (required)",
  "y": "number (required)",
  "z": "number (required)",
  "sentinel": "string (default: N/A)",
  "fauna": "string (default: N/A)",
  "flora": "string (default: N/A)",
  "properties": "string (default: N/A)",
  "materials": "string (default: N/A)",
  "base_location": "string (default: N/A)",
  "photo": "string (default: N/A)",
  "notes": "string (default: N/A)",
  "planets": ["array of planet objects"],
  "planets_names": ["array of planet name strings (legacy)"]
}
```

---

## Version History

### v2.0.0 (Current)
- Two-page wizard interface
- Rich planet/moon data with nested structure
- Upload list with Edit/Remove functionality
- Edit mode for existing systems
- Photo picker with auto-copy
- Backward compatible with v1.x data

### v1.0.0 (Phase 1)
- Single-page system entry
- Planets as string array
- Real-time validation
- Draft autosave
- Theme system
- Schema-driven help

---

## Support

For issues or feature requests, check:
- `logs/` directory for error logs
- `data.json.bak` for backup recovery
- `data/data.schema.json` for validation rules

---

## Next Steps

After mastering the wizard:
1. **Explore the Map**: View your systems in 3D (`python src/Beta_VH_Map.py`)
2. **Export Data**: Share `data.json` with team members
3. **Advanced Editing**: Modify JSON directly for bulk operations
4. **Custom Themes**: Edit `themes/haven_theme.json` for personalized colors

---

**Happy Exploring! 🚀**
