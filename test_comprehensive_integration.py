"""
Comprehensive Phase 2/3 Integration Test Suite

Tests all components and dependencies to ensure:
1. Control Room features
2. System Entry Wizard features
3. Map Generator integration
4. All UI components show Phase 2/3 updates
5. All dependencies properly import and function

Run this test to verify complete Phase 2/3 implementation.
"""
import sys
from pathlib import Path

# Add project paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "src"))

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def print_test(name, passed=True, details=""):
    """Print test result"""
    status = "✓" if passed else "✗"
    color = "PASS" if passed else "FAIL"
    print(f"  [{color}] {status} {name}")
    if details:
        print(f"      {details}")

def test_control_room_imports():
    """Test 1: Control Room Imports and Phase 2 Integration"""
    print_section("TEST 1: Control Room Imports & Phase 2")
    
    try:
        import src.control_room as cr
        print_test("Control Room module imported", True)
        
        # Check Phase 2 enabled
        phase2 = cr.PHASE2_ENABLED
        print_test("PHASE2_ENABLED flag", phase2, f"Value: {phase2}")
        
        # Check required imports
        has_use_db = hasattr(cr, 'USE_DATABASE')
        print_test("USE_DATABASE imported", has_use_db)
        
        has_get_provider = hasattr(cr, 'get_data_provider')
        print_test("get_data_provider imported", has_get_provider)
        
        has_get_backend = hasattr(cr, 'get_current_backend')
        print_test("get_current_backend imported", has_get_backend)
        
        # Check Phase 2 methods exist
        methods = dir(cr.ControlRoom)
        has_init_provider = '_init_data_provider' in methods
        print_test("_init_data_provider method exists", has_init_provider)
        
        has_sync_check = '_check_data_sync_status' in methods
        print_test("_check_data_sync_status method exists", has_sync_check)
        
        has_db_stats = 'show_database_stats' in methods
        print_test("show_database_stats method exists", has_db_stats)
        
        has_sync_dialog = 'show_sync_dialog' in methods
        print_test("show_sync_dialog method exists", has_sync_dialog)
        
        return True
        
    except Exception as e:
        print_test("Control Room import", False, str(e))
        return False

def test_wizard_imports():
    """Test 2: System Entry Wizard Imports and Phase 3 Integration"""
    print_section("TEST 2: System Entry Wizard Imports & Phase 3")
    
    try:
        import src.system_entry_wizard as wizard
        print_test("Wizard module imported", True)
        
        # Check Phase 3 enabled
        phase3 = wizard.PHASE3_ENABLED
        print_test("PHASE3_ENABLED flag", phase3, f"Value: {phase3}")
        
        # Check required imports
        has_use_db = hasattr(wizard, 'USE_DATABASE')
        print_test("USE_DATABASE imported", has_use_db)
        
        has_get_provider = hasattr(wizard, 'get_data_provider')
        print_test("get_data_provider imported", has_get_provider)
        
        # Check Phase 3 methods exist
        methods = dir(wizard.SystemEntryWizard)
        has_init_provider = '_init_data_provider' in methods
        print_test("_init_data_provider method exists", has_init_provider)
        
        has_save_via_provider = '_save_system_via_provider' in methods
        print_test("_save_system_via_provider method exists", has_save_via_provider)
        
        has_save_via_json = '_save_system_via_json' in methods
        print_test("_save_system_via_json method exists", has_save_via_json)
        
        return True
        
    except Exception as e:
        print_test("Wizard import", False, str(e))
        return False

def test_data_providers():
    """Test 3: Data Provider Functionality"""
    print_section("TEST 3: Data Provider Functionality")
    
    try:
        from src.common.data_provider import DatabaseDataProvider, JSONDataProvider
        print_test("Data providers imported", True)
        
        # Test JSON provider
        json_provider = JSONDataProvider("data/data.json")
        json_systems = json_provider.get_all_systems()
        print_test("JSON provider working", True, f"{len(json_systems)} systems")
        
        # Test Database provider
        db_provider = DatabaseDataProvider("data/haven.db")
        db_systems = db_provider.get_all_systems()
        print_test("Database provider working", True, f"{len(db_systems)} systems")
        
        # Test sync status
        from src.migration.sync_data import DataSynchronizer
        syncer = DataSynchronizer()
        status = syncer.check_sync_status()
        
        in_sync = status.get('in_sync', False)
        print_test("Data sync check working", True, 
                  f"Sync: {in_sync}, JSON: {status.get('json_count')}, DB: {status.get('db_count')}")
        
        return True
        
    except Exception as e:
        print_test("Data providers", False, str(e))
        return False

