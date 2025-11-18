"""
Round Table AI - FastAPI Integration
======================================

Integrates Round Table AI with Haven-UI's FastAPI server.
Provides API endpoints for triggering AI analysis and querying results.
"""

import logging
from pathlib import Path
from typing import Optional

from .core import get_conductor, get_ai_interface, Conductor
from .data_access import create_haven_data_access, HavenDataAccess
from .agents import ArchivistAgent, SentinelAgent, LorekeeperAgent

logger = logging.getLogger(__name__)


class RoundTableAI:
    """
    Main Round Table AI system interface.

    Initializes all components and provides high-level methods
    for external systems (like FastAPI) to interact with the AI.
    """

    def __init__(self, haven_ui_root: Path):
        """
        Initialize Round Table AI system.

        Args:
            haven_ui_root: Path to Haven-UI root directory
        """
        self.haven_ui_root = haven_ui_root

        # Initialize data access
        logger.info("Initializing Round Table AI data access...")
        self.data_access = self._init_data_access()

        # Initialize AI interface
        logger.info("Initializing AI interface...")
        self.ai_interface = get_ai_interface()

        # Initialize Conductor
        logger.info("Initializing Conductor...")
        self.conductor = get_conductor(
            data_access=self.data_access,
            ai_interface=self.ai_interface
        )

        # Register agents
        logger.info("Registering AI agents...")
        self._register_agents()

        logger.info("✓ Round Table AI initialized successfully")
        self.data_access.log_ai_activity("System", "Round Table AI initialized")

    def _init_data_access(self) -> HavenDataAccess:
        """Initialize data access layer."""
        haven_ui_db = self.haven_ui_root / 'data' / 'haven_ui.db'
        keeper_db = self.haven_ui_root.parent / 'keeper.db'

        return HavenDataAccess(
            haven_ui_db_path=str(haven_ui_db),
            keeper_db_path=str(keeper_db) if keeper_db.exists() else None
        )

    def _register_agents(self):
        """Register all AI agents with the Conductor."""
        # The Archivist - Pattern Analysis
        archivist = ArchivistAgent(
            data_access=self.data_access,
            ai_interface=self.ai_interface
        )
        self.conductor.register_agent(archivist)

        # The Sentinel - Community Monitoring
        sentinel = SentinelAgent(
            data_access=self.data_access,
            ai_interface=self.ai_interface
        )
        self.conductor.register_agent(sentinel)

        # The Lorekeeper - Narrative Consistency
        lorekeeper = LorekeeperAgent(
            data_access=self.data_access,
            ai_interface=self.ai_interface
        )
        self.conductor.register_agent(lorekeeper)

        logger.info(f"Registered {len(self.conductor.agents)} agents")

    async def analyze_discoveries(self, limit: int = 10):
        """
        Trigger discovery analysis workflow.

        Args:
            limit: Number of discoveries to analyze

        Returns:
            Analysis results
        """
        return await self.conductor.analyze_discoveries(limit=limit)

    async def get_community_health_report(self, days: int = 7):
        """
        Get community health report from The Sentinel.

        Args:
            days: Number of days to analyze

        Returns:
            Health report
        """
        task = await self.conductor.delegate_task(
            agent_name="The Sentinel",
            task_type="health_analysis",
            context={'analysis_type': 'full', 'period_days': days}
        )

        return task.result if task.status == 'completed' else {'error': task.error}

    async def review_keeper_response(self, keeper_response: str, discovery: dict):
        """
        Have The Lorekeeper review a Keeper bot response.

        Args:
            keeper_response: The Keeper's response text
            discovery: Discovery that triggered the response

        Returns:
            Review results
        """
        task = await self.conductor.delegate_task(
            agent_name="The Lorekeeper",
            task_type="review_response",
            context={
                'analysis_type': 'review_response',
                'keeper_response': keeper_response,
                'discovery': discovery
            }
        )

        return task.result if task.status == 'completed' else {'error': task.error}

    async def suggest_keeper_response(self, discovery: dict):
        """
        Have The Lorekeeper suggest a Keeper bot response.

        Args:
            discovery: Discovery to respond to

        Returns:
            Suggested response
        """
        task = await self.conductor.delegate_task(
            agent_name="The Lorekeeper",
            task_type="suggest_response",
            context={
                'analysis_type': 'suggest_response',
                'discovery': discovery
            }
        )

        return task.result if task.status == 'completed' else {'error': task.error}

    async def generate_pattern_report(self, days: int = 7):
        """
        Generate pattern analysis report from The Archivist.

        Args:
            days: Number of days to analyze

        Returns:
            Pattern report
        """
        archivist = self.conductor.get_agent("The Archivist")
        if archivist:
            return await archivist.generate_pattern_report(days=days)
        else:
            return {'error': 'Archivist not available'}

    def get_statistics(self):
        """Get Round Table AI statistics."""
        return self.conductor.get_statistics()

    def list_agents(self):
        """List all registered agents."""
        return self.conductor.list_agents()


# Global instance
_round_table_instance: Optional[RoundTableAI] = None


def get_round_table_ai(haven_ui_root: Path = None) -> RoundTableAI:
    """
    Get singleton RoundTableAI instance.

    Args:
        haven_ui_root: Haven-UI root path (only needed for first initialization)

    Returns:
        RoundTableAI instance
    """
    global _round_table_instance

    if _round_table_instance is None:
        if haven_ui_root is None:
            raise ValueError("First call to get_round_table_ai requires haven_ui_root")

        _round_table_instance = RoundTableAI(haven_ui_root)

    return _round_table_instance
