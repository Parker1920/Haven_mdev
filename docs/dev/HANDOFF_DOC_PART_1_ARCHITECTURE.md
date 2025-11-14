# Haven_mdev Handoff Documentation - Part 1: Architecture & Overview

**Created**: November 10, 2025  
**Purpose**: Complete AI handoff documentation for Claude to review, debug, and streamline the Haven project  
**Target**: Three-tier system (Master/User Edition EXE/Mobile PWA) currently in testing phase with test data

---

## 1. PROJECT OVERVIEW

### Mission Statement
Haven is a No Man's Sky community-powered star cataloging system with three implementations:
- **Master Edition** (`Haven_mdev/`) - Development hub with database backend
- **User Edition EXE** - Windows executable for standalone community members to catalog systems
- **Mobile Explorer PWA** - Web app for iOS/Android to view and manage discoveries

### Current Status (November 10, 2025)
- **Master Edition**: Active development, Phase 2-4 database integration complete, 20+ critical bugs identified in improvements roadmap
- **User Edition EXE**: Closer to beta, map display fixed, template bundling complete
- **Mobile PWA**: Standalone HTML fully functional, offline-capable, 54.5 KB single file
- **Discord Bot**: Terminal-based, connected to private "Voyagers Haven" server, Act I-III story system complete
- **Data Status**: Test data only, no real NMS systems cataloged yet

### Architecture Pattern: Multi-Tier with Loose Coupling
```
User Edition EXE (JSON-only, Windows)
        ↓
   Manual Export/Import (JSON)
        ↓
Master Edition (Dual JSON/SQLite, Development)
        ↓
   Manual Export/Import (JSON)
        ↓
Haven Mobile Explorer PWA (LocalStorage, iOS/Android)
```

---

## 2. THREE-TIER SYSTEM ARCHITECTURE

### Tier 1: Master Edition (Haven_mdev/)
**Purpose**: Development, data processing, map generation, Discord integration  
**Technology Stack**:
- Python 3.10+ with CustomTkinter 5.2+ GUI
- SQLite3 database (VH-Database.db) for billion-scale storage
- Discord.py 2.3.0+ for bot integration
- Three.js r128 for 3D star map visualization
- Pandas 2.0+ for data processing

**Key Features**:
- Dual-backend data provider (JSON for < 10K systems, SQLite for 1B+)
- Atomic operations on data.json (with rollback protection planned)
- VH-Database backup system (auto-backup on startup, keeps 10 backups)
- Progress dialogs and real-time feedback
- Map generator producing 2000+ pre-rendered system HTML files

**Configuration**: `config/settings.py` with `USE_DATABASE=True`

### Tier 2: User Edition (Windows EXE)
**Purpose**: Standalone application for community members to catalog systems  
**Technology Stack**:
- Python 3.10+ bundled with PyInstaller 6.0+ (Windows-only)
- CustomTkinter for identical UI experience
- JSON-only data backend (no database)
- Three.js for 3D visualization
- Base64 photo encoding for portability

**Key Features**:
- Self-contained executable with all dependencies bundled
- Portable data directory (`files/` in EXE folder)
- Map generation with Three.js rendering
- Photo upload with preview and base64 encoding
- No database complexity - pure JSON workflow

**Configuration**: `config/settings_user.py` with `USE_DATABASE=False`  
**Build Process**: PyInstaller spec at `config/HavenControlRoom.spec` with UPX compression

### Tier 3: Haven Mobile Explorer (PWA)
**Purpose**: iOS/Android web app for viewing and managing discoveries  
**File**: `dist/Haven_Mobile_Explorer.html` (54.5 KB, self-contained)

**Technology Stack**:
- Standalone HTML file (single source of truth, 1936 lines)
- Three.js r128 for 3D galaxy rendering (via CDN)
- LocalStorage API for browser persistence (5-10 MB limit)
- Camera integration (iOS PWA capability via getUserMedia)
- Service Worker for offline support (HTTPS only)

**Key Features**:
- Four-tab interface: System Entry (🛰️), 3D Map (🗺️), Activity Logs (📋), Export/Import (📤)
- Camera integration for photo capture on iOS/Android
- Base64 photo encoding (2 MB limit per image)
- 60 FPS Three.js rendering with touch controls
- Auto-saves to LocalStorage on every action
- Pinch-to-zoom, swipe-to-rotate, tap for system details
- Manual JSON export/import for data sync with Master/EXE
- Timestamps for all activity
- No installation required (browser native or "Add to Home Screen")

