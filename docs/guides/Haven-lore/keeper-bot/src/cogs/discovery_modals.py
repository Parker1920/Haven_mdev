"""
Type-Specific Discovery Modals
Each discovery type has custom fields relevant to what's being reported
"""

import discord

# Base modal class with shared functionality
class BaseDiscoveryModal(discord.ui.Modal):
    """Base class for all type-specific discovery modals"""

    def __init__(self, discovery_type: str, system_name: str, location_info: str, config: dict, haven_data: dict, title: str):
        super().__init__(title=title)
        self.discovery_type = discovery_type
        self.system_name = system_name
        self.location_info = location_info
        self.config = config
        self.haven_data = haven_data

        # Parse location info
        self.location_type, self.location_name = self._parse_location_info(location_info)

    def _parse_location_info(self, location_info: str) -> tuple:
        """Parse location info string into type and name."""
        parts = location_info.split(':', 2)
        if len(parts) >= 2:
            return parts[0], parts[1] if len(parts) == 2 else parts[2]
        return "unknown", location_info

    def get_common_data(self):
        """Get data common to all discovery types"""
        return {
            'type': self.discovery_type,
            'system_name': self.system_name,
            'location_type': self.location_type,
            'location_name': self.location_name,
            'location_info': self.location_info,
            'haven_data': self.haven_data
        }

    async def on_submit(self, interaction: discord.Interaction):
        """Handle form submission - must be implemented by child classes"""
        raise NotImplementedError("Child classes must implement on_submit")


