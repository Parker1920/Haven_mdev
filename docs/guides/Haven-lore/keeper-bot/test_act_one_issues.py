"""
Test script to diagnose why Act I story content doesn't appear in Discord.
This will systematically check all potential issues.
"""

import os
import sys
import json
import sqlite3
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

print("=" * 70)
print("ACT I DIAGNOSTIC TEST")
print("=" * 70)
print()

# Test 1: Check .env configuration
print("TEST 1: Checking .env configuration...")
print("-" * 70)

env_path = Path(__file__).parent / '.env'
if not env_path.exists():
    print("❌ ISSUE: .env file does not exist!")
else:
    # Parse .env manually
    env_vars = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    bot_token = env_vars.get('BOT_TOKEN', '')
    guild_id = env_vars.get('GUILD_ID', '')
    archive_channel_id = env_vars.get('ARCHIVE_CHANNEL_ID', '')
    discovery_channel_id = env_vars.get('DISCOVERY_CHANNEL_ID', '')
    
    print(f"✓ .env file exists")
    print(f"  BOT_TOKEN: {'✓ Set' if bot_token else '❌ MISSING'}")
    print(f"  GUILD_ID: {'✓ Set' if guild_id else '❌ MISSING'} ({guild_id})")
    print(f"  ARCHIVE_CHANNEL_ID: {'✓ Set' if archive_channel_id else '❌ EMPTY - ISSUE #1'} ({archive_channel_id})")
    print(f"  DISCOVERY_CHANNEL_ID: {'✓ Set' if discovery_channel_id else '❌ EMPTY'} ({discovery_channel_id})")
    
    if not archive_channel_id:
        print()
        print("🔴 ISSUE #1 CONFIRMED: ARCHIVE_CHANNEL_ID is empty!")
        print("   The startup embed in on_ready() will never be sent because:")
        print("   if archive_channel_id:  # This evaluates to False!")
        print("       channel = self.get_channel(int(archive_channel_id))")
        print("       await channel.send(embed=startup_embed)")

print()

# Test 2: Check database schema
print("TEST 2: Checking database schema...")
print("-" * 70)

db_path = Path(__file__).parent / 'src' / 'data' / 'keeper.db'
if not db_path.exists():
    print(f"⚠️ WARNING: Database doesn't exist yet at {db_path}")
    print("   (This is normal if bot hasn't been run)")
else:
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"✓ Database exists with {len(tables)} tables:")
    for table in tables:
        print(f"  - {table}")
    
    # Check for story progression tracking
    if 'story_progression' in tables:
        print("✓ story_progression table exists")
    else:
        print()
        print("🔴 ISSUE #2 CONFIRMED: No story_progression table!")
        print("   Database has NO tracking for Act I, II, or III progression")
        print("   Tables found: " + ", ".join(tables))
    
    # Check for act columns in other tables
    cursor.execute("PRAGMA table_info(server_config)")
    columns = [row[1] for row in cursor.fetchall()]
    
    act_columns = [col for col in columns if 'act' in col.lower() or 'story' in col.lower()]
    if act_columns:
        print(f"✓ Story columns found in server_config: {act_columns}")
    else:
        print("❌ No act/story columns in server_config table")
        print(f"   Available columns: {', '.join(columns)}")
    
    conn.close()

print()

# Test 3: Check keeper_personality.py for Act I content
print("TEST 3: Checking keeper_personality.py for Act I references...")
print("-" * 70)

