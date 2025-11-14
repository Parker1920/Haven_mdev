"""
Emergency Command Sync Tool
Use this to force-sync commands if they're not working
"""
import asyncio
import discord
from discord.ext import commands
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

async def emergency_sync():
    """Force sync with diagnostic output"""
    
    token = os.getenv('BOT_TOKEN')
    guild_id = os.getenv('GUILD_ID')
    
    if not token or not guild_id:
        print("❌ BOT_TOKEN or GUILD_ID not found in .env")
        return
    
    print("=" * 70)
    print("🚨 EMERGENCY COMMAND SYNC")
    print("=" * 70)
    print()
    print(f"Guild ID: {guild_id}")
    print()
    
    # Create bot with minimal setup
    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix='!', intents=intents)
    
    # Add a test command
    @bot.tree.command(name="test-sync", description="Test if sync is working")
    async def test_command(interaction: discord.Interaction):
        await interaction.response.send_message("✅ Commands are synced!", ephemeral=True)
    
    @bot.event
    async def on_ready():
        print(f"✅ Logged in as {bot.user}")
        print(f"📊 Bot is in {len(bot.guilds)} guild(s)")
        print()
        
        guild = discord.Object(id=int(guild_id))
        
        # Step 1: Check current commands
        print("[1/5] Checking existing commands...")
        try:
            current_guild_commands = await bot.tree.fetch_commands(guild=guild)
            current_global_commands = await bot.tree.fetch_commands()
            print(f"   📝 Current guild commands: {len(current_guild_commands)}")
            print(f"   🌐 Current global commands: {len(current_global_commands)}")
        except discord.Forbidden:
            print("   ❌ ERROR: Bot doesn't have applications.commands scope!")
            print("   ⚠️  You MUST re-authorize the bot with this URL:")
            print()
            print(f"   https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=274878294016&scope=bot%20applications.commands")
            print()
            await bot.close()
            return
        except Exception as e:
            print(f"   ⚠️  Error checking commands: {e}")
        
        print()
        
        # Step 2: Clear global commands
        print("[2/5] Clearing global commands...")
        try:
            bot.tree.clear_commands(guild=None)
            await bot.tree.sync()
            print("   ✅ Global commands cleared")
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
        
        print()
        
        # Step 3: Clear guild commands
        print("[3/5] Clearing guild commands...")
        try:
            bot.tree.clear_commands(guild=guild)
            await bot.tree.sync(guild=guild)
            print("   ✅ Guild commands cleared")
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
        
        print()
        
        # Step 4: Sync to guild
        print("[4/5] Syncing commands to guild...")
        try:
            synced = await bot.tree.sync(guild=guild)
            print(f"   ✅ Synced {len(synced)} commands to guild!")
            if synced:
                print("   📝 Commands synced:")
                for cmd in synced:
                    print(f"      - /{cmd.name}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
        
        # Step 5: Verify
        print("[5/5] Verifying sync...")
        try:
            await asyncio.sleep(2)
            current = await bot.tree.fetch_commands(guild=guild)
            print(f"   ✅ Verification: {len(current)} commands now in guild")
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
        
        print()
        print("=" * 70)
        print("🎉 SYNC COMPLETE!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Commands should now work in Discord")
        print("2. Try typing / in any channel")
        print("3. If still not working, check bot role permissions")
        print()
        
        await bot.close()
    
    try:
        await bot.start(token)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    asyncio.run(emergency_sync())
