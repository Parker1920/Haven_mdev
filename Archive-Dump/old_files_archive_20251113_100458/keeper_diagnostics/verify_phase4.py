#!/usr/bin/env python3
"""
The Keeper Bot - Complete Setup Verification (Phase 4)
Verifies all components are properly installed and configured.
"""

import os
import sys
import json
import asyncio
import sqlite3
from pathlib import Path

def print_section(title):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_check(item, status, details=""):
    """Print a check result."""
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {item}")
    if details:
        print(f"   {details}")

async def verify_complete_setup():
    """Verify complete Keeper bot setup."""
    print("🌌 THE KEEPER BOT - COMPLETE SETUP VERIFICATION (PHASE 4)")
    print("=" * 60)
    
    all_checks_passed = True
    
    # Phase 1: Basic Requirements
    print_section("PHASE 1: CORE REQUIREMENTS")
    
    # Python version check
    python_version = sys.version_info
    python_ok = python_version >= (3, 8)
    print_check(f"Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}", 
                python_ok, "Requires Python 3.8+" if not python_ok else "")
    all_checks_passed &= python_ok
    
    # Check for required packages
    required_packages = [
        ('discord', 'discord.py'),
        ('aiofiles', 'aiofiles'),
        ('aiosqlite', 'aiosqlite')
    ]
    
    for package, display_name in required_packages:
        try:
            __import__(package)
            print_check(f"{display_name} installed", True)
        except ImportError:
            print_check(f"{display_name} installed", False, f"Run: pip install {package}")
            all_checks_passed = False
    
    # Check project structure
    print_section("PHASE 1: PROJECT STRUCTURE")
    
    expected_files = [
        'src/main.py',
        'src/config.json',
        'src/core/keeper_personality.py',
        'src/core/haven_integration.py',
        'src/database/keeper_db.py',
        'src/cogs/enhanced_discovery.py',
        'src/cogs/pattern_recognition.py',
        'src/cogs/archive_system.py',
        'src/cogs/admin_tools.py',
        'src/cogs/community_features.py',  # Phase 4
        'requirements.txt'
    ]
    
    for file_path in expected_files:
        file_exists = Path(file_path).exists()
        print_check(f"File: {file_path}", file_exists)
        all_checks_passed &= file_exists
    
    # Check configuration
    print_section("PHASE 1: CONFIGURATION")
    
    try:
        with open('src/config.json', 'r') as f:
            config = json.load(f)
        print_check("config.json readable", True)
        
        # Check config structure
        required_keys = ['bot', 'theme', 'database']
        for key in required_keys:
            key_exists = key in config
            print_check(f"Config key: {key}", key_exists)
            all_checks_passed &= key_exists
            
    except Exception as e:
        print_check("config.json readable", False, str(e))
        all_checks_passed = False
    
    # Phase 2: Haven Integration
    print_section("PHASE 2: HAVEN INTEGRATION")
    
    # Check for Haven folder
    haven_paths = [
        '/Users/parkerstouffer/Desktop/untitled folder/Haven_mdev',
        './Haven_mdev',
        '../Haven_mdev'
    ]
    
    haven_found = False
    for haven_path in haven_paths:
        if Path(haven_path).exists():
            data_file = Path(haven_path) / 'data' / 'data.json'
            if data_file.exists():
                print_check(f"Haven integration path: {haven_path}", True)
                
                try:
                    with open(data_file, 'r') as f:
                        haven_data = json.load(f)
                    system_count = len(haven_data.get('star_systems', []))
                    print_check(f"Haven data loaded: {system_count} star systems", True)
                    haven_found = True
                    break
                except Exception as e:
                    print_check(f"Haven data readable", False, str(e))
            else:
                print_check(f"Haven data file missing: {data_file}", False)
    
    if not haven_found:
        print_check("Haven integration", False, "Haven_mdev folder not found in expected locations")
        all_checks_passed = False
    
    # Phase 3: Database Verification
    print_section("PHASE 3: DATABASE SYSTEM")
    
    try:
        # Test database creation
        db_path = "data/keeper.db"
        os.makedirs("data", exist_ok=True)
        
        # Import and test database
        sys.path.append('src')
        from database.keeper_db import KeeperDatabase
        
        db = KeeperDatabase()
        await db.initialize()
        
        # Check if tables were created
        async with db.connection.execute("""
            SELECT name FROM sqlite_master WHERE type='table'
        """) as cursor:
            tables = [row[0] for row in await cursor.fetchall()]
        
        expected_tables = [
            'discoveries', 'patterns', 'pattern_discoveries', 'investigations',
            'archive_entries', 'user_stats', 'server_config',
            # Phase 4 tables
            'user_tier_progress', 'community_challenges', 'challenge_submissions',
            'user_achievements', 'community_events', 'pattern_contributions'
        ]
        
        for table in expected_tables:
            table_exists = table in tables
            print_check(f"Database table: {table}", table_exists)
            all_checks_passed &= table_exists
        
        await db.connection.close()
        
    except Exception as e:
        print_check("Database initialization", False, str(e))
        all_checks_passed = False
    
    # Phase 4: Community Features
    print_section("PHASE 4: COMMUNITY FEATURES")
    
    try:
        # Test community features import
        from cogs.community_features import CommunityFeatures
        print_check("Community features module", True)
        
        # Test personality enhancements
        from core.keeper_personality import KeeperPersonality
        personality = KeeperPersonality(config if 'config' in locals() else {})
        
        # Check for Phase 4 attributes
        phase4_attributes = [
            'tier_acknowledgments',
            'community_responses', 
            'story_themes'
        ]
        
        for attr in phase4_attributes:
            attr_exists = hasattr(personality, attr)
            print_check(f"Personality attribute: {attr}", attr_exists)
            all_checks_passed &= attr_exists
            
        # Test Phase 4 methods
        phase4_methods = [
            'get_tier_acknowledgment',
            'create_tier_progression_embed',
            'generate_personalized_story'
        ]
        
        for method in phase4_methods:
            method_exists = hasattr(personality, method)
            print_check(f"Personality method: {method}", method_exists)
            all_checks_passed &= method_exists
            
    except Exception as e:
        print_check("Community features verification", False, str(e))
        all_checks_passed = False
    
    # Environment Configuration
    print_section("ENVIRONMENT CONFIGURATION")
    
    env_file_exists = Path('.env').exists()
    print_check(".env file exists", env_file_exists)
    
    if env_file_exists:
        try:
            with open('.env', 'r') as f:
                env_content = f.read()
            
            has_bot_token = 'DISCORD_BOT_TOKEN=' in env_content
            print_check("Discord bot token configured", has_bot_token)
            
            if not has_bot_token:
                print("   ⚠️  Add your Discord bot token to .env file:")
                print("   DISCORD_BOT_TOKEN=your_bot_token_here")
                
        except Exception as e:
            print_check(".env file readable", False, str(e))
    else:
        print("   ℹ️  Create .env file with your Discord bot token:")
        print("   DISCORD_BOT_TOKEN=your_bot_token_here")
    
    # Summary
    print_section("VERIFICATION SUMMARY")
    
    if all_checks_passed:
        print("🎉 ALL SYSTEMS OPERATIONAL")
        print("   The Keeper Bot is ready for deployment!")
        print("   Complete with Phase 4 community features:")
        print("   • Mystery tier progression system")
        print("   • Community challenges and events")  
        print("   • Explorer leaderboards")
        print("   • Personalized Keeper storytelling")
        print("   • Advanced achievement system")
        print()
        print("   🚀 To launch: cd src && python main.py")
        print()
        print("   📋 Next steps:")
        print("   1. Configure Discord channels with /setup-channels")
        print("   2. Start your first community challenge")
        print("   3. Watch explorers progress through the tiers!")
    else:
        print("❌ SETUP INCOMPLETE")
        print("   Please resolve the issues above before launching.")
        print("   Re-run this script after making fixes.")
    
    return all_checks_passed

if __name__ == "__main__":
    # Run the verification
    result = asyncio.run(verify_complete_setup())
    sys.exit(0 if result else 1)