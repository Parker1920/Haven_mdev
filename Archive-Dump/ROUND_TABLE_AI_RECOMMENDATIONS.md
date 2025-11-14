# 🎯 Round Table AI Assistant Recommendations

**For: Haven_mdev + Keeper Bot Admin Team**  
**Date: November 8, 2025**  
**Purpose: AI assistants designed to enhance admin workflows and system management**

---

## Overview

Based on the Haven Control Room (star mapping) + The Keeper Discord Bot (discovery/lore) ecosystem, these 10 AI concepts are tailored for Round Table admin use. Each assistant addresses specific admin pain points while integrating seamlessly with existing architecture.

---

## 1. The Archivist AI - Pattern Analysis Co-Pilot

### Purpose
Real-time pattern detection assistant that helps admins identify emerging mysteries

### Features
- Monitors `keeper.db` for new discovery submissions
- Uses NLP to cluster similar discoveries by theme/location
- Suggests pattern names and confidence levels
- Auto-generates investigation thread titles
- Recommends mystery tier assignments (1-4)
- Visualizes discovery heatmaps across Haven regions

### Integration Points
- **Reads**: `keeper.db` (discoveries table), `data.json` (Haven systems)
- **Writes**: Pattern suggestions to admin dashboard
- **API**: Discord webhook for real-time alerts

### Tech Stack
Python + spaCy/transformers + SQLite + FastAPI

### Why It Works
Reduces manual pattern detection work, surfaces hidden connections admins might miss

### Implementation Priority
⭐⭐⭐⭐ (High - Core functionality)

---

## 2. The Lorekeeper - Narrative Consistency Guardian

### Purpose
Ensures Keeper responses stay in-character and maintain story continuity

### Features
- Trained on The_Keepers_Story.md and all Keeper dialogue
- Reviews bot responses before posting for tone/lore accuracy
- Suggests alternative phrasings that fit character voice
- Tracks story progression state (which mysteries revealed, current act)
- Flags contradictions with established lore
- Generates Keeper-voice responses from admin prompts

### Integration Points
- **Reads**: The_Keepers_Story.md, keeper_dialogue_compilation.md
- **Writes**: Response suggestions to admin panel
- **API**: Discord bot middleware for response review

### Tech Stack
Python + LangChain + GPT-4 fine-tuning + vector DB

### Why It Works
Maintains narrative quality as Round Table scales, prevents lore inconsistencies

### Implementation Priority
⭐⭐⭐⭐⭐ (Critical - Story quality)

---

## 3. The Cartographer AI - Smart Map Enhancement

### Purpose
Suggests map improvements and detects data quality issues

### Features
- Analyzes `data.json` for incomplete system entries
- Detects coordinate outliers or impossible distances
- Suggests missing planet/moon data based on NMS biome rules
- Auto-generates planet descriptions from photos (if uploaded)
- Recommends regional groupings for better map organization
- Creates "exploration priority" lists based on discovery gaps

### Integration Points
- **Reads**: `data.json`, `haven.db`, photo metadata
- **Writes**: Suggestions to Control Room UI or admin dashboard
- **Direct**: Can run as Control Room plugin

### Tech Stack
Python + Pandas + scikit-learn + CV models

### Why It Works
Keeps Haven map data high-quality, surfaces maintenance needs

### Implementation Priority
⭐⭐⭐⭐ (High - Data quality)

---

## 4. The Scribe - Automated Story Beat Generator

### Purpose
Drafts story updates and Keeper transmissions based on community progress

### Features
- Monitors discovery milestones (100th submission, pattern thresholds)
- Auto-generates celebration posts and story advancement text
- Creates "Act progression" summaries based on template system
- Drafts investigation thread opening posts
- Suggests seasonal event narratives aligned with roadmap
- Generates weekly "State of the Archive" reports

### Integration Points
- **Reads**: `keeper.db` (stats), The_Keepers_Story.md (story state)
- **Writes**: Draft posts to admin review queue
- **Discord**: Posts approved content via bot

### Tech Stack
Python + Jinja2 templates + GPT-4 + scheduling

### Why It Works
Automates routine storytelling, lets Round Table focus on major narrative decisions

### Implementation Priority
⭐⭐⭐⭐ (High - Reduces admin workload)

---

## 5. The Sentinel - Community Health Monitor

### Purpose
Tracks community engagement and flags issues

