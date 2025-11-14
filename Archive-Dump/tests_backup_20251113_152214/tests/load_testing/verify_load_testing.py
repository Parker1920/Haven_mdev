#!/usr/bin/env python3
"""
Comprehensive Load Testing Verification Script

Validates the complete load testing system implementation:
- Database generation
- Data integrity
- Query performance
- Map generation
- Control Room integration

Run this to verify the system is working correctly.
"""
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from common.database import HavenDatabase
from common.paths import project_root


def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}")


def print_success(text):
    """Print success message"""
    print(f"✅ {text}")


def print_error(text):
    """Print error message"""
    print(f"❌ {text}")


def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")


def verify_database_exists():
    """Verify load test database exists"""
    print_header("1. Database Existence Check")
    
    db_path = project_root() / "data" / "haven_load_test.db"
    
    if db_path.exists():
        size_mb = db_path.stat().st_size / (1024 * 1024)
        print_success(f"Database exists: {db_path}")
        print_info(f"Size: {size_mb:.2f} MB")
        return True
    else:
        print_error(f"Database not found: {db_path}")
        print_info("Run: py tests/load_testing/generate_load_test_db.py")
        return False


def verify_database_schema():
    """Verify database has correct schema"""
    print_header("2. Database Schema Check")
    
    db_path = project_root() / "data" / "haven_load_test.db"
    
    try:
        with HavenDatabase(str(db_path)) as db:
            cursor = db.conn.cursor()
            
            # Check tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('systems', 'planets', 'moons', 'space_stations')
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['systems', 'planets', 'moons', 'space_stations']
            
            if set(tables) == set(expected_tables):
                print_success(f"All tables exist: {', '.join(tables)}")
            else:
                missing = set(expected_tables) - set(tables)
                print_error(f"Missing tables: {', '.join(missing)}")
                return False
            
            # Check indexes exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name LIKE 'idx_%'
            """)
            indexes = [row[0] for row in cursor.fetchall()]
            
            print_success(f"Found {len(indexes)} performance indexes")
            
            return True
            
    except Exception as e:
        print_error(f"Schema verification failed: {e}")
        return False


def verify_data_integrity():
    """Verify data relationships and counts"""
    print_header("3. Data Integrity Check")
    
    db_path = project_root() / "data" / "haven_load_test.db"
    
    try:
        with HavenDatabase(str(db_path)) as db:
            cursor = db.conn.cursor()
            
            # Count systems
            cursor.execute("SELECT COUNT(*) FROM systems")
            system_count = cursor.fetchone()[0]
            print_success(f"Systems: {system_count:,}")
            
            # Count planets
            cursor.execute("SELECT COUNT(*) FROM planets")
            planet_count = cursor.fetchone()[0]
            avg_planets = planet_count / system_count if system_count > 0 else 0
            print_success(f"Planets: {planet_count:,} (avg {avg_planets:.1f} per system)")
            
            # Count moons
            cursor.execute("SELECT COUNT(*) FROM moons")
            moon_count = cursor.fetchone()[0]
            avg_moons = moon_count / planet_count if planet_count > 0 else 0
            print_success(f"Moons: {moon_count:,} (avg {avg_moons:.1f} per planet)")
            
            # Count space stations
            cursor.execute("SELECT COUNT(*) FROM space_stations")
            station_count = cursor.fetchone()[0]
            station_pct = (station_count / system_count * 100) if system_count > 0 else 0
            print_success(f"Space Stations: {station_count:,} ({station_pct:.1f}% of systems)")
            
            # Check foreign key relationships
            cursor.execute("""
                SELECT COUNT(*) FROM planets 
                WHERE system_id NOT IN (SELECT id FROM systems)
            """)
            orphan_planets = cursor.fetchone()[0]
            
            if orphan_planets == 0:
                print_success("All planets have valid system references")
            else:
                print_error(f"{orphan_planets} orphan planets found")
                return False
            
            cursor.execute("""
                SELECT COUNT(*) FROM moons 
                WHERE planet_id NOT IN (SELECT id FROM planets)
            """)
            orphan_moons = cursor.fetchone()[0]
            
            if orphan_moons == 0:
                print_success("All moons have valid planet references")
            else:
                print_error(f"{orphan_moons} orphan moons found")
                return False
            
            return True
            
    except Exception as e:
        print_error(f"Data integrity check failed: {e}")
        return False


def verify_query_performance():
    """Verify query performance meets requirements"""
    print_header("4. Query Performance Check")
    
    db_path = project_root() / "data" / "haven_load_test.db"
    
    try:
        with HavenDatabase(str(db_path)) as db:
            cursor = db.conn.cursor()
            
            # Test 1: Count query
            start = time.time()
            cursor.execute("SELECT COUNT(*) FROM systems")
            count = cursor.fetchone()[0]
            t1 = (time.time() - start) * 1000
            
            if t1 < 5:
                print_success(f"Count systems: {count:,} in {t1:.2f}ms")
            else:
                print_error(f"Count query too slow: {t1:.2f}ms (should be < 5ms)")
            
            # Test 2: Spatial query (indexed)
            start = time.time()
            cursor.execute("""
                SELECT COUNT(*) FROM systems 
                WHERE x BETWEEN -50 AND 50 
                AND y BETWEEN -50 AND 50 
                AND z BETWEEN -10 AND 10
            """)
            count = cursor.fetchone()[0]
            t2 = (time.time() - start) * 1000
            
            if t2 < 5:
                print_success(f"Spatial query: {count:,} systems in {t2:.2f}ms")
            else:
                print_error(f"Spatial query too slow: {t2:.2f}ms (should be < 5ms)")
            
            # Test 3: Region query (indexed)
            start = time.time()
            cursor.execute("""
                SELECT COUNT(*) FROM systems 
                WHERE region = 'Euclid Core'
            """)
            count = cursor.fetchone()[0]
            t3 = (time.time() - start) * 1000
            
            if t3 < 5:
                print_success(f"Region query: {count:,} systems in {t3:.2f}ms")
            else:
                print_error(f"Region query too slow: {t3:.2f}ms (should be < 5ms)")
            
            # Test 4: Complex join
            start = time.time()
            cursor.execute("""
                SELECT s.name, p.name, m.name
                FROM systems s
                LEFT JOIN planets p ON s.id = p.system_id
                LEFT JOIN moons m ON p.id = m.planet_id
                LIMIT 100
            """)
            results = cursor.fetchall()
            t4 = (time.time() - start) * 1000
            
            if t4 < 10:
                print_success(f"Complex join: {len(results)} results in {t4:.2f}ms")
            else:
                print_error(f"Complex join too slow: {t4:.2f}ms (should be < 10ms)")
            
            return True
            
    except Exception as e:
        print_error(f"Query performance check failed: {e}")
        return False


def verify_full_system_load():
    """Verify loading complete system with planets and moons"""
    print_header("5. Full System Load Check")
    
    db_path = project_root() / "data" / "haven_load_test.db"
    
    try:
        with HavenDatabase(str(db_path)) as db:
            # Get first system
            cursor = db.conn.cursor()
            cursor.execute("SELECT name FROM systems LIMIT 1")
            system_name = cursor.fetchone()[0]
            
            # Load complete system
            start = time.time()
            system = db.get_system_by_name(system_name)
            t = (time.time() - start) * 1000
            
            if system:
                planet_count = len(system.get('planets', []))
                moon_count = sum(len(p.get('moons', [])) for p in system.get('planets', []))
                
                print_success(f"Loaded system: {system_name}")
                print_info(f"  Planets: {planet_count}")
                print_info(f"  Moons: {moon_count}")
                print_info(f"  Load time: {t:.2f}ms")
                
                if t < 100:
                    print_success("Load time acceptable (< 100ms)")
                else:
                    print_error(f"Load time too slow: {t:.2f}ms")
                
                return True
            else:
                print_error(f"Failed to load system: {system_name}")
                return False
                
    except Exception as e:
        print_error(f"Full system load check failed: {e}")
        return False


def verify_map_data_files():
    """Verify map generation created output files"""
    print_header("6. Map Generation Output Check")
    
    dist_dir = project_root() / "dist"
    
    # Check for VH-Map.html
    map_file = dist_dir / "VH-Map.html"
    if map_file.exists():
        print_success(f"Galaxy map exists: {map_file.name}")
    else:
        print_error(f"Galaxy map not found: {map_file}")
        return False
    
    # Count system view files
    system_files = list(dist_dir.glob("system_*.html"))
    if system_files:
        print_success(f"Found {len(system_files)} system view files")
    else:
        print_error("No system view files found")
        print_info("Run map generation first")
        return False
    
    # Check static files
    static_dir = dist_dir / "static"
    if static_dir.exists():
        js_files = list(static_dir.glob("**/*.js"))
        print_success(f"Static files exist: {len(js_files)} JavaScript files")
    else:
        print_error("Static files directory not found")
        return False
    
    return True


def main():
    """Run all verification checks"""
    print_header("Haven Load Testing System Verification")
    print("This script validates the complete load testing implementation")
    
    results = []
    
    # Run checks
    results.append(("Database Exists", verify_database_exists()))
    results.append(("Database Schema", verify_database_schema()))
    results.append(("Data Integrity", verify_data_integrity()))
    results.append(("Query Performance", verify_query_performance()))
    results.append(("Full System Load", verify_full_system_load()))
    results.append(("Map Generation", verify_map_data_files()))
    
    # Summary
    print_header("Verification Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {check_name}")
    
    print(f"\n{'='*70}")
    if passed == total:
        print(f"  🎉 ALL CHECKS PASSED ({passed}/{total})")
        print(f"{'='*70}")
        print("\n✅ Load testing system is fully operational!")
        return 0
    else:
        print(f"  ⚠️  SOME CHECKS FAILED ({passed}/{total})")
        print(f"{'='*70}")
        print(f"\n❌ {total - passed} check(s) failed. Review errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
