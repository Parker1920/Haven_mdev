"""
Sync Worker - Background task that syncs discoveries to VH-Database.db
Runs every 30 seconds as part of the bot process.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional
import os
from pathlib import Path

from database.keeper_db import KeeperDatabase
from database.sync_queue import SyncQueueManager
from core.haven_integration import HavenIntegration

logger = logging.getLogger('keeper.sync_worker')

class SyncWorker:
    """Background worker that syncs discoveries from keeper.db to VH-Database.db"""

    def __init__(self, keeper_db: KeeperDatabase, sync_interval: int = 30):
        """
        Initialize sync worker.

        Args:
            keeper_db: KeeperDatabase instance
            sync_interval: Seconds between sync attempts (default: 30)
        """
        self.keeper_db = keeper_db
        self.sync_queue = SyncQueueManager(keeper_db.connection)
        self.haven = HavenIntegration()
        self.sync_interval = sync_interval
        self.is_running = False
        self.task = None

        # Statistics
        self.total_synced = 0
        self.total_failed = 0
        self.last_sync_time = None
        self.startup_time = None

    async def start(self):
        """Start the sync worker background task."""
        if self.is_running:
            logger.warning("Sync worker already running")
            return

        # Initialize sync queue table
        await self.sync_queue.create_sync_queue_table()

        # Initialize Haven integration
        success = await self.haven.load_haven_data()
        if success:
            logger.info("✅ Haven integration initialized for sync worker")
        else:
            logger.warning("⚠️ Haven data not loaded - will sync to VH-Database.db only")

        self.is_running = True
        self.startup_time = datetime.utcnow()
        self.task = asyncio.create_task(self._run())

        logger.info(f"🔄 Sync worker started (interval: {self.sync_interval}s)")

    async def stop(self):
        """Stop the sync worker."""
        if not self.is_running:
            return

        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

        logger.info("🛑 Sync worker stopped")

    async def _run(self):
        """Main sync worker loop."""
        while self.is_running:
            try:
                await self._sync_batch()
                await asyncio.sleep(self.sync_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in sync worker loop: {e}", exc_info=True)
                await asyncio.sleep(self.sync_interval)

    async def _sync_batch(self):
        """Sync a batch of pending discoveries."""
        # Get pending items from queue
        pending = await self.sync_queue.get_pending_syncs(limit=10)

        if not pending:
            # No pending items, just return
            return

        logger.info(f"🔄 Processing {len(pending)} pending discoveries for sync")

        for item in pending:
            try:
                await self._sync_discovery(item)
            except Exception as e:
                logger.error(f"Error syncing discovery {item['discovery_id']}: {e}", exc_info=True)
                await self.sync_queue.mark_failed(
                    item['queue_id'],
                    f"Sync error: {str(e)[:200]}"
                )

        # Update last sync time
        self.last_sync_time = datetime.utcnow()

    async def _sync_discovery(self, queue_item: dict):
        """Sync a single discovery to VH-Database."""
        queue_id = queue_item['queue_id']
        discovery_id = queue_item['discovery_id']

        # Mark as syncing
        await self.sync_queue.mark_syncing(queue_id)

        # Get full discovery data from keeper.db
        discovery = await self.keeper_db.get_discovery(discovery_id)

        if not discovery:
            await self.sync_queue.mark_failed(queue_id, "Discovery not found in keeper.db")
            return

        # Prepare discovery data for VH-Database format
        discovery_data = await self._prepare_discovery_for_haven(discovery)

        # Write to VH-Database.db
        try:
            haven_id = self.haven.write_discovery_to_database(discovery_data)

            if haven_id:
                # Success!
                await self.sync_queue.mark_synced(queue_id, haven_id)
                self.total_synced += 1
                logger.info(f"✅ Discovery {discovery_id} synced to VH-Database (haven_id={haven_id})")
            else:
                # Write failed but didn't throw exception
                await self.sync_queue.mark_failed(
                    queue_id,
                    "VH-Database write returned None"
                )
                self.total_failed += 1

        except FileNotFoundError as e:
            # VH-Database.db not found
            await self.sync_queue.mark_failed(
                queue_id,
                f"VH-Database not accessible: {str(e)}"
            )
            self.total_failed += 1
            logger.warning(f"⚠️ VH-Database not found - will retry later")

        except Exception as e:
            # Other error (database locked, schema mismatch, etc.)
            await self.sync_queue.mark_failed(
                queue_id,
                f"Write error: {str(e)[:200]}"
            )
            self.total_failed += 1
            logger.error(f"❌ Failed to write discovery {discovery_id} to VH-Database: {e}")

        # Check if max retries exceeded
        queue_status = await self.sync_queue.get_queue_item(queue_id)
        if queue_status and queue_status['sync_attempts'] >= 10:
            await self.sync_queue.mark_max_retries_exceeded(queue_id)
            logger.error(f"❌ Discovery {discovery_id} exceeded max retry attempts")

    async def _prepare_discovery_for_haven(self, discovery: dict) -> dict:
        """
        Convert keeper.db discovery format to VH-Database.db format.

        keeper.db uses simplified schema, VH-Database uses full 66-field schema.
        """
        # Parse location info to determine location_type and location_name
        location_type = discovery.get('location_type', 'space')
        location_name = discovery.get('location', '')

        # If we have planet_name, use it
        if discovery.get('planet_name'):
            location_name = discovery['planet_name']
            # Determine if it's planet or moon from location string
            if 'moon' in location_name.lower() or 'moon' in discovery.get('location', '').lower():
                location_type = 'moon'
            else:
                location_type = 'planet'

        # Build VH-Database compatible discovery data
        haven_data = {
            # Core identification fields
            'type': discovery.get('type'),  # Discovery type emoji
            'discovery_type': discovery.get('type'),  # Alias
            'discovery_name': discovery.get('location_name'),
            'system_name': discovery.get('system_name'),
            'location_type': location_type,
            'location_name': location_name,

            # Description and context
            'description': discovery.get('description'),
            'coordinates': discovery.get('coordinates'),
            'condition': discovery.get('condition'),
            'time_period': discovery.get('time_period'),
            'significance': discovery.get('significance'),

            # Evidence
            'photo_url': discovery.get('evidence_url'),
            'evidence_url': discovery.get('evidence_url'),
            'evidence_urls': discovery.get('evidence_url'),  # VH-Database expects this field

            # User information
            'username': discovery.get('username'),
            'discovered_by': discovery.get('username'),
            'user_id': discovery.get('user_id'),
            'discord_user_id': discovery.get('user_id'),
            'guild_id': discovery.get('guild_id'),
            'discord_guild_id': discovery.get('guild_id'),

            # Pattern and analysis
            'pattern_matches': discovery.get('pattern_matches', 0),
            'mystery_tier': discovery.get('mystery_tier', 0),
            'analysis_status': discovery.get('analysis_status', 'pending'),
            'tags': discovery.get('tags'),
            'metadata': discovery.get('metadata'),

            # Type-specific fields from keeper.db metadata
            # These will be None if not in the discovery
            'species_type': self._extract_metadata_field(discovery, 'species_type'),
            'size_scale': self._extract_metadata_field(discovery, 'size_scale'),
            'preservation_quality': self._extract_metadata_field(discovery, 'preservation_quality'),
            'estimated_age': self._extract_metadata_field(discovery, 'estimated_age'),
            'language_status': self._extract_metadata_field(discovery, 'language_status'),
            'completeness': self._extract_metadata_field(discovery, 'completeness'),
            'author_origin': self._extract_metadata_field(discovery, 'author_origin'),
            'key_excerpt': self._extract_metadata_field(discovery, 'key_excerpt'),
            'structure_type': self._extract_metadata_field(discovery, 'structure_type'),
            'architectural_style': self._extract_metadata_field(discovery, 'architectural_style'),
            'structural_integrity': self._extract_metadata_field(discovery, 'structural_integrity'),
            'purpose_function': self._extract_metadata_field(discovery, 'purpose_function'),
            'tech_category': self._extract_metadata_field(discovery, 'tech_category'),
            'operational_status': self._extract_metadata_field(discovery, 'operational_status'),
            'power_source': self._extract_metadata_field(discovery, 'power_source'),
            'reverse_engineering': self._extract_metadata_field(discovery, 'reverse_engineering'),
            'species_name': self._extract_metadata_field(discovery, 'species_name'),
            'behavioral_notes': self._extract_metadata_field(discovery, 'behavioral_notes'),
            'habitat_biome': self._extract_metadata_field(discovery, 'habitat_biome'),
            'threat_level': self._extract_metadata_field(discovery, 'threat_level'),
            'resource_type': self._extract_metadata_field(discovery, 'resource_type'),
            'deposit_richness': self._extract_metadata_field(discovery, 'deposit_richness'),
            'extraction_method': self._extract_metadata_field(discovery, 'extraction_method'),
            'economic_value': self._extract_metadata_field(discovery, 'economic_value'),
            'ship_class': self._extract_metadata_field(discovery, 'ship_class'),
            'hull_condition': self._extract_metadata_field(discovery, 'hull_condition'),
            'salvageable_tech': self._extract_metadata_field(discovery, 'salvageable_tech'),
            'pilot_status': self._extract_metadata_field(discovery, 'pilot_status'),
            'hazard_type': self._extract_metadata_field(discovery, 'hazard_type'),
            'severity_level': self._extract_metadata_field(discovery, 'severity_level'),
            'duration_frequency': self._extract_metadata_field(discovery, 'duration_frequency'),
            'protection_required': self._extract_metadata_field(discovery, 'protection_required'),
            'update_name': self._extract_metadata_field(discovery, 'update_name'),
            'feature_category': self._extract_metadata_field(discovery, 'feature_category'),
            'gameplay_impact': self._extract_metadata_field(discovery, 'gameplay_impact'),
            'first_impressions': self._extract_metadata_field(discovery, 'first_impressions'),
            'story_type': self._extract_metadata_field(discovery, 'story_type'),
            'lore_connections': self._extract_metadata_field(discovery, 'lore_connections'),
            'creative_elements': self._extract_metadata_field(discovery, 'creative_elements'),
            'collaborative_work': self._extract_metadata_field(discovery, 'collaborative_work')
        }

        return haven_data

    def _extract_metadata_field(self, discovery: dict, field_name: str):
        """Extract a field from discovery metadata if it exists."""
        metadata = discovery.get('metadata', {})
        if isinstance(metadata, dict):
            return metadata.get(field_name)
        return None

    async def get_statistics(self) -> dict:
        """Get sync worker statistics."""
        queue_stats = await self.sync_queue.get_sync_statistics()

        uptime_seconds = None
        if self.startup_time:
            uptime_seconds = (datetime.utcnow() - self.startup_time).total_seconds()

        return {
            'is_running': self.is_running,
            'sync_interval': self.sync_interval,
            'total_synced': self.total_synced,
            'total_failed': self.total_failed,
            'last_sync_time': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'uptime_seconds': uptime_seconds,
            'queue_stats': queue_stats
        }

    async def manual_sync_discovery(self, discovery_id: int) -> bool:
        """Manually trigger sync for a specific discovery."""
        try:
            # Add to queue if not already there
            queue_id = await self.sync_queue.add_to_queue(discovery_id)

            if queue_id:
                logger.info(f"🔄 Manually queued discovery {discovery_id} for sync")
                return True
            else:
                # Already in queue, try to sync immediately
                pending = await self.sync_queue.get_pending_syncs(limit=100)
                for item in pending:
                    if item['discovery_id'] == discovery_id:
                        await self._sync_discovery(item)
                        return True

                logger.warning(f"Discovery {discovery_id} not found in queue")
                return False

        except Exception as e:
            logger.error(f"Error in manual sync: {e}", exc_info=True)
            return False
