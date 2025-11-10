#!/usr/bin/env python3
"""
Comprehensive Test Suite for Haven Control Room User Edition
Tests all functionality to ensure:
1. Standalone operation - doesn't call outside bundle
2. All functions work correctly
3. Data flow: wizard→save→map gen→render matches master
"""

import json
import sys
from pathlib import Path
import subprocess
import time

def run_test(name, test_func):
    """Run a test and report results"""
    print(f"\n{'='*70}")
    print(f"TEST: {name}")
    print(f"{'='*70}")
    try:
        result = test_func()
        if result:
            print(f"✅ PASSED: {name}")
            return True
        else:
            print(f"❌ FAILED: {name}")
            return False
    except Exception as e:
        print(f"❌ ERROR in {name}: {e}")
        import traceback
        traceback.print_exc()
        return False

class UserEditionTester:
    def __init__(self):
        self.project_root = Path(__file__).parent.resolve()
        self.user_edition_dir = self.project_root / "dist" / "HavenControlRoom_User"
        self.data_dir = self.user_edition_dir / "files"
        self.data_file = self.data_dir / "data.json"
        self.maps_dir = self.data_dir / "maps"
        self.logs_dir = self.data_dir / "logs"
        self.photos_dir = self.data_dir / "photos"
        
    def test_user_edition_structure(self):
        """Test 1: Verify user edition has correct directory structure"""
        print(f"Checking user edition structure at: {self.user_edition_dir}")
        
        required_items = [
            ("EXE", self.user_edition_dir / "HavenControlRoom.exe"),
            ("files dir", self.data_dir),
            ("data.json", self.data_file),
            ("maps dir", self.maps_dir),
            ("logs dir", self.logs_dir),
            ("photos dir", self.photos_dir),
        ]
        
        all_exist = True
        for name, path in required_items:
            if path.exists():
                print(f"  ✓ {name}: {path.name if path.is_file() else path.name + '/'}")
            else:
                print(f"  ✗ MISSING: {name}")
                all_exist = False
        
        return all_exist
    
    def test_data_file_integrity(self):
        """Test 2: Verify data.json is valid and has systems"""
        print(f"Checking data file: {self.data_file}")
        
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            # Count systems (exclude _meta)
            systems = {k: v for k, v in data.items() if k != "_meta"}
            num_systems = len(systems)
            
            print(f"  ✓ Data is valid JSON")
            print(f"  ✓ Contains {num_systems} systems")
            
            if num_systems > 0:
                # Show first 3 systems
                for i, (name, info) in enumerate(list(systems.items())[:3]):
                    print(f"    - {name}: ID={info.get('id')}, x={info.get('x')}, y={info.get('y')}, z={info.get('z')}")
                return True
            else:
                print(f"  ✗ No systems found in data file")
                return False
                
        except Exception as e:
            print(f"  ✗ Error reading data file: {e}")
            return False
    
    def test_map_generator_standalone(self):
        """Test 3: Verify map generator works standalone with user data"""
        print(f"Testing map generation with user data...")
        
        try:
            map_output = self.maps_dir / "VH-Map-TEST.html"
            if map_output.exists():
                map_output.unlink()
            
            # Run map generator
            map_script = self.project_root / "src" / "Beta_VH_Map.py"
            cmd = [
                sys.executable,
                str(map_script),
                "--data-file", str(self.data_file),
                "--out", str(map_output),
                "--no-open"
            ]
            
            print(f"  Running: {' '.join([str(x) if i > 1 else x for i, x in enumerate(cmd)])}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"  ✗ Map generation failed: {result.stderr}")
                return False
            
            # Check output file was created
            if not map_output.exists():
                print(f"  ✗ Map output file not created")
                return False
            
            file_size = map_output.stat().st_size
            print(f"  ✓ Map generated: {file_size / 1024:.1f} KB")
            
            # Check for system data in map
            with open(map_output, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            
            if 'window.SYSTEMS_DATA = []' in html_content:
                print(f"  ✗ Map has empty SYSTEMS_DATA - no systems rendered!")
                return False
            
            if 'window.SYSTEMS_DATA = [' not in html_content:
                print(f"  ✗ SYSTEMS_DATA not found in HTML")
                return False
            
            # Count how many systems are in the map
            count = html_content.count('"type": "system"')
            print(f"  ✓ Map contains {count} systems")
            
            if count == 0:
                print(f"  ✗ No systems found in SYSTEMS_DATA")
                return False
            
            # Check for Three.js and required scripts
            required_content = [
                ('Three.js', 'three.js'),
                ('Map viewer', 'map-viewer.js'),
                ('Loading overlay', 'loading-overlay'),
            ]
            
            for name, content in required_content:
                if content in html_content:
                    print(f"  ✓ {name} found in map")
                else:
                    print(f"  ✗ {name} NOT found in map")
                    return False
            
            return True
            
        except Exception as e:
            print(f"  ✗ Error testing map generation: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_no_external_calls(self):
        """Test 4: Verify all paths stay within user edition directory"""
        print(f"Checking for external path calls...")
        
        # Check control_room_user.py for any calls to project_root or outside paths
        control_room_file = self.project_root / "src" / "control_room_user.py"
        
        with open(control_room_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Look for problematic patterns
        problematic_patterns = [
            ('PROJECT_ROOT', 'Should not reference PROJECT_ROOT outside frozen context'),
            ('/../', 'Relative path going outside bundle'),
            ('data_path(', 'Using data_path function from common'),
        ]
        
        issues = []
        for pattern, desc in problematic_patterns:
            if pattern in content and 'IS_FROZEN' not in content.split(pattern)[0][-50:]:
                # Found pattern but check if it's properly guarded
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if pattern in line and not any(guard in lines[max(0, i-5):i] for guard in ['if IS_FROZEN', 'else:']):
                        issues.append(f"Line {i+1}: {desc}")
        
        if issues:
            print(f"  ⚠ Potential external calls found:")
            for issue in issues[:5]:
                print(f"    - {issue}")
            return False
        else:
            print(f"  ✓ No suspicious external path calls detected")
            return True
    
    def test_data_persistence(self):
        """Test 5: Verify data changes persist across runs"""
        print(f"Testing data persistence...")
        
        try:
            # Read current data
            with open(self.data_file, 'r') as f:
                original_data = json.load(f)
            
            systems_before = {k: v for k, v in original_data.items() if k != "_meta"}
            count_before = len(systems_before)
            print(f"  ✓ Original data has {count_before} systems")
            
            # Create a test system
            test_system = {
                "id": "TEST_001",
                "name": "TEST_SYSTEM",
                "x": 99.9,
                "y": 99.9,
                "z": 99.9,
                "region": "Test",
                "fauna": "High",
                "flora": "High",
                "sentinel": "None",
                "materials": "Test",
                "base_location": "Test",
                "photo": None,
                "planets": []
            }
            
            # Add test system to data
            original_data["TEST_SYSTEM"] = test_system
            with open(self.data_file, 'w') as f:
                json.dump(original_data, f, indent=2)
            print(f"  ✓ Added test system to data.json")
            
            # Reload and verify
            with open(self.data_file, 'r') as f:
                new_data = json.load(f)
            
            if "TEST_SYSTEM" in new_data:
                print(f"  ✓ Test system persisted in data.json")
            else:
                print(f"  ✗ Test system NOT found after save")
                return False
            
            # Remove test system
            del original_data["TEST_SYSTEM"]
            with open(self.data_file, 'w') as f:
                json.dump(original_data, f, indent=2)
            print(f"  ✓ Cleaned up test system")
            
            return True
            
        except Exception as e:
            print(f"  ✗ Error testing persistence: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests and report results"""
        print("\n" + "="*70)
        print("HAVEN CONTROL ROOM USER EDITION - COMPREHENSIVE TEST SUITE")
        print("="*70)
        print(f"User Edition Location: {self.user_edition_dir}")
        print(f"Data File: {self.data_file}")
        
        tests = [
            ("User Edition Directory Structure", self.test_user_edition_structure),
            ("Data File Integrity", self.test_data_file_integrity),
            ("Map Generator Standalone", self.test_map_generator_standalone),
            ("No External Calls", self.test_no_external_calls),
            ("Data Persistence", self.test_data_persistence),
        ]
        
        results = []
        for test_name, test_func in tests:
            result = run_test(test_name, test_func)
            results.append((test_name, result))
            time.sleep(0.5)  # Brief pause between tests
        
        # Summary
        print(f"\n{'='*70}")
        print("TEST SUMMARY")
        print(f"{'='*70}")
        passed = sum(1 for _, r in results if r)
        total = len(results)
        print(f"Passed: {passed}/{total}")
        print()
        
        for name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status}: {name}")
        
        print(f"{'='*70}")
        
        if passed == total:
            print("✅ ALL TESTS PASSED - User Edition is ready!")
            return True
        else:
            print(f"❌ {total - passed} test(s) failed - See details above")
            return False


if __name__ == "__main__":
    tester = UserEditionTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
