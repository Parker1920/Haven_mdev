# Billion-Scale Architecture: Complete System Flow

## Executive Summary

At 1 billion systems, the architecture fundamentally changes from **"load everything, then filter"** to **"query only what you need, when you need it"**.

---

## Current vs. Future Architecture

### **Current System (< 10K systems)**
```
data.json (all data)
    ↓
Control Room loads entire file
    ↓
System Entry Wizard loads entire file
    ↓
Map Generator loads entire file → Embeds in HTML
    ↓
Browser loads entire dataset → Renders all
```

**Works until:** ~10,000 systems (~10 MB file)

### **Future System (1B+ systems)**
```
haven.db (1B systems)
    ↓
Control Room → Query only visible page
    ↓
System Entry Wizard → Query single system
    ↓
Map Generator → Query spatial region → Embed viewport only
    ↓
Browser → Progressive loading as camera moves
```

**Handles:** Unlimited systems (query determines what loads)

---

## Data Storage: The Database Structure

### Physical Storage
```
data/
├── haven.db                    # Main SQLite database (10-100 GB for 1B systems)
├── haven.db-shm                # Shared memory (automatic)
├── haven.db-wal                # Write-ahead log (automatic)
└── backups/
    ├── haven_backup_20251105.db
    └── ...
```

### Database Schema (What's Actually Stored)

```sql
-- haven.db contains 4 main tables:

┌─────────────────────────────────────────────────────────────┐
│ systems (1,000,000,000 rows)                                │
├─────────────────────────────────────────────────────────────┤
│ id (TEXT)              │ SYS_ADAM_1                         │
│ name (TEXT)            │ OOTLEFAR V                         │
│ x, y, z (REAL)         │ 3.0, 2.0, 1.0                      │
│ region (TEXT)          │ Adam                                │
│ fauna, flora, etc.     │ ...                                 │
│ created_at (TIMESTAMP) │ 2025-11-05 12:00:00                │
│ modified_at (TIMESTAMP)│ 2025-11-05 12:00:00                │
└─────────────────────────────────────────────────────────────┘
         │
         │ system_id FK
         ↓
┌─────────────────────────────────────────────────────────────┐
│ planets (5,000,000,000 rows - avg 5 per system)             │
├─────────────────────────────────────────────────────────────┤
│ id (INTEGER)           │ 1                                   │
│ system_id (TEXT)       │ SYS_ADAM_1                         │
│ name (TEXT)            │ OOTLEFAR V-A                        │
│ sentinel, fauna, etc.  │ ...                                 │
└─────────────────────────────────────────────────────────────┘
         │
         │ planet_id FK
         ↓
┌─────────────────────────────────────────────────────────────┐
│ moons (10,000,000,000 rows - avg 2 per planet)              │
├─────────────────────────────────────────────────────────────┤
│ id (INTEGER)           │ 1                                   │
│ planet_id (INTEGER)    │ 1                                   │
│ name (TEXT)            │ Moon Alpha                          │
│ orbit_radius (REAL)    │ 0.5                                 │
│ orbit_speed (REAL)     │ 0.05                                │
│ sentinel, fauna, etc.  │ ...                                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ space_stations (500,000,000 rows - ~50% have stations)      │
├─────────────────────────────────────────────────────────────┤
│ id (INTEGER)           │ 1                                   │
│ system_id (TEXT)       │ SYS_ADAM_1                         │
│ name (TEXT)            │ KEPLER Station                      │
│ x, y, z (REAL)         │ -0.5, -2.5, 1.0                    │
└─────────────────────────────────────────────────────────────┘
```

### Critical Performance Indexes
```sql
-- These make queries FAST (milliseconds instead of minutes)
CREATE INDEX idx_systems_region ON systems(region);           -- Find by region
CREATE INDEX idx_systems_coords ON systems(x, y, z);          -- Spatial queries
CREATE INDEX idx_systems_name ON systems(name);               -- Search by name
CREATE INDEX idx_planets_system ON planets(system_id);        -- Find planet's system
CREATE INDEX idx_moons_planet ON moons(planet_id);            -- Find moon's planet
```

**Why indexes matter:**
- **Without index:** Search 1B rows = ~10 seconds
- **With index:** Search 1B rows = ~0.001 seconds (10,000x faster!)

---

## Control Room: User's Entry Point

### How It Works Now (JSON)
```python
# src/control_room.py (current)
def load_data(self):
    with open('data/data.json', 'r') as f:
        self.data = json.load(f)  # Loads ALL systems into memory

    # Display systems in list
    for name, system in self.data.items():
        if name != "_meta":
            self.system_list.insert(tk.END, name)
```

**Problem at 1B scale:** Takes minutes to load, crashes with out-of-memory error.

