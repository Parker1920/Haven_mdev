# Haven_mdev Handoff Documentation - Part 2: Codebase Details & Data Flows

**Created**: November 10, 2025  
**Purpose**: In-depth code analysis with function signatures, data flows, and integration points

---

## 1. CONTROL ROOM GUI (src/control_room.py - 1577 lines)

### Class Structure
```python
class ControlRoom(tk.Tk):
    """Main desktop application for Haven Master edition"""
    
    def __init__(self):
        # Initialization sequence:
        # 1. Theme loading from themes/haven_theme.json
        # 2. DataSourceManager initialization
        # 3. VH-Database backup system setup
        # 4. UI component creation
        # 5. Dashboard population with system counts
        
    def _initialize_vh_database_backups(self):
        """Executed on startup"""
        # Calls backup_vh_database()
        # Creates timestamped backup: VH-Database.db.YYYYMMDD_HHMMSS.bak
        # Calls cleanup_old_backups(keep_count=10)
        # Logs results to application logs/
        
    def _build_ui(self):
        """Constructs glassmorphic interface"""
        # Creates GlassCard components with rounded corners
        # Action buttons:
        #   - "Open Wizard" → launches SystemEntryWizard()
        #   - "Generate Map" → calls Beta_VH_Map.main()
        #   - "Export iOS PWA" → calls generate_ios_pwa.main()
        # Status display:
        #   - Current backend (JSON/SQLite)
        #   - System counts from DataSourceManager
        #   - Last update timestamp
        
    def _show_progress_dialog(self, title: str, callback):
        """Non-blocking progress for long operations"""
        # Spawns separate thread for operation
        # Shows progress bar and cancel button
        # Updates status messages from callback
        
    def _export_windows(self):
        """Windows EXE packaging with PyInstaller"""
        # Builds using HavenControlRoom.spec
        # Includes hidden imports:
        #   - customtkinter, PIL, sqlalchemy
        #   - pandas, discord, aiosqlite
        # Bundles data files and themes
        
    def _export_macos(self):
        """macOS app bundle packaging"""
        # Similar to Windows but creates .app bundle
        # Code signing handled separately
```

### Key Integration Points
**DataSourceManager Access**:
```python
manager = DataSourceManager()
current_source = manager.get_current()  # Get active source info
systems_count = current_source.count    # Pre-loaded system count
data_provider = manager.create_provider(current_source)
```

**VH-Database Backup Flow**:
```
Control Room.__init__()
    ↓
_initialize_vh_database_backups()
    ↓
Check: does VH-Database.db exist?
    ├─ YES: backup_vh_database() creates copy
    │         cleanup_old_backups(keep=10) removes oldest
    └─ NO: Skip (first run)
    ↓
DataSourceManager.register('yh_database', path)
    ↓
Ready for operations
```

### UI Components Used
- **GlassCard**: Custom widget with semi-transparent background and border
- **ModernButton**: Styled button with hover effects
- **ProgressDialog**: Non-blocking operation feedback
- **StatusBar**: Displays current state and counts

### Dependencies
- `customtkinter` (GUI framework)
- `PIL` (image handling)
- `common.paths` (path resolution)
- `common.data_source_manager` (DataSourceManager)
- `common.database` (VH-Database backup functions)
- `system_entry_wizard` (Wizard launching)
- `Beta_VH_Map` (Map generation)
- `generate_ios_pwa` (iOS export)

---

## 2. SYSTEM ENTRY WIZARD (src/system_entry_wizard.py - 1334 lines)

### Class Structure
```python
class SystemEntryWizard(tk.Toplevel):
    """Two-page wizard for entering star systems"""
    
    def __init__(self, parent, mode='new', system_data=None):
        # Mode determination: 'new' or 'edit'
        # If 'edit': load_existing_system(system_data)
        # Page 1 setup: System info entry
        # Page 2 setup: Planets and moons editor
        # Next/Back/Save button initialization
        
    @staticmethod
    def get_existing_systems() -> dict:
        """Load all systems from current data provider"""
        # Tries three data shapes in order:
        # 1. Top-level map form: {"SYSTEM-NAME": {...}}
        # 2. Wrapper form: {"systems": {...}}
        # 3. Legacy list: {"data": [...]}
        # Returns unified dict format
        
    def page_1_system_info(self):
        """First page: Basic system details"""
        # ModernEntry fields with validation:
        #   - System Name (required, string)
        #   - Region (required, dropdown or entry)
        #   - Star Type (dropdown: O/B/A/F/G/K/M/etc)
        #   - X coordinate (required, numeric, float)
        #   - Y coordinate (required, numeric, float)
        #   - Z coordinate (required, numeric, float)
        #   - Star Class (optional, string)
        #   - Notes (optional, large text)
        # Validation on "Next":
        #   - Required fields present?
        #   - Coordinates are valid floats?
        
    def page_2_planets_editor(self):
        """Second page: Planets and nested moons"""
        # Dynamic planet list with add/remove buttons
        # For each planet:
        #   - PlanetMoonEditor widget (custom)
        #   - Editable fields: name, type, biome, discovery_notes
        #   - Nested moons list with add/remove
        #   - Photo upload with base64 encoding
        # Validation on "Save":
        #   - At least 1 planet?
        #   - Planet names unique?
        
    def save_system(self):
        """Persist system to data backend"""
        # Creates atomic write operation:
        #   1. Generate new system dict from form data
        #   2. Create backup: data.json → data.json.bak
        #   3. Merge with existing systems
        #   4. Write to data.json
        #   5. If DB enabled: write to VH-Database.db
        # Issues (identified in improvements):
        #   - NO rollback protection (missing try/except)
        #   - NO file lock check for concurrent writes
        #   - Success callback may not fire if crash
        
    def load_existing_system(self, system_name: str):
        """Edit mode: Load system and populate forms"""
        # Fetch from DataProvider.get_system(system_name)
        # Populate Page 1 fields
        # Populate Page 2 planets/moons
        # Mark as edit mode in UI
        
    def _upload_photo(self, planet_name: str):
        """Photo management for planets"""
        # filedialog.askopenfilename() for image
        # Copy to photos/ directory
        # Encode as base64 for JSON embedding
        # Show preview in PhotoPreviewLabel
        # Store reference in planet data
```

