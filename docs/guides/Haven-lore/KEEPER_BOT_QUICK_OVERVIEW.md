# 🌌 THE KEEPER BOT - Quick Overview

*A Discord bot that adds lore depth to your Haven star map*

---

## What It Does

**The Keeper** is a roleplay Discord bot that lets you document in-game discoveries and automatically detects patterns across multiple submissions. It's designed to work alongside the Haven Control Room star mapping program.

---

## Core Features

### 📝 Discovery Submission (`/discovery-report`)
- **Select from Haven systems** - Bot reads your `keeper_test_data.json` file
- **4-step guided flow:**
  1. Choose star system (ORACLE OMEGA, VESTIGE ZETA, etc.)
  2. Choose location (specific planet/moon or deep space)
  3. Choose discovery type (🦴 Bones, 📜 Logs, 🏛️ Ruins, ⚙️ Tech, etc.)
  4. Fill detailed form (description, coordinates, condition, analysis)
- **Photo uploads** - Attach screenshot evidence
- **Keeper analyzes** - Bot responds in-character with lore-appropriate analysis

### 🌀 Pattern Detection (Automatic)
- **Watches for similarities** - When 3+ discoveries match (same type, same region, similar descriptions)
- **Creates patterns** - "Euclid Core Ancient Remains" with confidence score
- **Mystery tiers** - Patterns ranked 1-4 based on significance
- **Investigation threads** - Auto-creates discussion channels for major patterns

### 🔍 Search & Archive (`/advanced-search`)
- Filter by: discovery type, location, date range, explorer, pattern
- Paginated results with navigation
- View full discovery details

### 🎯 Progression System (`/mystery-tier`)
- **4 tiers:** Initiate Explorer → Pattern Seeker → Lore Investigator → Archive Curator
- Progress by submitting discoveries and contributing to patterns
- Unlock deeper Keeper interactions at higher tiers

### 🏆 Community Features
- **`/leaderboards`** - Rankings by discoveries, patterns, activity, tier
- **`/community-challenge`** - Time-limited events with rewards
- **`/keeper-story`** - Personalized narrative based on your discoveries
- **`/view-patterns`** - Browse all detected patterns by tier

### ⚙️ Admin Tools
- **`/setup-channels`** - Configure bot channels
- **`/server-stats`** - View discovery/pattern statistics
- **`/keeper-config`** - Adjust pattern detection sensitivity
- **`/pattern-manager`** - Curate detected patterns

### 📤 Export (`/haven-export`)
- Export your Discord discoveries back to Haven Control Room
- Enriches star map with lore data from bot
- JSON format compatible with Haven import

---

## How It Works With Haven Map

### Haven Control Room → Keeper Bot
1. **You create star systems** in Haven Control Room
2. **Export to JSON** (`data/keeper_test_data.json`)
3. **Set bot environment variable:** `HAVEN_DATA_PATH=C:\path\to\keeper_test_data.json`
4. **Bot loads systems** - Dropdowns populate with your Haven data
5. **Discovery submission uses real coordinates** - Bot knows system regions, planet names

### Keeper Bot → Haven Control Room
1. **Use `/haven-export`** in Discord
2. **Download JSON file** with all your discoveries
3. **Import into Haven Control Room** (future feature)
4. **Map shows lore annotations** - Systems with discoveries highlighted

### Integration Benefits
- **Consistent data** - Same system names, coordinates, regions
- **Two-way workflow** - Map first, explore with lore, enhance map with findings
- **Community exploration** - Multiple players document discoveries in same star systems
- **Pattern detection** - Bot connects discoveries across your mapped galaxy

---

## Pattern Detection Explained

**Automatic Analysis:**
```
User 1 submits: 🦴 Bones on ORACLE OMEGA-A (Euclid Core)
User 2 submits: 🦴 Bones on VESTIGE ZETA-B (Euclid Core)
User 3 submits: 🦴 Bones on KEEPER EPSILON-C (Euclid Core)

Bot calculates:
- Type Match: 100% (all bones)
- Region Match: 100% (all Euclid Core)
- Time Match: 100% (submitted same week)
→ Confidence: 87%

Pattern Created: "Euclid Core Ancient Remains"
Mystery Tier: 2 (Pattern Emergence)
Investigation Thread: Auto-created in #investigations
```