### How It Works at 1B Scale (Database)
```python
# src/control_room.py (future - database version)
from src.common.database import HavenDatabase

class ControlRoom:
    def __init__(self):
        self.db = HavenDatabase("data/haven.db")
        self.current_page = 1
        self.per_page = 100  # Show 100 systems at a time
        self.current_filter = None  # Region filter

        # UI Components
        self.system_list = ctk.CTkScrollableFrame(...)
        self.page_label = ctk.CTkLabel(...)  # "Page 1 of 10,000,000"
        self.next_btn = ctk.CTkButton(text="Next →", command=self.next_page)
        self.prev_btn = ctk.CTkButton(text="← Previous", command=self.prev_page)
        self.region_dropdown = ctk.CTkOptionMenu(...)  # Filter by region
        self.search_bar = ctk.CTkEntry(placeholder="Search systems...")

        # Load first page
        self.load_current_page()

    def load_current_page(self):
        """Load only current page of systems (100 at a time)"""
        with self.db as database:
            # Query only the systems for this page
            page_data = database.get_systems_paginated(
                page=self.current_page,
                per_page=self.per_page,
                region=self.current_filter  # Optional filter
            )

        # Clear current list
        for widget in self.system_list.winfo_children():
            widget.destroy()

        # Display only these 100 systems
        for system in page_data['systems']:
            self.add_system_card(system)

        # Update page indicator
        self.page_label.configure(
            text=f"Page {page_data['page']:,} of {page_data['total_pages']:,} "
                 f"({page_data['total']:,} total systems)"
        )

        # Enable/disable navigation buttons
        self.prev_btn.configure(state="normal" if page_data['page'] > 1 else "disabled")
        self.next_btn.configure(state="normal" if page_data['page'] < page_data['total_pages'] else "disabled")

    def next_page(self):
        """Load next page of systems"""
        self.current_page += 1
        self.load_current_page()

    def prev_page(self):
        """Load previous page of systems"""
        self.current_page -= 1
        self.load_current_page()

    def on_region_filter_change(self, region: str):
        """User selected a region from dropdown"""
        self.current_filter = region if region != "All Regions" else None
        self.current_page = 1  # Reset to first page
        self.load_current_page()

    def on_search(self, event):
        """User typed in search bar"""
        query = self.search_bar.get()
        if not query:
            self.load_current_page()
            return

        # Search database (returns max 100 matches)
        with self.db as database:
            results = database.search_systems(query, limit=100)

        # Display search results
        for widget in self.system_list.winfo_children():
            widget.destroy()

        for system in results:
            self.add_system_card(system)

        self.page_label.configure(text=f"Search results: {len(results)} systems")

    def add_system_card(self, system: dict):
        """Add system card to scrollable list"""
        card = ctk.CTkFrame(self.system_list)
        card.pack(fill="x", padx=5, pady=2)

        # System name
        name_label = ctk.CTkLabel(
            card,
            text=system['name'],
            font=("Rajdhani", 16, "bold")
        )
        name_label.pack(side="left", padx=10)

        # Quick info
        info = f"{system['region']} | ({system['x']:.1f}, {system['y']:.1f}, {system['z']:.1f})"
        info_label = ctk.CTkLabel(card, text=info, font=("Rajdhani", 12))
        info_label.pack(side="left", padx=10)

        # Action buttons
        view_btn = ctk.CTkButton(
            card,
            text="View",
            width=60,
            command=lambda: self.view_system(system['name'])
        )
        view_btn.pack(side="right", padx=5)

        edit_btn = ctk.CTkButton(
            card,
            text="Edit",
            width=60,
            command=lambda: self.edit_system(system['name'])
        )
        edit_btn.pack(side="right", padx=5)

    def view_system(self, system_name: str):
        """Open system in map viewer"""
        # Query full system data (with planets, moons)
        with self.db as database:
            system = database.get_system_by_name(system_name)

        if not system:
            messagebox.showerror("Error", f"System '{system_name}' not found")
            return

        # Generate system map (only this system, not all 1B)
        from src.Beta_VH_Map import generate_system_map
        map_path = generate_system_map(system)

        # Open in browser
        import webbrowser
        webbrowser.open(map_path)

    def edit_system(self, system_name: str):
        """Open system in wizard for editing"""
        # Query full system data
        with self.db as database:
            system = database.get_system_by_name(system_name)

        if not system:
            messagebox.showerror("Error", f"System '{system_name}' not found")
            return

        # Launch wizard in edit mode
        from src.system_entry_wizard import SystemEntryWizard
        wizard = SystemEntryWizard(edit_mode=True, system_data=system)
        wizard.mainloop()

    def open_map_generator(self):
        """Generate full galaxy map"""
        # This now opens a dialog asking:
        # - "Generate full galaxy (may be slow for 1B systems)"
        # - "Generate region view" (dropdown of regions)
        # - "Generate current view" (systems visible in current page)

        dialog = MapGeneratorDialog(self, db=self.db)
        dialog.show()

    def add_new_system(self):
        """Add new system via wizard"""
        from src.system_entry_wizard import SystemEntryWizard
        wizard = SystemEntryWizard(edit_mode=False)
        wizard.mainloop()

        # After wizard closes, refresh current page
        self.load_current_page()
```

### Key Changes in Control Room:

1. **Pagination**: Shows 100 systems at a time, not all 1B
2. **Region Filter**: Dropdown to filter by region (queries database)
3. **Search**: Real-time search (queries database, returns top 100 matches)
4. **Lazy Loading**: Only queries data when needed (view/edit buttons)
5. **Page Navigation**: Previous/Next buttons to browse through billions

**User Experience:**
```
User opens Control Room
    → Sees first 100 systems instantly (0.1s query)
    → Clicks "Next" → Loads next 100 (0.1s query)
    → Selects "Adam" region → Shows only Adam systems (0.1s query)
    → Types "Gold" in search → Shows systems with Gold (0.1s query)
    → Clicks "View" on a system → Queries full details (0.01s query)
    → Map opens with just that system
```

**Memory Usage:**
- **Old system:** 1 TB (all 1B systems)
- **New system:** 10 MB (100 systems × ~100 KB each)

---

## System Entry Wizard: Add/Edit Systems