### Data Flow: Form → Save → Backend
```
Page 1 fields
├─ system_name_var
├─ region_var
├─ x_coordinate_var
├─ y_coordinate_var
└─ z_coordinate_var

Page 2 fields
└─ planet_editors[0..N]
   ├─ name, type, biome
   └─ moon_editors[0..N]
      └─ name, type

    ↓ [Click Save]

save_system()
├─ Validate all fields
├─ Generate {system_uuid: {...}}
├─ Read data.json
├─ Merge systems
├─ Backup original
├─ Write new data.json
├─ (If DB enabled) Execute INSERT
└─ Show success dialog
```

### Key Validation Methods
```python
def validate_page_1(self) -> bool:
    """Returns False if validation fails"""
    errors = []
    if not self.system_name_var.get():
        errors.append("System name required")
    if not self._validate_coordinate(self.x_coordinate_var.get()):
        errors.append("X coordinate must be numeric")
    # ... similar for Y and Z
    if errors:
        messagebox.showerror("Validation Failed", "\n".join(errors))
        return False
    return True

def _validate_coordinate(self, value: str) -> bool:
    """Check if value is valid float"""
    try:
        float(value)
        return True
    except ValueError:
        return False
```

### Photo Upload Workflow
```
User clicks "Add Photo" on planet card
    ↓
_upload_photo() called
    ↓
File dialog: select PNG/JPG
    ↓
Copy to photos/{filename}
    ↓
Encode to base64
    ↓
Store in planet["photo_base64"]
    ↓
Display preview in PhotoPreviewLabel
    ↓
On save: data.json contains full base64
```

### Dependencies
- `customtkinter` (GUI)
- `PIL` (image preview)
- `filedialog`, `messagebox` (tkinter)
- `common.data_provider` (DataProvider)
- `common.data_source_manager` (DataSourceManager)
- `common.validation` (field validation)
- Custom widgets: `ModernEntry`, `ModernTextbox`, `PlanetMoonEditor`

---

## 3. MAP GENERATOR (src/Beta_VH_Map.py - 671 lines)

### Main Workflow
```python
def main(args=None):
    """Entry point for map generation"""
    # Parse arguments: --no-open (headless), --output (custom path)
    # Load configuration from settings
    # Call generate_map()
    
def generate_map():
    """Core map generation logic"""
    # 1. Load systems from DataProvider
    # 2. Process each system with Pandas DataFrame
    # 3. Normalize data format
    # 4. Render Three.js template for each system
    # 5. Save HTML files to dist/
    # 6. Open in browser (unless --no-open)
    
def load_systems() -> pd.DataFrame:
    """Fetch data from current backend"""
    # manager = DataSourceManager()
    # source = manager.get_current()
    # provider = manager.create_provider(source)
    # Return provider.get_all_systems() as DataFrame
    
def normalize_record(record: dict) -> dict:
    """Standardize system data format"""
    # Ensure all required fields present:
    #   - id, name, region, x, y, z
    # Extract planets list
    # Extract moons from each planet
    # Validate coordinate types (must be numeric)
    # Return normalized dict
```

### Desktop Map Generation vs Mobile Explorer Map
**Desktop** (src/Beta_VH_Map.py):
- Generates 2000+ individual HTML files (one per system)
- Each file: 50-100 KB standalone Three.js viewer
- Naming: `dist/system_REGION-SYSTEM_ID.html`
- Used by: Control Room, EXE, static distribution

**Mobile** (Haven_Mobile_Explorer.html):
- Integrated 3D map viewer in single 54.5 KB HTML file
- Renders all systems at once in galaxy view
- LocalStorage persistence for discovered systems
- Touch controls: pinch zoom, swipe rotate, tap for details
- Camera integration for photo capture
- See Section 3.4 below for mobile-specific details

### Three.js Template Rendering
**Template Location**: `src/templates/map_template.html`

**Template Variables** (Jinja2 style):
```html
<script>
  const systemData = {
    name: "{{ system.name }}",
    region: "{{ system.region }}",
    coordinates: [{{ system.x }}, {{ system.y }}, {{ system.z }}],
    planets: [
      {
        name: "{{ planet.name }}",
        type: "{{ planet.type }}",
        biome: "{{ planet.biome }}",
        moons: [
          {
            name: "{{ moon.name }}",
            type: "{{ moon.type }}"
          }
        ]
      }
    ]
  };
</script>
```

