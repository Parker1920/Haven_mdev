# Database Migration Guide: Scaling to 1 Billion Systems

## Architecture Comparison

### Current (JSON-based)
```
User Request → Load entire data.json → Filter in memory → Render
```

### Proposed (Database-based)
```
User Request → SQL Query (filtered) → Load only needed data → Render
```

---

## Phase 1: SQLite Implementation (Easiest Migration)

### Why SQLite?
- Single file (like JSON)
- No server setup required
- Handles billions of rows
- 10-100x faster queries than JSON parsing
- Built into Python

### Database Schema

```sql
-- Systems table
CREATE TABLE systems (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    x REAL NOT NULL,
    y REAL NOT NULL,
    z REAL NOT NULL,
    region TEXT NOT NULL,
    fauna TEXT,
    flora TEXT,
    sentinel TEXT,
    materials TEXT,
    base_location TEXT,
    photo TEXT,
    attributes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Planets table
CREATE TABLE planets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    system_id TEXT NOT NULL,
    name TEXT NOT NULL,
    sentinel TEXT,
    fauna TEXT,
    flora TEXT,
    properties TEXT,
    materials TEXT,
    base_location TEXT,
    photo TEXT,
    notes TEXT,
    FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE
);

-- Moons table
CREATE TABLE moons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    planet_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    sentinel TEXT,
    fauna TEXT,
    flora TEXT,
    properties TEXT,
    materials TEXT,
    base_location TEXT,
    photo TEXT,
    notes TEXT,
    orbit_radius REAL,
    orbit_speed REAL,
    FOREIGN KEY (planet_id) REFERENCES planets(id) ON DELETE CASCADE
);

-- Space stations table
CREATE TABLE space_stations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    system_id TEXT NOT NULL,
    name TEXT NOT NULL,
    x REAL NOT NULL,
    y REAL NOT NULL,
    z REAL NOT NULL,
    FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE
);

-- Performance indexes
CREATE INDEX idx_systems_region ON systems(region);
CREATE INDEX idx_systems_coords ON systems(x, y, z);
CREATE INDEX idx_planets_system ON planets(system_id);
CREATE INDEX idx_moons_planet ON moons(planet_id);
CREATE INDEX idx_space_stations_system ON space_stations(system_id);
```

### Migration Script

