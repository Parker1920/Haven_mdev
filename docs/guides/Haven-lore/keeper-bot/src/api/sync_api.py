"""
Simple HTTP API for sync status monitoring
Control Room can query this endpoint to check sync status.
"""

import aiohttp
from aiohttp import web
import logging
import json
from datetime import datetime

logger = logging.getLogger('keeper.sync_api')

class SyncAPI:
    """Simple HTTP API for exposing sync status to Control Room."""

    def __init__(self, bot, port: int = 8080):
        """
        Initialize sync API.

        Args:
            bot: The Keeper bot instance
            port: Port to run API on (default: 8080)
        """
        self.bot = bot
        self.port = port
        self.app = web.Application()
        self.runner = None
        self.site = None

        # Setup routes
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/sync/status', self.get_sync_status)
        self.app.router.add_get('/sync/statistics', self.get_sync_statistics)
        self.app.router.add_get('/sync/failed', self.get_failed_items)
        self.app.router.add_post('/sync/retry/{queue_id}', self.retry_sync)

    async def start(self):
        """Start the HTTP API server."""
        try:
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            self.site = web.TCPSite(self.runner, '0.0.0.0', self.port)
            await self.site.start()
            logger.info(f"🌐 Sync API started on port {self.port}")
        except Exception as e:
            logger.error(f"Failed to start Sync API: {e}")

    async def stop(self):
        """Stop the HTTP API server."""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        logger.info("🌐 Sync API stopped")

    async def health_check(self, request):
        """Health check endpoint."""
        return web.json_response({
            'status': 'healthy',
            'bot_online': self.bot.is_ready(),
            'sync_worker_running': self.bot.sync_worker.is_running if self.bot.sync_worker else False,
            'timestamp': datetime.utcnow().isoformat()
        })

    async def get_sync_status(self, request):
        """Get current sync queue status."""
        try:
            if not self.bot.sync_worker:
                return web.json_response({
                    'error': 'Sync worker not initialized'
                }, status=503)

            stats = await self.bot.sync_worker.get_statistics()

            return web.json_response({
                'status': 'ok',
                'sync_worker': {
                    'is_running': stats['is_running'],
                    'sync_interval': stats['sync_interval'],
                    'uptime_seconds': stats['uptime_seconds'],
                    'last_sync_time': stats['last_sync_time']
                },
                'queue': {
                    'pending': stats['queue_stats']['pending'],
                    'syncing': stats['queue_stats']['syncing'],
                    'synced': stats['queue_stats']['synced'],
                    'failed': stats['queue_stats']['failed']
                },
                'totals': {
                    'total_synced': stats['total_synced'],
                    'total_failed': stats['total_failed']
                }
            })

        except Exception as e:
            logger.error(f"Error getting sync status: {e}", exc_info=True)
            return web.json_response({
                'error': str(e)
            }, status=500)

    async def get_sync_statistics(self, request):
        """Get detailed sync statistics."""
        try:
            if not self.bot.sync_worker:
                return web.json_response({
                    'error': 'Sync worker not initialized'
                }, status=503)

            stats = await self.bot.sync_worker.get_statistics()

            return web.json_response({
                'status': 'ok',
                'statistics': stats
            })

        except Exception as e:
            logger.error(f"Error getting sync statistics: {e}", exc_info=True)
            return web.json_response({
                'error': str(e)
            }, status=500)

    async def get_failed_items(self, request):
        """Get list of failed sync items."""
        try:
            if not self.bot.sync_worker:
                return web.json_response({
                    'error': 'Sync worker not initialized'
                }, status=503)

            limit = int(request.query.get('limit', 20))
            failed_items = await self.bot.sync_worker.sync_queue.get_failed_items(limit=limit)

            return web.json_response({
                'status': 'ok',
                'failed_items': failed_items,
                'count': len(failed_items)
            })

        except Exception as e:
            logger.error(f"Error getting failed items: {e}", exc_info=True)
            return web.json_response({
                'error': str(e)
            }, status=500)

    async def retry_sync(self, request):
        """Manually retry a failed sync item."""
        try:
            if not self.bot.sync_worker:
                return web.json_response({
                    'error': 'Sync worker not initialized'
                }, status=503)

            queue_id = int(request.match_info['queue_id'])
            await self.bot.sync_worker.sync_queue.retry_failed_item(queue_id)

            return web.json_response({
                'status': 'ok',
                'message': f'Queue item {queue_id} marked for retry'
            })

        except Exception as e:
            logger.error(f"Error retrying sync: {e}", exc_info=True)
            return web.json_response({
                'error': str(e)
            }, status=500)