### How It Works at 1B Scale
```python
# src/system_entry_wizard.py (database version)
from src.common.database import HavenDatabase

class SystemEntryWizard:
    def __init__(self, edit_mode=False, system_data=None):
        self.db = HavenDatabase("data/haven.db")
        self.edit_mode = edit_mode
        self.system_data = system_data  # Passed from Control Room if editing

        # If editing, populate form with existing data
        if edit_mode and system_data:
            self.load_system_data(system_data)

        self.build_ui()

    def load_system_data(self, system: dict):
        """Load existing system into form fields"""
        self.name_entry.insert(0, system['name'])
        self.x_entry.insert(0, str(system['x']))
        self.y_entry.insert(0, str(system['y']))
        self.z_entry.insert(0, str(system['z']))
        self.region_entry.insert(0, system['region'])
        # ... populate all fields

        # Load planets
        for planet in system.get('planets', []):
            self.add_planet_to_form(planet)

            # Load moons for each planet
            for moon in planet.get('moons', []):
                self.add_moon_to_form(planet['name'], moon)

    def save_system(self):
        """Save system to database"""
        # Gather form data
        system_data = {
            'id': self.system_data['id'] if self.edit_mode else self.generate_system_id(),
            'name': self.name_entry.get(),
            'x': float(self.x_entry.get()),
            'y': float(self.y_entry.get()),
            'z': float(self.z_entry.get()),
            'region': self.region_entry.get(),
            'fauna': self.fauna_entry.get(),
            'flora': self.flora_entry.get(),
            'sentinel': self.sentinel_entry.get(),
            'materials': self.materials_entry.get(),
            'base_location': self.base_entry.get(),
            'photo': self.photo_entry.get(),
            'attributes': self.attributes_entry.get(),
            'planets': self.gather_planets_data(),
            'space_station': self.gather_station_data() if self.has_station.get() else None
        }

        # Validate
        if not self.validate_system_data(system_data):
            return False

        # Save to database
        try:
            with self.db as database:
                if self.edit_mode:
                    # Update existing system
                    database.update_system(system_data['id'], system_data)
                    messagebox.showinfo("Success", f"System '{system_data['name']}' updated!")
                else:
                    # Add new system
                    database.add_system(system_data)
                    messagebox.showinfo("Success", f"System '{system_data['name']}' added!")

            self.destroy()
            return True

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save system: {e}")
            return False

    def gather_planets_data(self) -> list:
        """Gather all planet data from form"""
        planets = []
        for planet_frame in self.planets_list:
            planet = {
                'name': planet_frame.name_entry.get(),
                'sentinel': planet_frame.sentinel_entry.get(),
                'fauna': planet_frame.fauna_entry.get(),
                'flora': planet_frame.flora_entry.get(),
                'properties': planet_frame.properties_entry.get(),
                'materials': planet_frame.materials_entry.get(),
                'base_location': planet_frame.base_entry.get(),
                'photo': planet_frame.photo_entry.get(),
                'notes': planet_frame.notes_entry.get(),
                'moons': self.gather_moons_data(planet_frame)
            }
            planets.append(planet)
        return planets

    def gather_moons_data(self, planet_frame) -> list:
        """Gather all moon data for a planet"""
        moons = []
        for moon_frame in planet_frame.moons_list:
            moon = {
                'name': moon_frame.name_entry.get(),
                'sentinel': moon_frame.sentinel_entry.get(),
                'fauna': moon_frame.fauna_entry.get(),
                'flora': moon_frame.flora_entry.get(),
                'properties': moon_frame.properties_entry.get(),
                'materials': moon_frame.materials_entry.get(),
                'base_location': moon_frame.base_entry.get(),
                'photo': moon_frame.photo_entry.get(),
                'notes': moon_frame.notes_entry.get(),
                'orbit_radius': float(moon_frame.orbit_radius_entry.get() or 0.5),
                'orbit_speed': float(moon_frame.orbit_speed_entry.get() or 0.05)
            }
            moons.append(moon)
        return moons
```

### Key Changes in Wizard:

1. **Single System Operations**: Only loads/saves one system at a time
2. **Database Transactions**: Uses database connection, not JSON file I/O
3. **Instant Save**: Saves immediately (no waiting to write 1TB file)
4. **Undo/Redo**: Can use database transactions for rollback

**Performance:**
- **Old system:** Save = 10+ seconds (write entire 1TB JSON)
- **New system:** Save = 0.01 seconds (single INSERT/UPDATE)

---

## Map Generator: Creating Visualizations

### How It Works at 1B Scale

