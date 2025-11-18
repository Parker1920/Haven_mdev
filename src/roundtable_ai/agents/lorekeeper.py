"""
The Lorekeeper - Narrative Consistency Guardian
================================================

Specializes in:
- Ensuring Keeper bot responses stay in-character
- Maintaining story continuity
- Reviewing bot responses for tone/lore accuracy
- Tracking story progression state
- Flagging contradictions with established lore

Priority: ⭐⭐⭐⭐⭐ (Critical)
"""

import logging
from typing import Dict, List, Optional, Any
import json

from ..core.base_agent import BaseAgent
from ..core.ai_interface import AIInterface
from ..data_access import HavenDataAccess

logger = logging.getLogger(__name__)


class LorekeeperAgent(BaseAgent):
    """
    The Lorekeeper: Narrative Consistency and Keeper Bot Guardian.

    The Lorekeeper ensures that all Keeper bot interactions maintain narrative
    consistency, stay in-character, and advance the mystery story in meaningful ways.
    """

    def __init__(self, data_access: HavenDataAccess, ai_interface: AIInterface):
        super().__init__(
            name="The Lorekeeper",
            role="Narrative Consistency Guardian - ensures Keeper bot stays in-character and maintains story continuity",
            data_access=data_access,
            ai_interface=ai_interface
        )

        # Load Keeper personality/lore guidelines
        self.keeper_personality = self._load_keeper_personality()

    def _load_keeper_personality(self) -> Dict[str, Any]:
        """
        Load Keeper bot's personality and lore guidelines.

        This would ideally be loaded from a configuration file or database.
        For now, returning baseline guidelines.
        """
        return {
            'voice': 'Mysterious, ancient, cryptic yet helpful',
            'knowledge_level': 'Knows about ancient civilizations, mysteries, and patterns',
            'tone': 'Professional but intriguing, never condescending',
            'purpose': 'Guide travelers through discoveries while maintaining mystery',
            'constraints': [
                'Never break the fourth wall',
                'Always acknowledge discoveries as real findings',
                'Maintain air of ancient wisdom',
                'Hint at larger mysteries without revealing everything'
            ]
        }

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method for The Lorekeeper.

        Args:
            context: Can contain:
                - 'keeper_response': Keeper bot response to review
                - 'discovery': Discovery that triggered the response
                - 'analysis_type': 'review_response', 'suggest_response', or 'check_continuity'

        Returns:
            Dictionary containing analysis results and recommendations
        """
        analysis_type = context.get('analysis_type', 'review_response')

        if analysis_type == 'review_response':
            return await self._review_keeper_response(context)
        elif analysis_type == 'suggest_response':
            return await self._suggest_keeper_response(context)
        elif analysis_type == 'check_continuity':
            return await self._check_story_continuity(context)
        else:
            return {'error': f'Unknown analysis_type: {analysis_type}'}

    async def _review_keeper_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review a Keeper bot response for lore accuracy and consistency.

        Args:
            context: Must contain 'keeper_response' and optionally 'discovery'

        Returns:
            Review results with score and suggestions
        """
        keeper_response = context.get('keeper_response')
        discovery = context.get('discovery', {})

        if not keeper_response:
            return {'error': 'No keeper_response provided'}

        self.log_activity("Reviewing Keeper bot response for lore consistency")

        # Build AI prompt for review
        prompt = f"""Review this response from The Keeper bot for a sci-fi worldbuilding project.

KEEPER'S CHARACTER:
{json.dumps(self.keeper_personality, indent=2)}

DISCOVERY CONTEXT:
Type: {discovery.get('discovery_type', 'unknown')}
Description: {discovery.get('description', 'N/A')[:300]}
Location: {discovery.get('location_name') or discovery.get('system_id', 'unknown')}

KEEPER'S RESPONSE:
{keeper_response}

Evaluate the response on:
1. In-character voice (mysterious, ancient, cryptic yet helpful)
2. Tone consistency (professional, intriguing, not condescending)
3. Lore accuracy (acknowledges discovery as real, hints at mysteries)
4. Narrative value (advances story, maintains intrigue)
5. Constraint adherence (no fourth-wall breaks, maintains wisdom)

Provide JSON response:
{{
  "overall_score": 0-100,
  "in_character": 0-100,
  "tone_appropriate": 0-100,
  "lore_accurate": 0-100,
  "narrative_value": 0-100,
  "issues": ["List any problems found"],
  "strengths": ["What works well"],
  "suggestions": ["How to improve if needed"],
  "verdict": "approved|needs_revision|rejected"
}}"""

        try:
            response = self.ask_ai_json(prompt=prompt, max_tokens=1500)

            if response:
                self.log_activity(
                    f"Response reviewed",
                    f"Score: {response.get('overall_score', 0)}/100, Verdict: {response.get('verdict', 'unknown')}"
                )
                return response
            else:
                return {'error': 'AI review failed'}

        except Exception as e:
            logger.error(f"Keeper response review failed: {e}")
            return {'error': str(e)}

    async def _suggest_keeper_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a suggested Keeper bot response for a discovery.

        Args:
            context: Must contain 'discovery'

        Returns:
            Suggested response with variants
        """
        discovery = context.get('discovery', {})

        if not discovery:
            return {'error': 'No discovery provided'}

        self.log_activity(f"Generating Keeper response suggestion for {discovery.get('discovery_type')} discovery")

        # Get recent patterns to inform response
        recent_discoveries = self.data_access.get_recent_discoveries(days=7, limit=10)

        prompt = f"""Generate a response from The Keeper bot for this discovery.

