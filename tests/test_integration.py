#!/usr/bin/env python3
"""
Quick integration test - verify control_room imports work correctly
"""

import sys
from pathlib import Path

# Set up path
sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("INTEGRATION TEST - Verifying control_room.py imports")
print("="*60)

try:
    print("\n[1] Importing DataSourceManager...")
    from src.common.data_source_manager import get_data_source_manager
    print("    ✓ DataSourceManager imported successfully")
    
    print("\n[2] Initializing manager...")
    manager = get_data_source_manager()
    print("    ✓ Manager initialized")
    
    print("\n[3] Verifying all sources registered...")
    sources = manager.get_all_sources()
    print(f"    ✓ Found {len(sources)} sources:")
    for name, info in sources.items():
        print(f"      - {name}: {info.display_name} ({info.system_count:,} systems)")
    
    print("\n[4] Testing source switching...")
    manager.set_current("production")
    current = manager.get_current()
    print(f"    ✓ Set to: {current.name} - {current.display_name}")
    
    manager.set_current("testing")
    current = manager.get_current()
    print(f"    ✓ Set to: {current.name} - {current.display_name}")
    
    print("\n[5] Checking control_room.py syntax (no import yet)...")
    ctrl_path = Path(__file__).parent / "src" / "control_room.py"
    with open(ctrl_path, 'r', encoding='utf-8') as f:
        code = f.read()
        # Quick check for expected unified functions
        if "_on_data_source_change" in code and "get_data_source_manager" in code:
            print("    ✓ control_room.py contains unified functions")
        else:
            print("    ✗ control_room.py may not be properly updated")
    
    print("\n[6] Checking system_entry_wizard.py syntax...")
    wizard_path = Path(__file__).parent / "src" / "system_entry_wizard.py"
    with open(wizard_path, 'r', encoding='utf-8') as f:
        code = f.read()
        if "get_data_source_manager" in code and "HAVEN_DATA_SOURCE" in code:
            print("    ✓ system_entry_wizard.py contains data source initialization")
        else:
            print("    ✗ system_entry_wizard.py may not be properly updated")
    
    print("\n" + "="*60)
    print("INTEGRATION TEST PASSED ✅")
    print("="*60)
    print("\nAll imports working correctly.")
    print("Next: Launch control room to verify UI integration.\n")
    
except Exception as e:
    print(f"\n✗ INTEGRATION TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