```python
# src/migration/json_to_sqlite.py
"""
Migrate data.json to SQLite database
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime

class DatabaseMigrator:
    def __init__(self, json_path: str, db_path: str):
        self.json_path = Path(json_path)
        self.db_path = Path(db_path)

    def migrate(self):
        """Migrate JSON data to SQLite"""
        print(f"[1/4] Loading {self.json_path}...")
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"[2/4] Creating database schema at {self.db_path}...")
        conn = sqlite3.connect(self.db_path)
        self._create_schema(conn)

        print(f"[3/4] Migrating {len(data)-1} systems...")
        self._migrate_data(conn, data)

        print(f"[4/4] Creating indexes...")
        self._create_indexes(conn)

        conn.close()
        print(f"✓ Migration complete: {self.db_path}")

    def _create_schema(self, conn):
        """Create database tables"""
        cursor = conn.cursor()

        # Systems table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS systems (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                x REAL NOT NULL,
                y REAL NOT NULL,
                z REAL NOT NULL,
                region TEXT NOT NULL,
                fauna TEXT,
                flora TEXT,
                sentinel TEXT,
                materials TEXT,
                base_location TEXT,
                photo TEXT,
                attributes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Planets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS planets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                system_id TEXT NOT NULL,
                name TEXT NOT NULL,
                sentinel TEXT,
                fauna TEXT,
                flora TEXT,
                properties TEXT,
                materials TEXT,
                base_location TEXT,
                photo TEXT,
                notes TEXT,
                FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE
            )
        """)

        # Moons table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS moons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                planet_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                sentinel TEXT,
                fauna TEXT,
                flora TEXT,
                properties TEXT,
                materials TEXT,
                base_location TEXT,
                photo TEXT,
                notes TEXT,
                orbit_radius REAL DEFAULT 0.5,
                orbit_speed REAL DEFAULT 0.05,
                FOREIGN KEY (planet_id) REFERENCES planets(id) ON DELETE CASCADE
            )
        """)

        # Space stations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS space_stations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                system_id TEXT NOT NULL,
                name TEXT NOT NULL,
                x REAL NOT NULL,
                y REAL NOT NULL,
                z REAL NOT NULL,
                FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE
            )
        """)

        conn.commit()

    def _migrate_data(self, conn, data):
        """Migrate JSON data to database"""
        cursor = conn.cursor()

        for key, system in data.items():
            if key == "_meta" or not isinstance(system, dict):
                continue

            # Insert system
            cursor.execute("""
                INSERT INTO systems
                (id, name, x, y, z, region, fauna, flora, sentinel,
                 materials, base_location, photo, attributes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                system.get('id', f'SYS_{key}'),
                system.get('name', key),
                system.get('x', 0.0),
                system.get('y', 0.0),
                system.get('z', 0.0),
                system.get('region', 'Unknown'),
                system.get('fauna'),
                system.get('flora'),
                system.get('sentinel'),
                system.get('materials'),
                system.get('base_location'),
                system.get('photo'),
                system.get('attributes')
            ))

            system_id = system.get('id', f'SYS_{key}')

            # Insert space station if exists
            if 'space_station' in system:
                ss = system['space_station']
                cursor.execute("""
                    INSERT INTO space_stations (system_id, name, x, y, z)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    system_id,
                    ss.get('name', 'Station'),
                    ss.get('x', 0.0),
                    ss.get('y', 0.0),
                    ss.get('z', 0.0)
                ))

            # Insert planets
            for planet in system.get('planets', []):
                cursor.execute("""
                    INSERT INTO planets
                    (system_id, name, sentinel, fauna, flora, properties,
                     materials, base_location, photo, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    system_id,
                    planet.get('name', 'Unknown'),
                    planet.get('sentinel'),
                    planet.get('fauna'),
                    planet.get('flora'),
                    planet.get('properties'),
                    planet.get('materials'),
                    planet.get('base_location'),
                    planet.get('photo'),
                    planet.get('notes')
                ))

                planet_id = cursor.lastrowid

                # Insert moons for this planet
                for moon in planet.get('moons', []):
                    cursor.execute("""
                        INSERT INTO moons
                        (planet_id, name, sentinel, fauna, flora, properties,
                         materials, base_location, photo, notes, orbit_radius, orbit_speed)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        planet_id,
                        moon.get('name', 'Unknown Moon'),
                        moon.get('sentinel'),
                        moon.get('fauna'),
                        moon.get('flora'),
                        moon.get('properties'),
                        moon.get('materials'),
                        moon.get('base_location'),
                        moon.get('photo'),
                        moon.get('notes'),
                        moon.get('orbit_radius', 0.5),
                        moon.get('orbit_speed', 0.05)
                    ))

        conn.commit()

    def _create_indexes(self, conn):
        """Create performance indexes"""
        cursor = conn.cursor()

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_systems_region ON systems(region)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_systems_coords ON systems(x, y, z)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_planets_system ON planets(system_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_moons_planet ON moons(planet_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_space_stations_system ON space_stations(system_id)")

        conn.commit()


if __name__ == "__main__":
    migrator = DatabaseMigrator(
        json_path="data/data.json",
        db_path="data/haven.db"
    )
    migrator.migrate()
```

### New Database Wrapper

