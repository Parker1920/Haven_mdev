"""
Enhanced Discovery System with Haven Integration
Allows users to select specific planets/locations from Haven star map data.
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Optional, List, Dict
import asyncio
import json

from core.keeper_personality import KeeperPersonality
from database.keeper_db import KeeperDatabase
from core.haven_integration import HavenIntegration
from core.channel_config import ChannelConfig

logger = logging.getLogger('keeper.enhanced_discovery')

class HavenSystemSelect(discord.ui.Select):
    """Dropdown for selecting a Haven star system."""
    
    def __init__(self, haven_systems: List[tuple], callback_handler):
        self.callback_handler = callback_handler
        
        options = []
        for i, (system_name, system_data) in enumerate(haven_systems[:25]):  # Discord limit
            region = system_data.get('region', 'Unknown Region')
            coords = f"({system_data.get('x', 0)}, {system_data.get('y', 0)}, {system_data.get('z', 0)})"
            
            options.append(discord.SelectOption(
                label=system_name,
                value=system_name,
                description=f"{region} • {coords}",
                emoji="🌟"
            ))
        
        super().__init__(
            placeholder="🗺️ Select Haven star system...",
            options=options,
            min_values=1,
            max_values=1
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle system selection."""
        selected_system = self.values[0]
        await self.callback_handler.handle_system_selection(interaction, selected_system)

