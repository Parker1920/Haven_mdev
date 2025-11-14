"""
The Keeper Database System
Handles persistent storage of discoveries, patterns, and investigations.
"""

import aiosqlite
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os

logger = logging.getLogger('keeper.database')

class KeeperDatabase:
    """Main database interface for The Keeper."""
    
    def __init__(self, db_path: str = "../data/keeper.db"):
        """Initialize with path relative to src/ directory pointing to docs/guides/Haven-lore/keeper-bot/data/keeper.db"""
        self.db_path = db_path
        self.connection = None
        
    async def initialize(self):
        """Initialize the database and create tables."""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.connection = await aiosqlite.connect(self.db_path)
        await self.create_tables()
        logger.info("🗃️ Keeper Database initialized")
    
    async def create_tables(self):
        """Create all necessary database tables."""
        
        # Discoveries table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS discoveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                username TEXT NOT NULL,
                guild_id TEXT,
                discovery_type TEXT NOT NULL,
                location TEXT NOT NULL,
                system_name TEXT,
                time_period TEXT,
                condition TEXT,
                description TEXT NOT NULL,
                significance TEXT,
                evidence_url TEXT,
                related_discoveries TEXT,
                coordinates TEXT,
                planet_name TEXT,
                galaxy_name TEXT,
                submission_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                analysis_status TEXT DEFAULT 'pending',
                pattern_matches INTEGER DEFAULT 0,
                mystery_tier INTEGER DEFAULT 0,
                tags TEXT,
                metadata TEXT
            )
        """)
        
        # Patterns table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                discovery_count INTEGER DEFAULT 0,
                confidence_level REAL DEFAULT 0.0,
                first_discovered DATETIME,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'emerging',
                mystery_tier INTEGER DEFAULT 1,
                description TEXT,
                investigation_channel_id TEXT,
                related_discoveries TEXT,
                metadata TEXT
            )
        """)
        
        # Pattern-Discovery relationships
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS pattern_discoveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id INTEGER,
                discovery_id INTEGER,
                correlation_strength REAL DEFAULT 0.0,
                added_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pattern_id) REFERENCES patterns (id),
                FOREIGN KEY (discovery_id) REFERENCES discoveries (id)
            )
        """)
        
        # Investigations table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS investigations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT NOT NULL,
                pattern_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                participant_count INTEGER DEFAULT 0,
                evidence_count INTEGER DEFAULT 0,
                conclusion TEXT,
                metadata TEXT,
                FOREIGN KEY (pattern_id) REFERENCES patterns (id)
            )
        """)
        
        # Archive entries for Keeper responses
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS archive_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id TEXT UNIQUE NOT NULL,
                discovery_id INTEGER,
                entry_type TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                embed_data TEXT,
                channel_id TEXT,
                message_id TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (discovery_id) REFERENCES discoveries (id)
            )
        """)
        
        # User statistics and participation
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                discovery_count INTEGER DEFAULT 0,
                pattern_contributions INTEGER DEFAULT 0,
                investigation_participation INTEGER DEFAULT 0,
                first_discovery DATETIME,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                reputation_score INTEGER DEFAULT 0,
                badges TEXT,
                metadata TEXT
            )
        """)
        
        # Server configuration
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS server_config (
                guild_id TEXT PRIMARY KEY,
                discovery_channel_id TEXT,
                archive_channel_id TEXT,
                investigation_channel_id TEXT,
                lore_discussion_channel_id TEXT,
                admin_role_id TEXT,
                moderator_role_id TEXT,
                pattern_threshold INTEGER DEFAULT 3,
                auto_pattern_enabled BOOLEAN DEFAULT 1,
                keeper_personality_mode TEXT DEFAULT 'standard',
                config_data TEXT,
                setup_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Phase 4: Community Features Tables
        
        # User tier progression table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS user_tier_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                guild_id TEXT NOT NULL,
                current_tier INTEGER DEFAULT 1,
                tier_progress REAL DEFAULT 0.0,
                total_discoveries INTEGER DEFAULT 0,
                pattern_contributions INTEGER DEFAULT 0,
                quality_score REAL DEFAULT 0.0,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                achievements TEXT,
                metadata TEXT,
                UNIQUE(user_id, guild_id)
            )
        """)
        
        # Community challenges table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS community_challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenge_name TEXT NOT NULL,
                challenge_type TEXT NOT NULL,
                description TEXT NOT NULL,
                requirements TEXT,
                rewards TEXT,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME NOT NULL,
                status TEXT DEFAULT 'active',
                max_participants INTEGER DEFAULT -1,
                created_by TEXT,
                metadata TEXT
            )
        """)
        
        # Challenge submissions table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS challenge_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenge_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                username TEXT NOT NULL,
                submission_text TEXT NOT NULL,
                supporting_evidence TEXT,
                submission_score INTEGER DEFAULT 0,
                submission_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                reviewed BOOLEAN DEFAULT 0,
                reviewer_notes TEXT,
                FOREIGN KEY (challenge_id) REFERENCES community_challenges (id)
            )
        """)
        
        # User achievements table  
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                achievement_name TEXT NOT NULL,
                achievement_description TEXT,
                achievement_tier INTEGER DEFAULT 1,
                earned_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                guild_id TEXT,
                trigger_data TEXT
            )
        """)
        
        # Community events table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS community_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT,
                start_time DATETIME,
                end_time DATETIME,
                status TEXT DEFAULT 'planned',
                host_user_id TEXT,
                participants TEXT,
                event_data TEXT,
                created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Story progression table - Track Act I, II, III completion per guild
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS story_progression (
                guild_id TEXT PRIMARY KEY,
                current_act INTEGER DEFAULT 1,
                act_1_complete BOOLEAN DEFAULT 0,
                act_2_complete BOOLEAN DEFAULT 0,
                act_3_complete BOOLEAN DEFAULT 0,
                act_1_timestamp DATETIME,
                act_2_timestamp DATETIME,
                act_3_timestamp DATETIME,
                total_discoveries INTEGER DEFAULT 0,
                total_patterns INTEGER DEFAULT 0,
                story_milestone_count INTEGER DEFAULT 0,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        # Pattern contributions tracking
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS pattern_contributions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                pattern_id INTEGER NOT NULL,
                contribution_type TEXT NOT NULL,
                contribution_description TEXT,
                confidence_contribution REAL DEFAULT 0.0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pattern_id) REFERENCES patterns (id)
            )
        """)

        await self.connection.commit()
        logger.info("📊 Database tables created/verified (Phase 4 Community Features included)")
    
    async def add_discovery(self, discovery_data: Dict) -> int:
        """Add a new discovery to the database."""
        # Store all type-specific fields in metadata for compatibility with VH-Database
        metadata = discovery_data.get('metadata', {})
        if not isinstance(metadata, dict):
            metadata = {}

        # Add all type-specific fields to metadata
        type_specific_fields = [
            'species_type', 'size_scale', 'preservation_quality', 'estimated_age',
            'language_status', 'completeness', 'author_origin', 'key_excerpt',
            'structure_type', 'architectural_style', 'structural_integrity', 'purpose_function',
            'tech_category', 'operational_status', 'power_source', 'reverse_engineering',
            'species_name', 'behavioral_notes', 'habitat_biome', 'threat_level',
            'resource_type', 'deposit_richness', 'extraction_method', 'economic_value',
            'ship_class', 'hull_condition', 'salvageable_tech', 'pilot_status',
            'hazard_type', 'severity_level', 'duration_frequency', 'protection_required',
            'update_name', 'feature_category', 'gameplay_impact', 'first_impressions',
            'story_type', 'lore_connections', 'creative_elements', 'collaborative_work',
            'location_type', 'location_name', 'location_info'
        ]

        for field in type_specific_fields:
            if field in discovery_data:
                metadata[field] = discovery_data[field]

        cursor = await self.connection.execute("""
            INSERT INTO discoveries (
                user_id, username, guild_id, discovery_type, location, system_name,
                time_period, condition, description, significance, evidence_url,
                related_discoveries, coordinates, planet_name, galaxy_name,
                tags, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            discovery_data.get('user_id'),
            discovery_data.get('username'),
            discovery_data.get('guild_id'),
            discovery_data.get('type'),
            discovery_data.get('location'),
            discovery_data.get('system_name'),
            discovery_data.get('time_period'),
            discovery_data.get('condition'),
            discovery_data.get('description'),
            discovery_data.get('significance'),
            discovery_data.get('evidence_url'),
            json.dumps(discovery_data.get('related_discoveries', [])),
            discovery_data.get('coordinates'),
            discovery_data.get('planet_name'),
            discovery_data.get('galaxy_name'),
            json.dumps(discovery_data.get('tags', [])),
            json.dumps(metadata)
        ))

        discovery_id = cursor.lastrowid
        await self.connection.commit()

        # Update user stats
        await self.update_user_stats(discovery_data.get('user_id'), 'discovery')

        logger.info(f"📝 Discovery {discovery_id} added to archive")
        return discovery_id
    
    async def get_discovery(self, discovery_id: int) -> Optional[Dict]:
        """Get a discovery by ID."""
        logger.info(f"🔍 Getting discovery #{discovery_id}")
        cursor = await self.connection.execute(
            "SELECT * FROM discoveries WHERE id = ?", (discovery_id,)
        )
        row = await cursor.fetchone()
        
        if row:
            discovery = self._row_to_discovery_dict(row)
            logger.info(f"✅ Found discovery #{discovery_id}, type: {discovery.get('type')}")
            return discovery
        logger.warning(f"❌ Discovery #{discovery_id} not found")
        return None
    
    async def search_discoveries(self, 
                               discovery_type: Optional[str] = None,
                               location: Optional[str] = None,
                               time_period: Optional[str] = None,
                               user_id: Optional[str] = None,
                               limit: int = 50) -> List[Dict]:
        """Search discoveries with filters."""
        query = "SELECT * FROM discoveries WHERE 1=1"
        params = []
        
        if discovery_type:
            query += " AND discovery_type = ?"
            params.append(discovery_type)
        
        if location:
            query += " AND (location LIKE ? OR planet_name LIKE ? OR galaxy_name LIKE ?)"
            location_pattern = f"%{location}%"
            params.extend([location_pattern, location_pattern, location_pattern])
        
        if time_period:
            query += " AND time_period = ?"
            params.append(time_period)
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        query += " ORDER BY submission_timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor = await self.connection.execute(query, params)
        rows = await cursor.fetchall()
        
        return [self._row_to_discovery_dict(row) for row in rows]
    
    async def find_similar_discoveries(self, discovery_id: int, threshold: float = 0.6) -> List[Dict]:
        """Find discoveries similar to the given one for pattern detection."""
        # Get the source discovery
        source = await self.get_discovery(discovery_id)
        if not source:
            return []
        
        logger.info(f"🔍 Finding similar discoveries to #{discovery_id}, type: {source['type']}")
        
        # Find discoveries with same type or location patterns
        similar = await self.search_discoveries(
            discovery_type=source['type'],
            limit=100
        )
        
        logger.info(f"🔍 Found {len(similar)} discoveries with same type before filtering")
        
        # Filter out the source discovery itself
        similar = [d for d in similar if d['id'] != discovery_id]
        
        logger.info(f"🔍 Returning {len(similar)} similar discoveries (after filtering source)")
        
        # TODO: Implement more sophisticated similarity scoring
        # For now, return discoveries with same type
        return similar[:10]
    
    async def create_pattern(self, pattern_data: Dict) -> int:
        """Create a new pattern."""
        cursor = await self.connection.execute("""
            INSERT INTO patterns (
                pattern_name, pattern_type, discovery_count, confidence_level,
                first_discovered, status, mystery_tier, description, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pattern_data.get('name'),
            pattern_data.get('type'),
            pattern_data.get('discovery_count', 0),
            pattern_data.get('confidence', 0.0),
            datetime.utcnow(),
            pattern_data.get('status', 'emerging'),
            pattern_data.get('mystery_tier', 1),
            pattern_data.get('description'),
            json.dumps(pattern_data.get('metadata', {}))
        ))
        
        pattern_id = cursor.lastrowid
        await self.connection.commit()
        
        logger.info(f"🌀 Pattern {pattern_id} created")
        return pattern_id
    
    async def add_discovery_to_pattern(self, pattern_id: int, discovery_id: int, correlation: float = 1.0):
        """Associate a discovery with a pattern."""
        await self.connection.execute("""
            INSERT INTO pattern_discoveries (pattern_id, discovery_id, correlation_strength)
            VALUES (?, ?, ?)
        """, (pattern_id, discovery_id, correlation))
        
        # Update pattern discovery count
        await self.connection.execute("""
            UPDATE patterns SET 
                discovery_count = (SELECT COUNT(*) FROM pattern_discoveries WHERE pattern_id = ?),
                last_updated = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (pattern_id, pattern_id))
        
        # Update discovery pattern matches
        await self.connection.execute("""
            UPDATE discoveries SET 
                pattern_matches = (SELECT COUNT(*) FROM pattern_discoveries WHERE discovery_id = ?)
            WHERE id = ?
        """, (discovery_id, discovery_id))
        
        await self.connection.commit()
    
    async def get_patterns_by_tier(self, tier: int) -> List[Dict]:
        """Get all patterns of a specific mystery tier."""
        cursor = await self.connection.execute(
            "SELECT * FROM patterns WHERE mystery_tier = ? ORDER BY last_updated DESC",
            (tier,)
        )
        rows = await cursor.fetchall()
        return [self._row_to_pattern_dict(row) for row in rows]
    
    async def update_user_stats(self, user_id: str, activity_type: str):
        """Update user statistics."""
        # Get current stats or create new record
        cursor = await self.connection.execute(
            "SELECT * FROM user_stats WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        
        if row:
            # Update existing stats
            updates = {"last_activity": datetime.utcnow()}
            if activity_type == 'discovery':
                updates["discovery_count"] = row[2] + 1  # Assuming discovery_count is index 2
            elif activity_type == 'pattern':
                updates["pattern_contributions"] = row[3] + 1
            elif activity_type == 'investigation':
                updates["investigation_participation"] = row[4] + 1
            
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [user_id]
            
            await self.connection.execute(
                f"UPDATE user_stats SET {set_clause} WHERE user_id = ?",
                values
            )
        else:
            # Create new stats record
            initial_stats = {
                'discovery_count': 1 if activity_type == 'discovery' else 0,
                'pattern_contributions': 1 if activity_type == 'pattern' else 0,
                'investigation_participation': 1 if activity_type == 'investigation' else 0
            }
            
            await self.connection.execute("""
                INSERT INTO user_stats (
                    user_id, username, discovery_count, pattern_contributions,
                    investigation_participation, first_discovery, last_activity
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, "Unknown", 
                initial_stats['discovery_count'],
                initial_stats['pattern_contributions'],
                initial_stats['investigation_participation'],
                datetime.utcnow(), datetime.utcnow()
            ))
        
        await self.connection.commit()
    
    def _row_to_discovery_dict(self, row) -> Dict:
        """Convert database row to discovery dictionary."""
        return {
            'id': row[0],
            'user_id': row[1],
            'username': row[2],
            'guild_id': row[3],
            'type': row[4],
            'location': row[5],
            'time_period': row[6],
            'condition': row[7],
            'description': row[8],
            'significance': row[9],
            'evidence_url': row[10],
            'related_discoveries': json.loads(row[11]) if row[11] else [],
            'coordinates': row[12],
            'planet_name': row[13],
            'galaxy_name': row[14],
            'submission_timestamp': row[15],
            'analysis_status': row[16],
            'pattern_matches': row[17],
            'mystery_tier': row[18],
            'tags': json.loads(row[19]) if row[19] else [],
            'metadata': json.loads(row[20]) if row[20] else {},
            'system_name': row[21] if len(row) > 21 else None  # Last column, may not exist in old rows
        }
    
    def _row_to_pattern_dict(self, row) -> Dict:
        """Convert database row to pattern dictionary."""
        return {
            'id': row[0],
            'name': row[1],
            'type': row[2],
            'discovery_count': row[3],
            'confidence': row[4],
            'first_discovered': row[5],
            'last_updated': row[6],
            'status': row[7],
            'mystery_tier': row[8],
            'description': row[9],
            'investigation_channel_id': row[10],
            'related_discoveries': json.loads(row[11]) if row[11] else [],
            'metadata': json.loads(row[12]) if row[12] else {}
        }
    
    async def get_server_config(self, guild_id: str) -> Optional[Dict]:
        """Get server configuration."""
        cursor = await self.connection.execute(
            "SELECT * FROM server_config WHERE guild_id = ?", (guild_id,)
        )
        row = await cursor.fetchone()
        
        if row:
            return {
                'guild_id': row[0],
                'discovery_channel_id': row[1],
                'archive_channel_id': row[2],
                'investigation_channel_id': row[3],
                'lore_discussion_channel_id': row[4],
                'admin_role_id': row[5],
                'moderator_role_id': row[6],
                'pattern_threshold': row[7],
                'auto_pattern_enabled': row[8],
                'keeper_personality_mode': row[9],
                'config_data': json.loads(row[10]) if row[10] else {},
                'setup_timestamp': row[11]
            }
        return None
    
    async def update_server_config(self, guild_id: str, config_data: Dict):
        """Update or create server configuration."""
        await self.connection.execute("""
            INSERT OR REPLACE INTO server_config (
                guild_id, discovery_channel_id, archive_channel_id,
                investigation_channel_id, lore_discussion_channel_id,
                admin_role_id, moderator_role_id, pattern_threshold,
                auto_pattern_enabled, keeper_personality_mode, config_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            guild_id,
            config_data.get('discovery_channel_id'),
            config_data.get('archive_channel_id'),
            config_data.get('investigation_channel_id'),
            config_data.get('lore_discussion_channel_id'),
            config_data.get('admin_role_id'),
            config_data.get('moderator_role_id'),
            config_data.get('pattern_threshold', 3),
            config_data.get('auto_pattern_enabled', True),
            config_data.get('keeper_personality_mode', 'standard'),
            json.dumps(config_data.get('extra', {}))
        ))
        await self.connection.commit()
    
    async def get_active_challenges(self, guild_id: str) -> List[Dict]:
        """Get all active community challenges for a guild."""
        cursor = await self.connection.execute("""
            SELECT 
                id, challenge_name, challenge_type, description,
                requirements, rewards, start_time, end_time, status,
                max_participants, created_by, metadata
            FROM community_challenges
            WHERE status = 'active' AND end_time > datetime('now')
        """)
        rows = await cursor.fetchall()
        
        challenges = []
        for row in rows:
            challenges.append({
                'id': row[0],
                'name': row[1],
                'challenge_type': row[2],
                'description': row[3],
                'requirements': row[4],
                'rewards': row[5],
                'start_time': row[6],
                'end_time': row[7],
                'status': row[8],
                'max_participants': row[9],
                'created_by': row[10],
                'metadata': json.loads(row[11]) if row[11] else {}
            })
        return challenges
    
    async def create_challenge(self, challenge_data: Dict):
        """Create a new community challenge."""
        from datetime import timedelta
        
        # Calculate end time
        start_time = datetime.now()
        duration_days = challenge_data.get('duration_days', 7)
        end_time = start_time + timedelta(days=duration_days)
        
        await self.connection.execute("""
            INSERT INTO community_challenges (
                challenge_name, challenge_type, description,
                requirements, rewards, start_time, end_time,
                status, created_by, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            challenge_data['name'],
            challenge_data['challenge_type'],
            challenge_data['description'],
            challenge_data.get('requirements', ''),
            challenge_data.get('rewards', ''),
            start_time.isoformat(),
            end_time.isoformat(),
            'active',
            challenge_data.get('created_by', ''),
            json.dumps({
                'guild_id': challenge_data.get('guild_id', ''),
                'created_by_name': challenge_data.get('created_by_name', '')
            })
        ))
        await self.connection.commit()
        logger.info(f"Created challenge: {challenge_data['name']}")
    
    # Story Progression Methods
    
    async def get_story_progression(self, guild_id: str) -> Dict:
        """Get story progression for a guild."""
        cursor = await self.connection.execute("""
            SELECT 
                current_act, act_1_complete, act_2_complete, act_3_complete,
                act_1_timestamp, act_2_timestamp, act_3_timestamp,
                total_discoveries, total_patterns, story_milestone_count,
                last_updated, metadata
            FROM story_progression
            WHERE guild_id = ?
        """, (guild_id,))
        row = await cursor.fetchone()
        
        if row:
            return {
                'guild_id': guild_id,
                'current_act': row[0],
                'act_1_complete': bool(row[1]),
                'act_2_complete': bool(row[2]),
                'act_3_complete': bool(row[3]),
                'act_1_timestamp': row[4],
                'act_2_timestamp': row[5],
                'act_3_timestamp': row[6],
                'total_discoveries': row[7],
                'total_patterns': row[8],
                'story_milestone_count': row[9],
                'last_updated': row[10],
                'metadata': json.loads(row[11]) if row[11] else {}
            }
        else:
            # Initialize story progression for new guild
            await self.initialize_story_progression(guild_id)
            return await self.get_story_progression(guild_id)
    
    async def initialize_story_progression(self, guild_id: str):
        """Initialize story progression for a new guild."""
        await self.connection.execute("""
            INSERT OR IGNORE INTO story_progression (
                guild_id, current_act, act_1_complete, act_2_complete, act_3_complete,
                total_discoveries, total_patterns, story_milestone_count
            ) VALUES (?, 1, 0, 0, 0, 0, 0, 0)
        """, (guild_id,))
        await self.connection.commit()
        logger.info(f"📖 Initialized story progression for guild {guild_id} - Act I begins")
    
    async def update_story_progression(self, guild_id: str, updates: Dict):
        """Update story progression for a guild."""
        set_clauses = []
        params = []
        
        # Build dynamic UPDATE query
        for key, value in updates.items():
            if key in ['current_act', 'act_1_complete', 'act_2_complete', 'act_3_complete',
                      'act_1_timestamp', 'act_2_timestamp', 'act_3_timestamp',
                      'total_discoveries', 'total_patterns', 'story_milestone_count', 'metadata']:
                set_clauses.append(f"{key} = ?")
                if key == 'metadata' and isinstance(value, dict):
                    params.append(json.dumps(value))
                else:
                    params.append(value)
        
        if not set_clauses:
            return
        
        set_clauses.append("last_updated = CURRENT_TIMESTAMP")
        params.append(guild_id)
        
        query = f"""
            UPDATE story_progression
            SET {', '.join(set_clauses)}
            WHERE guild_id = ?
        """
        
        await self.connection.execute(query, tuple(params))
        await self.connection.commit()
        logger.info(f"📖 Updated story progression for guild {guild_id}")
    
    async def complete_act(self, guild_id: str, act_number: int):
        """Mark an act as complete and transition to next act."""
        now = datetime.utcnow().isoformat()
        
        updates = {
            f'act_{act_number}_complete': 1,
            f'act_{act_number}_timestamp': now,
            'story_milestone_count': 1  # Will be incremented
        }
        
        # Transition to next act if not at Act III
        if act_number < 3:
            updates['current_act'] = act_number + 1
        
        await self.update_story_progression(guild_id, updates)
        
        # Increment milestone count
        cursor = await self.connection.execute("""
            UPDATE story_progression
            SET story_milestone_count = story_milestone_count + 1
            WHERE guild_id = ?
        """, (guild_id,))
        await self.connection.commit()
        
        logger.info(f"🎭 Guild {guild_id} completed Act {act_number}!")
    
    async def increment_story_stats(self, guild_id: str, stat_type: str, amount: int = 1):
        """Increment story-related statistics (discoveries or patterns)."""
        if stat_type == 'discoveries':
            column = 'total_discoveries'
        elif stat_type == 'patterns':
            column = 'total_patterns'
        else:
            return
        
        await self.connection.execute(f"""
            UPDATE story_progression
            SET {column} = {column} + ?,
                last_updated = CURRENT_TIMESTAMP
            WHERE guild_id = ?
        """, (amount, guild_id))
        await self.connection.commit()
    
    async def close(self):
        """Close the database connection."""
        if self.connection:
            await self.connection.close()
            logger.info("🗃️ Keeper Database connection closed")