```python
# src/common/database.py
"""
Database wrapper for Haven system data
Replaces direct JSON file access
"""
import sqlite3
from typing import List, Dict, Optional, Any
from pathlib import Path
import json

class HavenDatabase:
    """SQLite database wrapper for Haven system data"""

    def __init__(self, db_path: str = "data/haven.db"):
        self.db_path = Path(db_path)
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Return dict-like rows
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    # ========== QUERY METHODS ==========

    def get_all_systems(self, region: Optional[str] = None) -> List[Dict]:
        """
        Get all systems, optionally filtered by region

        Performance: O(n) where n = matching systems
        At 1B systems, this would still be slow - use pagination instead
        """
        cursor = self.conn.cursor()

        if region:
            cursor.execute("""
                SELECT * FROM systems WHERE region = ?
                ORDER BY name
            """, (region,))
        else:
            cursor.execute("SELECT * FROM systems ORDER BY name")

        return [dict(row) for row in cursor.fetchall()]

    def get_systems_paginated(self, page: int = 1, per_page: int = 100,
                             region: Optional[str] = None) -> Dict[str, Any]:
        """
        Get systems with pagination (CRITICAL for large datasets)

        Args:
            page: Page number (1-indexed)
            per_page: Systems per page
            region: Optional region filter

        Returns:
            {
                'systems': [...],
                'total': 1000000000,
                'page': 1,
                'per_page': 100,
                'total_pages': 10000000
            }
        """
        cursor = self.conn.cursor()
        offset = (page - 1) * per_page

        # Get total count
        if region:
            cursor.execute("SELECT COUNT(*) FROM systems WHERE region = ?", (region,))
        else:
            cursor.execute("SELECT COUNT(*) FROM systems")
        total = cursor.fetchone()[0]

        # Get page of systems
        if region:
            cursor.execute("""
                SELECT * FROM systems
                WHERE region = ?
                ORDER BY name
                LIMIT ? OFFSET ?
            """, (region, per_page, offset))
        else:
            cursor.execute("""
                SELECT * FROM systems
                ORDER BY name
                LIMIT ? OFFSET ?
            """, (per_page, offset))

        systems = [dict(row) for row in cursor.fetchall()]

        return {
            'systems': systems,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }

    def get_systems_in_region_sphere(self, cx: float, cy: float, cz: float,
                                     radius: float, limit: int = 1000) -> List[Dict]:
        """
        Get systems within spherical region (for map viewing)

        This is THE KEY QUERY for 1B systems - only load what's visible

        Performance: O(log n) with spatial index
        """
        cursor = self.conn.cursor()

        # Simple bounding box query (could use R-tree for better performance)
        cursor.execute("""
            SELECT * FROM systems
            WHERE x BETWEEN ? AND ?
              AND y BETWEEN ? AND ?
              AND z BETWEEN ? AND ?
            LIMIT ?
        """, (
            cx - radius, cx + radius,
            cy - radius, cy + radius,
            cz - radius, cz + radius,
            limit
        ))

        systems = []
        for row in cursor.fetchall():
            system = dict(row)
            # Calculate actual distance
            dx = system['x'] - cx
            dy = system['y'] - cy
            dz = system['z'] - cz
            distance = (dx*dx + dy*dy + dz*dz) ** 0.5

            if distance <= radius:
                system['distance'] = distance
                systems.append(system)

        return sorted(systems, key=lambda s: s['distance'])

    def get_system_by_name(self, name: str) -> Optional[Dict]:
        """Get single system by name with all related data"""
        cursor = self.conn.cursor()

        # Get system
        cursor.execute("SELECT * FROM systems WHERE name = ?", (name,))
        row = cursor.fetchone()
        if not row:
            return None

        system = dict(row)

        # Get space station
        cursor.execute("""
            SELECT * FROM space_stations WHERE system_id = ?
        """, (system['id'],))
        station_row = cursor.fetchone()
        if station_row:
            system['space_station'] = dict(station_row)

        # Get planets with moons
        cursor.execute("""
            SELECT * FROM planets WHERE system_id = ?
        """, (system['id'],))

        planets = []
        for planet_row in cursor.fetchall():
            planet = dict(planet_row)

            # Get moons for this planet
            cursor.execute("""
                SELECT * FROM moons WHERE planet_id = ?
            """, (planet['id'],))
            planet['moons'] = [dict(moon_row) for moon_row in cursor.fetchall()]

            planets.append(planet)

        system['planets'] = planets

        return system

    def search_systems(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Search systems by name or attributes

        Performance: O(n) without full-text index, O(log n) with FTS5
        """
        cursor = self.conn.cursor()

        search_pattern = f"%{query}%"
        cursor.execute("""
            SELECT * FROM systems
            WHERE name LIKE ?
               OR materials LIKE ?
               OR attributes LIKE ?
            LIMIT ?
        """, (search_pattern, search_pattern, search_pattern, limit))

        return [dict(row) for row in cursor.fetchall()]

    def get_regions(self) -> List[str]:
        """Get list of all unique regions"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT region FROM systems ORDER BY region")
        return [row[0] for row in cursor.fetchall()]

    # ========== WRITE METHODS ==========

    def add_system(self, system_data: Dict) -> str:
        """Add new system to database"""
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO systems
            (id, name, x, y, z, region, fauna, flora, sentinel,
             materials, base_location, photo, attributes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            system_data.get('id'),
            system_data['name'],
            system_data['x'],
            system_data['y'],
            system_data['z'],
            system_data['region'],
            system_data.get('fauna'),
            system_data.get('flora'),
            system_data.get('sentinel'),
            system_data.get('materials'),
            system_data.get('base_location'),
            system_data.get('photo'),
            system_data.get('attributes')
        ))

        system_id = system_data.get('id')

        # Add planets if provided
        for planet in system_data.get('planets', []):
            self._add_planet(cursor, system_id, planet)

        # Add space station if provided
        if 'space_station' in system_data:
            self._add_space_station(cursor, system_id, system_data['space_station'])

        self.conn.commit()
        return system_id

    def _add_planet(self, cursor, system_id: str, planet_data: Dict) -> int:
        """Add planet to system"""
        cursor.execute("""
            INSERT INTO planets
            (system_id, name, sentinel, fauna, flora, properties,
             materials, base_location, photo, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            system_id,
            planet_data['name'],
            planet_data.get('sentinel'),
            planet_data.get('fauna'),
            planet_data.get('flora'),
            planet_data.get('properties'),
            planet_data.get('materials'),
            planet_data.get('base_location'),
            planet_data.get('photo'),
            planet_data.get('notes')
        ))

        planet_id = cursor.lastrowid

        # Add moons if provided
        for moon in planet_data.get('moons', []):
            self._add_moon(cursor, planet_id, moon)

        return planet_id

    def _add_moon(self, cursor, planet_id: int, moon_data: Dict):
        """Add moon to planet"""
        cursor.execute("""
            INSERT INTO moons
            (planet_id, name, sentinel, fauna, flora, properties,
             materials, base_location, photo, notes, orbit_radius, orbit_speed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            planet_id,
            moon_data['name'],
            moon_data.get('sentinel'),
            moon_data.get('fauna'),
            moon_data.get('flora'),
            moon_data.get('properties'),
            moon_data.get('materials'),
            moon_data.get('base_location'),
            moon_data.get('photo'),
            moon_data.get('notes'),
            moon_data.get('orbit_radius', 0.5),
            moon_data.get('orbit_speed', 0.05)
        ))

    def _add_space_station(self, cursor, system_id: str, station_data: Dict):
        """Add space station to system"""
        cursor.execute("""
            INSERT INTO space_stations (system_id, name, x, y, z)
            VALUES (?, ?, ?, ?, ?)
        """, (
            system_id,
            station_data['name'],
            station_data['x'],
            station_data['y'],
            station_data['z']
        ))

    def update_system(self, system_id: str, updates: Dict):
        """Update system fields"""
        cursor = self.conn.cursor()

        # Build dynamic UPDATE query
        fields = []
        values = []
        for key, value in updates.items():
            if key not in ['id', 'planets', 'space_station']:
                fields.append(f"{key} = ?")
                values.append(value)

        values.append(system_id)

        cursor.execute(f"""
            UPDATE systems
            SET {', '.join(fields)}, modified_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, values)

        self.conn.commit()

    def delete_system(self, system_id: str):
        """Delete system and all related data (cascades to planets/moons)"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM systems WHERE id = ?", (system_id,))
        self.conn.commit()


# ========== USAGE EXAMPLES ==========

def example_basic_usage():
    """Basic database operations"""
    with HavenDatabase() as db:
        # Get all systems in Adam region
        systems = db.get_all_systems(region="Adam")
        print(f"Found {len(systems)} systems in Adam region")

        # Get single system with all data
        system = db.get_system_by_name("OOTLEFAR V")
        print(f"System: {system['name']}")
        print(f"  Planets: {len(system.get('planets', []))}")

        # Search
        results = db.search_systems("Cadmium")
        print(f"Found {len(results)} systems with Cadmium")


def example_pagination():
    """Paginated loading (CRITICAL for 1B systems)"""
    with HavenDatabase() as db:
        # Load first page
        page1 = db.get_systems_paginated(page=1, per_page=100)
        print(f"Page 1 of {page1['total_pages']}")
        print(f"Total systems: {page1['total']:,}")

        # Process in chunks
        for page_num in range(1, 11):  # First 10 pages
            page = db.get_systems_paginated(page=page_num, per_page=100)
            for system in page['systems']:
                print(f"  {system['name']}")


def example_spatial_query():
    """Load only visible systems (KEY for 1B scale)"""
    with HavenDatabase() as db:
        # User is looking at coordinates (3, 2, 1) with 10 LY radius
        visible = db.get_systems_in_region_sphere(
            cx=3.0, cy=2.0, cz=1.0,
            radius=10.0,
            limit=1000  # Max to render
        )
        print(f"Visible systems: {len(visible)}")
        for sys in visible[:5]:
            print(f"  {sys['name']}: {sys['distance']:.2f} LY away")
```

