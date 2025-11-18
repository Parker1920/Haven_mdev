"""
The Sentinel - Community Health Monitor
========================================

Specializes in:
- Tracking Discord activity and engagement
- Detecting quiet periods and suggesting campaigns
- Flagging potential abuse or spam
- Monitoring system health and security
- User engagement analytics

Priority: ⭐⭐⭐⭐⭐ (Critical)
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from ..core.base_agent import BaseAgent
from ..core.ai_interface import AIInterface
from ..data_access import HavenDataAccess

logger = logging.getLogger(__name__)


class SentinelAgent(BaseAgent):
    """
    The Sentinel: Community Health and Security Monitor.

    The Sentinel watches over the Haven community, tracking engagement,
    identifying issues, and suggesting proactive campaigns to maintain healthy activity.
    """

    def __init__(self, data_access: HavenDataAccess, ai_interface: AIInterface):
        super().__init__(
            name="The Sentinel",
            role="Community Health Monitor - tracks engagement, detects issues, and ensures system security",
            data_access=data_access,
            ai_interface=ai_interface
        )

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method for The Sentinel.

        Args:
            context: Can contain:
                - 'analysis_type': 'engagement', 'security', 'health', or 'full'
                - 'period_days': Number of days to analyze (default: 7)

        Returns:
            Dictionary containing health metrics and recommendations
        """
        analysis_type = context.get('analysis_type', 'full')
        period_days = context.get('period_days', 7)

        self.log_activity(f"Running {analysis_type} analysis for last {period_days} days")

        results = {
            'analysis_type': analysis_type,
            'period_days': period_days,
            'timestamp': datetime.now().isoformat()
        }

        # Run requested analysis
        if analysis_type in ['engagement', 'full']:
            results['engagement'] = self._analyze_engagement(period_days)

        if analysis_type in ['health', 'full']:
            results['health'] = self._analyze_system_health()

        if analysis_type in ['security', 'full']:
            results['security'] = self._analyze_security(period_days)

        # Generate AI-powered recommendations
        if analysis_type == 'full':
            results['ai_recommendations'] = await self._generate_recommendations(results)

        self.log_activity(f"Completed {analysis_type} analysis")

        return results

    def _analyze_engagement(self, days: int) -> Dict[str, Any]:
        """Analyze community engagement metrics."""
        stats = self.data_access.get_discovery_statistics()
        recent_discoveries = self.data_access.get_recent_discoveries(days=days)

        engagement = {
            'total_discoveries_alltime': stats.get('total_count', 0),
            'discoveries_last_period': len(recent_discoveries),
            'discoveries_per_day': len(recent_discoveries) / days if days > 0 else 0,
            'active_contributors': len(set(d.get('discovered_by') for d in recent_discoveries if d.get('discovered_by'))),
            'discovery_types': {},
            'top_contributors': [],
            'status': 'healthy'
        }

        # Calculate discovery types distribution
        type_counts = {}
        for d in recent_discoveries:
            dtype = d.get('discovery_type', 'unknown')
            type_counts[dtype] = type_counts.get(dtype, 0) + 1
        engagement['discovery_types'] = type_counts

        # Top contributors
        contributor_counts = {}
        for d in recent_discoveries:
            contributor = d.get('discovered_by')
            if contributor:
                contributor_counts[contributor] = contributor_counts.get(contributor, 0) + 1

        engagement['top_contributors'] = [
            {'user': k, 'count': v}
            for k, v in sorted(contributor_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        # Determine status
        daily_rate = engagement['discoveries_per_day']
        if daily_rate < 0.5:
            engagement['status'] = 'low'
            engagement['alert'] = f'Low engagement: Only {daily_rate:.1f} discoveries per day'
        elif daily_rate < 1.0:
            engagement['status'] = 'moderate'
        else:
            engagement['status'] = 'healthy'

        return engagement

    def _analyze_system_health(self) -> Dict[str, Any]:
        """Analyze overall system health."""
        stats = self.data_access.get_discovery_statistics()

        health = {
            'database_status': 'operational',
            'total_discoveries': stats.get('total_count', 0),
            'analysis_backlog': stats.get('by_analysis_status', {}).get('pending', 0),
            'systems_mapped': len(self.data_access.get_all_systems()),
            'data_quality': {
                'discoveries_with_location': 0,
                'discoveries_with_description': 0
            },
            'status': 'healthy'
        }

        # Quick data quality check
        all_discoveries = self.data_access.get_all_discoveries(limit=100)
        if all_discoveries:
            with_location = sum(1 for d in all_discoveries if d.get('system_id') or d.get('location_name'))
            with_desc = sum(1 for d in all_discoveries if d.get('description'))

            health['data_quality']['discoveries_with_location'] = (with_location / len(all_discoveries)) * 100
            health['data_quality']['discoveries_with_description'] = (with_desc / len(all_discoveries)) * 100

        # Check for issues
        if health['analysis_backlog'] > 50:
            health['status'] = 'warning'
            health['alert'] = f'Large analysis backlog: {health["analysis_backlog"]} pending'

        return health

    def _analyze_security(self, days: int) -> Dict[str, Any]:
        """Analyze for potential security issues or spam."""
        recent_discoveries = self.data_access.get_recent_discoveries(days=days)

        security = {
            'suspicious_activity': [],
            'spam_detected': False,
            'duplicate_submissions': 0,
            'status': 'secure'
        }

        # Check for suspicious patterns
        # 1. High volume from single user
        user_counts = {}
        for d in recent_discoveries:
            user = d.get('discovered_by') or d.get('discord_user_id')
            if user:
                user_counts[user] = user_counts.get(user, 0) + 1

        for user, count in user_counts.items():
            if count > 20:  # More than 20 discoveries in period
                security['suspicious_activity'].append({
                    'type': 'high_volume',
                    'user': user,
                    'count': count,
                    'severity': 'medium'
                })

        # 2. Check for duplicate descriptions (potential spam)
        descriptions = [d.get('description', '')[:100].lower() for d in recent_discoveries]
        from collections import Counter
        desc_counts = Counter(descriptions)

        for desc, count in desc_counts.items():
            if count > 3 and len(desc) > 10:  # Same description 3+ times
                security['duplicate_submissions'] += 1

        if security['duplicate_submissions'] > 5:
            security['spam_detected'] = True
            security['status'] = 'warning'

        return security

    async def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """
        Use AI to generate actionable recommendations based on analysis.

        Args:
            analysis_results: Results from engagement, health, and security analysis

        Returns:
            List of recommended actions
        """
        import json

        prompt = f"""Based on this community health analysis, provide 3-5 specific, actionable recommendations:

{json.dumps(analysis_results, indent=2)}

Recommendations should:
1. Address any alerts or warnings
2. Suggest ways to improve engagement if it's low
3. Propose campaigns or events to maintain momentum
4. Highlight positive trends to celebrate

Return as JSON:
{{
  "recommendations": [
    {{
      "priority": "high|medium|low",
      "category": "engagement|quality|security|celebration",
      "action": "Specific action to take",
      "reasoning": "Why this is important"
    }}
  ]
}}"""

        try:
            response = self.ask_ai_json(prompt=prompt, max_tokens=1000)

            if response and 'recommendations' in response:
                return response['recommendations']
            else:
                return []
        except Exception as e:
            logger.error(f"Failed to generate AI recommendations: {e}")
            return []

    async def generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily community health report."""
        self.log_activity("Generating daily report")

        report = await self.analyze({
            'analysis_type': 'full',
            'period_days': 1
        })

        self.log_activity("Daily report generated")
        return report