### Features
- Analyzes Discord activity (discovery submission frequency, participation)
- Detects "quiet periods" and suggests engagement campaigns
- Identifies power users for recognition/rewards
- Flags potential bot abuse or spam patterns
- Measures investigation thread health (replies, theories)
- Predicts when story events will hit milestones

### Integration Points
- **Reads**: Discord API (messages, reactions), `keeper.db` (user_stats)
- **Writes**: Health reports to admin dashboard
- **Alerts**: Slack/Discord DMs for critical issues

### Tech Stack
Python + Discord.py + time-series analysis + Grafana

### Why It Works
Proactive community management, prevents engagement drops

### Implementation Priority
⭐⭐⭐⭐⭐ (Critical - Community health)

---

## 6. The Oracle - Predictive Story Planner

### Purpose
Simulates story progression based on current discovery rates

### Features
- Projects when convergence thresholds will be hit
- Suggests optimal mystery reveal timing
- Simulates different story branch outcomes
- Estimates seasonal content duration
- Recommends challenge difficulty adjustments
- Models "what-if" scenarios for major plot choices

### Integration Points
- **Reads**: `keeper.db` (historical submission rates), The_Keepers_Story.md
- **Writes**: Projections to admin planning dashboard
- **Exports**: Timeline visualizations

### Tech Stack
Python + Plotly + time-series forecasting + Monte Carlo

### Why It Works
Data-driven narrative pacing, prevents story droughts or rushes

### Implementation Priority
⭐⭐⭐ (Medium - Strategic planning)

---

## 7. The Curator - Asset Management Assistant

### Purpose
Organizes photos, manages backups, handles data exports

### Features
- Auto-tags discovery photos with metadata (system, planet, type)
- Generates photo galleries for Discord/web display
- Manages `data.json` and `keeper.db` backup rotation
- Creates "best discoveries" compilations
- Exports data for web archive or marketing
- Detects duplicate photos or corrupted files
- Compresses/optimizes images for performance

### Integration Points
- **Reads**: `photos/`, `data.json`, `keeper.db`
- **Writes**: Organized galleries, backup archives
- **Storage**: Cloud sync (optional)

### Tech Stack
Python + Pillow + ImageHash + AWS S3 (optional)

### Why It Works
Prevents data loss, keeps media library organized at scale

### Implementation Priority
⭐⭐⭐ (Medium - Asset management)

---

## 8. The Chronicler - Documentation Generator

### Purpose
Auto-generates and updates documentation based on code/data changes

### Features
- Monitors `src/` for code changes, updates technical docs
- Generates user guides from Control Room UI state
- Creates "New Features" announcements from git commits
- Builds API reference docs for Haven integration
- Maintains changelog automatically
- Generates quick-start guides for new community members
- Creates video script outlines from feature descriptions

### Integration Points
- **Reads**: Git history, Python docstrings, `README.md`
- **Writes**: Updated docs to `docs/` directory
- **GitHub**: Auto-PR for doc updates

### Tech Stack
Python + Sphinx + GitPython + markdown generation

### Why It Works
Keeps docs current without manual work, reduces onboarding friction

### Implementation Priority
⭐⭐ (Low - Nice to have)

---

## 9. The Investigator - Deep Discovery Analysis

### Purpose
Performs semantic analysis on discovery descriptions for hidden patterns

### Features
- NLP analysis on discovery text (sentiment, themes, entities)
- Detects references to lore elements (First Spawn, Atlas, etc.)
- Cross-references discoveries with Haven system locations
- Identifies "theory clusters" from community discussions
- Suggests related discoveries for investigation threads
- Generates "discovery summaries" for long investigations
- Finds correlations humans might miss (time, coords, keywords)

### Integration Points
- **Reads**: `keeper.db` (discoveries, investigation threads)
- **Writes**: Analysis reports to admin dashboard
- **Discord**: Can post insights to investigation threads

### Tech Stack
Python + spaCy + BERT embeddings + graph analysis

### Why It Works
Surfaces deep patterns, enhances mystery depth and realism

### Implementation Priority
⭐⭐⭐⭐ (High - Pattern enhancement)

---

## 10. The Conductor - Workflow Orchestrator

### Purpose
Central command AI that coordinates Round Table admin tasks

