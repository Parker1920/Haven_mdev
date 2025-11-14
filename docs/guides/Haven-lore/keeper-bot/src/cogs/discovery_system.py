"""
Discovery System Cog - Phase 1
Handles discovery report submissions and basic Keeper responses.
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Optional
import asyncio

from core.keeper_personality import KeeperPersonality
from database.keeper_db import KeeperDatabase
from core.haven_integration import HavenIntegration

logger = logging.getLogger('keeper.discovery')

class DiscoveryModal(discord.ui.Modal, title="🌌 Discovery Report Archive"):
    """Modal for discovery report submission."""
    
    def __init__(self, discovery_type: str, config: dict):
        super().__init__()
        self.discovery_type = discovery_type
        self.config = config
        self.discovery_types = config['discovery_types']
        
    location = discord.ui.TextInput(
        label="📍 Location",
        placeholder="Planet Name — Galaxy Name — [Coordinates]",
        max_length=200,
        required=True
    )
    
    description = discord.ui.TextInput(
        label="📝 Description",
        placeholder="Describe what you found. Include direct NMS text if applicable.",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )
    
    time_period = discord.ui.TextInput(
        label="⏰ Time Period",
        placeholder="Ancient / Recent / Unknown / Specific Era",
        max_length=100,
        required=False,
        default="Unknown"
    )
    
    condition = discord.ui.TextInput(
        label="⚡ Condition/Signal Strength",
        placeholder="Well-Preserved / Damaged / Fragmented / Mysterious",
        max_length=100,
        required=False,
        default="Unknown"
    )
    
    significance = discord.ui.TextInput(
        label="🔮 Your Analysis",
        placeholder="What do YOU think it means? Any theories or connections?",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle form submission."""
        await interaction.response.defer()
        
        # Get the bot instance and process the discovery
        bot = interaction.client
        cog = bot.get_cog('DiscoverySystem')
        if cog:
            await cog.process_discovery_submission(interaction, {
                'type': self.discovery_type,
                'location': self.location.value,
                'description': self.description.value,
                'time_period': self.time_period.value,
                'condition': self.condition.value,
                'significance': self.significance.value
            })

