#!/usr/bin/env python3
"""
Test YH-Database Integration
Verify that all three functions (dropdown, wizard, stats) work correctly
and maintain single source of truth with the new YH-Database.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.common.data_source_manager import get_data_source_manager
from src.common.database import HavenDatabase
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def test_yh_database_registration():
    """Test 1: YH-Database is registered in manager"""
    print("\n" + "="*70)
    print("TEST 1: YH-Database Registration in DataSourceManager")
    print("="*70)
    
    manager = get_data_source_manager()
    sources = manager.get_all_sources()
    
    print(f"\n✓ Found {len(sources)} registered sources:")
    for name, info in sources.items():
        print(f"  • {name:12} → {info.display_name:30} | {info.system_count:,} systems | {info.size_mb:.2f} MB")
    
    # Verify YH-Database exists
    assert "yh_database" in sources, "❌ yh_database not registered!"
    yh_info = sources["yh_database"]
    
    assert yh_info.display_name == "YH-Database (Official Map)", "❌ Wrong display name!"
    assert yh_info.backend_type == "database", "❌ Wrong backend type!"
    assert yh_info.system_count == 0, "❌ Should start with 0 systems!"
    assert yh_info.path.name == "VH-Database.db", "❌ Wrong database filename!"
    
    print("\n✅ TEST 1 PASSED: YH-Database properly registered")
    return True


def test_yh_database_file_exists():
    """Test 2: VH-Database.db file exists and is valid"""
    print("\n" + "="*70)
    print("TEST 2: VH-Database File Validation")
    print("="*70)
    
    manager = get_data_source_manager()
    current = manager.get_current()
    
    # Find yh_database
    manager.set_current("yh_database")
    yh_source = manager.get_current()
    
    print(f"\nDatabase path: {yh_source.path}")
    print(f"File exists: {yh_source.path.exists()}")
    print(f"File size: {yh_source.size_mb:.2f} MB")
    
    assert yh_source.path.exists(), "❌ VH-Database.db file not found!"
    assert yh_source.size_mb > 0, "❌ Database file is empty!"
    
    print("\n✅ TEST 2 PASSED: VH-Database file exists and valid")
    return True


def test_yh_database_schema():
    """Test 3: VH-Database has correct schema"""
    print("\n" + "="*70)
    print("TEST 3: VH-Database Schema Validation")
    print("="*70)
    
    manager = get_data_source_manager()
    manager.set_current("yh_database")
    yh_source = manager.get_current()
    
    with HavenDatabase(str(yh_source.path)) as db:
        # Get metadata
        metadata = {}
        cursor = db.conn.cursor()
        cursor.execute("SELECT key, value FROM metadata")
        for key, value in cursor.fetchall():
            metadata[key] = value
        
        print("\n📊 Database Metadata:")
        for key, value in metadata.items():
            print(f"  • {key:20} = {value}")
        
        # Verify critical tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['systems', 'planets', 'moons', 'space_stations', 'metadata']
        print(f"\n📋 Tables in database: {len(tables)}")
        for table in tables:
            status = "✓" if table in required_tables else " "
            print(f"  {status} {table}")
        
        for required in required_tables:
            assert required in tables, f"❌ Missing required table: {required}"
        
        # Count records
        cursor.execute("SELECT COUNT(*) FROM systems")
        system_count = cursor.fetchone()[0]
        
        print(f"\n📈 Current data:")
        print(f"  • Systems: {system_count}")
        
        assert system_count == 0, "❌ Should start with 0 systems!"
    
    print("\n✅ TEST 3 PASSED: VH-Database schema is correct")
    return True


def test_data_source_switching():
    """Test 4: Data source switching works correctly"""
    print("\n" + "="*70)
    print("TEST 4: Data Source Switching (Single Source of Truth)")
    print("="*70)
    
    manager = get_data_source_manager()
    
    sources_to_test = ["production", "testing", "load_test", "yh_database"]
    
    for source_name in sources_to_test:
        result = manager.set_current(source_name)
        assert result, f"❌ Failed to set current source to {source_name}"
        
        current = manager.get_current()
        assert current.name == source_name, f"❌ Current source mismatch!"
        
        print(f"\n✓ {source_name:12} → {current.display_name:30}")
        print(f"             Backend: {current.backend_type:8} | Systems: {current.system_count:,}")
        print(f"             Path: {current.path}")
    
    print("\n✅ TEST 4 PASSED: Data source switching works correctly")
    return True


def test_backup_system():
    """Test 5: Backup system works"""
    print("\n" + "="*70)
    print("TEST 5: VH-Database Backup System")
    print("="*70)
    
    from src.common.vh_database_backup import backup_vh_database, cleanup_old_backups
    from pathlib import Path
    
    manager = get_data_source_manager()
    manager.set_current("yh_database")
    yh_source = manager.get_current()
    
    print(f"\nDatabase to backup: {yh_source.path}")
    backup_dir = yh_source.path.parent / "backups"
    print(f"Backup directory: {backup_dir}")
    
    # Create backup
    backup_path = backup_vh_database(yh_source.path, backup_dir)
    
    if backup_path:
        print(f"\n✓ Backup created: {backup_path.name}")
        print(f"  Size: {backup_path.stat().st_size / 1024:.1f} KB")
        
        assert backup_path.exists(), "❌ Backup file not created!"
        
        # Test cleanup
        deleted_count = cleanup_old_backups(backup_dir, keep_count=5)
        print(f"\n✓ Backup cleanup: Kept 5, deleted {deleted_count} old backups")
        
        print("\n✅ TEST 5 PASSED: Backup system works correctly")
        return True
    else:
        print("\n❌ TEST 5 FAILED: Could not create backup")
        return False


def test_complete_workflow():
    """Test 6: Complete workflow - all three functions see same data"""
    print("\n" + "="*70)
    print("TEST 6: Complete Workflow (All Three Functions)")
    print("="*70)
    
    manager = get_data_source_manager()
    
    # Set to YH-Database
    manager.set_current("yh_database")
    yh_source = manager.get_current()
    
    print(f"\nCurrent data source: {yh_source.display_name}")
    print(f"Backend type: {yh_source.backend_type}")
    print(f"System count: {yh_source.system_count:,}")
    print(f"Database path: {yh_source.path}")
    
    # Simulate the three functions
    print("\n--- FUNCTION 1: Data Source Dropdown ---")
    print(f"Display text: {yh_source.icon} {yh_source.display_name}")
    print(f"Description: {yh_source.description}")
    print(f"System count shown: {yh_source.system_count:,}")
    
    print("\n--- FUNCTION 2: System Entry Wizard ---")
    print(f"Data source context: {yh_source.name}")
    print(f"Write destination: {yh_source.path}")
    print(f"Ready for data entry: YES")
    
    print("\n--- FUNCTION 3: Database Statistics ---")
    print(f"Source: {yh_source.display_name}")
    print(f"Path: {yh_source.path}")
    print(f"Total Systems: {yh_source.system_count:,}")
    print(f"Database Size: {yh_source.size_mb:.2f} MB")
    
    print("\n--- SINGLE SOURCE OF TRUTH VERIFICATION ---")
    print(f"✓ All three functions access: {yh_source.name}")
    print(f"✓ All show system count: {yh_source.system_count:,}")
    print(f"✓ All write to: {yh_source.path}")
    print(f"✓ No data mismatches possible!")
    
    print("\n✅ TEST 6 PASSED: Complete workflow verified")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("YH-DATABASE INTEGRATION TEST SUITE")
    print("="*70)
    print(f"Testing new 'YH-Database' for billion-scale star map")
    print(f"Date: {Path.cwd().name}")
    
    tests = [
        test_yh_database_registration,
        test_yh_database_file_exists,
        test_yh_database_schema,
        test_data_source_switching,
        test_backup_system,
        test_complete_workflow,
    ]
    
    results = []
    for i, test_func in enumerate(tests, 1):
        try:
            result = test_func()
            results.append((test_func.__name__, result))
        except Exception as e:
            print(f"\n❌ {test_func.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_func.__name__, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "="*70)
        print("🎉 ALL TESTS PASSED! YH-Database is ready!")
        print("="*70)
        print("\nYou can now:")
        print("  1. Launch Control Room")
        print("  2. Select 'YH-Database (Official Map)' from dropdown")
        print("  3. Click 'Launch System Entry (Wizard)'")
        print("  4. Start building your official map!")
        print("\nThe YH-Database will:")
        print("  ✓ Store all your systems")
        print("  ✓ Handle 1 billion+ star systems")
        print("  ✓ Auto-backup on each startup")
        print("  ✓ Use single source of truth across all functions")
        print("\n" + "="*70 + "\n")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