### Features
- Natural language task management ("Schedule Act 2 reveal for next Friday")
- Delegates tasks to other AI assistants (Scribe, Oracle, etc.)
- Tracks story roadmap progress vs. actual milestones
- Generates Round Table meeting agendas based on pending decisions
- Sends reminders for seasonal content deadlines
- Provides daily briefings on Haven/Keeper status
- Voice interface option for hands-free admin work

### Integration Points
- **Reads**: All system data sources
- **Writes**: Task assignments, calendar events, briefing reports
- **APIs**: Discord, Notion/Trello (task management), Google Calendar

### Tech Stack
Python + LangChain + function calling + voice recognition

### Why It Works
Single interface to manage entire ecosystem, reduces context-switching

### Implementation Priority
⭐⭐⭐⭐⭐ (Critical - Unified admin experience)

---

## Implementation Roadmap

### Phase 1: Foundation (Months 1-2)
**Start with immediate value, low complexity**

1. **The Sentinel** - Community health monitoring
   - Easiest to implement
   - Immediate visibility into engagement
   - Uses existing Discord API

2. **The Cartographer** - Data quality checks
   - Improves Haven map data fast
   - Can run as standalone script
   - Low integration complexity

3. **The Scribe** - Content generation
   - Reduces routine posting work
   - Template-based (simpler than full AI)
   - High admin time savings

**Expected Outcomes:**
- Automated community monitoring
- Cleaner data in Haven systems
- 50% reduction in routine posting work

---

### Phase 2: Core Intelligence (Months 3-5)
**Add pattern detection and narrative consistency**

4. **The Archivist** - Pattern analysis
   - Automates mystery detection
   - Core to Keeper functionality
   - Requires NLP training

5. **The Lorekeeper** - Story consistency
   - Maintains narrative quality
   - Prevents lore contradictions
   - Requires fine-tuning on lore corpus

6. **The Curator** - Asset management
   - Prevents data loss at scale
   - Organizes photo library
   - Essential before community growth

**Expected Outcomes:**
- Automated pattern detection
- Consistent Keeper voice
- Organized asset library

---

### Phase 3: Advanced Systems (Months 6-8)
**Strategic planning and deep analysis**

7. **The Oracle** - Predictive planning
   - Data-driven pacing decisions
   - Forecasts milestone timing
   - Requires historical data

8. **The Investigator** - Deep analysis
   - Surfaces hidden connections
   - Semantic discovery analysis
   - Enhances mystery depth

9. **The Chronicler** - Documentation
   - Auto-updates all docs
   - Reduces maintenance burden
   - Nice-to-have automation

**Expected Outcomes:**
- Strategic narrative planning
- Deeper pattern insights
- Self-maintaining documentation

---

### Phase 4: Unification (Month 9+)
**Bring it all together**

10. **The Conductor** - Orchestrator
    - Central admin interface
    - Coordinates all other AIs
    - Natural language task management
    - Voice interface option

**Expected Outcomes:**
- Single admin command center
- Reduced context-switching
- Unified Round Table workflow

---

## System Architecture

### Proposed Structure

```
┌─────────────────────────────────────────────────────┐
│         Round Table Admin Interface                  │
│    (Web Dashboard / Discord Bot / Voice Assistant)   │
└─────────────────────┬───────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│              The Conductor (Orchestrator)            │
│  - Task routing                                      │
│  - Natural language processing                       │
│  - Delegation to specialized AIs                     │
└─────────────────────┬───────────────────────────────┘
                      ↓
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
┌───────────────┐ ┌──────────┐ ┌──────────┐
│  Archivist    │ │ Scribe   │ │ Sentinel │
│  - Patterns   │ │ - Posts  │ │ - Health │
└───────────────┘ └──────────┘ └──────────┘

┌───────────────┐ ┌──────────┐ ┌──────────┐
│  Lorekeeper   │ │ Oracle   │ │Cartograph│
│  - Narrative  │ │ - Predict│ │ - Maps   │
└───────────────┘ └──────────┘ └──────────┘

┌───────────────┐ ┌──────────┐ ┌──────────┐
│  Investigator │ │ Curator  │ │Chronicler│
│  - Analysis   │ │ - Assets │ │ - Docs   │
└───────────────┘ └──────────┘ └──────────┘
        ↓             ↓             ↓
┌─────────────────────────────────────────────────────┐
│              Shared Data Layer                       │
│  ┌─────────────┬──────────────┬─────────────┐      │
│  │ data.json   │  keeper.db   │  photos/    │      │
│  │ haven.db    │  logs/       │  backups/   │      │
│  └─────────────┴──────────────┴─────────────┘      │
└─────────────────────────────────────────────────────┘
```

