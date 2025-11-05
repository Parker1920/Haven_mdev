"""
System Entry Model

Business logic and data model for star system entry.
Separate from UI concerns for better testability and maintainability.

Classes:
    - SystemModel: Represents a star system with planets and moons
    - PlanetModel: Represents a planet within a system
    - MoonModel: Represents a moon within a planet
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class MoonModel:
    """Model for a moon within a planet."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    type: Optional[str] = None

    def validate(self) -> Tuple[bool, str]:
        """Validate moon data."""
        if not self.name or not self.name.strip():
            return False, "Moon name cannot be empty"

        if len(self.name) > 100:
            return False, f"Moon name too long (max 100 chars, got {len(self.name)})"

        return True, ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MoonModel":
        """Create from dictionary."""
        return cls(
            id=data.get("id", uuid.uuid4().hex[:12]),
            name=data.get("name", ""),
            type=data.get("type")
        )


@dataclass
class PlanetModel:
    """Model for a planet within a system."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    type: Optional[str] = None
    moons: List[MoonModel] = field(default_factory=list)

    def validate(self) -> Tuple[bool, str]:
        """Validate planet data."""
        if not self.name or not self.name.strip():
            return False, "Planet name cannot be empty"

        if len(self.name) > 100:
            return False, f"Planet name too long (max 100 chars, got {len(self.name)})"

        # Validate all moons
        for moon in self.moons:
            is_valid, error = moon.validate()
            if not is_valid:
                return False, f"Moon '{self.name}': {error}"

        return True, ""

    def add_moon(self, moon: MoonModel) -> None:
        """Add a moon to this planet."""
        if isinstance(moon, MoonModel):
            self.moons.append(moon)

    def remove_moon(self, moon_id: str) -> bool:
        """Remove a moon by ID."""
        initial_len = len(self.moons)
        self.moons = [m for m in self.moons if m.id != moon_id]
        return len(self.moons) < initial_len

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "moons": [m.to_dict() for m in self.moons]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlanetModel":
        """Create from dictionary."""
        moons = [
            MoonModel.from_dict(m)
            for m in data.get("moons", [])
        ]
        return cls(
            id=data.get("id", uuid.uuid4().hex[:12]),
            name=data.get("name", ""),
            type=data.get("type"),
            moons=moons
        )


@dataclass
class SystemModel:
    """Model for a star system."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    region: str = ""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    planets: List[PlanetModel] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    notes: Optional[str] = None

    def validate(self) -> Tuple[bool, str]:
        """Validate system data."""
        # Name validation
        if not self.name or not self.name.strip():
            return False, "System name cannot be empty"

        if len(self.name) > 100:
            return False, f"System name too long (max 100 chars, got {len(self.name)})"

        # Region validation
        if not self.region or not self.region.strip():
            return False, "Region cannot be empty"

        # Coordinate validation
        if not isinstance(self.x, (int, float)):
            return False, f"X coordinate must be a number, got {type(self.x).__name__}"
        if not isinstance(self.y, (int, float)):
            return False, f"Y coordinate must be a number, got {type(self.y).__name__}"
        if not isinstance(self.z, (int, float)):
            return False, f"Z coordinate must be a number, got {type(self.z).__name__}"

        if not (-100 <= self.x <= 100):
            return False, f"X coordinate must be between -100 and 100 (got {self.x})"
        if not (-100 <= self.y <= 100):
            return False, f"Y coordinate must be between -100 and 100 (got {self.y})"
        if not (-25 <= self.z <= 25):
            return False, f"Z coordinate must be between -25 and 25 (got {self.z})"

        # Validate all planets
        for planet in self.planets:
            is_valid, error = planet.validate()
            if not is_valid:
                return False, f"Planet '{planet.name}': {error}"

        return True, ""

    def add_planet(self, planet: PlanetModel) -> None:
        """Add a planet to this system."""
        if isinstance(planet, PlanetModel):
            self.planets.append(planet)

    def remove_planet(self, planet_id: str) -> bool:
        """Remove a planet by ID."""
        initial_len = len(self.planets)
        self.planets = [p for p in self.planets if p.id != planet_id]
        return len(self.planets) < initial_len

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (JSON-compatible)."""
        return {
            "id": self.id,
            "name": self.name,
            "region": self.region,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "planets": [p.to_dict() for p in self.planets],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SystemModel":
        """Create system from dictionary (JSON-compatible)."""
        planets = [
            PlanetModel.from_dict(p)
            for p in data.get("planets", [])
        ]
        return cls(
            id=data.get("id", uuid.uuid4().hex[:12]),
            name=data.get("name", ""),
            region=data.get("region", ""),
            x=float(data.get("x", 0)),
            y=float(data.get("y", 0)),
            z=float(data.get("z", 0)),
            planets=planets,
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            notes=data.get("notes")
        )

    def update_timestamp(self) -> None:
        """Update the last modified timestamp."""
        self.updated_at = datetime.now().isoformat()
