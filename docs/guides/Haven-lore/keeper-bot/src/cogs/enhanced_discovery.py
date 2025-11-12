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
from cogs.discovery_modals import get_modal_for_type

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
        import logging
        logger = logging.getLogger('keeper.enhanced_discovery')
        logger.info(f"HavenLocationSelect.callback: selected_location='{selected_location}' for system '{self.system_name}'")
        await self.callback_handler.handle_location_selection(interaction, self.system_name, selected_location)

# DEPRECATED: Generic modal replaced with type-specific modals in discovery_modals.py
# See: cogs/discovery_modals.py for 10 custom modal classes with relevant fields for each discovery type

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
        import logging
        logger = logging.getLogger('keeper.enhanced_discovery')
        logger.info(f"handle_location_selection: location_info='{location_info}', system_name='{system_name}'")

        # Validate location_info
        if not location_info:
            logger.error("handle_location_selection: location_info is empty/None!")
            await interaction.response.send_message(
                "❌ Error: No location selected. Please try again.",
                ephemeral=True
            )
            return

        # Parse location for display
        try:
            location_display = location_info.split(':')[-1]
        except:
            location_display = "Unknown"

        logger.info(f"handle_location_selection: Creating DiscoveryTypeSelect with location_info='{location_info}'")

        embed = discord.Embed(
            title="🔍 Discovery Type Selection",
            description=f"*Location confirmed: {location_display} in {system_name}*\n\nWhat type of discovery did you make?",
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

        import logging
        logger = logging.getLogger('keeper.enhanced_discovery')
        logger.info(f"DiscoveryTypeSelect.callback: discovery_type='{discovery_type}', system='{self.system_name}', location_info='{self.location_info}'")

        # Get Haven system data for context
        bot = interaction.client
        cog = bot.get_cog('EnhancedDiscoverySystem')
        haven_data = cog.haven.get_system(self.system_name)

        # Show the type-specific discovery modal
        logger.info(f"DiscoveryTypeSelect.callback: Creating modal with location_info='{self.location_info}'")
        modal = get_modal_for_type(discovery_type, self.system_name, self.location_info, self.config, haven_data)
        await interaction.response.send_modal(modal)

class PhotoUploadView(discord.ui.View):
    """View for handling photo uploads."""

    def __init__(self, discovery_id: int, cog):
        super().__init__(timeout=300)
        self.discovery_id = discovery_id
        self.cog = cog

    @discord.ui.button(label="📸 Upload Evidence Photo", style=discord.ButtonStyle.secondary)
    async def upload_photo(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle photo upload."""
        # Register this user as waiting to upload a photo
        self.cog.pending_photo_uploads[interaction.user.id] = self.discovery_id

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

        # Track users waiting to upload evidence photos
        self.pending_photo_uploads = {}  # {user_id: discovery_id}

        # Start Haven data loading
        self.bot.loop.create_task(self._initialize_haven())
    
    async def _initialize_haven(self):
        """Initialize Haven integration."""
        success = await self.haven.load_haven_data()
        if success:
            logger.info("✅ Haven integration initialized")
        else:
            logger.warning("⚠️ Haven integration failed - bot will work in standalone mode")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Listen for photo uploads from users who clicked the upload button."""
        # Ignore bot messages
        if message.author.bot:
            return

        # Check if this user is waiting to upload a photo
        if message.author.id not in self.pending_photo_uploads:
            return

        # Check if message has attachments
        if not message.attachments:
            return

        # Get the discovery ID this photo is for
        discovery_id = self.pending_photo_uploads[message.author.id]

        # Get the first image attachment
        photo_url = None
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith('image/'):
                photo_url = attachment.url
                break

        if not photo_url:
            # No image found, inform user
            await message.reply("⚠️ Please attach an image file (PNG, JPG, etc.)")
            return

        try:
            # Update the discovery with the photo URL
            await self.db.connection.execute(
                "UPDATE discoveries SET evidence_url = ? WHERE id = ?",
                (photo_url, discovery_id)
            )
            await self.db.connection.commit()

            # Remove user from pending uploads
            del self.pending_photo_uploads[message.author.id]

            # Confirm to user
            embed = discord.Embed(
                title="✅ Evidence Photo Archived",
                description=f"*Your evidence photo has been attached to Discovery #{discovery_id}*\n\nThe Keeper has preserved this visual record.",
                color=0x00ff00
            )
            embed.set_image(url=photo_url)
            await message.reply(embed=embed)

            logger.info(f"Photo uploaded for discovery {discovery_id} by user {message.author.id}")

        except Exception as e:
            logger.error(f"Error saving photo for discovery {discovery_id}: {e}")
            await message.reply("❌ Error archiving photo. Please try again later.")

    @app_commands.command(
        name="discovery-report",
        description="🔍 Report a discovery to The Keeper's Archive (Haven-Enhanced)"
    )
    async def discovery_report(self, interaction: discord.Interaction):
        """Main command to start discovery reporting with Haven integration."""

        try:
            await interaction.response.defer(ephemeral=True)
        except discord.errors.NotFound:
            # Interaction token expired - this happens with network lag
            # Try to send a followup instead
            logger.warning(f"Interaction token expired for user {interaction.user.id}, attempting recovery")
            try:
                await interaction.followup.send(
                    "⚠️ Network delay detected. Please try the command again.",
                    ephemeral=True
                )
            except:
                pass
            return
        except Exception as e:
            logger.error(f"Error deferring interaction: {e}")
            return
        
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
                'location_name': discovery_data.get('location_name'),  # CRITICAL: Must pass location_name for planet_id resolution
                'location_info': discovery_data.get('location_info'),
                # Type-specific fields (will be None if not applicable)
                'species_type': discovery_data.get('species_type'),
                'size_scale': discovery_data.get('size_scale'),
                'preservation_quality': discovery_data.get('preservation_quality'),
                'estimated_age': discovery_data.get('estimated_age'),
                'language_status': discovery_data.get('language_status'),
                'completeness': discovery_data.get('completeness'),
                'author_origin': discovery_data.get('author_origin'),
                'key_excerpt': discovery_data.get('key_excerpt'),
                'structure_type': discovery_data.get('structure_type'),
                'architectural_style': discovery_data.get('architectural_style'),
                'structural_integrity': discovery_data.get('structural_integrity'),
                'purpose_function': discovery_data.get('purpose_function'),
                'tech_category': discovery_data.get('tech_category'),
                'operational_status': discovery_data.get('operational_status'),
                'power_source': discovery_data.get('power_source'),
                'reverse_engineering': discovery_data.get('reverse_engineering'),
                'species_name': discovery_data.get('species_name'),
                'behavioral_notes': discovery_data.get('behavioral_notes'),
                'habitat_biome': discovery_data.get('habitat_biome'),
                'threat_level': discovery_data.get('threat_level'),
                'resource_type': discovery_data.get('resource_type'),
                'deposit_richness': discovery_data.get('deposit_richness'),
                'extraction_method': discovery_data.get('extraction_method'),
                'economic_value': discovery_data.get('economic_value'),
                'ship_class': discovery_data.get('ship_class'),
                'hull_condition': discovery_data.get('hull_condition'),
                'salvageable_tech': discovery_data.get('salvageable_tech'),
                'pilot_status': discovery_data.get('pilot_status'),
                'hazard_type': discovery_data.get('hazard_type'),
                'severity_level': discovery_data.get('severity_level'),
                'duration_frequency': discovery_data.get('duration_frequency'),
                'protection_required': discovery_data.get('protection_required'),
                'update_name': discovery_data.get('update_name'),
                'feature_category': discovery_data.get('feature_category'),
                'gameplay_impact': discovery_data.get('gameplay_impact'),
                'first_impressions': discovery_data.get('first_impressions'),
                'story_type': discovery_data.get('story_type'),
                'lore_connections': discovery_data.get('lore_connections'),
                'creative_elements': discovery_data.get('creative_elements'),
                'collaborative_work': discovery_data.get('collaborative_work')
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

            # Get user's tier for signal strength calculation
            user_tier = await self._get_user_tier(str(interaction.user.id), str(interaction.guild.id))
            enhanced_data['user_tier'] = user_tier

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
            photo_view = PhotoUploadView(discovery_id, self)
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
    @app_commands.default_permissions(administrator=True)
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
    
    async def _get_user_tier(self, user_id: str, guild_id: str) -> int:
        """Get user's current tier for signal strength calculation."""
        try:
            # Get user's discovery count
            cursor = await self.db.connection.execute(
                "SELECT COUNT(*) FROM discoveries WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            )
            discoveries = (await cursor.fetchone())[0]

            # Get pattern contributions
            cursor = await self.db.connection.execute(
                "SELECT COUNT(DISTINCT pattern_id) FROM pattern_contributions WHERE user_id = ?",
                (user_id,)
            )
            result = await cursor.fetchone()
            patterns = result[0] if result else 0

            # Calculate tier (same logic as community_features.py)
            if discoveries >= 30 and patterns >= 5:
                return 4
            elif discoveries >= 15 and patterns >= 3:
                return 3
            elif discoveries >= 5 and patterns >= 1:
                return 2
            else:
                return 1

        except Exception as e:
            logger.error(f"Error getting user tier: {e}")
            return 1  # Default to Tier 1

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