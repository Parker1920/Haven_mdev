"""
Haven Data Access Layer
========================

Unified interface for accessing all Haven data sources:
- haven_ui.db: Systems, planets, moons, discoveries, space stations
- keeper.db: Keeper bot discoveries, patterns, investigations
- data.json: Legacy map data (deprecated but supported)

This layer abstracts database operations so AI agents can focus on logic.
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class HavenDataAccess:
    """
    Unified data access for Round Table AI agents.

    Provides read access to all Haven databases and handles
    connection management, error handling, and data normalization.
    """

    def __init__(self, haven_ui_db_path: str, keeper_db_path: str = None, data_json_path: str = None):
        """
        Initialize data access layer.

        Args:
            haven_ui_db_path: Path to Haven-UI/data/haven_ui.db
            keeper_db_path: Path to keeper.db (optional, for Keeper bot integration)
            data_json_path: Path to data.json (optional, for legacy support)
        """
        self.haven_ui_db = Path(haven_ui_db_path)
        self.keeper_db = Path(keeper_db_path) if keeper_db_path else None
        self.data_json = Path(data_json_path) if data_json_path else None

        if not self.haven_ui_db.exists():
            raise FileNotFoundError(f"Haven UI database not found: {self.haven_ui_db}")

        logger.info(f"Initialized HavenDataAccess with haven_ui.db: {self.haven_ui_db}")
        if self.keeper_db:
            logger.info(f"  - keeper.db: {self.keeper_db}")

    @contextmanager
    def _haven_ui_connection(self):
        """Context manager for haven_ui.db connections."""
        conn = sqlite3.connect(self.haven_ui_db)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def _keeper_connection(self):
        """Context manager for keeper.db connections."""
        if not self.keeper_db or not self.keeper_db.exists():
            raise FileNotFoundError(f"Keeper database not available: {self.keeper_db}")

        conn = sqlite3.connect(self.keeper_db)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    # ==================== DISCOVERY QUERIES ====================

    def get_all_discoveries(self, limit: int = None, discovery_type: str = None) -> List[Dict]:
        """
        Get all discoveries from haven_ui.db.

        Args:
            limit: Maximum number of discoveries to return
            discovery_type: Filter by discovery type (artifact, structure, etc.)

        Returns:
            List of discovery dictionaries
        """
        with self._haven_ui_connection() as conn:
            query = "SELECT * FROM discoveries WHERE 1=1"
            params = []

            if discovery_type:
                query += " AND discovery_type = ?"
                params.append(discovery_type)

            query += " ORDER BY submission_timestamp DESC"

            if limit:
                query += " LIMIT ?"
                params.append(limit)

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def get_recent_discoveries(self, days: int = 7, limit: int = 100) -> List[Dict]:
        """
        Get discoveries from the last N days.

        Args:
            days: Number of days to look back
            limit: Maximum number of discoveries

        Returns:
            List of recent discoveries
        """
        with self._haven_ui_connection() as conn:
            query = """
                SELECT * FROM discoveries
                WHERE submission_timestamp >= datetime('now', '-' || ? || ' days')
                ORDER BY submission_timestamp DESC
                LIMIT ?
            """
            cursor = conn.execute(query, (days, limit))
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def get_discoveries_by_location(self, system_id: str = None, planet_id: int = None,
                                   moon_id: int = None) -> List[Dict]:
        """
        Get discoveries filtered by location.

        Args:
            system_id: Filter by system
            planet_id: Filter by planet
            moon_id: Filter by moon

        Returns:
            List of discoveries at the specified location
        """
        with self._haven_ui_connection() as conn:
            query = "SELECT * FROM discoveries WHERE 1=1"
            params = []

            if system_id:
                query += " AND system_id = ?"
                params.append(system_id)
            if planet_id:
                query += " AND planet_id = ?"
                params.append(planet_id)
            if moon_id:
                query += " AND moon_id = ?"
                params.append(moon_id)

            query += " ORDER BY submission_timestamp DESC"

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def get_discoveries_by_type(self, discovery_type: str) -> List[Dict]:
        """Get all discoveries of a specific type."""
        return self.get_all_discoveries(discovery_type=discovery_type)

    def get_unanalyzed_discoveries(self, limit: int = 50) -> List[Dict]:
        """
        Get discoveries that haven't been analyzed yet.

        Returns:
            List of discoveries with analysis_status = 'pending'
        """
        with self._haven_ui_connection() as conn:
            query = """
                SELECT * FROM discoveries
                WHERE analysis_status = 'pending'
                ORDER BY submission_timestamp ASC
                LIMIT ?
            """
            cursor = conn.execute(query, (limit,))
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def get_discovery_statistics(self) -> Dict[str, Any]:
        """
        Get statistical overview of discoveries.

        Returns:
            Dictionary with discovery stats
        """
        with self._haven_ui_connection() as conn:
            stats = {}

            # Total count
            cursor = conn.execute("SELECT COUNT(*) FROM discoveries")
            stats['total_count'] = cursor.fetchone()[0]

            # By type
            cursor = conn.execute("""
                SELECT discovery_type, COUNT(*) as count
                FROM discoveries
                GROUP BY discovery_type
                ORDER BY count DESC
            """)
            stats['by_type'] = {row[0]: row[1] for row in cursor.fetchall()}

            # By analysis status
            cursor = conn.execute("""
                SELECT analysis_status, COUNT(*) as count
                FROM discoveries
                GROUP BY analysis_status
            """)
            stats['by_analysis_status'] = {row[0]: row[1] for row in cursor.fetchall()}

            # Recent activity (last 7 days)
            cursor = conn.execute("""
                SELECT COUNT(*) FROM discoveries
                WHERE submission_timestamp >= datetime('now', '-7 days')
            """)
            stats['last_7_days'] = cursor.fetchone()[0]

            # Top submitters
            cursor = conn.execute("""
                SELECT discovered_by, COUNT(*) as count
                FROM discoveries
                WHERE discovered_by IS NOT NULL
                GROUP BY discovered_by
                ORDER BY count DESC
                LIMIT 10
            """)
            stats['top_submitters'] = {row[0]: row[1] for row in cursor.fetchall()}

            return stats

    # ==================== SYSTEMS QUERIES ====================

    def get_all_systems(self, region: str = None) -> List[Dict]:
        """
        Get all systems from haven_ui.db.

        Args:
            region: Filter by region

        Returns:
            List of system dictionaries
        """
        with self._haven_ui_connection() as conn:
            if region:
                cursor = conn.execute("SELECT * FROM systems WHERE region = ?", (region,))
            else:
                cursor = conn.execute("SELECT * FROM systems")

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_system_by_id(self, system_id: str) -> Optional[Dict]:
        """Get a specific system by ID."""
        with self._haven_ui_connection() as conn:
            cursor = conn.execute("SELECT * FROM systems WHERE id = ?", (system_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_system_by_name(self, name: str) -> Optional[Dict]:
        """Get a specific system by name."""
        with self._haven_ui_connection() as conn:
            cursor = conn.execute("SELECT * FROM systems WHERE name = ?", (name,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_planets_for_system(self, system_id: str) -> List[Dict]:
        """Get all planets in a system."""
        with self._haven_ui_connection() as conn:
            cursor = conn.execute("SELECT * FROM planets WHERE system_id = ?", (system_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_moons_for_planet(self, planet_id: int) -> List[Dict]:
        """Get all moons for a planet."""
        with self._haven_ui_connection() as conn:
            cursor = conn.execute("SELECT * FROM moons WHERE planet_id = ?", (planet_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    # ==================== KEEPER DATABASE QUERIES ====================

    def get_keeper_discoveries(self, limit: int = 100) -> List[Dict]:
        """
        Get discoveries from keeper.db (Keeper bot).

        Note: This is separate from haven_ui.db discoveries.
        """
        try:
            with self._keeper_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM discoveries
                    ORDER BY submission_timestamp DESC
                    LIMIT ?
                """, (limit,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except FileNotFoundError:
            logger.warning("Keeper database not available")
            return []

    def get_keeper_patterns(self) -> List[Dict]:
        """Get all patterns detected by The Keeper."""
        try:
            with self._keeper_connection() as conn:
                cursor = conn.execute("SELECT * FROM patterns ORDER BY last_updated DESC")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except (FileNotFoundError, sqlite3.OperationalError):
            logger.warning("Keeper patterns table not available")
            return []

    def get_keeper_investigations(self) -> List[Dict]:
        """Get all active investigations from The Keeper."""
        try:
            with self._keeper_connection() as conn:
                cursor = conn.execute("SELECT * FROM investigations ORDER BY created_at DESC")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except (FileNotFoundError, sqlite3.OperationalError):
            logger.warning("Keeper investigations table not available")
            return []

    # ==================== WRITE OPERATIONS ====================

    def update_discovery_analysis(self, discovery_id: int, analysis_status: str,
                                 pattern_matches: int = None, mystery_tier: int = None,
                                 tags: str = None) -> None:
        """
        Update discovery analysis results.

        Args:
            discovery_id: ID of the discovery
            analysis_status: New status (e.g., 'analyzed', 'pattern_detected')
            pattern_matches: Number of pattern matches found
            mystery_tier: Mystery tier level (1-5)
            tags: Comma-separated tags
        """
        with self._haven_ui_connection() as conn:
            updates = ["analysis_status = ?"]
            params = [analysis_status]

            if pattern_matches is not None:
                updates.append("pattern_matches = ?")
                params.append(pattern_matches)

            if mystery_tier is not None:
                updates.append("mystery_tier = ?")
                params.append(mystery_tier)

            if tags is not None:
                updates.append("tags = ?")
                params.append(tags)

            params.append(discovery_id)

            query = f"UPDATE discoveries SET {', '.join(updates)} WHERE id = ?"
            conn.execute(query, params)
            conn.commit()

            logger.info(f"Updated discovery {discovery_id}: status={analysis_status}")

    def log_ai_activity(self, agent_name: str, action: str, details: str = None) -> None:
        """
        Log AI agent activity to the Round Table AI chat log.

        Args:
            agent_name: Name of the agent (e.g., "Archivist", "Sentinel")
            action: Action performed
            details: Optional additional details
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {agent_name}: {action}"
        if details:
            log_entry += f" - {details}"

        # Write to ai_chat.log
        log_file = self.haven_ui_db.parent.parent / 'logs' / 'ai_chat.log'
        log_file.parent.mkdir(exist_ok=True)

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')

        logger.debug(f"AI Activity: {log_entry}")


# Convenience function for creating data access instance
def create_haven_data_access(haven_ui_root: Path = None) -> HavenDataAccess:
    """
    Create a HavenDataAccess instance with default paths.

    Args:
        haven_ui_root: Root directory of Haven-UI (auto-detected if not provided)

    Returns:
        Configured HavenDataAccess instance
    """
    if haven_ui_root is None:
        # Try to auto-detect
        from src.common.paths import project_root
        haven_ui_root = project_root() / 'Haven-UI'

    haven_ui_db = haven_ui_root / 'data' / 'haven_ui.db'
    keeper_db = project_root() / 'keeper.db' if 'project_root' in locals() else None

    return HavenDataAccess(
        haven_ui_db_path=str(haven_ui_db),
        keeper_db_path=str(keeper_db) if keeper_db and keeper_db.exists() else None
    )