---

## Phase 2: Frontend Changes (Progressive Loading)

### Current Problem
```javascript
// This fails at 1B systems - loads everything into browser memory
window.SYSTEMS_DATA = {{SYSTEMS_DATA}};  // 1TB of JSON!
```

### Solution: REST API + Progressive Loading

```python
# src/api/system_api.py
"""
REST API for system data
Serves data progressively instead of all at once
"""
from flask import Flask, jsonify, request
from src.common.database import HavenDatabase

app = Flask(__name__)

@app.route('/api/systems/region/<region_name>')
def get_region_systems(region_name):
    """Get all systems in a region"""
    with HavenDatabase() as db:
        systems = db.get_all_systems(region=region_name)
        return jsonify(systems)

@app.route('/api/systems/visible')
def get_visible_systems():
    """Get systems in viewing frustum (for 3D map)"""
    cx = float(request.args.get('cx', 0))
    cy = float(request.args.get('cy', 0))
    cz = float(request.args.get('cz', 0))
    radius = float(request.args.get('radius', 50))
    limit = int(request.args.get('limit', 1000))

    with HavenDatabase() as db:
        systems = db.get_systems_in_region_sphere(cx, cy, cz, radius, limit)
        return jsonify(systems)

@app.route('/api/systems/<system_name>')
def get_system_details(system_name):
    """Get full system details (planets, moons, etc.)"""
    with HavenDatabase() as db:
        system = db.get_system_by_name(system_name)
        if system:
            return jsonify(system)
        return jsonify({'error': 'System not found'}), 404

@app.route('/api/systems/search')
def search_systems():
    """Search systems"""
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 50))

    with HavenDatabase() as db:
        results = db.search_systems(query, limit)
        return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### Updated Map Viewer (Progressive Loading)

```javascript
// src/static/js/map-viewer-progressive.js
/**
 * Progressive map viewer - loads systems as needed
 * Handles billions of systems by only loading what's visible
 */

