"""
Base Agent Class
=================

Abstract base class for all Round Table AI agents.
Provides common functionality for logging, AI interaction, and data access.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from ..data_access import HavenDataAccess
from .ai_interface import AIInterface

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for Round Table AI agents.

    All agents (Sentinel, Archivist, Lorekeeper, etc.) inherit from this class.

    Attributes:
        name: Agent's display name
        role: Agent's role/purpose description
        data_access: Interface to Haven databases
        ai: Interface to cloud AI services
    """

    def __init__(self,
                 name: str,
                 role: str,
                 data_access: HavenDataAccess,
                 ai_interface: AIInterface):
        """
        Initialize base agent.

        Args:
            name: Agent name (e.g., "The Archivist")
            role: Brief description of agent's purpose
            data_access: HavenDataAccess instance
            ai_interface: AIInterface instance
        """
        self.name = name
        self.role = role
        self.data_access = data_access
        self.ai = ai_interface

        logger.info(f"Initialized {self.name}: {self.role}")

    @abstractmethod
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method - must be implemented by subclasses.

        Args:
            context: Input context/data to analyze

        Returns:
            Analysis results as dictionary
        """
        pass

    def log_activity(self, action: str, details: str = None):
        """
        Log agent activity to Round Table AI chat log.

        Args:
            action: Action performed (e.g., "Analyzed 5 discoveries")
            details: Optional additional details
        """
        self.data_access.log_ai_activity(
            agent_name=self.name,
            action=action,
            details=details
        )

    def ask_ai(self,
              prompt: str,
              system_prompt: str = None,
              max_tokens: int = 2000,
              temperature: float = 0.7) -> Optional[str]:
        """
        Ask AI a question (convenience wrapper).

        Args:
            prompt: Question/prompt
            system_prompt: System instructions (optional)
            max_tokens: Max response tokens
            temperature: Sampling temperature

        Returns:
            AI response
        """
        # Add agent context to system prompt
        agent_context = f"You are {self.name}, {self.role}"

        if system_prompt:
            full_system_prompt = f"{agent_context}\n\n{system_prompt}"
        else:
            full_system_prompt = agent_context

        return self.ai.complete(
            prompt=prompt,
            system_prompt=full_system_prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )

    def ask_ai_json(self,
                   prompt: str,
                   system_prompt: str = None,
                   max_tokens: int = 2000) -> Optional[Dict]:
        """
        Ask AI for structured JSON response.

        Args:
            prompt: Question/prompt
            system_prompt: System instructions (optional)
            max_tokens: Max response tokens

        Returns:
            Parsed JSON response
        """
        # Add agent context
        agent_context = f"You are {self.name}, {self.role}"

        if system_prompt:
            full_system_prompt = f"{agent_context}\n\n{system_prompt}"
        else:
            full_system_prompt = agent_context

        return self.ai.analyze_json(
            prompt=prompt,
            system_prompt=full_system_prompt,
            max_tokens=max_tokens
        )

    def get_agent_info(self) -> Dict[str, str]:
        """Get agent metadata."""
        return {
            "name": self.name,
            "role": self.role,
            "status": "active"
        }


class AgentTask:
    """
    Represents a task assigned to an agent by the Conductor.

    Attributes:
        task_id: Unique task identifier
        agent_name: Name of assigned agent
        task_type: Type of task (e.g., 'analyze_discoveries')
        context: Task context/input data
        priority: Task priority (1-5, higher is more important)
        status: Current status ('pending', 'in_progress', 'completed', 'failed')
        result: Task result (once completed)
    """

    def __init__(self,
                 task_id: str,
                 agent_name: str,
                 task_type: str,
                 context: Dict[str, Any],
                 priority: int = 3):
        self.task_id = task_id
        self.agent_name = agent_name
        self.task_type = task_type
        self.context = context
        self.priority = priority
        self.status = 'pending'
        self.result: Optional[Dict[str, Any]] = None
        self.created_at = datetime.now()
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None

    def mark_in_progress(self):
        """Mark task as in progress."""
        self.status = 'in_progress'

    def mark_completed(self, result: Dict[str, Any]):
        """Mark task as completed with result."""
        self.status = 'completed'
        self.result = result
        self.completed_at = datetime.now()

    def mark_failed(self, error: str):
        """Mark task as failed with error."""
        self.status = 'failed'
        self.error = error
        self.completed_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            'task_id': self.task_id,
            'agent_name': self.agent_name,
            'task_type': self.task_type,
            'context': self.context,
            'priority': self.priority,
            'status': self.status,
            'result': self.result,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error': self.error
        }