### Generated Output
**File Naming**: `dist/system_[REGION]-[SYSTEM_ID].html`

**Examples**:
- `system_EUCLID-NEXUS_PRIME.html`
- `system_CALYPSO-SYSTEM_01.html`
- 2000+ files generated during testing

**File Contents**:
- Complete standalone HTML (no external dependencies)
- Embedded Three.js library
- Embedded system data as JSON
- CSS for styling
- Event handlers for camera controls

### Camera Controls (Three.js)
```javascript
// Mouse controls
- Orbit: Left mouse drag
- Pan: Right mouse drag
- Zoom: Mouse wheel

// Keyboard controls
- 'R': Reset camera to default position
- 'Space': Auto-rotate toggle
- 'G': Toggle grid helper visibility

// Touch controls (mobile)
- 1 finger drag: Orbit
- 2 finger drag: Pan
- Pinch: Zoom
```

### Data Processing: Pandas Integration
```python
# Load all systems as DataFrame
df = pd.DataFrame(systems)

# Column structure:
# - system_id (unique identifier)
# - system_name (display name)
# - region (galaxy region)
# - x, y, z (coordinates)
# - planet_count (derived)
# - moon_count (derived)

# Filtering operations:
filtered = df[df['region'] == 'Euclid']
nearby = df[
    (df['x'].between(x-100, x+100)) &
    (df['y'].between(y-100, y+100)) &
    (df['z'].between(z-100, z+100))
]
```

### Dependencies
- `customtkinter` (GUI, --no-open flag handling)
- `pandas` (DataFrame processing)
- `pathlib` (file operations)
- `jinja2` (template rendering)
- `common.data_provider` (data loading)
- `common.data_source_manager` (backend selection)
- Template: `src/templates/map_template.html`

---

## 3.4 HAVEN MOBILE EXPLORER (dist/Haven_Mobile_Explorer.html - 1936 lines)

### Purpose
**Single-file Progressive Web App (PWA)** for iOS and Android providing full system exploration, data entry, and 3D visualization. Complete feature parity with Desktop Edition in mobile-optimized interface.

### Architecture (Single HTML File)
```
Haven_Mobile_Explorer.html (54.5 KB)
├── HTML (lines 1-100)
│   └── Meta tags, viewport, app icons
├── CSS (lines 101-600)
│   ├── Design system with CSS variables
│   ├── Component styles (tabs, cards, buttons)
│   └── Touch-optimized spacing and sizing
└── JavaScript (lines 601-1936)
    ├── Tab system management
    ├── System Entry Wizard implementation
    ├── 3D Map Viewer with Three.js
    ├── Activity Logging system
    └── Export/Import functionality
```

### Four Core Tabs (Mobile UI)

**Tab 1: System Entry Wizard (🛰️)**
```javascript
// In Haven_Mobile_Explorer.html
function addSystem() {
    // Form fields:
    // - System Name (required, string)
    // - Region (dropdown: Euclid, Calypso, etc.)
    // - X, Y, Z coordinates (numeric, with validation)
    // - Star Type (optional)
    // - Planets (dynamic add/remove)
    //   - Each planet: name, type, biome
    //   - Each planet can have moons
    // - Photo upload (camera or file)
    
    // On submit:
    // 1. Validate all required fields
    // 2. Generate system UUID
    // 3. Encode photo as base64
    // 4. Save to LocalStorage
    // 5. Add to activity logs
    // 6. Refresh display
}
```

**Tab 2: 3D Map Viewer (🗺️)**
```javascript
// Renders galaxy with all discovered systems
function initMap() {
    // Load systems from LocalStorage
    // Create Three.js scene:
    // - Ambient light (base illumination)
    // - Point light (sun-like)
    // - Systems as glowing spheres (radius = 10 units)
    // - Positioned by coordinates (x, y, z)
    // - Grid helper for reference plane
    // - Glow shader effects
    
    // Touch controls:
    // - Pinch gesture: zoom
    // - Swipe: rotate camera
    // - Long press: system details
    // - Reset button: return to default view
    
    // Auto-rotation option with speed control
    // FPS counter and performance metrics
}
```

**Tab 3: Activity Logs (📋)**
```javascript
// Timestamped log of all user actions
function addLog(action, details) {
    // Log entries:
    // - "System added: NEXUS-PRIME"
    // - "Map generated"
    // - "Data exported"
    // - "Data imported"
    // - "Tab switched to map"
    // - "Photo captured"
    
    // Displayed as:
    // [2025-11-10 12:34:56] System added: NEXUS-PRIME
    // [2025-11-10 12:35:12] Map generated (15 systems)
    // ...
    
    // Last 50 logs kept
    // Scrollable list view
    // Clear logs function available
}
```

**Tab 4: Export/Import (📤)**
```javascript
// Data management interface
function exportData() {
    // Creates JSON file matching Master format:
    // {
    //   "_meta": {
    //     "version": "1.0",
    //     "exported_at": "ISO timestamp",
    //     "device": "Mobile Explorer",
    //     "system_count": 15
    //   },
    //   "SYSTEM_NAME": { ...system data... },
    //   ...
    // }
    
    // Download as file (auto-names based on date)
    // Filename: Haven_Explorer_2025-11-10.json
}

function importData(file) {
    // Parse uploaded JSON file
    // Validate structure
    // Merge with existing systems (no duplicates)
    // Update LocalStorage
    // Log import action
    // Show summary: "Imported 10 new systems"
}
```