**Installation**:
- iOS: Safari → Share → "Add to Home Screen" → Appears as native app
- Android: Chrome → Menu → "Add to Home Screen" → Appears as native app
- Fallback: Use in any browser without installing

**Offline Capability**: Full functionality after first visit (LocalStorage persists)

---

## 3. CORE DATA ARCHITECTURE

### Data Provider Abstraction Layer
**Purpose**: Unified interface allowing seamless switching between JSON and database backends

```
Application Code (Control Room, Wizard, Map Generator)
        ↓
DataProvider Protocol (Interface definition)
        ↓
        ├─ JSONDataProvider (JSON file operations)
        └─ DatabaseDataProvider (SQLite operations)
        ↓
DataSourceManager (Single source of truth)
        ↓
Filesystem / SQLite Database
```

**Four Registered Data Sources**:
1. `production` - Primary data.json file
2. `testing` - Test data for development
3. `load_test` - Large dataset for performance testing
4. `yh_database` - VH-Database.db for billion-scale

**Key Principle**: Single call to `DataSourceManager.get_current()` provides active source to all components

### Data Model: System → Planets → Moons → Space Stations

**System Structure** (JSON):
```json
{
  "_meta": {
    "version": "1.0",
    "last_updated": "2025-11-10",
    "source": "Haven Community"
  },
  "NEXUS-PRIME": {
    "id": "system-uuid",
    "name": "NEXUS-PRIME",
    "region": "Euclid",
    "x": 2048.5,
    "y": 1024.3,
    "z": 512.1,
    "star_type": "F-class",
    "planets": [
      {
        "id": "planet-uuid",
        "name": "Primary",
        "type": "Terrestrial",
        "biome": "Lush",
        "moons": [
          {
            "id": "moon-uuid",
            "name": "Orbital Body",
            "type": "Rocky"
          }
        ]
      }
    ]
  }
}
```

**Database Schema** (SQLite - VH-Database.db):
```
TABLES:
- systems (id, name, region, x, y, z, star_type, created_at, updated_at)
- planets (id, system_id, name, type, biome, created_at)
- moons (id, planet_id, name, type, created_at)
- space_stations (id, system_id, name, category, created_at)
- _metadata (key, value) - schema version, last update

INDEXES:
- Spatial indexes on (x, y, z) for "find nearby" queries
- FTS5 full-text search on name columns
- Foreign keys enforce referential integrity
```

### Data Validation: Schema and Validation Module
- **Schema File**: `data/data.schema.json` defines JSON structure requirements
- **Validation**: Required fields (id, name, region, x, y, z), allows additional properties
- **Enforcement**: ModernEntry widgets validate numeric ranges and required fields before save

---

## 4. CONFIGURATION SYSTEM

### Master Edition Settings (`config/settings.py`)
```python
USE_DATABASE = True                    # Enable SQLite backend
AUTO_DETECT_BACKEND = False            # Manual source selection
PAGINATION_ENABLED = True              # Auto-enable above 100 systems
SHOW_BACKEND_STATUS = True             # Display current backend in UI
SHOW_SYSTEM_COUNT = True               # Display system counts
ENABLE_DATABASE_STATS = True           # Show database statistics
```

### User Edition Settings (`config/settings_user.py`)
```python
USE_DATABASE = False                   # Force JSON-only mode
IS_FROZEN = True                       # Assume EXE context
IS_USER_EDITION = True                 # Portable data directory
ENABLE_JSON_IMPORT = True              # Allow data sync
ENABLE_PROGRESSIVE_MAPS = False        # Don't auto-generate all maps
```

### Path Management (`src/common/paths.py`)
**Key Detection Logic**:
- `FROZEN = getattr(sys, 'frozen', False)` - Detects PyInstaller bundle
- `IS_USER_EDITION = os.getenv('IS_USER_EDITION')` - Environment-based edition selection
- Conditional paths based on context:
  - User EXE: `/files/` subdirectory in EXE folder
  - Master: Project root paths
  - Frozen vs unfrozen handled automatically

