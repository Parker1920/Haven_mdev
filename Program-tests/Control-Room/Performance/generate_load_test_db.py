#!/usr/bin/env python3
"""
Generate comprehensive load test database for Haven Starmap
Designed to test billion-scale architecture with realistic data

This generator creates a SQLite database following the billion-scale architecture
with configurable numbers of systems, planets, moons, and space stations.

Usage:
    python generate_load_test_db.py --systems 10000 --output data/haven_load_test.db
    python generate_load_test_db.py --systems 100000  # Stress test
    python generate_load_test_db.py --systems 1000000 # Million scale

Default: 10,000 systems with ~5 planets each, ~2 moons per planet, ~50% space stations
"""
import sqlite3
import argparse
import random
import sys
from pathlib import Path
from datetime import datetime
import time

# Add src to path for database imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from common.database import HavenDatabase


# ============================================================================
# CONFIGURATION - Realistic galactic data
# ============================================================================

# Regions for spatial partitioning (helps with queries)
REGIONS = [
    "Euclid Core", "Euclid Outer Rim", "Euclid Frontier",
    "Hilbert Dimension", "Calypso Expanse", "Hesperius Cluster",
    "Hyades Belt", "Ickjamatew Quadrant", "Budullangr Sector",
    "Elkupalos Territory", "Aptarkaba Region", "Ontiniangp Space",
    "Odiwagiri Domain", "Ogtialabi Nexus", "Muhacksonto Reach",
    "Hitonskyer Zone", "Rerasmutul Collective", "Isdoraijung Empire"
]

# Star system name prefixes (realistic NMS-style)
PREFIXES = [
    "ALPHA", "BETA", "GAMMA", "DELTA", "EPSILON", "ZETA", "ETA", "THETA",
    "IOTA", "KAPPA", "LAMBDA", "MU", "NU", "XI", "OMICRON", "PI",
    "RHO", "SIGMA", "TAU", "UPSILON", "PHI", "CHI", "PSI", "OMEGA",
    "KEPLER", "HUBBLE", "GAIA", "NOVA", "STELLAR", "COSMIC", "NEXUS",
    "VORTEX", "HORIZON", "QUANTUM", "PULSAR", "QUASAR", "NEBULA"
]

# Planet/Moon attributes
SENTINELS = ["None", "Low", "Moderate", "Aggressive", "Hostile", "Extreme"]
SENTINEL_WEIGHTS = [40, 30, 15, 10, 3, 2]  # Most systems are safe

FAUNA_LEVELS = ["None", "Sparse", "Low", "Moderate", "Abundant", "Rich", "Extreme diversity"]
FAUNA_WEIGHTS = [15, 20, 25, 20, 10, 7, 3]

FLORA_LEVELS = ["None", "Sparse", "Moderate", "Dense", "Abundant", "Lush vegetation"]
FLORA_WEIGHTS = [10, 20, 30, 20, 15, 5]

PLANET_PROPERTIES = [
    "Terrestrial, breathable atmosphere",
    "Gas giant, massive storms",
    "Desert world, extreme temperatures",
    "Ocean world, deep seas",
    "Ice planet, frozen surface",
    "Volcanic world, active tectonics",
    "Barren, no atmosphere",
    "Earth-like, habitable conditions",
    "Toxic atmosphere, hazardous",
    "Scorched world, intense radiation",
    "Frozen wasteland, sub-zero temperatures",
    "Paradise world, ideal conditions",
    "Exotic biome, anomalous features"
]

MOON_PROPERTIES = [
    "Rocky, airless",
    "Ice world",
    "Volcanic activity",
    "Thin atmosphere",
    "Dense atmosphere",
    "Tidally locked",
    "Frozen surface",
    "Barren moonscape",
    "Cratered terrain",
    "Geologically active"
]

MATERIALS = [
    "Iron, Carbon, Silicon",
    "Gold, Platinum, Silver",
    "Copper, Aluminum, Titanium",
    "Rare Earth Elements, Uranium",
    "Diamonds, Emeralds, Exotic crystals",
    "Hydrogen, Helium, Deuterium",
    "Activated Indium, Cadmium, Emeril",
    "Chromatic Metal, Pure Ferrite",
    "Magnetised Ferrite, Ammonia",
    "Dioxite, Phosphorus, Uranium",
    "Pyrite, Ammonia, Paraffinium",
    "Star Bulb, Solanium, Frost Crystal"
]

STATION_NAMES = [
    "Trading Post Alpha", "KEPLER Station", "Nexus Hub", "Commerce Center",
    "Research Outpost", "Mining Station", "Refinery Platform", "Observatory",
    "Military Garrison", "Diplomatic Waystation", "Supply Depot", "Shipyard",
    "Science Station", "Colonial Hub", "Sentinel Watchtower", "Freighter Dock"
]


