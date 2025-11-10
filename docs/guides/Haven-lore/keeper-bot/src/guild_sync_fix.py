#!/usr/bin/env python3
"""
Guild Command Sync Fix for The Keeper Bot
Forces immediate guild-specific command sync with detailed debugging.
"""

import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

async def fix_guild_commands():
    """Force sync commands to specific guild with debugging."""
    
    load_dotenv('../.env')
    token = os.getenv('DISCORD_BOT_TOKEN')
    guild_id = os.getenv('GUILD_ID')
    
    if not token:
        print("❌ No Discord bot token found")
        return
        
    if not guild_id:
        print("❌ No GUILD_ID found in .env file")
        return
        
    print("🔧 GUILD COMMAND SYNC FIX")
    print("=" * 40)
    print(f"🎯 Target Guild ID: {guild_id}")
    print()
    
    # Create bot with proper permissions
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.members = True
    
    class FixBot(commands.Bot):
        def __init__(self):
            super().__init__(command_prefix='!', intents=intents)
            
        async def setup_hook(self):
            # Add all The Keeper's commands manually
            @self.tree.command(name="test-keeper", description="🧪 Test command to verify The Keeper is working")
            async def test_keeper(interaction: discord.Interaction):
                await interaction.response.send_message("✅ **The Keeper responds!** Slash commands are working!", ephemeral=True)
            
            @self.tree.command(name="setup-channels", description="🔧 Setup bot channels (Admin only)")
            async def setup_channels(interaction: discord.Interaction):
                await interaction.response.send_message("🔧 **Setup command works!** (This is a test response)", ephemeral=True)
                
        async def on_ready(self):
            print(f"🤖 Connected as {self.user}")
            print(f"📊 Connected to {len(self.guilds)} guild(s)")
            
            # List all guilds
            for guild in self.guilds:
                print(f"  • {guild.name} (ID: {guild.id})")
            print()
            
            # Verify target guild exists
            target_guild = self.get_guild(int(guild_id))
            if not target_guild:
                print(f"❌ Bot is not in guild {guild_id}")
                print("   Make sure the bot is invited to your Discord server!")
                await self.close()
                return
                
            print(f"✅ Found target guild: {target_guild.name}")
            print()
            
            # Check bot permissions in guild
            bot_member = target_guild.get_member(self.user.id)
            if bot_member:
                perms = bot_member.guild_permissions
                print("🔑 Bot permissions:")
                print(f"  • Administrator: {perms.administrator}")
                print(f"  • Use Slash Commands: {perms.use_slash_commands}")
                print(f"  • Send Messages: {perms.send_messages}")
                print(f"  • Manage Channels: {perms.manage_channels}")
                print()
                
                if not perms.use_slash_commands and not perms.administrator:
                    print("⚠️  Bot lacks 'Use Slash Commands' permission!")
                    print("   Add this permission in Discord server settings")
            
            # Count commands
            command_count = len(self.tree.get_commands())
            print(f"🎯 Commands to sync: {command_count}")
            
            # List commands
            for cmd in self.tree.get_commands():
                print(f"  • /{cmd.name} - {cmd.description}")
            print()
            
            # Force sync to guild
            try:
                guild_obj = discord.Object(id=int(guild_id))
                print("🔄 Syncing commands to guild...")
                synced = await self.tree.sync(guild=guild_obj)
                print(f"✅ SUCCESS! Synced {len(synced)} commands to {target_guild.name}")
                print()
                print("🎉 Commands should now appear instantly in your Discord server!")
                print("   Type / in any channel to see them")
                
            except discord.app_commands.MissingApplicationID:
                print("❌ Missing Application ID - bot token may be invalid")
            except discord.Forbidden:
                print("❌ Bot lacks permissions to sync commands")
                print("   Grant 'Administrator' permission in Discord")
            except discord.HTTPException as e:
                print(f"❌ HTTP error during sync: {e}")
                print("   This might be a rate limit - try again in a few minutes")
            except Exception as e:
                print(f"❌ Sync failed: {e}")
                import traceback
                traceback.print_exc()
            
            await self.close()
    
    bot = FixBot()
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(fix_guild_commands())