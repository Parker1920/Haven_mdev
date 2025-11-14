# Admin Quick Reference Guide

**The Keeper Discord Bot - Admin Commands**

---

## 🔑 Admin Role Configuration

**Your Admin Role ID:** `1436890437909610618`
**Set in:** `.env` file as `ADMIN_ROLE_ID`

To grant admin access, assign this role to users in Discord.

---

## 🔒 Admin-Only Commands (7 Total)

### Bot Configuration
```
/setup-channels
Configure which Discord channels the bot uses for:
- Discoveries
- Archive
- Investigations
- Lore discussions
```

```
/keeper-config
Configure bot behavior settings:
- Pattern detection thresholds
- Auto-pattern analysis on/off
- Minimum discoveries for patterns
```

### Data Management
```
/reload-haven
Reload star systems from VH-Database.db
Use after: Adding new systems via wizard or manual DB updates
```

```
/haven-export [system_name]
Export discoveries in Haven-compatible format
Optional: Specify system name, or export all
Use for: Integrating discoveries into other Haven tools
```

### Pattern & Challenge Management
```
/pattern-manager
View and manage detected patterns across discoveries
Shows: Pattern list, similarity scores, discovery clusters
```

```
/pattern-analysis <discovery_id>
Manually trigger pattern analysis for a specific discovery
Use for: Testing pattern recognition or investigating anomalies
```

```
/create-challenge
Create a new community challenge for explorers
Opens: Modal to define challenge goals, rewards, duration
```

---

## 👥 User Commands (Available to Everyone)

### Discovery Submission
- `/discovery-report` - Submit a discovery to the archive (Haven-Enhanced)

### Search & Browse
- `/search-discoveries` - Basic search
- `/advanced-search` - Advanced filtering options
- `/view-patterns` - View detected patterns by tier

### Community & Progression
- `/mystery-tier` - View personal progression
- `/community-challenge` - View/join active challenges
- `/leaderboards` - Rankings and statistics
- `/server-stats` - Server activity overview

### Story & Lore
- `/keeper-story` - Interactive story experience
- `/story-intro` - Act I introduction
- `/story-progress` - Community story progression

---

## 📊 When to Use Admin Commands

### After Adding Systems
```bash
1. Add system via System Entry Wizard
2. Run /reload-haven in Discord
3. Verify system appears in /discovery-report system list
```

### For Data Analysis
```bash
1. Check /pattern-manager for new patterns
2. Use /pattern-analysis for specific investigations
3. Export data via /haven-export if needed
```

### Managing Community
```bash
1. Monitor /server-stats for activity
2. Create challenges via /create-challenge
3. Configure channels via /setup-channels (if needed)
```

### Bot Maintenance
```bash
1. Adjust behavior via /keeper-config
2. Reconfigure channels via /setup-channels
3. Reload systems via /reload-haven
```

---

## 🚨 Important Notes

1. **Commands Auto-Hide:** Regular users won't see admin commands in their list
2. **Discovery Fix Active:** location_name bug fixed - discoveries will link to planets
3. **Clean Slate:** Database reset complete - 0 discoveries, 5 systems ready
4. **Legacy Disabled:** Old discovery system removed - no duplicate commands

---

## 🔧 Quick Troubleshooting

**Users can't submit discoveries?**
- Check channels configured via `/setup-channels`
- Verify bot has permissions in discovery channel
- Check `DISCOVERY_CHANNEL_ID` in .env

**New system not appearing?**
- Run `/reload-haven` after adding systems
- Check bot startup logs for Haven system count
- Verify system exists in VH-Database.db

**Pattern detection not working?**
- Check `/keeper-config` settings
- Verify `MIN_DISCOVERIES_FOR_PATTERN` in .env (default: 3)
- Use `/pattern-analysis` to manually trigger

**Admin commands not visible?**
- Verify user has Administrator permission in Discord
- OR verify user has role ID: 1436890437909610618
- Bot must be fully restarted after role changes

---

## 📝 Admin Workflow Example

### Daily Operations:
1. Monitor `/server-stats` for activity
2. Check `/pattern-manager` for new discoveries
3. Review and approve community contributions

### Weekly Tasks:
1. Create new `/create-challenge` for engagement
2. Review `/leaderboards` and recognize top contributors
3. Export data via `/haven-export` for backups

### After Updates:
1. Add new systems via wizard
2. Run `/reload-haven` to sync
3. Test discovery submission works
4. Verify patterns detect correctly

---

## 🆘 Emergency Commands

**Bot stuck or unresponsive?**
```bash
cd docs/guides/Haven-lore/keeper-bot
taskkill /F /IM python.exe
py src/main.py
```

**Need to reset discoveries?**
```bash
py scripts/utils/reset_discoveries.py
# Keeps all systems, removes all discoveries
```

**Restore from backup?**
```bash
copy data\VH-Database.db.backup_before_discovery_reset data\VH-Database.db /Y
```

---

**Documentation:**
- Full command audit: [COMMAND_AUDIT.md](COMMAND_AUDIT.md)
- Permission update details: [PERMISSIONS_UPDATE_SUMMARY.md](PERMISSIONS_UPDATE_SUMMARY.md)
- Production reset: [DISCORD_BOT_RESET_SUMMARY.md](../../DISCORD_BOT_RESET_SUMMARY.md)