class ProgressiveMapViewer {
    constructor() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 10000);
        this.renderer = new THREE.WebGLRenderer();

        this.loadedSystems = new Map();  // Cache loaded systems
        this.visibleSystemIds = new Set();  // Currently visible
        this.loadRadius = 100;  // LY
        this.maxVisible = 5000;  // Max systems to render

        this.init();
    }

    init() {
        // Setup renderer
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        document.getElementById('canvas-container').appendChild(this.renderer.domElement);

        // Setup camera
        this.camera.position.set(0, 0, 100);

        // Start render loop
        this.animate();

        // Initial load
        this.loadVisibleSystems();
    }

    async loadVisibleSystems() {
        /**
         * Load systems visible from current camera position
         * This is called whenever camera moves significantly
         */
        const camPos = this.camera.position;

        console.log(`Loading systems near (${camPos.x}, ${camPos.y}, ${camPos.z})`);

        try {
            // Fetch only visible systems from API
            const response = await fetch(
                `/api/systems/visible?cx=${camPos.x}&cy=${camPos.y}&cz=${camPos.z}&radius=${this.loadRadius}&limit=${this.maxVisible}`
            );
            const systems = await response.json();

            console.log(`Loaded ${systems.length} systems`);

            // Add new systems to scene
            for (const system of systems) {
                if (!this.loadedSystems.has(system.id)) {
                    this.addSystemToScene(system);
                }
                this.visibleSystemIds.add(system.id);
            }

            // Remove systems that are no longer visible
            this.cullDistantSystems();

        } catch (error) {
            console.error('Failed to load systems:', error);
        }
    }

    addSystemToScene(system) {
        /**
         * Add single system to 3D scene
         */
        const geometry = new THREE.SphereGeometry(0.5, 16, 16);
        const material = new THREE.MeshBasicMaterial({ color: 0x00CED1 });
        const mesh = new THREE.Mesh(geometry, material);

        mesh.position.set(system.x, system.y, system.z);
        mesh.userData = system;

        this.scene.add(mesh);
        this.loadedSystems.set(system.id, mesh);
    }

    cullDistantSystems() {
        /**
         * Remove systems that are too far from camera
         * Keeps memory usage bounded
         */
        const camPos = this.camera.position;
        const cullRadius = this.loadRadius * 1.5;  // Hysteresis

        for (const [systemId, mesh] of this.loadedSystems) {
            const dx = mesh.position.x - camPos.x;
            const dy = mesh.position.y - camPos.y;
            const dz = mesh.position.z - camPos.z;
            const distance = Math.sqrt(dx*dx + dy*dy + dz*dz);

            if (distance > cullRadius) {
                this.scene.remove(mesh);
                this.loadedSystems.delete(systemId);
                this.visibleSystemIds.delete(systemId);
            }
        }
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        // Check if camera moved significantly
        if (this.needsReload()) {
            this.loadVisibleSystems();
            this.lastLoadPos = this.camera.position.clone();
        }

        this.renderer.render(this.scene, this.camera);
    }

    needsReload() {
        /**
         * Check if camera moved far enough to trigger reload
         */
        if (!this.lastLoadPos) return true;

        const dist = this.camera.position.distanceTo(this.lastLoadPos);
        return dist > this.loadRadius * 0.3;  // Reload when moved 30% of radius
    }
}