KEEPER'S CHARACTER:
{json.dumps(self.keeper_personality, indent=2)}

DISCOVERY:
Type: {discovery.get('discovery_type')}
Location: {discovery.get('location_name') or discovery.get('system_id')}
Description: {discovery.get('description')}
Condition: {discovery.get('condition')}
Time Period: {discovery.get('time_period')}

RECENT CONTEXT (last 7 days):
{len(recent_discoveries)} discoveries submitted, types: {set(d.get('discovery_type') for d in recent_discoveries)}

Generate a Keeper response that:
1. Acknowledges the discovery in-character
2. Hints at potential significance or patterns
3. Maintains mystery while being helpful
4. Stays true to Keeper's ancient, cryptic voice
5. Is 2-4 sentences long

Provide JSON:
{{
  "suggested_response": "The main response",
  "alternate_versions": ["Two alternate phrasings"],
  "reasoning": "Why this approach works"
}}"""

        try:
            response = self.ask_ai_json(prompt=prompt, max_tokens=1000)

            if response:
                self.log_activity("Generated Keeper response suggestion")
                return response
            else:
                return {'error': 'Failed to generate suggestion'}

        except Exception as e:
            logger.error(f"Keeper response generation failed: {e}")
            return {'error': str(e)}

    async def _check_story_continuity(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for story continuity issues across recent discoveries.

        Returns:
            Report on narrative consistency and potential contradictions
        """
        days = context.get('days', 30)

        self.log_activity(f"Checking story continuity across last {days} days")

        recent_discoveries = self.data_access.get_recent_discoveries(days=days, limit=50)

        if not recent_discoveries:
            return {
                'status': 'no_data',
                'message': 'No recent discoveries to check'
            }

        # Summarize discoveries for AI analysis
        discovery_summaries = [
            {
                'id': d.get('id'),
                'type': d.get('discovery_type'),
                'description': d.get('description', '')[:200],
                'time_period': d.get('time_period'),
                'location': d.get('location_name') or d.get('system_id')
            }
            for d in recent_discoveries[:30]  # Limit for token efficiency
        ]

        prompt = f"""Analyze these {len(discovery_summaries)} discoveries for narrative continuity and potential contradictions:

{json.dumps(discovery_summaries, indent=2)}

Check for:
1. Contradictory information (conflicting facts about same topic)
2. Timeline inconsistencies (temporal contradictions)
3. Location contradictions (impossible spatial relationships)
4. Character/entity inconsistencies
5. Emerging narrative threads that should be highlighted

Return JSON:
{{
  "contradictions": [
    {{
      "type": "timeline|location|factual|character",
      "discovery_ids": [relevant IDs],
      "description": "What contradicts",
      "severity": "minor|moderate|major"
    }}
  ],
  "narrative_threads": [
    {{
      "theme": "Thread name",
      "discovery_ids": [supporting IDs],
      "description": "What's emerging",
      "potential": "Story potential"
    }}
  ],
  "overall_consistency": "excellent|good|fair|poor",
  "recommendations": ["Actions to take"]
}}"""

        try:
            response = self.ask_ai_json(prompt=prompt, max_tokens=2000)

            if response:
                self.log_activity(
                    "Continuity check complete",
                    f"{len(response.get('contradictions', []))} issues, {len(response.get('narrative_threads', []))} threads"
                )
                return response
            else:
                return {'error': 'Continuity check failed'}

        except Exception as e:
            logger.error(f"Story continuity check failed: {e}")
            return {'error': str(e)}

    async def generate_keeper_guidelines_update(self) -> Dict[str, Any]:
        """
        Analyze recent interactions and suggest updates to Keeper personality guidelines.

        Returns:
            Suggested guideline updates based on community feedback and patterns
        """
        self.log_activity("Reviewing Keeper guidelines")

        # This would analyze Keeper bot logs if available
        # For now, return current guidelines
        return {
            'current_guidelines': self.keeper_personality,
            'suggestions': [],
            'note': 'Keeper bot log integration not yet implemented'
        }
