"""
Archive System - Phase 3
Advanced archive search, viewing, and organization functionality.
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import asyncio

from core.keeper_personality import KeeperPersonality
from database.keeper_db import KeeperDatabase
from core.haven_integration import HavenIntegration

logger = logging.getLogger('keeper.archive')

class AdvancedSearchModal(discord.ui.Modal, title="🔍 Advanced Archive Search"):
    """Modal for advanced search parameters."""
    
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
    
    search_terms = discord.ui.TextInput(
        label="🔤 Search Terms",
        placeholder="Keywords to search in descriptions, significance, or analysis",
        max_length=200,
        required=False
    )
    
    date_range = discord.ui.TextInput(
        label="📅 Date Range",
        placeholder="e.g. '7 days', '2024-01', 'last month' (optional)",
        max_length=50,
        required=False
    )
    
    location_filter = discord.ui.TextInput(
        label="🗺️ Location Filter",
        placeholder="System, planet, region, or coordinates",
        max_length=100,
        required=False
    )
    
    user_filter = discord.ui.TextInput(
        label="👤 Explorer Filter",
        placeholder="Username or part of username",
        max_length=50,
        required=False
    )
    
    pattern_filter = discord.ui.TextInput(
        label="🌀 Pattern/Tier Filter",
        placeholder="Pattern name or mystery tier (1-4)",
        max_length=50,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Process the advanced search."""
        bot = interaction.client
        cog = bot.get_cog('ArchiveSystem')
        if cog:
            search_params = {
                'search_terms': self.search_terms.value,
                'date_range': self.date_range.value,
                'location_filter': self.location_filter.value,
                'user_filter': self.user_filter.value,
                'pattern_filter': self.pattern_filter.value
            }
            await cog.process_advanced_search(interaction, search_params)

