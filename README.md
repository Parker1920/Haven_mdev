# Haven Control Room — Complete Star Mapping System

Welcome to **Haven Control Room**, a comprehensive star mapping and data collection toolkit for No Man's Sky explorers. This system provides everything you need to catalog, visualize, and share your discoveries in an interactive 3D galaxy map.

## Table of Contents

### [Chapter 1: Overview & Quick Start](docs/overview_quickstart.md)
- What Haven Control Room does
- Key features and capabilities
- 5-minute setup guide
- Basic workflow overview

### [Chapter 2: Installation & Setup](docs/installation_setup.md)
- System requirements
- Python installation guide
- Virtual environment setup
- Dependency installation
- First-time configuration

### [Chapter 3: Control Room Interface](docs/control_room_guide.md)
- Launching the Control Room
- Interface overview and layout
- Quick actions and file management
- Advanced tools and settings
- Log monitoring and troubleshooting

### [Chapter 4: System Entry Wizard](docs/system_entry_wizard_guide.md)
- Complete guide to adding star systems
- Two-page workflow (System Info → Planets & Moons)
- Planet and moon data entry
- Photo management and file handling
- Edit mode and data validation

### [Chapter 5: 3D Galaxy Map Generation](docs/galaxy_map_guide.md)
- Map generation process
- Interactive 3D visualization features
- Browser-based viewing and controls
- System and planet display options
- Performance optimization

### [Chapter 6: Exporting Applications](docs/exporting_applications.md)
- Creating standalone executables (Windows/macOS)
- iOS Progressive Web App generation
- Distribution and sharing options
- Platform-specific considerations
- Offline functionality

### [Chapter 7: Data Structure & Schema](docs/data_structure_guide.md)
- JSON data format overview
- Schema validation and requirements
- Migration between data formats
- Backup and recovery procedures
- Custom field management

### [Chapter 8: Troubleshooting & Support](docs/troubleshooting_guide.md)
- Common issues and solutions
- Log file analysis
- Performance optimization
- Data recovery procedures
- Getting help and support

## Quick Start (5 Minutes)

1. **Install Python 3.10+** from [python.org](https://www.python.org/downloads/)
2. **Open terminal in Haven_Mdev folder**
3. **Set up environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # or .venv\Scripts\activate on Windows
   pip install -r config/requirements.txt
   ```
4. **Launch Control Room:**
   - Windows: Double-click `Haven Control Room.bat`
   - macOS: Double-click `haven_control_room_mac.command`
   - Linux: `python src/control_room.py`

5. **Add your first system:**
   - Click "🛰️ Launch System Entry (Wizard)"
   - Fill in system details and planets
   - Click "💾 Finish & Save"

6. **Generate your map:**
   - Click "🗺️ Generate Map"
   - Click "🌐 Open Latest Map" to view in browser

## Key Features

- **📊 Complete Data Entry**: Two-page wizard for systems, planets, and moons with full metadata
- **🌌 Interactive 3D Maps**: Touch-optimized Three.js visualizations with galaxy and system views
- **📱 Cross-Platform**: Desktop GUI + iOS PWA that installs to home screen
- **🔧 Standalone Exports**: Create executable files for users without Python
- **💾 Local Storage**: All data stored locally with automatic backups
- **🎨 Modern UI**: Glassmorphic design with customizable themes
- **📋 Schema Validation**: Ensures data integrity and consistency
- **🔄 Migration Support**: Handles legacy data formats automatically

## System Requirements

- **Python 3.10+** (with pip)
- **Web browser** with WebGL support (Chrome, Firefox, Safari, Edge)
- **4GB RAM** recommended for large datasets
- **2GB free disk space** for dependencies and generated files

## File Structure

```
Haven_Mdev/
├── src/                    # Python source code
├── data/                   # Your star system data (data.json)
├── dist/                   # Generated maps and exports
├── docs/                   # Detailed documentation (chapters)
├── logs/                   # Application logs
├── photos/                 # System screenshots
├── config/                 # Dependencies and build config
├── scripts/                # Helper scripts and launchers
├── themes/                 # UI theme files
└── Archive-Dump/           # Legacy files and version history
```

## Data Storage

All your star system data is stored locally in `data/data.json`. The system automatically:
- Creates backups before saving changes
- Validates data against schema requirements
- Migrates legacy formats when detected
- Supports unlimited custom fields and metadata

## Community & Support

- **Documentation**: Comprehensive guides in the `docs/` folder
- **Logs**: Check `logs/` folder for troubleshooting information
- **Backups**: Legacy files archived in `Archive-Dump/` for reference
- **Issues**: Review logs and documentation first, then check data integrity

## Version History

This system has evolved through multiple phases:
- **Phase 1**: Basic system entry with manual JSON editing
- **Phase 2**: Two-page wizard with planet/moon support
- **Current**: Full Control Room with exports, iOS support, and modern UI

Legacy components are preserved in `Archive-Dump/` for reference and migration purposes.

---

*Built for the Haven Galaxy community — explore, document, and share your discoveries!*
