#!/usr/bin/env python3
"""
Simple command sync script for The Keeper Bot
Forces global command sync to fix slash command issues.
"""

import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

async def force_sync():
    """Force sync commands globally."""
    
    # Load environment
    load_dotenv('../.env')
    token = os.getenv('DISCORD_BOT_TOKEN')
    guild_id = os.getenv('GUILD_ID')
    
    if not token:
        print("❌ No Discord bot token found")
        return
        
    print("🔄 FORCING COMMAND SYNC")
    print("=" * 30)
    print()
    
    # Create minimal bot
    intents = discord.Intents.default()
    intents.message_content = True
    
    class SyncBot(commands.Bot):
        def __init__(self):
            super().__init__(command_prefix='!', intents=intents)
            
        async def setup_hook(self):
            # Add a simple test command to verify syncing
            @self.tree.command(name="test", description="Test command for sync verification")
            async def test_cmd(interaction: discord.Interaction):
                await interaction.response.send_message("✅ Commands are working!", ephemeral=True)
        
        async def on_ready(self):
            print(f"🤖 Connected as {self.user}")
            print()
            
            try:
                # Try guild sync first
                if guild_id:
                    guild = discord.Object(id=int(guild_id))
                    synced = await self.tree.sync(guild=guild)
                    print(f"✅ Guild sync: {len(synced)} commands")
                else:
                    print("⚠️  No GUILD_ID found, using global sync")
                    
                # Also do global sync as backup
                synced_global = await self.tree.sync()
                print(f"✅ Global sync: {len(synced_global)} commands")
                print()
                print("🎯 COMMANDS SHOULD NOW BE AVAILABLE IN DISCORD!")
                print("   (May take a few minutes to appear)")
                print()
                print("Try typing / in your Discord server to see available commands")
                
            except Exception as e:
                print(f"❌ Sync failed: {e}")
                import traceback
                traceback.print_exc()
            
            await self.close()
    
    bot = SyncBot()
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(force_sync())