"""
The Keeper - Discord Bot
A mysterious intelligence that archives discoveries and reveals patterns.
"""

import discord
from discord.ext import commands
import json
import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

from database.keeper_db import KeeperDatabase
from core.keeper_personality import KeeperPersonality
from cogs.enhanced_discovery import EnhancedDiscoverySystem
from cogs.pattern_recognition import PatternRecognition
from cogs.archive_system import ArchiveSystem
from cogs.admin_tools import AdminTools
from sync.sync_worker import SyncWorker
from api.sync_api import SyncAPI

# Load environment variables from parent directory
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

# Configure logging with UTF-8 encoding for Windows
import sys
# Force UTF-8 output for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/keeper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('keeper')

class TheKeeper(commands.Bot):
    """The Keeper - Main bot class embodying the mysterious archivist."""
    
    def __init__(self):
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Bot intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix='!keeper ',
            intents=intents,
            help_command=None
        )
        
        # Initialize components
        self.db = None
        self.personality = None
        self.startup_time = None
        self.sync_worker = None
        self.sync_api = None
        
    async def setup_hook(self):
        """Setup the bot components."""
        logger.info("🌌 The Keeper awakens...")
        
        # Initialize database
        self.db = KeeperDatabase()
        await self.db.initialize()
        
        # Initialize personality
        self.personality = KeeperPersonality(self.config)
        
        # Load cogs with error handling
        cogs_to_load = [
            'cogs.enhanced_discovery',
            'cogs.pattern_recognition',
            'cogs.archive_system',
            'cogs.admin_tools',
            'cogs.community_features'
        ]
        
        loaded_cogs = 0
        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                logger.info(f"✅ Loaded {cog}")
                loaded_cogs += 1
            except Exception as e:
                logger.error(f"❌ Failed to load {cog}: {e}")
                import traceback
                traceback.print_exc()
        
        logger.info(f"📦 Loaded {loaded_cogs}/{len(cogs_to_load)} cogs")

        # Start sync worker (built-in background task)
        self.sync_worker = SyncWorker(self.db, sync_interval=30)
        await self.sync_worker.start()
        logger.info("🔄 Sync worker started (30s intervals)")

        # Start HTTP API for Control Room integration
        api_port = int(os.getenv('SYNC_API_PORT', 8080))
        self.sync_api = SyncAPI(self, port=api_port)
        await self.sync_api.start()
        logger.info(f"🌐 Sync API available on port {api_port}")

        # Count commands before syncing
        command_count = len(self.tree.get_commands())
        logger.info(f"🎯 Found {command_count} slash commands to sync")
        
        # Sync commands to guild for instant updates
        try:
            guild_id = os.getenv('GUILD_ID')
            if guild_id:
                guild = discord.Object(id=int(guild_id))
                
                # Copy all commands to guild tree
                logger.info("📋 Copying commands to guild tree...")
                self.tree.copy_global_to(guild=guild)
                
                # Now sync to the guild
                synced = await self.tree.sync(guild=guild)
                logger.info(f"✅ Synced {len(synced)} commands to guild {guild_id}")
                
                if len(synced) == 0:
                    logger.error("⚠️ WARNING: 0 commands synced! Bot may not have applications.commands scope!")
                    logger.error(f"⚠️ Re-invite bot with: https://discord.com/api/oauth2/authorize?client_id={self.user.id}&permissions=274878294016&scope=bot%20applications.commands")
            else:
                logger.error("GUILD_ID not found - cannot sync commands")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
            import traceback
            traceback.print_exc()
    
    async def on_ready(self):
        """Called when the bot is ready."""
        self.startup_time = datetime.utcnow()
        
        # Set presence
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="the patterns between stars..."
        )
        await self.change_presence(activity=activity, status=discord.Status.online)
        
        logger.info(f"🔮 The Keeper is online as {self.user}")
        logger.info(f"📊 Connected to {len(self.guilds)} guild(s)")
        
        # Send startup message to archive channel if configured
        archive_channel_id = os.getenv('ARCHIVE_CHANNEL_ID')
        if archive_channel_id:
            channel = self.get_channel(int(archive_channel_id))
            if channel:
                embed = self.personality.create_startup_embed()
                await channel.send(embed=embed)
    
    async def on_guild_join(self, guild):
        """Called when the bot joins a new guild."""
        logger.info(f"📡 The Keeper has been invited to {guild.name} ({guild.id})")
        
        # Try to find a general channel to send welcome message
        general_channel = None
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                general_channel = channel
                break
        
        if general_channel:
            embed = self.personality.create_welcome_embed()
            await general_channel.send(embed=embed)
    
    async def on_member_join(self, member):
        """Called when a new member joins the guild."""
        logger.info(f"👤 New member joined: {member.name} ({member.id})")
        
        try:
            # Get story progression to show appropriate intro
            guild_id = str(member.guild.id)
            progression = await self.db.get_story_progression(guild_id)
            current_act = progression.get('current_act', 1)
            
            # Create Act I intro embed (always show Act I for new members)
            embed = self.personality.create_act_intro_embed(1)
            
            # Add personal welcome
            embed.description = f"*Traveler... your signal reaches the Archive. {member.mention}, I detect your presence in the datasphere.*\n\n" + embed.description
            
            # Try to send DM first
            try:
                await member.send(embed=embed)
                logger.info(f"✅ Sent Act I intro DM to {member.name}")
            except discord.Forbidden:
                # If DM fails, try to send in discovery or general channel
                discovery_channel_id = os.getenv('DISCOVERY_CHANNEL_ID')
                if discovery_channel_id:
                    channel = self.get_channel(int(discovery_channel_id))
                    if channel:
                        await channel.send(f"Welcome {member.mention}!", embed=embed)
                        logger.info(f"✅ Sent Act I intro in channel for {member.name}")
                else:
                    # Fallback to first available channel
                    for channel in member.guild.text_channels:
                        if channel.permissions_for(member.guild.me).send_messages:
                            await channel.send(f"Welcome {member.mention}!", embed=embed)
                            logger.info(f"✅ Sent Act I intro in {channel.name} for {member.name}")
                            break
        except Exception as e:
            logger.error(f"Error in on_member_join: {e}")
            import traceback
            traceback.print_exc()
    
    async def on_application_command_error(self, interaction, error):
        """Handle application command errors."""
        logger.error(f"Command error: {error}")
        
        embed = discord.Embed(
            title="⚠️ Archive Corruption Detected",
            description="*The Keeper's systems have encountered an anomaly. The signal grows weak.*",
            color=self.config['theme']['embed_colors']['error']
        )
        embed.add_field(
            name="Technical Analysis",
            value=f"```\n{str(error)[:500]}\n```",
            inline=False
        )
        
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def close(self):
        """Clean shutdown."""
        logger.info("🌙 The Keeper enters dormancy...")

        # Stop sync API
        if self.sync_api:
            await self.sync_api.stop()
            logger.info("🌐 Sync API stopped")

        # Stop sync worker gracefully
        if self.sync_worker:
            await self.sync_worker.stop()
            logger.info("🛑 Sync worker stopped")

        if self.db:
            await self.db.close()
        await super().close()

async def main():
    """Main entry point."""
    bot = TheKeeper()
    
    token = os.getenv('BOT_TOKEN')
    if not token:
        logger.error("BOT_TOKEN not found in environment variables")
        logger.error("Please ensure BOT_TOKEN is set in your .env file")
        return
    
    try:
        await bot.start(token)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
    finally:
        await bot.close()

if __name__ == '__main__':
    asyncio.run(main())