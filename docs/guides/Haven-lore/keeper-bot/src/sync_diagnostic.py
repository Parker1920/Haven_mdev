#!/usr/bin/env python3
"""
The Keeper Bot - Command Sync Diagnostic Tool
Tests command registration and syncing issues.
"""

import sys
import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_command_sync():
    """Test command syncing with detailed output."""
    
    # Load environment
    load_dotenv('../.env')
    token = os.getenv('DISCORD_BOT_TOKEN')
    guild_id = os.getenv('GUILD_ID')
    
    if not token:
        print("❌ No Discord bot token found in .env file")
        return
        
    print("🔧 COMMAND SYNC DIAGNOSTIC")
    print("=" * 40)
    print(f"Guild ID: {guild_id}")
    print()
    
    # Create minimal bot
    intents = discord.Intents.default()
    intents.message_content = True
    
    bot = commands.Bot(command_prefix='!', intents=intents)
    
    @bot.event
    async def on_ready():
        print(f"🤖 Connected as {bot.user}")
        print(f"📊 Connected to {len(bot.guilds)} guild(s)")
        print()
        
        # Load all cogs and count commands
        try:
            print("📦 Loading cogs...")
            await bot.load_extension('cogs.enhanced_discovery')
            await bot.load_extension('cogs.pattern_recognition') 
            await bot.load_extension('cogs.archive_system')
            await bot.load_extension('cogs.admin_tools')
            await bot.load_extension('cogs.community_features')
            print("✅ All cogs loaded successfully")
            print()
            
            # Count commands
            command_count = len(bot.tree.get_commands())
            print(f"🎯 Found {command_count} slash commands")
            
            # List all commands
            print("📋 Available commands:")
            for cmd in bot.tree.get_commands():
                print(f"  • /{cmd.name} - {cmd.description}")
            print()
            
            # Try syncing to guild first
            if guild_id:
                try:
                    guild = discord.Object(id=int(guild_id))
                    synced = await bot.tree.sync(guild=guild)
                    print(f"✅ Synced {len(synced)} commands to guild {guild_id}")
                    print("Guild sync successful!")
                except Exception as e:
                    print(f"❌ Guild sync failed: {e}")
                    print("Trying global sync...")
                    
                    # Try global sync as fallback
                    try:
                        synced = await bot.tree.sync()
                        print(f"✅ Synced {len(synced)} commands globally")
                        print("⚠️  Global sync successful - commands may take up to 1 hour to appear")
                    except Exception as e2:
                        print(f"❌ Global sync also failed: {e2}")
            else:
                # No guild ID, try global
                try:
                    synced = await bot.tree.sync()
                    print(f"✅ Synced {len(synced)} commands globally")
                    print("⚠️  Global sync - commands may take up to 1 hour to appear")
                except Exception as e:
                    print(f"❌ Global sync failed: {e}")
                    
        except Exception as e:
            print(f"❌ Error loading cogs: {e}")
            import traceback
            traceback.print_exc()
        
        print()
        print("🏁 Diagnostic complete - shutting down")
        await bot.close()
    
    # Start bot
    try:
        await bot.start(token)
    except Exception as e:
        print(f"❌ Bot startup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_command_sync())