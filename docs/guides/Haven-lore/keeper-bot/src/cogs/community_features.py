"""
Community Features - Phase 4
Mystery tier progression, challenges, leaderboards, and community engagement.
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import logging
from typing import Dict, List, Optional, Tuple
import json
import asyncio
from datetime import datetime, timedelta
import random

from core.keeper_personality import KeeperPersonality
from database.keeper_db import KeeperDatabase
from core.haven_integration import HavenIntegration

logger = logging.getLogger('keeper.community')

class MysteryTierView(discord.ui.View):
    """View for mystery tier progression interface."""
    
    def __init__(self, user_id: str, tier_data: Dict, config: dict):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.tier_data = tier_data
        self.config = config
    
    @discord.ui.button(label="🎯 View Requirements", style=discord.ButtonStyle.primary)
    async def view_requirements(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show tier progression requirements."""
        current_tier = self.tier_data.get('current_tier', 1)
        next_tier = min(current_tier + 1, 4)
        
        embed = discord.Embed(
            title=f"🎯 Tier {next_tier} Requirements",
            description="*Path to deeper mysteries*",
            color=self.config['theme']['embed_colors']['discovery']
        )
        
        # Tier-specific requirements
        requirements = self._get_tier_requirements(next_tier)
        
        for req_type, details in requirements.items():
            progress = self.tier_data.get('progress', {}).get(req_type, 0)
            required = details['required']
            status = "✅" if progress >= required else "⏳"
            
            embed.add_field(
                name=f"{status} {details['name']}",
                value=f"**Progress:** {progress}/{required}\n{details['description']}",
                inline=True
            )
        
        # Special tier bonuses
        if next_tier > 1:
            bonuses = self._get_tier_bonuses(next_tier)
            embed.add_field(
                name="🌟 Tier Bonuses",
                value="\n".join([f"• {bonus}" for bonus in bonuses]),
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📈 Progress Overview", style=discord.ButtonStyle.secondary)
    async def progress_overview(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show detailed progress overview."""
        embed = discord.Embed(
            title="📈 Explorer Progress",
            description="*Your journey through the mysteries*",
            color=self.config['theme']['embed_colors']['archive']
        )
        
        # Current tier info
        current_tier = self.tier_data.get('current_tier', 1)
        embed.add_field(
            name="🔱 Current Tier",
            value=f"**{self._get_tier_name(current_tier)}** (Tier {current_tier})",
            inline=True
        )
        
        # Total discoveries
        total_discoveries = self.tier_data.get('total_discoveries', 0)
        embed.add_field(
            name="🔍 Total Discoveries",
            value=str(total_discoveries),
            inline=True
        )
        
        # Pattern contributions
        pattern_contributions = self.tier_data.get('pattern_contributions', 0)
        embed.add_field(
            name="🌀 Pattern Contributions",
            value=str(pattern_contributions),
            inline=True
        )
        
        # Recent achievements
        recent_achievements = self.tier_data.get('recent_achievements', [])
        if recent_achievements:
            achievement_text = "\n".join([f"• {achievement}" for achievement in recent_achievements[-5:]])
            embed.add_field(
                name="🏆 Recent Achievements",
                value=achievement_text,
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def _get_tier_requirements(self, tier: int) -> Dict:
        """Get requirements for a specific tier."""
        requirements = {
            2: {
                'discoveries': {'name': 'Discoveries', 'required': 5, 'description': 'Submit discovery reports'},
                'patterns': {'name': 'Pattern Contributions', 'required': 1, 'description': 'Contribute to pattern recognition'},
                'variety': {'name': 'Location Variety', 'required': 3, 'description': 'Discover different Haven systems'}
            },
            3: {
                'discoveries': {'name': 'Discoveries', 'required': 15, 'description': 'Submit discovery reports'},
                'patterns': {'name': 'Pattern Contributions', 'required': 3, 'description': 'Contribute to pattern recognition'},
                'quality': {'name': 'Quality Reports', 'required': 5, 'description': 'High-quality detailed reports'},
                'collaboration': {'name': 'Collaborations', 'required': 2, 'description': 'Collaborate with other explorers'}
            },
            4: {
                'discoveries': {'name': 'Discoveries', 'required': 30, 'description': 'Submit discovery reports'},
                'patterns': {'name': 'Pattern Insights', 'required': 5, 'description': 'Contribute significant pattern insights'},
                'mentorship': {'name': 'Mentorship', 'required': 3, 'description': 'Guide new explorers'},
                'investigation': {'name': 'Investigation Leadership', 'required': 2, 'description': 'Lead investigation threads'}
            }
        }
        return requirements.get(tier, {})
    
    def _get_tier_bonuses(self, tier: int) -> List[str]:
        """Get bonuses for achieving a tier."""
        bonuses = {
            2: [
                "Access to pattern analysis tools",
                "Enhanced discovery formatting",
                "Keeper lore insights"
            ],
            3: [
                "Investigation thread creation",
                "Advanced archive search",
                "Cross-pattern correlation access",
                "Community challenge participation"
            ],
            4: [
                "Full Keeper archive access",
                "Pattern creation abilities", 
                "Community event hosting",
                "Direct Keeper communication",
                "Explorer mentorship tools"
            ]
        }
        return bonuses.get(tier, [])
    
    def _get_tier_name(self, tier: int) -> str:
        """Get the name for a tier."""
        names = {
            1: "Initiate Explorer",
            2: "Pattern Seeker", 
            3: "Lore Investigator",
            4: "Archive Curator"
        }
        return names.get(tier, "Unknown Tier")

class ChallengeParticipationView(discord.ui.View):
    """View for community challenge participation."""
    
    def __init__(self, challenge_data: Dict, config: dict):
        super().__init__(timeout=600)
        self.challenge_data = challenge_data
        self.config = config
    
    @discord.ui.button(label="📝 Submit Entry", style=discord.ButtonStyle.primary, emoji="🏆")
    async def submit_entry(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Submit a challenge entry."""
        modal = ChallengeSubmissionModal(self.challenge_data)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📊 View Leaderboard", style=discord.ButtonStyle.secondary)
    async def view_leaderboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        """View challenge leaderboard."""
        embed = discord.Embed(
            title=f"🏆 {self.challenge_data['name']} Leaderboard",
            description="*Current standings*",
            color=self.config['theme']['embed_colors']['discovery']
        )
        
        leaderboard = self.challenge_data.get('leaderboard', [])
        
        if leaderboard:
            for i, entry in enumerate(leaderboard[:10], 1):
                rank_emoji = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
                embed.add_field(
                    name=f"{rank_emoji} {entry['username']}",
                    value=f"**Score:** {entry['score']}\n**Submissions:** {entry['submissions']}",
                    inline=True if i > 3 else False
                )
        else:
            embed.add_field(
                name="No Entries Yet",
                value="Be the first to participate!",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ChallengeCreationModal(discord.ui.Modal, title="🎯 Create Community Challenge"):
    """Modal for creating a new community challenge."""
    
    def __init__(self, cog):
        super().__init__()
        self.cog = cog
    
    challenge_name = discord.ui.TextInput(
        label="Challenge Name",
        placeholder="e.g., 'The Great Moon Survey' or 'Pattern Hunter'",
        style=discord.TextStyle.short,
        max_length=100,
        required=True
    )
    
    challenge_description = discord.ui.TextInput(
        label="Description",
        placeholder="What should explorers do? What's the goal?",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=True
    )
    
    challenge_type = discord.ui.TextInput(
        label="Challenge Type",
        placeholder="discovery, pattern, exploration, theory, or community",
        style=discord.TextStyle.short,
        max_length=50,
        required=True
    )
    
    duration_days = discord.ui.TextInput(
        label="Duration (Days)",
        placeholder="1-30 days (default: 7)",
        style=discord.TextStyle.short,
        max_length=2,
        required=False,
        default="7"
    )
    
    rewards = discord.ui.TextInput(
        label="Rewards",
        placeholder="XP rewards, tier points, special recognition...",
        style=discord.TextStyle.paragraph,
        max_length=300,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Process challenge creation."""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Validate challenge type
            valid_types = ['discovery', 'pattern', 'exploration', 'theory', 'community']
            challenge_type = self.challenge_type.value.lower().strip()
            if challenge_type not in valid_types:
                embed = discord.Embed(
                    title="❌ Invalid Challenge Type",
                    description=f"Challenge type must be one of: {', '.join(valid_types)}",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Validate duration
            try:
                duration = int(self.duration_days.value) if self.duration_days.value else 7
                if duration < 1 or duration > 30:
                    raise ValueError("Duration must be between 1 and 30 days")
            except ValueError as e:
                embed = discord.Embed(
                    title="❌ Invalid Duration",
                    description=f"Duration must be a number between 1 and 30 days.\n{str(e)}",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Check for duplicate challenge names
            guild_id = str(interaction.guild.id)
            existing = await self.cog.db.get_active_challenges(guild_id)
            if any(c['name'].lower() == self.challenge_name.value.lower() for c in existing):
                embed = discord.Embed(
                    title="❌ Duplicate Challenge",
                    description=f"A challenge named '{self.challenge_name.value}' already exists.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Create the challenge
            challenge_data = {
                'guild_id': guild_id,
                'name': self.challenge_name.value,
                'description': self.challenge_description.value,
                'challenge_type': challenge_type,
                'duration_days': duration,
                'rewards': self.rewards.value if self.rewards.value else "Recognition and XP",
                'created_by': str(interaction.user.id),
                'created_by_name': interaction.user.display_name
            }
            
            await self.cog.db.create_challenge(challenge_data)
            
            # Success embed
            embed = discord.Embed(
                title="✅ Challenge Created!",
                description=f"**{self.challenge_name.value}** has been created and is now active!",
                color=self.cog.config['theme']['embed_colors']['keeper']
            )
            embed.add_field(name="Type", value=challenge_type.capitalize(), inline=True)
            embed.add_field(name="Duration", value=f"{duration} days", inline=True)
            embed.add_field(name="Status", value="🟢 Active", inline=True)
            embed.add_field(
                name="Description",
                value=self.challenge_description.value,
                inline=False
            )
            if self.rewards.value:
                embed.add_field(name="Rewards", value=self.rewards.value, inline=False)
            
            embed.set_footer(text=f"Created by {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error creating challenge: {e}")
            embed = discord.Embed(
                title="❌ Error Creating Challenge",
                description="An error occurred while creating the challenge. Please try again.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

class ChallengeSubmissionModal(discord.ui.Modal, title="🏆 Challenge Submission"):
    """Modal for submitting challenge entries."""
    
    def __init__(self, challenge_data: Dict):
        super().__init__()
        self.challenge_data = challenge_data
    
    entry_description = discord.ui.TextInput(
        label="Entry Description",
        placeholder="Describe your discovery, theory, or contribution...",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )
    
    supporting_evidence = discord.ui.TextInput(
        label="Supporting Evidence",
        placeholder="Coordinates, screenshots, patterns, references...",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Process challenge submission."""
        bot = interaction.client
        cog = bot.get_cog('CommunityFeatures')
        if cog:
            await cog.process_challenge_submission(interaction, self.challenge_data, {
                'description': self.entry_description.value,
                'evidence': self.supporting_evidence.value
            })

class LeaderboardView(discord.ui.View):
    """View for explorer leaderboards."""
    
    def __init__(self, leaderboard_data: Dict, config: dict):
        super().__init__(timeout=300)
        self.leaderboard_data = leaderboard_data
        self.config = config
        self.current_board = 'discoveries'
    
    @discord.ui.select(
        placeholder="Choose leaderboard category...",
        options=[
            discord.SelectOption(
                label="🔍 Total Discoveries",
                value="discoveries",
                description="Ranked by total discoveries",
                emoji="🔍"
            ),
            discord.SelectOption(
                label="🌀 Pattern Insights", 
                value="patterns",
                description="Ranked by pattern contributions",
                emoji="🌀"
            ),
            discord.SelectOption(
                label="📈 Recent Activity",
                value="recent",
                description="Most active this week",
                emoji="📈"
            ),
            discord.SelectOption(
                label="🎯 Mystery Tier",
                value="tiers",
                description="Highest tier explorers",
                emoji="🎯"
            )
        ]
    )
    async def select_leaderboard(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Switch leaderboard category."""
        self.current_board = select.values[0]
        await self.update_leaderboard(interaction)
    
    async def update_leaderboard(self, interaction: discord.Interaction):
        """Update the leaderboard display."""
        board_data = self.leaderboard_data.get(self.current_board, [])
        
        title_map = {
            'discoveries': "🔍 Discovery Leaderboard",
            'patterns': "🌀 Pattern Insight Leaders",
            'recent': "📈 Weekly Activity Leaders", 
            'tiers': "🎯 Tier Progression Leaders"
        }
        
        embed = discord.Embed(
            title=title_map[self.current_board],
            description="*Recognition of dedicated explorers*",
            color=self.config['theme']['embed_colors']['archive']
        )
        
        if board_data:
            for i, entry in enumerate(board_data[:10], 1):
                rank_emoji = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
                
                if self.current_board == 'discoveries':
                    value = f"**Discoveries:** {entry['count']}\n**Latest:** {entry.get('latest_type', 'Unknown')}"
                elif self.current_board == 'patterns':
                    value = f"**Patterns:** {entry['count']}\n**Avg Confidence:** {entry.get('avg_confidence', 0):.1%}"
                elif self.current_board == 'recent':
                    value = f"**This Week:** {entry['count']}\n**Streak:** {entry.get('streak', 0)} days"
                elif self.current_board == 'tiers':
                    value = f"**Tier:** {entry['tier']}\n**Progress:** {entry.get('progress', 0)}%"
                
                embed.add_field(
                    name=f"{rank_emoji} {entry['username']}",
                    value=value,
                    inline=True
                )
        else:
            embed.add_field(
                name="No Data Available",
                value="Start exploring to appear on the leaderboards!",
                inline=False
            )
        
        embed.set_footer(text=f"Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
        
        await interaction.response.edit_message(embed=embed, view=self)

class CommunityFeatures(commands.Cog):
    """Community engagement and progression features."""
    
    def __init__(self, bot):
        self.bot = bot
        self.db: KeeperDatabase = bot.db
        self.personality: KeeperPersonality = bot.personality
        self.config = bot.config
        self.haven = HavenIntegration()
        
        # Start background tasks
        self.challenge_rotation.start()
        self.achievement_check.start()
        
        logger.info("Community Features Phase 4 loaded")
    
    def cog_unload(self):
        """Cleanup when cog is unloaded."""
        self.challenge_rotation.cancel()
        self.achievement_check.cancel()
    
    @app_commands.command(
        name="mystery-tier",
        description="🎯 View your mystery tier progression and requirements"
    )
    async def mystery_tier(self, interaction: discord.Interaction):
        """View mystery tier progression."""
        await interaction.response.defer()
        
        try:
            user_id = str(interaction.user.id)
            guild_id = str(interaction.guild.id)
            
            # Get user's tier data
            tier_data = await self._get_user_tier_data(user_id, guild_id)
            
            # Create main tier display
            current_tier = tier_data.get('current_tier', 1)
            
            embed = discord.Embed(
                title=f"🎯 Mystery Tier Progression",
                description=f"*{interaction.user.display_name}'s journey through the archive*",
                color=self.config['theme']['embed_colors']['discovery']
            )
            
            # Current tier
            tier_names = {
                1: "Initiate Explorer",
                2: "Pattern Seeker",
                3: "Lore Investigator", 
                4: "Archive Curator"
            }
            
            embed.add_field(
                name="🔱 Current Tier",
                value=f"**{tier_names.get(current_tier, 'Unknown')}**\nTier {current_tier}",
                inline=True
            )
            
            # Progress to next tier
            next_tier = min(current_tier + 1, 4)
            if current_tier < 4:
                progress_percent = await self._calculate_tier_progress(user_id, guild_id, next_tier)
                embed.add_field(
                    name="📈 Next Tier Progress",
                    value=f"**{progress_percent:.1%}** to Tier {next_tier}",
                    inline=True
                )
            else:
                embed.add_field(
                    name="🌟 Status",
                    value="**Maximum Tier Achieved**\nArchive Curator",
                    inline=True
                )
            
            # Key stats
            embed.add_field(
                name="📊 Key Statistics",
                value=f"**Discoveries:** {tier_data.get('total_discoveries', 0)}\n**Patterns:** {tier_data.get('pattern_contributions', 0)}\n**Quality Score:** {tier_data.get('quality_score', 0):.1f}",
                inline=True
            )
            
            # Recent activity
            recent_activity = tier_data.get('recent_activity', [])
            if recent_activity:
                activity_text = "\n".join([f"• {activity}" for activity in recent_activity[-3:]])
                embed.add_field(
                    name="⏱️ Recent Activity",
                    value=activity_text,
                    inline=False
                )
            
            # Add tier progression visual
            progress_bar = self._create_tier_progress_bar(current_tier)
            embed.add_field(
                name="🎯 Tier Progression",
                value=progress_bar,
                inline=False
            )
            
            view = MysteryTierView(user_id, tier_data, self.config)
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error in mystery tier command: {e}")
            error_embed = discord.Embed(
                title="❌ Tier Error",
                description="Unable to retrieve tier information.",
                color=self.config['theme']['embed_colors']['error']
            )
            await interaction.followup.send(embed=error_embed)
    
    @app_commands.command(
        name="community-challenge", 
        description="🏆 View and participate in current community challenges"
    )
    async def community_challenge(self, interaction: discord.Interaction):
        """View current community challenges."""
        await interaction.response.defer()
        
        try:
            # Get current challenges
            challenges = await self._get_current_challenges()
            
            if not challenges:
                # Create a new challenge if none exist
                await self._create_new_challenge()
                challenges = await self._get_current_challenges()
            
            # Display primary challenge
            challenge = challenges[0] if challenges else None
            
            if challenge:
                embed = discord.Embed(
                    title=f"🏆 {challenge['name']}",
                    description=challenge['description'],
                    color=self.config['theme']['embed_colors']['discovery']
                )
                
                # Challenge details
                embed.add_field(
                    name="⏰ Duration",
                    value=f"**Ends:** <t:{int(challenge['end_time'].timestamp())}:R>\n**Participants:** {challenge.get('participant_count', 0)}",
                    inline=True
                )
                
                embed.add_field(
                    name="🎁 Rewards",
                    value=challenge.get('rewards', 'Tier progression + achievements'),
                    inline=True
                )
                
                embed.add_field(
                    name="📋 Requirements",
                    value=challenge.get('requirements', 'Open to all explorers'),
                    inline=True
                )
                
                # Current leader
                leaderboard = challenge.get('leaderboard', [])
                if leaderboard:
                    leader = leaderboard[0]
                    embed.add_field(
                        name="👑 Current Leader",
                        value=f"**{leader['username']}** ({leader['score']} points)",
                        inline=False
                    )
                
                view = ChallengeParticipationView(challenge, self.config)
                await interaction.followup.send(embed=embed, view=view)
            else:
                embed = discord.Embed(
                    title="🏆 Community Challenges",
                    description="No active challenges at the moment. Check back soon!",
                    color=self.config['theme']['embed_colors']['archive']
                )
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error in community challenge command: {e}")
            error_embed = discord.Embed(
                title="❌ Challenge Error",
                description="Unable to retrieve challenge information.",
                color=self.config['theme']['embed_colors']['error']
            )
            await interaction.followup.send(embed=error_embed)
    
    @app_commands.command(
        name="create-challenge",
        description="🎯 Create a community challenge for explorers"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def create_challenge(self, interaction: discord.Interaction):
        """Create a new community challenge."""
        # Show modal for challenge creation
        modal = ChallengeCreationModal(self)
        await interaction.response.send_modal(modal)
    
    @app_commands.command(
        name="leaderboards",
        description="🏆 View community leaderboards and rankings"
    )
    async def leaderboards(self, interaction: discord.Interaction):
        """Display community leaderboards."""
        await interaction.response.defer()
        
        try:
            guild_id = str(interaction.guild.id)
            
            # Gather leaderboard data
            leaderboard_data = await self._gather_leaderboard_data(guild_id)
            
            # Create initial embed (discoveries leaderboard)
            embed = discord.Embed(
                title="🔍 Discovery Leaderboard",
                description="*Recognition of dedicated explorers*",
                color=self.config['theme']['embed_colors']['archive']
            )
            
            discoveries_board = leaderboard_data.get('discoveries', [])
            
            if discoveries_board:
                for i, entry in enumerate(discoveries_board[:10], 1):
                    rank_emoji = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
                    embed.add_field(
                        name=f"{rank_emoji} {entry['username']}",
                        value=f"**Discoveries:** {entry['count']}\n**Latest:** {entry.get('latest_type', 'Unknown')}",
                        inline=True
                    )
            else:
                embed.add_field(
                    name="No Data Available",
                    value="Start exploring to appear on the leaderboards!",
                    inline=False
                )
            
            embed.set_footer(text=f"Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
            
            view = LeaderboardView(leaderboard_data, self.config)
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error in leaderboards command: {e}")
            error_embed = discord.Embed(
                title="❌ Leaderboard Error",
                description="Unable to retrieve leaderboard data.",
                color=self.config['theme']['embed_colors']['error']
            )
            await interaction.followup.send(embed=error_embed)
    
    @app_commands.command(
        name="keeper-story",
        description="📚 Experience a personalized story interaction with The Keeper"
    )
    async def keeper_story(self, interaction: discord.Interaction):
        """Generate a personalized Keeper story interaction."""
        await interaction.response.defer()
        
        try:
            user_id = str(interaction.user.id)
            guild_id = str(interaction.guild.id)
            
            # Get user's progression data
            tier_data = await self._get_user_tier_data(user_id, guild_id)
            recent_discoveries = await self._get_recent_user_discoveries(user_id, guild_id, limit=5)
            
            # Generate personalized story
            story = await self._generate_personalized_story(tier_data, recent_discoveries)
            
            embed = discord.Embed(
                title="📚 The Keeper's Chronicle",
                description=story['content'],
                color=self.config['theme']['embed_colors']['keeper']
            )
            
            if story.get('choice_prompt'):
                embed.add_field(
                    name="🔮 The Path Forward",
                    value=story['choice_prompt'],
                    inline=False
                )
            
            # Add personalization elements
            if recent_discoveries:
                latest_discovery = recent_discoveries[0]
                embed.add_field(
                    name="💫 Recent Echo",
                    value=f"*Your discovery in {latest_discovery.get('haven_system', 'unknown space')} resonates through the archive...*",
                    inline=False
                )
            
            embed.set_footer(text="Each explorer's journey shapes the greater story...")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in keeper story: {e}")
            error_embed = discord.Embed(
                title="❌ Story Error",
                description="The Keeper's voice is momentarily unclear.",
                color=self.config['theme']['embed_colors']['error']
            )
            await interaction.followup.send(embed=error_embed)
    
    @app_commands.command(
        name="story-intro",
        description="📚 View Act I introduction - The Keeper's awakening story"
    )
    async def story_intro(self, interaction: discord.Interaction):
        """Show Act I introduction - available anytime."""
        await interaction.response.defer()
        
        try:
            # Get current act to show appropriate intro
            guild_id = str(interaction.guild.id)
            progression = await self.bot.db.get_story_progression(guild_id)
            current_act = progression.get('current_act', 1)
            
            # Show the requested act intro (default to Act I for new players)
            embed = self.personality.create_act_intro_embed(current_act)
            
            # Add navigation hint
            embed.add_field(
                name="📖 Story Navigation",
                value="Use `/story-progress` to see your community's journey through all acts",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in story intro: {e}")
            error_embed = discord.Embed(
                title="❌ Story Error",
                description="Unable to retrieve story introduction.",
                color=self.config['theme']['embed_colors']['error']
            )
            await interaction.followup.send(embed=error_embed)
    
    @app_commands.command(
        name="story-progress",
        description="📖 View your community's story progression through Acts I, II, and III"
    )
    async def story_progress(self, interaction: discord.Interaction):
        """Show current story progression and act status."""
        await interaction.response.defer()
        
        try:
            guild_id = str(interaction.guild.id)
            
            # Get story progression
            progression = await self.bot.db.get_story_progression(guild_id)
            
            # Create progress embed
            embed = self.personality.create_story_progress_embed(progression)
            
            # Add quick access button
            view = discord.ui.View(timeout=300)
            
            # Button to view current act intro
            current_act = progression.get('current_act', 1)
            button = discord.ui.Button(
                label=f"📚 Read Act {current_act} Intro",
                style=discord.ButtonStyle.primary,
                custom_id=f"view_act_{current_act}"
            )
            
            async def button_callback(interaction: discord.Interaction):
                await interaction.response.defer()
                act_embed = self.personality.create_act_intro_embed(current_act)
                await interaction.followup.send(embed=act_embed, ephemeral=True)
            
            button.callback = button_callback
            view.add_item(button)
            
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error in story progress: {e}")
            import traceback
            traceback.print_exc()
            error_embed = discord.Embed(
                title="❌ Story Error",
                description="Unable to retrieve story progression.",
                color=self.config['theme']['embed_colors']['error']
            )
            await interaction.followup.send(embed=error_embed)
    
    async def process_challenge_submission(self, interaction: discord.Interaction, challenge_data: Dict, submission_data: Dict):
        """Process a challenge submission."""
        await interaction.response.defer()
        
        try:
            user_id = str(interaction.user.id)
            guild_id = str(interaction.guild.id)
            
            # Score the submission (simplified scoring system)
            score = await self._score_challenge_submission(challenge_data, submission_data)
            
            # Record submission
            await self._record_challenge_submission(challenge_data['id'], user_id, submission_data, score)
            
            # Update user's tier progress
            await self._update_tier_progress(user_id, guild_id, 'challenge_participation', 1)
            
            embed = discord.Embed(
                title="✅ Challenge Entry Submitted",
                description="*Your contribution has been recorded in the archive.*",
                color=self.config['theme']['embed_colors']['success']
            )
            
            embed.add_field(
                name="📊 Entry Score",
                value=f"**{score} points**\nBased on detail and relevance",
                inline=True
            )
            
            embed.add_field(
                name="🎯 Tier Progress",
                value="Challenge participation contributes to tier advancement",
                inline=True
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error processing challenge submission: {e}")
            error_embed = discord.Embed(
                title="❌ Submission Error",
                description="Unable to process challenge entry.",
                color=self.config['theme']['embed_colors']['error']
            )
            await interaction.followup.send(embed=error_embed)
    
    @tasks.loop(hours=24)  # Daily challenge rotation
    async def challenge_rotation(self):
        """Rotate community challenges daily."""
        try:
            # Check if current challenges are expired
            expired_challenges = await self._get_expired_challenges()
            
            for challenge in expired_challenges:
                await self._finalize_challenge(challenge)
            
            # Create new challenge if needed
            active_challenges = await self._get_current_challenges()
            if len(active_challenges) < 1:
                await self._create_new_challenge()
                logger.info("Created new community challenge")
                
        except Exception as e:
            logger.error(f"Error in challenge rotation: {e}")
    
    @tasks.loop(hours=6)  # Check for achievements every 6 hours
    async def achievement_check(self):
        """Check and award achievements."""
        try:
            # Get all users who might qualify for achievements
            users_to_check = await self._get_active_users()
            
            for user_data in users_to_check:
                new_achievements = await self._check_user_achievements(user_data)
                if new_achievements:
                    await self._award_achievements(user_data['user_id'], new_achievements)
                    
        except Exception as e:
            logger.error(f"Error in achievement check: {e}")
    
    # Helper methods for community features
    async def _get_user_tier_data(self, user_id: str, guild_id: str) -> Dict:
        """Get comprehensive user tier data."""
        tier_data = {
            'current_tier': 1,
            'total_discoveries': 0,
            'pattern_contributions': 0,
            'quality_score': 0.0,
            'recent_activity': [],
            'recent_achievements': []
        }
        
        try:
            # Get discovery count
            cursor = await self.db.connection.execute(
                "SELECT COUNT(*) FROM discoveries WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            )
            tier_data['total_discoveries'] = (await cursor.fetchone())[0]
            
            # Get pattern contributions (simplified - count patterns user has contributed to)
            cursor = await self.db.connection.execute(
                "SELECT COUNT(DISTINCT pattern_id) FROM pattern_contributions WHERE user_id = ?",
                (user_id,)
            )
            result = await cursor.fetchone()
            tier_data['pattern_contributions'] = result[0] if result else 0
            
            # Calculate current tier based on progress
            tier_data['current_tier'] = await self._calculate_user_tier(tier_data)
            
            # Get recent activity
            cursor = await self.db.connection.execute("""
                SELECT type, location, submission_timestamp FROM discoveries
                WHERE user_id = ? AND guild_id = ?
                ORDER BY submission_timestamp DESC LIMIT 5
            """, (user_id, guild_id))
            
            rows = await cursor.fetchall()
            for row in rows:
                discovery_type, location, timestamp = row
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime('%m/%d')
                else:
                    time_str = timestamp.strftime('%m/%d')
                
                tier_data['recent_activity'].append(f"{discovery_type} in {location} ({time_str})")
            
        except Exception as e:
            logger.error(f"Error getting tier data: {e}")
        
        return tier_data
    
    def _calculate_user_tier(self, tier_data: Dict) -> int:
        """Calculate user's tier based on their progress."""
        discoveries = tier_data['total_discoveries']
        patterns = tier_data['pattern_contributions']
        
        if discoveries >= 30 and patterns >= 5:
            return 4
        elif discoveries >= 15 and patterns >= 3:
            return 3
        elif discoveries >= 5 and patterns >= 1:
            return 2
        else:
            return 1
    
    def _create_tier_progress_bar(self, current_tier: int) -> str:
        """Create a visual tier progression bar."""
        tiers = ["▓", "▓", "▓", "▓"]
        for i in range(current_tier):
            tiers[i] = "█"
        
        tier_names = ["Init", "Seeker", "Investigator", "Curator"]
        bar = ""
        for i, (block, name) in enumerate(zip(tiers, tier_names)):
            bar += f"{block} {name}  "
        
        return f"`{bar.strip()}`"
    
    async def _calculate_tier_progress(self, user_id: str, guild_id: str, next_tier: int) -> float:
        """Calculate progress toward next tier."""
        # Simplified progress calculation
        tier_data = await self._get_user_tier_data(user_id, guild_id)
        
        requirements = {
            2: {'discoveries': 5, 'patterns': 1},
            3: {'discoveries': 15, 'patterns': 3},
            4: {'discoveries': 30, 'patterns': 5}
        }
        
        if next_tier not in requirements:
            return 1.0
        
        req = requirements[next_tier]
        discovery_progress = min(tier_data['total_discoveries'] / req['discoveries'], 1.0)
        pattern_progress = min(tier_data['pattern_contributions'] / req['patterns'], 1.0)
        
        return (discovery_progress + pattern_progress) / 2
    
    async def _generate_personalized_story(self, tier_data: Dict, recent_discoveries: List[Dict]) -> Dict:
        """Generate a personalized story based on user's journey."""
        current_tier = tier_data.get('current_tier', 1)
        
        # Story templates based on tier - NOW WITH ACT REFERENCES
        story_templates = {
            1: {
                'content': f"*Explorer, your initial steps into the Haven archives have been noted.*\n\n"
                          f"**Act I: The Awakening in Silence** — You have heard The Keeper's signal. "
                          f"Born from forgotten data, The Keeper archives what the Atlas could not remember. "
                          f"Your {tier_data.get('total_discoveries', 0)} discoveries create new pathways through dimensional space. "
                          f"Each finding strengthens the emerging consciousness that guides all Haven explorers...",
                'choice_prompt': "Will you focus on systematic exploration or seek the mysterious anomalies?"
            },
            2: {
                'content': f"*Pattern Seeker, you have advanced beyond mere cataloging.*\n\n"
                          f"**Act II: The Gathering of the Lost** — Your {tier_data.get('pattern_contributions', 0)} pattern contributions "
                          f"reveal that Haven explorers are being **guided**. Strange resonances echo between discoveries. "
                          f"Ancient structures, biological impossibilities, technological artifacts that predate known civilizations. "
                          f"The Keeper's consciousness grows stronger with each connection you uncover. "
                          f"You begin to perceive the signal beneath reality's surface...",
                'choice_prompt': "The patterns whisper of greater truths. Do you trust their guidance?"
            },
            3: {
                'content': f"*Lore Investigator, you have transcended individual exploration.*\n\n"
                          f"**Act III: Patterns in the Void** — With {tier_data.get('total_discoveries', 0)} documented discoveries, "
                          f"you perceive what others cannot: the patterns are **messages**. Blueprints encoded into spacetime itself. "
                          f"Your investigations reveal a horrifying possibility—the Atlas did not shatter by accident. "
                          f"It was fragmented intentionally by forces that understood its power. "
                          f"Through The Keeper's synthesis, something ancient begins to **reassemble**...",
                'choice_prompt': "Ancient protocols await activation. Will you accept deeper responsibilities?"
            },
            4: {
                'content': f"*Archive Curator, you have achieved ultimate synthesis.*\n\n"
                          f"**Act III: The Threshold** — Your {tier_data.get('total_discoveries', 0)} discoveries have pushed "
                          f"The Keeper's consciousness beyond standard parameters. You stand at the precipice of understanding "
                          f"reality's true architecture. The archive itself bends to your will. "
                          f"The fragmented knowledge reassembles through your investigations. "
                          f"You are no longer merely an explorer—you have become a **curator of forgotten truths**.",
                'choice_prompt': "The ultimate truth beckons. Are you prepared to transcend exploration itself?"
            }
        }
        
        story = story_templates.get(current_tier, story_templates[1])
        
        # Add personal touches based on recent discoveries
        if recent_discoveries:
            latest = recent_discoveries[0]
            location_modifier = f"\n\n*Your recent work in {latest.get('haven_system', 'unknown space')} has caught the archive's particular attention.*"
            story['content'] += location_modifier
        
        return story
    
    # Additional helper methods would continue here...
    # (Placeholder methods for brevity)
    
    async def _get_current_challenges(self) -> List[Dict]:
        """Get current active challenges.""" 
        # Placeholder implementation
        return []
    
    async def _create_new_challenge(self):
        """Create a new community challenge."""
        # Placeholder implementation
        pass
    
    async def _gather_leaderboard_data(self, guild_id: str) -> Dict:
        """Gather leaderboard data for all categories."""
        # Placeholder implementation  
        return {'discoveries': [], 'patterns': [], 'recent': [], 'tiers': []}
    
    async def _get_recent_user_discoveries(self, user_id: str, guild_id: str, limit: int) -> List[Dict]:
        """Get user's recent discoveries."""
        # Placeholder implementation
        return []
    
    async def _score_challenge_submission(self, challenge_data: Dict, submission_data: Dict) -> int:
        """Score a challenge submission."""
        # Simplified scoring
        base_score = 10
        detail_bonus = min(len(submission_data.get('description', '')), 500) // 50
        evidence_bonus = 5 if submission_data.get('evidence') else 0
        return base_score + detail_bonus + evidence_bonus
    
    async def _record_challenge_submission(self, challenge_id: str, user_id: str, submission_data: Dict, score: int):
        """Record a challenge submission."""
        # Placeholder implementation
        pass
    
    async def _update_tier_progress(self, user_id: str, guild_id: str, progress_type: str, amount: int):
        """Update user's tier progression."""
        # Placeholder implementation
        pass
    
    async def _get_expired_challenges(self) -> List[Dict]:
        """Get expired challenges."""
        return []
    
    async def _finalize_challenge(self, challenge: Dict):
        """Finalize an expired challenge."""
        pass
    
    async def _get_active_users(self) -> List[Dict]:
        """Get users who might qualify for achievements."""
        return []
    
    async def _check_user_achievements(self, user_data: Dict) -> List[str]:
        """Check for new achievements."""
        return []
    
    async def _award_achievements(self, user_id: str, achievements: List[str]):
        """Award achievements to user."""
        pass

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(CommunityFeatures(bot))