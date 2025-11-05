# 📁 Haven Starmap - Root Organization Structure

**Last Updated:** November 4, 2025  
**Status:** ✅ Clean & Organized

---

## 📂 Root Directory Structure

```
Haven_Mdev/
│
├── 🚀 MAIN ENTRY POINTS (Root Level)
│   ├── Haven Control Room.bat          ← Windows launcher (Primary)
│   ├── haven_control_room_mac.command  ← macOS launcher (Primary)
│   ├── README.md                       ← Master documentation
│   ├── setup.py                        ← Python package setup
│   ├── pyproject.toml                  ← Project configuration
│   ├── pytest.ini                      ← Test configuration
│   └── conftest.py                     ← Pytest fixtures
│
├── 📚 Source Code
│   ├── src/                            ← Main application source
│   ├── haven/                          ← Python package
│   ├── config/                         ← Configuration files
│   ├── themes/                         ← UI themes
│   └── static/                         ← Static assets
│
├── 📖 Documentation
│   ├── docs/
│   │   ├── IMPLEMENTATION_SUMMARY.md   ← Complete implementation guide
│   │   ├── SESSION_SUMMARY.md          ← Session overview
│   │   ├── MODULES_QUICK_REFERENCE.md  ← API reference
│   │   ├── QUICK_FIX_INSTRUCTIONS.md   ← Quick fixes
│   │   ├── SESSION_COMPLETE.txt        ← ASCII summary
│   │   ├── analysis/                   ← Analysis documents
│   │   │   ├── INDEX.md
│   │   │   ├── COMPREHENSIVE.md
│   │   │   ├── EXPLORATION_SUMMARY.md
│   │   │   └── IMPROVEMENTS.md
│   │   ├── dev/                        ← Developer guides
│   │   ├── user/                       ← User guides
│   │   └── testing/                    ← Testing documentation
│
├── 🛠️ Scripts & Tools
│   ├── scripts/
│   │   ├── Create Control Room Shortcut.ps1
│   │   ├── First Run Setup.ps1
│   │   ├── Hide Legacy Launchers.ps1
│   │   ├── haven_control_room_windows.bat (Legacy)
│   │   ├── haven_control_room_mac_legacy.command (Legacy)
│   │   ├── haven_control_room_legacy.pyw (Legacy)
│   │   ├── build_map_mac.command
│   │   ├── holo_net_update_mac.command
│   │   └── run_haven_mac.command
│   └── serve_map.py                    ← Map server utility
│
├── 📊 Data & Output
│   ├── data/                           ← Application data files
│   ├── dist/                           ← Distribution/export output
│   ├── photos/                         ← User uploaded images
│   ├── logs/                           ← Application logs
│   └── Archive-Dump/                   ← Legacy/archived code
│
├── 🧪 Testing
│   └── tests/
│       ├── unit/                       ← Unit tests
│       ├── integration/                ← Integration tests
│       ├── validation/                 ← Validation tests
│       └── stress_testing/             ← Performance tests
│
├── 🎨 Themes & Styling
│   ├── themes/
│   │   └── haven_theme.json            ← Dark mode theme
│   └── static/                         ← CSS/JS files
│
└── ⚙️ Configuration
    ├── config/
    │   ├── requirements.txt             ← Python dependencies
    │   ├── data_schema.json             ← Data validation schema
    │   ├── HavenControlRoom.spec        ← PyInstaller config
    │   ├── pyinstaller/                 ← PyInstaller configs
    │   └── icons/                       ← Application icons
    ├── .github/                         ← GitHub workflows
    └── .gitignore                       ← Git ignore rules
```

---

## 🎯 Key Improvements

### What Changed

#### **Before Cleanup:**
- 🔴 Multiple launcher files scattered in root
- 🔴 Documentation files mixed at root level
- 🔴 Confusing file organization
- 🔴 Duplicates between root and scripts

