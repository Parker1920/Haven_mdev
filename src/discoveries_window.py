"""
Discoveries Viewer Window
Displays discoveries from Discord bot for a specific location (planet/moon)
"""
import customtkinter as ctk
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Import color scheme from control room
from control_room import COLORS


class DiscoveriesWindow(ctk.CTkToplevel):
    """Window to display discoveries for a planet or moon"""

    def __init__(self, parent, location_data: Dict, db):
        """
        Initialize discoveries window

        Args:
            parent: Parent window
            location_data: Dictionary with location info (system_id, planet_id, moon_id, name, type)
            db: HavenDatabase instance
        """
        super().__init__(parent)

        self.db = db
        self.location_data = location_data
        self.discoveries = []

        # Window setup
        self.title(f"Discoveries - {location_data.get('name', 'Unknown')}")
        self.geometry("900x700")

        # Set theme colors
        self.configure(fg_color=COLORS['bg_dark'])

        # Make window modal
        self.transient(parent)
        self.grab_set()

        # Build UI
        self._build_ui()

        # Load discoveries
        self._load_discoveries()

    def _build_ui(self):
        """Build the discoveries window UI"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color=COLORS['glass'], corner_radius=12)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        # Location info
        location_type = self.location_data.get('type', 'Location')
        location_name = self.location_data.get('name', 'Unknown')
        system_name = self.location_data.get('system_name', 'Unknown System')

        title_label = ctk.CTkLabel(
            header_frame,
            text=f"🔍 Discoveries",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=COLORS['text_primary']
        )
        title_label.pack(padx=20, pady=(15, 5))

        location_label = ctk.CTkLabel(
            header_frame,
            text=f"{location_type.title()}: {location_name} ({system_name})",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=COLORS['text_secondary']
        )
        location_label.pack(padx=20, pady=(0, 15))

        # Filter controls
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            filter_frame,
            text="Filter by type:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS['text_secondary']
        ).pack(side="left", padx=(0, 10))

        self.filter_var = ctk.StringVar(value="All")
        filter_options = ["All", "Ruins", "Fossils", "Logs", "Technology", "Flora/Fauna", "Minerals", "Ships", "Hazards", "Lore"]

        self.filter_dropdown = ctk.CTkOptionMenu(
            filter_frame,
            variable=self.filter_var,
            values=filter_options,
            command=self._filter_discoveries,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=COLORS['glass'],
            button_color=COLORS['accent_purple'],
            button_hover_color=COLORS['accent_cyan'],
            dropdown_fg_color=COLORS['glass'],
            dropdown_hover_color=COLORS['accent_purple'],
            width=150
        )
        self.filter_dropdown.pack(side="left")

        # Refresh button
        refresh_btn = ctk.CTkButton(
            filter_frame,
            text="🔄 Refresh",
            command=self._load_discoveries,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=COLORS['glass'],
            hover_color=COLORS['accent_purple'],
            width=100,
            height=32
        )
        refresh_btn.pack(side="right")

        # Scrollable frame for discoveries
        self.discoveries_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS['accent_purple'],
            scrollbar_button_hover_color=COLORS['accent_cyan']
        )
        self.discoveries_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Footer with close button
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(fill="x", padx=20, pady=(0, 20))

        close_btn = ctk.CTkButton(
            footer_frame,
            text="Close",
            command=self.destroy,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=COLORS['glass'],
            hover_color=COLORS['accent_purple'],
            width=120,
            height=36
        )
        close_btn.pack(side="right")

    def _load_discoveries(self):
        """Load discoveries from database"""
        try:
            # Clear existing discoveries
            for widget in self.discoveries_frame.winfo_children():
                widget.destroy()

            # Get discoveries based on location type
            system_id = self.location_data.get('system_id')
            planet_id = self.location_data.get('planet_id')
            moon_id = self.location_data.get('moon_id')

            with self.db as database:
                if moon_id:
                    self.discoveries = database.get_discoveries(moon_id=moon_id, limit=1000)
                elif planet_id:
                    self.discoveries = database.get_discoveries(planet_id=planet_id, limit=1000)
                elif system_id:
                    self.discoveries = database.get_discoveries(system_id=system_id, limit=1000)
                else:
                    self.discoveries = []

            if not self.discoveries:
                self._show_no_discoveries()
            else:
                self._display_discoveries(self.discoveries)

            logger.info(f"Loaded {len(self.discoveries)} discoveries for {self.location_data.get('name')}")

        except Exception as e:
            logger.error(f"Failed to load discoveries: {e}")
            self._show_error()

    def _show_no_discoveries(self):
        """Display message when no discoveries found"""
        no_data_label = ctk.CTkLabel(
            self.discoveries_frame,
            text="🔭 No discoveries yet\n\nBe the first to report a discovery here using\nThe Keeper Discord bot!",
            font=ctk.CTkFont(family="Segoe UI", size=16),
            text_color=COLORS['text_secondary'],
            justify="center"
        )
        no_data_label.pack(pady=100)

    def _show_error(self):
        """Display error message"""
        error_label = ctk.CTkLabel(
            self.discoveries_frame,
            text="⚠️ Error loading discoveries\n\nPlease try again",
            font=ctk.CTkFont(family="Segoe UI", size=16),
            text_color=COLORS['text_secondary'],
            justify="center"
        )
        error_label.pack(pady=100)

    def _display_discoveries(self, discoveries: List[Dict]):
        """Display list of discoveries"""
        for discovery in discoveries:
            self._create_discovery_card(discovery)

    def _create_discovery_card(self, discovery: Dict):
        """Create a card for a single discovery"""
        # Card frame
        card = ctk.CTkFrame(
            self.discoveries_frame,
            fg_color=COLORS['glass'],
            corner_radius=12,
            border_width=2,
            border_color=COLORS['accent_purple']
        )
        card.pack(fill="x", pady=8, padx=5)

        # Header with type and date
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))

        # Discovery type icon and name
        discovery_type = discovery.get('discovery_type', 'Unknown')
        type_icon = self._get_type_icon(discovery_type)

        type_label = ctk.CTkLabel(
            header,
            text=f"{type_icon} {discovery_type.replace('_', ' ').title()}",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLORS['accent_cyan']
        )
        type_label.pack(side="left")

        # Mystery tier badge (if applicable)
        mystery_tier = discovery.get('mystery_tier', 0)
        if mystery_tier > 0:
            tier_names = ["", "Surface Anomaly", "Deep Mystery", "Cosmic Enigma", "Cosmic Significance"]
            tier_name = tier_names[min(mystery_tier, len(tier_names) - 1)]

            tier_badge = ctk.CTkLabel(
                header,
                text=f"⭐ {tier_name}",
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=COLORS['accent_purple'],
                fg_color=COLORS['bg_dark'],
                corner_radius=8,
                padx=10,
                pady=3
            )
            tier_badge.pack(side="right")

        # Timestamp
        timestamp = discovery.get('submission_timestamp', '')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime('%Y-%m-%d %H:%M UTC')
            except:
                time_str = timestamp
        else:
            time_str = 'Unknown date'

        date_label = ctk.CTkLabel(
            header,
            text=f"📅 {time_str}",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS['text_secondary']
        )
        date_label.pack(side="right", padx=(0, 10))

        # Description
        description = discovery.get('description', 'No description provided')
        desc_label = ctk.CTkLabel(
            card,
            text=description,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS['text_primary'],
            wraplength=820,
            justify="left"
        )
        desc_label.pack(fill="x", padx=15, pady=(0, 10), anchor="w")

        # Details section
        details = []

        condition = discovery.get('condition')
        if condition:
            details.append(f"🔧 Condition: {condition}")

        time_period = discovery.get('time_period')
        if time_period:
            details.append(f"⏳ Era: {time_period}")

        coordinates = discovery.get('coordinates')
        if coordinates:
            details.append(f"📍 Coordinates: {coordinates}")

        if details:
            details_text = " • ".join(details)
            details_label = ctk.CTkLabel(
                card,
                text=details_text,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=COLORS['text_secondary'],
                wraplength=820,
                justify="left"
            )
            details_label.pack(fill="x", padx=15, pady=(0, 10), anchor="w")

        # Significance (if provided)
        significance = discovery.get('significance')
        if significance:
            sig_frame = ctk.CTkFrame(card, fg_color=COLORS['bg_dark'], corner_radius=8)
            sig_frame.pack(fill="x", padx=15, pady=(0, 10))

            sig_label = ctk.CTkLabel(
                sig_frame,
                text=f"💡 Analysis: {significance}",
                font=ctk.CTkFont(family="Segoe UI", size=12, slant="italic"),
                text_color=COLORS['accent_cyan'],
                wraplength=800,
                justify="left"
            )
            sig_label.pack(padx=10, pady=8, anchor="w")

        # Footer with discoverer
        discovered_by = discovery.get('discovered_by', 'Unknown Explorer')
        footer_label = ctk.CTkLabel(
            card,
            text=f"👤 Discovered by: {discovered_by}",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS['text_secondary']
        )
        footer_label.pack(padx=15, pady=(0, 15), anchor="e")

    def _get_type_icon(self, discovery_type: str) -> str:
        """Get emoji icon for discovery type"""
        icons = {
            'ruins': '🏛️',
            'ruins_structures': '🏛️',
            'fossils': '🦴',
            'bones': '🦴',
            'logs': '📜',
            'text_logs': '📜',
            'technology': '⚙️',
            'flora': '🌿',
            'fauna': '🦗',
            'flora_fauna': '🦗',
            'minerals': '💎',
            'ships': '🚀',
            'hazards': '⚡',
            'lore': '📖',
            'nms_update': '🆕'
        }
        type_lower = discovery_type.lower().replace(' ', '_')
        return icons.get(type_lower, '🔍')

    def _filter_discoveries(self, selected_filter: str):
        """Filter discoveries by type"""
        if selected_filter == "All":
            filtered = self.discoveries
        else:
            # Map filter names to discovery types
            type_map = {
                "Ruins": "ruins",
                "Fossils": "bones",
                "Logs": "logs",
                "Technology": "technology",
                "Flora/Fauna": "flora",
                "Minerals": "minerals",
                "Ships": "ships",
                "Hazards": "hazards",
                "Lore": "lore"
            }
            filter_type = type_map.get(selected_filter, "").lower()
            filtered = [d for d in self.discoveries if filter_type in d.get('discovery_type', '').lower()]

        # Clear and redisplay
        for widget in self.discoveries_frame.winfo_children():
            widget.destroy()

        if not filtered:
            no_results_label = ctk.CTkLabel(
                self.discoveries_frame,
                text=f"No discoveries found for filter: {selected_filter}",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color=COLORS['text_secondary']
            )
            no_results_label.pack(pady=50)
        else:
            self._display_discoveries(filtered)