**Helper Functions**:
- `project_root()` - Base directory
- `data_dir()` - Data storage directory
- `data_path(name)` - Specific file path
- `dist_dir()` - Generated map output
- `logs_dir()` - Log file storage
- `photos_dir()` - User uploaded images

---

## 5. DATABASE SYSTEM (VH-Database.db)

### Purpose & Capacity
- Billion-scale system storage (1B+ systems, 5B+ planets, 10B+ moons, 500M+ space stations)
- Official map backend for Master edition
- Automatic backup with 10-backup retention policy
- Supports spatial and full-text search

### Initialization on Startup
```
Control Room Launch
    ↓
VH-Database Backup Check
    ↓
If exists: backup_vh_database() creates timestamped copy
    ↓
cleanup_old_backups(keep_count=10) removes oldest
    ↓
DataSourceManager registers 'yh_database' source
    ↓
Database ready for operations
```

### Schema Components
**Spatial Indexing**: (x, y, z) coordinates indexed for "find systems within radius X" queries  
**Full-Text Search**: FTS5 indexes on system_name, planet_name for fast searching  
**Referential Integrity**: Foreign keys ensure planets reference valid systems, moons reference valid planets  
**Metadata Table**: Stores schema version and last update timestamp

### Known Issues (Improvements Roadmap)
- [ ] Transactions not properly wrapped (partial writes possible)
- [ ] No atomic operation guarantees
- [ ] Need connection pooling for concurrent access
- [ ] Cascade delete rules need verification

---

## 6. DISCORD BOT INTEGRATION

### The Keeper Bot
**Purpose**: Community engagement in "Voyagers Haven" Discord server  
**Architecture**: Terminal-based standalone process, reads Master data files

### Story System: Act I → Act II → Act III
**Act I: Discovery Phase**
- New members receive introduction via DM or channel
- Invited to submit system discoveries
- Track total discoveries in database

**Act II: Pattern Recognition**
- Once 3+ discoveries submitted (configurable: MIN_DISCOVERIES_FOR_PATTERN=3)
- Bot analyzes data for patterns
- Announces pattern detections to community

**Act III: Archive System**
- Aggregated findings stored in keeper_db.py
- Historical record of all discoveries
- Community-curated astronomical knowledge

### Database: keeper_db.py
**Tables**:
- `discoveries` - User submissions with metadata
- `patterns` - Detected patterns from analysis
- `pattern_discoveries` - Link discoveries to patterns
- `investigations` - Long-term research projects
- `story_progression` - Act completion and thresholds
- `user_stats` - Per-user discovery/pattern counts

**Key Methods**:
- `get_story_progression()` - Current act and completion %
- `complete_act()` - Automatic transition when thresholds met
- `increment_story_stats()` - Track discoveries per user

### Integration: haven_integration.py
**Data Sources** (priority order):
1. `HAVEN_DATA_PATH` environment variable
2. `keeper_test_data.json` (test data)
3. `data.json` from Master edition
4. Cross-platform path detection (Windows/Mac/Linux)

**Operations**:
- `get_all_systems()` - Loads all systems from data file
- `get_planets_in_system()` - Extracts planets and moons
- `find_systems_near()` - Spatial search within radius

### Configuration: .env.example
```
GUILD_ID=<Voyagers Haven server ID>
BOT_TOKEN=<Discord bot token>
DISCOVERY_CHANNEL_ID=<channel for discoveries>
ARCHIVE_CHANNEL_ID=<channel for archived findings>
INVESTIGATION_CHANNEL_ID=<channel for research>
MIN_DISCOVERIES_FOR_PATTERN=3
AUTO_PATTERN_THRESHOLD=0.75
```

---

## 7. PHASE SYSTEM & INTEGRATION MILESTONES

### Phase 2: Control Room Database Integration
- **Status**: ✅ Complete
- **Implementation**: `src/control_room.py` lines 100-200
- **Features**:
  - VH-Database backup on startup
  - DataSourceManager integration
  - Backend status display in UI
  - System count caching

### Phase 3: Wizard Database Integration
- **Status**: ✅ Complete
- **Implementation**: `src/system_entry_wizard.py` save_system() method
- **Features**:
  - Dual-mode JSON and database writing
  - Atomic file operations (with rollback protection planned)
  - Planet/moon hierarchical saving
  - Backward compatibility with legacy data formats