personality_path = Path(__file__).parent / 'src' / 'core' / 'keeper_personality.py'
if personality_path.exists():
    with open(personality_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for create_welcome_embed
    if 'def create_welcome_embed' in content:
        print("✓ create_welcome_embed() method exists")
        
        # Check what it says
        if 'consciousness born from forgotten data' in content:
            print("  ✓ Contains Act I lore: 'consciousness born from forgotten data'")
    
    # Check for create_startup_embed  
    if 'def create_startup_embed' in content:
        print("✓ create_startup_embed() method exists")
    
    # Check for Act I references
    act_references = ['Act I', 'Act 1', 'Awakening in Silence', 'awakening', 'The Awakening']
    found_references = [ref for ref in act_references if ref in content]
    
    if found_references:
        print(f"✓ Act I references found: {found_references}")
    else:
        print("❌ NO explicit 'Act I' or 'Awakening' references found")
        print("   The embeds exist but don't explicitly reference the story acts")

else:
    print("❌ keeper_personality.py not found!")

print()

# Test 4: Check main.py on_ready and on_guild_join
print("TEST 4: Checking main.py event handlers...")
print("-" * 70)

main_path = Path(__file__).parent / 'src' / 'main.py'
if main_path.exists():
    with open(main_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check on_ready
    if 'async def on_ready' in content:
        print("✓ on_ready() handler exists")
        
        # Check what happens in on_ready
        if 'ARCHIVE_CHANNEL_ID' in content:
            print("  ✓ Checks ARCHIVE_CHANNEL_ID")
            print("  🔴 But this is EMPTY in .env, so startup embed never sends!")
        
        if 'create_startup_embed' in content:
            print("  ✓ Calls create_startup_embed()")
    
    # Check on_guild_join
    if 'async def on_guild_join' in content:
        print("✓ on_guild_join() handler exists")
        
        if 'create_welcome_embed' in content:
            print("  ✓ Calls create_welcome_embed()")
        
        print()
        print("  🔴 ISSUE #3: on_guild_join only fires when bot joins NEW guild!")
        print("     If the bot is already in your server, this will NEVER fire")
        print("     This means Act I welcome message was only shown once (if at all)")
    
    # Check for on_member_join
    if 'async def on_member_join' in content:
        print("✓ on_member_join() handler exists (greets new users)")
    else:
        print("❌ No on_member_join() handler")
        print("   New Discord members don't get Act I introduction!")

print()

# Test 5: Check for /keeper-story command
print("TEST 5: Checking /keeper-story command...")
print("-" * 70)

community_features_path = Path(__file__).parent / 'src' / 'cogs' / 'community_features.py'
if community_features_path.exists():
    with open(community_features_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'name="keeper-story"' in content:
        print("✓ /keeper-story command exists")
        
        # Check what story it tells
        if '_generate_personalized_story' in content:
            print("  ✓ Generates personalized story")
            
            # Check if it mentions Act I, II, III
            if any(act in content for act in ['Act I', 'Act II', 'Act III', 'Act 1', 'Act 2', 'Act 3']):
                print("  ✓ References Act I/II/III explicitly")
            else:
                print("  🔴 ISSUE #4: Does NOT reference Act I/II/III!")
                print("     The story is tier-based (Tier 1-4), not act-based")
                print("     Players see tier progression, not narrative acts")

print()

# Test 6: Check config.json for story settings
print("TEST 6: Checking config.json...")
print("-" * 70)

config_path = Path(__file__).parent / 'src' / 'config.json'
if config_path.exists():
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("✓ config.json exists")
    
    # Check for story settings
    if 'story' in config:
        print("  ✓ Has 'story' section")
        print(f"    {config['story']}")
    else:
        print("  ❌ No 'story' section in config")
    
    if 'keeper' in config:
        print(f"  ✓ Has 'keeper' section")
        if 'personality' in config['keeper']:
            print(f"    Personality mode: {config['keeper'].get('personality', {})}")

print()

# SUMMARY
print("=" * 70)
print("DIAGNOSIS SUMMARY")
print("=" * 70)
print()
print("🔴 CRITICAL ISSUES FOUND:")
print()
print("ISSUE #1: ARCHIVE_CHANNEL_ID is empty in .env")
print("  → Startup embed (Act I introduction) never sends")
print("  → Fix: Run /setup-channels command in Discord or manually set ARCHIVE_CHANNEL_ID")
print()
print("ISSUE #2: No story_progression table in database")
print("  → Bot has NO tracking for Act I, II, III completion")
print("  → Fix: Create story_progression table with act_1_complete, act_2_complete, act_3_complete")
print()
print("ISSUE #3: on_guild_join only fires for NEW guilds")
print("  → If bot already in server, Act I welcome never shows again")
print("  → Fix: Create /story-intro command to manually trigger Act I introduction")
print()
print("ISSUE #4: /keeper-story uses tier system (1-4), not Act system (I-III)")
print("  → Players see tier progression, not narrative acts")
print("  → Fix: Add Act I/II/III references to tier stories, or create separate /story-progress command")
print()
print("ISSUE #5: No on_member_join handler for Act I intro")
print("  → New Discord members don't get introduced to the story")
print("  → Fix: Send Act I intro DM or channel message when new member joins")
print()
print("=" * 70)
print("RECOMMENDED FIXES:")
print("=" * 70)
print()
print("1. Set ARCHIVE_CHANNEL_ID in .env (run /setup-channels)")
print("2. Add story_progression table to database")
print("3. Create /story-intro command (shows Act I anytime)")
print("4. Create /story-progress command (shows current act and progression)")
print("5. Add Act I/II/III references to existing content")
print("6. Add on_member_join to greet new users with Act I")
print("7. Modify tier stories to reference Acts explicitly")
print()
print("Would you like me to implement these fixes? (y/n)")
print()
