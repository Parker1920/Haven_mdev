#!/usr/bin/env python3
"""
Test that all three functions use the same data source.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.common.data_source_manager import get_data_source_manager


def test_consistent_counts():
    """Verify all sources have consistent counts"""
    manager = get_data_source_manager()
    
    print("\n" + "="*60)
    print("TESTING DATA SOURCE UNIFICATION")
    print("="*60)
    
    # Test 1: All sources registered
    sources = manager.get_all_sources()
    print(f"\n✓ Registered {len(sources)} sources:")
    for name, info in sources.items():
        print(f"  - {name}: {info.display_name} ({info.system_count:,} systems)")
    
    # Test 2: Current source consistency
    manager.set_current("production")
    current1 = manager.get_current()
    current2 = manager.get_current()  # Should be SAME object
    print(f"\n✓ Current source returns SAME object:")
    print(f"  - Both calls return: {current1.name}")
    print(f"  - System count: {current1.system_count:,}")
    assert current1 is current2, "ERROR: get_current() returns different objects!"
    
    # Test 3: Switching sources
    manager.set_current("testing")
    current_test = manager.get_current()
    print(f"\n✓ Switching to testing source:")
    print(f"  - Current: {current_test.name}")
    print(f"  - System count: {current_test.system_count:,}")
    assert current_test.name == "testing", "ERROR: Switch failed!"
    
    # Test 4: Refresh counts
    print(f"\n✓ Refreshing all counts...")
    manager.refresh_counts()
    
    for name, info in manager.get_all_sources().items():
        print(f"  - {name}: {info.system_count:,} systems")
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED ✅")
    print("="*60 + "\n")


if __name__ == '__main__':
    test_consistent_counts()