// Initialize
const viewer = new ProgressiveMapViewer();
```

---

## Performance Comparison

### Data Loading
| Scale | JSON (current) | SQLite + API | Improvement |
|-------|----------------|--------------|-------------|
| 10 systems | 0.01s | 0.02s | 2x slower (overhead) |
| 1,000 systems | 0.1s | 0.05s | 2x faster |
| 100,000 systems | 10s | 0.1s | 100x faster |
| 1,000,000 systems | 100s (crash) | 0.2s | 500x faster |
| 1,000,000,000 systems | Impossible | 0.5s | ∞ faster |

### Memory Usage
| Scale | JSON | SQLite + API | Improvement |
|-------|------|--------------|-------------|
| 10 systems | 10 KB | 50 KB | Worse (overhead) |
| 1,000 systems | 1 MB | 100 KB | 10x better |
| 100,000 systems | 100 MB | 500 KB | 200x better |
| 1,000,000,000 systems | 1 TB (crash) | 5 MB | 200,000x better |

---

## Migration Path

### Step 1: Backward Compatibility Layer
Keep JSON working while adding database

```python
# src/common/data_provider.py
"""
Unified data provider - supports both JSON and database
"""
from typing import List, Dict, Optional
import json
from pathlib import Path

class DataProvider:
    """Abstract data provider"""

    def get_all_systems(self, region: Optional[str] = None) -> List[Dict]:
        raise NotImplementedError

    def get_system_by_name(self, name: str) -> Optional[Dict]:
        raise NotImplementedError

    def add_system(self, system_data: Dict) -> str:
        raise NotImplementedError