# 🦴 Ancient Bones & Fossils Modal
class AncientBonesModal(BaseDiscoveryModal):
    """Modal for reporting ancient bones and fossil discoveries"""

    def __init__(self, discovery_type: str, system_name: str, location_info: str, config: dict, haven_data: dict):
        super().__init__(discovery_type, system_name, location_info, config, haven_data,
                         title="🦴 Ancient Bones & Fossils Discovery")

    description = discord.ui.TextInput(
        label="📝 Discovery Description",
        placeholder="Describe the bones/fossils you found. What did they look like?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )

    species_type = discord.ui.TextInput(
        label="🦖 Species/Creature Type",
        placeholder="e.g., Large Predator, Flying Creature, Aquatic Life, Unknown",
        max_length=200,
        required=False
    )

    size_scale = discord.ui.TextInput(
        label="📏 Size/Scale",
        placeholder="e.g., Small (cat-sized), Medium (human-sized), Large (building-sized)",
        max_length=200,
        required=False
    )

    preservation_quality = discord.ui.TextInput(
        label="⚗️ Preservation Quality",
        placeholder="e.g., Excellent, Good, Fragmented, Petrified, Fossilized",
        max_length=200,
        required=False
    )

    estimated_age = discord.ui.TextInput(
        label="⏰ Estimated Age/Era",
        placeholder="e.g., Ancient, Pre-Gek, Millions of years old, Unknown",
        max_length=200,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        bot = interaction.client
        cog = bot.get_cog('EnhancedDiscoverySystem')
        if cog:
            discovery_data = self.get_common_data()
            discovery_data.update({
                'description': self.description.value,
                'species_type': self.species_type.value,
                'size_scale': self.size_scale.value,
                'preservation_quality': self.preservation_quality.value,
                'estimated_age': self.estimated_age.value
            })
            await cog.process_discovery_submission(interaction, discovery_data)


# 📜 Text Logs & Documents Modal
class TextLogsModal(BaseDiscoveryModal):
    """Modal for reporting text logs and document discoveries"""

    def __init__(self, discovery_type: str, system_name: str, location_info: str, config: dict, haven_data: dict):
        super().__init__(discovery_type, system_name, location_info, config, haven_data,
                         title="📜 Text Logs & Documents Discovery")

    description = discord.ui.TextInput(
        label="📝 Discovery Description",
        placeholder="Describe the log/document. Where was it found?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )

    key_excerpt = discord.ui.TextInput(
        label="📖 Key Excerpt/Quote",
        placeholder="Copy any interesting text from the log (if readable)",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=False
    )

    language_status = discord.ui.TextInput(
        label="🗣️ Language/Decryption Status",
        placeholder="e.g., Gek Language, Encrypted, Partially Decoded, English, Korvax",
        max_length=200,
        required=False
    )

    completeness = discord.ui.TextInput(
        label="📄 Completeness",
        placeholder="e.g., Complete Log, Fragmented (30%), Corrupted, Missing Pages",
        max_length=200,
        required=False
    )

    author_origin = discord.ui.TextInput(
        label="✍️ Author/Origin (if known)",
        placeholder="e.g., Unknown Traveler, Gek Merchant, Atlas Entity, Artemis",
        max_length=200,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        bot = interaction.client
        cog = bot.get_cog('EnhancedDiscoverySystem')
        if cog:
            discovery_data = self.get_common_data()
            discovery_data.update({
                'description': self.description.value,
                'key_excerpt': self.key_excerpt.value,
                'language_status': self.language_status.value,
                'completeness': self.completeness.value,
                'author_origin': self.author_origin.value
            })
            await cog.process_discovery_submission(interaction, discovery_data)


# 🏛️ Ruins & Structures Modal
class RuinsModal(BaseDiscoveryModal):
    """Modal for reporting ruins and structure discoveries"""

    def __init__(self, discovery_type: str, system_name: str, location_info: str, config: dict, haven_data: dict):
        super().__init__(discovery_type, system_name, location_info, config, haven_data,
                         title="🏛️ Ruins & Structures Discovery")

    description = discord.ui.TextInput(
        label="📝 Discovery Description",
        placeholder="Describe the ruins/structure. What makes it notable?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )

    structure_type = discord.ui.TextInput(
        label="🏗️ Structure Type",
        placeholder="e.g., Temple, Monument, Crashed Freighter, Settlement, Observatory",
        max_length=200,
        required=False
    )

    architectural_style = discord.ui.TextInput(
        label="🎨 Architectural Style",
        placeholder="e.g., Gek, Korvax, Vy'keen, Ancient, Unknown Civilization",
        max_length=200,
        required=False
    )

    structural_integrity = discord.ui.TextInput(
        label="🏚️ Structural Integrity",
        placeholder="e.g., Well-Preserved, Partially Collapsed, Heavily Damaged, Ruins",
        max_length=200,
        required=False
    )

    purpose_function = discord.ui.TextInput(
        label="🎯 Purpose/Function (if known)",
        placeholder="e.g., Religious Site, Trading Post, Research Facility, Unknown",
        max_length=200,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        bot = interaction.client
        cog = bot.get_cog('EnhancedDiscoverySystem')
        if cog:
            discovery_data = self.get_common_data()
            discovery_data.update({
                'description': self.description.value,
                'structure_type': self.structure_type.value,
                'architectural_style': self.architectural_style.value,
                'structural_integrity': self.structural_integrity.value,
                'purpose_function': self.purpose_function.value
            })
            await cog.process_discovery_submission(interaction, discovery_data)


# ⚙️ Alien Technology & Artifacts Modal
class AlienTechModal(BaseDiscoveryModal):
    """Modal for reporting alien technology and artifact discoveries"""

    def __init__(self, discovery_type: str, system_name: str, location_info: str, config: dict, haven_data: dict):
        super().__init__(discovery_type, system_name, location_info, config, haven_data,
                         title="⚙️ Alien Technology & Artifacts Discovery")

    description = discord.ui.TextInput(
        label="📝 Discovery Description",
        placeholder="Describe the technology/artifact. How does it work?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )

    tech_category = discord.ui.TextInput(
        label="🔧 Technology Category",
        placeholder="e.g., Weapon, Tool, Data Core, Power Source, Communication Device",
        max_length=200,
        required=False
    )

    operational_status = discord.ui.TextInput(
        label="⚡ Operational Status",
        placeholder="e.g., Fully Functional, Partially Working, Inert, Emitting Signal",
        max_length=200,
        required=False
    )

    power_source = discord.ui.TextInput(
        label="🔋 Power Source/Energy",
        placeholder="e.g., Unknown Energy, Solar, Biological, Nanite-Based, Depleted",
        max_length=200,
        required=False
    )

    reverse_engineering = discord.ui.TextInput(
        label="🔬 Reverse Engineering Potential",
        placeholder="e.g., Blueprint Obtainable, Too Advanced, Partially Understood",
        max_length=200,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        bot = interaction.client
        cog = bot.get_cog('EnhancedDiscoverySystem')
        if cog:
            discovery_data = self.get_common_data()
            discovery_data.update({
                'description': self.description.value,
                'tech_category': self.tech_category.value,
                'operational_status': self.operational_status.value,
                'power_source': self.power_source.value,
                'reverse_engineering': self.reverse_engineering.value
            })
            await cog.process_discovery_submission(interaction, discovery_data)


# 🦗 Flora & Fauna Modal
class FloraFaunaModal(BaseDiscoveryModal):
    """Modal for reporting flora and fauna discoveries"""

    def __init__(self, discovery_type: str, system_name: str, location_info: str, config: dict, haven_data: dict):
        super().__init__(discovery_type, system_name, location_info, config, haven_data,
                         title="🦗 Flora & Fauna Discovery")

    description = discord.ui.TextInput(
        label="📝 Discovery Description",
        placeholder="Describe the creature/plant. What makes it unique?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )

    species_name = discord.ui.TextInput(
        label="🏷️ Species Name (if scanned)",
        placeholder="e.g., Bipedal Carnivore, Glowing Flora, proc-gen name from scanner",
        max_length=200,
        required=False
    )

    behavioral_notes = discord.ui.TextInput(
        label="👁️ Behavioral Observations",
        placeholder="e.g., Aggressive, Passive, Herd Behavior, Bioluminescent at Night",
        max_length=200,
        required=False
    )

    habitat_biome = discord.ui.TextInput(
        label="🌍 Habitat/Biome",
        placeholder="e.g., Toxic Swamps, Frozen Tundra, Desert Plains, Underground Caves",
        max_length=200,
        required=False
    )

    threat_level = discord.ui.TextInput(
        label="⚠️ Threat Level",
        placeholder="e.g., Harmless, Defensive, Aggressive, Apex Predator, Non-Hostile",
        max_length=200,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        bot = interaction.client
        cog = bot.get_cog('EnhancedDiscoverySystem')
        if cog:
            discovery_data = self.get_common_data()
            discovery_data.update({
                'description': self.description.value,
                'species_name': self.species_name.value,
                'behavioral_notes': self.behavioral_notes.value,
                'habitat_biome': self.habitat_biome.value,
                'threat_level': self.threat_level.value
            })
            await cog.process_discovery_submission(interaction, discovery_data)


# 💎 Minerals & Resources Modal
class MineralsModal(BaseDiscoveryModal):
    """Modal for reporting mineral and resource discoveries"""

    def __init__(self, discovery_type: str, system_name: str, location_info: str, config: dict, haven_data: dict):
        super().__init__(discovery_type, system_name, location_info, config, haven_data,
                         title="💎 Minerals & Resources Discovery")

    description = discord.ui.TextInput(
        label="📝 Discovery Description",
        placeholder="Describe the mineral/resource deposit. Where is it located?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )

    resource_type = discord.ui.TextInput(
        label="⛏️ Resource Type",
        placeholder="e.g., Activated Indium, Gold, Cobalt, Rare Earth, Exotic Crystals",
        max_length=200,
        required=False
    )

    deposit_richness = discord.ui.TextInput(
        label="💰 Deposit Size/Richness",
        placeholder="e.g., Small Vein, Large Deposit, S-Class Hotspot, Abundant Field",
        max_length=200,
        required=False
    )

    extraction_method = discord.ui.TextInput(
        label="🔨 Extraction Method",
        placeholder="e.g., Mining Laser, Mineral Extractor, Terrain Manipulator Required",
        max_length=200,
        required=False
    )

    economic_value = discord.ui.TextInput(
        label="💵 Economic Value/Market Demand",
        placeholder="e.g., High Value (+80%), Common, Rare Trade Good, Star System Specific",
        max_length=200,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        bot = interaction.client
        cog = bot.get_cog('EnhancedDiscoverySystem')
        if cog:
            discovery_data = self.get_common_data()
            discovery_data.update({
                'description': self.description.value,
                'resource_type': self.resource_type.value,
                'deposit_richness': self.deposit_richness.value,
                'extraction_method': self.extraction_method.value,
                'economic_value': self.economic_value.value
            })
            await cog.process_discovery_submission(interaction, discovery_data)


# 🚀 Crashed Ships & Wrecks Modal
class CrashedShipsModal(BaseDiscoveryModal):
    """Modal for reporting crashed ship and wreck discoveries"""

    def __init__(self, discovery_type: str, system_name: str, location_info: str, config: dict, haven_data: dict):
        super().__init__(discovery_type, system_name, location_info, config, haven_data,
                         title="🚀 Crashed Ships & Wrecks Discovery")

    description = discord.ui.TextInput(
        label="📝 Discovery Description",
        placeholder="Describe the crashed ship/wreck. How did you find it?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )

    ship_class = discord.ui.TextInput(
        label="🛸 Ship Class/Type",
        placeholder="e.g., Hauler, Fighter, Explorer, Exotic, Freighter Debris, Unknown",
        max_length=200,
        required=False
    )

    hull_condition = discord.ui.TextInput(
        label="🔧 Hull Condition/Damage",
        placeholder="e.g., Heavily Damaged, Salvageable, Burnt Out, Mostly Intact",
        max_length=200,
        required=False
    )

    salvageable_tech = discord.ui.TextInput(
        label="⚙️ Salvageable Tech/Cargo",
        placeholder="e.g., Upgrade Modules, Cargo Pods, Technology Blueprints, Empty",
        max_length=200,
        required=False
    )

    pilot_status = discord.ui.TextInput(
        label="👤 Pilot Status/Evidence",
        placeholder="e.g., No Remains Found, Abandoned, Distress Signal Active, Unknown",
        max_length=200,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        bot = interaction.client
        cog = bot.get_cog('EnhancedDiscoverySystem')
        if cog:
            discovery_data = self.get_common_data()
            discovery_data.update({
                'description': self.description.value,
                'ship_class': self.ship_class.value,
                'hull_condition': self.hull_condition.value,
                'salvageable_tech': self.salvageable_tech.value,
                'pilot_status': self.pilot_status.value
            })
            await cog.process_discovery_submission(interaction, discovery_data)


# ⚡ Environmental Hazards Modal
class HazardsModal(BaseDiscoveryModal):
    """Modal for reporting environmental hazard discoveries"""

    def __init__(self, discovery_type: str, system_name: str, location_info: str, config: dict, haven_data: dict):
        super().__init__(discovery_type, system_name, location_info, config, haven_data,
                         title="⚡ Environmental Hazards Discovery")

    description = discord.ui.TextInput(
        label="📝 Discovery Description",
        placeholder="Describe the hazard. What makes it dangerous or unusual?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )

    hazard_type = discord.ui.TextInput(
        label="☢️ Hazard Type",
        placeholder="e.g., Extreme Heat, Freezing Cold, Toxic Atmosphere, Radiation Storm",
        max_length=200,
        required=False
    )

    severity_level = discord.ui.TextInput(
        label="⚠️ Severity Level",
        placeholder="e.g., Moderate, High, Extreme, Deadly, Survivable with Protection",
        max_length=200,
        required=False
    )

    duration_frequency = discord.ui.TextInput(
        label="⏱️ Duration/Frequency",
        placeholder="e.g., Constant, Every 5 Minutes, Random Storms, Day/Night Cycle",
        max_length=200,
        required=False
    )

    protection_required = discord.ui.TextInput(
        label="🛡️ Protection Required",
        placeholder="e.g., Hazard Protection +3, Suit Upgrades, None (Death Zone), Oxygen",
        max_length=200,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        bot = interaction.client
        cog = bot.get_cog('EnhancedDiscoverySystem')
        if cog:
            discovery_data = self.get_common_data()
            discovery_data.update({
                'description': self.description.value,
                'hazard_type': self.hazard_type.value,
                'severity_level': self.severity_level.value,
                'duration_frequency': self.duration_frequency.value,
                'protection_required': self.protection_required.value
            })
            await cog.process_discovery_submission(interaction, discovery_data)


# 🆕 NMS Update Content Modal
class UpdateContentModal(BaseDiscoveryModal):
    """Modal for reporting new NMS update content discoveries"""

    def __init__(self, discovery_type: str, system_name: str, location_info: str, config: dict, haven_data: dict):
        super().__init__(discovery_type, system_name, location_info, config, haven_data,
                         title="🆕 NMS Update Content Discovery")

    description = discord.ui.TextInput(
        label="📝 Discovery Description",
        placeholder="Describe the new content. What update added it?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )

    update_name = discord.ui.TextInput(
        label="📦 Update/Patch Name",
        placeholder="e.g., Worlds Part I, Echoes, Orbital, Interceptor, Unknown",
        max_length=200,
        required=False
    )

    feature_category = discord.ui.TextInput(
        label="🎯 Feature Category",
        placeholder="e.g., New Building Type, Ship Class, Biome, Mechanic, Quest Line",
        max_length=200,
        required=False
    )

    gameplay_impact = discord.ui.TextInput(
        label="🎮 Gameplay Impact",
        placeholder="e.g., Major Feature, Quality of Life, Visual Enhancement, Game-Changing",
        max_length=200,
        required=False
    )

    first_impressions = discord.ui.TextInput(
        label="💭 First Impressions/Thoughts",
        placeholder="Your initial reaction and thoughts on this new content",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        bot = interaction.client
        cog = bot.get_cog('EnhancedDiscoverySystem')
        if cog:
            discovery_data = self.get_common_data()
            discovery_data.update({
                'description': self.description.value,
                'update_name': self.update_name.value,
                'feature_category': self.feature_category.value,
                'gameplay_impact': self.gameplay_impact.value,
                'first_impressions': self.first_impressions.value
            })
            await cog.process_discovery_submission(interaction, discovery_data)


# 📖 Player-Created Lore Modal
class PlayerLoreModal(BaseDiscoveryModal):
    """Modal for reporting player-created lore discoveries"""

    def __init__(self, discovery_type: str, system_name: str, location_info: str, config: dict, haven_data: dict):
        super().__init__(discovery_type, system_name, location_info, config, haven_data,
                         title="📖 Player-Created Lore Discovery")

    description = discord.ui.TextInput(
        label="📝 Lore Entry/Story",
        placeholder="Share your creative lore, theory, or story about this location",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )

    story_type = discord.ui.TextInput(
        label="📚 Story Type",
        placeholder="e.g., Journal Entry, Theory, Fiction, Historical Account, Roleplay",
        max_length=200,
        required=False
    )

    lore_connections = discord.ui.TextInput(
        label="🔗 Lore Connections",
        placeholder="How does this connect to existing game lore or other discoveries?",
        max_length=200,
        required=False
    )

    creative_elements = discord.ui.TextInput(
        label="✨ Creative Elements Used",
        placeholder="e.g., Base Building, Photos, Community Event, Coordinates Trail",
        max_length=200,
        required=False
    )

    collaborative_work = discord.ui.TextInput(
        label="🤝 Collaborative Work?",
        placeholder="e.g., Solo Project, Community Collaboration, Open for Others, Ongoing",
        max_length=200,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        bot = interaction.client
        cog = bot.get_cog('EnhancedDiscoverySystem')
        if cog:
            discovery_data = self.get_common_data()
            discovery_data.update({
                'description': self.description.value,
                'story_type': self.story_type.value,
                'lore_connections': self.lore_connections.value,
                'creative_elements': self.creative_elements.value,
                'collaborative_work': self.collaborative_work.value
            })
            await cog.process_discovery_submission(interaction, discovery_data)


# Modal factory function to get the right modal based on discovery type
def get_modal_for_type(discovery_type: str, system_name: str, location_info: str, config: dict, haven_data: dict):
    """
    Factory function to return the appropriate modal class based on discovery type emoji

    Args:
        discovery_type: Emoji representing the discovery type
        system_name: Name of the star system
        location_info: Location information string
        config: Bot configuration dictionary
        haven_data: Haven star system data

    Returns:
        Instance of appropriate modal class
    """
    modal_map = {
        '🦴': AncientBonesModal,
        '📜': TextLogsModal,
        '🏛️': RuinsModal,
        '⚙️': AlienTechModal,
        '🦗': FloraFaunaModal,
        '💎': MineralsModal,
        '🚀': CrashedShipsModal,
        '⚡': HazardsModal,
        '🆕': UpdateContentModal,
        '📖': PlayerLoreModal
    }

    modal_class = modal_map.get(discovery_type)
    if modal_class:
        return modal_class(discovery_type, system_name, location_info, config, haven_data)

    # Fallback to generic modal if type not recognized (shouldn't happen)
    raise ValueError(f"Unknown discovery type: {discovery_type}")
