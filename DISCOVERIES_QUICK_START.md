# Quick Start: Making Discoveries Appear on the Haven Map

## TL;DR - 3 Steps

1. **In Discord**: Type `/haven-export` and hit Enter
2. **In Haven Control Room**: Click the "Generate Map" button
3. **On the Map**: Your discovery now appears as a colored marker! Click it for details.

---

## Why This Is Needed

The Discord bot stores discoveries in its own database. The Haven map reads from the Haven database. The `/haven-export` command connects them.

---

## Visual Guide

### Step 1: Export Discoveries from Discord
```
Type this in any Discord channel:
/haven-export

(Leave all options blank if you want to export ALL discoveries)

Bot will respond with:
✅ "Exported 5 discoveries to Haven database"
```

### Step 2: Regenerate the Map
**Option A - Use Control Room UI:**
1. Open Haven Control Room
2. Click "GENERATE MAP" button
3. Wait for confirmation

**Option B - Run Directly:**
```bash
python src/Beta_VH_Map.py
```

### Step 3: View on Map
1. Open the generated map (dist/VH-Map.html)
2. Discoveries appear as colored tetrahedra
3. Click any to see details in the info panel

---

## What You'll See

Each discovery appears as a **glowing tetrahedron** near its location:

- 🟡 **Tan** = Bones
- 🟠 **Orange** = Ruins
- 🔵 **Cyan** = Technology
- 🟢 **Green** = Flora
- 🩷 **Pink** = Fauna
- 🔴 **Red** = Energy signals
- 🟣 **Purple** = Radio signals

**Click any marker** → See full discovery details:
- Type and description
- Who found it
- When it was found
- Condition and significance
- Mystery tier rating

---

## Troubleshooting

**If `/haven-export` returns an error:**
- Make sure you're typing it exactly: `/haven-export`
- Ensure the bot is online
- Check bot logs for database errors

**If discoveries still don't appear after `/haven-export`:**
1. Check that VH-Database.db exists in the `data/` folder
2. Make sure bot has write permissions to the database file
3. Try regenerating the map again: `python src/Beta_VH_Map.py`

**If map doesn't load:**
1. Ensure map HTML was created: check `dist/VH-Map.html` exists
2. Open it in a modern web browser (Chrome, Firefox, Safari, Edge)
3. Check browser console (F12) for JavaScript errors

---

## That's It!

Once you run `/haven-export` and regenerate the map, all your discoveries will be visible. The system is now fully integrated!