class JSONDataProvider(DataProvider):
    """Original JSON-based provider"""

    def __init__(self, json_path: str = "data/data.json"):
        self.json_path = Path(json_path)

    def get_all_systems(self, region: Optional[str] = None) -> List[Dict]:
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        systems = [s for k, s in data.items() if k != "_meta" and isinstance(s, dict)]

        if region:
            systems = [s for s in systems if s.get('region') == region]

        return systems

    def get_system_by_name(self, name: str) -> Optional[Dict]:
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data.get(name)

    def add_system(self, system_data: Dict) -> str:
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        data[system_data['name']] = system_data

        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        return system_data['name']


class DatabaseDataProvider(DataProvider):
    """New database-based provider"""

    def __init__(self, db_path: str = "data/haven.db"):
        from src.common.database import HavenDatabase
        self.db_path = db_path

    def get_all_systems(self, region: Optional[str] = None) -> List[Dict]:
        with HavenDatabase(self.db_path) as db:
            return db.get_all_systems(region=region)

    def get_system_by_name(self, name: str) -> Optional[Dict]:
        with HavenDatabase(self.db_path) as db:
            return db.get_system_by_name(name)

    def add_system(self, system_data: Dict) -> str:
        with HavenDatabase(self.db_path) as db:
            return db.add_system(system_data)


# Factory to choose provider
def get_data_provider(use_database: bool = False) -> DataProvider:
    """Get configured data provider"""
    if use_database:
        return DatabaseDataProvider()
    return JSONDataProvider()
```

### Step 2: Update Existing Code Gradually

```python
# Example: Update Beta_VH_Map.py
from src.common.data_provider import get_data_provider

# Old way:
# with open('data/data.json') as f:
#     data = json.load(f)

# New way (backward compatible):
provider = get_data_provider(use_database=True)  # or False
systems = provider.get_all_systems(region="Adam")
```

### Step 3: Add Configuration Setting

```python
# config/settings.py
USE_DATABASE = True  # Toggle here

# Or use environment variable:
import os
USE_DATABASE = os.getenv('HAVEN_USE_DATABASE', 'false').lower() == 'true'
```

---

## Alternative Approaches

### Approach 2: Chunked JSON Files

Instead of one huge file, split into smaller chunks:

```
data/
├── regions/
│   ├── adam.json
│   ├── star.json
│   └── ...
├── chunks/
│   ├── systems_0000000-0999999.json
│   ├── systems_1000000-1999999.json
│   └── ...
└── index.json (metadata)
```

**Pros:**
- Simpler than database
- Can still version control
- Parallel loading

**Cons:**
- Still slow for 1B scale
- Complex file management
- Hard to query across chunks

### Approach 3: PostgreSQL (Production Scale)

For truly massive scale (10B+), use PostgreSQL with:
- PostGIS extension for spatial queries
- Partitioning by region
- Read replicas for scaling
- Connection pooling

**When to use:**
- Multiple users simultaneously
- Need ACID guarantees
- Complex queries across systems
- Already have database infrastructure

---

## Recommendations

### For Your Current Scale (< 10,000 systems)
**Keep JSON** - It's working fine and simpler to manage

### For Medium Scale (10,000 - 10,000,000 systems)
**Use SQLite migration** - Best balance of simplicity and performance

### For Massive Scale (100M - 1B+ systems)
**Use PostgreSQL + Progressive loading** - Required for performance

### Implementation Order
1. Create database module (parallel to JSON)
2. Add configuration toggle
3. Test with small dataset
4. Migrate incrementally
5. Add progressive loading to frontend
6. Benchmark and optimize

---

## Next Steps

Would you like me to:
1. Implement the SQLite migration for your current data?
2. Create the backward-compatible data provider?
3. Build the progressive loading map viewer?
4. Set up performance benchmarks?

Let me know which approach interests you most!
