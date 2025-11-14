# Haven Master - Control Room

**Version:** Beta v1.0
**Last Updated:** November 2025

## What is Haven Master?

Haven Master is the central hub for managing your No Man's Sky community data in the Haven civilization. This tool helps you:

- **Manage Star Systems**: Add and edit star system information including planets, moons, and discoveries
- **Track Discoveries**: Log all types of discoveries from ancient ruins to alien technology
- **Visualize Data**: View your systems and planets in an interactive 3D map
- **Sync with Discord**: Integrate with The Keeper Discord bot for community-wide discovery tracking

## System Requirements

- **Operating System**: Windows 10 or later (64-bit)
- **Screen Resolution**: 1366x768 or higher recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 100MB free space

## Getting Started

### First-Time Setup

1. **Extract the Files**: Unzip this folder to a permanent location on your computer (e.g., `C:\Haven` or `Documents\Haven`)

2. **Run the Program**: Double-click `HavenControlRoom.exe` to launch the application

3. **Initial Data Setup**: On first launch, the program will:
   - Create a `data` folder for your databases
   - Initialize the VH-Database.db file
   - Set up the Haven Master data structure

### Main Features

#### Control Room (Main Menu)

The Control Room is your main dashboard with access to all features:

- **System Entry Wizard**: Step-by-step wizard to add new star systems with planets and moons
- **3D System Map**: Interactive 3D visualization of your star systems
- **Discovery Manager**: View and filter all logged discoveries
- **Database Tools**: Import/export data, backup your database

#### System Entry Wizard

Use this to add new star systems to Haven:

1. **System Information**: Enter star system name, coordinates, economy, etc.
2. **Planet Details**: Add planets with their biomes, sentinels, weather, and resources
3. **Moon Details**: Add moons orbiting each planet
4. **Review & Save**: Review all information before saving to the database

**Important**: Make sure you can see the Save/Next/Back buttons at the bottom of the wizard. If your screen is too small, you can:
- Resize the window by dragging the edges
- Use the scroll wheel to scroll within sections
- Minimize other windows to maximize screen space

#### 3D System Map

Explore your systems in an interactive 3D environment:

- **Rotate**: Click and drag to rotate the view
- **Zoom**: Use mouse wheel to zoom in/out
- **Select**: Click on planets/moons to view details
- **Filter**: Use the dropdown to filter by system
- **Discoveries**: Click "View X Discoveries" to see discoveries for that body

#### Discovery Tracking

All discoveries submitted through The Keeper Discord bot automatically sync to the Haven Master database. You can:

- View all discoveries by type, system, or planet
- Filter by discovery categories (ruins, fossils, tech, flora/fauna, etc.)
- See detailed information including coordinates and significance
- Track who discovered what and when

## Discord Bot Integration

Haven Master works seamlessly with **The Keeper** Discord bot:

1. Submit discoveries through Discord using `/discover`
2. Choose your discovery type (Ancient Bones, Text Logs, Ruins, etc.)
3. Fill out the type-specific modal with details
4. The discovery automatically appears in Haven Master's 3D map and Discovery Manager

### Discovery Types Supported

- 🦴 **Ancient Bones & Fossils**: Prehistoric remains and fossils
- 📜 **Text Logs & Documents**: Written records and communications
- 🏛️ **Ruins & Structures**: Ancient buildings and monuments
- ⚙️ **Alien Technology**: Advanced devices and machinery
- 🦗 **Flora & Fauna**: Native species and ecosystems
- 💎 **Minerals & Resources**: Valuable deposits and materials
- 🚀 **Crashed Ships**: Downed vessels and salvage opportunities
- ⚡ **Hazards & Phenomena**: Dangerous conditions and anomalies
- 🆕 **NMS Updates**: New game content and features
- 📖 **Player Lore**: Community stories and collaborative narratives

## Tips & Best Practices

### Data Entry Tips

- **Be Accurate**: Double-check coordinates and names before saving
- **Use Standard Names**: Follow Haven naming conventions (e.g., "Tenex[VH]")
- **Complete Information**: Fill in as many fields as possible for better tracking
- **Save Often**: Use the Save button frequently when entering large amounts of data

### Performance Tips

- **Close Background Apps**: For best performance with the 3D map
- **Regular Backups**: Export your database regularly (Database Tools > Export)
- **Screen Size**: Use a monitor with at least 1366x768 resolution for best experience

### Troubleshooting

**Issue**: Can't see Save/Next/Back buttons
- **Solution**: Resize the window larger or scroll down within the wizard sections

**Issue**: 3D map is slow or laggy
- **Solution**: Close other programs, reduce the number of visible planets, or filter by system

**Issue**: Database not found
- **Solution**: Make sure the `data` folder exists in the same directory as the exe

**Issue**: Discoveries not appearing
- **Solution**: Check that the discovery has valid planet_id or moon_id in the database

## Data Locations

- **Main Database**: `data/VH-Database.db` (all systems, planets, moons, discoveries)
- **Bot Database**: `docs/guides/Haven-lore/keeper-bot/keeper.db` (bot state and cache)
- **Backups**: Created in the same directory when you export data

## Support & Community

For questions, bug reports, or feature requests:
- Contact the Haven civilization administrators
- Report issues on the Haven Discord server
- Contribute to the project on GitHub (if applicable)

## What's New in This Version

### v1.0 Beta (November 2025)

- ✅ **Window Sizing Fixed**: Buttons now visible on all screen sizes (1366x768+)
- ✅ **DPI Awareness**: Crisp rendering on high-DPI displays (4K monitors, Surface devices)
- ✅ **Type-Specific Discovery Modals**: 10 custom modals with relevant fields for each discovery type
- ✅ **Improved Discovery Linking**: Discoveries now properly link to planets/moons and appear on map
- ✅ **Act Progression Reset**: Clean slate for beta testing with Act 1 story state
- ✅ **Database Schema Extended**: 40+ new columns for type-specific discovery data

## Credits

**Developed For**: Haven Civilization (No Man's Sky)
**Integration**: The Keeper Discord Bot
**Database**: VH-Database (Master Community Database)

---

**Thank you for being part of Haven!** Your discoveries help build our shared universe. Safe travels, Traveller. 🚀
