# Round Table AI - Multi-Agent System for Haven_mdev

## Overview

The Round Table AI is a modular framework of specialized AI assistants that collaborate to automate Haven_mdev workflows. Each agent has a specific role, and they work together under the coordination of The Conductor.

## Architecture

```
Round Table AI
├── Core Framework
│   ├── AIInterface        - Cloud AI abstraction (Claude/GPT)
│   ├── BaseAgent          - Abstract base class for all agents
│   └── Conductor          - Central orchestrator
│
├── Data Access Layer
│   └── HavenDataAccess    - Unified interface to databases
│
└── Agents
    ├── The Archivist      - Pattern analysis in discoveries
    ├── The Sentinel       - Community health monitoring
    └── The Lorekeeper     - Narrative consistency for Keeper bot
```

## Agents

### The Archivist ⭐⭐⭐⭐
**Role:** Pattern Analysis Co-Pilot

Capabilities:
- Detects patterns in discovery submissions
- Clusters similar discoveries using AI
- Identifies emerging mysteries and correlations
- Provides confidence scores for patterns
- Updates discovery records with analysis results

### The Sentinel ⭐⭐⭐⭐⭐
**Role:** Community Health Monitor

Capabilities:
- Tracks engagement metrics (discoveries per day, active users)
- Detects quiet periods and suggests campaigns
- Monitors for potential spam or abuse
- Analyzes system health and data quality
- Generates daily/weekly health reports

### The Lorekeeper ⭐⭐⭐⭐⭐
**Role:** Narrative Consistency Guardian

Capabilities:
- Reviews Keeper bot responses for in-character accuracy
- Suggests Keeper responses for new discoveries
- Checks story continuity across discoveries
- Flags contradictions in the narrative
- Maintains Keeper's mysterious, ancient voice

## Setup

### 1. Install Dependencies

```bash
pip install -r src/roundtable_ai/requirements.txt
```

### 2. Set API Keys

Create a `.env` file in `Haven-UI/` directory:

```env
# For Claude AI (primary)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# For OpenAI GPT (fallback)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Set primary/fallback models
RTAI_PRIMARY_MODEL=claude
RTAI_FALLBACK_MODEL=gpt
```

### 3. Start Haven-UI Server

The Round Table AI automatically initializes when the Haven-UI server starts:

```bash
cd Haven-UI
python -m uvicorn src.control_room_api:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### System Status
```
GET /api/rtai/status
```
Returns status, statistics, and list of registered agents.

### Discovery Analysis
```
POST /api/rtai/analyze/discoveries?limit=10
```
Triggers The Archivist to analyze recent discoveries for patterns.
Runs in background and logs to `ai_chat.log`.

### Community Health Report
```
GET /api/rtai/health-report?days=7
```
Gets The Sentinel's health report for the last N days.

### Pattern Analysis Report
```
GET /api/rtai/pattern-report?days=7
```
Gets The Archivist's pattern analysis report.

### Keeper Bot - Review Response
```
POST /api/rtai/keeper/review
Body: {
  "keeper_response": "The response text to review",
  "discovery": {...discovery object...}
}
```
Has The Lorekeeper review a Keeper bot response for accuracy.

### Keeper Bot - Suggest Response
```
POST /api/rtai/keeper/suggest
Body: {...discovery object...}
```
Has The Lorekeeper suggest an in-character Keeper response.

## Monitoring

### Real-Time Chat Monitor

The Round Table AI logs all activity to `Haven-UI/logs/ai_chat.log`.

View in real-time via:
- WebSocket: `ws://localhost:8000/ws/rtai`
- REST API: `GET /api/rtai/history`
- UI Component: Navigate to `/rtai` in Haven-UI

## Usage Examples

### Analyze Discoveries from Python

```python
from pathlib import Path
from src.roundtable_ai.api_integration import get_round_table_ai

# Initialize
haven_ui_root = Path("Haven-UI")
rtai = get_round_table_ai(haven_ui_root)

# Analyze recent discoveries
result = await rtai.analyze_discoveries(limit=20)
print(f"Found {len(result['patterns'])} patterns")

# Get health report
health = await rtai.get_community_health_report(days=7)
print(f"Engagement status: {health['engagement']['status']}")

# Generate pattern report
patterns = await rtai.generate_pattern_report(days=7)
print(f"Patterns: {patterns['patterns']}")
```

### Trigger Analysis via API

```bash
# Analyze discoveries
curl -X POST http://localhost:8000/api/rtai/analyze/discoveries?limit=10

# Get health report
curl http://localhost:8000/api/rtai/health-report?days=7

# Check AI status
curl http://localhost:8000/api/rtai/status
```

## Data Flow

```
User Discovery (Discord/Web)
        ↓
   Haven-UI Database
        ↓
   Conductor orchestrates
        ↓
   ┌────────────┬────────────┬────────────┐
   ↓            ↓            ↓            ↓
Archivist   Sentinel   Lorekeeper   (Future Agents)
   ↓            ↓            ↓            ↓
   └────────────┴────────────┴────────────┘
                ↓
         AI Chat Log
                ↓
         WebSocket UI
```

## Adding New Agents

To add a new agent (e.g., "The Scribe"):

1. Create `src/roundtable_ai/agents/scribe.py`:

```python
from ..core.base_agent import BaseAgent

class ScribeAgent(BaseAgent):
    def __init__(self, data_access, ai_interface):
        super().__init__(
            name="The Scribe",
            role="Automated Story Beat Generator",
            data_access=data_access,
            ai_interface=ai_interface
        )

    async def analyze(self, context):
        # Your agent logic here
        return {"status": "success"}
```

2. Register in `src/roundtable_ai/api_integration.py`:

```python
from .agents import ScribeAgent

# In _register_agents method:
scribe = ScribeAgent(self.data_access, self.ai_interface)
self.conductor.register_agent(scribe)
```

## Configuration

### Agent Behavior

Each agent's behavior can be customized by modifying its prompts and logic in its respective file under `src/roundtable_ai/agents/`.

### AI Model Selection

Set in `.env`:
- `RTAI_PRIMARY_MODEL=claude` - Use Claude by default
- `RTAI_FALLBACK_MODEL=gpt` - Fall back to GPT if Claude fails

### Rate Limiting

Configured in `AIInterface` class (`src/roundtable_ai/core/ai_interface.py`):
- Default: 1 second between requests
- Modify `min_request_interval` to adjust

## Troubleshooting

### AI API Errors

**Problem:** "Anthropic client not initialized"
**Solution:** Set `ANTHROPIC_API_KEY` in `.env` file

**Problem:** "All AI providers failed"
**Solution:** Check API keys and internet connection

### Database Errors

**Problem:** "Haven UI database not found"
**Solution:** Ensure `Haven-UI/data/haven_ui.db` exists

### Import Errors

**Problem:** "No module named 'anthropic'"
**Solution:** `pip install anthropic openai`

## Logs

- **AI Activity:** `Haven-UI/logs/ai_chat.log`
- **System Logs:** `Haven-UI/logs/control-room-web.log`
- **API Errors:** Check FastAPI console output

## Future Agents

Planned agents from the documentation:
- **The Cartographer** - Smart map enhancement
- **The Scribe** - Automated story beat generator
- **The Oracle** - Predictive story planning
- **The Curator** - Asset management
- **The Investigator** - Deep discovery analysis
- **The Chronicler** - Documentation generator

## License

Part of the Haven_mdev project.
