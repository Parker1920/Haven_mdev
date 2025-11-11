"""
Pattern Recognition System - Phase 2
Semi-automated detection of patterns across discoveries with Haven integration.
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import json

from core.keeper_personality import KeeperPersonality
from database.keeper_db import KeeperDatabase
from core.haven_integration import HavenIntegration
from core.channel_config import ChannelConfig

logger = logging.getLogger('keeper.pattern_recognition')

class PatternRecognition(commands.Cog):
    """Handles pattern detection and investigation thread management."""
    
    def __init__(self, bot):
        self.bot = bot
        self.db: KeeperDatabase = bot.db
        self.personality: KeeperPersonality = bot.personality
        self.config = bot.config
        self.haven = HavenIntegration()
        self.channel_config = ChannelConfig(bot)
        
        # Pattern detection settings
        self.min_discoveries_for_pattern = 3
        self.pattern_confidence_threshold = 0.6
        self.regional_pattern_weight = 1.5  # Boost for same region patterns
        
        # Start Haven data loading
        self.bot.loop.create_task(self._initialize_haven())
    
    async def _initialize_haven(self):
        """Initialize Haven integration."""
        await self.haven.load_haven_data()
    
    async def analyze_for_patterns(self, discovery_id: int) -> Optional[Dict]:
        """Analyze a new discovery for patterns."""
        try:
            # Get the new discovery
            discovery = await self.db.get_discovery(discovery_id)
            if not discovery:
                return None
            
            # Find similar discoveries
            similar_discoveries = await self.db.find_similar_discoveries(discovery_id)
            
            if len(similar_discoveries) < self.min_discoveries_for_pattern - 1:
                logger.info(f"Discovery {discovery_id}: Not enough similar discoveries for pattern ({len(similar_discoveries)})")
                return None
            
            # Calculate pattern strength
            pattern_analysis = await self._analyze_pattern_strength(discovery, similar_discoveries)
            
            if pattern_analysis['confidence'] >= self.pattern_confidence_threshold:
                # Create or update pattern
                pattern = await self._create_or_update_pattern(discovery, similar_discoveries, pattern_analysis)
                
                # Check if this triggers a new investigation
                if pattern and pattern['discovery_count'] >= self.min_discoveries_for_pattern:
                    await self._trigger_investigation_check(pattern)
                
                return pattern
            
            logger.info(f"Discovery {discovery_id}: Pattern confidence below threshold ({pattern_analysis['confidence']:.2f})")
            return None
            
        except Exception as e:
            logger.error(f"Error in pattern analysis for discovery {discovery_id}: {e}")
            return None
    
    async def _analyze_pattern_strength(self, discovery: Dict, similar_discoveries: List[Dict]) -> Dict:
        """Analyze the strength of a potential pattern."""
        analysis = {
            'confidence': 0.0,
            'pattern_type': 'discovery_cluster',
            'regional_coherence': 0.0,
            'temporal_coherence': 0.0,
            'type_coherence': 0.0,
            'location_coherence': 0.0,
            'narrative_coherence': 0.0
        }
        
        all_discoveries = [discovery] + similar_discoveries
        
        # Type coherence - same discovery types
        discovery_types = [d['type'] for d in all_discoveries]
        type_matches = discovery_types.count(discovery['type'])
        analysis['type_coherence'] = type_matches / len(all_discoveries)
        
        # Regional coherence - discoveries in same galactic region
        if hasattr(self.haven, 'haven_data') and self.haven.haven_data:
            regional_matches = await self._calculate_regional_coherence(all_discoveries)
            analysis['regional_coherence'] = regional_matches
        
        # Temporal coherence - discoveries within time window
        analysis['temporal_coherence'] = self._calculate_temporal_coherence(all_discoveries)
        
        # Location coherence - same systems or nearby systems  
        analysis['location_coherence'] = self._calculate_location_coherence(all_discoveries)
        
        # Narrative coherence - similar descriptions, keywords
        analysis['narrative_coherence'] = self._calculate_narrative_coherence(all_discoveries)
        
        # Calculate overall confidence
        weights = {
            'type_coherence': 0.3,
            'regional_coherence': 0.25,
            'temporal_coherence': 0.15,
            'location_coherence': 0.2,
            'narrative_coherence': 0.1
        }
        
        analysis['confidence'] = sum(
            analysis[key] * weight for key, weight in weights.items()
        )
        
        # Boost regional patterns as per requirements
        if analysis['regional_coherence'] > 0.7:
            analysis['confidence'] *= self.regional_pattern_weight
            analysis['pattern_type'] = 'regional_pattern'
        
        logger.info(f"Pattern analysis: {analysis['confidence']:.2f} confidence, type: {analysis['pattern_type']}")
        return analysis
    
    async def _calculate_regional_coherence(self, discoveries: List[Dict]) -> float:
        """Calculate how many discoveries are in the same galactic region."""
        if not discoveries:
            return 0.0
        
        # Get regions for each discovery
        regions = []
        for discovery in discoveries:
            planet_name = discovery.get('planet_name') or ''
            system_name = discovery.get('system_name') or (planet_name.split()[0] if planet_name else None)
            if system_name:
                system_data = self.haven.get_system(system_name)
                if system_data:
                    regions.append(system_data.get('region', 'Unknown'))
                else:
                    regions.append('Unknown')
            else:
                regions.append('Unknown')
        
        if not regions:
            return 0.0
        
        # Find most common region
        region_counts = {}
        for region in regions:
            region_counts[region] = region_counts.get(region, 0) + 1
        
        most_common_count = max(region_counts.values())
        return most_common_count / len(regions)
    
    def _calculate_temporal_coherence(self, discoveries: List[Dict]) -> float:
        """Calculate temporal clustering of discoveries."""
        if len(discoveries) < 2:
            return 1.0
        
        timestamps = []
        for discovery in discoveries:
            timestamp = discovery.get('submission_timestamp')
            if timestamp:
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                timestamps.append(timestamp)
        
        if len(timestamps) < 2:
            return 0.5
        
        # Calculate time span
        timestamps.sort()
        time_span = timestamps[-1] - timestamps[0]
        
        # Higher coherence for discoveries within shorter time spans
        # 1 week = high coherence, 1 month = medium, 3+ months = low
        days = time_span.days
        if days <= 7:
            return 1.0
        elif days <= 30:
            return 0.7
        elif days <= 90:
            return 0.4
        else:
            return 0.1
    
    def _calculate_location_coherence(self, discoveries: List[Dict]) -> float:
        """Calculate spatial clustering of discoveries."""
        if len(discoveries) < 2:
            return 1.0
        
        # Group by system/planet
        locations = {}
        for discovery in discoveries:
            system = discovery.get('system_name', 'Unknown')
            planet = discovery.get('location_name', 'Unknown') 
            location_key = f"{system}:{planet}"
            locations[location_key] = locations.get(location_key, 0) + 1
        
        # Higher coherence if discoveries are clustered in fewer locations
        total_discoveries = len(discoveries)
        unique_locations = len(locations)
        
        return 1.0 - (unique_locations / total_discoveries)
    
    def _calculate_narrative_coherence(self, discoveries: List[Dict]) -> float:
        """Calculate narrative/thematic similarity between discoveries."""
        if len(discoveries) < 2:
            return 1.0
        
        # Simple keyword matching approach
        # In production, this could use more sophisticated NLP
        keywords_lists = []
        for discovery in discoveries:
            description = (discovery.get('description') or '').lower()
            significance = (discovery.get('significance') or '').lower()
            text = f"{description} {significance}"
            
            # Extract meaningful words (simple approach)
            words = text.split()
            meaningful_words = [w for w in words if len(w) > 3 and w.isalpha()]
            keywords_lists.append(set(meaningful_words))
        
        if not keywords_lists:
            return 0.0
        
        # Calculate average pairwise similarity
        total_similarity = 0.0
        comparisons = 0
        
        for i in range(len(keywords_lists)):
            for j in range(i + 1, len(keywords_lists)):
                set1, set2 = keywords_lists[i], keywords_lists[j]
                if set1 or set2:
                    similarity = len(set1.intersection(set2)) / len(set1.union(set2))
                    total_similarity += similarity
                    comparisons += 1
        
        return total_similarity / comparisons if comparisons > 0 else 0.0
    
    async def _create_or_update_pattern(self, discovery: Dict, similar_discoveries: List[Dict], 
                                      analysis: Dict) -> Optional[Dict]:
        """Create a new pattern or update existing one."""
        try:
            # Check if a pattern already exists for this type/region combination
            discovery_type = discovery['type']
            region = 'Unknown'
            
            system_name = discovery.get('system_name')
            if system_name:
                system_data = self.haven.get_system(system_name)
                if system_data:
                    region = system_data.get('region', 'Unknown')
            
            # Generate pattern name
            pattern_name = self._generate_pattern_name(discovery_type, region, analysis)
            
            # Create pattern data
            pattern_data = {
                'name': pattern_name,
                'type': analysis['pattern_type'],
                'discovery_count': len(similar_discoveries) + 1,
                'confidence': analysis['confidence'],
                'mystery_tier': self._calculate_mystery_tier(analysis),
                'description': self._generate_pattern_description(discovery, similar_discoveries, analysis),
                'metadata': {
                    'discovery_type': discovery_type,
                    'region': region,
                    'analysis': analysis,
                    'trigger_discovery_id': discovery['id']
                }
            }
            
            # Save pattern
            pattern_id = await self.db.create_pattern(pattern_data)
            
            # Update story progression - increment pattern count
            guild_id = str(discovery['guild_id']) if discovery.get('guild_id') else None
            if guild_id:
                await self.db.increment_story_stats(guild_id, 'patterns', 1)
            
            # Associate all discoveries with this pattern
            all_discoveries = [discovery] + similar_discoveries
            for disc in all_discoveries:
                correlation_strength = self._calculate_correlation_strength(disc, analysis)
                await self.db.add_discovery_to_pattern(pattern_id, disc['id'], correlation_strength)
            
            # Get the complete pattern data
            pattern_data['id'] = pattern_id
            
            logger.info(f"Pattern {pattern_id} created: {pattern_name}")
            return pattern_data
            
        except Exception as e:
            logger.error(f"Error creating pattern: {e}")
            return None
    
    def _generate_pattern_name(self, discovery_type: str, region: str, analysis: Dict) -> str:
        """Generate a descriptive pattern name."""
        type_names = {
            '🦴': 'Ancient Remains',
            '📜': 'Textual Echoes', 
            '🏛️': 'Structural Anomalies',
            '⚙️': 'Technology Signatures',
            '🦗': 'Biological Patterns',
            '💎': 'Geological Formations',
            '🚀': 'Wreckage Clusters',
            '⚡': 'Environmental Phenomena',
            '🆕': 'Temporal Variances',
            '📖': 'Consciousness Fragments'
        }
        
        base_name = type_names.get(discovery_type, 'Unknown Phenomena')
        
        if analysis['pattern_type'] == 'regional_pattern':
            return f"{region} {base_name}"
        else:
            return f"Cross-Regional {base_name}"
    
    def _calculate_mystery_tier(self, analysis: Dict) -> int:
        """Calculate the mystery tier based on pattern strength."""
        confidence = analysis['confidence']
        
        if confidence >= 0.9:
            return 4  # Cosmic Significance
        elif confidence >= 0.8:
            return 3  # Deep Mystery
        elif confidence >= 0.7:
            return 2  # Pattern Emergence
        else:
            return 1  # Surface Anomaly
    
    def _generate_pattern_description(self, discovery: Dict, similar_discoveries: List[Dict], 
                                    analysis: Dict) -> str:
        """Generate a narrative description of the pattern."""
        total_count = len(similar_discoveries) + 1
        discovery_type = discovery['type']
        
        descriptions = {
            '🦴': f"Archaeological evidence suggests a civilization that once thrived across multiple systems. {total_count} fossilized remains have been catalogued, displaying consistent genetic markers that transcend natural evolutionary patterns.",
            
            '📜': f"A series of {total_count} textual fragments have emerged across different worlds, each bearing linguistic signatures that suggest a coordinated communication network. The messages appear to be connected by underlying protocols.",
            
            '🏛️': f"Structural anomalies detected across {total_count} locations reveal architectural principles beyond current understanding. The geometric relationships suggest these ruins serve purposes not yet comprehended.",
            
            '⚙️': f"Technological artifacts numbering {total_count} have been recovered, each displaying quantum signatures that resonate with a common source frequency. The devices appear to be components of a larger mechanism.",
            
            '🦗': f"Biological specimens from {total_count} separate ecosystems show evidence of coordinated genetic modification. The organisms display traits that could not have evolved independently.",
            
            'default': f"Pattern analysis has identified {total_count} related discoveries that exceed the probability of random occurrence. The connections suggest intentional design or external influence."
        }
        
        base_description = descriptions.get(discovery_type, descriptions['default'])
        
        # Add regional context if applicable
        if analysis['regional_coherence'] > 0.7:
            base_description += f"\n\nRegional analysis indicates this pattern is concentrated within a specific galactic sector, suggesting localized influence or containment."
        
        # Add confidence qualifier
        confidence_level = analysis['confidence']
        if confidence_level > 0.9:
            base_description += "\n\n**The Keeper's assessment: Cosmic significance confirmed.**"
        elif confidence_level > 0.8:
            base_description += "\n\n**The Keeper's assessment: Deep mystery requiring immediate investigation.**"
        else:
            base_description += "\n\n**The Keeper's assessment: Pattern emergence detected. Continued monitoring essential.**"
        
        return base_description
    
    def _calculate_correlation_strength(self, discovery: Dict, analysis: Dict) -> float:
        """Calculate how strongly a discovery correlates with the pattern."""
        # This is a simplified calculation - could be enhanced with ML in the future
        base_strength = analysis['confidence']
        
        # Boost for exact type matches
        if analysis.get('type_coherence', 0) > 0.8:
            base_strength *= 1.2
        
        # Boost for regional matches
        if analysis.get('regional_coherence', 0) > 0.7:
            base_strength *= 1.1
        
        return min(1.0, base_strength)
    
    async def _trigger_investigation_check(self, pattern: Dict):
        """Check if a pattern should trigger a new investigation thread."""
        try:
            # Check if investigation already exists
            cursor = await self.db.connection.execute(
                "SELECT * FROM investigations WHERE pattern_id = ?",
                (pattern['id'],)
            )
            existing = await cursor.fetchone()
            
            if existing:
                logger.info(f"Investigation already exists for pattern {pattern['id']}")
                return
            
            # Post pattern alert to archive channel and create thread
            thread = await self._post_pattern_alert(pattern)
            
            # Create investigation thread if pattern alert was posted
            if thread:
                await self._create_investigation_thread(pattern, thread)
                logger.info(f"✅ Investigation thread created for pattern {pattern['id']}")
            else:
                logger.info(f"Pattern {pattern['id']} ready for investigation thread creation")
            
        except Exception as e:
            logger.error(f"Error in investigation trigger: {e}")
    
    async def _post_pattern_alert(self, pattern: Dict):
        """Post a pattern recognition alert to the archive channel. Returns the message if successful."""
        try:
            # Find a guild to post to
            guild = None
            for g in self.bot.guilds:
                if await self.channel_config.is_configured(g):
                    guild = g
                    break
            
            if not guild:
                logger.warning("No configured guild found for pattern alert")
                return None
            
            # Get archive channel using centralized config
            archive_channel = await self.channel_config.get_archive_channel(guild)
            
            if not archive_channel:
                logger.warning("Archive channel not found")
                return None
            
            # Create pattern alert embed
            pattern_embed = self.personality.create_pattern_alert({
                'count': pattern['discovery_count'],
                'confidence': pattern['confidence'],
                'type': pattern['type'],
                'name': pattern['name'],
                'description': pattern['description'],
                'mystery_tier': pattern['mystery_tier']
            })
            
            # Post the alert
            message = await archive_channel.send(embed=pattern_embed)
            
            # Save archive entry
            await self.db.connection.execute("""
                INSERT INTO archive_entries (
                    entry_id, entry_type, title, content,
                    channel_id, message_id, embed_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                f"PATTERN_{pattern['id']:06d}",
                "pattern_alert",
                pattern_embed.title,
                pattern_embed.description,
                str(archive_channel.id),
                str(message.id),
                json.dumps(pattern_embed.to_dict())  # Convert dict to JSON string
            ))
            await self.db.connection.commit()
            
            logger.info(f"Pattern alert posted for pattern {pattern['id']}")
            return message
            
        except Exception as e:
            logger.error(f"Error posting pattern alert: {e}")
            return None
    
    async def _create_investigation_thread(self, pattern: Dict, alert_message: discord.Message):
        """Create an investigation thread for a pattern."""
        try:
            # Create thread from the pattern alert message
            thread_name = f"🔍 {pattern['name']}"
            thread = await alert_message.create_thread(
                name=thread_name[:100],  # Discord limit
                auto_archive_duration=10080  # 7 days
            )
            
            # Post initial investigation message (enhanced template from master file)
            investigation_embed = discord.Embed(
                title="🔍 INVESTIGATION THREAD OPENED",
                description="*The pattern requires field work. Collective intelligence activated.*",
                color=self.config['theme']['embed_colors']['pattern']
            )
            
            # Pattern Matrix
            investigation_embed.add_field(
                name="📊 Pattern Matrix",
                value=f"```yaml\nConfidence: {pattern['confidence']:.1%}\nSimilar Discoveries: {pattern['discovery_count']}\nPrimary Region: {pattern.get('metadata', {}).get('region', 'Unknown')}\nDiscovery Type: {pattern.get('metadata', {}).get('discovery_type', 'Unknown')}\n```",
                inline=False
            )
            
            # Significance Assessment
            investigation_embed.add_field(
                name="🔮 Significance Assessment",
                value=f"*The pattern solidifies across multiple dimensional echoes. This is no mere coincidence—intelligence is at work. "
                      f"{pattern['discovery_count']} separate explorers have uncovered evidence. "
                      f"The Archive detects intentional design in these discoveries.*",
                inline=False
            )
            
            # Investigation Phase
            investigation_embed.add_field(
                name="🎯 PHASE 1: HYPOTHESIS SUBMISSION",
                value="Explorers are invited to submit theories explaining the pattern connections.\n\n"
                      "**What do these discoveries reveal? Why are they appearing together?**\n\n"
                      "*The Archive awaits your insights.*",
                inline=False
            )
            
            investigation_embed.set_footer(text="— Archive Protocol Active")
            
            await thread.send(embed=investigation_embed)
            
            # Create investigation record in database
            await self.db.connection.execute("""
                INSERT INTO investigations (
                    pattern_id, status, thread_id, created_at
                ) VALUES (?, ?, ?, ?)
            """, (
                pattern['id'],
                'active',
                str(thread.id),
                datetime.utcnow()
            ))
            await self.db.connection.commit()
            
            logger.info(f"🧵 Investigation thread {thread.id} created for pattern {pattern['id']}")
            
        except Exception as e:
            logger.error(f"Error creating investigation thread: {e}")
    
    @app_commands.command(
        name="pattern-analysis",
        description="🌀 Manually trigger pattern analysis"
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(discovery_id="Discovery ID to analyze for patterns")
    async def manual_pattern_analysis(self, interaction: discord.Interaction, discovery_id: int):
        """Manually trigger pattern analysis for testing."""
        await interaction.response.defer()
        
        try:
            pattern = await self.analyze_for_patterns(discovery_id)
            
            if pattern:
                embed = discord.Embed(
                    title="🌀 Pattern Analysis Complete",
                    description=f"Pattern detected and catalogued: **{pattern['name']}**",
                    color=self.config['theme']['embed_colors']['pattern']
                )
                
                embed.add_field(
                    name="📊 Pattern Statistics",
                    value=f"**Discoveries:** {pattern['discovery_count']}\n**Confidence:** {pattern['confidence']:.1%}\n**Mystery Tier:** {pattern['mystery_tier']}",
                    inline=False
                )
                
                embed.add_field(
                    name="🔮 Assessment",
                    value=pattern['description'][:500] + ("..." if len(pattern['description']) > 500 else ""),
                    inline=False
                )
            else:
                embed = discord.Embed(
                    title="🔍 Pattern Analysis Complete",
                    description="No significant patterns detected for this discovery.",
                    color=self.config['theme']['embed_colors']['warning']
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in manual pattern analysis: {e}")
            error_embed = discord.Embed(
                title="❌ Analysis Error",
                description="Pattern analysis encountered an error.",
                color=self.config['theme']['embed_colors']['error']
            )
            await interaction.followup.send(embed=error_embed)
    
    @app_commands.command(
        name="view-patterns",
        description="📊 View detected patterns by mystery tier"
    )
    @app_commands.describe(tier="Mystery tier to filter by (1-4)")
    async def view_patterns(self, interaction: discord.Interaction, tier: Optional[int] = None):
        """View patterns by mystery tier."""
        await interaction.response.defer()
        
        try:
            if tier:
                patterns = await self.db.get_patterns_by_tier(tier)
                title = f"🌀 Mystery Tier {tier} Patterns"
            else:
                # Get all patterns and group by tier
                all_patterns = {}
                for t in range(1, 5):
                    tier_patterns = await self.db.get_patterns_by_tier(t)
                    if tier_patterns:
                        all_patterns[t] = tier_patterns
                
                embed = discord.Embed(
                    title="🌀 All Detected Patterns",
                    description="*The Keeper's pattern recognition archives*",
                    color=self.config['theme']['embed_colors']['archive']
                )
                
                for tier_num, tier_patterns in all_patterns.items():
                    tier_names = self.config['mystery_tiers'][str(tier_num)]
                    pattern_list = "\n".join([f"• {p['name']} ({p['discovery_count']} discoveries)" for p in tier_patterns[:5]])
                    if len(tier_patterns) > 5:
                        pattern_list += f"\n• ... and {len(tier_patterns) - 5} more"
                    
                    embed.add_field(
                        name=f"Tier {tier_num}: {tier_names['name']}",
                        value=pattern_list or "No patterns detected",
                        inline=False
                    )
                
                await interaction.followup.send(embed=embed)
                return
            
            if not patterns:
                embed = discord.Embed(
                    title=title,
                    description="*No patterns detected at this tier.*",
                    color=self.config['theme']['embed_colors']['warning']
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title=title,
                description=f"*{len(patterns)} patterns detected*",
                color=self.config['theme']['embed_colors']['pattern']
            )
            
            for pattern in patterns[:10]:  # Limit to 10 patterns
                embed.add_field(
                    name=f"🌀 {pattern['name']}",
                    value=f"**Discoveries:** {pattern['discovery_count']}\n**Confidence:** {pattern.get('confidence', 0):.1%}\n**Status:** {pattern.get('status', 'Active')}",
                    inline=True
                )
            
            if len(patterns) > 10:
                embed.set_footer(text=f"Showing 10 of {len(patterns)} patterns")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error viewing patterns: {e}")
            error_embed = discord.Embed(
                title="❌ Archive Error",
                description="Unable to access pattern archives.",
                color=self.config['theme']['embed_colors']['error']
            )
            await interaction.followup.send(embed=error_embed)

async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(PatternRecognition(bot))