### Key Features

**Photo Management**:
```javascript
// Camera integration (iOS PWA capability)
function capturePhoto() {
    // iOS Safari support:
    // - Request camera permission
    // - Capture image with native camera
    // - Compress if needed (2 MB limit)
    // - Encode as base64: data:image/jpeg;base64,/9j/...
    // - Store in system.photo field
}

// File upload fallback
function uploadPhoto() {
    // Open file picker
    // Accept PNG, JPG, HEIC
    // Preview before saving
    // Base64 encode for JSON storage
}
```

**LocalStorage Persistence**:
```javascript
// Automatic saving on every action
function saveToStorage() {
    // Saves to browser's LocalStorage
    // Limit: 5-10 MB (warning at 75%)
    // Key structure: "haven_systems", "haven_logs", "haven_meta"
    // Survives browser close/app quit
    // No cloud sync required
}

// On startup
function loadFromStorage() {
    // Restore user's last session
    // Systems, logs, and settings
    // Full offline capability after first load
}
```

**Offline Support**:
```javascript
// Service Worker registration (optional, HTTPS only)
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('sw.js');
}

// Works offline:
// ✅ Wizard (add/edit systems)
// ✅ Map (view existing systems)
// ✅ Logs (read activity)
// ❌ Export (needs browser capability)
// ❌ Import (can't load files offline, but can import after online)
```

### Installation Methods

**Method 1: iOS (Easiest)**
```
1. On iPhone, open Haven_Mobile_Explorer.html in Safari
2. Tap Share button (arrow up)
3. Scroll and tap "Add to Home Screen"
4. Name: "Haven Explorer"
5. Tap "Add"
6. App icon appears on home screen
7. Tap to open as native app experience
```

**Method 2: Android**
```
1. On Android, open Haven_Mobile_Explorer.html in Chrome
2. Tap menu (⋮) 
3. Tap "Add to Home Screen"
4. Customize name: "Haven Explorer"
5. Tap "Install"
6. App appears on home screen
7. Tap to open in full-screen mode
```

**Method 3: Browser (No Install)**
```
1. Open Haven_Mobile_Explorer.html in any browser
2. Use as normal web page
3. LocalStorage still persists between visits
4. No home screen icon, but fully functional
```

### Data Format (Compatible with Desktop)
```json
{
  "_meta": {
    "version": "1.0.0",
    "exported_at": "2025-11-10T12:34:56Z",
    "device": "Mobile Explorer",
    "system_count": 15
  },
  "NEXUS-PRIME": {
    "id": "uuid-12345",
    "name": "NEXUS-PRIME",
    "region": "Euclid",
    "x": 2048.5,
    "y": 1024.3,
    "z": 512.1,
    "star_type": "F-class",
    "photo": "data:image/jpeg;base64,/9j/4AAQSkZJRgABA...",
    "planets": [
      {
        "name": "Primary",
        "type": "Terrestrial",
        "biome": "Lush",
        "moons": [
          {
            "name": "Orbital Body",
            "type": "Rocky"
          }
        ]
      }
    ]
  }
}
```

### Browser Compatibility
```
✅ iOS Safari 14.0+
✅ Chrome 90+ (Android/Desktop)
✅ Firefox 88+
✅ Edge 90+
✅ Samsung Internet 14+
```

### Performance Specifications
- **File Size**: 54.5 KB (self-contained, no CDN except Three.js)
- **Startup**: < 2 seconds
- **Map Render**: 60 FPS (GPU accelerated)
- **LocalStorage**: ~10 MB limit (warns at 7.5 MB)
- **Photo Encoding**: 2 MB per image limit

### Known Limitations & Workarounds
```
iOS Safari Issues:
  ⚠️ Home screen add sometimes hidden in UI
  ✅ Works perfectly in browser without installing
  ✅ Install guide provides detailed steps
  
Android:
  ✅ No significant issues
  ✅ Smooth home screen installation
  ✅ Chrome PWA support excellent
  
Photo Storage:
  ⚠️ Large photos slow export (2 MB limit enforced)
  ✅ App warns about size and recommends compression
  ⚠️ Many photos increase JSON file size
  ✅ Recommend < 50 photos per export file
```

### Workflow Data Flow
```
User Entry (Mobile Explorer)
        ↓
Validates input
        ↓
Encodes photo as base64
        ↓
Saves to LocalStorage
        ↓
Updates 3D map immediately
        ↓
Logs action with timestamp
        ↓
       ↓
[Export to JSON]
        ↓
Downloads JSON file
        ↓
[Email/cloud share to others]
        ↓
Recipient opens Master Edition or User EXE
        ↓
Imports JSON file
        ↓
Systems merge with their data
        ↓
Available for mapping and further exploration
```

### Deployment
**Location**: `dist/Haven_Mobile_Explorer.html`
**Distribution**: Email, cloud share, or web link
**Hosting**: Any web server, or local via `python -m http.server 8000`
**Updates**: Replace single HTML file with new version

