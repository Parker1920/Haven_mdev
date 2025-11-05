"""
Database wrapper for Haven system data
Provides SQLite-based storage for billion-scale system datasets

This module is part of the Master version of Haven, designed to handle
massive datasets that the public EXE version (JSON-based) cannot manage.
"""
import sqlite3
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class HavenDatabase:
    """
    SQLite database wrapper for Haven system data

    Provides CRUD operations for systems, planets, moons, and space stations.
    Designed to scale from 10 systems to 1 billion+ systems.

    Usage:
        with HavenDatabase("data/haven.db") as db:
            systems = db.get_all_systems(region="Adam")
            system = db.get_system_by_name("OOTLEFAR V")
            db.add_system(system_data)
    """

    def __init__(self, db_path: str = "data/haven.db"):
        """
        Initialize database connection

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.conn = None
        self._ensure_database_exists()

    def __enter__(self):
        """Context manager entry - opens database connection"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Return dict-like rows
        # Enable foreign keys for referential integrity
        self.conn.execute("PRAGMA foreign_keys = ON")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - closes database connection"""
        if self.conn:
            self.conn.close()

    def _ensure_database_exists(self):
        """Create database and schema if it doesn't exist"""
        if not self.db_path.exists():
            logger.info(f"Creating new database at {self.db_path}")
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(str(self.db_path)) as conn:
                self._create_schema(conn)
                self._create_indexes(conn)
                logger.info("Database schema created successfully")

    def _create_schema(self, conn: sqlite3.Connection):
        """Create database tables"""
        cursor = conn.cursor()

        # Systems table - main star systems
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
                FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE,
                UNIQUE(system_id, name)
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

        # Metadata table for tracking database version and stats
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS _metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Initialize metadata
        cursor.execute("""
            INSERT OR IGNORE INTO _metadata (key, value)
            VALUES ('version', '1.0.0')
        """)
        cursor.execute("""
            INSERT OR IGNORE INTO _metadata (key, value)
            VALUES ('last_import', '')
        """)

        conn.commit()

    def _create_indexes(self, conn: sqlite3.Connection):
        """Create performance indexes"""
        cursor = conn.cursor()

        # Systems indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_systems_region ON systems(region)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_systems_coords ON systems(x, y, z)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_systems_name ON systems(name)")

        # Planets indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_planets_system ON planets(system_id)")

        # Moons indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_moons_planet ON moons(planet_id)")

        # Space stations indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_space_stations_system ON space_stations(system_id)")

        conn.commit()

    # ========== QUERY METHODS ==========

    def get_all_systems(self, region: Optional[str] = None) -> List[Dict]:
        """
        Get all systems, optionally filtered by region

        NOTE: At large scales (1M+), use get_systems_paginated() instead

        Args:
            region: Optional region filter

        Returns:
            List of system dictionaries
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
        Get systems with pagination (recommended for large datasets)

        Args:
            page: Page number (1-indexed)
            per_page: Systems per page
            region: Optional region filter

        Returns:
            {
                'systems': [...],
                'total': 1000000,
                'page': 1,
                'per_page': 100,
                'total_pages': 10000
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

        This is the KEY query for billion-scale systems - only load what's visible

        Args:
            cx, cy, cz: Center coordinates
            radius: Radius in same units as coordinates
            limit: Maximum systems to return

        Returns:
            List of systems within sphere, sorted by distance
        """
        cursor = self.conn.cursor()

        # Use bounding box query first (fast with spatial index)
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
            limit * 2  # Get extra for sphere filtering
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

        # Sort by distance and limit
        systems.sort(key=lambda s: s['distance'])
        return systems[:limit]

    def get_system_by_name(self, name: str) -> Optional[Dict]:
        """
        Get single system by name with all related data

        Args:
            name: System name

        Returns:
            System dictionary with planets, moons, and space station
            None if not found
        """
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

    def get_system_by_id(self, system_id: str) -> Optional[Dict]:
        """Get system by ID instead of name"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM systems WHERE id = ?", (system_id,))
        row = cursor.fetchone()
        if not row:
            return None

        system = dict(row)
        # Get full system data like get_system_by_name
        return self.get_system_by_name(system['name'])

    def search_systems(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Search systems by name, materials, or attributes

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching systems
        """
        cursor = self.conn.cursor()

        search_pattern = f"%{query}%"
        cursor.execute("""
            SELECT * FROM systems
            WHERE name LIKE ?
               OR materials LIKE ?
               OR attributes LIKE ?
            ORDER BY name
            LIMIT ?
        """, (search_pattern, search_pattern, search_pattern, limit))

        return [dict(row) for row in cursor.fetchall()]

    def get_regions(self) -> List[str]:
        """Get list of all unique regions"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT region FROM systems ORDER BY region")
        return [row[0] for row in cursor.fetchall()]

    def get_total_count(self) -> int:
        """Get total number of systems"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM systems")
        return cursor.fetchone()[0]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics

        Returns:
            {
                'total_systems': 1000000,
                'total_planets': 5000000,
                'total_moons': 10000000,
                'total_stations': 500000,
                'regions': ['Adam', 'Star', ...],
                'database_size_mb': 1024.5
            }
        """
        cursor = self.conn.cursor()

        stats = {}

        # Count systems
        cursor.execute("SELECT COUNT(*) FROM systems")
        stats['total_systems'] = cursor.fetchone()[0]

        # Count planets
        cursor.execute("SELECT COUNT(*) FROM planets")
        stats['total_planets'] = cursor.fetchone()[0]

        # Count moons
        cursor.execute("SELECT COUNT(*) FROM moons")
        stats['total_moons'] = cursor.fetchone()[0]

        # Count space stations
        cursor.execute("SELECT COUNT(*) FROM space_stations")
        stats['total_stations'] = cursor.fetchone()[0]

        # Get regions
        stats['regions'] = self.get_regions()

        # Database file size
        if self.db_path.exists():
            stats['database_size_mb'] = self.db_path.stat().st_size / (1024 * 1024)
        else:
            stats['database_size_mb'] = 0

        return stats

    # ========== WRITE METHODS ==========

    def add_system(self, system_data: Dict) -> str:
        """
        Add new system to database

        Args:
            system_data: System dictionary (same format as JSON)

        Returns:
            System ID

        Raises:
            sqlite3.IntegrityError if system already exists
        """
        cursor = self.conn.cursor()

        system_id = system_data.get('id')
        if not system_id:
            # Generate ID if not provided
            import time
            system_id = f"SYS_{system_data['region'].upper()}_{int(time.time())}"

        cursor.execute("""
            INSERT INTO systems
            (id, name, x, y, z, region, fauna, flora, sentinel,
             materials, base_location, photo, attributes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            system_id,
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

        # Add planets if provided
        for planet in system_data.get('planets', []):
            self._add_planet(cursor, system_id, planet)

        # Add space station if provided
        if 'space_station' in system_data and system_data['space_station'] is not None:
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
        """
        Update system fields

        Args:
            system_id: System ID
            updates: Dictionary of fields to update
        """
        cursor = self.conn.cursor()

        # Build dynamic UPDATE query for simple fields
        simple_fields = ['name', 'x', 'y', 'z', 'region', 'fauna', 'flora',
                        'sentinel', 'materials', 'base_location', 'photo', 'attributes']

        fields = []
        values = []
        for key, value in updates.items():
            if key in simple_fields:
                fields.append(f"{key} = ?")
                values.append(value)

        if fields:
            values.append(system_id)
            cursor.execute(f"""
                UPDATE systems
                SET {', '.join(fields)}, modified_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, values)

        # Handle planets separately if provided
        if 'planets' in updates:
            # Delete existing planets (cascade will delete moons)
            cursor.execute("DELETE FROM planets WHERE system_id = ?", (system_id,))
            # Add new planets
            for planet in updates['planets']:
                self._add_planet(cursor, system_id, planet)

        # Handle space station if provided
        if 'space_station' in updates:
            cursor.execute("DELETE FROM space_stations WHERE system_id = ?", (system_id,))
            if updates['space_station']:
                self._add_space_station(cursor, system_id, updates['space_station'])

        self.conn.commit()

    def delete_system(self, system_id: str):
        """
        Delete system and all related data

        Foreign key cascade will automatically delete:
        - Planets
        - Moons (via planet deletion)
        - Space stations

        Args:
            system_id: System ID
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM systems WHERE id = ?", (system_id,))
        self.conn.commit()

    def system_exists(self, name: str) -> bool:
        """Check if system with given name exists"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM systems WHERE name = ? LIMIT 1", (name,))
        return cursor.fetchone() is not None

    # ========== METADATA METHODS ==========

    def set_metadata(self, key: str, value: str):
        """Set metadata key-value pair"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO _metadata (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (key, value))
        self.conn.commit()

    def get_metadata(self, key: str) -> Optional[str]:
        """Get metadata value by key"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM _metadata WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else None


# ========== USAGE EXAMPLES ==========

def example_usage():
    """Example usage of HavenDatabase"""

    # Basic operations
    with HavenDatabase() as db:
        # Get all systems in Adam region
        systems = db.get_all_systems(region="Adam")
        print(f"Found {len(systems)} systems in Adam region")

        # Get single system with all data
        system = db.get_system_by_name("OOTLEFAR V")
        if system:
            print(f"System: {system['name']}")
            print(f"  Planets: {len(system.get('planets', []))}")
            for planet in system.get('planets', []):
                print(f"    - {planet['name']}: {len(planet.get('moons', []))} moons")

        # Search
        results = db.search_systems("Cadmium")
        print(f"Found {len(results)} systems with Cadmium")

        # Statistics
        stats = db.get_statistics()
        print(f"Database stats:")
        print(f"  Systems: {stats['total_systems']}")
        print(f"  Planets: {stats['total_planets']}")
        print(f"  Moons: {stats['total_moons']}")
        print(f"  Size: {stats['database_size_mb']:.2f} MB")


if __name__ == "__main__":
    example_usage()