### Data Flow

```
User Discovery (Discord)
        ↓
Keeper Bot receives → Stores in keeper.db
        ↓
Sentinel monitors engagement
        ↓
Archivist analyzes for patterns
        ↓
Lorekeeper reviews Keeper response
        ↓
Scribe drafts milestone post
        ↓
Oracle updates timeline projections
        ↓
Investigator performs deep analysis
        ↓
Conductor presents summary to Round Table
```

---

## Technical Considerations

### Hosting Options

**Option 1: Single Server**
- All AIs run on one machine
- Shared database connections
- Simplest deployment
- Cost: ~$20-50/month (VPS)

**Option 2: Microservices**
- Each AI as separate service
- API communication between them
- Scalable but complex
- Cost: ~$50-100/month (cloud)

**Option 3: Hybrid**
- Critical AIs (Sentinel, Conductor) always-on
- Others run on-demand or scheduled
- Balance of cost and performance
- Cost: ~$30-60/month

**Recommendation**: Start with Option 1, migrate to Option 3 as needed

---

### Data Privacy & Security

**Considerations:**
- Discord user data (GDPR/privacy laws)
- Discovery content (user-submitted)
- Admin authentication
- API key management

**Best Practices:**
- Encrypt sensitive data at rest
- Use environment variables for secrets
- Implement role-based access control
- Regular security audits
- Data retention policies

---

### API Rate Limits

**Discord API:**
- 50 requests/second per token
- 10,000 requests/10 minutes global
- Solution: Request queuing + caching

**OpenAI/GPT:**
- Tier-based limits (varies by plan)
- Solution: Local models for non-critical tasks

**Haven Data:**
- No external API (local files)
- Bottleneck: File I/O
- Solution: In-memory caching

---

## Cost Estimates

### Development Phase
| Item | Cost |
|------|------|
| Developer time (you/team) | Variable |
| OpenAI API (training/testing) | $50-200/month |
| Cloud hosting (dev environment) | $20-40/month |
| Testing infrastructure | $10-20/month |
| **Total (per month)** | **$80-260** |

### Production Phase
| Item | Cost |
|------|------|
| VPS/Cloud hosting | $30-60/month |
| OpenAI API (production) | $100-300/month |
| Database storage | $10-20/month |
| CDN (if web dashboard) | $10-30/month |
| Backup storage | $5-10/month |
| **Total (per month)** | **$155-420** |

**Note**: Can reduce costs significantly using local models (LLaMA, Mistral) instead of OpenAI

---

## Alternative: Local-First Approach

### Why Consider It?
- No recurring API costs
- Full data privacy control
- Works offline
- No rate limits

### Recommended Local Models
| Model | Use Case | Size | Performance |
|-------|----------|------|-------------|
| Mistral 7B | General text generation | 4GB | Excellent |
| LLaMA 3 8B | Lore consistency | 5GB | Excellent |
| CodeLLaMA 7B | Code analysis | 4GB | Good |
| BERT-base | Pattern detection | 500MB | Fast |

### Hardware Requirements
- **CPU**: 8+ cores recommended
- **RAM**: 16GB minimum, 32GB ideal
- **GPU**: Optional but 2-3x faster (RTX 3060+)
- **Storage**: 50GB for models + data

### Trade-offs
| Aspect | Cloud AI | Local AI |
|--------|----------|----------|
| Cost | High recurring | High upfront (hardware) |
| Speed | Fast (GPT-4) | Medium (local models) |
| Privacy | Data leaves server | Fully private |
| Maintenance | Low | Medium |
| Customization | Limited | Full control |

**Recommendation**: Hybrid approach
- Use local models for high-volume tasks (Sentinel, Cartographer)
- Use cloud AI for quality-critical tasks (Lorekeeper, Scribe)

---

## Quick Start Guide

### For Phase 1 Implementation

#### 1. The Sentinel (Community Monitor)

**Step 1**: Install dependencies
```bash
pip install discord.py pandas matplotlib
```

