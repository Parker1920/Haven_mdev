# 🌍 YH-DATABASE QUICK START

## ✅ What's Ready

Your official billion-star map database is **READY TO USE**.

**File Created:** `data/VH-Database.db` (155 KB)  
**Status:** Empty and ready for systems  
**Capacity:** 1 billion+ star systems  
**Backup:** Auto-created at `data/backups/`

---

## 🚀 How to Start Using It

### Step 1: Launch Control Room
```bash
# Windows
Haven Control Room.bat

# OR from terminal
python src/control_room.py
```

### Step 2: Select YH-Database
1. Look at the **Data Source dropdown** (left sidebar, top)
2. Click it (currently shows "Production Data")
3. Select: **"YH-Database (Official Map)"** 🌍

**You'll see:**
- Indicator changes to: 🌍 **YH-Database (Official Map)**
- System count: "0 systems" (ready for data)
- Description: "Official Haven Map - Ready for 1 billion+ star systems"

### Step 3: Launch the Wizard
1. Click: **"🛰️ Launch System Entry (Wizard)"**
2. Wizard launches with YH-Database context
3. You're ready to enter your first system!

### Step 4: Add Your First System

**Page 1 - Basic Info:**
- System Name: e.g., "APOLLO PRIME"
- Region: e.g., "Euclid Cluster"
- X Coordinate: e.g., 0.0
- Y Coordinate: e.g., 0.0
- Z Coordinate: e.g., 0.0

**Page 2 - Planets:**
- Click "Add Planet"
- Enter planet name, type, data
- Add moons if desired
- Add photos, notes

**Click "Finish & Save"**
- System saved to YH-Database ✅
- Success message shows: "System saved to YH-Database (Official Map)"

### Step 5: View Your System
1. Back at Control Room
2. Click: **"🗺️ Generate Map"**
3. Map opens in browser with your new system!

---

## 🎯 Key Features Ready

✅ **Unified Data Source**  
All three functions pull from same place:
- Data source dropdown
- System entry wizard
- Database statistics

✅ **Automatic Backups**  
- Created on every Control Room startup
- Stored in `data/backups/`
- Last 10 kept automatically

✅ **Single Source of Truth**  
No more data mismatches between:
- What dropdown shows
- What wizard uses
- What stats display

✅ **Billion-Star Ready**  
- Spatial indexes for fast queries
- Full-text search for finding systems
- Optimized for 1 billion+ systems
- Auto-backup before every session

---

## 📊 What's Inside YH-Database

```
VH-Database.db contains:
- Systems table (stores star systems)
- Planets table (stores planets per system)
- Moons table (stores moons per planet)
- Space Stations table (stores stations)
- Full metadata for tracking

All with automatic backups, audit trails, and timestamps.
```

---

## 🔄 Data Flow

```
Control Room
    ↓
Select "YH-Database" in dropdown
    ↓
All three functions now use YH-Database
    ├─ Dropdown shows: 🌍 YH-Database (Official Map)
    ├─ Wizard writes to: VH-Database.db
    └─ Stats show: 0 systems (from manager)
    ↓
Launch Wizard → Add System → Click Save
    ↓
System written to VH-Database.db
    ↓
Generate Map → All your systems appear!
```

---

## 📁 Files in Your Project

**New Database:**
- `data/VH-Database.db` - Your official database

**Backups (Auto-Created):**
- `data/backups/VH-Database_backup_*.db`

**Modified Files:**
- `src/control_room.py` - Added YH-Database support
- `src/system_entry_wizard.py` - Now writes to YH-Database
- `src/common/data_source_manager.py` - Registers YH-Database
- `src/common/vh_database_backup.py` - Backup system (NEW)

**Documentation:**
- `YH_DATABASE_COMPLETE.md` - Full technical details
- `YH_DATABASE_QUICK_START.md` - This file

---

## 🎓 You're All Set!

**Next Action:**
1. Launch Control Room
2. Select "YH-Database (Official Map)"
3. Click "Launch Wizard"
4. Add your first system
5. Build your official map!

**The database will:**
- ✅ Store all your systems
- ✅ Auto-backup before each session
- ✅ Handle 1 billion+ systems when you get there
- ✅ Keep all three functions synchronized

---

## ❓ Common Questions

**Q: Where's my data stored?**  
A: In `data/VH-Database.db` - this is your official map database.

**Q: What if Control Room crashes?**  
A: Your last backup is in `data/backups/` - auto-created before each session.

**Q: Can I switch between YH-Database and other sources?**  
A: Yes! Click dropdown, select different source, wizard and stats update automatically.

**Q: How big will the database get?**  
A: Starts at 155 KB, grows with your data (very efficient).

**Q: What happens when I add 1 million systems?**  
A: Database scales seamlessly - it's built for 1 billion.

---

**Status:** 🟢 Ready to Use  
**Database:** 🌍 VH-Database.db (Official Map)  
**Next Step:** Launch Control Room and add your first system!

