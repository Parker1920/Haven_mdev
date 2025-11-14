#!/usr/bin/env python3
"""
Quick slash command fix for The Keeper Bot
"""

import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

async def quick_fix():
    load_dotenv('../.env')
    token = os.getenv('DISCORD_BOT_TOKEN')
    guild_id = os.getenv('GUILD_ID')
    
    print("🔧 QUICK SLASH COMMAND FIX")
    print(f"Guild ID: {guild_id}")
    
    intents = discord.Intents.default()
    intents.message_content = True
    
    class QuickBot(commands.Bot):
        async def on_ready(self):
            print(f"Connected as {self.user}")
            
            # Add a simple test command
            @self.tree.command(name="keeper-test", description="Test if slash commands work")
            async def keeper_test(interaction: discord.Interaction):
                await interaction.response.send_message("✅ Slash commands working!", ephemeral=True)
            
            # Force sync to both guild and global
            try:
                if guild_id:
                    guild = discord.Object(id=int(guild_id))
                    synced_guild = await self.tree.sync(guild=guild)
                    print(f"Guild sync: {len(synced_guild)} commands")
                
                synced_global = await self.tree.sync()
                print(f"Global sync: {len(synced_global)} commands")
                print("✅ Sync complete! Check Discord in 1-2 minutes.")
                
            except Exception as e:
                print(f"Error: {e}")
            
            await self.close()
    
    bot = QuickBot(command_prefix='!', intents=intents)
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(quick_fix())