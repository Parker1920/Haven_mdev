# 🌌 THE KEEPER BOT - QUICK COMMANDS GUIDE

## 🚀 **LAUNCH COMMANDS**

### **Start the Bot:**
```bash
cd /Users/parkerstouffer/Desktop/Haven-lore/keeper-bot/src
source /Users/parkerstouffer/Desktop/Haven-lore/.venv/bin/activate
python main.py
```

### **Alternative Launch:**
```bash
cd /Users/parkerstouffer/Desktop/Haven-lore/keeper-bot/src
/Users/parkerstouffer/Desktop/Haven-lore/.venv/bin/python main.py
```

---

## 💬 **DISCORD SLASH COMMANDS**

### **🔍 FOR ALL USERS:**

| Command | Description | Example Usage |
|---------|-------------|---------------|
| `/discovery-report` | Submit a discovery report | Choose star system → Select planet → Fill details |
| `/archive-search` | Search the archive database | Search by type, location, user, date range |
| `/mystery-tier` | View your tier progression | See current tier, progress to next level |
| `/community-challenge` | Join active challenges | View/participate in community events |
| `/leaderboards` | View community rankings | Browse discovery, pattern, activity leaders |
| `/keeper-story` | Get personalized story | Experience Keeper narrative based on your progress |

### **⚙️ FOR ADMINISTRATORS:**

| Command | Description | Example Usage |
|---------|-------------|---------------|
| `/setup-channels` | Configure bot channels | Set discovery, archive, investigation channels |
| `/server-stats` | View server statistics | See discovery counts, patterns, user activity |
| `/keeper-config` | Configure bot settings | Adjust pattern thresholds, auto-detection |
| `/pattern-management` | Manage detected patterns | Review, approve, investigate patterns |

---

## 🎯 **TIER PROGRESSION SYSTEM**

### **Tier Levels:**
1. **🔰 Initiate Explorer** (Starting tier)
2. **🔍 Pattern Seeker** (5 discoveries, 1 pattern contribution)
3. **🧠 Lore Investigator** (15 discoveries, 3 pattern contributions)
4. **📚 Archive Curator** (30 discoveries, 5 pattern contributions)

### **Tier Benefits:**
- **Tier 2+**: Pattern analysis tools, enhanced discovery formatting
- **Tier 3+**: Investigation threads, advanced search, challenge participation
- **Tier 4**: Full archive access, pattern creation, community event hosting

---

## 🏆 **COMMUNITY FEATURES**

### **Challenge Types:**
- **Discovery Challenges**: Find specific types of discoveries
- **Pattern Hunts**: Contribute to emerging pattern investigations
- **Lore Events**: Collaborative storytelling experiences
- **Exploration Contests**: Compete across different star systems

### **Leaderboard Categories:**
- **🔍 Total Discoveries**: Ranked by discovery count
- **🌀 Pattern Insights**: Ranked by pattern contributions
- **📈 Recent Activity**: Most active this week
- **🎯 Mystery Tier**: Highest tier explorers

---

## 🛠️ **SETUP & MAINTENANCE**

### **Initial Server Setup:**
```bash
# 1. Invite bot to Discord server
# 2. Run this command in Discord:
/setup-channels

# 3. Configure channels:
- #discovery-reports (required)
- #keeper-archive (required)
- #investigation-threads (optional)
- #lore-discussion (optional)
```

### **Testing Commands:**
```bash
# Verify all systems
cd /Users/parkerstouffer/Desktop/Haven-lore/keeper-bot
python verify_phase4.py

# Test imports only
cd /Users/parkerstouffer/Desktop/Haven-lore/keeper-bot/src
python -c "from main import TheKeeper; print('✅ Ready')"
```

### **Troubleshooting:**
```bash
# Fix SSL issues (macOS)
/Applications/Python\ 3.14/Install\ Certificates.command

# Check environment
cd /Users/parkerstouffer/Desktop/Haven-lore/keeper-bot
cat .env

# Reinstall dependencies
pip install discord.py aiofiles aiosqlite python-dotenv
```

---

## 📝 **DISCOVERY SUBMISSION FLOW**

1. **User runs** `/discovery-report`
2. **Bot shows** Haven star system selector
3. **User picks** system → planet/moon
4. **Modal opens** with discovery details form
5. **User fills** type, description, significance, evidence
6. **Keeper responds** with personality-appropriate analysis
7. **Auto-analysis** checks for patterns across discoveries
8. **If pattern found**: Creates investigation thread
9. **User gets** tier progression credit

---

## 🌀 **PATTERN RECOGNITION**

### **How It Works:**
- Bot analyzes discoveries for similarities
- Groups by: location, type, time period, conditions
- Calculates confidence levels (0-100%)
- Auto-creates investigation threads for strong patterns
- Awards tier progression for pattern contributions

### **Mystery Tier Classification:**
- **Tier 1**: 3+ similar discoveries (Surface Anomaly)
- **Tier 2**: 7+ discoveries with strong correlation (Pattern Emergence)
- **Tier 3**: 15+ discoveries, cross-system patterns (Deep Mystery)
- **Tier 4**: 30+ discoveries, cosmic significance (Universe-altering)

---

## 💡 **PRO TIPS**

### **For Users:**
- **Include coordinates** for better pattern matching
- **Upload photos** for visual evidence
- **Reference related discoveries** to strengthen patterns
- **Participate in challenges** for faster tier progression
- **Check `/mystery-tier`** regularly to track progress

### **For Admins:**
- **Monitor `/server-stats`** for community health
- **Launch challenges** within 48 hours of setup
- **Review patterns** in `/pattern-management` weekly
- **Adjust thresholds** in `/keeper-config` based on activity
- **Celebrate tier progressions** to encourage engagement

---

## 🔗 **INTEGRATION WITH HAVEN**

The Keeper works alongside your existing Haven star mapping system:
- **Haven** = Navigation tool for coordinates/systems
- **Keeper** = Lore archive and community engagement
- **Data sync**: Reads Haven's star system data directly
- **Complementary**: Use both for complete exploration experience

---

**🌌 The archive awaits your discoveries. Begin your journey into the mysteries of Haven!**