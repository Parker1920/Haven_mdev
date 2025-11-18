"""
Round Table AI - Multi-Agent System for Haven_mdev
====================================================

A modular framework of specialized AI assistants that collaborate to:
- Analyze discovery submissions for patterns
- Monitor community engagement
- Ensure narrative consistency
- Generate content and insights
- Orchestrate complex workflows

Architecture:
- Conductor: Central orchestrator coordinating all agents
- Agents: Specialized assistants (Sentinel, Archivist, Lorekeeper, etc.)
- Cloud AI Interface: Abstraction layer for Claude/GPT/other LLMs
- Data Access: Unified interface to keeper.db, haven_ui.db, and data.json
"""

__version__ = "0.1.0"