# ============================================================================
# DATABASE GENERATOR
# ============================================================================

class LoadTestGenerator:
    """Generate comprehensive load test database"""
    
    def __init__(self, db_path: str, num_systems: int = 10000):
        """
        Initialize generator
        
        Args:
            db_path: Path to output database file
            num_systems: Number of star systems to generate
        """
        self.db_path = Path(db_path)
        self.num_systems = num_systems
        self.db = None
        
        # Statistics
        self.stats = {
            'systems': 0,
            'planets': 0,
            'moons': 0,
            'space_stations': 0,
            'start_time': None,
            'end_time': None
        }
    
    def generate(self):
        """Main generation process"""
        print(f"\n{'='*70}")
        print(f"  Haven Load Test Database Generator")
        print(f"{'='*70}")
        print(f"  Target: {self.num_systems:,} star systems")
        print(f"  Output: {self.db_path}")
        print(f"{'='*70}\n")
        
        self.stats['start_time'] = time.time()
        
        # Remove existing database
        if self.db_path.exists():
            print(f"⚠️  Removing existing database: {self.db_path}")
            self.db_path.unlink()
        
        # Create database with schema
        print("📊 Creating database schema...")
        self.db = HavenDatabase(str(self.db_path))
        
        # Generate data in batches for performance
        batch_size = 100
        with self.db as database:
            conn = database.conn
            cursor = conn.cursor()
            
            print(f"\n🌟 Generating {self.num_systems:,} star systems...")
            
            for batch_start in range(0, self.num_systems, batch_size):
                batch_end = min(batch_start + batch_size, self.num_systems)
                self._generate_batch(cursor, batch_start, batch_end)
                
                # Progress indicator
                progress = (batch_end / self.num_systems) * 100
                elapsed = time.time() - self.stats['start_time']
                rate = batch_end / elapsed if elapsed > 0 else 0
                eta = (self.num_systems - batch_end) / rate if rate > 0 else 0
                
                print(f"  Progress: {progress:5.1f}% | "
                      f"Systems: {batch_end:7,}/{self.num_systems:,} | "
                      f"Rate: {rate:6.1f}/s | "
                      f"ETA: {eta:5.1f}s", end='\r')
            
            print()  # New line after progress
            conn.commit()
        
        self.stats['end_time'] = time.time()
        self._print_summary()
    
    def _generate_batch(self, cursor: sqlite3.Cursor, start_idx: int, end_idx: int):
        """Generate a batch of systems with all related data"""
        for i in range(start_idx, end_idx):
            # Generate system
            system_id, system_name = self._generate_system(cursor, i)
            self.stats['systems'] += 1
            
            # Generate planets (1-10 per system, weighted toward 4-6)
            num_planets = random.choices([1,2,3,4,5,6,7,8,9,10], 
                                        weights=[5,8,12,18,20,18,10,5,3,1])[0]
            
            planet_ids = []
            for p in range(num_planets):
                planet_id = self._generate_planet(cursor, system_id, system_name, p)
                planet_ids.append(planet_id)
                self.stats['planets'] += 1
                
                # Generate moons (0-5 per planet, weighted toward 0-2)
                num_moons = random.choices([0,1,2,3,4,5], 
                                          weights=[30,25,20,15,7,3])[0]
                
                for m in range(num_moons):
                    self._generate_moon(cursor, planet_id, p, m)
                    self.stats['moons'] += 1
            
            # Generate space station (50% chance)
            if random.random() < 0.5:
                self._generate_space_station(cursor, system_id, system_name)
                self.stats['space_stations'] += 1
    
    def _generate_system(self, cursor: sqlite3.Cursor, index: int) -> tuple:
        """Generate a star system"""
        # Generate unique name (using index ensures uniqueness)
        prefix = random.choice(PREFIXES)
        system_name = f"{prefix}-{index:07d}"  # e.g., ALPHA-0000123
        system_id = f"SYS_{prefix}_{index}"
        
        # Spatial coordinates (large galactic space)
        # Distribute in 3D space: -500 to +500 for x/y, -100 to +100 for z
        x = random.uniform(-500, 500)
        y = random.uniform(-500, 500)
        z = random.uniform(-100, 100)
        
        # Region assignment (spatial partitioning for efficient queries)
        region = random.choice(REGIONS)
        
        # System-level attributes
        fauna = random.choices(FAUNA_LEVELS, weights=FAUNA_WEIGHTS)[0]
        flora = random.choices(FLORA_LEVELS, weights=FLORA_WEIGHTS)[0]
        sentinel = random.choices(SENTINELS, weights=SENTINEL_WEIGHTS)[0]
        materials = random.choice(MATERIALS)
        
        # Insert system
        cursor.execute("""
            INSERT INTO systems (id, name, x, y, z, region, fauna, flora, sentinel, materials)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (system_id, system_name, x, y, z, region, fauna, flora, sentinel, materials))
        
        return system_id, system_name
    
    def _generate_planet(self, cursor: sqlite3.Cursor, system_id: str, 
                        system_name: str, planet_idx: int) -> int:
        """Generate a planet"""
        planet_name = f"{system_name}-{chr(65 + planet_idx)}"  # A, B, C, etc.
        
        # Planet attributes
        sentinel = random.choices(SENTINELS, weights=SENTINEL_WEIGHTS)[0]
        fauna = random.choices(FAUNA_LEVELS, weights=FAUNA_WEIGHTS)[0]
        flora = random.choices(FLORA_LEVELS, weights=FLORA_WEIGHTS)[0]
        properties = random.choice(PLANET_PROPERTIES)
        materials = random.choice(MATERIALS)
        
        # Generate coordinates for base location
        base_lat = random.uniform(-90, 90)
        base_lon = random.uniform(-180, 180)
        base_location = f"Settlement-{planet_idx+1}: {base_lat:.2f}, {base_lon:.2f}"
        
        # Notes
        notes_options = [
            "Colonization candidate",
            "Resource rich extraction site",
            "Scientific research ongoing",
            "Hostile environment - extreme caution",
            "Exploration in progress",
            "Ancient ruins detected",
            "Anomalous readings present",
            "Paradise world - recommended",
            "High sentinel activity",
            "Rare materials detected"
        ]
        notes = random.choice(notes_options)
        
        # Insert planet
        cursor.execute("""
            INSERT INTO planets (system_id, name, sentinel, fauna, flora, 
                               properties, materials, base_location, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (system_id, planet_name, sentinel, fauna, flora, 
              properties, materials, base_location, notes))
        
        return cursor.lastrowid
    
    def _generate_moon(self, cursor: sqlite3.Cursor, planet_id: int, 
                      planet_idx: int, moon_idx: int):
        """Generate a moon"""
        moon_name = f"Moon-{chr(945 + moon_idx)}"  # Greek letters: α, β, γ, etc.
        
        # Moon attributes (generally less diverse than planets)
        sentinel = random.choices(SENTINELS, weights=[60,25,10,3,1,1])[0]  # Mostly safe
        fauna = random.choices(FAUNA_LEVELS, weights=[40,25,15,10,5,3,2])[0]  # Less fauna
        flora = random.choices(FLORA_LEVELS, weights=[35,25,20,10,7,3])[0]  # Less flora
        properties = random.choice(MOON_PROPERTIES)
        materials = random.choice(MATERIALS)
        
        # Orbit parameters (realistic ranges)
        orbit_radius = random.uniform(0.3, 1.5)  # Scaled units
        orbit_speed = random.uniform(0.02, 0.1)  # Angular velocity
        
        # Base location
        base_lat = random.uniform(-90, 90)
        base_lon = random.uniform(-180, 180)
        base_location = f"Outpost: {base_lat:.2f}, {base_lon:.2f}"
        
        # Notes
        notes = f"Natural satellite in stable orbit"
        
        # Insert moon
        cursor.execute("""
            INSERT INTO moons (planet_id, name, sentinel, fauna, flora, 
                             properties, materials, base_location, notes,
                             orbit_radius, orbit_speed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (planet_id, moon_name, sentinel, fauna, flora, 
              properties, materials, base_location, notes,
              orbit_radius, orbit_speed))
    
    def _generate_space_station(self, cursor: sqlite3.Cursor, 
                               system_id: str, system_name: str):
        """Generate a space station"""
        station_name = f"{system_name} {random.choice(STATION_NAMES)}"
        
        # Position in system (relative to star at origin)
        # Stations typically in inner to mid system
        x = random.uniform(-5, 5)
        y = random.uniform(-5, 5)
        z = random.uniform(-2, 2)
        
        # Insert space station
        cursor.execute("""
            INSERT INTO space_stations (system_id, name, x, y, z)
            VALUES (?, ?, ?, ?, ?)
        """, (system_id, station_name, x, y, z))
    
    def _print_summary(self):
        """Print generation summary"""
        elapsed = self.stats['end_time'] - self.stats['start_time']
        
        print(f"\n{'='*70}")
        print(f"  Generation Complete!")
        print(f"{'='*70}")
        print(f"  Systems:        {self.stats['systems']:,}")
        print(f"  Planets:        {self.stats['planets']:,}")
        print(f"  Moons:          {self.stats['moons']:,}")
        print(f"  Space Stations: {self.stats['space_stations']:,}")
        print(f"  Total Objects:  {sum([self.stats['systems'], self.stats['planets'], self.stats['moons'], self.stats['space_stations']]):,}")
        print(f"{'='*70}")
        print(f"  Time Elapsed:   {elapsed:.2f} seconds")
        print(f"  Systems/sec:    {self.stats['systems']/elapsed:.1f}")
        print(f"  Database Size:  {self.db_path.stat().st_size / (1024*1024):.2f} MB")
        print(f"{'='*70}")
        print(f"  Database: {self.db_path}")
        print(f"{'='*70}\n")
        
        # Query performance test
        print("🔍 Testing query performance...")
        with HavenDatabase(str(self.db_path)) as db:
            cursor = db.conn.cursor()
            
            # Test 1: Count systems
            start = time.time()
            cursor.execute("SELECT COUNT(*) FROM systems")
            count = cursor.fetchone()[0]
            t1 = time.time() - start
            print(f"  ✓ Count systems:     {count:,} in {t1*1000:.2f}ms")
            
            # Test 2: Count planets
            start = time.time()
            cursor.execute("SELECT COUNT(*) FROM planets")
            count = cursor.fetchone()[0]
            t2 = time.time() - start
            print(f"  ✓ Count planets:     {count:,} in {t2*1000:.2f}ms")
            
            # Test 3: Count moons
            start = time.time()
            cursor.execute("SELECT COUNT(*) FROM moons")
            count = cursor.fetchone()[0]
            t3 = time.time() - start
            print(f"  ✓ Count moons:       {count:,} in {t3*1000:.2f}ms")
            
            # Test 4: Spatial query (indexed)
            start = time.time()
            cursor.execute("""
                SELECT COUNT(*) FROM systems 
                WHERE x BETWEEN -10 AND 10 
                AND y BETWEEN -10 AND 10 
                AND z BETWEEN -10 AND 10
            """)
            count = cursor.fetchone()[0]
            t4 = time.time() - start
            print(f"  ✓ Spatial query:     {count:,} systems in {t4*1000:.2f}ms")
            
            # Test 5: Region query (indexed)
            start = time.time()
            cursor.execute("SELECT COUNT(*) FROM systems WHERE region = ?", (REGIONS[0],))
            count = cursor.fetchone()[0]
            t5 = time.time() - start
            print(f"  ✓ Region query:      {count:,} systems in {t5*1000:.2f}ms")
            
            # Test 6: Complex join (get system with all planets and moons)
            start = time.time()
            cursor.execute("""
                SELECT s.name, p.name, m.name
                FROM systems s
                LEFT JOIN planets p ON s.id = p.system_id
                LEFT JOIN moons m ON p.id = m.planet_id
                LIMIT 10
            """)
            results = cursor.fetchall()
            t6 = time.time() - start
            print(f"  ✓ Complex join:      {len(results)} results in {t6*1000:.2f}ms")
        
        print(f"\n{'='*70}")
        print("  ✅ Database ready for load testing!")
        print(f"{'='*70}\n")


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate Haven load test database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 10K systems (default) - Good for basic testing
  python generate_load_test_db.py
  
  # Generate 100K systems - Stress test
  python generate_load_test_db.py --systems 100000
  
  # Generate 1M systems - Million-scale test
  python generate_load_test_db.py --systems 1000000 --output data/haven_1M.db
  
  # Quick test with 1K systems
  python generate_load_test_db.py --systems 1000 --output data/haven_quick_test.db

Recommended Test Scales:
  - 1,000 systems   = ~10 MB    (Quick validation)
  - 10,000 systems  = ~100 MB   (Standard load test)
  - 100,000 systems = ~1 GB     (Stress test)
  - 1,000,000 systems = ~10 GB  (Million-scale test)
        """
    )
    
    parser.add_argument(
        '--systems',
        type=int,
        default=10000,
        help='Number of star systems to generate (default: 10,000)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='data/haven_load_test.db',
        help='Output database file path (default: data/haven_load_test.db)'
    )
    
    args = parser.parse_args()
    
    # Validate
    if args.systems < 1:
        print("❌ Error: Number of systems must be at least 1")
        return 1
    
    if args.systems > 10_000_000:
        print(f"⚠️  Warning: {args.systems:,} systems will create a very large database!")
        response = input("Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return 0
    
    # Generate
    generator = LoadTestGenerator(args.output, args.systems)
    generator.generate()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