### Development
```
To modify Haven Mobile Explorer:
1. Open Haven_Mobile_Explorer.html in text editor
2. Find relevant section (search for key function)
3. Edit HTML, CSS, or JavaScript
4. Test in multiple browsers on actual device
5. Verify three.js loads (check browser console)
6. Test export/import functionality
7. Verify LocalStorage persists across sessions
```

---

### Dependencies
- `customtkinter` (GUI, --no-open flag handling)
- `pandas` (DataFrame processing)
- `pathlib` (file operations)
- `jinja2` (template rendering)
- `common.data_provider` (data loading)
- `common.data_source_manager` (backend selection)
- Template: `src/templates/map_template.html`

---

## 4. COMMON UTILITIES

### paths.py - Path Management (300+ lines)
```python
FROZEN = getattr(sys, 'frozen', False)
IS_USER_EDITION = os.getenv('IS_USER_EDITION', 'false').lower() == 'true'

def project_root() -> Path:
    """Get base directory"""
    if FROZEN:
        # PyInstaller bundle: directory containing .exe
        return Path(sys.executable).parent
    else:
        # Development: repository root
        return Path(__file__).parent.parent.parent

def data_dir() -> Path:
    """Get data storage directory"""
    if IS_USER_EDITION and FROZEN:
        # User EXE: files/ subdirectory in .exe folder
        return project_root() / "files"
    else:
        # Master: project root data/
        return project_root() / "data"

def data_path(name: str) -> Path:
    """Get specific data file path"""
    return data_dir() / name

def dist_dir() -> Path:
    """Generated maps output directory"""
    return project_root() / "dist"

def logs_dir() -> Path:
    """Log files directory"""
    logs = project_root() / "logs"
    logs.mkdir(exist_ok=True)
    return logs

def photos_dir() -> Path:
    """User uploaded photos directory"""
    photos = project_root() / "photos"
    photos.mkdir(exist_ok=True)
    return photos
```

**Path Resolution Examples**:
- Master (unfrozen): `/home/user/Haven_mdev/data/data.json`
- User EXE (frozen): `C:\Users\user\AppData\Local\Programs\Haven\files\data.json`
- Generated maps: `/home/user/Haven_mdev/dist/system_EUCLID-01.html`

### database.py - SQLite Wrapper (746 lines)
```python
class HavenDatabase:
    """Context manager for safe database operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection = None
        
    def __enter__(self):
        """Connection pooling"""
        self._connection = sqlite3.connect(self.db_path)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Automatic cleanup"""
        if self._connection:
            self._connection.close()
    
    def create_schema(self):
        """Initialize database with full schema"""
        # Creates tables: systems, planets, moons, space_stations, _metadata
        # Creates indexes: spatial (x,y,z), FTS5 (name search)
        # Sets up foreign keys
        
    def add_system(self, system_data: dict) -> str:
        """Insert system and nested planets/moons"""
        # Transaction:
        #   1. INSERT into systems
        #   2. For each planet: INSERT into planets
        #   3. For each moon: INSERT into moons
        # Returns system_id on success
        # Raises exception on foreign key violation
        
    def get_system(self, system_id: str) -> dict:
        """Fetch system with nested data"""
        # Query systems table
        # LEFT JOIN planets
        # LEFT JOIN moons
        # Reconstruct nested dict structure
        
    def search_nearby(self, x: float, y: float, z: float, radius: float) -> list:
        """Spatial search using indexes"""
        # WHERE distance(x,y,z from reference) <= radius
        # Uses spatial index for performance
        # Returns list of {system_id, name, distance}
        
    def search_by_name(self, query: str) -> list:
        """Full-text search using FTS5"""
        # WHERE system_name MATCH query OR planet_name MATCH query
        # Fast substring matching
```

### data_provider.py - Abstraction Layer (478 lines)
```python
class DataProvider(Protocol):
    """Contract for backend implementations"""
    
    def get_all_systems(self) -> dict:
        """Return all systems as {system_id: system_data}"""
        ...
        
    def get_system(self, system_id: str) -> dict:
        """Fetch single system"""
        ...
        
    def get_systems_paginated(self, page: int, per_page: int) -> dict:
        """Return paginated results with metadata"""
        # Returns:
        # {
        #   'systems': [...],
        #   'total': 10000,
        #   'page': 2,
        #   'per_page': 100,
        #   'total_pages': 100
        # }
        ...
        
    def search_systems(self, query: str) -> list:
        """Full-text search"""
        ...
        
    def add_system(self, system_data: dict) -> str:
        """Create new system"""
        ...
        
    def update_system(self, system_id: str, updates: dict) -> bool:
        """Modify existing system"""
        ...

class JSONDataProvider:
    """File-based implementation"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._cache = None
        
    def get_all_systems(self) -> dict:
        if self._cache is None:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            # Handle three data shapes
            self._cache = self._normalize_format(data)
        return self._cache
        
    def add_system(self, system_data: dict) -> str:
        systems = self.get_all_systems()
        system_id = system_data.get('id') or str(uuid.uuid4())
        systems[system_id] = system_data
        with open(self.file_path, 'w') as f:
            json.dump(systems, f, indent=2)
        return system_id

class DatabaseDataProvider:
    """SQLite implementation"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def get_all_systems(self) -> dict:
        with HavenDatabase(self.db_path) as db:
            systems = {}
            for record in db.get_all_raw():
                systems[record['id']] = record
        return systems
        
    def add_system(self, system_data: dict) -> str:
        with HavenDatabase(self.db_path) as db:
            return db.add_system(system_data)
```

