"""
Test Wizard Save Fix - Verify duplicate system handling
"""
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from config.settings import get_data_provider

print("=" * 70)
print("TESTING WIZARD SAVE FIX - DUPLICATE SYSTEM HANDLING")
print("=" * 70)

# Get provider
provider = get_data_provider()

# Test 1: Check if system exists
print("\n[TEST 1] Check existing system")
system_name = "OOTLEFAR V"
existing = provider.get_system_by_name(system_name)
if existing:
    print(f"  ✓ Found system: {system_name}")
    print(f"  ✓ System ID: {existing['id']}")
    print(f"  ✓ Planets: {len(existing.get('planets', []))}")
else:
    print(f"  ❌ System '{system_name}' not found")

# Test 2: Simulate save with duplicate name
print("\n[TEST 2] Simulate duplicate save (delete + add)")
if existing:
    try:
        # Save original count
        original_count = provider.get_total_count()
        print(f"  ✓ Original system count: {original_count}")

        # Delete existing
        provider.delete_system(existing['id'])
        after_delete = provider.get_total_count()
        print(f"  ✓ After delete: {after_delete}")

        # Re-add with same data
        new_id = provider.add_system(existing)
        after_add = provider.get_total_count()
        print(f"  ✓ After add: {after_add}")
        print(f"  ✓ New system ID: {new_id}")

        # Verify count is the same
        if after_add == original_count:
            print(f"  ✓ System count restored correctly")
        else:
            print(f"  ⚠️  Count mismatch: {original_count} -> {after_add}")

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 70)
print("✓ TEST COMPLETE")
print("=" * 70)