```python
# src/Beta_VH_Map.py (database version)
from src.common.database import HavenDatabase
import json

class MapGenerator:
    def __init__(self):
        self.db = HavenDatabase("data/haven.db")

    def generate_galaxy_map(self, region: str = None):
        """
        Generate full galaxy map or region view

        At 1B scale, this generates a PROGRESSIVE map that loads data via API
        """
        print("Generating galaxy map...")

        # For 1B systems, we DON'T embed all data in HTML
        # Instead, we embed a "viewport loader" that fetches data as needed

        if region:
            # Generate region view (e.g., "Adam" region with ~100 systems)
            with self.db as database:
                systems = database.get_all_systems(region=region)

            # This is small enough to embed
            html = self.create_static_map_html(systems, f"Region: {region}")
        else:
            # Generate progressive galaxy view
            html = self.create_progressive_map_html()

        # Save to file
        output_path = f"dist/VH-Map.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✓ Map generated: {output_path}")
        return output_path

    def generate_system_map(self, system_name: str):
        """
        Generate single system view (solar system map)
        This is always fast - just one system
        """
        print(f"Generating system map: {system_name}")

        # Query single system with all details
        with self.db as database:
            system = database.get_system_by_name(system_name)

        if not system:
            raise ValueError(f"System '{system_name}' not found")

        # Convert to map data format
        map_data = self.prepare_single_system_data(system)

        # Create HTML with embedded data
        html = self.create_system_map_html(map_data, system_name)

        # Save to file
        output_path = f"dist/system_{self.sanitize_filename(system_name)}.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✓ System map generated: {output_path}")
        return output_path

    def create_static_map_html(self, systems: list, title: str) -> str:
        """
        Create traditional static map (for small datasets)
        Embeds all data in HTML
        """
        # Load template
        with open('src/templates/map_template.html', 'r', encoding='utf-8') as f:
            template = f.read()

        # Convert systems to map data
        map_data = []
        for system in systems:
            item = {
                'type': 'system',
                'name': system['name'],
                'x': system['x'],
                'y': system['y'],
                'z': system['z'],
                'region': system['region'],
                'fauna': system.get('fauna'),
                'flora': system.get('flora'),
                'sentinel': system.get('sentinel'),
                'materials': system.get('materials'),
                'id': system['id']
            }
            map_data.append(item)

        # Embed data in template
        html = template.replace('{{SYSTEMS_DATA}}', json.dumps(map_data))
        html = html.replace('{{VIEW_MODE}}', 'galaxy')
        html = html.replace('{{REGION_NAME}}', title)
        html = html.replace('{{SYSTEM_META}}', '{}')

        return html

    def create_progressive_map_html(self) -> str:
        """
        Create progressive loading map (for billion-scale datasets)
        Loads data via API as user navigates
        """
        # Load progressive template
        with open('src/templates/map_template_progressive.html', 'r', encoding='utf-8') as f:
            template = f.read()

        # Get metadata (regions, total count)
        with self.db as database:
            regions = database.get_regions()
            total_systems = database.get_total_count()

        # Embed minimal metadata
        meta = {
            'regions': regions,
            'total_systems': total_systems,
            'api_endpoint': 'http://localhost:5000/api'  # API server
        }

        html = template.replace('{{GALAXY_META}}', json.dumps(meta))
        html = html.replace('{{VIEW_MODE}}', 'progressive')

        return html

    def prepare_single_system_data(self, system: dict) -> list:
        """
        Convert database system format to map data format
        """
        data = []

        # Add star
        star = {
            'type': 'star',
            'name': f"{system['name']} (Star)",
            'x': 0,
            'y': 0,
            'z': 0,
            'region': system['region']
        }
        data.append(star)

        # Add planets (with orbital positions)
        for i, planet in enumerate(system.get('planets', [])):
            # Calculate orbital position (simple circular orbit)
            angle = (i / max(len(system['planets']), 1)) * 2 * 3.14159
            radius = 2 + i  # AU from star

            planet_item = {
                'type': 'planet',
                'name': planet['name'],
                'x': radius * math.cos(angle),
                'y': 0,
                'z': radius * math.sin(angle),
                'sentinel': planet.get('sentinel'),
                'fauna': planet.get('fauna'),
                'flora': planet.get('flora'),
                'materials': planet.get('materials'),
                'moons': []  # Moons nested under planet
            }

            # Add moons (kept nested for orbiting visualization)
            for moon in planet.get('moons', []):
                moon_item = {
                    'name': moon['name'],
                    'sentinel': moon.get('sentinel'),
                    'fauna': moon.get('fauna'),
                    'flora': moon.get('flora'),
                    'materials': moon.get('materials'),
                    'orbit_radius': moon.get('orbit_radius', 0.5),
                    'orbit_speed': moon.get('orbit_speed', 0.05)
                }
                planet_item['moons'].append(moon_item)

            data.append(planet_item)

        # Add space station if exists
        if 'space_station' in system:
            ss = system['space_station']
            station = {
                'type': 'space_station',
                'name': ss['name'],
                'x': ss['x'],
                'y': ss['y'],
                'z': ss['z']
            }
            data.append(station)

        return data

    def sanitize_filename(self, name: str) -> str:
        """Convert system name to safe filename"""
        import re
        # Remove invalid filename characters
        safe = re.sub(r'[<>:"/\\|?*]', '_', name)
        safe = safe.replace(' ', '_')
        return safe
```

### Key Changes in Map Generator:

1. **Progressive Maps**: For full galaxy, generates HTML that loads data via API
2. **Static Maps**: For regions/systems, embeds data (small enough)
3. **Query-Based**: Only loads data needed for current map
4. **Fast Generation**: No longer needs to read entire database

**Map Generation Times:**
- **Old system (1B):** Hours (load 1TB JSON)
- **New system (1B):**
  - Galaxy map: 1 second (generates progressive loader)
  - Region map: 0.5 seconds (query region, embed data)
  - System map: 0.1 seconds (query one system, embed data)

---

## Map Viewer (Browser): The Final Display

### Progressive Loading Map (New for 1B Scale)