class HavenLocationSelect(discord.ui.Select):
    """Dropdown for selecting specific location within a system."""
    
    def __init__(self, system_name: str, location_choices: List[Dict], callback_handler):
        self.system_name = system_name
        self.callback_handler = callback_handler
        
        options = []
        for choice in location_choices[:25]:  # Discord limit
            options.append(discord.SelectOption(
                label=choice['label'],
                value=choice['value'],
                description=choice['description'][:100]  # Discord limit
            ))
        
        super().__init__(
            placeholder=f"📍 Select location in {system_name}...",
            options=options,
            min_values=1,
            max_values=1
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle location selection."""
        selected_location = self.values[0]
        await self.callback_handler.handle_location_selection(interaction, self.system_name, selected_location)

class HavenDiscoveryModal(discord.ui.Modal, title="🌌 Discovery Report Archive"):
    """Enhanced modal with Haven integration."""
    
    def __init__(self, discovery_type: str, system_name: str, location_info: str, config: dict, haven_data: dict):
        super().__init__()
        self.discovery_type = discovery_type
        self.system_name = system_name
        self.location_info = location_info
        self.config = config
        self.haven_data = haven_data
        
        # Parse location info
        self.location_type, self.location_name = self._parse_location_info(location_info)
        
        # Update modal title
        location_display = self.location_name if self.location_name else "Unknown Location"
        self.title = f"{discovery_type} Discovery - {location_display}"
    
    def _parse_location_info(self, location_info: str) -> tuple:
        """Parse location info string into type and name."""
        parts = location_info.split(':', 2)
        if len(parts) >= 2:
            return parts[0], parts[1] if len(parts) == 2 else parts[2]
        return "unknown", location_info
    
    description = discord.ui.TextInput(
        label="📝 Discovery Description",
        placeholder="Describe what you found. Include direct NMS text if applicable.",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )
    
    coordinates = discord.ui.TextInput(
        label="📍 Specific Coordinates (Optional)",
        placeholder="Portal coordinates, base coordinates, or landmark reference",
        max_length=200,
        required=False
    )
    
    condition = discord.ui.TextInput(
        label="⚡ Condition/Signal Strength",
        placeholder="Well-Preserved / Damaged / Fragmented / Mysterious",
        max_length=100,
        required=False,
        default="Unknown"
    )
    
    time_period = discord.ui.TextInput(
        label="⏰ Time Period",
        placeholder="Ancient / Recent / Unknown / Specific Era",
        max_length=100,
        required=False,
        default="Unknown"
    )
    
    significance = discord.ui.TextInput(
        label="🔮 Your Analysis & Theory",
        placeholder="What do you think it means? Any connections to other discoveries?",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle form submission."""
        await interaction.response.defer()
        
        # Get the bot instance and process the discovery
        bot = interaction.client
        cog = bot.get_cog('EnhancedDiscoverySystem')
        if cog:
            discovery_data = {
                'type': self.discovery_type,
                'system_name': self.system_name,
                'location_type': self.location_type,
                'location_name': self.location_name,
                'location_info': self.location_info,
                'description': self.description.value,
                'coordinates': self.coordinates.value,
                'condition': self.condition.value,
                'time_period': self.time_period.value,
                'significance': self.significance.value,
                'haven_data': self.haven_data
            }
            await cog.process_discovery_submission(interaction, discovery_data)

class DiscoveryFlowHandler:
    """Handles the multi-step discovery flow."""
    
    def __init__(self, cog, config):
        self.cog = cog
        self.config = config
        self.haven = cog.haven
    
    async def handle_system_selection(self, interaction: discord.Interaction, system_name: str):
        """Handle when user selects a star system."""
        await interaction.response.defer()
        
        # Get location choices for this system
        location_choices = self.haven.create_discovery_location_choices(system_name)
        
        if not location_choices:
            # No locations found - suggest system might need more data
            embed = discord.Embed(
                title="🔍 System Analysis Required",
                description=f"*The Keeper detects sparse data for {system_name}. This system may need detailed exploration.*",
                color=self.config['theme']['embed_colors']['warning']
            )
            embed.add_field(
                name="Suggested Action",
                value="Consider updating the Haven star map with detailed planet information for this system.",
                inline=False
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Show location selection
        embed = discord.Embed(
            title=f"🗺️ {system_name} - Location Selection",
            description="*Select the specific location where your discovery was made.*",
            color=self.config['theme']['embed_colors']['discovery']
        )
        
        # Add system info if available
        system_data = self.haven.get_system(system_name)
        if system_data:
            region = system_data.get('region', 'Unknown')
            coords = f"({system_data.get('x', 0)}, {system_data.get('y', 0)}, {system_data.get('z', 0)})"
            embed.add_field(name="📍 System Info", value=f"**Region:** {region}\n**Coordinates:** {coords}", inline=False)
        
        view = discord.ui.View(timeout=300)
        view.add_item(HavenLocationSelect(system_name, location_choices, self))
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    
    async def handle_location_selection(self, interaction: discord.Interaction, system_name: str, location_info: str):
        """Handle when user selects a specific location."""
        # This is where we determine the discovery type
        # For now, we'll use a simple type selector
        # In Phase 3, this could be enhanced with context-aware suggestions
        
        embed = discord.Embed(
            title="🔍 Discovery Type Selection",
            description=f"*Location confirmed: {location_info.split(':')[-1]} in {system_name}*\n\nWhat type of discovery did you make?",
            color=self.config['theme']['embed_colors']['discovery']
        )
        
        view = discord.ui.View(timeout=300)
        view.add_item(DiscoveryTypeSelect(self.config, system_name, location_info))
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class DiscoveryTypeSelect(discord.ui.Select):
    """Dropdown for selecting discovery type with Haven context."""
    
    def __init__(self, config: dict, system_name: str, location_info: str):
        self.config = config
        self.system_name = system_name
        self.location_info = location_info
        discovery_types = config['discovery_types']
        
        options = []
        for emoji, name in discovery_types.items():
            options.append(discord.SelectOption(
                label=name,
                emoji=emoji,
                value=emoji,
                description=f"Report {name.lower()} discoveries"
            ))
        
        super().__init__(
            placeholder="🔍 Choose discovery type...",
            options=options,
            min_values=1,
            max_values=1
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle discovery type selection."""
        discovery_type = self.values[0]
        discovery_name = self.config['discovery_types'][discovery_type]
        
        # Get Haven system data for context
        bot = interaction.client
        cog = bot.get_cog('EnhancedDiscoverySystem')
        haven_data = cog.haven.get_system(self.system_name)
        
        # Show the discovery modal
        modal = HavenDiscoveryModal(discovery_type, self.system_name, self.location_info, self.config, haven_data)
        await interaction.response.send_modal(modal)

class PhotoUploadView(discord.ui.View):
    """View for handling photo uploads."""
    
    def __init__(self, discovery_id: int):
        super().__init__(timeout=300)
        self.discovery_id = discovery_id
    
    @discord.ui.button(label="📸 Upload Evidence Photo", style=discord.ButtonStyle.secondary)
    async def upload_photo(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle photo upload."""
        embed = discord.Embed(
            title="📸 Evidence Upload",
            description="Please attach an image to your next message in this channel.\n\n*The Keeper will process and archive the evidence.*",
            color=0x00d9ff
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class EnhancedDiscoverySystem(commands.Cog):
    """Enhanced discovery system with Haven integration."""
    
    def __init__(self, bot):
        self.bot = bot
        self.db: KeeperDatabase = bot.db
        self.personality: KeeperPersonality = bot.personality
        self.config = bot.config
        self.haven = HavenIntegration()
        self.flow_handler = DiscoveryFlowHandler(self, bot.config)
        self.channel_config = ChannelConfig(bot)
        
        # Start Haven data loading
        self.bot.loop.create_task(self._initialize_haven())
    
    async def _initialize_haven(self):
        """Initialize Haven integration."""
        success = await self.haven.load_haven_data()
        if success:
            logger.info("✅ Haven integration initialized")
        else:
            logger.warning("⚠️ Haven integration failed - bot will work in standalone mode")
    
    @app_commands.command(
        name="discovery-report",
        description="🔍 Report a discovery to The Keeper's Archive (Haven-Enhanced)"
    )
    async def discovery_report(self, interaction: discord.Interaction):
        """Main command to start discovery reporting with Haven integration."""
        
        await interaction.response.defer()
        
        # Check if Haven data is available
        haven_systems = self.haven.get_all_systems()
        
        if not haven_systems:
            # Fallback to original discovery system
            embed = discord.Embed(
                title="🌌 Discovery Report Interface",
                description="*The Keeper awakens, ready to receive your findings...*\n\n⚠️ Haven star map integration unavailable - using standalone mode.",
                color=self.config['theme']['embed_colors']['warning']
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Show system selection
        embed = discord.Embed(
            title="🗺️ Haven Star Map Integration",
            description=f"*The Keeper interfaces with the Haven star charts. {len(haven_systems)} systems available for exploration.*",
            color=self.config['theme']['embed_colors']['discovery']
        )
        
        embed.add_field(
            name="📋 Discovery Process",
            value="1. Select your star system from Haven charts\n2. Choose specific planet/location\n3. Report your discovery details",
            inline=False
        )
        
        embed.add_field(
            name="🔄 Data Integration", 
            value="Your discoveries will be archived by The Keeper and can be exported to enhance the Haven star map.",
            inline=False
        )
        
        # Create system selection dropdown
        system_list = list(haven_systems.items())[:25]  # Discord limit
        view = discord.ui.View(timeout=300)
        view.add_item(HavenSystemSelect(system_list, self.flow_handler))
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    
    async def process_discovery_submission(self, interaction: discord.Interaction, discovery_data: dict):
        """Process a completed discovery submission with Haven integration."""
        try:
            # Enhance discovery data with Haven context
            enhanced_data = {
                'user_id': str(interaction.user.id),
                'username': interaction.user.display_name,
                'submission_timestamp': discord.utils.utcnow(),
                'guild_id': str(interaction.guild.id) if interaction.guild else None,
                # Map fields correctly for database
                'type': discovery_data.get('type'),  # Discovery type emoji
                'location': discovery_data.get('location_name', 'Unknown'),  # Planet/location name
                'system_name': discovery_data.get('system_name'),  # Star system name
                'planet_name': discovery_data.get('location_name'),  # Also set planet_name
                'description': discovery_data.get('description'),
                'coordinates': discovery_data.get('coordinates', '[]'),
                'condition': discovery_data.get('condition'),
                'time_period': discovery_data.get('time_period'),
                'significance': discovery_data.get('significance'),
                'evidence_url': discovery_data.get('evidence_url', ''),
                'haven_data': discovery_data.get('haven_data'),
                'location_type': discovery_data.get('location_type'),
                'location_info': discovery_data.get('location_info')
            }
            
            # Save to keeper database
            discovery_id = await self.db.add_discovery(enhanced_data)
            enhanced_data['id'] = discovery_id

            # Also write to Haven VH-Database if enabled
            try:
                haven_discovery_id = self.haven.write_discovery_to_database(enhanced_data)
                if haven_discovery_id:
                    logger.info(f"Discovery also saved to Haven database with ID {haven_discovery_id}")
            except Exception as e:
                logger.warning(f"Could not write to Haven database: {e}")
                # Continue execution - keeper.db save was successful

            # Update story progression - increment discovery count
            guild_id = str(interaction.guild.id)
            await self.db.increment_story_stats(guild_id, 'discoveries', 1)
            
            # Check for automatic act transitions
            await self._check_story_progression(interaction.guild)
            
            # Create Keeper analysis response
            analysis_embed = self.personality.create_discovery_analysis(enhanced_data)
            
            # Add Haven context to the analysis
            if discovery_data.get('haven_data'):
                haven_system = discovery_data['haven_data']
                region_info = f"**Galactic Region:** {haven_system.get('region', 'Unknown')}\n"
                coord_info = f"**System Coordinates:** ({haven_system.get('x', 0)}, {haven_system.get('y', 0)}, {haven_system.get('z', 0)})\n"
                
                analysis_embed.add_field(
                    name="🗺️ Haven Chart Reference",
                    value=region_info + coord_info + f"**Location:** {enhanced_data.get('location_name', 'Unknown')}",
                    inline=False
                )
            
            # Send confirmation to user (enhanced with master file template)
            confirm_embed = discord.Embed(
                title="✅ Discovery Archived",
                description=f"*Your discovery has been processed and added to the Archive as Entry #{discovery_id}*\n\n"
                           f"The Keeper has analyzed your submission. Correlation with existing patterns: [checking...]",
                color=self.config['theme']['embed_colors']['success']
            )
            
            confirm_embed.add_field(
                name="📤 Export Available",
                value="This discovery can be exported to enhance your Haven star map data.",
                inline=False
            )
            
            # Add photo upload option
            photo_view = PhotoUploadView(discovery_id)
            await interaction.followup.send(embed=confirm_embed, view=photo_view, ephemeral=True)
            
            # Post analysis to archive channel
            await self.post_to_archive_channel(interaction.guild, analysis_embed, discovery_id)
            
            # Check for patterns (Phase 2 functionality)
            if hasattr(self.bot, 'get_cog') and self.bot.get_cog('PatternRecognition'):
                pattern_cog = self.bot.get_cog('PatternRecognition')
                await pattern_cog.analyze_for_patterns(discovery_id)
            
            logger.info(f"Haven-integrated discovery {discovery_id} processed for user {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error processing Haven discovery: {e}")
            error_embed = discord.Embed(
                title="❌ Archive Error",
                description="*The Keeper's systems experienced a disruption. Please try again.*",
                color=self.config['theme']['embed_colors']['error']
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
    
    async def post_to_archive_channel(self, guild: discord.Guild, embed: discord.Embed, discovery_id: int):
        """Post the analysis to the configured archive channel."""
        try:
            # Get archive channel using centralized config
            archive_channel = await self.channel_config.get_archive_channel(guild)
            if not archive_channel:
                logger.warning(f"No archive channel configured for guild {guild.id}")
                return
            
            # Post the analysis
            message = await archive_channel.send(embed=embed)
            
            # Save archive entry reference
            await self.db.connection.execute("""
                INSERT INTO archive_entries (
                    entry_id, discovery_id, entry_type, title, content,
                    channel_id, message_id, embed_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"HAVEN_DISC_{discovery_id:06d}",
                discovery_id,
                "haven_discovery_analysis",
                embed.title,
                embed.description,
                str(archive_channel.id),
                str(message.id),
                json.dumps(embed.to_dict())  # Convert dict to JSON string
            ))
            await self.db.connection.commit()
            
            logger.info(f"Haven discovery {discovery_id} posted to archive channel")
            
        except Exception as e:
            logger.error(f"Error posting to archive channel: {e}")
    
    @app_commands.command(
        name="haven-export",
        description="📤 Export discoveries for Haven star map integration"
    )
    async def export_to_haven(self, interaction: discord.Interaction, 
                            system_name: Optional[str] = None):
        """Export discoveries in Haven-compatible format."""
        await interaction.response.defer()
        
        try:
            # Get discoveries to export
            if system_name:
                discoveries = await self.db.search_discoveries(location=system_name, limit=100)
            else:
                discoveries = await self.db.search_discoveries(limit=100)
            
            if not discoveries:
                embed = discord.Embed(
                    title="📤 Export Status",
                    description="*No discoveries found for export.*",
                    color=self.config['theme']['embed_colors']['warning']
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create backup and export
            backup_path = self.haven.backup_keeper_discoveries(discoveries)
            
            embed = discord.Embed(
                title="📤 Haven Export Complete",
                description=f"*{len(discoveries)} discoveries have been prepared for Haven integration.*",
                color=self.config['theme']['embed_colors']['success']
            )
            
            embed.add_field(
                name="📁 Export File",
                value=f"`{backup_path}`",
                inline=False
            )
            
            embed.add_field(
                name="🔄 Integration Instructions",
                value="Use this file to enhance your Haven star map with discovered lore and details.",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in Haven export: {e}")
            error_embed = discord.Embed(
                title="❌ Export Error",
                description="*Export process encountered an error.*",
                color=self.config['theme']['embed_colors']['error']
            )
            await interaction.followup.send(embed=error_embed)
    
    async def _check_story_progression(self, guild):
        """Check if community has reached act transition milestones."""
        try:
            guild_id = str(guild.id)
            progression = await self.db.get_story_progression(guild_id)
            
            current_act = progression.get('current_act', 1)
            discoveries = progression.get('total_discoveries', 0)
            patterns = progression.get('total_patterns', 0)
            
            # Act I → Act II: First pattern detected
            if current_act == 1 and patterns >= 1 and not progression.get('act_1_complete'):
                await self.db.complete_act(guild_id, 1)
                await self._announce_act_transition(guild, 2)
                logger.info(f"🎭 Guild {guild_id} transitioned to Act II!")
            
            # Act II → Act III: 3+ patterns AND 30+ discoveries
            elif current_act == 2 and patterns >= 3 and discoveries >= 30 and not progression.get('act_2_complete'):
                await self.db.complete_act(guild_id, 2)
                await self._announce_act_transition(guild, 3)
                logger.info(f"🎭 Guild {guild_id} transitioned to Act III!")
        
        except Exception as e:
            logger.error(f"Error checking story progression: {e}")
    
    async def _announce_act_transition(self, guild, new_act: int):
        """Announce act transition in archive channel."""
        try:
            # Get archive channel using centralized config
            channel = await self.channel_config.get_archive_channel(guild)
            if not channel:
                logger.warning(f"No archive channel configured for act transition announcement")
                return
            
            # Create transition announcement
            embed = self.personality.create_act_intro_embed(new_act)
            
            # Add celebration message
            embed.description = f"🎭 **ACT TRANSITION ACHIEVED!** 🎭\n\n" + embed.description
            
            embed.add_field(
                name="🌟 Community Achievement",
                value="Your collective discoveries and pattern recognition have unlocked the next chapter of The Keeper's story!",
                inline=False
            )
            
            await channel.send("@everyone", embed=embed)
            logger.info(f"📢 Announced Act {new_act} transition in {guild.name}")
            
        except Exception as e:
            logger.error(f"Error announcing act transition: {e}")

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(EnhancedDiscoverySystem(bot))