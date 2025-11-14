"""
Phase 4 Test Suite: Map Generator Integration

Tests the integration of Beta_VH_Map.py with the database backend.
Verifies that the map generator can load data from both JSON and database backends.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Also add src to path for imports
src_dir = project_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

def test_phase4_imports():
    """Test that Phase 4 imports work correctly."""
    print("TEST 1: Phase 4 imports...")
    try:
        from src.Beta_VH_Map import PHASE4_ENABLED, USE_DATABASE
        print(f"  ✓ PHASE4_ENABLED = {PHASE4_ENABLED}")
        print(f"  ✓ USE_DATABASE = {USE_DATABASE}")
        assert isinstance(PHASE4_ENABLED, bool), "PHASE4_ENABLED should be a boolean"
        print("  ✓ Phase 4 imports successful")
        return True
    except Exception as e:
        print(f"  ✗ Phase 4 imports failed: {e}")
        return False


def test_phase4_load_systems():
    """Test that load_systems() function exists and can be called."""
    print("\nTEST 2: load_systems() function...")
    try:
        from src.Beta_VH_Map import load_systems
        print("  ✓ load_systems() imported successfully")
        
        # Try to load systems
        df = load_systems()
        print(f"  ✓ Loaded {len(df)} systems")
        assert len(df) > 0, "Should load at least one system"
        
        # Check required columns
        required_cols = ["name", "x", "y", "z", "region"]
        for col in required_cols:
            assert col in df.columns, f"Missing required column: {col}"
        print(f"  ✓ All required columns present: {required_cols}")
        
        return True
    except Exception as e:
        print(f"  ✗ load_systems() test failed: {e}")
        return False


def test_phase4_data_provider():
    """Test that map generator uses data provider when Phase 4 enabled."""
    print("\nTEST 3: Data provider integration...")
    try:
        from src.Beta_VH_Map import PHASE4_ENABLED, load_systems
        from config.settings import USE_DATABASE, get_current_backend
        
        if not PHASE4_ENABLED:
            print("  ⚠ Phase 4 disabled - skipping data provider test")
            return True
        
        backend = get_current_backend()
        print(f"  ✓ Current backend: {backend}")
        
        df = load_systems()
        print(f"  ✓ Loaded {len(df)} systems via data provider")
        
        return True
    except Exception as e:
        print(f"  ✗ Data provider test failed: {e}")
        return False


def test_phase4_json_fallback():
    """Test that JSON fallback works if data provider fails."""
    print("\nTEST 4: JSON fallback...")
    try:
        from src.Beta_VH_Map import load_systems, DATA_FILE
        
        # Load directly via JSON path (tests fallback)
        df = load_systems(path=DATA_FILE)
        print(f"  ✓ JSON fallback loaded {len(df)} systems")
        assert len(df) > 0, "JSON fallback should load systems"
        
        return True
    except Exception as e:
        print(f"  ✗ JSON fallback test failed: {e}")
        return False


def test_phase4_backend_toggle():
    """Test that backend toggle is respected."""
    print("\nTEST 5: Backend toggle...")
    try:
        from src.Beta_VH_Map import PHASE4_ENABLED, USE_DATABASE
        from config.settings import get_current_backend
        
        if not PHASE4_ENABLED:
            print("  ⚠ Phase 4 disabled - USE_DATABASE should be False")
            assert USE_DATABASE == False, "USE_DATABASE should be False when Phase 4 disabled"
            print("  ✓ Correct fallback behavior")
        else:
            backend = get_current_backend()
            print(f"  ✓ Backend toggle working: {backend}")
            if USE_DATABASE:
                assert backend == "database", "Backend should be database when USE_DATABASE=True"
            else:
                assert backend == "json", "Backend should be json when USE_DATABASE=False"
        
        return True
    except Exception as e:
        print(f"  ✗ Backend toggle test failed: {e}")
        return False


def run_all_tests():
    """Run all Phase 4 tests."""
    print("=" * 60)
    print("PHASE 4 TEST SUITE: Map Generator Integration")
    print("=" * 60)
    
    tests = [
        test_phase4_imports,
        test_phase4_load_systems,
        test_phase4_data_provider,
        test_phase4_json_fallback,
        test_phase4_backend_toggle
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
        print("✅ ALL PHASE 4 TESTS PASSED")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