### data_source_manager.py - Single Source of Truth (406 lines)
```python
class DataSourceInfo:
    """Immutable container for source metadata"""
    name: str              # 'production', 'testing', 'load_test', 'yh_database'
    provider_type: str     # 'json' or 'database'
    path: str              # File or database path
    count: int             # Pre-cached system count
    description: str       # Human-readable description
    is_active: bool        # Currently selected source

class DataSourceManager:
    """Singleton managing all data sources"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
        
    def _initialize(self):
        """Register all data sources"""
        self.sources = {
            'production': DataSourceInfo(
                name='production',
                provider_type='json',
                path=data_path('data.json'),
                count=0,  # Loaded on startup
                is_active=True
            ),
            'testing': DataSourceInfo(
                name='testing',
                provider_type='json',
                path=data_path('keeper_test_data.json'),
                count=50
            ),
            'load_test': DataSourceInfo(
                name='load_test',
                provider_type='database',
                path=data_path('load_test.db'),
                count=10000
            ),
            'yh_database': DataSourceInfo(
                name='yh_database',
                provider_type='database',
                path=data_path('VH-Database.db'),
                count=0
            )
        }
        self._cache_system_counts()
        
    def _cache_system_counts(self):
        """Pre-load system counts for UI"""
        for source in self.sources.values():
            provider = self.create_provider(source)
            source.count = len(provider.get_all_systems())
            
    def get_current(self) -> DataSourceInfo:
        """Return active data source"""
        for source in self.sources.values():
            if source.is_active:
                return source
        return self.sources['production']  # Default fallback
        
    def set_active(self, name: str) -> bool:
        """Switch active data source"""
        if name not in self.sources:
            return False
        for source in self.sources.values():
            source.is_active = False
        self.sources[name].is_active = True
        return True
        
    def create_provider(self, source: DataSourceInfo) -> DataProvider:
        """Factory method for provider instances"""
        if source.provider_type == 'json':
            return JSONDataProvider(str(source.path))
        elif source.provider_type == 'database':
            return DatabaseDataProvider(str(source.path))
        raise ValueError(f"Unknown provider type: {source.provider_type}")
```

---

## 5. CONFIGURATION SYSTEMS

### settings.py (Master Edition)
```python
# === BACKEND CONFIGURATION ===
USE_DATABASE = True                    # SQLite vs JSON
AUTO_DETECT_BACKEND = False            # Manual selection
PAGINATION_ENABLED = True              # Auto-page above 100 systems

# === PATH CONFIGURATION ===
JSON_DATA_PATH = data_path('data.json')
DATABASE_PATH = data_path('VH-Database.db')
BACKUP_DIR = project_root() / 'backups'
LOG_DIR = logs_dir()

# === UI CONFIGURATION ===
SHOW_BACKEND_STATUS = True             # Display in status bar
SHOW_SYSTEM_COUNT = True               # Update count display
ENABLE_DATABASE_STATS = True           # Show DB size/performance

# === FEATURES ===
ENABLE_JSON_IMPORT = True              # Allow EXE exports
ENABLE_PROGRESSIVE_MAPS = True         # Generate on-demand
AUTO_BACKUP_ON_STARTUP = True          # VH-Database backups

# === PERFORMANCE ===
PAGINATION_SIZE = 100
MEMORY_LIMIT_MB = 1024
MAX_CONCURRENT_OPS = 5
```

### settings_user.py (User Edition)
```python
# === BACKEND CONFIGURATION ===
USE_DATABASE = False                   # Always JSON for portability
IS_FROZEN = True                       # Assume EXE context
IS_USER_EDITION = True                 # Triggers file/ directory

# === PATH CONFIGURATION ===
BASE_DIR = Path(sys.executable).parent if FROZEN else project_root()
FILES_DIR = BASE_DIR / 'files'
JSON_DATA_PATH = FILES_DIR / 'data.json'
CLEAN_DATA_PATH = FILES_DIR / 'clean_data.json'
EXAMPLE_DATA_PATH = FILES_DIR / 'example_data.json'

# === BUNDLED RESOURCES ===
THEMES_DIR = FILES_DIR / 'themes'
ICONS_DIR = FILES_DIR / 'icons'

# === FEATURES ===
ENABLE_JSON_IMPORT = True              # Manual data sync with Master
ENABLE_PROGRESSIVE_MAPS = False        # Don't auto-generate (disk space)
SHOW_BACKEND_STATUS = False            # Simplify UI
SHOW_SYSTEM_COUNT = True               # But show data status

# === PERMISSIONS ===
ALLOW_DATABASE_CREATE = False          # Never upgrade to DB
ALLOW_EXTERNAL_CONFIG = False          # No config file edits
```

---

## 6. DISCORD BOT INTEGRATION

