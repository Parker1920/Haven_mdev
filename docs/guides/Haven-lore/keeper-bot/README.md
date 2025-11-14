# 🌌 The Keeper Discord Bot - Setup Guide

*A Discord bot companion for the Haven_mdev star mapping system*

## 🎯 What is The Keeper?

The Keeper is a Discord bot that embodies the mysterious archivist intelligence from your Haven lore. It serves as a **lore assistant** that works hand-in-hand with your Haven_mdev star mapping program:

- **Haven_mdev**: Primary star system mapping and planet cataloging  
- **The Keeper Bot**: Discord-based discovery assistant that enhances Haven with lore
- **Workflow**: Map first → Detailed exploration with Keeper → Export back to enhance map

## ✨ Features

### Phase 1: Discovery Submission System ✅
- **Haven-Integrated Discovery Reports**: Select star systems from your Haven data
- **Planet/Location Selection**: Choose specific planets, moons, or space anomalies
- **Multiple Input Methods**: Detailed forms, quick commands, and guided flows
- **Photo Upload**: Archive evidence with your discoveries
- **Keeper Voice**: Authentic responses in The Keeper's mysterious character

### Phase 2: Pattern Recognition ✅  
- **Semi-Automated Pattern Detection**: Analyzes cross-system patterns in same region
- **Regional Analysis**: Uses Haven's galactic region system
- **Mystery Tiers**: Escalating significance levels (1-4)
- **Investigation Triggers**: Automatic alerts when patterns emerge
- **Haven Export**: Discoveries can be exported back to enhance your star map

### Phase 3: Advanced Archive Tools 🚧
- Search functionality, admin dashboard, pattern management

### Phase 4: Community Engagement 🚧
- Mystery tier system, community challenges, leaderboards

## 🛠️ Installation

### Prerequisites

