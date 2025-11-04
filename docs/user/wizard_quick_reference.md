# Haven System Entry Wizard - Quick Reference Card

## 🚀 Launch
```bash
python src/system_entry_wizard.py
```

---

## 📋 Two-Page Workflow

### **Page 1: System Information**
1. Fill **required** fields: System Name, Region, X, Y, Z
2. Optional: Attributes (freeform descriptors)
3. Edit Mode: Load existing system from dropdown
4. Click **Next ➡**

### **Page 2: Planets & Moons**
1. Click **➕ Add Planet** → Planet editor opens
2. Fill planet fields (only **Name** required)
3. Click **➕ Add Moon** for moons → Moon editor opens
4. Fill moon fields (only **Name** required)
5. Save moon → Returns to planet editor
6. Save planet → Appears in **Upload List**
7. Repeat for more planets
8. Click **💾 Finish & Save** to save entire system

---

## 🔑 Required Fields

| Level | Required | Optional |
|-------|----------|----------|
| **System** | Name, Region, X, Y, Z | Attributes |
| **Planet** | Name | Sentinel, Fauna, Flora, Properties, Materials, Base, Photo, Notes |
| **Moon** | Name | Sentinel, Fauna, Flora, Properties, Materials, Base, Photo, Notes |

---

## 🎨 Upload List Actions

| Button | Action |
|--------|--------|
| **✏️ Edit** | Re-open editor with existing data |
| **✖ Remove** | Delete planet (with confirmation) |

---

## 📸 Photo Picker
1. Click **📂 Choose Photo**
2. Select image file
3. Automatically copied to `photos/` folder
4. Path saved (relative to project root)

---

## ✅ Validation Rules

- ✅ **Unique planet names** within system
- ✅ **Unique moon names** within planet
- ✅ **Numeric coordinates** (X, Y, Z)
- ✅ **No limits** on planets or moons

---

## 🗺️ Map Display

**Map automatically shows:**
- Legacy format: `• Planet Name`
- New format: `• Planet Name (N moons)`

**Generate map:**
```bash
python src/Beta_VH_Map.py
```

---

## ⚠️ Troubleshooting

| Error | Fix |
|-------|-----|
| "System Name is required!" | Fill all required fields on Page 1 |
| "Planet '[name]' already exists!" | Use unique planet names |
| "Invalid coordinates!" | Enter valid numbers for X, Y, Z |
| Duplicate moon name | Use unique moon names within planet |

---

## 💾 Data Location

- **Saved To**: `data/data.json`
- **Backup**: `data/data.json.bak` (auto-created)
- **Photos**: `photos/` folder (auto-copied)
- **Logs**: `logs/gui-YYYY-MM-DD.log`

---

## 🔄 Edit Existing System

1. Launch wizard
2. Page 1 → Dropdown: `(New System)` ▼
3. Select existing system name
4. Form auto-fills
5. Click **Next ➡**
6. Edit planets in upload list
7. Click **💾 Finish & Save**
8. Confirm overwrite: **Yes**

---

## ⌨️ Keyboard Shortcuts

- **Tab**: Move between fields
- **Enter**: Confirm dialogs
- **Esc**: Close editors (no save)

---

## 📊 Example Data Structure

```json
{
  "name": "ZENITH PRIME",
  "region": "Core Worlds",
  "x": 100.5, "y": -42.3, "z": 15.0,
  "planets": [
    {
      "name": "Terra Prime",
      "sentinel": "Low",
      "fauna": "8",
      "moons": [
        {
          "name": "Luna",
          "sentinel": "None"
        }
      ]
    }
  ]
}
```

---

## 🆘 Support

- **User Guide**: `docs/system_entry_wizard_guide.md`
- **Tests**: `python tests/test_wizard_validation.py`
- **Schema**: `data/data.schema.json`
- **Logs**: Check `logs/` directory

---

## ✨ Pro Tips

1. **Batch Entry**: Add multiple systems in one session
2. **N/A for Unknown**: Use "N/A" for missing data (not blank)
3. **Edit Mode**: Load → Modify → Save (faster than manual JSON)
4. **Backup**: Automatic backup created on every save
5. **Unique Names**: Enforce at save time (prevents duplicates)

---

**Version 2.0.0** | **Ready for Production** | **100% Backward Compatible**

🚀 **Happy Exploring!**