### Bot Entry (main.py - 252 lines)
```python
class TheKeeper(commands.Bot):
    """Discord bot representing 'The Keeper' entity"""
    
    def __init__(self):
        # Initialize bot with intents:
        # - message_content (read message text)
        # - members (track joins/leaves)
        # - guilds (manage servers)
        # - dm_messages (DM support)
        
    async def setup_hook(self):
        """Pre-connection initialization"""
        # Load 5 cogs:
        # - enhanced_discovery.py (submission system)
        # - pattern_recognition.py (data analysis)
        # - archive_system.py (historical records)
        # - admin_tools.py (moderator commands)
        # - community_features.py (engagement)
        
        # Sync command tree:
        # Copy global commands to guild for instant updates
        # await self.tree.sync(guild=discord.Object(GUILD_ID))
        
    async def on_ready(self):
        """Connection established"""
        # Set activity: "watching the patterns between stars..."
        # Log "Bot ready!" to keeper_db
        
    async def on_member_join(self, member: discord.Member):
        """New member initialization"""
        # Fetch Act I introduction from keeper_personality
        # Send via DM if possible, else in welcome channel
        # Record in story_progression table
        
    @app_commands.command(name='story-intro')
    async def story_intro(self, interaction: discord.Interaction):
        """Show current Act introduction"""
        # Get user's story_progression record
        # Render Act I/II/III intro embed
        # Send to user
        
    @app_commands.command(name='story-progress')
    async def story_progress(self, interaction: discord.Interaction):
        """Show user's story progression"""
        # Query discoveries and patterns counts
        # Calculate % progress to next Act
        # Show tier/status

async def main():
    # Load .env configuration
    # Create bot instance
    # Run with bot.run(TOKEN)
```

### Personality System (keeper_personality.py)
```python
def create_base_embed(title: str, description: str, color_key: str) -> discord.Embed:
    """Factory for themed embeds"""
    # color_key: 'discovery' (cyan), 'warning' (orange), 'alert' (red)
    # Returns Embed with consistent styling
    
def create_act_intro_embed(act: int) -> discord.Embed:
    """Act I/II/III introduction narratives"""
    # Act I: "Welcome to the exploration..."
    # Act II: "Your discoveries reveal patterns..."
    # Act III: "The archive preserves all..."
    # Returns formatted embed with story text
    
def create_discovery_analysis(discovery_data: dict) -> discord.Embed:
    """Format user discovery submission"""
    # Fields:
    # - System Name
    # - Coordinates
    # - Planets Found
    # - Submitted By
    # - Submitted At
    
def create_pattern_alert(pattern_data: dict) -> discord.Embed:
    """Announce detected pattern"""
    # Fields:
    # - Pattern Type (e.g., "Gold-rich systems in region")
    # - Confidence Level
    # - Sample Systems
    # - Next Steps
    
def create_tier_progression_embed(user: str, new_tier: str) -> discord.Embed:
    """Celebrate user advancement"""
    # Shows previous tier → new tier
    # Encourages further exploration
```

### Haven Integration (haven_integration.py - 316 lines)
```python
class HavenDataIntegration:
    """Bridge between Discord and Haven data files"""
    
    def __init__(self):
        # Priority path search:
        # 1. Environment variable: HAVEN_DATA_PATH
        # 2. keeper_test_data.json (test)
        # 3. Production data.json
        # 4. Fallback: empty data
        
    def _find_haven_data(self) -> Path:
        """Cross-platform data file discovery"""
        # Windows: Check AppData/Local/Programs/Haven/files/
        # macOS: Check ~/Library/Application Support/Haven/
        # Linux: Check ~/.config/haven/
        # Returns first found path or None
        
    def get_all_systems(self) -> dict:
        """Load systems excluding _meta"""
        # Read JSON file
        # Remove _meta field
        # Return {system_name: system_data}
        
    def get_planets_in_system(self, system_name: str) -> list:
        """Extract planets and moons"""
        # Returns list of:
        # {
        #   'name': planet_name,
        #   'type': planet_type,
        #   'biome': biome,
        #   'moons': [...]
        # }
        
    def find_systems_near(self, x: float, y: float, z: float, radius: float) -> list:
        """Spatial search within radius"""
        # Filter systems by distance formula
        # distance = sqrt((x-x0)^2 + (y-y0)^2 + (z-z0)^2)
        # Returns matching systems within radius
```

### Bot Database (keeper_db.py - 789 lines)
```python
class KeeperDatabase:
    """Story progression and discovery tracking"""
    
    async def connect(self):
        """Async SQLite connection"""
        # Uses aiosqlite for non-blocking
        # Creates schema if needed
        
    async def get_story_progression(self, user_id: int) -> dict:
        """User's Act and progress"""
        # Returns {
        #   'user_id': int,
        #   'current_act': 1-3,
        #   'discoveries': int,
        #   'patterns': int,
        #   'progress_percent': 0-100
        # }
        
    async def complete_act(self, user_id: int, act: int):
        """Transition to next Act"""
        # Update current_act
        # Trigger celebration embed
        # Thresholds:
        # - Act I complete: 1 discovery
        # - Act II complete: 3 discoveries OR 1 pattern
        # - Act III complete: 10 discoveries OR 5 patterns
        
    async def increment_story_stats(self, user_id: int, discovery_count: int = 0, pattern_count: int = 0):
        """Update user statistics"""
        # Add to discovery/pattern counts
        # Check for Act progression
        # Emit tier-up celebration if needed
        
    async def record_discovery(self, user_id: int, system_data: dict):
        """Store user submission"""
        # INSERT into discoveries table
        # Link to user_id
        # Check for pattern triggers
        
    async def detect_patterns(self) -> list:
        """Analyze all discoveries for patterns"""
        # Example patterns:
        # - "System X always has Y resource"
        # - "Region Z has unusual coordinate pattern"
        # Returns list of detected patterns
```