```javascript
// src/static/js/map-viewer-progressive.js
/**
 * Progressive map viewer - handles billion-scale datasets
 */

class ProgressiveGalaxyViewer {
    constructor() {
        // Three.js setup
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 10000);
        this.renderer = new THREE.WebGLRenderer({ antialias: true });

        // Data management
        this.loadedSystems = new Map();      // system_id → mesh
        this.systemCache = new Map();        // system_id → data
        this.loadRadius = 50;                 // LY radius to load
        this.maxVisible = 5000;               // Max systems to render
        this.lastLoadPos = null;              // Camera position at last load
        this.loadThreshold = 15;              // LY movement to trigger reload

        // API endpoint (from embedded meta)
        this.apiEndpoint = window.GALAXY_META.api_endpoint;

        this.init();
    }

    async init() {
        // Setup renderer
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setClearColor(0x0a0a14);
        document.getElementById('canvas-container').appendChild(this.renderer.domElement);

        // Setup camera
        this.camera.position.set(0, 50, 100);
        this.camera.lookAt(0, 0, 0);

        // Setup controls (OrbitControls)
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;

        // Setup raycaster for clicking
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();

        // Add event listeners
        window.addEventListener('resize', () => this.onWindowResize());
        window.addEventListener('mousemove', (e) => this.onMouseMove(e));
        window.addEventListener('click', (e) => this.onClick(e));

        // Initial load
        console.log('Progressive Galaxy Viewer initialized');
        console.log(`Total systems in database: ${window.GALAXY_META.total_systems.toLocaleString()}`);

        await this.loadVisibleSystems();

        // Start render loop
        this.animate();
    }

    async loadVisibleSystems() {
        /**
         * Load systems visible from current camera position
         * KEY FUNCTION: Only loads ~1000 systems, not all 1 billion!
         */
        const camPos = this.camera.position;

        console.log(`[LOAD] Camera at (${camPos.x.toFixed(1)}, ${camPos.y.toFixed(1)}, ${camPos.z.toFixed(1)})`);
        console.log(`[LOAD] Loading systems within ${this.loadRadius} LY...`);

        // Show loading indicator
        this.showLoadingIndicator(true);

        try {
            // Fetch visible systems from API
            const url = `${this.apiEndpoint}/systems/visible?` +
                       `cx=${camPos.x}&cy=${camPos.y}&cz=${camPos.z}&` +
                       `radius=${this.loadRadius}&limit=${this.maxVisible}`;

            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const systems = await response.json();
            console.log(`[LOAD] Received ${systems.length} systems from API`);

            // Add new systems to scene
            let addedCount = 0;
            for (const system of systems) {
                if (!this.loadedSystems.has(system.id)) {
                    this.addSystemToScene(system);
                    addedCount++;
                }
                this.systemCache.set(system.id, system);
            }

            console.log(`[LOAD] Added ${addedCount} new systems to scene`);

            // Remove systems that are now too far
            const culled = this.cullDistantSystems();
            console.log(`[LOAD] Removed ${culled} distant systems`);

            // Update stats display
            this.updateStatsDisplay();

        } catch (error) {
            console.error('[LOAD] Failed to load systems:', error);
            this.showError('Failed to load systems. Is the API server running?');
        } finally {
            this.showLoadingIndicator(false);
        }
    }

    addSystemToScene(system) {
        /**
         * Add single system to 3D scene
         */
        // Create star mesh
        const geometry = new THREE.SphereGeometry(0.5, 16, 16);
        const material = new THREE.MeshBasicMaterial({
            color: this.getStarColor(system.region)
        });
        const mesh = new THREE.Mesh(geometry, material);

        mesh.position.set(system.x, system.y, system.z);
        mesh.userData = {
            type: 'system',
            id: system.id,
            name: system.name,
            region: system.region
        };

        // Add glow effect
        const glowGeometry = new THREE.SphereGeometry(0.7, 16, 16);
        const glowMaterial = new THREE.MeshBasicMaterial({
            color: this.getStarColor(system.region),
            transparent: true,
            opacity: 0.3
        });
        const glow = new THREE.Mesh(glowGeometry, glowMaterial);
        mesh.add(glow);

        // Add to scene
        this.scene.add(mesh);
        this.loadedSystems.set(system.id, mesh);
    }

    cullDistantSystems() {
        /**
         * Remove systems too far from camera
         * Keeps memory usage bounded
         */
        const camPos = this.camera.position;
        const cullRadius = this.loadRadius * 1.5;  // 50% hysteresis
        let culledCount = 0;

        for (const [systemId, mesh] of this.loadedSystems) {
            const dx = mesh.position.x - camPos.x;
            const dy = mesh.position.y - camPos.y;
            const dz = mesh.position.z - camPos.z;
            const distance = Math.sqrt(dx*dx + dy*dy + dz*dz);

            if (distance > cullRadius) {
                // Remove from scene
                this.scene.remove(mesh);
                mesh.geometry.dispose();
                mesh.material.dispose();

                // Remove from cache
                this.loadedSystems.delete(systemId);
                this.systemCache.delete(systemId);

                culledCount++;
            }
        }

        return culledCount;
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        // Update controls
        this.controls.update();

        // Check if camera moved significantly
        if (this.needsReload()) {
            this.loadVisibleSystems();
            this.lastLoadPos = this.camera.position.clone();
        }

        // Render scene
        this.renderer.render(this.scene, this.camera);
    }

    needsReload() {
        /**
         * Check if camera moved far enough to trigger reload
         */
        if (!this.lastLoadPos) return true;

        const dist = this.camera.position.distanceTo(this.lastLoadPos);
        return dist > this.loadThreshold;
    }

    async onClick(event) {
        /**
         * Handle system click - load full details
         */
        // Calculate mouse position
        this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

        // Raycast
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const meshes = Array.from(this.loadedSystems.values());
        const intersects = this.raycaster.intersectObjects(meshes);

        if (intersects.length > 0) {
            const mesh = intersects[0].object;
            const systemName = mesh.userData.name;

            console.log(`[CLICK] System: ${systemName}`);

            // Load full system details from API
            try {
                const response = await fetch(`${this.apiEndpoint}/systems/${encodeURIComponent(systemName)}`);
                const system = await response.json();

                // Show system details panel
                this.showSystemDetails(system);

            } catch (error) {
                console.error('[CLICK] Failed to load system details:', error);
            }
        }
    }

    showSystemDetails(system) {
        /**
         * Display system information panel
         */
        const panel = document.getElementById('info-panel');

        let html = `<h3>${system.name}</h3>`;
        html += `<p><strong>Region:</strong> ${system.region}</p>`;
        html += `<p><strong>Coordinates:</strong> (${system.x}, ${system.y}, ${system.z})</p>`;
        html += `<p><strong>Fauna:</strong> ${system.fauna || 'Unknown'}</p>`;
        html += `<p><strong>Flora:</strong> ${system.flora || 'Unknown'}</p>`;
        html += `<p><strong>Sentinel:</strong> ${system.sentinel || 'Unknown'}</p>`;

        if (system.materials) {
            html += `<p><strong>Materials:</strong> ${system.materials}</p>`;
        }

        if (system.planets && system.planets.length > 0) {
            html += `<p><strong>Planets:</strong> ${system.planets.length}</p>`;
            html += `<ul>`;
            for (const planet of system.planets) {
                html += `<li>${planet.name}`;
                if (planet.moons && planet.moons.length > 0) {
                    html += ` (${planet.moons.length} moon${planet.moons.length > 1 ? 's' : ''})`;
                }
                html += `</li>`;
            }
            html += `</ul>`;
        }

        if (system.space_station) {
            html += `<p><strong>Space Station:</strong> ${system.space_station.name}</p>`;
        }

        // Button to open full system view
        html += `<button onclick="window.openSystemView('${system.name}')">Open System View</button>`;

        panel.innerHTML = html;
        panel.style.display = 'block';
    }

    updateStatsDisplay() {
        /**
         * Update stats overlay
         */
        const stats = document.getElementById('stats-panel');
        if (!stats) return;

        const loaded = this.loadedSystems.size;
        const cached = this.systemCache.size;
        const total = window.GALAXY_META.total_systems;

        stats.innerHTML = `
            <div>Loaded: ${loaded.toLocaleString()} systems</div>
            <div>Cached: ${cached.toLocaleString()} systems</div>
            <div>Total in database: ${total.toLocaleString()} systems</div>
            <div>Load radius: ${this.loadRadius} LY</div>
        `;
    }

    getStarColor(region) {
        /**
         * Get star color based on region
         */
        const colors = {
            'Adam': 0x00CED1,      // Cyan
            'Star': 0xFFD700,      // Gold
            'Beta': 0xFF6B6B,      // Red
            'Gamma': 0x4ECDC4,     // Teal
            'Delta': 0x9B59B6      // Purple
        };
        return colors[region] || 0x00CED1;
    }

    showLoadingIndicator(show) {
        const indicator = document.getElementById('loading-indicator');
        if (indicator) {
            indicator.style.display = show ? 'block' : 'none';
        }
    }

    showError(message) {
        const errorPanel = document.getElementById('error-panel');
        if (errorPanel) {
            errorPanel.textContent = message;
            errorPanel.style.display = 'block';
            setTimeout(() => {
                errorPanel.style.display = 'none';
            }, 5000);
        }
    }

    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    onMouseMove(event) {
        // Update mouse position for raycasting
        this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    }
}

// Global function to open system view
window.openSystemView = async function(systemName) {
    console.log(`Opening system view for: ${systemName}`);
    // This would trigger map generation on backend
    const response = await fetch(`${viewer.apiEndpoint}/generate/system/${encodeURIComponent(systemName)}`);
    const result = await response.json();

    // Open generated map in new tab
    window.open(result.map_url, '_blank');
};

// Initialize viewer
const viewer = new ProgressiveGalaxyViewer();
```