**Step 2**: Create basic structure
```python
# sentinel.py
import discord
from discord.ext import tasks
import aiosqlite

class Sentinel:
    def __init__(self, keeper_db_path, discord_token):
        self.db_path = keeper_db_path
        self.token = discord_token
        
    @tasks.loop(hours=1)
    async def check_health(self):
        # Query keeper.db for stats
        # Analyze trends
        # Send alerts if needed
        pass
```

**Step 3**: Connect to existing systems
- Read from: `keeper.db` (user_stats, discoveries tables)
- Write to: Admin Discord channel
- Schedule: Hourly health checks

**Time to MVP**: 2-3 days

---

#### 2. The Cartographer (Data Quality)

**Step 1**: Install dependencies
```bash
pip install pandas numpy scipy
```

**Step 2**: Create analysis script
```python
# cartographer.py
import json
import pandas as pd

class Cartographer:
    def __init__(self, data_json_path):
        self.data_path = data_json_path
        
    def analyze_quality(self):
        # Load data.json
        # Check for missing fields
        # Detect coordinate outliers
        # Generate report
        pass
```

**Step 3**: Integration
- Run as: Standalone script or Control Room plugin
- Output: JSON report + Discord notification
- Schedule: Daily automated scan

**Time to MVP**: 1-2 days

---

#### 3. The Scribe (Content Generator)

**Step 1**: Install dependencies
```bash
pip install jinja2 openai  # or use local model
```

**Step 2**: Create template system
```python
# scribe.py
from jinja2 import Template

MILESTONE_TEMPLATE = """
🌌 Archive Milestone Reached!

The Keeper has processed {{ count }} discoveries.
Pattern confidence increases across {{ regions }} regions.

{{ keeper_voice_comment }}

[Auto-generated by The Scribe]
"""

class Scribe:
    def draft_milestone_post(self, count, regions):
        # Use template + GPT for keeper voice
        pass
```

**Step 3**: Integration
- Triggered by: Discovery count thresholds
- Outputs to: Admin review queue
- Approval: Manual or auto-post after review

**Time to MVP**: 3-4 days

---

## Success Metrics

### How to Measure AI Impact

**The Sentinel:**
- Metric: Admin response time to issues
- Target: Reduce from 24h → 4h average

**The Cartographer:**
- Metric: % of systems with complete data
- Target: Increase from 70% → 95%

**The Scribe:**
- Metric: Admin hours spent on routine posts
- Target: Reduce from 5h/week → 1h/week

**The Archivist:**
- Metric: Patterns detected (auto vs manual)
- Target: 80% auto-detected

**The Lorekeeper:**
- Metric: Lore consistency score (community feedback)
- Target: Maintain >90% positive sentiment

---

## FAQ

### Q: Do all 10 need to be built?
**A**: No. Start with Phase 1 (Sentinel, Cartographer, Scribe). Others can be added based on need.

### Q: Can I use existing AI APIs instead of building from scratch?
**A**: Yes! Many can leverage OpenAI, Claude, or local models via LangChain. Custom logic is mainly routing and integration.

### Q: How do these interact with Haven Control Room?
**A**: They read `data.json` and `haven.db`, can write suggestions to logs or admin dashboard. Control Room can optionally display AI insights.

### Q: What about Keeper Bot integration?
**A**: Direct integration via Discord bot commands or middleware. AIs can monitor `keeper.db` and enhance bot responses.

### Q: Can community members access any of this?
**A**: No, these are admin-only tools. But outputs (like Scribe posts) are visible to community.

### Q: What if I don't know Python/AI?
**A**: Recommended: Partner with developer, or start with no-code tools (Zapier + GPT) for basic versions.

---

## Next Steps

### To Begin Implementation:

1. **Choose Phase 1 Focus**: Pick 1-2 AIs from Phase 1
2. **Set Up Dev Environment**: Python 3.10+, virtual environment
3. **Create Project Structure**: `round_table_ai/` directory
4. **Start with Prototypes**: MVP versions (2-4 days each)
5. **Test with Real Data**: Use `keeper_test_data.json` for testing
6. **Deploy & Monitor**: Start with manual runs, automate later
7. **Iterate Based on Usage**: Add features as needs emerge

### Want Implementation Help?

I can create the initial codebase for any of these AIs. Just let me know which one(s) you want to start with, and I'll:

- Set up the project structure
- Write the core logic
- Create integration points with Haven/Keeper
- Provide deployment instructions
- Include example configurations

---

**Ready to enhance the Round Table admin experience with AI!** 🚀

Choose your starting point and we'll build it together.
