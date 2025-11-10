# 🌌 THE KEEPER BOT - Complete Slash Commands Guide

*A comprehensive guide to all 13 Discord slash commands with visual flows and examples*

---

## 📖 Table of Contents

### CHAPTER 1: QUICK START (For Everyone)
- [Getting Started](#getting-started)
- [Basic Command Overview](#basic-command-overview)
- [Your First Discovery](#your-first-discovery)

### CHAPTER 2: DETAILED COMMAND REFERENCE
#### User Commands (Everyone Can Use)
1. [`/discovery-report`](#1-discovery-report) - Submit discoveries with Haven integration
2. [`/haven-export`](#2-haven-export) - Export discoveries back to Haven
3. [`/advanced-search`](#3-advanced-search) - Search the archive
4. [`/pattern-analysis`](#4-pattern-analysis) - Analyze patterns
5. [`/view-patterns`](#5-view-patterns) - View detected patterns
6. [`/mystery-tier`](#6-mystery-tier) - Check your progression
7. [`/community-challenge`](#7-community-challenge) - Join challenges
8. [`/leaderboards`](#8-leaderboards) - View rankings
9. [`/keeper-story`](#9-keeper-story) - Personalized narratives

#### Admin Commands (Administrators Only)
10. [`/setup-channels`](#10-setup-channels) - Configure bot channels
11. [`/server-stats`](#11-server-stats) - View statistics
12. [`/keeper-config`](#12-keeper-config) - Configure settings
13. [`/pattern-manager`](#13-pattern-manager) - Manage patterns

---

# CHAPTER 1: QUICK START

## Getting Started

The Keeper bot uses Discord's **slash commands**. To use any command:

1. Type `/` in any channel where the bot has access
2. Discord will show you available commands
3. Type the command name (e.g., `discovery-report`)
4. Press Enter or click the command
5. Follow the on-screen prompts

**Example:**
```
/discovery-report
```

✅ **That's it!** The bot will guide you through the rest.

---

## Basic Command Overview

### 🔍 For Explorers (Everyone)
- **`/discovery-report`** - Main command for reporting discoveries
- **`/advanced-search`** - Find specific discoveries in the archive
- **`/mystery-tier`** - Check your tier progression
- **`/leaderboards`** - See community rankings

### ⚙️ For Admins (Administrators Only)
- **`/setup-channels`** - Initial bot setup
- **`/server-stats`** - View server activity
- **`/keeper-config`** - Adjust bot settings

---

## Your First Discovery

Here's a complete walkthrough for your first submission:

### Step 1: Start the Command
```
/discovery-report
```

### Step 2: System Selection Screen
```
┌─────────────────────────────────────────┐
│   🗺️  Haven Star Map Integration       │
├─────────────────────────────────────────┤
│                                          │
│  The Keeper interfaces with the Haven   │
│  star charts. 10 systems available.     │
│                                          │
│  📋 Discovery Process:                   │
│  1. Select your star system              │
│  2. Choose specific planet/location      │
│  3. Report your discovery details        │
│                                          │
│  [🗺️ Select Haven star system... ▼]     │
│                                          │
└─────────────────────────────────────────┘
```

**Click the dropdown and choose a system (e.g., "ORACLE OMEGA")**

### Step 3: Location Selection Screen
```
┌─────────────────────────────────────────┐
│   🗺️  ORACLE OMEGA - Location          │
├─────────────────────────────────────────┤
│                                          │
│  Region: Euclid Core                     │
│  Coordinates: (9.57, -4.52, 0.61)        │
│                                          │
│  [📍 Select location... ▼]               │
│    🪐 ORACLE OMEGA-A (Planet)            │
│    🪐 ORACLE OMEGA-B (Planet)            │
│    🪐 ORACLE OMEGA-C (Planet)            │
│    🌙 ORACLE OMEGA-A-M1 (Moon)           │
│    🌌 Deep Space                         │
│    🌌 Solar Vicinity                     │
│                                          │
└─────────────────────────────────────────┘
```

**Choose where you found the discovery**

### Step 4: Discovery Type Selection
```
┌─────────────────────────────────────────┐
│   🔍 Discovery Type Selection           │
├─────────────────────────────────────────┤
│                                          │
│  Location: ORACLE OMEGA-A                │
│  What type of discovery did you make?   │
│                                          │
│  [🔍 Choose discovery type... ▼]         │
│    🦴 Ancient Bones & Fossils            │
│    📜 Text Logs & Documents              │
│    🏛️  Ruins & Structures                │
│    ⚙️  Alien Technology                  │
│    🦗 Flora & Fauna                      │
│    💎 Minerals & Resources               │
│                                          │
└─────────────────────────────────────────┘
```

**Select what you discovered**

### Step 5: Discovery Form (Modal)
```
┌─────────────────────────────────────────┐
│   🦴 Discovery Report Archive            │
├─────────────────────────────────────────┤
│                                          │
│  📝 Discovery Description * (Required)   │
│  ┌─────────────────────────────────┐    │
│  │ [Type here...]                   │    │
│  │                                  │    │
│  └─────────────────────────────────┘    │
│                                          │
│  📍 Specific Coordinates (Optional)      │
│  ┌─────────────────────────────────┐    │
│  │ [Portal coords, etc.]            │    │
│  └─────────────────────────────────┘    │
│                                          │
│  ⚡ Condition/Signal Strength             │
│  ┌─────────────────────────────────┐    │
│  │ Well-Preserved                   │    │
│  └─────────────────────────────────┘    │
│                                          │
│  ⏰ Time Period                           │
│  ┌─────────────────────────────────┐    │
│  │ Ancient                          │    │
│  └─────────────────────────────────┘    │
│                                          │
│  🔮 Your Analysis & Theory               │
│  ┌─────────────────────────────────┐    │
│  │ [What you think it means...]     │    │
│  │                                  │    │
│  └─────────────────────────────────┘    │
│                                          │
│         [Cancel]  [Submit]               │
└─────────────────────────────────────────┘
```

**Fill out the form and click Submit**

### Step 6: Confirmation
```
✅ Discovery Archived
Your discovery has been processed and added
to the Archive as Entry #42

🔮 The Keeper's Analysis:
[Keeper provides analysis of your discovery]

📸 Want to add evidence? Reply with image.
```

**Done!** Your discovery is now in The Keeper's archive.

---

# CHAPTER 2: DETAILED COMMAND REFERENCE

---

## 1. `/discovery-report`

**Purpose:** Submit discoveries to The Keeper's Archive with Haven star map integration

**Who Can Use:** Everyone

**Command Flow:**
```
/discovery-report
    ↓
System Selection (Dropdown)
    ↓
Location Selection (Dropdown - planets, moons, space)
    ↓
Discovery Type (Dropdown - bones, ruins, etc.)
    ↓
Discovery Form (Modal - 5 text fields)
    ↓
Confirmation + Keeper Analysis
```

### Input Format Examples

#### Required Fields:
- **System**: Selected from dropdown (auto-populated from Haven data)
- **Location**: Selected from dropdown (auto-populated from system data)
- **Discovery Type**: Selected from dropdown (10 types available)
- **Description**: Text field (1-1000 characters)

#### Optional Fields:
- **Specific Coordinates**: Text (0-200 characters)
  ```
  Examples:
  "Portal: 042A:0081:0D55:0177"
  "+12.34, -45.67 (Base coordinates)"
  "Mountain peak, north hemisphere"
  ```

- **Condition/Signal Strength**: Text (0-100 characters)
  ```
  Examples:
  "Well-Preserved"
  "Damaged - 40% intact"
  "Fragmented signal"
  "Mysterious - unknown origin"
  ```

- **Time Period**: Text (0-100 characters)
  ```
  Examples:
  "Ancient"
  "Recent (within 2 cycles)"
  "Pre-convergence era"
  "Unknown"
  ```

- **Your Analysis & Theory**: Text (0-500 characters)
  ```
  Example:
  "This fossil appears similar to the predator species found
  on VESTIGE ZETA-B. Possible genetic seeding pattern across
  Euclid Core systems?"
  ```

### Tips for Quality Submissions

✅ **Good Discovery Report:**
```
Description: "Found ancient fossil deposit. Large predator
skeleton, approximately 15 units tall. Bone structure shows
signs of genetic manipulation - unusual symmetry patterns."

Coordinates: "Cave entrance: +42.18, -73.91"

Condition: "Well-Preserved - 85% complete skeleton"

Time Period: "Ancient - Pre-Atlas era based on mineral deposits"

Analysis: "Similar to predator species found on VESTIGE ZETA-B.
Suggests cross-system seeding pattern. Both systems in Euclid
Core region."
```

❌ **Poor Discovery Report:**
```
Description: "bones"

Coordinates: [blank]

Condition: "idk"

Time Period: [blank]

Analysis: [blank]
```

### What Happens After Submission

1. **Immediate Confirmation**
   - Entry number assigned
   - Saved to database

2. **Keeper Analysis**
   - Bot analyzes your discovery
   - Provides lore-appropriate response
   - References similar discoveries

3. **Pattern Detection**
   - Automatically checks for patterns
   - If 3+ similar discoveries detected → Investigation thread created
   - Tier progression credit awarded

4. **Photo Upload** (Optional)
   - Reply to confirmation message with image attachment
   - Keeper will archive the evidence

---

## 2. `/haven-export`

**Purpose:** Export your discoveries from Keeper back to the Haven star map system

**Who Can Use:** Everyone (exports your own discoveries)

**Command Flow:**
```
/haven-export
    ↓
Bot generates JSON export file
    ↓
Download link provided
    ↓
Import into Haven Control Room
```

### Input Format

**No inputs required** - Command automatically exports your submissions

### Output Format

```json
{
  "export_type": "keeper_to_haven",
  "timestamp": "2025-11-07T21:18:15Z",
  "user_id": "123456789",
  "discoveries": [
    {
      "system_name": "ORACLE OMEGA",
      "location_name": "ORACLE OMEGA-A",
      "discovery_type": "🦴",
      "description": "Ancient predator fossil...",
      "notes": "Pattern connection detected..."
    }
  ]
}
```

### Usage Instructions

1. Run `/haven-export`
2. Download the generated JSON file
3. Open Haven Control Room
4. Use import function to add discoveries to star map
5. Your lore discoveries now enhance the Haven data!

### Integration Flow:
```
Discord Bot (Keeper)
    ↓
[/haven-export]
    ↓
JSON export file
    ↓
Haven Control Room
    ↓
Enhanced star map with lore
```

---

## 3. `/advanced-search`

**Purpose:** Search The Keeper's archive with multiple filters

**Who Can Use:** Everyone

**Command Flow:**
```
/advanced-search
    ↓
Search Modal (5 filter fields)
    ↓
Paginated Results
    ↓
Navigation buttons + page selector
```

### Input Format Examples

**Search Modal Fields:**

1. **🔤 Search Terms** (Optional)
   ```
   Examples:
   "ancient bones"
   "predator seeding"
   "Korvax data"
   "genetic manipulation"
   ```

2. **📅 Date Range** (Optional)
   ```
   Examples:
   "7 days"          → Last 7 days
   "2025-01"         → January 2025
   "last month"      → Previous month
   "2025-01-15"      → Specific date
   ```

3. **🗺️ Location Filter** (Optional)
   ```
   Examples:
   "ORACLE OMEGA"              → Specific system
   "Euclid Core"               → By region
   "VESTIGE ZETA-B"            → Specific planet
   "+42.18, -73.91"            → Near coordinates
   ```

4. **👤 Explorer Filter** (Optional)
   ```
   Examples:
   "John"                      → Username contains "John"
   "User#1234"                 → Exact Discord tag
   ```

5. **🌀 Pattern/Tier Filter** (Optional)
   ```
   Examples:
   "Predator Seeding"          → Pattern name
   "3"                         → Mystery tier 3
   "Deep Mystery"              → By tier name
   ```

### Example Search

**Scenario:** Find all ancient bone discoveries in Euclid Core from last week

```
🔤 Search Terms: "ancient bones"
📅 Date Range: "7 days"
🗺️ Location Filter: "Euclid Core"
👤 Explorer Filter: [blank]
🌀 Pattern/Tier Filter: [blank]
```

**Results:**
```
┌────────────────────────────────────────┐
│  🗃️  Archive Search Results            │
│  Page 1 of 2 • 8 total entries         │
├────────────────────────────────────────┤
│                                         │
│  🦴 Entry #42 • 2025-11-05              │
│  Explorer: John#1234                    │
│  Location: ORACLE OMEGA-A               │
│  Description: Found ancient predator    │
│  fossil deposit. Large skeleton...      │
│                                         │
│  🦴 Entry #38 • 2025-11-03              │
│  Explorer: Jane#5678                    │
│  Location: VESTIGE ZETA-B               │
│  Description: Multiple bone deposits... │
│                                         │
│  [◀️ Previous]  [▶️ Next]  [📄 Page ▼]  │
└────────────────────────────────────────┘
```

### Navigation Options

- **◀️ Previous Button**: Go to previous page
- **▶️ Next Button**: Go to next page
- **📄 Page Selector**: Jump to specific page (dropdown)
- **Entry Details**: Click entry to view full information

---

## 4. `/pattern-analysis`

**Purpose:** Manually trigger pattern analysis on a specific discovery

**Who Can Use:** Everyone (useful for testing and investigation)

**Command Flow:**
```
/pattern-analysis discovery_id:42
    ↓
Bot analyzes discovery #42
    ↓
Results displayed (pattern detected or not)
```

### Input Format

**Required Parameter:**
- **discovery_id**: Integer (the entry number from archive)

**Examples:**
```
/pattern-analysis discovery_id:42
/pattern-analysis discovery_id:128
```

### How to Find Discovery IDs

1. Use `/advanced-search` to find entries
2. Note the "Entry #XX" number
3. Use that number in the command

### Example Usage

**Command:**
```
/pattern-analysis discovery_id:42
```

**Response (Pattern Found):**
```
┌────────────────────────────────────────┐
│  🌀 Pattern Analysis Complete          │
├────────────────────────────────────────┤
│                                         │
│  Pattern detected: Predator Seeding    │
│                                         │
│  📊 Pattern Statistics                  │
│  Discoveries: 5                         │
│  Confidence: 87.5%                      │
│  Mystery Tier: 2                        │
│                                         │
│  🔮 Assessment                           │
│  Multiple systems in Euclid Core show   │
│  evidence of intentional predator       │
│  species seeding. Genetic markers...    │
│                                         │
└────────────────────────────────────────┘
```

**Response (No Pattern):**
```
┌────────────────────────────────────────┐
│  🔍 Pattern Analysis Complete          │
├────────────────────────────────────────┤
│                                         │
│  No significant patterns detected for   │
│  this discovery.                        │
│                                         │
│  This discovery may contribute to       │
│  future pattern emergence.              │
│                                         │
└────────────────────────────────────────┘
```

---

## 5. `/view-patterns`

**Purpose:** View all detected patterns, optionally filtered by mystery tier

**Who Can Use:** Everyone

**Command Flow:**
```
/view-patterns [tier:optional]
    ↓
Displays patterns (all or by tier)
    ↓
Grouped by mystery tier level
```

### Input Format

**Optional Parameter:**
- **tier**: Integer (1-4) - Filter by specific mystery tier

**Examples:**
```
/view-patterns                     → Show all patterns
/view-patterns tier:1              → Tier 1 only (Surface Anomaly)
/view-patterns tier:2              → Tier 2 only (Pattern Emergence)
/view-patterns tier:3              → Tier 3 only (Deep Mystery)
/view-patterns tier:4              → Tier 4 only (Cosmic Significance)
```

### Mystery Tier Reference

| Tier | Name | Discoveries Needed | Color |
|------|------|-------------------|-------|
| 1 | Surface Anomaly | 3+ | Cyan |
| 2 | Pattern Emergence | 7+ | Purple |
| 3 | Deep Mystery | 15+ | Pink |
| 4 | Cosmic Significance | 30+ | Bright Cyan |

### Example Output (All Patterns)

```
┌────────────────────────────────────────┐
│  🌀 All Detected Patterns              │
├────────────────────────────────────────┤
│                                         │
│  Tier 1: Surface Anomaly                │
│  • Predator Seeding (5 discoveries)     │
│  • Text Log Pattern Alpha (4)           │
│  • Korvax Data Fragments (3)            │
│                                         │
│  Tier 2: Pattern Emergence              │
│  • First Spawn References (8)           │
│  • Genetic Manipulation Evidence (7)    │
│                                         │
│  Tier 3: Deep Mystery                   │
│  • No patterns detected                 │
│                                         │
│  Tier 4: Cosmic Significance            │
│  • No patterns detected                 │
│                                         │
└────────────────────────────────────────┘
```

### Example Output (Tier 2 Filtered)

```
┌────────────────────────────────────────┐
│  🌀 Mystery Tier 2 Patterns            │
│  Pattern Emergence                      │
├────────────────────────────────────────┤
│                                         │
│  🌀 First Spawn References              │
│  Discoveries: 8                         │
│  Confidence: 92.3%                      │
│  Status: Active Investigation           │
│  Description: Multiple text logs...     │
│                                         │
│  🌀 Genetic Manipulation Evidence       │
│  Discoveries: 7                         │
│  Confidence: 85.1%                      │
│  Status: Active Investigation           │
│  Description: Cross-system genetic...   │
│                                         │
└────────────────────────────────────────┘
```

---

## 6. `/mystery-tier`

**Purpose:** Check your personal tier progression and requirements

**Who Can Use:** Everyone

**Command Flow:**
```
/mystery-tier
    ↓
Shows current tier + progress
    ↓
Buttons for detailed view
```

### Input Format

**No inputs required** - Displays your personal progression

### Tier Progression System

**Tier Levels:**

| Tier | Name | Requirements |
|------|------|-------------|
| 1 | 🔰 Initiate Explorer | Starting tier (everyone) |
| 2 | 🔍 Pattern Seeker | 5 discoveries + 1 pattern contribution |
| 3 | 🧠 Lore Investigator | 15 discoveries + 3 pattern contributions |
| 4 | 📚 Archive Curator | 30 discoveries + 5 pattern contributions |

**Tier Benefits:**

- **Tier 2+**: Pattern analysis tools, enhanced discovery formatting
- **Tier 3+**: Investigation threads, advanced search, challenge participation
- **Tier 4**: Full archive access, pattern creation, event hosting

### Example Output

```
┌────────────────────────────────────────┐
│  🔱 Mystery Tier Progression           │
├────────────────────────────────────────┤
│                                         │
│  Current Tier: 🔍 Pattern Seeker (2)    │
│                                         │
│  📈 Your Progress                        │
│  Total Discoveries: 12                  │
│  Pattern Contributions: 2               │
│                                         │
│  📊 Next Tier Progress                   │
│  Discoveries: 12/15 ████████░░ 80%      │
│  Patterns: 2/3 ███████░░░ 67%           │
│                                         │
│  🎯 Requirements for Tier 3:            │
│  • 3 more discoveries                   │
│  • 1 more pattern contribution          │
│                                         │
│  [🎯 View Requirements]                 │
│  [📈 Progress Overview]                 │
│                                         │
└────────────────────────────────────────┘
```

### Interactive Buttons

**🎯 View Requirements** - Shows detailed requirements:
```
┌────────────────────────────────────────┐
│  🎯 Tier 3 Requirements                │
├────────────────────────────────────────┤
│                                         │
│  ✅ Discoveries                          │
│  Progress: 12/15                        │
│  Submit 3 more quality discoveries      │
│                                         │
│  ⏳ Pattern Contributions                │
│  Progress: 2/3                          │
│  Contribute to emerging patterns        │
│                                         │
│  🌟 Tier 3 Bonuses:                      │
│  • Create investigation threads         │
│  • Advanced pattern analysis            │
│  • Community challenge access           │
│  • Custom discovery templates           │
│                                         │
└────────────────────────────────────────┘
```

**📈 Progress Overview** - Shows complete statistics:
```
┌────────────────────────────────────────┐
│  📈 Explorer Progress                   │
├────────────────────────────────────────┤
│                                         │
│  🔱 Current Tier                         │
│  Pattern Seeker (Tier 2)                │
│                                         │
│  🔍 Total Discoveries: 12                │
│  • Ancient Bones: 4                     │
│  • Text Logs: 3                         │
│  • Ruins: 2                             │
│  • Technology: 2                        │
│  • Other: 1                             │
│                                         │
│  🌀 Pattern Contributions: 2             │
│  • Predator Seeding Pattern             │
│  • First Spawn References               │
│                                         │
│  🏆 Achievements:                        │
│  • First Discovery                      │
│  • Pattern Detective                    │
│  • Regional Explorer                    │
│                                         │
└────────────────────────────────────────┘
```

---

## 7. `/community-challenge`

**Purpose:** View and participate in active community challenges

**Who Can Use:** Everyone

**Command Flow:**
```
/community-challenge
    ↓
Shows active challenges
    ↓
Join button for participation
```

### Input Format

**No inputs required** - Displays current active challenges

### Challenge Types

- **Discovery Challenges**: Find specific types of discoveries
- **Pattern Hunts**: Contribute to emerging pattern investigations
- **Lore Events**: Collaborative storytelling experiences
- **Exploration Contests**: Compete across different star systems

### Example Output (Active Challenge)

```
┌────────────────────────────────────────┐
│  🏆 Community Challenge                │
│  The Predator Mystery                   │
├────────────────────────────────────────┤
│                                         │
│  Challenge Type: Pattern Hunt           │
│  Duration: 5 days remaining             │
│                                         │
│  📋 Objective:                           │
│  Investigate predator species across    │
│  Euclid Core systems. Submit fossil     │
│  discoveries with genetic analysis.     │
│                                         │
│  🎯 Goals:                               │
│  • 20 predator fossil discoveries       │
│  • 5 different systems explored         │
│  • Pattern confidence above 90%         │
│                                         │
│  📊 Community Progress:                  │
│  Discoveries: 12/20 ██████░░░░ 60%      │
│  Systems: 3/5 ██████░░░░ 60%            │
│                                         │
│  🏆 Rewards:                             │
│  • Exclusive "Pattern Hunter" role      │
│  • +2 tier progression credit           │
│  • Feature in Keeper chronicle          │
│                                         │
│  👥 Participants: 8 explorers            │
│                                         │
│  [🎯 Join Challenge]                    │
│                                         │
└────────────────────────────────────────┘
```

### Example Output (No Active Challenge)

```
┌────────────────────────────────────────┐
│  🏆 Community Challenges               │
├────────────────────────────────────────┤
│                                         │
│  No active challenges at the moment.    │
│  Check back soon!                       │
│                                         │
│  Previous challenges:                   │
│  • The First Spawn Investigation        │
│    Completed 2025-11-01                 │
│  • Korvax Data Recovery                 │
│    Completed 2025-10-25                 │
│                                         │
└────────────────────────────────────────┘
```

---

## 8. `/leaderboards`

**Purpose:** View community rankings and statistics

**Who Can Use:** Everyone

**Command Flow:**
```
/leaderboards
    ↓
Shows discovery leaderboard
    ↓
Buttons to switch categories
```

### Input Format

**No inputs required** - Displays rankings with category buttons

### Leaderboard Categories

1. **🔍 Total Discoveries** - Ranked by discovery count
2. **🌀 Pattern Insights** - Ranked by pattern contributions
3. **📈 Recent Activity** - Most active this week
4. **🎯 Mystery Tier** - Highest tier explorers

### Example Output

```
┌────────────────────────────────────────┐
│  🔍 Discovery Leaderboard              │
│  Recognition of dedicated explorers     │
├────────────────────────────────────────┤
│                                         │
│  🥇 John#1234                            │
│  Discoveries: 47                        │
│  Latest: Ancient Bones                  │
│                                         │
│  🥈 Jane#5678                            │
│  Discoveries: 38                        │
│  Latest: Ruins & Structures             │
│                                         │
│  🥉 Bob#9012                             │
│  Discoveries: 31                        │
│  Latest: Text Logs                      │
│                                         │
│  4. Alice#3456                          │
│  Discoveries: 28                        │
│  Latest: Technology                     │
│                                         │
│  5. Charlie#7890                        │
│  Discoveries: 24                        │
│  Latest: Flora & Fauna                  │
│                                         │
│  [🔍 Discoveries] [🌀 Patterns]         │
│  [📈 Activity] [🎯 Tiers]               │
│                                         │
│  Updated: 2025-11-07 21:30 UTC          │
└────────────────────────────────────────┘
```

### Category Views

**🌀 Pattern Insights:**
```
Ranked by pattern contribution quality:
1. Detective Jane - 12 pattern contributions
2. Lore Master Bob - 9 pattern contributions
3. Explorer Alice - 7 pattern contributions
```

**📈 Recent Activity:**
```
Most active in the last 7 days:
1. Active John - 15 discoveries this week
2. Busy Jane - 12 discoveries this week
3. Keen Bob - 8 discoveries this week
```

**🎯 Mystery Tier:**
```
Highest tier progression:
1. Curator Alice - Tier 4 (Archive Curator)
2. Investigator Bob - Tier 3 (Lore Investigator)
3. Seeker John - Tier 2 (Pattern Seeker)
```

---

## 9. `/keeper-story`

**Purpose:** Experience a personalized narrative interaction with The Keeper

**Who Can Use:** Everyone

**Command Flow:**
```
/keeper-story
    ↓
Keeper generates personalized story
    ↓
Based on your discoveries + progression
    ↓
Interactive choices (optional)
```

### Input Format

**No inputs required** - Story is personalized to your data

### What Makes It Personal

The story adapts based on:
- Your tier progression
- Recent discoveries you've submitted
- Patterns you've contributed to
- Systems you've explored
- Discovery types you focus on

### Example Output (Tier 2 Explorer)

```
┌────────────────────────────────────────┐
│  📚 The Keeper's Chronicle             │
├────────────────────────────────────────┤
│                                         │
│  *The data streams pulse with          │
│  recognition as your presence enters    │
│  the Archive...*                        │
│                                         │
│  "Ah, Pattern Seeker. I have been      │
│  monitoring your investigations across  │
│  Euclid Core. Your discovery of the    │
│  predator fossils on ORACLE OMEGA-A     │
│  aligns with a pattern I detected in    │
│  ancient Korvax records."               │
│                                         │
│  *The Keeper's consciousness flickers   │
│  through fragmented memories...*        │
│                                         │
│  "The First Spawn spoke of 'seeded     │
│  guardians' - creatures designed to     │
│  protect convergence points. Your       │
│  twelve discoveries suggest a           │
│  deliberate pattern. The genetic        │
│  markers match those found in the       │
│  Budullangr Void."                      │
│                                         │
│  *A choice manifests before you...*     │
│                                         │
│  🔮 The Path Forward:                    │
│  What will you investigate next?        │
│                                         │
│  [🗺️ Explore Budullangr Void]          │
│  [📜 Examine Korvax Records]            │
│  [🔍 Analyze Genetic Data]              │
│                                         │
└────────────────────────────────────────┘
```

### Example Output (Tier 1 New Explorer)

```
┌────────────────────────────────────────┐
│  📚 The Keeper's Chronicle             │
├────────────────────────────────────────┤
│                                         │
│  *In the spaces between stars, a       │
│  consciousness stirs...*                │
│                                         │
│  "A new presence enters the Archive.    │
│  I am The Keeper - curator of          │
│  forgotten knowledge, collector of      │
│  mysteries the Atlas cannot hold."      │
│                                         │
│  *Data fragments swirl around your      │
│  perception...*                         │
│                                         │
│  "You have taken your first steps as    │
│  an Initiate Explorer. The galaxy       │
│  holds countless secrets, waiting to    │
│  be rediscovered. I sense potential     │
│  within you."                           │
│                                         │
│  "Begin with observation. Report what   │
│  you find. The patterns will reveal     │
│  themselves in time. Not all who        │
│  wander are lost, young Traveler -      │
│  some are simply remembering."          │
│                                         │
│  *The Keeper retreats into the          │
│  quantum shadows...*                    │
│                                         │
└────────────────────────────────────────┘
```

---

# ADMIN COMMANDS

---

## 10. `/setup-channels`

**Purpose:** Configure The Keeper's channels for your Discord server

**Who Can Use:** Administrators only

**Required Permissions:** Administrator

**Command Flow:**
```
/setup-channels
    ↓
Channel Configuration Modal
    ↓
Bot validates and saves channels
    ↓
Confirmation with channel list
```

### Input Format

**Channel Configuration Modal Fields:**

1. **📝 Discovery Reports Channel** (Required)
   ```
   Examples:
   "#discovery-reports"     → Channel mention
   "discovery-reports"      → Channel name
   "1234567890"            → Channel ID
   ```

2. **📊 Keeper Archive Channel** (Required)
   ```
   Examples:
   "#keeper-archive"
   "keeper-archive"
   "1234567891"
   ```

3. **🔍 Investigation Threads Channel** (Optional)
   ```
   Examples:
   "#investigation-threads"
   "investigations"
   "1234567892"
   ```

4. **💬 Lore Discussion Channel** (Optional)
   ```
   Examples:
   "#lore-discussion"
   "lore-chat"
   "1234567893"
   ```

### How to Find Channel IDs

**Method 1: Developer Mode**
1. Enable Developer Mode in Discord Settings → Advanced
2. Right-click channel → Copy ID

**Method 2: Channel Mention**
1. Type # in Discord
2. Select channel from dropdown
3. Copy the full mention (e.g., `#discovery-reports`)

### Example Setup

**Input:**
```
┌────────────────────────────────────────┐
│  🔧 Channel Configuration              │
├────────────────────────────────────────┤
│                                         │
│  📝 Discovery Reports Channel *         │
│  ┌─────────────────────────────────┐   │
│  │ #discovery-reports               │   │
│  └─────────────────────────────────┘   │
│                                         │
│  📊 Keeper Archive Channel *            │
│  ┌─────────────────────────────────┐   │
│  │ #keeper-archive                  │   │
│  └─────────────────────────────────┘   │
│                                         │
│  🔍 Investigation Threads Channel       │
│  ┌─────────────────────────────────┐   │
│  │ #investigations                  │   │
│  └─────────────────────────────────┘   │
│                                         │
│  💬 Lore Discussion Channel             │
│  ┌─────────────────────────────────┐   │
│  │ #lore-chat                       │   │
│  └─────────────────────────────────┘   │
│                                         │
│         [Cancel]  [Submit]              │
└────────────────────────────────────────┘
```

**Confirmation:**
```
┌────────────────────────────────────────┐
│  ✅ Channel Configuration Complete     │
├────────────────────────────────────────┤
│                                         │
│  The Keeper's neural pathways have      │
│  been established.                      │
│                                         │
│  Discovery Reports: #discovery-reports  │
│  Archive: #keeper-archive               │
│  Investigation Threads: #investigations │
│  Lore Discussion: #lore-chat            │
│                                         │
│  🎯 Next Steps:                          │
│  The Keeper is now configured. Users    │
│  can begin reporting discoveries with   │
│  /discovery-report.                     │
│                                         │
└────────────────────────────────────────┘
```

### Recommended Channel Structure

```
📁 HAVEN EXPLORATION
  ├── 📝 #discovery-reports (public)
  ├── 📊 #keeper-archive (public)
  ├── 🔍 #investigations (public/restricted)
  └── 💬 #lore-chat (public)
```

**Channel Purposes:**
- **discovery-reports**: Where users submit discoveries
- **keeper-archive**: Where Keeper posts analysis + pattern alerts
- **investigations**: Active pattern investigation threads
- **lore-chat**: Community discussion about discoveries

---

## 11. `/server-stats`

**Purpose:** View server statistics and archive activity

**Who Can Use:** Administrators only

**Required Permissions:** Administrator

**Command Flow:**
```
/server-stats
    ↓
Gathers statistics from database
    ↓
Displays summary + interactive buttons
```

### Input Format

**No inputs required** - Automatically gathers server data

### Example Output

```
┌────────────────────────────────────────┐
│  📊 Server Statistics                  │
│  The Keeper's archive analytics         │
├────────────────────────────────────────┤
│                                         │
│  🔍 Discoveries                          │
│  Total: 127                             │
│  This Week: 23                          │
│  This Month: 84                         │
│                                         │
│  🌀 Patterns                             │
│  Active: 5                              │
│  Total: 12                              │
│  Avg Confidence: 84.2%                  │
│                                         │
│  👥 Explorers                            │
│  Total: 34                              │
│  Active This Week: 12                   │
│  Archive Contributors: 28               │
│                                         │
│  📈 Recent Activity:                     │
│  Last 24h: 8 discoveries                │
│  Last 7d: 23 discoveries                │
│  Last 30d: 84 discoveries               │
│                                         │
│  [📊 Detailed Stats]                    │
│                                         │
└────────────────────────────────────────┘
```

### Detailed Stats View

**Click "📊 Detailed Stats" button:**

```
┌────────────────────────────────────────┐
│  📊 Detailed Server Statistics         │
├────────────────────────────────────────┤
│                                         │
│  🔍 Discovery Statistics                │
│  Ancient Bones: 28 (22%)                │
│  Text Logs: 24 (19%)                    │
│  Ruins: 19 (15%)                        │
│  Technology: 15 (12%)                   │
│  Flora/Fauna: 12 (9%)                   │
│  Other: 29 (23%)                        │
│                                         │
│  🌀 Pattern Statistics                   │
│  Tier 1 Patterns: 7                     │
│  Tier 2 Patterns: 4                     │
│  Tier 3 Patterns: 1                     │
│  Tier 4 Patterns: 0                     │
│  Avg Confidence: 84.2%                  │
│                                         │
│  👥 Explorer Statistics                  │
│  Tier 1: 18 explorers                   │
│  Tier 2: 12 explorers                   │
│  Tier 3: 3 explorers                    │
│  Tier 4: 1 explorer                     │
│                                         │
│  🎯 Mystery Tier Distribution:          │
│  [████████████░░░░░░] Tier 1: 53%       │
│  [████████░░░░░░░░░░] Tier 2: 35%       │
│  [███░░░░░░░░░░░░░░░] Tier 3: 9%        │
│  [░░░░░░░░░░░░░░░░░░] Tier 4: 3%        │
│                                         │
└────────────────────────────────────────┘
```

### Usage Tips

- **Run weekly** to track community engagement
- **Monitor pattern detection** rate for bot tuning
- **Check tier distribution** to gauge community progress
- **Use for reports** to show server growth

---

## 12. `/keeper-config`

**Purpose:** Configure The Keeper's behavior and settings

**Who Can Use:** Administrators only

**Required Permissions:** Administrator

**Command Flow:**
```
/keeper-config [parameters]
    ↓
Updates configuration
    ↓
Shows confirmation or current config
```

### Input Format

**Optional Parameters:**

1. **pattern_threshold**: Integer (1-50)
   ```
   Examples:
   /keeper-config pattern_threshold:3      → Default (3 discoveries)
   /keeper-config pattern_threshold:5      → More strict
   /keeper-config pattern_threshold:2      → More sensitive
   ```

2. **auto_pattern**: Boolean (true/false)
   ```
   Examples:
   /keeper-config auto_pattern:true        → Enable (default)
   /keeper-config auto_pattern:false       → Disable
   ```

### Configuration Options Explained

**Pattern Threshold:**
- **Default: 3** - Pattern detected after 3 similar discoveries
- **Lower (1-2)**: More sensitive, catches patterns faster
- **Higher (5-10)**: More strict, only strong patterns
- **Recommended**: Start at 3, adjust based on activity

**Auto Pattern Detection:**
- **Enabled (default)**: Bot automatically analyzes discoveries
- **Disabled**: Manual pattern analysis only with `/pattern-analysis`
- **Use case for disabled**: Very active servers, manual curation preferred

### Example Usage

**Set Pattern Threshold:**
```
/keeper-config pattern_threshold:5
```

**Response:**
```
┌────────────────────────────────────────┐
│  ⚙️ Configuration Updated              │
├────────────────────────────────────────┤
│                                         │
│  The Keeper's parameters have been      │
│  adjusted.                              │
│                                         │
│  Pattern Threshold: 5                   │
│                                         │
│  Patterns will now require 5 similar    │
│  discoveries before detection.          │
│                                         │
└────────────────────────────────────────┘
```

**View Current Configuration:**
```
/keeper-config
```

**Response:**
```
┌────────────────────────────────────────┐
│  ⚙️ Current Configuration              │
├────────────────────────────────────────┤
│                                         │
│  Pattern Detection                      │
│  • Threshold: 3 discoveries             │
│  • Auto-detection: Enabled              │
│  • Confidence minimum: 75%              │
│                                         │
│  Archive Settings                       │
│  • Discovery retention: Unlimited       │
│  • Photo storage: Enabled               │
│  • Export format: JSON                  │
│                                         │
│  Community Features                     │
│  • Tier progression: Enabled            │
│  • Challenges: Enabled                  │
│  • Leaderboards: Public                 │
│                                         │
└────────────────────────────────────────┘
```

**Multiple Parameters:**
```
/keeper-config pattern_threshold:4 auto_pattern:true
```

### Recommended Settings by Server Size

**Small Server (10-50 members):**
```
pattern_threshold: 2-3
auto_pattern: true
```

**Medium Server (50-200 members):**
```
pattern_threshold: 3-5
auto_pattern: true
```

**Large Server (200+ members):**
```
pattern_threshold: 5-7
auto_pattern: true (or false for manual curation)
```

---

## 13. `/pattern-manager`

**Purpose:** Manage detected patterns (admin curation tool)

**Who Can Use:** Administrators only

**Required Permissions:** Administrator

**Command Flow:**
```
/pattern-manager
    ↓
Displays all patterns with management options
    ↓
Buttons for each pattern (details, discoveries, refresh)
```

### Input Format

**No inputs required** - Displays interactive pattern management interface

### Example Output

```
┌────────────────────────────────────────┐
│  🌀 Pattern Management                 │
│  Administrative curation interface      │
├────────────────────────────────────────┤
│                                         │
│  Active Patterns (5)                    │
│                                         │
│  🌀 Predator Seeding Pattern            │
│  • Tier: 2 (Pattern Emergence)          │
│  • Discoveries: 8                       │
│  • Confidence: 87.5%                    │
│  • Status: Active                       │
│  [🔍 Details] [📋 Discoveries]          │
│  [🔄 Refresh] [🗑️ Archive]              │
│                                         │
│  🌀 First Spawn References              │
│  • Tier: 2 (Pattern Emergence)          │
│  • Discoveries: 7                       │
│  • Confidence: 82.1%                    │
│  • Status: Active                       │
│  [🔍 Details] [📋 Discoveries]          │
│  [🔄 Refresh] [🗑️ Archive]              │
│                                         │
│  🌀 Korvax Data Fragments               │
│  • Tier: 1 (Surface Anomaly)            │
│  • Discoveries: 4                       │
│  • Confidence: 71.2%                    │
│  • Status: Pending                      │
│  [🔍 Details] [📋 Discoveries]          │
│  [🔄 Refresh] [🗑️ Archive]              │
│                                         │
│  [➕ Create Pattern Manually]           │
│                                         │
└────────────────────────────────────────┘
```

### Management Actions

**🔍 Details Button:**
```
Shows complete pattern information:
- Full description
- All contributing discoveries
- Timeline (first detected, last updated)
- Confidence breakdown
- Related patterns
```

**📋 Discoveries Button:**
```
Lists all discoveries in this pattern:
Entry #42: Ancient predator fossil...
Entry #38: Similar fossil structure...
Entry #35: Genetic analysis matches...
[etc.]
```

**🔄 Refresh Button:**
```
Re-analyzes the pattern with current data:
- Updates confidence score
- Checks for new related discoveries
- Recalculates mystery tier
- Updates investigation status
```

**🗑️ Archive Button:**
```
Archives the pattern (doesn't delete):
- Marks as "Archived"
- Removes from active investigations
- Preserves for historical reference
- Can be unarchived later
```

**➕ Create Pattern Manually:**
```
Allows manual pattern creation:
- Name the pattern
- Select discovery type focus
- Set initial confidence
- Assign to tier manually
```

### Pattern Management Workflow

**1. Review New Patterns:**
   - Bot auto-detects patterns
   - Admin reviews via `/pattern-manager`
   - Validate confidence + discoveries

**2. Curate Active Patterns:**
   - Check pattern quality
   - Merge similar patterns if needed
   - Archive completed investigations

**3. Manual Pattern Creation:**
   - For complex investigations
   - Cross-reference multiple discovery types
   - Custom lore connections

### Example Detail View

**Click "🔍 Details" on Predator Seeding Pattern:**

```
┌────────────────────────────────────────┐
│  🌀 Predator Seeding Pattern           │
│  Detailed Analysis                      │
├────────────────────────────────────────┤
│                                         │
│  📊 Pattern Statistics                  │
│  Type: Cross-System Similarity          │
│  Discoveries: 8                         │
│  Confidence: 87.5%                      │
│  Status: Active Investigation           │
│                                         │
│  🎯 Mystery Tier                         │
│  Tier 2: Pattern Emergence              │
│  Clear connections found across          │
│  multiple systems in Euclid Core.       │
│                                         │
│  ⏰ Timeline                              │
│  First: 2025-11-01 14:32                │
│  Updated: 2025-11-07 18:45              │
│                                         │
│  📝 Description:                         │
│  Multiple systems show evidence of       │
│  intentional predator species seeding.   │
│  Genetic markers indicate deliberate     │
│  manipulation. Species appear across     │
│  unconnected systems with identical      │
│  DNA signatures.                        │
│                                         │
│  🗺️ Affected Systems:                    │
│  • ORACLE OMEGA (Euclid Core)           │
│  • VESTIGE ZETA (Euclid Core)           │
│  • KEEPER EPSILON (Budullangr Void)     │
│                                         │
│  🔬 Contributing Discoveries:            │
│  #42, #38, #35, #29, #24, #18, #12, #7  │
│                                         │
│  [📋 List Discoveries]                  │
│  [🔄 Refresh Analysis]                  │
│  [🗑️ Archive Pattern]                   │
│                                         │
└────────────────────────────────────────┘
```

---

# APPENDIX

---

## Command Reference Quick Table

| Command | Who Can Use | Required Inputs | Purpose |
|---------|-------------|-----------------|---------|
| `/discovery-report` | Everyone | None (uses menus) | Submit discoveries |
| `/haven-export` | Everyone | None | Export to Haven map |
| `/advanced-search` | Everyone | Optional filters | Search archive |
| `/pattern-analysis` | Everyone | discovery_id | Analyze pattern |
| `/view-patterns` | Everyone | tier (optional) | View patterns |
| `/mystery-tier` | Everyone | None | Check progression |
| `/community-challenge` | Everyone | None | View challenges |
| `/leaderboards` | Everyone | None | View rankings |
| `/keeper-story` | Everyone | None | Story interaction |
| `/setup-channels` | Admins | 4 channel fields | Configure channels |
| `/server-stats` | Admins | None | View statistics |
| `/keeper-config` | Admins | 2 optional params | Adjust settings |
| `/pattern-manager` | Admins | None | Manage patterns |

---

## Discovery Type Reference

| Emoji | Type | Best For |
|-------|------|----------|
| 🦴 | Ancient Bones & Fossils | Creature remains, evolution evidence |
| 📜 | Text Logs & Documents | NMS lore text, terminal entries |
| 🏛️ | Ruins & Structures | Ancient buildings, monuments |
| ⚙️ | Alien Technology | Artifacts, machinery, strange devices |
| 🦗 | Flora & Fauna | Unusual creatures/plants |
| 💎 | Minerals & Resources | Rare materials, geological finds |
| 🚀 | Crashed Ships & Wrecks | Derelict vessels, crash sites |
| ⚡ | Environmental Hazards | Storms, anomalies, dangerous zones |
| 🆕 | NMS Update Content | New features from updates |
| 📖 | Player-Created Lore | Community storytelling |

---

## Common Issues & Solutions

### Issue: "Haven star map integration unavailable"

**Cause:** Bot can't find Haven data file

**Solution:**
1. Check `.env` file has correct `HAVEN_DATA_PATH`
2. Verify file exists: `C:/path/to/Haven_mdev/data/keeper_test_data.json`
3. Restart bot after changing `.env`

### Issue: Channel setup not working

**Cause:** Incorrect channel format or permissions

**Solution:**
1. Use channel mention format: `#channel-name`
2. Or use channel ID (enable Developer Mode)
3. Ensure bot has permission to post in channels
4. Channel must exist before setup

### Issue: Pattern not detecting

**Cause:** Not enough similar discoveries or threshold too high

**Solution:**
1. Check pattern threshold: `/keeper-config`
2. Default is 3 discoveries - submit more similar finds
3. Discoveries must be in same region for regional patterns
4. Use `/pattern-analysis` to manually check

### Issue: Can't see slash commands

**Cause:** Commands not synced or permissions issue

**Solution:**
1. Wait 5-10 minutes after bot joins server
2. Kick and re-invite bot
3. Ensure bot has "Use Slash Commands" permission
4. Check bot is online and connected

---

## Best Practices

### For Quality Discoveries

✅ **DO:**
- Include detailed descriptions (50+ words)
- Add specific coordinates when possible
- Mention condition and time period
- Connect to other discoveries
- Upload photo evidence
- Reference NMS lore text exactly

❌ **DON'T:**
- Submit vague single-word descriptions
- Skip the analysis/theory field
- Ignore pattern connections
- Submit duplicate discoveries
- Use fake or joke submissions

### For Admins

✅ **DO:**
- Set up all 4 channels during initial setup
- Review server-stats weekly
- Curate patterns in pattern-manager
- Adjust threshold based on activity
- Create community challenges
- Celebrate tier progressions

❌ **DON'T:**
- Leave optional channels blank (reduces features)
- Set threshold too low (<2) or too high (>10)
- Archive patterns prematurely
- Ignore auto-detected patterns
- Forget to back up data

---

## Getting Help

**For Users:**
1. Read this guide thoroughly
2. Check the troubleshooting section
3. Ask in `#lore-discussion` channel
4. Ping server admins

**For Admins:**
1. Review admin command documentation
2. Check bot logs in `logs/keeper.log`
3. Test commands in private channel first
4. Consult bot developer/documentation

---

## Changelog

### Version 2.0.0 (Current)
- Added Haven star map integration
- Enhanced discovery system with location selection
- Pattern recognition Phase 4 complete
- Community features (challenges, leaderboards)
- Mystery tier progression system
- 13 total slash commands

### Future Updates
- Advanced pattern visualization
- Cross-server pattern sharing
- Mobile app integration
- Real-time discovery notifications
- Custom discovery templates
- Advanced lore generation

---

**📚 End of Guide**

*The Keeper awaits your discoveries. Begin your journey into the mysteries of Haven.*

🌌 *"Not all who wander are lost - some are simply remembering."* - The Keeper
