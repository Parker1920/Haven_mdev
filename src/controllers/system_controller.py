"""
System Entry Controller

Handles business logic for system entry operations.
Separates UI concerns from data management.

Classes:
    - SystemEntryController: Main controller for system operations
"""

import logging
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import json

from models.system_model import SystemModel, PlanetModel, MoonModel
from common.paths import data_path
from common.validation import validate_system_data
from common.file_lock import FileLock

logger = logging.getLogger(__name__)


class SystemEntryController:
    """Controller for system entry operations."""

    def __init__(self):
        """Initialize controller."""
        self.data_file = data_path("data.json")
        self.backup_suffix = ".bak"

    def load_all_systems(self) -> Dict[str, SystemModel]:
        """Load all systems from data file."""
        try:
            if not self.data_file.exists():
                logger.info(f"Data file not found: {self.data_file}")
                return {}

            with FileLock(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

            systems = {}
            for key, value in data.items():
                if key == "_meta":
                    continue
                try:
                    system = SystemModel.from_dict(value)
                    systems[system.name] = system
                except Exception as e:
                    logger.error(f"Error loading system '{key}': {e}")

            return systems

        except Exception as e:
            logger.error(f"Error loading systems: {e}")
            return {}

    def save_system(self, system: SystemModel) -> Tuple[bool, str]:
        """Save a system to the data file."""
        try:
            # Validate system
            is_valid, error = system.validate()
            if not is_valid:
                return False, error

            # Load existing data
            if self.data_file.exists():
                with FileLock(self.data_file):
                    with open(self.data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
            else:
                data = {"_meta": {"version": "3.0.0"}}

            # Ensure _meta exists
            if "_meta" not in data:
                data["_meta"] = {"version": "3.0.0"}

            # Add or update system
            system.update_timestamp()
            data[system.name] = system.to_dict()

            # Create backup
            backup_path = self.data_file.with_suffix(
                self.data_file.suffix + self.backup_suffix
            )

            # Write with lock
            with FileLock(self.data_file):
                if self.data_file.exists():
                    import shutil
                    shutil.copy2(self.data_file, backup_path)

                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"System saved: {system.name}")
            return True, "System saved successfully"

        except Exception as e:
            logger.error(f"Error saving system: {e}")
            return False, f"Error saving system: {e}"

    def delete_system(self, system_name: str) -> Tuple[bool, str]:
        """Delete a system from the data file."""
        try:
            if not self.data_file.exists():
                return False, "Data file not found"

            with FileLock(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if system_name not in data:
                    return False, f"System '{system_name}' not found"

                del data[system_name]

                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"System deleted: {system_name}")
            return True, "System deleted successfully"

        except Exception as e:
            logger.error(f"Error deleting system: {e}")
            return False, f"Error deleting system: {e}"

    def duplicate_system(self, original_name: str, new_name: str) -> Tuple[bool, str]:
        """Duplicate an existing system with a new name."""
        try:
            systems = self.load_all_systems()

            if original_name not in systems:
                return False, f"System '{original_name}' not found"

            # Create new system with copied data
            original = systems[original_name]
            new_system = SystemModel(
                name=new_name,
                region=original.region,
                x=original.x,
                y=original.y,
                z=original.z,
                planets=[
                    PlanetModel(
                        name=p.name,
                        type=p.type,
                        moons=[MoonModel(name=m.name, type=m.type) for m in p.moons]
                    )
                    for p in original.planets
                ],
                notes=original.notes
            )

            return self.save_system(new_system)

        except Exception as e:
            logger.error(f"Error duplicating system: {e}")
            return False, f"Error duplicating system: {e}"

    def export_systems_json(
        self,
        systems: List[SystemModel],
        output_path: Path
    ) -> Tuple[bool, str]:
        """Export systems to a JSON file."""
        try:
            data = {
                "_meta": {"version": "3.0.0"},
            }

            for system in systems:
                is_valid, error = system.validate()
                if not is_valid:
                    return False, f"System '{system.name}' validation error: {error}"

                data[system.name] = system.to_dict()

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Systems exported to {output_path}")
            return True, f"Exported {len(systems)} system(s)"

        except Exception as e:
            logger.error(f"Error exporting systems: {e}")
            return False, f"Error exporting systems: {e}"