class DiscoveryTypeSelect(discord.ui.Select):
    """Dropdown for selecting discovery type."""
    
    def __init__(self, config: dict):
        self.config = config
        discovery_types = config['discovery_types']
        
        options = []
        for emoji, name in discovery_types.items():
            options.append(discord.SelectOption(
                label=name,
                emoji=emoji,
                value=emoji,
                description=f"Report discoveries of type: {name}"
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
        
        # Show the discovery modal
        modal = DiscoveryModal(discovery_type, self.config)
        modal.title = f"{discovery_type} {discovery_name} Report"
        
        await interaction.response.send_modal(modal)

class DiscoveryTypeView(discord.ui.View):
    """View containing the discovery type selector."""
    
    def __init__(self, config: dict):
        super().__init__(timeout=300)
        self.add_item(DiscoveryTypeSelect(config))
    
    async def on_timeout(self):
        """Handle view timeout."""
        for item in self.children:
            item.disabled = True

class DiscoverySystem(commands.Cog):
    """Main discovery system cog."""
    
    def __init__(self, bot):
        self.bot = bot
        self.db: KeeperDatabase = bot.db
        self.personality: KeeperPersonality = bot.personality
        self.config = bot.config
        
    @app_commands.command(
        name="discovery-report",
        description="🔍 Report a discovery to The Keeper's Archive"
    )
    async def discovery_report(self, interaction: discord.Interaction):
        """Main command to start discovery reporting."""
        
        embed = discord.Embed(
            title="🌌 Discovery Report Interface",
            description="*The Keeper's consciousness stirs, ready to receive your findings...*",
            color=self.config['theme']['embed_colors']['discovery']
        )
        
        embed.add_field(
            name="📋 Reporting Process",
            value="Select the type of discovery you've made, then provide details through the guided interface.",
            inline=False
        )
        
        embed.add_field(
            name="💡 Tips for Quality Reports",
            value="• Include exact NMS text when possible\\n• Mention planet/system names\\n• Note any unusual characteristics\\n• Share your theories about significance",
            inline=False
        )
        
        embed.set_footer(text="The Archive awaits your contribution, Traveler.")
        
        view = DiscoveryTypeView(self.config)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    async def process_discovery_submission(self, interaction: discord.Interaction, discovery_data: dict):
        """Process a completed discovery submission."""
        try:
            # Enhance discovery data
            enhanced_data = {
                **discovery_data,
                'user_id': str(interaction.user.id),
                'username': interaction.user.display_name,
                'submission_timestamp': discord.utils.utcnow(),
                'guild_id': str(interaction.guild.id) if interaction.guild else None
            }
            
            # Parse location data
            location_parts = discovery_data['location'].split('—')
            if len(location_parts) >= 2:
                enhanced_data['planet_name'] = location_parts[0].strip()
                enhanced_data['galaxy_name'] = location_parts[1].strip()
                if len(location_parts) >= 3:
                    enhanced_data['coordinates'] = location_parts[2].strip()
            
            # Save to database
            discovery_id = await self.db.add_discovery(enhanced_data)
            enhanced_data['id'] = discovery_id
            
            # Create Keeper analysis response
            analysis_embed = self.personality.create_discovery_analysis(enhanced_data)
            
            # Send confirmation to user
            confirm_embed = discord.Embed(
                title="✅ Discovery Archived",
                description=f"*Your discovery has been processed and added to the Archive as Entry #{discovery_id}*",
                color=self.config['theme']['embed_colors']['success']
            )
            
            await interaction.followup.send(embed=confirm_embed, ephemeral=True)
            
            # Post analysis to archive channel
            await self.post_to_archive_channel(interaction.guild, analysis_embed, discovery_id)
            
            # Check for patterns (Phase 2 functionality)
            if hasattr(self.bot, 'get_cog') and self.bot.get_cog('PatternRecognition'):
                pattern_cog = self.bot.get_cog('PatternRecognition')
                await pattern_cog.analyze_for_patterns(discovery_id)
            
            logger.info(f"Discovery {discovery_id} processed for user {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error processing discovery: {e}")
            error_embed = discord.Embed(
                title="❌ Archive Error",
                description="*The Keeper's systems experienced a disruption. Please try again.*",
                color=self.config['theme']['embed_colors']['error']
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
    
    async def post_to_archive_channel(self, guild: discord.Guild, embed: discord.Embed, discovery_id: int):
        """Post the analysis to the configured archive channel."""
        try:
            # Get server config
            config = await self.db.get_server_config(str(guild.id))
            if not config or not config.get('archive_channel_id'):
                logger.warning(f"No archive channel configured for guild {guild.id}")
                return
            
            # Get the archive channel
            archive_channel = guild.get_channel(int(config['archive_channel_id']))
            if not archive_channel:
                logger.warning(f"Archive channel not found: {config['archive_channel_id']}")
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
                f"DISC_{discovery_id:06d}",
                discovery_id,
                "discovery_analysis",
                embed.title,
                embed.description,
                str(archive_channel.id),
                str(message.id),
                embed.to_dict()
            ))
            await self.db.connection.commit()
            
            logger.info(f"Discovery {discovery_id} posted to archive channel")
            
        except Exception as e:
            logger.error(f"Error posting to archive channel: {e}")
    
    @app_commands.command(
        name="quick-discovery",
        description="🚀 Quick discovery report (streamlined)"
    )
    @app_commands.describe(
        discovery_type="Type of discovery",
        description="What you found",
        location="Where you found it"
    )
    @app_commands.choices(discovery_type=[
        app_commands.Choice(name=f"{emoji} {name}", value=emoji)
        for emoji, name in {
            "🦴": "Ancient Bones & Fossils",
            "📜": "Text Logs & Documents", 
            "🏛️": "Ruins & Structures",
            "⚙️": "Alien Technology",
            "🦗": "Flora & Fauna"
        }.items()
    ])
    async def quick_discovery(
        self,
        interaction: discord.Interaction,
        discovery_type: str,
        description: str,
        location: str,
        time_period: Optional[str] = "Unknown",
        condition: Optional[str] = "Unknown"
    ):
        """Quick discovery report for experienced users."""
        
        await interaction.response.defer()
        
        # Process the quick submission
        discovery_data = {
            'type': discovery_type,
            'description': description,
            'location': location,
            'time_period': time_period,
            'condition': condition,
            'significance': ""
        }
        
        await self.process_discovery_submission(interaction, discovery_data)
    
    @app_commands.command(
        name="search-discoveries",
        description="🔍 Search the Archive for discoveries"
    )
    @app_commands.describe(
        query="Search term (location, type, or description)",
        discovery_type="Filter by discovery type",
        user="Filter by user"
    )
    async def search_discoveries(
        self,
        interaction: discord.Interaction,
        query: Optional[str] = None,
        discovery_type: Optional[str] = None,
        user: Optional[discord.Member] = None
    ):
        """Search the discovery archive."""
        
        await interaction.response.defer()
        
        try:
            # Build search parameters
            search_params = {
                'limit': 20
            }
            
            if discovery_type:
                search_params['discovery_type'] = discovery_type
            if user:
                search_params['user_id'] = str(user.id)
            if query:
                search_params['location'] = query  # Simple location search for now
            
            # Perform search
            discoveries = await self.db.search_discoveries(**search_params)
            
            if not discoveries:
                embed = discord.Embed(
                    title="🔍 Archive Search Results",
                    description="*The Keeper's algorithms found no matching entries.*",
                    color=self.config['theme']['embed_colors']['warning']
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Format results
            embed = discord.Embed(
                title="🔍 Archive Search Results",
                description=f"*{len(discoveries)} entries located in the Archive*",
                color=self.config['theme']['embed_colors']['archive']
            )
            
            for i, discovery in enumerate(discoveries[:5]):  # Show top 5
                embed.add_field(
                    name=f"{discovery['type']} Entry #{discovery['id']}",
                    value=f"**Traveler:** {discovery['username']}\\n**Location:** {discovery['location']}\\n**Description:** {discovery['description'][:100]}{'...' if len(discovery['description']) > 100 else ''}",
                    inline=False
                )
            
            if len(discoveries) > 5:
                embed.set_footer(text=f"Showing 5 of {len(discoveries)} results. Use more specific search terms for better results.")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in discovery search: {e}")
            error_embed = discord.Embed(
                title="❌ Search Error",
                description="*The Archive experienced a query malfunction.*",
                color=self.config['theme']['embed_colors']['error']
            )
            await interaction.followup.send(embed=error_embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for natural language discovery reports."""
        # Skip bot messages and DMs
        if message.author.bot or not message.guild:
            return
        
        # Check if this is the discovery channel
        config = await self.db.get_server_config(str(message.guild.id))
        if not config or str(message.channel.id) != config.get('discovery_channel_id'):
            return
        
        # Look for discovery keywords
        discovery_keywords = ['found', 'discovered', 'located', 'uncovered', 'excavated']
        message_lower = message.content.lower()
        
        if any(keyword in message_lower for keyword in discovery_keywords):
            # React to suggest using the proper command
            await message.add_reaction('🔍')
            
            # Send helpful response
            embed = discord.Embed(
                title="🌌 Discovery Detected",
                description=f"*The Keeper senses a discovery in your message, {message.author.mention}.*",
                color=self.config['theme']['embed_colors']['discovery']
            )
            embed.add_field(
                name="📝 Proper Archive Format",
                value="Use `/discovery-report` for complete analysis and archival, or `/quick-discovery` for rapid submission.",
                inline=False
            )
            
            await message.reply(embed=embed, delete_after=30)

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(DiscoverySystem(bot))