**Thresholds:**
- Minimum 3 similar discoveries
- 60%+ confidence score required
- Regional patterns get 1.5x confidence boost

---

## Roleplay Elements

- **The Keeper speaks in-character** - Mysterious AI archivist voice
- **References NMS lore** - Atlas, First Spawn, Korvax, Gek, convergence points
- **Personality modes** - Curious, analytical, cautious, philosophical
- **Consistent character** - Remembers patterns, builds theories, admits mistakes
- **Community storytelling** - Investigations become collaborative mysteries

---

## Example Workflow

**Day 1:**
```
1. Map 10 systems in Haven Control Room
2. Export to keeper_test_data.json
3. Start Keeper bot, it loads your systems
4. /discovery-report → ORACLE OMEGA → Planet A → 🦴 Bones → Submit details
5. Keeper responds: "Fascinating... quantum signatures detected..."
```

**Day 3:**
```
6. Friend submits similar bones in VESTIGE ZETA
7. Pattern emerges: "Euclid Core Ancient Remains"
8. Keeper posts alert: "Pattern detected! 2 discoveries, 73% confidence"
```

**Day 7:**
```
9. Community submits 5 more matching discoveries
10. Pattern upgrades to Tier 2
11. Investigation thread created
12. /haven-export downloads all discoveries
13. Import into Haven Control Room
14. Star map now annotated with lore
```

---

## Technical Setup (Quick)

```bash
# 1. Install
cd keeper-bot
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure
# Edit .env:
BOT_TOKEN=your_discord_bot_token
GUILD_ID=your_server_id
HAVEN_DATA_PATH=C:\path\to\Haven_mdev\data\keeper_test_data.json

# 3. Run
python src/main.py
```

---

## Commands Summary

| Command | What It Does |
|---------|-------------|
| `/discovery-report` | Submit new discovery (4-step flow) |
| `/haven-export` | Export discoveries to JSON |
| `/advanced-search` | Search archive with filters |
| `/pattern-analysis` | Manually analyze specific discovery |
| `/view-patterns` | Browse all patterns (optionally by tier) |
| `/mystery-tier` | Check your progression |
| `/community-challenge` | View/join active challenges |
| `/leaderboards` | See rankings |
| `/keeper-story` | Get personalized Keeper narrative |
| `/setup-channels` | ⚙️ Admin: Configure channels |
| `/server-stats` | ⚙️ Admin: View statistics |
| `/keeper-config` | ⚙️ Admin: Adjust settings |
| `/pattern-manager` | ⚙️ Admin: Manage patterns |

---

## Key Benefits

✅ **Organized Discovery Tracking** - Never lose your exploration notes  
✅ **Automatic Pattern Detection** - Bot finds connections you might miss  
✅ **Community Collaboration** - Multiple explorers contribute to shared mysteries  
✅ **Roleplay Enhancement** - The Keeper adds story depth to exploration  
✅ **Haven Integration** - Two-way sync between map and lore database  
✅ **Progression System** - Tiers and achievements for engagement  
✅ **Exportable Data** - Own your discoveries, export anytime  

---

## Current Status

- ✅ **Phase 1:** Discovery submission with Haven integration
- ✅ **Phase 2:** Pattern recognition and mystery tiers  
- ✅ **Phase 3:** Archive search and admin tools
- ✅ **Phase 4:** Community features and progression
- 🔄 **Phase 5 (Planned):** Advanced AI responses, deeper roleplay

---

**TL;DR:** Discord bot reads your Haven star map, lets you submit lore discoveries with location context, automatically detects patterns across submissions, and exports everything back to enhance your map. The Keeper acts as an in-character AI that analyzes your findings and builds collaborative mysteries. 🌌