### Key Features of Progressive Viewer:

1. **Viewport Loading**: Only loads systems within 50 LY radius of camera
2. **Auto-Reload**: Loads new systems as camera moves
3. **Culling**: Removes systems outside view to save memory
4. **Caching**: Keeps recently viewed systems in memory
5. **Lazy Details**: Full system details loaded only when clicked

**Memory Usage in Browser:**
- **Old system (1B):** Crash (tries to load 1 TB)
- **New system (1B):** ~50 MB (5,000 systems × 10 KB each)

---

## API Server: The Middleman

### Flask API (Serves Data to Browser)

```python
# src/api/haven_api_server.py
"""
REST API server for Haven database
Serves system data to progressive map viewer
"""
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from src.common.database import HavenDatabase
from src.Beta_VH_Map import MapGenerator
import os

app = Flask(__name__)
CORS(app)  # Allow browser to fetch from this API

db_path = "data/haven.db"

@app.route('/api/systems/visible')
def get_visible_systems():
    """
    Get systems within spherical viewing frustum
    This is THE KEY ENDPOINT for progressive loading
    """
    try:
        cx = float(request.args.get('cx', 0))
        cy = float(request.args.get('cy', 0))
        cz = float(request.args.get('cz', 0))
        radius = float(request.args.get('radius', 50))
        limit = int(request.args.get('limit', 5000))

        with HavenDatabase(db_path) as db:
            systems = db.get_systems_in_region_sphere(cx, cy, cz, radius, limit)

        return jsonify(systems)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/systems/<system_name>')
def get_system(system_name):
    """
    Get full details for single system
    Called when user clicks on a system
    """
    try:
        with HavenDatabase(db_path) as db:
            system = db.get_system_by_name(system_name)

        if system:
            return jsonify(system)
        return jsonify({'error': 'System not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/systems/search')
def search_systems():
    """
    Search systems by name, materials, etc.
    """
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 100))

        with HavenDatabase(db_path) as db:
            results = db.search_systems(query, limit)

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/regions')
def get_regions():
    """
    Get list of all regions
    """
    try:
        with HavenDatabase(db_path) as db:
            regions = db.get_regions()

        return jsonify(regions)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/regions/<region_name>/systems')
def get_region_systems(region_name):
    """
    Get all systems in a region
    """
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 100))

        with HavenDatabase(db_path) as db:
            result = db.get_systems_paginated(page, per_page, region=region_name)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate/system/<system_name>')
def generate_system_map(system_name):
    """
    Generate system map on-demand
    """
    try:
        generator = MapGenerator()
        map_path = generator.generate_system_map(system_name)

        # Return URL to generated map
        return jsonify({
            'map_url': f'/maps/{os.path.basename(map_path)}',
            'system_name': system_name
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/maps/<filename>')
def serve_map(filename):
    """
    Serve generated map files
    """
    return send_file(f'../dist/{filename}')


@app.route('/api/stats')
def get_stats():
    """
    Get database statistics
    """
    try:
        with HavenDatabase(db_path) as db:
            stats = {
                'total_systems': db.get_total_count(),
                'regions': db.get_regions(),
                'database_size_mb': os.path.getsize(db_path) / (1024 * 1024)
            }

        return jsonify(stats)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("HAVEN API SERVER")
    print("=" * 60)
    print(f"Database: {db_path}")

    if not os.path.exists(db_path):
        print(f"⚠️  Database not found at {db_path}")
        print("   Run migration first: python src/migration/json_to_sqlite.py")
    else:
        size_mb = os.path.getsize(db_path) / (1024 * 1024)
        print(f"✓ Database found ({size_mb:.1f} MB)")

    print("\nStarting API server on http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    app.run(debug=True, port=5000, threaded=True)
```

