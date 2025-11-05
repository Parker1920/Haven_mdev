"""
Interactive UI Test Script

This script will launch components and prompt you to verify UI features.
Tests:
1. Control Room UI elements
2. System Entry Wizard UI elements
3. Map Generator output
4. Database Statistics dialog
5. Sync dialog
6. All Advanced Tools buttons
"""
import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def print_header(text):
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80 + "\n")

def test_control_room_ui():
    """Test Control Room UI visibility"""
    print_header("CONTROL ROOM UI TEST")
    
    print("Items to verify in Control Room:")
    print("\n📊 STATUS INDICATORS (in sidebar):")
    print("  □ Backend: DATABASE (or JSON)")
    print("  □ Systems: 9 (or current count)")
    print("  □ Data source indicator shows correct mode")
    
    print("\n⚙️ ADVANCED TOOLS (bottom of sidebar):")
    print("  □ 🔧 Update Dependencies button")
    print("  □ 📦 Export App (EXE/.app) button")
    print("  □ 🧪 System Test button")
    print("  □ 📊 Database Statistics button (if database mode)")
    print("  □ 🔄 Sync Data (JSON ↔ DB) button")
    
    print("\n🚀 QUICK ACTIONS:")
    print("  □ Generate Map button")
    print("  □ System Entry button")
    
    print("\n📁 FILE MANAGEMENT:")
    print("  □ Data Folder button")
    print("  □ Logs Folder button")
    print("  □ Documentation button")
    
    print("\n✅ ACTION: Launch Control Room and verify all items above")
    input("Press Enter when ready to launch Control Room...")
    
    try:
        import subprocess
        subprocess.Popen(["py", "-3", "src/control_room.py"])
        print("\n✓ Control Room launched!")
        print("  Check the UI and verify all items in the checklist")
        input("\nPress Enter when you've verified the Control Room UI...")
    except Exception as e:
        print(f"✗ Failed to launch: {e}")

def test_database_statistics():
    """Test Database Statistics dialog"""
    print_header("DATABASE STATISTICS TEST")
    
    print("To test Database Statistics:")
    print("1. Ensure Control Room is running")
    print("2. Click '📊 Database Statistics' button in Advanced Tools")
    print("3. Verify dialog shows:")
    print("   □ Total Systems count")
    print("   □ Total Planets count")
    print("   □ Total Moons count")
    print("   □ Total Space Stations count")
    print("   □ Regions list")
    print("   □ Database Size (MB)")
    print("   □ Database Path")
    
    input("\nPress Enter when you've verified Database Statistics...")

def test_sync_dialog():
    """Test Data Sync dialog"""
    print_header("DATA SYNC DIALOG TEST")
    
    print("To test Data Sync dialog:")
    print("1. Ensure Control Room is running")
    print("2. Click '🔄 Sync Data (JSON ↔ DB)' button in Advanced Tools")
    print("3. Verify dialog shows:")
    print("   □ JSON File: X systems")
    print("   □ Database: X systems")
    print("   □ In Both: X systems")
    print("   □ Status: ✓ IN SYNC or ✗ OUT OF SYNC")
    print("   □ 'JSON → Database' button")
    print("   □ 'Database → JSON' button")
    print("   □ Info text explaining sync options")
    print("   □ Close button")
    
    input("\nPress Enter when you've verified Sync Dialog...")

def test_wizard_ui():
    """Test System Entry Wizard UI"""
    print_header("SYSTEM ENTRY WIZARD TEST")
    
    print("Items to verify in System Entry Wizard:")
    print("\n📊 HEADER STATUS (top of window):")
    print("  □ Backend: DATABASE (or JSON)")
    print("  □ Systems: 9 (or current count)")
    print("  □ Title: ✨ HAVEN SYSTEM ENTRY WIZARD")
    print("  □ Page indicator: Page 1 of 2: System Information")
    
    print("\n📝 PAGE 1 - SYSTEM INFORMATION:")
    print("  □ System Name field")
    print("  □ Region field")
    print("  □ Coordinates (X, Y, Z)")
    print("  □ All other system fields")
    print("  □ Next button")
    
    print("\n🌍 PAGE 2 - PLANETS & MOONS:")
    print("  □ Planet list")
    print("  □ Add Planet button")
    print("  □ Moon editing per planet")
    print("  □ Back button")
    print("  □ Save System button")
    
    print("\n✅ ACTION: Launch Wizard from Control Room")
    print("   Click 'System Entry' button in Control Room")
    
    input("\nPress Enter when you've verified the Wizard UI...")

