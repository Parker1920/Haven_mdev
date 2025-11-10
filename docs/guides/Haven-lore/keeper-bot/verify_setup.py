"""
The Keeper Bot - Setup and Verification Script
Tests bot functionality and Haven integration.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

async def test_haven_integration():
    """Test Haven data integration."""
    print("🗺️  Testing Haven Integration...")
    
    try:
        from core.haven_integration import HavenIntegration
        
        haven = HavenIntegration()
        success = await haven.load_haven_data()
        
        if success:
            systems = haven.get_all_systems()
            print(f"   ✅ Haven data loaded: {len(systems)} star systems")
            
            # Test system selection
            if systems:
                first_system = list(systems.keys())[0]
                system_data = haven.get_system(first_system)
                print(f"   ✅ System lookup works: {first_system}")
                
                # Test location choices
                choices = haven.create_discovery_location_choices(first_system)
                print(f"   ✅ Location choices: {len(choices)} options for {first_system}")
                
                # Test regional stats
                region = system_data.get('region', 'Unknown')
                stats = haven.get_regional_statistics(region)
                print(f"   ✅ Regional analysis: {region} has {stats['system_count']} systems")
            
            return True
        else:
            print("   ❌ Haven data not found - bot will run in standalone mode")
            return False
            
    except Exception as e:
        print(f"   ❌ Haven integration error: {e}")
        return False

async def test_database():
    """Test database functionality."""
    print("🗃️  Testing Database...")
    
    try:
        from database.keeper_db import KeeperDatabase
        
        db = KeeperDatabase("./data/test_keeper.db")
        await db.initialize()
        
        # Test discovery creation
        test_discovery = {
            'user_id': '123456789',
            'username': 'TestExplorer',
            'type': '🦴',
            'location': 'Test Planet — Test Galaxy',
            'description': 'Test discovery for verification',
            'system_name': 'Test System',
            'location_type': 'planet',
            'location_name': 'Test Planet'
        }
        
        discovery_id = await db.add_discovery(test_discovery)
        print(f"   ✅ Discovery creation: ID {discovery_id}")
        
        # Test discovery retrieval
        retrieved = await db.get_discovery(discovery_id)
        if retrieved:
            print(f"   ✅ Discovery retrieval: {retrieved['type']} {retrieved['description'][:30]}...")
        
        await db.close()
        
        # Clean up test database
        if os.path.exists("./data/test_keeper.db"):
            os.remove("./data/test_keeper.db")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

async def test_keeper_personality():
    """Test Keeper personality system."""
    print("🎭  Testing Keeper Personality...")
    
    try:
        with open('./src/config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        from core.keeper_personality import KeeperPersonality
        
        personality = KeeperPersonality(config)
        
        # Test voice lines
        greeting = personality.get_voice_line('greeting')
        print(f"   ✅ Voice generation: '{greeting[:50]}...'")
        
        # Test embed creation
        test_discovery = {
            'type': '🦴',
            'location': 'Test Location',
            'time_period': 'Ancient',
            'condition': 'Well-Preserved',
            'description': 'A test discovery for verification',
            'id': 1
        }
        
        embed = personality.create_discovery_analysis(test_discovery)
        print(f"   ✅ Embed creation: {embed.title}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Personality error: {e}")
        return False

def check_environment():
    """Check environment setup."""
    print("⚙️  Checking Environment...")
    
    # Check Python version
    version = sys.version_info
    if version >= (3, 10):
        print(f"   ✅ Python version: {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"   ❌ Python version: {version.major}.{version.minor}.{version.micro} (requires 3.10+)")
        return False
    
    # Check required directories
    dirs = ['./src', './data', './logs']
    for directory in dirs:
        if os.path.exists(directory):
            print(f"   ✅ Directory exists: {directory}")
        else:
            print(f"   ❌ Directory missing: {directory}")
            return False
    
    # Check config file
    if os.path.exists('./src/config.json'):
        print("   ✅ Config file exists")
        try:
            with open('./src/config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"   ✅ Config loaded: {len(config)} sections")
        except Exception as e:
            print(f"   ❌ Config error: {e}")
            return False
    else:
        print("   ❌ Config file missing: ./src/config.json")
        return False
    
    # Check .env.example
    if os.path.exists('./.env.example'):
        print("   ✅ Environment template exists")
    else:
        print("   ❌ Environment template missing")
        return False
    
    return True

def check_dependencies():
    """Check if required packages are available."""
    print("📦  Checking Dependencies...")
    
    required_packages = [
        'discord',
        'aiosqlite', 
        'aiofiles',
        'dotenv'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\\n   Install missing packages with:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True

async def main():
    """Main verification process."""
    print("🌌 The Keeper Bot - Setup Verification")
    print("=" * 50)
    
    # Environment checks
    env_ok = check_environment()
    deps_ok = check_dependencies()
    
    if not (env_ok and deps_ok):
        print("\\n❌ Environment setup incomplete. Please fix the above issues.")
        return
    
    print("\\n🔧  Testing Bot Components...")
    
    # Component tests
    personality_ok = await test_keeper_personality()
    database_ok = await test_database()
    haven_ok = await test_haven_integration()
    
    print("\\n" + "=" * 50)
    print("📊  Verification Summary:")
    print("=" * 50)
    
    results = {
        "Environment Setup": env_ok,
        "Dependencies": deps_ok,
        "Keeper Personality": personality_ok,
        "Database System": database_ok,
        "Haven Integration": haven_ok
    }
    
    for component, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {component}")
    
    success_count = sum(results.values())
    total_count = len(results)
    
    if success_count == total_count:
        print(f"\\n🎉  All systems operational! The Keeper is ready to serve.")
        print("\\n🚀  Next Steps:")
        print("   1. Copy .env.example to .env and configure your bot token")
        print("   2. Set up Discord channels using /setup-channels")
        print("   3. Run the bot with: python src/main.py")
        print("\\n📚  Phase Implementation Status:")
        print("   ✅ Phase 1: Discovery submission system")
        print("   ✅ Phase 2: Pattern recognition + investigation threads")
        print("   🚧 Phase 3: Advanced archive + admin tools")
        print("   🚧 Phase 4: Community engagement features")
    else:
        print(f"\\n⚠️   {success_count}/{total_count} systems operational.")
        print("     Please resolve the failed components before proceeding.")

if __name__ == "__main__":
    asyncio.run(main())