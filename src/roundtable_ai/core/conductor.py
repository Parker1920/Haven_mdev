"""
The Conductor - Round Table AI Orchestrator
============================================

Central coordinator for all Round Table AI agents.
Decides which agents to invoke, manages task queues, and coordinates multi-agent workflows.

The Conductor is the "brain" of the Round Table AI system.
"""

import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

from .base_agent import BaseAgent, AgentTask
from .ai_interface import AIInterface
from ..data_access import HavenDataAccess

logger = logging.getLogger(__name__)


class Conductor:
    """
    Orchestrates all Round Table AI agents.

    Responsibilities:
    - Route requests to appropriate agents
    - Manage task queues and priorities
    - Coordinate multi-agent workflows
    - Aggregate results from multiple agents
    - Provide unified interface for external systems
    """

    def __init__(self, data_access: HavenDataAccess, ai_interface: AIInterface):
        """
        Initialize the Conductor.

        Args:
            data_access: HavenDataAccess instance
            ai_interface: AIInterface instance
        """
        self.data_access = data_access
        self.ai = ai_interface

        # Registry of all available agents
        self.agents: Dict[str, BaseAgent] = {}

        # Task management
        self.tasks: Dict[str, AgentTask] = {}
        self.task_queue: List[AgentTask] = []

        logger.info("Conductor initialized")

    def register_agent(self, agent: BaseAgent):
        """
        Register an agent with the Conductor.

        Args:
            agent: Agent instance to register
        """
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")
        self.data_access.log_ai_activity("Conductor", f"Registered {agent.name}")

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get agent by name."""
        return self.agents.get(name)

    def list_agents(self) -> List[Dict[str, str]]:
        """Get list of all registered agents."""
        return [agent.get_agent_info() for agent in self.agents.values()]

    async def delegate_task(self,
                           agent_name: str,
                           task_type: str,
                           context: Dict[str, Any],
                           priority: int = 3) -> AgentTask:
        """
        Delegate a task to a specific agent.

        Args:
            agent_name: Name of agent to assign task to
            task_type: Type of task
            context: Task context/input
            priority: Task priority (1-5)

        Returns:
            AgentTask object

        Raises:
            ValueError: If agent not found
        """
        agent = self.get_agent(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found")

        # Create task
        task_id = str(uuid.uuid4())
        task = AgentTask(
            task_id=task_id,
            agent_name=agent_name,
            task_type=task_type,
            context=context,
            priority=priority
        )

        self.tasks[task_id] = task
        self.task_queue.append(task)

        logger.info(f"Delegated task {task_id} to {agent_name}: {task_type}")
        self.data_access.log_ai_activity(
            "Conductor",
            f"Delegated {task_type} to {agent_name}",
            f"Task ID: {task_id}"
        )

        # Execute task immediately (for now; later can be queued)
        await self._execute_task(task)

        return task

    async def _execute_task(self, task: AgentTask):
        """Execute a single task."""
        agent = self.get_agent(task.agent_name)
        if not agent:
            task.mark_failed(f"Agent {task.agent_name} not found")
            return

        try:
            task.mark_in_progress()
            logger.info(f"Executing task {task.task_id} with {agent.name}")

            self.data_access.log_ai_activity(
                agent.name,
                f"Starting {task.task_type}",
                f"Task: {task.task_id}"
            )

            # Execute agent's analyze method
            result = await agent.analyze(task.context)

            task.mark_completed(result)
            logger.info(f"Task {task.task_id} completed successfully")

            self.data_access.log_ai_activity(
                agent.name,
                f"Completed {task.task_type}",
                f"Task: {task.task_id}"
            )

        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {e}", exc_info=True)
            task.mark_failed(str(e))

            self.data_access.log_ai_activity(
                agent.name,
                f"Failed {task.task_type}",
                f"Error: {str(e)}"
            )

    async def analyze_discoveries(self, limit: int = 10) -> Dict[str, Any]:
        """
        Coordinate discovery analysis workflow.

        This is a multi-agent workflow that involves:
        1. Archivist: Pattern detection
        2. Lorekeeper: Narrative consistency check
        3. Sentinel: Quality validation

        Args:
            limit: Number of discoveries to analyze

        Returns:
            Aggregated analysis results
        """
        self.data_access.log_ai_activity(
            "Conductor",
            f"Starting discovery analysis workflow",
            f"Analyzing {limit} discoveries"
        )

        # Get unanalyzed discoveries
        discoveries = self.data_access.get_unanalyzed_discoveries(limit=limit)

        if not discoveries:
            logger.info("No unanalyzed discoveries found")
            return {
                'status': 'no_discoveries',
                'message': 'No unanalyzed discoveries found'
            }

        logger.info(f"Found {len(discoveries)} unanalyzed discoveries")

        # Delegate to Archivist for pattern analysis
        results = {
            'discoveries_analyzed': len(discoveries),
            'patterns_found': [],
            'errors': []
        }

        # Check if Archivist is available
        if 'The Archivist' in self.agents:
            try:
                task = await self.delegate_task(
                    agent_name='The Archivist',
                    task_type='pattern_analysis',
                    context={'discoveries': discoveries}
                )

                if task.status == 'completed' and task.result:
                    results['archivist_analysis'] = task.result
                    results['patterns_found'] = task.result.get('patterns', [])
            except Exception as e:
                logger.error(f"Archivist analysis failed: {e}")
                results['errors'].append(f"Archivist: {str(e)}")

        # Could add more agents here (Lorekeeper, Sentinel, etc.)

        self.data_access.log_ai_activity(
            "Conductor",
            f"Completed discovery analysis workflow",
            f"Analyzed {len(discoveries)} discoveries, found {len(results['patterns_found'])} patterns"
        )

        return results

    async def run_daily_briefing(self) -> Dict[str, Any]:
        """
        Generate daily briefing by querying all agents.

        Returns:
            Aggregated briefing from all agents
        """
        self.data_access.log_ai_activity("Conductor", "Generating daily briefing")

        briefing = {
            'timestamp': datetime.now().isoformat(),
            'agent_reports': {}
        }

        # Collect reports from each agent
        for agent_name, agent in self.agents.items():
            try:
                # Request daily summary from agent
                task = await self.delegate_task(
                    agent_name=agent_name,
                    task_type='daily_summary',
                    context={'period': '24_hours'}
                )

                if task.status == 'completed':
                    briefing['agent_reports'][agent_name] = task.result
            except Exception as e:
                logger.error(f"Failed to get briefing from {agent_name}: {e}")
                briefing['agent_reports'][agent_name] = {'error': str(e)}

        return briefing

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        task = self.tasks.get(task_id)
        return task.to_dict() if task else None

    def get_all_tasks(self, status: str = None) -> List[Dict[str, Any]]:
        """
        Get all tasks, optionally filtered by status.

        Args:
            status: Filter by status ('pending', 'completed', etc.)

        Returns:
            List of task dictionaries
        """
        tasks = self.tasks.values()

        if status:
            tasks = [t for t in tasks if t.status == status]

        return [t.to_dict() for t in tasks]

    def get_statistics(self) -> Dict[str, Any]:
        """Get Conductor statistics."""
        return {
            'total_agents': len(self.agents),
            'total_tasks': len(self.tasks),
            'pending_tasks': len([t for t in self.tasks.values() if t.status == 'pending']),
            'completed_tasks': len([t for t in self.tasks.values() if t.status == 'completed']),
            'failed_tasks': len([t for t in self.tasks.values() if t.status == 'failed']),
            'agents': [a.get_agent_info() for a in self.agents.values()]
        }


# Global conductor instance
_conductor_instance: Optional[Conductor] = None


def get_conductor(data_access: HavenDataAccess = None,
                 ai_interface: AIInterface = None) -> Conductor:
    """
    Get singleton Conductor instance.

    Args:
        data_access: HavenDataAccess (only needed for first initialization)
        ai_interface: AIInterface (only needed for first initialization)

    Returns:
        Conductor instance
    """
    global _conductor_instance

    if _conductor_instance is None:
        if data_access is None or ai_interface is None:
            raise ValueError("First call to get_conductor requires data_access and ai_interface")

        _conductor_instance = Conductor(data_access, ai_interface)

    return _conductor_instance