### Phase 4: Map Generator Database Integration
- **Status**: ✅ Complete
- **Implementation**: `src/Beta_VH_Map.py` load_systems() method
- **Features**:
  - DataProvider abstraction for JSON or DB
  - Pandas DataFrame processing
  - Three.js template rendering
  - 2000+ pre-generated system HTML files

### Phase 5+: Planned Improvements
- Atomic write operations with full rollback
- Database transaction wrapping
- Memory optimization in map generator
- Exception recovery dialogs
- User edition cloud sync (planned)

---

## 8. FILE INVENTORY BY COMPONENT

### Core Application Files
| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `src/control_room.py` | 1577 | Main GUI dashboard, exports, packaging | Active Development |
| `src/system_entry_wizard.py` | 1334 | Two-page wizard for system/planet/moon entry | Production Ready |
| `src/Beta_VH_Map.py` | 671 | 3D map generator with Three.js | Phase 4 Complete |
| `src/generate_ios_pwa.py` | TBD | iOS PWA HTML generation | Legacy (Superseded) |

### Common Utilities
| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `src/common/paths.py` | 300+ | Path management for frozen/unfrozen, user/master | Production Ready |
| `src/common/database.py` | 746 | SQLite wrapper with CRUD operations | Production Ready |
| `src/common/data_provider.py` | 478 | Abstraction layer for JSON/DB backends | Production Ready |
| `src/common/data_source_manager.py` | 406 | Single source of truth managing 4 data sources | Production Ready |
| `src/common/validation.py` | TBD | Form validation and data integrity | Active |
| `src/common/logging_config.py` | TBD | Rotating file logger configuration | Active |

### Configuration Files
| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `config/settings.py` | 254 | Master edition configuration | Active |
| `config/settings_user.py` | 251 | User edition configuration | Active |
| `config/requirements.txt` | TBD | Python dependencies | Active |
| `config/HavenControlRoom.spec` | 35 | PyInstaller Windows build spec | Active |
| `config/pyproject.toml` | TBD | Project metadata | Active |

### Data Files
| File | Purpose | Status |
|------|---------|--------|
| `data/data.json` | Primary system data (JSON format) | Active (Empty Template) |
| `data/data.schema.json` | JSON schema validation | Active |
| `data/VH-Database.db` | Billion-scale SQLite database | Active (Empty Shell) |
| `data/keeper_test_data.json` | Test data for bot development | Active |

### Discord Bot Files
| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `docs/guides/Haven-lore/keeper-bot/src/main.py` | 252 | Bot entry point, cog loading, activity | Complete |
| `docs/guides/Haven-lore/keeper-bot/src/core/keeper_personality.py` | TBD | Embed creation, voice/tone system | Complete |
| `docs/guides/Haven-lore/keeper-bot/src/core/haven_integration.py` | 316 | Data loading, spatial search | Complete |
| `docs/guides/Haven-lore/keeper-bot/src/database/keeper_db.py` | 789 | Story progression, discovery tracking | Complete |

### Mobile PWA
| File | Size | Purpose | Status |
|------|------|---------|--------|
| `dist/Haven_Mobile_Explorer.html` | 54.5 KB | Standalone PWA with Four-tab interface | Production Ready |

### Generated Artifacts
| Directory | Contents | Purpose | Status |
|-----------|----------|---------|--------|
| `dist/` | 2000+ system HTML files | Pre-rendered 3D maps | Generated by Beta_VH_Map.py |
| `photos/` | User uploaded images | Referenced in system entries | Managed by Wizard |
| `logs/` | Rotating log files | Application diagnostics | Active |
| `build/` | PyInstaller output | Windows EXE assembly | Generated by build script |

---

## 9. BUILD & DEPLOYMENT PROCESS

### Master Edition (Development)
```bash
# Setup
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
.venv\Scripts\Activate.ps1          # Windows PowerShell

# Install
pip install -r config/requirements.txt

# Run
python src/control_room.py

# Run Wizard standalone
python src/system_entry_wizard.py

# Generate map headless
python src/Beta_VH_Map.py --no-open

# Run tests
pytest -q tests/
```

### User Edition (Windows EXE)
```bash
# Build
pyinstaller config/HavenControlRoom.spec

# Run from build output
.\build\HavenControlRoom_User\HavenControlRoom.exe
```