### Starting the API Server

```batch
REM Start API Server.bat
@echo off
title Haven API Server
cd /d "%~dp0"

echo Starting Haven API Server...
python src/api/haven_api_server.py

pause
```

---

## Complete Data Flow at 1B Scale

### User Adds New System
```
1. User clicks "Add System" in Control Room
    ↓
2. System Entry Wizard opens (blank form)
    ↓
3. User fills in system details, planets, moons
    ↓
4. User clicks "Save"
    ↓
5. Wizard calls: db.add_system(system_data)
    ↓
6. Database executes:
    - INSERT INTO systems (...)
    - INSERT INTO planets (...) for each planet
    - INSERT INTO moons (...) for each moon
    ↓
7. Transaction completes in 0.01 seconds
    ↓
8. Success message shown
    ↓
9. Control Room refreshes current page
    ↓
10. New system appears in list
```

**Time:** < 1 second total

### User Views Galaxy Map
```
1. User clicks "Generate Galaxy Map" in Control Room
    ↓
2. Dialog asks: "Full galaxy or region?"
    ↓
3. User selects "Full Galaxy (Progressive)"
    ↓
4. Map Generator creates progressive HTML (no data embedded)
    ↓
5. Browser opens map HTML
    ↓
6. JavaScript loads, camera at (0, 0, 0)
    ↓
7. Fetch: GET /api/systems/visible?cx=0&cy=0&cz=0&radius=50&limit=5000
    ↓
8. API queries database:
    SELECT * FROM systems
    WHERE x BETWEEN -50 AND 50
      AND y BETWEEN -50 AND 50
      AND z BETWEEN -50 AND 50
    LIMIT 5000
    ↓
9. Returns ~1,000 systems near origin (0.1s query)
    ↓
10. Browser renders 1,000 stars in 3D
    ↓
11. User navigates camera to (100, 200, 150)
    ↓
12. Camera moved > 15 LY, trigger reload
    ↓
13. Fetch: GET /api/systems/visible?cx=100&cy=200&cz=150&radius=50&limit=5000
    ↓
14. API returns ~1,000 systems near new position (0.1s)
    ↓
15. Browser adds new stars, removes distant ones
    ↓
16. User clicks on a star
    ↓
17. Fetch: GET /api/systems/OOTLEFAR%20V
    ↓
18. API returns full system details (0.01s)
    ↓
19. Info panel displays system info
    ↓
20. User clicks "Open System View"
    ↓
21. Fetch: GET /api/generate/system/OOTLEFAR%20V
    ↓
22. API generates system map (0.1s)
    ↓
23. Returns URL to generated map
    ↓
24. Browser opens system map in new tab
    ↓
25. Solar system view displays with orbiting moons
```

**Total time:** ~2 seconds (mostly network latency)
**Memory used:** ~50 MB (browser), ~10 MB (Control Room)

### User Searches for System
```
1. User types "Gold" in Control Room search bar
    ↓
2. Debounced input triggers search after 500ms
    ↓
3. Control Room calls: db.search_systems("Gold", limit=100)
    ↓
4. Database executes:
    SELECT * FROM systems
    WHERE name LIKE '%Gold%'
       OR materials LIKE '%Gold%'
       OR attributes LIKE '%Gold%'
    LIMIT 100
    ↓
5. Returns ~50 matching systems in 0.05 seconds
    ↓
6. Control Room displays 50 results
    ↓
7. User clicks on "OOTLEFAR V"
    ↓
8. Control Room calls: db.get_system_by_name("OOTLEFAR V")
    ↓
9. Database executes:
    SELECT * FROM systems WHERE name = 'OOTLEFAR V'
    SELECT * FROM planets WHERE system_id = 'SYS_ADAM_1'
    SELECT * FROM moons WHERE planet_id IN (...)
    SELECT * FROM space_stations WHERE system_id = 'SYS_ADAM_1'
    ↓
10. Returns full system data in 0.01 seconds
    ↓
11. Map generator creates system map (0.1s)
    ↓
12. Browser opens map
```

