"""
Test script to verify map generator correctly handles test data vs production data.

This script simulates what Control Room does when switching between test and production data.
"""
import subprocess
import sys
from pathlib import Path

def test_map_generation():
    """Test both production and test data map generation."""
    print("="*70)
    print("MAP GENERATOR TEST DATA FIX VERIFICATION")
    print("="*70)
    print()
    
    # Test 1: Production data (should use database)
    print("TEST 1: Production Data (should use database - 11 systems)")
    print("-" * 70)
    result = subprocess.run(
        [sys.executable, "src/Beta_VH_Map.py", "--data-file", "data/data.json", "--no-open", "--limit", "3"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    output = result.stdout + result.stderr
    print(output[:500])  # Print first 500 chars
    
    if "Loading systems from DATABASE backend" in output:
        print("✅ PASS: Using database backend for production data")
    elif "Loaded 11 systems from database backend" in output:
        print("✅ PASS: Using database backend for production data")
    else:
        print("❌ FAIL: Should be using database backend")
    print()
    
    # Test 2: Test data (should use JSON file)
    print("TEST 2: Test Data (should use JSON file - 500 systems)")
    print("-" * 70)
    result = subprocess.run(
        [sys.executable, "src/Beta_VH_Map.py", "--data-file", "tests/stress_testing/TESTING.json", "--no-open", "--limit", "3"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    output = result.stdout + result.stderr
    print(output[:500])  # Print first 500 chars
    
    if "Loading systems from custom data file" in output and "Loaded 500 records" in output:
        print("✅ PASS: Using test data JSON file (500 systems)")
    else:
        print("❌ FAIL: Should be using test data JSON file")
    print()
    
    print("="*70)
    print("VERIFICATION COMPLETE")
    print("="*70)

if __name__ == "__main__":
    test_map_generation()
