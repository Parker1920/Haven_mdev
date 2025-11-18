"""
The Archivist - Pattern Analysis Agent
=======================================

Specializes in:
- Real-time pattern detection in discoveries
- Clustering similar discoveries using NLP
- Suggesting pattern names and confidence levels
- Cross-referencing discoveries with locations
- Finding correlations that humans might miss

Priority: ⭐⭐⭐⭐ (High)
"""

import logging
from typing import Dict, List, Optional, Any
from collections import Counter
import json

from ..core.base_agent import BaseAgent
from ..core.ai_interface import AIInterface
from ..data_access import HavenDataAccess

logger = logging.getLogger(__name__)


class ArchivistAgent(BaseAgent):
    """
    The Archivist: Pattern Analysis and Discovery Correlation Specialist.

    The Archivist excels at finding hidden patterns in discovery data,
    grouping similar discoveries, and identifying emerging mysteries.
    """

    def __init__(self, data_access: HavenDataAccess, ai_interface: AIInterface):
        super().__init__(
            name="The Archivist",
            role="Pattern Analysis Co-Pilot - detects patterns, clusters discoveries, and reveals hidden correlations",
            data_access=data_access,
            ai_interface=ai_interface
        )

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method for The Archivist.

        Args:
            context: Should contain either:
                - 'discoveries': List of discovery dicts to analyze
                - 'discovery_ids': List of discovery IDs to fetch and analyze

        Returns:
            Dictionary containing:
                - patterns: List of detected patterns
                - clusters: Grouped discoveries
                - insights: AI-generated insights
                - recommendations: Suggested actions
        """
        # Extract discoveries from context
        discoveries = context.get('discoveries')
        if not discoveries:
            discovery_ids = context.get('discovery_ids', [])
            if discovery_ids:
                # Fetch discoveries by IDs
                discoveries = self._fetch_discoveries_by_ids(discovery_ids)

        if not discoveries:
            # Get recent unanalyzed discoveries
            limit = context.get('limit', 20)
            discoveries = self.data_access.get_unanalyzed_discoveries(limit=limit)

        if not discoveries:
            return {
                'status': 'no_data',
                'message': 'No discoveries to analyze'
            }

        self.log_activity(f"Analyzing {len(discoveries)} discoveries for patterns")

        # Perform pattern analysis
        results = {
            'discoveries_analyzed': len(discoveries),
            'patterns': [],
            'clusters': [],
            'insights': None,
            'recommendations': []
        }

        # 1. Basic statistical pattern detection
        stat_patterns = self._detect_statistical_patterns(discoveries)
        results['patterns'].extend(stat_patterns)

        # 2. AI-powered deep pattern analysis
        ai_patterns = await self._detect_ai_patterns(discoveries)
        if ai_patterns:
            results['patterns'].extend(ai_patterns.get('patterns', []))
            results['insights'] = ai_patterns.get('insights')
            results['recommendations'] = ai_patterns.get('recommendations', [])

        # 3. Update discovery records
        self._update_discovery_analysis(discoveries, results['patterns'])

        self.log_activity(
            f"Pattern analysis complete",
            f"Found {len(results['patterns'])} patterns across {len(discoveries)} discoveries"
        )

        return results

    def _fetch_discoveries_by_ids(self, discovery_ids: List[int]) -> List[Dict]:
        """Fetch specific discoveries by their IDs."""
        # For now, get all and filter (could optimize with SQL IN clause)
        all_discoveries = self.data_access.get_all_discoveries()
        return [d for d in all_discoveries if d.get('id') in discovery_ids]

    def _detect_statistical_patterns(self, discoveries: List[Dict]) -> List[Dict]:
        """
        Detect basic statistical patterns in discoveries.

        Patterns detected:
        - Multiple discoveries of same type in same location
        - Repeated discovery types across different locations
        - Time-based clustering
        - Keyword frequency analysis
        """
        patterns = []

        # Pattern 1: Discovery type frequency
        type_counts = Counter(d.get('discovery_type') for d in discoveries if d.get('discovery_type'))

        for disc_type, count in type_counts.items():
            if count >= 3:  # Threshold: 3+ discoveries of same type
                patterns.append({
                    'pattern_type': 'type_frequency',
                    'pattern_name': f'Multiple {disc_type} discoveries',
                    'discovery_type': disc_type,
                    'count': count,
                    'confidence': min(0.5 + (count * 0.1), 0.95)
                })

        # Pattern 2: Location clustering
        location_counts = Counter()
        for d in discoveries:
            if d.get('system_id'):
                location_counts[d['system_id']] += 1
            elif d.get('location_name'):
                location_counts[d['location_name']] += 1

        for location, count in location_counts.items():
            if count >= 3:  # Threshold: 3+ discoveries in same location
                patterns.append({
                    'pattern_type': 'location_clustering',
                    'pattern_name': f'Activity hotspot in {location}',
                    'location': location,
                    'count': count,
                    'confidence': min(0.4 + (count * 0.1), 0.9)
                })

        # Pattern 3: Keyword extraction from descriptions
        keyword_freq = Counter()
        for d in discoveries:
            desc = d.get('description', '').lower()
            # Extract significant keywords (simple approach)
            words = desc.split()
            significant_words = [w for w in words if len(w) > 5 and w.isalpha()]
            keyword_freq.update(significant_words)

        for keyword, count in keyword_freq.most_common(5):
            if count >= 3:
                patterns.append({
                    'pattern_type': 'keyword_frequency',
                    'pattern_name': f'Recurring theme: "{keyword}"',
                    'keyword': keyword,
                    'count': count,
                    'confidence': min(0.3 + (count * 0.1), 0.85)
                })

        return patterns

    async def _detect_ai_patterns(self, discoveries: List[Dict]) -> Optional[Dict]:
        """
        Use AI to detect complex patterns that statistical methods might miss.

        This is where The Archivist's true power comes in - using LLMs to
        understand narrative patterns, thematic connections, and subtle correlations.
        """
        # Prepare discovery summaries for AI
        discovery_summaries = []
        for d in discoveries[:20]:  # Limit to 20 for token efficiency
            summary = {
                'id': d.get('id'),
                'type': d.get('discovery_type'),
                'location': d.get('location_name') or d.get('system_id'),
                'description': d.get('description', '')[:200],  # Truncate long descriptions
                'time_period': d.get('time_period'),
                'condition': d.get('condition')
            }
            discovery_summaries.append(summary)

        # Build AI prompt
        prompt = f"""Analyze these {len(discovery_summaries)} discoveries from a sci-fi worldbuilding project and identify patterns:

