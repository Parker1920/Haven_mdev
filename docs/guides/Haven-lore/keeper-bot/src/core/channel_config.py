"""
Centralized Channel Configuration
Provides consistent channel ID retrieval across all cogs.
Prioritizes database config, falls back to environment variables.
"""

import os
import logging
from typing import Optional
import discord

logger = logging.getLogger('keeper.channel_config')

class ChannelConfig:
    """Centralized channel configuration manager."""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    async def get_archive_channel(self, guild: discord.Guild) -> Optional[discord.TextChannel]:
        """
        Get the archive channel for a guild.
        Priority: Database config -> Environment variable
        """
        try:
            # Try database first
            config = await self.db.get_server_config(str(guild.id))
            if config and config.get('archive_channel_id'):
                channel = guild.get_channel(int(config['archive_channel_id']))
                if channel:
                    logger.debug(f"Archive channel from database: {channel.name}")
                    return channel
            
            # Fallback to environment variable
            archive_channel_id = os.getenv('ARCHIVE_CHANNEL_ID')
            if archive_channel_id:
                channel = guild.get_channel(int(archive_channel_id))
                if channel:
                    logger.debug(f"Archive channel from environment: {channel.name}")
                    return channel
            
            logger.warning(f"No archive channel configured for guild {guild.name}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting archive channel: {e}")
            return None
    
    async def get_investigation_channel(self, guild: discord.Guild) -> Optional[discord.TextChannel]:
        """
        Get the investigation channel for a guild.
        Priority: Database config -> Environment variable
        """
        try:
            # Try database first
            config = await self.db.get_server_config(str(guild.id))
            if config and config.get('investigation_channel_id'):
                channel = guild.get_channel(int(config['investigation_channel_id']))
                if channel:
                    logger.debug(f"Investigation channel from database: {channel.name}")
                    return channel
            
            # Fallback to environment variable
            investigation_channel_id = os.getenv('INVESTIGATION_CHANNEL_ID')
            if investigation_channel_id:
                channel = guild.get_channel(int(investigation_channel_id))
                if channel:
                    logger.debug(f"Investigation channel from environment: {channel.name}")
                    return channel
            
            logger.warning(f"No investigation channel configured for guild {guild.name}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting investigation channel: {e}")
            return None
    
    async def get_community_channel(self, guild: discord.Guild) -> Optional[discord.TextChannel]:
        """
        Get the community channel for a guild.
        Priority: Database config -> Environment variable
        """
        try:
            # Try database first
            config = await self.db.get_server_config(str(guild.id))
            if config and config.get('community_channel_id'):
                channel = guild.get_channel(int(config['community_channel_id']))
                if channel:
                    logger.debug(f"Community channel from database: {channel.name}")
                    return channel
            
            # Fallback to environment variable
            community_channel_id = os.getenv('COMMUNITY_CHANNEL_ID')
            if community_channel_id:
                channel = guild.get_channel(int(community_channel_id))
                if channel:
                    logger.debug(f"Community channel from environment: {channel.name}")
                    return channel
            
            logger.warning(f"No community channel configured for guild {guild.name}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting community channel: {e}")
            return None
    
    async def is_configured(self, guild: discord.Guild) -> bool:
        """Check if guild has at least archive channel configured."""
        archive = await self.get_archive_channel(guild)
        return archive is not None