class ArchivePaginationView(discord.ui.View):
    """Paginated view for archive results."""
    
    def __init__(self, results: List[Dict], config: dict, page_size: int = 5):
        super().__init__(timeout=300)
        self.results = results
        self.config = config
        self.page_size = page_size
        self.current_page = 0
        self.max_pages = (len(results) - 1) // page_size + 1
        
        # Update button states
        self.update_buttons()
    
    def update_buttons(self):
        """Update button enabled/disabled states."""
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page >= self.max_pages - 1
        self.page_selector.placeholder = f"Page {self.current_page + 1} of {self.max_pages}"
    
    def create_page_embed(self) -> discord.Embed:
        """Create embed for current page."""
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, len(self.results))
        page_results = self.results[start_idx:end_idx]
        
        embed = discord.Embed(
            title="🗃️ Archive Search Results",
            description=f"*Page {self.current_page + 1} of {self.max_pages} • {len(self.results)} total entries*",
            color=self.config['theme']['embed_colors']['archive']
        )
        
        for result in page_results:
            discovery_type = result.get('type', '❓')
            location = result.get('location_name', result.get('location', 'Unknown'))
            system = result.get('system_name', 'Unknown System')
            
            # Format timestamp
            timestamp = result.get('submission_timestamp', '')
            if timestamp:
                if isinstance(timestamp, str):
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        timestamp_str = dt.strftime('%Y-%m-%d')
                    except:
                        timestamp_str = timestamp[:10]
                else:
                    timestamp_str = timestamp.strftime('%Y-%m-%d')
            else:
                timestamp_str = 'Unknown'
            
            embed.add_field(
                name=f"{discovery_type} Entry #{result['id']} • {timestamp_str}",
                value=f"**Explorer:** {result.get('username', 'Unknown')}\\n**Location:** {location} ({system})\\n**Description:** {result.get('description', 'No description')[:150]}{'...' if len(result.get('description', '')) > 150 else ''}",
                inline=False
            )
        
        embed.set_footer(text="Use buttons to navigate • Select entry for detailed view")
        return embed
    
    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to previous page."""
        self.current_page = max(0, self.current_page - 1)
        self.update_buttons()
        embed = self.create_page_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="▶️ Next", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to next page."""
        self.current_page = min(self.max_pages - 1, self.current_page + 1)
        self.update_buttons()
        embed = self.create_page_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.select(placeholder="📄 Select page...", min_values=1, max_values=1)
    async def page_selector(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Jump to specific page."""
        try:
            page_num = int(select.values[0]) - 1
            self.current_page = max(0, min(page_num, self.max_pages - 1))
            self.update_buttons()
            embed = self.create_page_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        except:
            await interaction.response.defer()
    
    async def on_timeout(self):
        """Handle view timeout."""
        for item in self.children:
            item.disabled = True

class PatternManagementView(discord.ui.View):
    """View for pattern management operations."""
    
    def __init__(self, pattern: Dict, config: dict):
        super().__init__(timeout=300)
        self.pattern = pattern
        self.config = config
    
    @discord.ui.button(label="🔍 View Details", style=discord.ButtonStyle.primary)
    async def view_details(self, interaction: discord.Interaction, button: discord.ui.Button):
        """View detailed pattern information."""
        pattern = self.pattern
        
        embed = discord.Embed(
            title=f"🌀 {pattern['name']} - Detailed Analysis",
            description=pattern.get('description', 'No description available'),
            color=self.config['theme']['embed_colors']['pattern']
        )
        
        embed.add_field(
            name="📊 Pattern Statistics",
            value=f"**Type:** {pattern.get('type', 'Unknown')}\\n**Discoveries:** {pattern.get('discovery_count', 0)}\\n**Confidence:** {pattern.get('confidence', 0):.1%}\\n**Status:** {pattern.get('status', 'Unknown')}",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Mystery Tier",
            value=f"**Tier {pattern.get('mystery_tier', 1)}**\\n{self._get_tier_description(pattern.get('mystery_tier', 1))}",
            inline=True
        )
        
        # Get timeline info
        first_discovered = pattern.get('first_discovered')
        last_updated = pattern.get('last_updated')
        
        if first_discovered:
            if isinstance(first_discovered, str):
                first_discovered = datetime.fromisoformat(first_discovered.replace('Z', '+00:00'))
            timeline = f"**First:** {first_discovered.strftime('%Y-%m-%d %H:%M')}"
        else:
            timeline = "**First:** Unknown"
        
        if last_updated:
            if isinstance(last_updated, str):
                last_updated = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            timeline += f"\\n**Updated:** {last_updated.strftime('%Y-%m-%d %H:%M')}"
        
        embed.add_field(name="⏰ Timeline", value=timeline, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📋 List Discoveries", style=discord.ButtonStyle.secondary)
    async def list_discoveries(self, interaction: discord.Interaction, button: discord.ui.Button):
        """List all discoveries associated with this pattern."""
        bot = interaction.client
        cog = bot.get_cog('ArchiveSystem')
        if cog:
            await cog.list_pattern_discoveries(interaction, self.pattern['id'])
    
    @discord.ui.button(label="🔄 Refresh Analysis", style=discord.ButtonStyle.secondary)
    async def refresh_analysis(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Refresh pattern analysis (admin only)."""
        # Check if user has admin permissions
        if not await self._check_admin_permissions(interaction):
            await interaction.response.send_message("❌ Admin permissions required.", ephemeral=True)
            return
        
        await interaction.response.send_message("🔄 Pattern analysis refresh initiated...", ephemeral=True)
        # This would trigger a re-analysis of the pattern
    
    def _get_tier_description(self, tier: int) -> str:
        """Get description for mystery tier."""
        tier_descriptions = {
            1: "Surface Anomaly - Initial pattern detection",
            2: "Pattern Emergence - Clear connections found",
            3: "Deep Mystery - Significant implications",
            4: "Cosmic Significance - Reality-altering discoveries"
        }
        return tier_descriptions.get(tier, "Unknown significance")
    
    async def _check_admin_permissions(self, interaction: discord.Interaction) -> bool:
        """Check if user has admin permissions."""
        # Simple permission check - can be enhanced
        return interaction.user.guild_permissions.administrator

class ArchiveSystem(commands.Cog):
    """Advanced archive system for Phase 3."""
    
    def __init__(self, bot):
        self.bot = bot
        self.db: KeeperDatabase = bot.db
        self.personality: KeeperPersonality = bot.personality
        self.config = bot.config
        self.haven = HavenIntegration()
        logger.info("Archive System Phase 3 loaded")
    
    @app_commands.command(
        name="advanced-search",
        description="🔍 Advanced search through The Keeper's archives"
    )
    async def advanced_search(self, interaction: discord.Interaction):
        """Advanced search interface."""
        modal = AdvancedSearchModal(self.config)
        await interaction.response.send_modal(modal)
    
    async def process_advanced_search(self, interaction: discord.Interaction, search_params: Dict):
        """Process advanced search parameters."""
        await interaction.response.defer()
        
        try:
            # Build search query
            discoveries = await self._execute_advanced_search(search_params)
            
            if not discoveries:
                embed = discord.Embed(
                    title="🔍 Archive Search Complete",
                    description="*No entries match your search criteria.*",
                    color=self.config['theme']['embed_colors']['warning']
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create paginated results
            view = ArchivePaginationView(discoveries, self.config)
            embed = view.create_page_embed()
            
            # Add page selector options
            if view.max_pages > 1:
                options = [discord.SelectOption(label=f"Page {i+1}", value=str(i+1)) 
                          for i in range(min(view.max_pages, 25))]
                view.page_selector.options = options
            
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error in advanced search: {e}")
            error_embed = discord.Embed(
                title="❌ Search Error",
                description="An error occurred while searching the archives.",
                color=self.config['theme']['embed_colors']['error']
            )
            await interaction.followup.send(embed=error_embed)
    
    async def _execute_advanced_search(self, params: Dict) -> List[Dict]:
        """Execute advanced search with multiple parameters."""
        query = "SELECT * FROM discoveries WHERE 1=1"
        query_params = []
        
        # Search terms in description/significance
        if params.get('search_terms'):
            search_terms = params['search_terms'].strip()
            query += " AND (description LIKE ? OR significance LIKE ?)"
            query_params.extend([f"%{search_terms}%", f"%{search_terms}%"])
        
        # Date range filter
        if params.get('date_range'):
            date_filter = self._parse_date_range(params['date_range'])
            if date_filter:
                query += " AND submission_timestamp >= ?"
                query_params.append(date_filter.isoformat())
        
        # Location filter
        if params.get('location_filter'):
            location = params['location_filter'].strip()
            query += " AND (location LIKE ? OR system_name LIKE ? OR location_name LIKE ?)"
            location_pattern = f"%{location}%"
            query_params.extend([location_pattern, location_pattern, location_pattern])
        
        # User filter
        if params.get('user_filter'):
            username = params['user_filter'].strip()
            query += " AND username LIKE ?"
            query_params.append(f"%{username}%")
        
        # Pattern/tier filter
        if params.get('pattern_filter'):
            pattern_filter = params['pattern_filter'].strip()
            if pattern_filter.isdigit():
                # Filter by mystery tier
                query += " AND mystery_tier = ?"
                query_params.append(int(pattern_filter))
            else:
                # Filter by pattern matches
                query += " AND pattern_matches > 0"
        
        query += " ORDER BY submission_timestamp DESC LIMIT 100"
        
        cursor = await self.db.connection.execute(query, query_params)
        rows = await cursor.fetchall()
        
        return [self.db._row_to_discovery_dict(row) for row in rows]
    
    def _parse_date_range(self, date_str: str) -> Optional[datetime]:
        """Parse date range string into datetime."""
        date_str = date_str.lower().strip()
        now = datetime.utcnow()
        
        try:
            if 'day' in date_str:
                days = int(''.join(filter(str.isdigit, date_str)))
                return now - timedelta(days=days)
            elif 'week' in date_str:
                weeks = int(''.join(filter(str.isdigit, date_str)))
                return now - timedelta(weeks=weeks)
            elif 'month' in date_str:
                months = int(''.join(filter(str.isdigit, date_str)))
                return now - timedelta(days=months * 30)
            elif len(date_str) >= 7:  # Date format like 2024-01
                return datetime.fromisoformat(date_str + "-01" if len(date_str) == 7 else date_str)
        except:
            pass
        
        return None
    
    @app_commands.command(
        name="pattern-manager",
        description="🌀 Manage and analyze detected patterns"
    )
    @app_commands.default_permissions(administrator=True)
    async def pattern_manager(self, interaction: discord.Interaction):
        """Pattern management interface."""
        await interaction.response.defer()
        
        try:
            # Get all patterns
            all_patterns = []
            for tier in range(1, 5):
                tier_patterns = await self.db.get_patterns_by_tier(tier)
                all_patterns.extend(tier_patterns)
            
            if not all_patterns:
                embed = discord.Embed(
                    title="🌀 Pattern Management",
                    description="*No patterns detected in the Archive.*",
                    color=self.config['theme']['embed_colors']['warning']
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create management interface
            embed = discord.Embed(
                title="🌀 Pattern Management Interface",
                description=f"*{len(all_patterns)} patterns detected across all mystery tiers*",
                color=self.config['theme']['embed_colors']['pattern']
            )
            
            # Group by tier
            tier_counts = {}
            for pattern in all_patterns:
                tier = pattern.get('mystery_tier', 1)
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
            
            for tier in range(1, 5):
                tier_name = self.config['mystery_tiers'][str(tier)]['name']
                count = tier_counts.get(tier, 0)
                embed.add_field(
                    name=f"Tier {tier}: {tier_name}",
                    value=f"{count} patterns",
                    inline=True
                )
            
            # Add pattern selector
            view = PatternSelectorView(all_patterns, self.config)
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error in pattern manager: {e}")
            error_embed = discord.Embed(
                title="❌ Pattern Manager Error",
                description="Unable to access pattern management interface.",
                color=self.config['theme']['embed_colors']['error']
            )
            await interaction.followup.send(embed=error_embed)
    
    async def list_pattern_discoveries(self, interaction: discord.Interaction, pattern_id: int):
        """List all discoveries associated with a pattern."""
        try:
            # Get pattern-discovery relationships
            cursor = await self.db.connection.execute("""
                SELECT d.* FROM discoveries d
                JOIN pattern_discoveries pd ON d.id = pd.discovery_id
                WHERE pd.pattern_id = ?
                ORDER BY d.submission_timestamp DESC
            """, (pattern_id,))
            
            rows = await cursor.fetchall()
            discoveries = [self.db._row_to_discovery_dict(row) for row in rows]
            
            if not discoveries:
                await interaction.response.send_message("No discoveries found for this pattern.", ephemeral=True)
                return
            
            # Create discovery list embed
            embed = discord.Embed(
                title=f"📋 Pattern Discoveries",
                description=f"*{len(discoveries)} discoveries associated with this pattern*",
                color=self.config['theme']['embed_colors']['archive']
            )
            
            for discovery in discoveries[:10]:  # Limit to 10 for display
                embed.add_field(
                    name=f"{discovery['type']} Entry #{discovery['id']}",
                    value=f"**Explorer:** {discovery['username']}\\n**Location:** {discovery.get('location_name', 'Unknown')}\\n**Date:** {discovery.get('submission_timestamp', 'Unknown')[:10]}",
                    inline=True
                )
            
            if len(discoveries) > 10:
                embed.set_footer(text=f"Showing 10 of {len(discoveries)} discoveries")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error listing pattern discoveries: {e}")
            await interaction.response.send_message("Error retrieving pattern discoveries.", ephemeral=True)

class PatternSelectorView(discord.ui.View):
    """View for selecting patterns to manage."""
    
    def __init__(self, patterns: List[Dict], config: dict):
        super().__init__(timeout=300)
        self.patterns = patterns
        self.config = config
        
        # Add pattern selector
        options = []
        for pattern in patterns[:25]:  # Discord limit
            tier = pattern.get('mystery_tier', 1)
            options.append(discord.SelectOption(
                label=pattern['name'],
                value=str(pattern['id']),
                description=f"Tier {tier} • {pattern.get('discovery_count', 0)} discoveries",
                emoji="🌀"
            ))
        
        if options:
            self.add_item(PatternSelector(options, self.patterns, config))
    
    @discord.ui.button(label="🔄 Refresh Patterns", style=discord.ButtonStyle.secondary)
    async def refresh_patterns(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Refresh pattern list."""
        await interaction.response.send_message("🔄 Refreshing pattern list...", ephemeral=True)

class PatternSelector(discord.ui.Select):
    """Dropdown for selecting a pattern."""
    
    def __init__(self, options: List[discord.SelectOption], patterns: List[Dict], config: dict):
        self.patterns = {str(p['id']): p for p in patterns}
        self.config = config
        super().__init__(placeholder="🌀 Select a pattern to manage...", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        """Handle pattern selection."""
        pattern_id = self.values[0]
        pattern = self.patterns.get(pattern_id)
        
        if pattern:
            view = PatternManagementView(pattern, self.config)
            embed = discord.Embed(
                title=f"🌀 {pattern['name']}",
                description=f"Managing pattern with {pattern.get('discovery_count', 0)} discoveries",
                color=self.config['theme']['embed_colors']['pattern']
            )
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        else:
            await interaction.response.send_message("Pattern not found.", ephemeral=True)

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(ArchiveSystem(bot))