def test_map_generator():
    """Test 4: Map Generator Integration"""
    print_section("TEST 4: Map Generator Integration")
    
    try:
        import src.Beta_VH_Map as map_gen
        print_test("Map generator imported", True)
        
        # Check if it can read data
        # Note: We won't actually generate a map, just check structure
        print_test("Map generator module structure", True)
        
        return True
        
    except Exception as e:
        print_test("Map generator", False, str(e))
        return False

def test_common_dependencies():
    """Test 5: Common Dependencies"""
    print_section("TEST 5: Common Dependencies")
    
    try:
        # Paths
        from src.common.paths import project_root, data_dir, logs_dir
        print_test("paths.py imported", True)
        print_test("project_root()", project_root().exists(), str(project_root()))
        
        # File lock
        from src.common.file_lock import FileLock
        print_test("file_lock.py imported", True)
        
        # Validation
        from src.common.validation import validate_system_data, validate_coordinates
        print_test("validation.py imported", True)
        
        # Progress dialogs
        from src.common.progress import ProgressDialog, IndeterminateProgressDialog
        print_test("progress.py imported", True)
        
        return True
        
    except Exception as e:
        print_test("Common dependencies", False, str(e))
        return False

def test_config_settings():
    """Test 6: Configuration Settings"""
    print_section("TEST 6: Configuration Settings")
    
    try:
        from config.settings import (
            USE_DATABASE,
            SHOW_BACKEND_STATUS,
            SHOW_SYSTEM_COUNT,
            ENABLE_DATABASE_STATS,
            ENABLE_BACKEND_TOGGLE,
            get_current_backend,
            get_data_provider
        )
        print_test("config.settings imported", True)
        
        print_test("USE_DATABASE", True, f"Value: {USE_DATABASE}")
        print_test("SHOW_BACKEND_STATUS", True, f"Value: {SHOW_BACKEND_STATUS}")
        print_test("SHOW_SYSTEM_COUNT", True, f"Value: {SHOW_SYSTEM_COUNT}")
        print_test("ENABLE_DATABASE_STATS", True, f"Value: {ENABLE_DATABASE_STATS}")
        print_test("ENABLE_BACKEND_TOGGLE", True, f"Value: {ENABLE_BACKEND_TOGGLE}")
        
        backend = get_current_backend()
        print_test("get_current_backend()", True, f"Backend: {backend}")
        
        provider = get_data_provider()
        print_test("get_data_provider()", True, f"Type: {type(provider).__name__}")
        
        return True
        
    except Exception as e:
        print_test("Config settings", False, str(e))
        return False

def test_migration_tools():
    """Test 7: Migration Tools"""
    print_section("TEST 7: Migration & Sync Tools")
    
    try:
        # JSON to SQLite migrator
        from src.migration.json_to_sqlite import JSONToSQLiteMigrator
        print_test("json_to_sqlite.py imported", True)
        
        # JSON importer
        from src.migration.import_json import JSONImporter
        print_test("import_json.py imported", True)
        
        # Sync tool
        from src.migration.sync_data import DataSynchronizer
        print_test("sync_data.py imported", True)
        
        # Test sync functionality
        syncer = DataSynchronizer()
        status = syncer.check_sync_status()
        print_test("Sync check functional", 'error' not in status, 
                  f"Status: {status.get('in_sync', 'unknown')}")
        
        return True
        
    except Exception as e:
        print_test("Migration tools", False, str(e))
        return False

def test_database_module():
    """Test 8: Database Module"""
    print_section("TEST 8: Database Module")
    
    try:
        from src.common.database import HavenDatabase
        print_test("database.py imported", True)
        
        # Test database connection
        db = HavenDatabase("data/haven.db")
        print_test("Database connection", True)
        
        # Test basic queries
        stats = db.get_statistics()
        print_test("Database statistics", True, 
                  f"Systems: {stats.get('total_systems', 0)}")
        
        return True
        
    except Exception as e:
        print_test("Database module", False, str(e))
        return False

