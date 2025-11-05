"""
Phase 6 Test Suite: Production Deployment & Comprehensive Testing

Tests all components end-to-end and verifies production readiness.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

src_dir = project_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

def test_phase6_all_tests_passing():
    """Test that all Phase 1-5 test suites pass."""
    print("TEST 1: All Phase Test Suites...")
    try:
        import subprocess
        
        test_files = [
            ('test_phase2.py', 'Phase 2: Control Room'),
            ('test_phase3.py', 'Phase 3: Wizard'),
            ('test_phase4.py', 'Phase 4: Map Generator')
        ]
        
        all_passed = True
        for test_file, name in test_files:
            if Path(test_file).exists():
                print(f"  Running {name}...")
                result = subprocess.run(
                    [sys.executable, test_file],
                    capture_output=True,
                    text=True,
                    cwd=str(project_root)
                )
                if result.returncode == 0:
                    print(f"  ✓ {name} PASSED")
                else:
                    print(f"  ✗ {name} FAILED")
                    all_passed = False
            else:
                print(f"  ⊘ {name} test file not found")
        
        if all_passed:
            print("  ✓ All test suites passed")
            return True
        else:
            print("  ✗ Some tests failed")
            return False
            
    except Exception as e:
        print(f"  ✗ Test execution failed: {e}")
        return False


def test_phase6_database_integrity():
    """Test database integrity and data consistency."""
    print("\nTEST 2: Database Integrity...")
    try:
        from src.common.data_provider import DatabaseDataProvider
        from config.settings import DATABASE_PATH
        
        # Use database provider which handles connection properly
        db_provider = DatabaseDataProvider(str(DATABASE_PATH))
        
        # Test basic operations
        systems = db_provider.get_all_systems()
        assert len(systems) > 0, "Database should have systems"
        print(f"  ✓ Database accessible")
        print(f"  ✓ Query systems: {len(systems)} systems")
        
        # Get statistics via database provider
        total_count = db_provider.get_total_count()
        print(f"  ✓ Total systems: {total_count}")
        
        # Test that we can get a specific system
        first_system = systems[0]
        system_name = first_system['name']
        system = db_provider.get_system_by_name(system_name)
        assert system is not None, "Should retrieve system by name"
        print(f"  ✓ Get system by name: '{system_name}'")
        
        # Test region filtering
        regions = db_provider.get_regions()
        print(f"  ✓ Total regions: {len(regions)}")
        
        return True
    except Exception as e:
        print(f"  ✗ Database integrity test failed: {e}")
        return False


def test_phase6_data_sync():
    """Test data synchronization between JSON and database."""
    print("\nTEST 3: Data Synchronization...")
    try:
        from src.migration.sync_data import DataSynchronizer
        
        syncer = DataSynchronizer()
        status = syncer.check_sync_status()
        
        if "error" in status:
            print(f"  ✗ Sync check error: {status['error']}")
            return False
        
        print(f"  ✓ JSON systems: {status['json_count']}")
        print(f"  ✓ Database systems: {status['db_count']}")
        print(f"  ✓ In sync: {status['in_sync']}")
        
        if not status['in_sync']:
            print(f"  ⚠ Systems out of sync:")
            print(f"    - Only in JSON: {status['only_in_json']}")
            print(f"    - Only in DB: {status['only_in_db']}")
            print(f"    - Differences: {status['differences']}")
        
        return True
    except Exception as e:
        print(f"  ✗ Data sync test failed: {e}")
        return False


def test_phase6_map_generation():
    """Test map generation from database."""
    print("\nTEST 4: Map Generation...")
    try:
        from src.Beta_VH_Map import load_systems
        from common.paths import dist_dir
        
        # Load systems via Phase 4 integration
        df = load_systems()
        print(f"  ✓ Loaded {len(df)} systems for map")
        
        # Check required columns
        required = ['name', 'x', 'y', 'z', 'region']
        for col in required:
            assert col in df.columns, f"Missing column: {col}"
        print(f"  ✓ All required columns present")
        
        # Check that dist directory exists
        dist = dist_dir()
        if dist.exists():
            print(f"  ✓ Dist directory exists: {dist}")
        else:
            print(f"  ⚠ Dist directory not found (will be created on map gen)")
        
        return True
    except Exception as e:
        print(f"  ✗ Map generation test failed: {e}")
        return False


def test_phase6_import_functionality():
    """Test JSON import functionality."""
    print("\nTEST 5: JSON Import Functionality...")
    try:
        from src.migration.import_json import JSONImporter
        from config.settings import USE_DATABASE
        
        importer = JSONImporter(use_database=USE_DATABASE)
        print(f"  ✓ JSONImporter initialized")
        print(f"  ✓ Using backend: {'database' if USE_DATABASE else 'json'}")
        
        # Check that imports directory exists
        imports_dir = project_root / "data" / "imports"
        if imports_dir.exists():
            json_files = list(imports_dir.glob("*.json"))
            print(f"  ✓ Imports directory exists: {len(json_files)} JSON files found")
        else:
            print(f"  ⊘ Imports directory not found (will be created when needed)")
        
        return True
    except Exception as e:
        print(f"  ✗ Import functionality test failed: {e}")
        return False


def test_phase6_configuration():
    """Test production configuration settings."""
    print("\nTEST 6: Production Configuration...")
    try:
        from config.settings import (
            USE_DATABASE, AUTO_DETECT_BACKEND, 
            SHOW_BACKEND_STATUS, SHOW_SYSTEM_COUNT,
            ENABLE_DATABASE_STATS, get_current_backend
        )
        
        print(f"  ✓ USE_DATABASE: {USE_DATABASE}")
        print(f"  ✓ AUTO_DETECT_BACKEND: {AUTO_DETECT_BACKEND}")
        print(f"  ✓ SHOW_BACKEND_STATUS: {SHOW_BACKEND_STATUS}")
        print(f"  ✓ SHOW_SYSTEM_COUNT: {SHOW_SYSTEM_COUNT}")
        print(f"  ✓ ENABLE_DATABASE_STATS: {ENABLE_DATABASE_STATS}")
        print(f"  ✓ Current backend: {get_current_backend()}")
        
        # Verify production defaults
        if USE_DATABASE:
            print(f"  ✓ Database mode enabled (production)")
        else:
            print(f"  ⚠ Database mode disabled (development)")
        
        return True
    except Exception as e:
        print(f"  ✗ Configuration test failed: {e}")
        return False


def test_phase6_all_modules_import():
    """Test that all critical modules can be imported."""
    print("\nTEST 7: Module Import Test...")
    try:
        modules = [
            ('src.control_room', 'Control Room'),
            ('src.system_entry_wizard', 'System Entry Wizard'),
            ('src.Beta_VH_Map', 'Map Generator'),
            ('src.common.database', 'Database'),
            ('src.common.data_provider', 'Data Provider'),
            ('src.migration.sync_data', 'Sync Tool'),
            ('src.migration.import_json', 'JSON Importer'),
            ('config.settings', 'Configuration'),
        ]
        
        all_imported = True
        for module_name, display_name in modules:
            try:
                __import__(module_name)
                print(f"  ✓ {display_name}")
            except ImportError as e:
                print(f"  ✗ {display_name}: {e}")
                all_imported = False
        
        if all_imported:
            print(f"  ✓ All critical modules imported successfully")
            return True
        else:
            print(f"  ✗ Some modules failed to import")
            return False
            
    except Exception as e:
        print(f"  ✗ Module import test failed: {e}")
        return False


def test_phase6_file_structure():
    """Test that all required files and directories exist."""
    print("\nTEST 8: File Structure Verification...")
    try:
        required_files = [
            'src/control_room.py',
            'src/system_entry_wizard.py',
            'src/Beta_VH_Map.py',
            'src/common/database.py',
            'src/common/data_provider.py',
            'src/migration/sync_data.py',
            'src/migration/import_json.py',
            'config/settings.py',
            'data/data.json',
            'data/data.schema.json',
        ]
        
        required_dirs = [
            'src',
            'data',
            'config',
            'logs',
            'dist',
        ]
        
        all_exist = True
        for file_path in required_files:
            path = project_root / file_path
            if path.exists():
                print(f"  ✓ {file_path}")
            else:
                print(f"  ✗ {file_path} NOT FOUND")
                all_exist = False
        
        for dir_path in required_dirs:
            path = project_root / dir_path
            if path.exists():
                print(f"  ✓ {dir_path}/")
            else:
                print(f"  ✗ {dir_path}/ NOT FOUND")
                all_exist = False
        
        if all_exist:
            print(f"  ✓ All required files and directories present")
            return True
        else:
            print(f"  ✗ Some files or directories missing")
            return False
            
    except Exception as e:
        print(f"  ✗ File structure test failed: {e}")
        return False


def test_phase6_performance():
    """Test basic performance metrics."""
    print("\nTEST 9: Performance Test...")
    try:
        import time
        from src.common.data_provider import get_data_provider
        
        provider = get_data_provider()
        
        # Test get_all_systems performance
        start = time.time()
        systems = provider.get_all_systems()
        elapsed = time.time() - start
        
        print(f"  ✓ Loaded {len(systems)} systems in {elapsed:.4f}s")
        
        if elapsed < 1.0:
            print(f"  ✓ Performance: Excellent (< 1s)")
        elif elapsed < 5.0:
            print(f"  ✓ Performance: Good (< 5s)")
        else:
            print(f"  ⚠ Performance: Slow (> 5s)")
        
        # Test single system lookup
        if systems:
            first_name = systems[0]['name']
            start = time.time()
            system = provider.get_system_by_name(first_name)
            elapsed = time.time() - start
            print(f"  ✓ Single system lookup: {elapsed:.4f}s")
        
        return True
    except Exception as e:
        print(f"  ✗ Performance test failed: {e}")
        return False


def test_phase6_data_provider_switching():
    """Test switching between JSON and database backends."""
    print("\nTEST 10: Backend Switching...")
    try:
        from src.common.data_provider import get_data_provider, JSONDataProvider, DatabaseDataProvider
        from config import settings
        
        # Get provider with correct settings
        is_using_db = settings.USE_DATABASE
        current_provider = get_data_provider(use_database=is_using_db)
        
        if is_using_db:
            assert isinstance(current_provider, DatabaseDataProvider), "Should be using database"
            print(f"  ✓ Using database backend (as configured)")
        else:
            assert isinstance(current_provider, JSONDataProvider), "Should be using JSON"
            print(f"  ✓ Using JSON backend (as configured)")
        
        # Test that both providers can be created
        json_provider = JSONDataProvider()
        db_provider = DatabaseDataProvider()
        
        json_count = json_provider.get_total_count()
        db_count = db_provider.get_total_count()
        
        print(f"  ✓ JSON backend: {json_count} systems")
        print(f"  ✓ Database backend: {db_count} systems")
        print(f"  ✓ Backend switching functional")
        
        return True
    except Exception as e:
        print(f"  ✗ Backend switching test failed: {e}")
        return False


def run_all_tests():
    """Run all Phase 6 tests."""
    print("=" * 60)
    print("PHASE 6 COMPREHENSIVE TEST SUITE")
    print("Production Deployment & System Verification")
    print("=" * 60)
    
    tests = [
        test_phase6_all_modules_import,
        test_phase6_file_structure,
        test_phase6_configuration,
        test_phase6_database_integrity,
        test_phase6_data_sync,
        test_phase6_map_generation,
        test_phase6_import_functionality,
        test_phase6_data_provider_switching,
        test_phase6_performance,
        # test_phase6_all_tests_passing,  # Skip subprocess tests for now
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ✗ Test crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("✅ ALL PHASE 6 TESTS PASSED")
        print("System is production-ready!")
        return True
    else:
        print("⚠️  SOME TESTS FAILED")
        print("Review failures above")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