#### **After Cleanup:**
- ✅ **Clean root with only essential files**
- ✅ **Main launchers visible (Windows & macOS)**
- ✅ **README front-and-center**
- ✅ **All documentation organized in docs/**
- ✅ **Legacy files clearly labeled**
- ✅ **Scripts folder organized by purpose**
- ✅ **Clear structure for new users**

### Root Files Explained

| File | Purpose | Priority |
|------|---------|----------|
| `Haven Control Room.bat` | Windows launcher | 🔴 Primary |
| `haven_control_room_mac.command` | macOS launcher | 🔴 Primary |
| `README.md` | Master documentation | 🔴 Primary |
| `setup.py` | Python package setup | 🟡 Important |
| `pyproject.toml` | Project metadata | 🟡 Important |
| `pytest.ini` | Test configuration | 🟡 Important |
| `conftest.py` | Pytest fixtures | 🟡 Important |
| `serve_map.py` | Utility script | 🟢 Utility |

---

## 📂 Documentation Organization

### In `/docs`

**Top Level (Quick Access):**
- `IMPLEMENTATION_SUMMARY.md` - Full implementation details
- `SESSION_SUMMARY.md` - Session overview
- `MODULES_QUICK_REFERENCE.md` - API documentation
- `QUICK_FIX_INSTRUCTIONS.md` - Common fixes
- `SESSION_COMPLETE.txt` - ASCII summary

**Analysis Subdirectory** (`/analysis`):
- `INDEX.md` - Analysis index
- `COMPREHENSIVE.md` - Full project analysis
- `EXPLORATION_SUMMARY.md` - Exploration findings
- `IMPROVEMENTS.md` - Improvement recommendations

**Category Subdirectories:**
- `/dev/` - Developer guides
- `/user/` - User documentation
- `/testing/` - Testing guides

---

## 🛠️ Scripts Organization

### In `/scripts`

**Setup & Configuration:**
- `Create Control Room Shortcut.ps1` - Create desktop shortcuts
- `First Run Setup.ps1` - Initial setup script
- `Hide Legacy Launchers.ps1` - Hide old launchers

**Utilities:**
- `build_map_mac.command` - Build map on macOS
- `holo_net_update_mac.command` - Update utility (macOS)
- `run_haven_mac.command` - Run app (macOS)

**Legacy (Archived):**
- `haven_control_room_windows.bat` - Old Windows launcher
- `haven_control_room_mac_legacy.command` - Old macOS launcher
- `haven_control_room_legacy.pyw` - Old Python launcher

---

## 👥 File Access Patterns

### For Users
```
📍 ROOT
  ├── README.md                    ← Start here!
  ├── Haven Control Room.bat       ← Run on Windows
  └── haven_control_room_mac.command ← Run on macOS
```

### For Developers
```
📍 ROOT
  ├── src/                         ← Edit source code
  ├── tests/                       ← Write tests
  ├── setup.py                     ← Package config
  ├── pytest.ini                   ← Test config
  └── conftest.py                  ← Test fixtures
```

### For Documentation
```
📍 docs/
  ├── IMPLEMENTATION_SUMMARY.md    ← How it works
  ├── MODULES_QUICK_REFERENCE.md   ← API docs
  └── analysis/                    ← Analysis reports
```

---

## 🚀 Getting Started (New Users)

1. **Start Here:** Read `README.md` in root
2. **Run Application:**
   - Windows: Double-click `Haven Control Room.bat`
   - macOS: Double-click `haven_control_room_mac.command`
3. **Learn More:** See `docs/IMPLEMENTATION_SUMMARY.md`
4. **API Reference:** See `docs/MODULES_QUICK_REFERENCE.md`

---

## 🔧 Development Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/Parker1920/Haven_mdev.git
   cd Haven_mdev
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # macOS/Linux
   ```

3. **Install Dependencies**
   ```bash
   pip install -r config/requirements.txt
   pip install -e ".[dev]"
   ```

4. **Run Tests**
   ```bash
   pytest -v
   ```

5. **Run Application**
   ```bash
   python src/control_room.py
   ```

---

## 📝 File Naming Conventions

### Launcher Files
- **Primary:** `Haven Control Room.bat`, `haven_control_room_mac.command`
- **Legacy:** `*_legacy.*` or `*_old.*`
- **Utility:** `build_*.command`, `run_*.command`

### Documentation
- **Analysis:** `docs/analysis/*.md`
- **Implementation:** `docs/IMPLEMENTATION_*.md`
- **User Guides:** `docs/*.md` (root level)

### Source Code
- **Application:** `src/control_room.py`, `src/system_entry_wizard.py`
- **Package:** `haven/` (main package)
- **Models:** `src/models/`
- **Controllers:** `src/controllers/`
- **Common:** `src/common/`

---

## ✨ Benefits of This Organization

1. **🎯 Clear Entry Points** - Main launchers immediately visible
2. **📚 Organized Documentation** - Easy to find what you need
3. **🧹 Clean Root** - No clutter, professional appearance
4. **🔄 Legacy Support** - Old files clearly marked
5. **👥 User Friendly** - Easy for new users to navigate
6. **👨‍💻 Developer Friendly** - Proper package structure
7. **📈 Scalable** - Room for growth and new files

---

## 🔗 Quick Links

| Resource | Location |
|----------|----------|
| Master README | `README.md` |
| Implementation Guide | `docs/IMPLEMENTATION_SUMMARY.md` |
| API Reference | `docs/MODULES_QUICK_REFERENCE.md` |
| Project Analysis | `docs/analysis/COMPREHENSIVE.md` |
| Quick Fixes | `docs/QUICK_FIX_INSTRUCTIONS.md` |
| Test Framework | `pytest.ini` + `conftest.py` |

---

**Status:** ✅ Organized & Ready  
**Last Updated:** November 4, 2025  
**Maintained By:** Haven Development Team
