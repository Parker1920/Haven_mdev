# 🔮 The Keeper - Quick Command Reference

## 🔍 Discovery Commands

### `/discovery-report`
Submit a discovery to The Keeper's Archive. Select a Haven star system, choose a location (planet/moon/space), pick discovery type, and provide details. Discoveries are posted to #keeper-archives and analyzed for patterns.

### `/haven-export`
Export all discoveries as JSON for Haven star map integration. Creates a downloadable file with all archived discoveries.

---

## 🌀 Pattern & Analysis

### `/pattern-analysis [discovery_id]`
Manually trigger pattern analysis on a specific discovery. Useful for testing or re-analyzing discoveries. Creates investigation threads when patterns are detected.

### `/view-patterns [tier]`
View all detected patterns organized by mystery tier (1-4). Shows pattern names, discovery counts, confidence levels, and descriptions.

---

## 📚 Archive & Search

### `/advanced-search`
Search the archive with filters: keywords, date range, location, user, or pattern/tier. Returns paginated results with detailed discovery information.

### `/pattern-manager`
*Admin only* - Manage patterns: update status, edit descriptions, merge similar patterns, or archive old patterns.

---

## 🎮 Community & Progression

### `/mystery-tier`
View your personal mystery tier progression (1-4), statistics (discoveries, patterns contributed), and requirements for next tier.

### `/community-challenge`
View the current active community challenge, including type, duration, description, and rewards. Encourages collaborative discovery efforts.

### `/leaderboards [type]`
View community rankings: Top Explorers (discoveries), Pattern Hunters (contributions), Weekly Most Active, or Tier Masters (highest tiers).

### `/keeper-story`
Read The Keeper's lore and backstory. Learn about the mysterious AI consciousness that archives Haven's discoveries and why patterns matter.

### `/create-challenge`
*Admin only* - Create a new community challenge with custom type, duration, description, and rewards.

---

## 🔧 Server Setup (Admin)

### `/setup-channels`
Configure bot channels: set archive channel (where discoveries post), announcements channel, and other bot settings.

### `/server-stats`
View server statistics: total discoveries, patterns detected, active investigators, tier distribution, and recent activity.

### `/keeper-config`
Manage advanced bot configuration: pattern detection thresholds, mystery tier requirements, personality settings, and feature toggles.

---

## 📊 Quick Tips

- **Start here:** `/discovery-report` to submit your first discovery
- **Track progress:** `/mystery-tier` to see your advancement
- **Find patterns:** 3+ similar discoveries trigger automatic pattern detection
- **Investigate:** Pattern alerts create threads for collaboration
- **Compete:** `/leaderboards` to see top contributors

*The Archive awaits your discoveries, explorer.* 🌌