**Story Tables**:
```sql
CREATE TABLE story_progression (
    user_id INTEGER PRIMARY KEY,
    current_act INTEGER DEFAULT 1,
    discoveries INTEGER DEFAULT 0,
    patterns INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE discoveries (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    system_name TEXT,
    coordinates TEXT,
    planet_count INTEGER,
    submitted_at TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES story_progression(user_id)
);

CREATE TABLE patterns (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    confidence REAL,
    sample_count INTEGER,
    created_at TIMESTAMP
);
```

---

## 7. DATA FLOW EXAMPLES

### Flow 1: System Entry (User Creates New System)
```
User clicks "Open Wizard" in Control Room
    ↓
SystemEntryWizard.__init__() starts
    ↓
Page 1: User enters system details
    - System name: "NEXUS-PRIME"
    - Region: "Euclid"
    - Coordinates: (2048.5, 1024.3, 512.1)
    ↓
User clicks "Next"
    ↓
Validation: page_1_system_info() checks required fields
    ✓ All fields present and valid
    ↓
Page 2: User adds planets
    - Planet 1: "Primary" (Terrestrial, Lush)
      - Moon 1: "Orbital Body" (Rocky)
    - Planet 2: "Secondary" (Gas Giant)
    ↓
User clicks "Save"
    ↓
Validation: page_2_planets_editor() checks planets exist
    ✓ At least 1 planet, names unique
    ↓
save_system() executes:
    1. Generate system dict with uuid
    2. Read current data.json
    3. Backup to data.json.bak
    4. Merge new system
    5. Write data.json
    6. (If USE_DATABASE=True) Call db.add_system()
    ↓
Success dialog shown
    ↓
Wizard closes, returns to Control Room
    ↓
Control Room status updates:
    - System count incremented
    - Last update timestamp updated
```

### Flow 2: Map Generation (Generate 3D Visualization)
```
User clicks "Generate Map" in Control Room
    ↓
Control Room._show_progress_dialog() called
    ↓
Beta_VH_Map.generate_map() starts in background thread
    ↓
load_systems():
    - manager = DataSourceManager()
    - source = manager.get_current()
    - provider = manager.create_provider(source)
    - df = provider.get_all_systems() → Pandas DataFrame
    ↓
For each system in DataFrame:
    1. normalize_record(system_data)
    2. Validate coordinates are numeric
    3. Load map_template.html
    4. Render with system data
    5. Save to dist/system_REGION-ID.html
    ↓
Progress dialog updates for each file
    ↓
All HTML files generated to dist/
    ↓
Open dist/ in default browser (unless --no-open)
    ↓
User sees: system_EUCLID-NEXUS_PRIME.html opens
    - 3D galaxy view with system positions
    - Click on system to enter detail view
    - Orbit camera, rotate, zoom, pan
```

### Flow 3: Data Source Switching (Master → User EXE)
```
Master Edition with USE_DATABASE=True
    ↓
User selects: "Export systems as JSON"
    ↓
DataSourceManager.get_current() → yh_database (SQLite)
    ↓
DatabaseDataProvider.get_all_systems() → dict
    ↓
Write to data.json (snapshot)
    ↓
User downloads data.json
    ↓
User runs User Edition EXE
    ↓
EXE detected (FROZEN=True)
    ↓
settings_user.py loaded: USE_DATABASE=False
    ↓
paths.py returns: C:\Program Files\Haven\files\data.json
    ↓
User pastes downloaded data.json → files/ folder
    ↓
EXE wizard reads from: JSONDataProvider(files/data.json)
    ↓
User can now edit and submit new discoveries
    ↓
User exports updated data.json from EXE
    ↓
User uploads back to Master Edition
    ↓
Master merges changes into VH-Database.db
```

### Flow 4: Discord Bot Discovery Recording
```
User types: /submit-discovery
    ↓
Discord bot command triggered
    ↓
haven_integration.py loads data.json
    ↓
get_systems_near() returns nearby systems
    ↓
User selects system they discovered
    ↓
keeper_db.record_discovery() called:
    1. INSERT into discoveries table
    2. Link to user_id
    3. Call detect_patterns()
    ↓
detect_patterns() runs analysis:
    - Find common attributes across multiple discoveries
    - Create pattern if confidence > AUTO_PATTERN_THRESHOLD (0.75)
    ↓
If pattern created:
    - keeper_personality.create_pattern_alert()
    - Post in ARCHIVE_CHANNEL_ID
    ↓
keeper_db.increment_story_stats():
    - discovery_count += 1
    - Check for Act progression thresholds
    ↓
If Act progression triggered:
    - keeper_db.complete_act(user_id, new_act)
    - Post celebration embed in channel
    ↓
User sees progression notification
```

---

**Document Status**: Part 2 of 3 (Codebase Details - Complete)  
**Next**: Part 3 - Operations, Troubleshooting & Deployment