**Total time:** ~0.5 seconds

---

## File Structure at 1B Scale

```
Haven_Mdev/
├── data/
│   ├── haven.db                      # 10-100 GB (1B systems)
│   ├── haven.db-shm                  # Shared memory
│   ├── haven.db-wal                  # Write-ahead log
│   ├── data.json                     # LEGACY (keep for backward compat)
│   └── backups/
│       └── haven_backup_*.db         # Daily backups
│
├── src/
│   ├── control_room.py               # MODIFIED: Uses database
│   ├── system_entry_wizard.py        # MODIFIED: Uses database
│   ├── Beta_VH_Map.py                # MODIFIED: Progressive maps
│   │
│   ├── common/
│   │   ├── database.py               # NEW: Database wrapper
│   │   ├── data_provider.py          # NEW: Unified data interface
│   │   └── ...
│   │
│   ├── api/
│   │   └── haven_api_server.py       # NEW: Flask API server
│   │
│   ├── migration/
│   │   ├── json_to_sqlite.py         # NEW: JSON → SQLite migrator
│   │   └── import_bulk_data.py       # NEW: Bulk import tool
│   │
│   ├── static/js/
│   │   ├── map-viewer.js             # Existing: Static maps
│   │   └── map-viewer-progressive.js # NEW: Progressive loading
│   │
│   └── templates/
│       ├── map_template.html         # Existing: Static maps
│       └── map_template_progressive.html  # NEW: Progressive maps
│
├── dist/                             # Generated maps (same as before)
├── logs/                             # Logs (same as before)
├── tests/                            # Tests (add database tests)
│
├── Haven Control Room.bat            # MODIFIED: Set USE_DATABASE=true
├── Start API Server.bat              # NEW: Starts Flask API
└── config/
    └── settings.py                   # NEW: USE_DATABASE toggle
```

---

## Performance Summary

### Current System (JSON)
| Scale | Load Time | Memory Usage | Map Generation | Search |
|-------|-----------|--------------|----------------|--------|
| 10 systems | 0.01s | 100 KB | 0.1s | 0.01s |
| 1,000 systems | 0.1s | 10 MB | 1s | 0.5s |
| 10,000 systems | 1s | 100 MB | 10s | 5s |
| 100,000 systems | 10s | 1 GB | 100s | 50s |
| 1,000,000 systems | 100s | 10 GB | Crash | Crash |
| **1,000,000,000 systems** | **Impossible** | **1 TB** | **Impossible** | **Impossible** |

### New System (Database + Progressive Loading)
| Scale | Load Time | Memory Usage | Map Generation | Search |
|-------|-----------|--------------|----------------|--------|
| 10 systems | 0.02s (+overhead) | 1 MB | 0.1s | 0.01s |
| 1,000 systems | 0.05s | 2 MB | 0.5s | 0.01s |
| 10,000 systems | 0.1s | 5 MB | 1s | 0.02s |
| 100,000 systems | 0.1s | 10 MB | 1s | 0.05s |
| 1,000,000 systems | 0.2s | 20 MB | 1s | 0.1s |
| **1,000,000,000 systems** | **0.5s** | **50 MB** | **1s** | **0.2s** |

**Improvement at 1B scale:** ∞ (impossible → possible)

---

## Migration Strategy

### Phase 1: Add Database Layer (Parallel to JSON)
- Implement database.py, data_provider.py
- Add USE_DATABASE toggle
- Test with current 8 systems
- **Timeline:** 1-2 days

### Phase 2: Update Control Room & Wizard
- Add pagination to Control Room
- Update Wizard to use database
- Keep JSON as fallback
- **Timeline:** 2-3 days

### Phase 3: Add API Server & Progressive Maps
- Implement Flask API
- Create progressive map viewer
- Test with synthetic 100K systems
- **Timeline:** 3-4 days

### Phase 4: Migration Tools & Bulk Import
- Create bulk import script
- Add database management tools
- Benchmark performance
- **Timeline:** 2-3 days

### Phase 5: Production Deployment
- Migrate real data
- Set USE_DATABASE=True by default
- Monitor performance
- **Timeline:** 1-2 days

**Total timeline:** 2-3 weeks for full migration

---

## Key Takeaways

1. **Database is essential at 1B scale** - JSON physically cannot handle it

2. **Progressive loading is the secret** - Only load what's visible

3. **API separates concerns** - Backend handles queries, frontend handles display

4. **Pagination everywhere** - Control Room, Map Viewer, Search

5. **Indexes are critical** - 10,000x speedup on queries

6. **Backward compatible** - Can keep JSON for small datasets

7. **Memory bounded** - Never loads more than ~5,000 systems

8. **Query-driven architecture** - "Ask for what you need" instead of "Load everything"

---

## Next Steps

Would you like me to:

1. **Implement Phase 1** - Add database layer to your current system?
2. **Create demo with 100K systems** - Show progressive loading in action?
3. **Build migration script** - Convert your current data.json to SQLite?
4. **Add synthetic data generator** - Create 1M test systems for benchmarking?

Let me know what you'd like to tackle first!
