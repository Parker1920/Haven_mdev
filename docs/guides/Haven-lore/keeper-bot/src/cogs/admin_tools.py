"""
Admin Tools - Phase 3/4
Bot administration, configuration tools, and community management.
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Dict, List, Optional
import json
import asyncio
from datetime import datetime, timedelta

from core.keeper_personality import KeeperPersonality
from database.keeper_db import KeeperDatabase
from core.haven_integration import HavenIntegration

logger = logging.getLogger('keeper.admin')

class ChannelSetupModal(discord.ui.Modal, title="🔧 Channel Configuration"):
    """Modal for setting up bot channels."""
    
    def __init__(self):
        super().__init__()
    
    discovery_channel = discord.ui.TextInput(
        label="📝 Discovery Reports Channel",
        placeholder="#discovery-reports (or channel ID)",
        max_length=100,
        required=True
    )
    
    archive_channel = discord.ui.TextInput(
        label="📊 Keeper Archive Channel", 
        placeholder="#keeper-archive (or channel ID)",
        max_length=100,
        required=True
    )
    
    investigation_channel = discord.ui.TextInput(
        label="🔍 Investigation Threads Channel",
        placeholder="#investigation-threads (or channel ID)",
        max_length=100,
        required=False
    )
    
    lore_channel = discord.ui.TextInput(
        label="💬 Lore Discussion Channel",
        placeholder="#lore-discussion (or channel ID)",
        max_length=100,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Process channel setup."""
        bot = interaction.client
        cog = bot.get_cog('AdminTools')
        if cog:
            channel_config = {
                'discovery_channel': self.discovery_channel.value,
                'archive_channel': self.archive_channel.value,
                'investigation_channel': self.investigation_channel.value,
                'lore_channel': self.lore_channel.value
            }
            await cog.process_channel_setup(interaction, channel_config)

