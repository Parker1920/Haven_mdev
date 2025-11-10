#!/usr/bin/env python3
"""
Create VH-Database.db - The Official Haven Map Database
Ready for 1 billion+ star systems

This script creates an empty, optimized database shell ready to be
populated with Haven star system data. It includes:
- Full schema for systems, planets, moons, space stations
- Spatial indexes for coordinate queries
- Full-text search for system names
- Audit logging capabilities
- Billion-scale query optimization
"""

import sqlite3
from pathlib import Path
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def create_vh_database():
    """Create the VH-Database.db empty shell"""
    
    # Paths
    project_root = Path(__file__).parent
    db_path = project_root / "data" / "VH-Database.db"
    backup_dir = project_root / "data" / "backups"
    
    # Ensure directory exists
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Remove old database if it exists
    if db_path.exists():
        logger.info(f"Removing existing database: {db_path}")
        db_path.unlink()
    
    logger.info(f"Creating VH-Database at: {db_path}")
    
    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.cursor()
        
        # Enable foreign keys for referential integrity
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Enable WAL mode for better concurrency at scale
        cursor.execute("PRAGMA journal_mode = WAL")
        
        # Optimize for billion-scale operations
        cursor.execute("PRAGMA synchronous = NORMAL")  # Balance speed/safety
        cursor.execute("PRAGMA cache_size = -64000")   # 64MB cache
        cursor.execute("PRAGMA temp_store = MEMORY")   # Use memory for temp ops
        
        logger.info("Creating schema...")
        
        # ============================================================
        # SYSTEMS TABLE - The core of the map
        # ============================================================
        cursor.execute("""
            CREATE TABLE systems (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE COLLATE NOCASE,
                x REAL NOT NULL,
                y REAL NOT NULL,
                z REAL NOT NULL,
                region TEXT NOT NULL,
                
                -- Biological data
                fauna TEXT,
                flora TEXT,
                sentinel TEXT,
                
                -- Resources
                materials TEXT,
                
                -- Player locations
                base_location TEXT,
                photo TEXT,
                
                -- Metadata
                attributes TEXT,  -- JSON for extensibility
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                modified_by TEXT,
                
                -- Flags
                is_complete BOOLEAN DEFAULT 0,
                notes TEXT
            )
        """)
        
        # ============================================================
        # PLANETS TABLE - Child of systems
        # ============================================================
        cursor.execute("""
            CREATE TABLE planets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                system_id TEXT NOT NULL,
                name TEXT NOT NULL,
                designation TEXT,  -- e.g., "A", "B", "C"
                
                -- Biological data
                sentinel TEXT,
                fauna TEXT,
                flora TEXT,
                
                -- Environmental
                properties TEXT,
                materials TEXT,
                
                -- Player locations
                base_location TEXT,
                photo TEXT,
                
                -- Planetary stats
                orbit_radius REAL,
                orbit_speed REAL,
                rotation_period REAL,
                axial_tilt REAL,
                
                -- Metadata
                attributes TEXT,  -- JSON for extensibility
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                modified_by TEXT,
                
                -- Flags
                is_complete BOOLEAN DEFAULT 0,
                notes TEXT,
                
                FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE
            )
        """)
        
        # ============================================================
        # MOONS TABLE - Child of planets
        # ============================================================
        cursor.execute("""
            CREATE TABLE moons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                planet_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                
                -- Biological data
                sentinel TEXT,
                fauna TEXT,
                flora TEXT,
                
                -- Environmental
                properties TEXT,
                materials TEXT,
                
                -- Player locations
                base_location TEXT,
                photo TEXT,
                
                -- Orbital mechanics
                orbit_radius REAL,
                orbit_speed REAL,
                rotation_period REAL,
                axial_tilt REAL,
                
                -- Metadata
                attributes TEXT,  -- JSON for extensibility
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                modified_by TEXT,
                
                -- Flags
                is_complete BOOLEAN DEFAULT 0,
                notes TEXT,
                
                FOREIGN KEY (planet_id) REFERENCES planets(id) ON DELETE CASCADE
            )
        """)
        
        # ============================================================
        # SPACE STATIONS TABLE - Points of interest in systems
        # ============================================================
        cursor.execute("""
            CREATE TABLE space_stations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                system_id TEXT NOT NULL,
                name TEXT NOT NULL,
                
                -- Type and classification
                station_type TEXT,  -- "Trading", "Scientific", "Military", etc.
                faction TEXT,
                
                -- Location
                x REAL,
                y REAL,
                z REAL,
                
                -- Services
                services TEXT,  -- JSON array of available services
                trade_goods TEXT,  -- JSON
                
                -- Metadata
                attributes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                modified_by TEXT,
                
                notes TEXT,
                
                FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE
            )
        """)
        
        # ============================================================
        # METADATA TABLE - Database-wide configuration
        # ============================================================
        cursor.execute("""
            CREATE TABLE metadata (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Initialize metadata
        cursor.execute("""
            INSERT INTO metadata (key, value) VALUES 
            ('db_version', '1.0'),
            ('db_name', 'VH-Database'),
            ('db_purpose', 'Official Haven Map - Billion-scale star system database'),
            ('created_date', ?),
            ('last_backup', ?),
            ('total_systems', '0'),
            ('schema_generation', '1')
        """, (datetime.now().isoformat(), datetime.now().isoformat()))
        
        logger.info("Creating indexes for performance...")
        
        # ============================================================
        # INDEXES - Critical for billion-scale queries
        # ============================================================
        
        # System lookups
        cursor.execute("CREATE INDEX idx_systems_name ON systems(name COLLATE NOCASE)")
        cursor.execute("CREATE INDEX idx_systems_region ON systems(region)")
        
        # Spatial indexes (for "find nearby systems" queries)
        cursor.execute("CREATE INDEX idx_systems_x ON systems(x)")
        cursor.execute("CREATE INDEX idx_systems_y ON systems(y)")
        cursor.execute("CREATE INDEX idx_systems_z ON systems(z)")
        cursor.execute("CREATE INDEX idx_systems_xyz ON systems(x, y, z)")
        
        # Planet lookups
        cursor.execute("CREATE INDEX idx_planets_system ON planets(system_id)")
        cursor.execute("CREATE INDEX idx_planets_name ON planets(name COLLATE NOCASE)")
        cursor.execute("CREATE INDEX idx_planets_system_name ON planets(system_id, name)")
        
        # Moon lookups
        cursor.execute("CREATE INDEX idx_moons_planet ON moons(planet_id)")
        cursor.execute("CREATE INDEX idx_moons_name ON moons(name COLLATE NOCASE)")
        
        # Station lookups
        cursor.execute("CREATE INDEX idx_stations_system ON space_stations(system_id)")
        cursor.execute("CREATE INDEX idx_stations_type ON space_stations(station_type)")
        
        # Timestamps for time-range queries
        cursor.execute("CREATE INDEX idx_systems_created ON systems(created_at)")
        cursor.execute("CREATE INDEX idx_systems_modified ON systems(modified_at)")
        cursor.execute("CREATE INDEX idx_planets_created ON planets(created_at)")
        cursor.execute("CREATE INDEX idx_moons_created ON moons(created_at)")
        
        logger.info("Creating full-text search indexes...")
        
        # ============================================================
        # FULL-TEXT SEARCH - For system name queries
        # ============================================================
        cursor.execute("""
            CREATE VIRTUAL TABLE systems_fts USING fts5(
                system_id UNINDEXED,
                name,
                region,
                content='systems',
                content_rowid='rowid'
            )
        """)
        
        cursor.execute("""
            CREATE VIRTUAL TABLE planets_fts USING fts5(
                planet_id UNINDEXED,
                name,
                content='planets',
                content_rowid='id'
            )
        """)
        
        logger.info("Creating triggers for full-text search maintenance...")
        
        # ============================================================
        # TRIGGERS - Keep FTS indexes in sync
        # ============================================================
        cursor.execute("""
            CREATE TRIGGER systems_insert_fts AFTER INSERT ON systems BEGIN
                INSERT INTO systems_fts(rowid, system_id, name, region) 
                VALUES (new.rowid, new.id, new.name, new.region);
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER systems_delete_fts AFTER DELETE ON systems BEGIN
                DELETE FROM systems_fts WHERE rowid = old.rowid;
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER systems_update_fts AFTER UPDATE ON systems BEGIN
                DELETE FROM systems_fts WHERE rowid = old.rowid;
                INSERT INTO systems_fts(rowid, system_id, name, region) 
                VALUES (new.rowid, new.id, new.name, new.region);
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER planets_insert_fts AFTER INSERT ON planets BEGIN
                INSERT INTO planets_fts(rowid, planet_id, name) 
                VALUES (new.id, new.id, new.name);
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER planets_delete_fts AFTER DELETE ON planets BEGIN
                DELETE FROM planets_fts WHERE rowid = old.id;
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER planets_update_fts AFTER UPDATE ON planets BEGIN
                DELETE FROM planets_fts WHERE rowid = old.id;
                INSERT INTO planets_fts(rowid, planet_id, name) 
                VALUES (new.id, new.id, new.name);
            END
        """)
        
        logger.info("Creating update timestamp triggers...")
        
        # ============================================================
        # UPDATE TRIGGERS - Auto-update modified_at
        # ============================================================
        cursor.execute("""
            CREATE TRIGGER systems_update_timestamp AFTER UPDATE ON systems
            FOR EACH ROW WHEN NEW.modified_at = OLD.modified_at
            BEGIN
                UPDATE systems SET modified_at = CURRENT_TIMESTAMP 
                WHERE id = NEW.id;
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER planets_update_timestamp AFTER UPDATE ON planets
            FOR EACH ROW WHEN NEW.modified_at = OLD.modified_at
            BEGIN
                UPDATE planets SET modified_at = CURRENT_TIMESTAMP 
                WHERE id = NEW.id;
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER moons_update_timestamp AFTER UPDATE ON moons
            FOR EACH ROW WHEN NEW.modified_at = OLD.modified_at
            BEGIN
                UPDATE moons SET modified_at = CURRENT_TIMESTAMP 
                WHERE id = NEW.id;
            END
        """)
        
        conn.commit()
        
        logger.info("✅ VH-Database created successfully!")
        logger.info(f"Location: {db_path}")
        logger.info(f"Size: {db_path.stat().st_size / 1024:.1f} KB")
        logger.info("Status: Empty and ready for star system population")
        logger.info("\nFeatures:")
        logger.info("  ✓ Full billion-scale schema")
        logger.info("  ✓ Spatial indexes (x, y, z)")
        logger.info("  ✓ Full-text search for system/planet names")
        logger.info("  ✓ Foreign key constraints")
        logger.info("  ✓ Automatic timestamp maintenance")
        logger.info("  ✓ Audit logging (created_by, modified_by)")
        logger.info("  ✓ WAL mode for better concurrency")
        logger.info("  ✓ Query optimization pragmas")
        logger.info("\nReady for import from:")
        logger.info("  - JSON files (legacy exe/mobile data)")
        logger.info("  - Manual wizard entry")
        logger.info("  - Bulk data import")


if __name__ == '__main__':
    create_vh_database()