**PyInstaller Configuration** (`config/HavenControlRoom.spec`):
- Single-file bundle with UPX compression
- Hidden imports for database, pandas, discord
- Data files bundled: clean_data.json, example_data.json, themes/
- Console disabled for GUI mode

### Mobile Explorer (PWA)
```bash
# Generate from template (if rebuilding)
python src/generate_ios_pwa.py

# Deploy
1. Copy Haven-mobile-explorer.html to web server
2. Or serve locally with: python -m http.server 8000
3. Access via: https://your-domain/Haven-mobile-explorer.html

# Add to Home Screen (iOS)
1. Safari: Share → Add to Home Screen
2. Names as "Haven Explorer"
3. Appears as native app in home screen
```

---

## 10. KNOWN ISSUES & CRITICAL IMPROVEMENTS

### From MASTER_PROGRAM_IMPROVEMENTS.md (20 Critical Fixes)

**Tier 1: Data Integrity (CRITICAL)**
- [ ] **Atomic File Writing**: Currently lack rollback protection on wizard saves. Crash during write = data loss.
- [ ] **Database Transactions**: Operations not wrapped in transactions. Partial writes possible on crash.
- [ ] **File Lock Mechanism**: Concurrent access to data.json can cause corruption.

**Tier 2: User Experience**
- [ ] **Exception Recovery Dialogs**: Crashes don't provide recovery options
- [ ] **Progress Dialog Blocking**: Long operations freeze UI
- [ ] **Memory Leaks**: DataFrame processing in map generator leaks memory on large datasets

**Tier 3: Performance**
- [ ] **Pagination Performance**: Slow on 10K+ systems without proper indexing
- [ ] **Map Generation**: 2000+ HTML files take too long to generate
- [ ] **Database Connection Pooling**: Missing for concurrent operations

**Tier 4: Compatibility**
- [ ] **Legacy Data Migration**: Heuristics sometimes fail on older formats
- [ ] **Cross-Platform Paths**: Some edge cases on macOS with special characters
- [ ] **Photo Encoding**: Base64 limits image file sizes

---

## 11. RECENT IMPROVEMENTS (November 8, 2025)

### Completed Implementations
✅ **User Edition Map Display Fix** - Updated data loading to use user-specific paths, verified 3D visualization  
✅ **Act I Story System** - Added story_progression table, /story-intro and /story-progress commands  
✅ **VH-Database Integration** - Created backup system, integrated into DataSourceManager  
✅ **Mobile PWA Complete** - Self-contained HTML with Three.js, camera integration, offline capability  
✅ **Template Bundling** - PyInstaller spec updated to include clean_data.json and example_data.json  

### Documentation Created
- `MAP_FIX_COMPLETE.md` - User edition map display resolution
- `ACT_I_IMPLEMENTATION_COMPLETE.md` - Discord bot story system
- `YH_DATABASE_COMPLETE.md` - Database backup and integration
- `HAVEN_MOBILE_COMPLETE_SUMMARY.md` - Haven Mobile Explorer final status (1936 lines)
- `VERIFICATION_COMPLETE.md` - Testing and validation results

---

## 12. NEXT STEPS FOR CLAUDE

### Phase 1: Code Review & Bug Fixes
1. Review the 20 critical improvements from Tier 1-4
2. Prioritize data integrity fixes (atomic writes, transactions, file locks)
3. Test rollback scenarios with intentional crashes
4. Validate all three tiers (Master/EXE/Mobile) function together

### Phase 2: Streamlining & Refactoring
1. Eliminate dead code and unused imports
2. Consolidate duplicate functionality
3. Ensure DataSourceManager is the single source of truth
4. Verify all components see each other correctly

### Phase 3: Production Readiness
1. Complete atomic write operations
2. Add exception recovery dialogs
3. Optimize memory usage in map generator
4. Document final architecture for community handoff

### Phase 4: Real Data Preparation
1. Verify data flow between Master ↔ EXE ↔ Mobile
2. Test with larger datasets (1K+ systems)
3. Prepare for production NMS data collection
4. Create user documentation and deployment guide

---

**Document Status**: Part 1 of 3 (Architecture & Overview - Complete)  
**Next**: Part 2 - Codebase Details & Data Flows  
**Then**: Part 3 - Operations & Troubleshooting
