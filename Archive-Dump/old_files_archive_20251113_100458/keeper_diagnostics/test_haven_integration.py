"""
Test Keeper Bot Haven Integration
Quick test to verify bot can load the test data
"""
import sys
import os
sys.path.insert(0, 'src')

from dotenv import load_dotenv
load_dotenv('.env')

print("=" * 70)
print("TESTING KEEPER BOT HAVEN INTEGRATION")
print("=" * 70)
print()

# Check environment
haven_path = os.getenv('HAVEN_DATA_PATH')
print(f"📍 HAVEN_DATA_PATH from .env: {haven_path}")
print(f"✅ File exists: {os.path.exists(haven_path) if haven_path else False}")
print()

# Test Haven Integration
from core.haven_integration import HavenIntegration
import asyncio

h = HavenIntegration()
print(f"🔍 Haven integration found path: {h.haven_data_path}")

# Load data
loaded = asyncio.run(h.load_haven_data())
print(f"📥 Data loaded: {loaded}")
print()

if loaded:
    systems = h.get_all_systems()
    print(f"✅ SUCCESS: Loaded {len(systems)} test systems")
    print()
    print("Systems available:")
    for i, (name, data) in enumerate(systems.items(), 1):
        planets = len(data.get('planets', []))
        region = data.get('region', 'Unknown')
        print(f"   {i}. {name:20} - {region:20} - {planets} planets")
    
    print()
    print("=" * 70)
    print("✅ INTEGRATION TEST PASSED")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Make sure Discord bot token is set in .env")
    print("2. Run: .venv\\Scripts\\python.exe src\\main.py")
    print("3. Test /discovery-report command in Discord")
    
else:
    print("❌ FAILED: Could not load Haven data")
    print(f"Expected path: {haven_path}")