class ServerStatsView(discord.ui.View):
    """View for server statistics and management."""
    
    def __init__(self, stats: Dict, config: dict):
        super().__init__(timeout=300)
        self.stats = stats
        self.config = config
    
    @discord.ui.button(label="📊 Detailed Stats", style=discord.ButtonStyle.primary)
    async def detailed_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show detailed server statistics."""
        embed = discord.Embed(
            title="📊 Detailed Server Statistics", 
            description="*Complete breakdown of archive activity*",
            color=self.config['theme']['embed_colors']['archive']
        )
        
        # Discovery statistics
        discovery_stats = self.stats.get('discoveries', {})
        embed.add_field(
            name="🔍 Discovery Statistics",
            value=f"**Total Discoveries:** {discovery_stats.get('total', 0)}\n**This Week:** {discovery_stats.get('week', 0)}\n**This Month:** {discovery_stats.get('month', 0)}",
            inline=True
        )
        
        # Pattern statistics
        pattern_stats = self.stats.get('patterns', {})
        embed.add_field(
            name="🌀 Pattern Statistics",
            value=f"**Active Patterns:** {pattern_stats.get('active', 0)}\n**Total Patterns:** {pattern_stats.get('total', 0)}\n**Avg Confidence:** {pattern_stats.get('avg_confidence', 0):.1%}",
            inline=True
        )
        
        # User statistics
        user_stats = self.stats.get('users', {})
        embed.add_field(
            name="👥 Explorer Statistics",
            value=f"**Active Explorers:** {user_stats.get('active', 0)}\n**Total Participants:** {user_stats.get('total', 0)}\n**Top Contributor:** {user_stats.get('top_explorer', 'None')}",
            inline=True
        )
        
        # Mystery tier breakdown
        tier_stats = self.stats.get('tiers', {})
        tier_breakdown = "\n".join([f"**Tier {tier}:** {count}" for tier, count in tier_stats.items()])
        if tier_breakdown:
            embed.add_field(
                name="🎯 Mystery Tier Distribution",
                value=tier_breakdown,
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📈 Export Data", style=discord.ButtonStyle.secondary)
    async def export_data(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Export server data."""
        await interaction.response.send_message("📤 Data export initiated... This may take a moment.", ephemeral=True)
        
        # This would trigger a data export process
        bot = interaction.client
        cog = bot.get_cog('AdminTools')
        if cog:
            await cog.export_server_data(interaction)
    
    @discord.ui.button(label="🔄 Refresh Stats", style=discord.ButtonStyle.secondary)
    async def refresh_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Refresh statistics."""
        await interaction.response.send_message("🔄 Refreshing statistics...", ephemeral=True)

class AdminTools(commands.Cog):
    """Admin tools and server management."""
    
    def __init__(self, bot):
        self.bot = bot
        self.db: KeeperDatabase = bot.db
        self.personality: KeeperPersonality = bot.personality
        self.config = bot.config
        self.haven = HavenIntegration()
        logger.info("Admin Tools Phase 3 loaded")
    
    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Handle admin command errors."""
        if isinstance(error, app_commands.MissingPermissions):
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="*The Keeper's administrative functions require proper authorization.*",
                color=self.config['theme']['embed_colors']['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            logger.error(f"Admin command error: {error}")
    
    @app_commands.command(
        name="setup-channels",
        description="🔧 Configure The Keeper's channels"
    )
    @app_commands.default_permissions(administrator=True)
    async def setup_channels(self, interaction: discord.Interaction):
        """Setup bot channels configuration."""
        modal = ChannelSetupModal()
        await interaction.response.send_modal(modal)
    
    async def process_channel_setup(self, interaction: discord.Interaction, channel_config: Dict):
        """Process channel configuration."""
        await interaction.response.defer()
        
        try:
            guild_id = str(interaction.guild.id)
            resolved_channels = {}
            
            # Resolve channel mentions/IDs to actual channel IDs
            for key, value in channel_config.items():
                if not value:
                    continue
                
                # Try to parse channel mention or ID
                channel = None
                if value.startswith('<#') and value.endswith('>'):
                    # Channel mention
                    channel_id = value[2:-1]
                    channel = interaction.guild.get_channel(int(channel_id))
                elif value.startswith('#'):
                    # Channel name
                    channel_name = value[1:]
                    channel = discord.utils.get(interaction.guild.channels, name=channel_name)
                elif value.isdigit():
                    # Channel ID
                    channel = interaction.guild.get_channel(int(value))
                
                if channel:
                    resolved_channels[key.replace('_channel', '_channel_id')] = str(channel.id)
            
            # Update server configuration
            await self.db.update_server_config(guild_id, resolved_channels)
            
            # Create confirmation embed
            embed = discord.Embed(
                title="✅ Channel Configuration Complete",
                description="*The Keeper's neural pathways have been established.*",
                color=self.config['theme']['embed_colors']['success']
            )
            
            for key, channel_id in resolved_channels.items():
                channel = interaction.guild.get_channel(int(channel_id))
                if channel:
                    field_name = key.replace('_channel_id', '').replace('_', ' ').title()
                    embed.add_field(name=field_name, value=channel.mention, inline=True)
            
            embed.add_field(
                name="🎯 Next Steps",
                value="The Keeper is now configured. Users can begin reporting discoveries with `/discovery-report`.",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in channel setup: {e}")
            error_embed = discord.Embed(
                title="❌ Configuration Error",
                description="Failed to configure channels. Please check channel names/IDs and try again.",
                color=self.config['theme']['embed_colors']['error']
            )
            await interaction.followup.send(embed=error_embed)
    
    @app_commands.command(
        name="server-stats",
        description="📊 View server statistics and activity"
    )
    @app_commands.default_permissions(administrator=True)
    async def server_stats(self, interaction: discord.Interaction):
        """Display server statistics."""
        await interaction.response.defer()
        
        try:
            stats = await self._gather_server_stats(str(interaction.guild.id))
            
            embed = discord.Embed(
                title="📊 Server Statistics",
                description="*The Keeper's archive analytics*",
                color=self.config['theme']['embed_colors']['archive']
            )
            
            # Basic stats
            embed.add_field(
                name="🔍 Discoveries",
                value=f"**Total:** {stats['discoveries']['total']}\n**This Week:** {stats['discoveries']['week']}",
                inline=True
            )

            embed.add_field(
                name="🌀 Patterns",
                value=f"**Active:** {stats['patterns']['active']}\n**Total:** {stats['patterns']['total']}",
                inline=True
            )

            embed.add_field(
                name="👥 Explorers",
                value=f"**Active:** {stats['users']['active']}\n**Total:** {stats['users']['total']}",
                inline=True
            )

            # Recent activity
            if stats['recent_activity']:
                activity_text = "\n".join(stats['recent_activity'][:5])
                embed.add_field(
                    name="📈 Recent Activity",
                    value=activity_text,
                    inline=False
                )
            
            view = ServerStatsView(stats, self.config)
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error gathering server stats: {e}")
            error_embed = discord.Embed(
                title="❌ Statistics Error",
                description="Unable to gather server statistics.",
                color=self.config['theme']['embed_colors']['error']
            )
            await interaction.followup.send(embed=error_embed)
    
    async def _gather_server_stats(self, guild_id: str) -> Dict:
        """Gather comprehensive server statistics."""
        stats = {
            'discoveries': {'total': 0, 'week': 0, 'month': 0},
            'patterns': {'total': 0, 'active': 0, 'avg_confidence': 0},
            'users': {'total': 0, 'active': 0, 'top_explorer': 'None'},
            'tiers': {},
            'recent_activity': []
        }

        try:
            # Use Haven integration to get master database path
            import sqlite3
            import os
            haven_db_path = os.getenv('HAVEN_DB_PATH')

            if not haven_db_path or not os.path.exists(haven_db_path):
                logger.error("Haven database not found at HAVEN_DB_PATH")
                return stats

            # Connect to VH-Database.db (master database)
            conn = sqlite3.connect(haven_db_path)
            cursor = conn.cursor()

            # Discovery stats - total
            cursor.execute("SELECT COUNT(*) FROM discoveries WHERE discord_guild_id = ?", (guild_id,))
            stats['discoveries']['total'] = cursor.fetchone()[0]

            # Weekly discoveries
            week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
            cursor.execute(
                "SELECT COUNT(*) FROM discoveries WHERE discord_guild_id = ? AND submission_timestamp >= ?",
                (guild_id, week_ago)
            )
            stats['discoveries']['week'] = cursor.fetchone()[0]
            
            # Pattern stats
            cursor = await self.db.connection.execute("SELECT COUNT(*), AVG(confidence_level) FROM patterns")
            result = await cursor.fetchone()
            stats['patterns']['total'] = result[0] or 0
            stats['patterns']['avg_confidence'] = result[1] or 0
            
            # Active patterns
            cursor = await self.db.connection.execute(
                "SELECT COUNT(*) FROM patterns WHERE status = 'active' OR status = 'emerging'"
            )
            stats['patterns']['active'] = (await cursor.fetchone())[0]
            
            # User stats
            cursor = await self.db.connection.execute("SELECT COUNT(DISTINCT user_id) FROM discoveries WHERE guild_id = ?", (guild_id,))
            stats['users']['total'] = (await cursor.fetchone())[0]
            
            # Active users (last 30 days)
            month_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
            cursor = await self.db.connection.execute(
                "SELECT COUNT(DISTINCT user_id) FROM discoveries WHERE guild_id = ? AND submission_timestamp >= ?",
                (guild_id, month_ago)
            )
            stats['users']['active'] = (await cursor.fetchone())[0]
            
            # Top explorer
            cursor = await self.db.connection.execute("""
                SELECT username, COUNT(*) as count FROM discoveries 
                WHERE guild_id = ? GROUP BY user_id ORDER BY count DESC LIMIT 1
            """, (guild_id,))
            result = await cursor.fetchone()
            if result:
                stats['users']['top_explorer'] = f"{result[0]} ({result[1]} discoveries)"
            
            # Mystery tier distribution
            for tier in range(1, 5):
                cursor = await self.db.connection.execute(
                    "SELECT COUNT(*) FROM patterns WHERE mystery_tier = ?", (tier,)
                )
                count = (await cursor.fetchone())[0]
                if count > 0:
                    stats['tiers'][tier] = count
            
            # Recent activity
            cursor = await self.db.connection.execute("""
                SELECT discovery_type, username, submission_timestamp FROM discoveries
                WHERE guild_id = ? ORDER BY submission_timestamp DESC LIMIT 5
            """, (guild_id,))
            
            rows = await cursor.fetchall()
            for row in rows:
                discovery_type, username, timestamp = row
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime('%m/%d %H:%M')
                else:
                    time_str = timestamp.strftime('%m/%d %H:%M')
                
                stats['recent_activity'].append(f"{discovery_type} discovery by {username} ({time_str})")
            
        except Exception as e:
            logger.error(f"Error gathering stats: {e}")
        
        return stats
    
    async def export_server_data(self, interaction: discord.Interaction):
        """Export server data for backup/analysis."""
        try:
            guild_id = str(interaction.guild.id)
            
            # Gather all server data
            discoveries = await self.db.search_discoveries(limit=1000)  # Large limit
            patterns_data = []
            for tier in range(1, 5):
                tier_patterns = await self.db.get_patterns_by_tier(tier)
                patterns_data.extend(tier_patterns)
            
            # Create export data
            export_data = {
                'export_info': {
                    'timestamp': datetime.utcnow().isoformat(),
                    'guild_id': guild_id,
                    'guild_name': interaction.guild.name,
                    'bot_version': 'The Keeper v2.0'
                },
                'discoveries': discoveries,
                'patterns': patterns_data,
                'summary': {
                    'total_discoveries': len(discoveries),
                    'total_patterns': len(patterns_data),
                    'export_size': f"{len(json.dumps(discoveries)) + len(json.dumps(patterns_data))} bytes"
                }
            }
            
            # Create backup file
            backup_filename = f"keeper_export_{guild_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            backup_path = f"./data/{backup_filename}"
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            # Send confirmation
            embed = discord.Embed(
                title="📤 Data Export Complete",
                description="*Server data has been exported and archived.*",
                color=self.config['theme']['embed_colors']['success']
            )
            
            embed.add_field(
                name="📊 Export Summary",
                value=f"**Discoveries:** {len(discoveries)}\\n**Patterns:** {len(patterns_data)}\\n**File:** `{backup_filename}`",
                inline=False
            )
            
            embed.add_field(
                name="💾 Backup Location",
                value=f"`{backup_path}`\\n*File can be used for data recovery or analysis.*",
                inline=False
            )
            
            await interaction.edit_original_response(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in data export: {e}")
            error_embed = discord.Embed(
                title="❌ Export Error",
                description="Data export failed. Check logs for details.",
                color=self.config['theme']['embed_colors']['error']
            )
            await interaction.edit_original_response(embed=error_embed)
    
    @app_commands.command(
        name="keeper-config",
        description="⚙️ Configure The Keeper's settings"
    )
    @app_commands.describe(
        pattern_threshold="Minimum discoveries required for pattern detection (default: 3)",
        auto_pattern="Enable automatic pattern detection (default: true)"
    )
    @app_commands.default_permissions(administrator=True)
    async def keeper_config(
        self,
        interaction: discord.Interaction,
        pattern_threshold: Optional[int] = None,
        auto_pattern: Optional[bool] = None
    ):
        """Configure bot settings."""
        await interaction.response.defer()
        
        try:
            guild_id = str(interaction.guild.id)
            config_updates = {}
            
            if pattern_threshold is not None:
                if 1 <= pattern_threshold <= 50:
                    config_updates['pattern_threshold'] = pattern_threshold
                else:
                    await interaction.followup.send("❌ Pattern threshold must be between 1 and 50.")
                    return
            
            if auto_pattern is not None:
                config_updates['auto_pattern_enabled'] = auto_pattern
            
            if config_updates:
                await self.db.update_server_config(guild_id, config_updates)
                
                embed = discord.Embed(
                    title="⚙️ Configuration Updated",
                    description="*The Keeper's parameters have been adjusted.*",
                    color=self.config['theme']['embed_colors']['success']
                )
                
                for key, value in config_updates.items():
                    field_name = key.replace('_', ' ').title()
                    embed.add_field(name=field_name, value=str(value), inline=True)
                
                await interaction.followup.send(embed=embed)
            else:
                # Show current configuration
                server_config = await self.db.get_server_config(guild_id)
                
                embed = discord.Embed(
                    title="⚙️ Current Configuration",
                    description="*The Keeper's current parameters*",
                    color=self.config['theme']['embed_colors']['archive']
                )
                
                if server_config:
                    embed.add_field(
                        name="Pattern Detection",
                        value=f"**Threshold:** {server_config.get('pattern_threshold', 3)}\\n**Auto-detect:** {'Enabled' if server_config.get('auto_pattern_enabled', True) else 'Disabled'}",
                        inline=True
                    )
                
                await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error in keeper config: {e}")
            error_embed = discord.Embed(
                title="❌ Configuration Error",
                description="Failed to update configuration.",
                color=self.config['theme']['embed_colors']['error']
            )
            await interaction.followup.send(embed=error_embed)

    @app_commands.command(name="reload-haven", description="Reload Haven star systems from database")
    @app_commands.default_permissions(administrator=True)
    async def reload_haven(self, interaction: discord.Interaction):
        """Reload Haven star systems from VH-Database.db"""
        await interaction.response.defer(ephemeral=True)

        try:
            # Get all cogs that have Haven integration
            cogs_with_haven = []

            # Check enhanced_discovery cog
            enhanced_discovery = self.bot.get_cog('EnhancedDiscoverySystem')
            if enhanced_discovery and hasattr(enhanced_discovery, 'haven'):
                cogs_with_haven.append(('EnhancedDiscoverySystem', enhanced_discovery.haven))

            # Check pattern_recognition cog
            pattern_recognition = self.bot.get_cog('PatternRecognition')
            if pattern_recognition and hasattr(pattern_recognition, 'haven'):
                cogs_with_haven.append(('PatternRecognition', pattern_recognition.haven))

            # Check archive_system cog
            archive_system = self.bot.get_cog('ArchiveSystem')
            if archive_system and hasattr(archive_system, 'haven'):
                cogs_with_haven.append(('ArchiveSystem', archive_system.haven))

            # Check community_features cog
            community_features = self.bot.get_cog('CommunityFeatures')
            if community_features and hasattr(community_features, 'haven'):
                cogs_with_haven.append(('CommunityFeatures', community_features.haven))

            if not cogs_with_haven:
                error_embed = discord.Embed(
                    title="❌ No Haven Integration",
                    description="No cogs with Haven integration found.",
                    color=self.config['theme']['embed_colors']['error']
                )
                await interaction.followup.send(embed=error_embed)
                return

            # Reload Haven data for each cog
            reload_results = []
            for cog_name, haven_instance in cogs_with_haven:
                success = await haven_instance.load_haven_data()
                system_count = len(haven_instance.get_all_systems())
                reload_results.append((cog_name, success, system_count))

            # Build result embed
            if all(result[1] for result in reload_results):
                # All successful
                total_systems = reload_results[0][2] if reload_results else 0

                embed = discord.Embed(
                    title="✅ Haven Data Reloaded",
                    description=f"Successfully reloaded Haven star systems from database.",
                    color=self.config['theme']['embed_colors']['success']
                )
                embed.add_field(
                    name="📊 Systems Loaded",
                    value=f"{total_systems} star system(s)",
                    inline=False
                )
                embed.add_field(
                    name="🔄 Cogs Updated",
                    value="\n".join([f"✅ {name}" for name, _, _ in reload_results]),
                    inline=False
                )

                logger.info(f"Admin {interaction.user} reloaded Haven data: {total_systems} systems")
            else:
                # Some failed
                embed = discord.Embed(
                    title="⚠️ Haven Reload Partial",
                    description="Some cogs failed to reload Haven data.",
                    color=self.config['theme']['embed_colors']['warning']
                )
                for name, success, count in reload_results:
                    status = "✅" if success else "❌"
                    embed.add_field(
                        name=f"{status} {name}",
                        value=f"{count} systems" if success else "Failed to load",
                        inline=False
                    )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error reloading Haven data: {e}")
            error_embed = discord.Embed(
                title="❌ Reload Error",
                description=f"Failed to reload Haven data: {str(e)}",
                color=self.config['theme']['embed_colors']['error']
            )
            await interaction.followup.send(embed=error_embed)

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(AdminTools(bot))