{json.dumps(discovery_summaries, indent=2)}

Look for:
1. Thematic patterns (recurring story elements)
2. Temporal patterns (discoveries from same time period)
3. Narrative connections (discoveries that might be related to same mystery/event)
4. Geographic patterns (spatial clustering with narrative significance)
5. Anomalies (discoveries that stand out or contradict patterns)

Provide your analysis as JSON with:
{{
  "patterns": [
    {{
      "pattern_name": "Clear, evocative name",
      "pattern_type": "thematic|temporal|narrative|geographic|anomaly",
      "confidence": 0.0-1.0,
      "affected_discoveries": [list of discovery IDs],
      "description": "What this pattern means",
      "significance": "Why this matters for the worldbuilding mystery"
    }}
  ],
  "insights": "Overall narrative insights from these discoveries",
  "recommendations": ["Suggested follow-up actions"]
}}"""

        system_prompt = """You are an expert at narrative analysis and pattern recognition in worldbuilding projects.
You excel at finding meaningful connections between disparate pieces of information.
You think like a mystery novelist and a data scientist combined."""

        try:
            response = self.ask_ai_json(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=2000
            )

            if response:
                logger.info(f"AI detected {len(response.get('patterns', []))} patterns")
                return response
            else:
                logger.warning("AI pattern detection returned no results")
                return None

        except Exception as e:
            logger.error(f"AI pattern detection failed: {e}")
            return None

    def _update_discovery_analysis(self, discoveries: List[Dict], patterns: List[Dict]):
        """
        Update discovery records with analysis results.

        Marks discoveries as analyzed and notes pattern matches.
        """
        # Count pattern matches per discovery
        discovery_pattern_counts = Counter()

        for pattern in patterns:
            # Check which discoveries contributed to this pattern
            affected_ids = pattern.get('affected_discoveries', [])
            for disc_id in affected_ids:
                discovery_pattern_counts[disc_id] += 1

        # Update each discovery
        for discovery in discoveries:
            disc_id = discovery.get('id')
            pattern_matches = discovery_pattern_counts.get(disc_id, 0)

            # Determine mystery tier based on pattern matches
            if pattern_matches >= 3:
                mystery_tier = 3  # High significance
            elif pattern_matches >= 1:
                mystery_tier = 2  # Medium significance
            else:
                mystery_tier = 1  # Low significance

            # Update in database
            self.data_access.update_discovery_analysis(
                discovery_id=disc_id,
                analysis_status='analyzed',
                pattern_matches=pattern_matches,
                mystery_tier=mystery_tier
            )

    async def generate_pattern_report(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate a pattern analysis report for recent discoveries.

        Args:
            days: Number of days to look back

        Returns:
            Comprehensive pattern report
        """
        self.log_activity(f"Generating {days}-day pattern report")

        discoveries = self.data_access.get_recent_discoveries(days=days)

        if not discoveries:
            return {
                'status': 'no_data',
                'period': f'{days} days',
                'discoveries_found': 0
            }

        # Run analysis
        analysis = await self.analyze({'discoveries': discoveries})

        # Add metadata
        report = {
            'period': f'{days} days',
            'generated_at': 'now',
            **analysis
        }

        self.log_activity(f"Pattern report generated", f"{len(discoveries)} discoveries, {len(analysis.get('patterns', []))} patterns")

        return report