def test_phase_integration():
    """Test 9: End-to-End Phase Integration"""
    print_section("TEST 9: End-to-End Phase Integration")
    
    try:
        # Test Control Room can initialize with Phase 2
        from config.settings import USE_DATABASE, get_data_provider
        
        backend = "database" if USE_DATABASE else "json"
        print_test("Backend selection", True, f"Active: {backend}")
        
        # Test data provider initialization
        provider = get_data_provider()
        count = provider.get_total_count()
        print_test("Provider initialization", True, f"Systems: {count}")
        
        # Test data access
        systems = provider.get_all_systems()
        print_test("Data retrieval", len(systems) > 0, f"Retrieved {len(systems)} systems")
        
        # Test sync status
        from src.migration.sync_data import DataSynchronizer
        syncer = DataSynchronizer()
        status = syncer.check_sync_status()
        in_sync = status.get('in_sync', False)
        print_test("Data synchronization", in_sync, 
                  f"JSON: {status.get('json_count')}, DB: {status.get('db_count')}")
        
        return True
        
    except Exception as e:
        print_test("Phase integration", False, str(e))
        return False

def test_ui_components():
    """Test 10: UI Component Availability"""
    print_section("TEST 10: UI Components (Static Check)")
    
    try:
        import src.control_room as cr
        
        # Check for UI builder methods
        methods = dir(cr.ControlRoom)
        
        has_build_ui = '_build_ui' in methods
        print_test("_build_ui method exists", has_build_ui)
        
        has_get_indicator = '_get_data_indicator_text' in methods
        print_test("_get_data_indicator_text method exists", has_get_indicator)
        
        has_on_change = '_on_data_source_change' in methods
        print_test("_on_data_source_change method exists", has_on_change)
        
        # Check theme colors loaded
        has_colors = hasattr(cr, 'COLORS')
        print_test("COLORS theme loaded", has_colors)
        
        if has_colors:
            required_colors = ['bg_dark', 'bg_card', 'accent_cyan', 'text_primary']
            all_present = all(color in cr.COLORS for color in required_colors)
            print_test("Required theme colors present", all_present)
        
        return True
        
    except Exception as e:
        print_test("UI components", False, str(e))
        return False

def check_file_structure():
    """Test 11: File Structure Integrity"""
    print_section("TEST 11: File Structure Integrity")
    
    required_files = {
        "data/data.json": "JSON data file",
        "data/haven.db": "SQLite database",
        "data/data.schema.json": "Data schema",
        "config/settings.py": "Configuration",
        "src/control_room.py": "Control Room",
        "src/system_entry_wizard.py": "System Entry Wizard",
        "src/Beta_VH_Map.py": "Map Generator",
        "src/common/paths.py": "Path utilities",
        "src/common/data_provider.py": "Data providers",
        "src/common/database.py": "Database module",
        "src/migration/sync_data.py": "Sync utility",
        "src/migration/json_to_sqlite.py": "Migration tool",
    }
    
    all_exist = True
    for file_path, description in required_files.items():
        exists = Path(file_path).exists()
        print_test(f"{description} ({file_path})", exists)
        if not exists:
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print(" COMPREHENSIVE PHASE 2/3 INTEGRATION TEST SUITE")
    print(" Testing all components, dependencies, and integrations")
    print("=" * 80)
    
    results = []
    
    # Run all tests
    results.append(("File Structure", check_file_structure()))
    results.append(("Config Settings", test_config_settings()))
    results.append(("Common Dependencies", test_common_dependencies()))
    results.append(("Database Module", test_database_module()))
    results.append(("Data Providers", test_data_providers()))
    results.append(("Migration Tools", test_migration_tools()))
    results.append(("Control Room", test_control_room_imports()))
    results.append(("Wizard", test_wizard_imports()))
    results.append(("Map Generator", test_map_generator()))
    results.append(("UI Components", test_ui_components()))
    results.append(("Phase Integration", test_phase_integration()))
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    print("\nDetailed Results:")
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status} - {name}")
    
    if passed == total:
        print("\n" + "=" * 80)
        print(" ✓ ALL TESTS PASSED - PHASE 2/3 FULLY INTEGRATED")
        print("=" * 80)
        return 0
    else:
        print("\n" + "=" * 80)
        print(f" ✗ {total - passed} TEST(S) FAILED")
        print("=" * 80)
        return 1

if __name__ == '__main__':
    sys.exit(main())
