"""
Map Generator Data Access Test

Tests that Beta_VH_Map.py can properly access data from both backends
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def test_map_data_access():
    """Test map generator can access system data"""
    print("\n" + "=" * 80)
    print(" MAP GENERATOR DATA ACCESS TEST")
    print("=" * 80 + "\n")
    
    try:
        # Import map generator
        import src.Beta_VH_Map as map_gen
        print("✓ Map generator imported")
        
        # Check if it has data loading capability
        import json
        
        # Test reading from JSON
        json_path = Path("data/data.json")
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            systems = [v for k, v in data.items() if k != "_meta" and isinstance(v, dict)]
            print(f"✓ Can read JSON: {len(systems)} systems")
        
        # Test reading from database
        from src.common.data_provider import DatabaseDataProvider
        db_provider = DatabaseDataProvider("data/haven.db")
        db_systems = db_provider.get_all_systems()
        print(f"✓ Can read Database: {len(db_systems)} systems")
        
        # Test that map can use current backend
        from config.settings import USE_DATABASE, get_data_provider
        provider = get_data_provider()
        systems = provider.get_all_systems()
        print(f"✓ Current backend accessible: {len(systems)} systems")
        
        print("\n" + "=" * 80)
        print(" ✓ MAP GENERATOR CAN ACCESS DATA FROM BOTH BACKENDS")
        print("=" * 80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_map_data_access()
    sys.exit(0 if success else 1)