- **Python 3.10+** (download from [python.org](https://www.python.org/downloads/))
- **Discord Bot Token** (create at [Discord Developer Portal](https://discord.com/developers/applications))
- **Haven_mdev System** (for full integration features)

### Step 1: Environment Setup

```bash
# Navigate to the keeper-bot folder
cd /path/to/keeper-bot

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Bot Configuration

1. **Create Discord Bot:**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application" → Give it a name (e.g., "The Keeper")
   - Go to "Bot" section → Click "Add Bot"
   - Copy the bot token

2. **Configure Environment:**
   ```bash
   # Copy the environment template
   cp .env.example .env
   
   # Edit .env and add your bot token:
   BOT_TOKEN=your_discord_bot_token_here
   GUILD_ID=your_discord_server_id_here
   ```

3. **Invite Bot to Server:**
   - In Developer Portal, go to OAuth2 → URL Generator
   - Select scopes: `bot`, `applications.commands`
   - Select permissions: `Send Messages`, `Use Slash Commands`, `Read Message History`, `Attach Files`
   - Copy the generated URL and open it to invite the bot

### Step 3: Discord Server Setup

The Keeper needs 4 channels:

```
#discovery-reports - Where users submit discoveries
#keeper-archive - Where The Keeper posts analysis  
#investigation-threads - Active mysteries
#lore-discussion - Community theories
```

### Step 4: Haven Integration (Optional)

If you have the Haven_mdev star mapping system:

1. **Update Haven Path:**
   Edit `src/core/haven_integration.py` line 24 to point to your Haven data:
   ```python
   "/path/to/your/Haven_mdev/data/data.json"
   ```

2. **Verify Integration:**
   ```bash
   python verify_setup.py
   ```

## 🚀 Running The Keeper

### Start the Bot

```bash
# Make sure you're in the keeper-bot directory with venv activated
python src/main.py
```

### Verification

```bash
# Run the verification script to test all systems
python verify_setup.py
```

The verification will test:
- ✅ Environment Setup
- ✅ Dependencies  
- ✅ Keeper Personality
- ✅ Database System
- ✅ Haven Integration

## 🎮 Usage

### Basic Discovery Flow

1. **User runs:** `/discovery-report`
2. **Bot shows:** Haven star system selection (if integrated)
3. **User selects:** Specific system from their Haven charts
4. **Bot shows:** Planet/moon/space location options for that system
5. **User selects:** Exact location of discovery
6. **Bot shows:** Discovery type selection (bones, logs, ruins, etc.)
7. **User fills:** Detailed discovery form
8. **Keeper analyzes:** Creates lore response and archives discovery
9. **Pattern detection:** Automatically checks for patterns with other discoveries
10. **Investigation trigger:** Opens mystery threads when patterns emerge

### Commands

- `/discovery-report` - Submit a discovery with Haven integration
- `/quick-discovery` - Streamlined discovery submission  
- `/search-discoveries` - Search the archive
- `/pattern-analysis` - Manually trigger pattern analysis
- `/view-patterns` - View detected patterns by tier
- `/haven-export` - Export discoveries for Haven integration

### Haven Integration Workflow

```
Haven Star Map → Discovery Report → Keeper Analysis → Pattern Detection → Export to Haven
      ↑                                                                            ↓
      ←←←←←←←←←←← Enhanced map with lore ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
```

## 🔧 Configuration

### Bot Settings (src/config.json)

```json
{
  "theme": {
    "colors": {
      "accent_cyan": "#00d9ff",
      "accent_purple": "#9d4edd", 
      "accent_pink": "#ff006e"
    }
  },
  "discovery_types": {
    "🦴": "Ancient Bones & Fossils",
    "📜": "Text Logs & Documents",
    "🏛️": "Ruins & Structures",
    "⚙️": "Alien Technology & Artifacts"
  },
  "mystery_tiers": {
    "1": {"name": "Surface Anomaly", "threshold": 3},
    "2": {"name": "Pattern Emergence", "threshold": 7},
    "3": {"name": "Deep Mystery", "threshold": 15}, 
    "4": {"name": "Cosmic Significance", "threshold": 30}
  }
}
```

### Environment Variables (.env)

```bash
# Required
BOT_TOKEN=your_discord_bot_token
GUILD_ID=your_discord_server_id

# Optional  
DEBUG_MODE=True
MIN_DISCOVERIES_FOR_PATTERN=3
AUTO_PATTERN_THRESHOLD=0.75
```

## 📁 File Structure

```
keeper-bot/
├── src/
│   ├── main.py                    # Bot entry point
│   ├── config.json               # Configuration
│   ├── core/
│   │   ├── keeper_personality.py # The Keeper's voice & responses
│   │   └── haven_integration.py  # Haven star map integration
│   ├── database/
│   │   └── keeper_db.py          # SQLite database management
│   └── cogs/
│       ├── enhanced_discovery.py # Haven-integrated discovery system
│       ├── pattern_recognition.py# Semi-automated pattern detection
│       ├── archive_system.py     # Archive tools (Phase 3)
│       └── admin_tools.py        # Admin tools (Phase 3)
├── data/                         # Database and backups
├── logs/                         # Bot logs
├── requirements.txt              # Python dependencies  
├── .env                          # Environment configuration
└── verify_setup.py              # Setup verification script
```

## 🔍 Troubleshooting

### Common Issues

**Bot doesn't respond to commands:**
- Check bot permissions in Discord server
- Verify bot token in .env file
- Check console for error messages

**Haven integration not working:**
- Verify Haven data path in haven_integration.py
- Check that Haven_mdev/data/data.json exists
- Run verification script to test integration

**Database errors:**
- Check that data/ folder exists and is writable
- Delete data/keeper.db to reset (will lose discovery history)

**Pattern detection not triggering:**
- Verify minimum discovery threshold in config
- Check that discoveries have similar types/locations
- Use `/pattern-analysis` to manually test

### Logs

Check `logs/keeper.log` for detailed error information:

```bash
tail -f logs/keeper.log
```

## 🚀 Deployment

### Development Mode
```bash
python src/main.py
```

### Production Mode

1. **Set up as service** (Linux/macOS):
   ```bash
   # Create systemd service file
   sudo nano /etc/systemd/system/keeper-bot.service
   ```

2. **Or use screen/tmux**:
   ```bash
   screen -S keeper-bot
   python src/main.py
   # Ctrl+A+D to detach
   ```

3. **Monitor with logs**:
   ```bash
   tail -f logs/keeper.log
   ```

## 🤝 Integration with Haven_mdev

The Keeper is designed to complement your Haven star mapping system:

### Data Flow
1. **Users map systems** in Haven_mdev first
2. **Detailed exploration** reported through The Keeper bot  
3. **Discoveries archived** with lore context
4. **Patterns detected** across multiple systems/regions
5. **Enhanced data exported** back to Haven for richer maps

### Benefits
- **Rich narrative context** for your star charts
- **Community-driven exploration** beyond basic mapping
- **Pattern recognition** that reveals deeper mysteries  
- **Backup archive** of all discoveries separate from main map
- **Discord integration** for real-time collaboration

## 📈 Future Phases

### Phase 3: Advanced Archive + Admin Tools
- Comprehensive search functionality
- Admin dashboard for pattern management  
- Advanced archive viewing and organization
- Bulk import/export tools

### Phase 4: Community Engagement Features  
- Mystery tier progression system
- Community challenges and events
- Explorer leaderboards and achievements
- Advanced Keeper interactions and storytelling

## 🆘 Support

1. **Run verification**: `python verify_setup.py`
2. **Check logs**: `logs/keeper.log`  
3. **Test components**: Individual command testing
4. **Haven integration**: Verify data path and format

---

*The Keeper awaits. Your story begins now.*