def test_map_generation():
    """Test Map Generator"""
    print_header("MAP GENERATOR TEST")
    
    print("To test Map Generator:")
    print("1. In Control Room, click 'Generate Map' button")
    print("2. Wait for map generation")
    print("3. Verify:")
    print("   □ Map opens in browser")
    print("   □ All 9 systems visible")
    print("   □ System names display correctly")
    print("   □ Coordinates match data")
    print("   □ Can click on systems to see details")
    print("   □ 3D view works")
    print("   □ Zoom/pan works")
    
    input("\nPress Enter when you've verified the Map...")

def test_advanced_features():
    """Test advanced features"""
    print_header("ADVANCED FEATURES TEST")
    
    print("Additional features to test:")
    print("\n1. DATA SOURCE TOGGLE:")
    print("   □ Toggle 'Use Test Data' switch")
    print("   □ Data indicator updates")
    print("   □ System count updates (if test data exists)")
    
    print("\n2. LOGS:")
    print("   □ Click 'Logs Folder' button")
    print("   □ Folder opens with recent logs")
    print("   □ Check control-room-2025-11-05.log for:")
    print("      - 'Using DATABASE data provider'")
    print("      - 'Data provider initialized: database'")
    print("      - 'Data sync OK: JSON and database both have X systems'")
    
    print("\n3. SYSTEM TEST:")
    print("   □ Click 'System Test' button")
    print("   □ Test menu appears with options")
    print("   □ Can run individual tests")
    
    input("\nPress Enter when you've verified Advanced Features...")

def test_map_views():
    """Test map views"""
    print_header("MAP VIEWS TEST")
    
    print("Testing Galaxy View and System View:")
    print("\n1. GALAXY VIEW (VH-Map.html):")
    print("   □ Shows all systems in 3D space")
    print("   □ Systems positioned by X, Y, Z coordinates")
    print("   □ Can rotate view")
    print("   □ Can zoom in/out")
    print("   □ Click system to see info popup")
    
    print("\n2. SYSTEM VIEW (per-system detail):")
    print("   □ Click on a system in galaxy view")
    print("   □ Details panel appears showing:")
    print("      - System name")
    print("      - Region")
    print("      - Coordinates")
    print("      - Planets count")
    print("      - Other system info")
    
    print("\n3. DATABASE INTEGRATION:")
    print("   □ Map loads data from active backend (database or JSON)")
    print("   □ All systems from database appear")
    print("   □ No missing systems")
    print("   □ No duplicate systems")
    
    input("\nPress Enter when you've verified Map Views...")

def run_all_tests():
    """Run all UI tests"""
    print("\n" + "=" * 80)
    print(" INTERACTIVE UI TEST SUITE - PHASE 2/3 VERIFICATION")
    print(" This will walk you through testing all UI components")
    print("=" * 80)
    
    input("\nPress Enter to begin testing...")
    
    # Test Control Room
    test_control_room_ui()
    
    # Test Database Statistics
    test_database_statistics()
    
    # Test Sync Dialog
    test_sync_dialog()
    
    # Test Wizard
    test_wizard_ui()
    
    # Test Map
    test_map_generation()
    
    # Test Map Views
    test_map_views()
    
    # Test Advanced Features
    test_advanced_features()
    
    # Summary
    print_header("TEST COMPLETE")
    print("✓ All UI components have been checked")
    print("\nSUMMARY CHECKLIST:")
    print("  □ Control Room shows Phase 2 indicators")
    print("  □ Database Statistics dialog works")
    print("  □ Data Sync dialog works")
    print("  □ System Entry Wizard shows Phase 3 indicators")
    print("  □ Map Generator produces correct output")
    print("  □ Galaxy View displays all systems")
    print("  □ System View shows correct details")
    print("  □ All Advanced Tools buttons present")
    print("  □ Data sync check runs on startup")
    print("  □ Logs show correct backend initialization")
    
    print("\n" + "=" * 80)
    print(" If all items checked: Phase 2/3 integration is COMPLETE ✓")
    print("=" * 80 + "\n")

if __name__ == '__main__':
    run_all_tests()
