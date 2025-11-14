"""
Sync Queue Manager
Manages the queue of discoveries waiting to be synced to VH-Database.db
"""

import aiosqlite
import logging
from datetime import datetime
from typing import Dict, List, Optional
import json

logger = logging.getLogger('keeper.sync_queue')

class SyncQueueManager:
    """Manages sync queue for discoveries waiting to be written to VH-Database."""

    def __init__(self, db_connection: aiosqlite.Connection):
        """Initialize with existing keeper database connection."""
        self.connection = db_connection

    async def create_sync_queue_table(self):
        """Create the sync queue table if it doesn't exist."""
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS sync_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discovery_id INTEGER NOT NULL,
                sync_status TEXT DEFAULT 'pending',
                sync_attempts INTEGER DEFAULT 0,
                max_attempts INTEGER DEFAULT 10,
                last_sync_attempt DATETIME,
                next_retry_after DATETIME,
                sync_error TEXT,
                haven_discovery_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                synced_at DATETIME,
                metadata TEXT,
                FOREIGN KEY (discovery_id) REFERENCES discoveries(id),
                UNIQUE(discovery_id)
            )
        """)

        # Create index for faster queries
        await self.connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_sync_status
            ON sync_queue(sync_status, next_retry_after)
        """)

        await self.connection.commit()
        logger.info("📋 Sync queue table created/verified")

    async def add_to_queue(self, discovery_id: int, metadata: Dict = None) -> int:
        """Add a discovery to the sync queue."""
        try:
            cursor = await self.connection.execute("""
                INSERT INTO sync_queue (discovery_id, sync_status, metadata)
                VALUES (?, 'pending', ?)
            """, (discovery_id, json.dumps(metadata or {})))

            queue_id = cursor.lastrowid
            await self.connection.commit()

            logger.info(f"📋 Discovery {discovery_id} added to sync queue (queue_id={queue_id})")
            return queue_id

        except aiosqlite.IntegrityError:
            # Discovery already in queue
            logger.warning(f"Discovery {discovery_id} already in sync queue")
            return None

    async def get_pending_syncs(self, limit: int = 10) -> List[Dict]:
        """Get discoveries that need to be synced."""
        cursor = await self.connection.execute("""
            SELECT
                sq.id, sq.discovery_id, sq.sync_attempts, sq.sync_error,
                sq.created_at, sq.last_sync_attempt
            FROM sync_queue sq
            WHERE sq.sync_status = 'pending'
            AND (
                sq.next_retry_after IS NULL
                OR sq.next_retry_after <= datetime('now')
            )
            AND sq.sync_attempts < sq.max_attempts
            ORDER BY sq.created_at ASC
            LIMIT ?
        """, (limit,))

        rows = await cursor.fetchall()

        pending = []
        for row in rows:
            pending.append({
                'queue_id': row[0],
                'discovery_id': row[1],
                'sync_attempts': row[2],
                'sync_error': row[3],
                'created_at': row[4],
                'last_sync_attempt': row[5]
            })

        return pending

    async def mark_syncing(self, queue_id: int):
        """Mark a queue item as currently syncing."""
        await self.connection.execute("""
            UPDATE sync_queue
            SET sync_status = 'syncing',
                last_sync_attempt = datetime('now')
            WHERE id = ?
        """, (queue_id,))
        await self.connection.commit()

    async def mark_synced(self, queue_id: int, haven_discovery_id: int):
        """Mark a queue item as successfully synced."""
        await self.connection.execute("""
            UPDATE sync_queue
            SET sync_status = 'synced',
                haven_discovery_id = ?,
                synced_at = datetime('now'),
                sync_error = NULL
            WHERE id = ?
        """, (haven_discovery_id, queue_id))
        await self.connection.commit()

        logger.info(f"✅ Queue item {queue_id} synced successfully (haven_id={haven_discovery_id})")

    async def mark_failed(self, queue_id: int, error_message: str):
        """Mark a queue item as failed and schedule retry."""
        # Calculate next retry time using exponential backoff
        # Attempts: 1=30s, 2=60s, 3=120s, 4=240s, etc.
        cursor = await self.connection.execute(
            "SELECT sync_attempts FROM sync_queue WHERE id = ?",
            (queue_id,)
        )
        row = await cursor.fetchone()
        attempts = row[0] if row else 0

        # Exponential backoff: 30s * 2^attempts
        retry_delay_seconds = 30 * (2 ** attempts)

        await self.connection.execute("""
            UPDATE sync_queue
            SET sync_status = 'pending',
                sync_attempts = sync_attempts + 1,
                sync_error = ?,
                next_retry_after = datetime('now', '+{} seconds')
            WHERE id = ?
        """.format(retry_delay_seconds), (error_message, queue_id))
        await self.connection.commit()

        logger.warning(f"⚠️ Queue item {queue_id} failed (attempt {attempts + 1}): {error_message}")
        logger.info(f"⏰ Will retry in {retry_delay_seconds} seconds")

    async def mark_max_retries_exceeded(self, queue_id: int):
        """Mark a queue item as failed after max retries."""
        await self.connection.execute("""
            UPDATE sync_queue
            SET sync_status = 'max_retries_exceeded'
            WHERE id = ?
        """, (queue_id,))
        await self.connection.commit()

        logger.error(f"❌ Queue item {queue_id} exceeded max retries")

    async def get_sync_statistics(self) -> Dict:
        """Get statistics about the sync queue."""
        cursor = await self.connection.execute("""
            SELECT
                COUNT(CASE WHEN sync_status = 'pending' THEN 1 END) as pending,
                COUNT(CASE WHEN sync_status = 'syncing' THEN 1 END) as syncing,
                COUNT(CASE WHEN sync_status = 'synced' THEN 1 END) as synced,
                COUNT(CASE WHEN sync_status = 'max_retries_exceeded' THEN 1 END) as failed,
                MAX(synced_at) as last_sync_time,
                AVG(CASE WHEN sync_status = 'synced'
                    THEN (julianday(synced_at) - julianday(created_at)) * 86400
                END) as avg_sync_time_seconds
            FROM sync_queue
        """)

        row = await cursor.fetchone()

        return {
            'pending': row[0] or 0,
            'syncing': row[1] or 0,
            'synced': row[2] or 0,
            'failed': row[3] or 0,
            'last_sync_time': row[4],
            'avg_sync_time_seconds': row[5]
        }

    async def get_failed_items(self, limit: int = 20) -> List[Dict]:
        """Get items that have failed sync after max retries."""
        cursor = await self.connection.execute("""
            SELECT
                sq.id, sq.discovery_id, sq.sync_attempts, sq.sync_error,
                sq.created_at, sq.last_sync_attempt,
                d.system_name, d.location, d.discovery_type, d.username
            FROM sync_queue sq
            JOIN discoveries d ON sq.discovery_id = d.id
            WHERE sq.sync_status = 'max_retries_exceeded'
            ORDER BY sq.last_sync_attempt DESC
            LIMIT ?
        """, (limit,))

        rows = await cursor.fetchall()

        failed = []
        for row in rows:
            failed.append({
                'queue_id': row[0],
                'discovery_id': row[1],
                'sync_attempts': row[2],
                'sync_error': row[3],
                'created_at': row[4],
                'last_sync_attempt': row[5],
                'system_name': row[6],
                'location': row[7],
                'discovery_type': row[8],
                'username': row[9]
            })

        return failed

    async def retry_failed_item(self, queue_id: int):
        """Manually retry a failed sync item."""
        await self.connection.execute("""
            UPDATE sync_queue
            SET sync_status = 'pending',
                sync_attempts = 0,
                sync_error = NULL,
                next_retry_after = NULL
            WHERE id = ?
        """, (queue_id,))
        await self.connection.commit()

        logger.info(f"🔄 Manually retrying queue item {queue_id}")

    async def get_queue_item(self, queue_id: int) -> Optional[Dict]:
        """Get a specific queue item by ID."""
        cursor = await self.connection.execute("""
            SELECT
                sq.id, sq.discovery_id, sq.sync_status, sq.sync_attempts,
                sq.sync_error, sq.haven_discovery_id, sq.created_at, sq.synced_at,
                sq.last_sync_attempt, sq.next_retry_after, sq.metadata
            FROM sync_queue sq
            WHERE sq.id = ?
        """, (queue_id,))

        row = await cursor.fetchone()
        if not row:
            return None

        return {
            'queue_id': row[0],
            'discovery_id': row[1],
            'sync_status': row[2],
            'sync_attempts': row[3],
            'sync_error': row[4],
            'haven_discovery_id': row[5],
            'created_at': row[6],
            'synced_at': row[7],
            'last_sync_attempt': row[8],
            'next_retry_after': row[9],
            'metadata': json.loads(row[10]) if row[10] else {}
        }

    async def cleanup_old_synced_items(self, days_old: int = 30):
        """Clean up old synced items from the queue (keeps records for 30 days by default)."""
        cursor = await self.connection.execute("""
            DELETE FROM sync_queue
            WHERE sync_status = 'synced'
            AND synced_at < datetime('now', '-{} days')
        """.format(days_old))

        deleted = cursor.rowcount
        await self.connection.commit()

        if deleted > 0:
            logger.info(f"🧹 Cleaned up {deleted} old synced items from queue")

        return deleted
