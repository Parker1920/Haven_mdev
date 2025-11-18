# Round Table AI - Complete Setup Guide

## Overview

The Round Table AI system has been successfully built and integrated into Haven_mdev! This guide will help you get it up and running.

## What Was Built

### ✅ Core Framework
- **AIInterface**: Abstraction layer for Claude and GPT with automatic fallback
- **BaseAgent**: Abstract base class for all AI agents
- **Conductor**: Central orchestrator coordinating all agents
- **HavenDataAccess**: Unified interface to all Haven databases

### ✅ Three AI Agents

1. **The Archivist** ⭐⭐⭐⭐
   - Pattern detection in discoveries
   - Clusters similar discoveries using NLP
   - Suggests pattern names and confidence levels
   - Cross-references discoveries with locations

2. **The Sentinel** ⭐⭐⭐⭐⭐
   - Community health monitoring
   - Engagement analytics
   - Detects quiet periods
   - Security/spam detection

3. **The Lorekeeper** ⭐⭐⭐⭐⭐
   - Keeper bot response review
   - Narrative consistency checks
   - Story continuity validation
   - Generates suggested Keeper responses

### ✅ API Integration
- 6 new REST endpoints in Haven-UI
- Real-time WebSocket chat monitor
- Background task processing
- Comprehensive logging

## Quick Start

### 1. Install Dependencies

```bash
pip install anthropic openai
```

Or use the requirements file:

```bash
pip install -r src/roundtable_ai/requirements.txt
```

### 2. Set Up API Keys

Create or edit `Haven-UI/.env`:

```env
# Claude AI (Recommended - you're already using this in VS Code)
ANTHROPIC_API_KEY=your_anthropic_api_key

# OpenAI GPT (Optional fallback)
OPENAI_API_KEY=your_openai_api_key

# Optional: Configure which model to use
RTAI_PRIMARY_MODEL=claude
RTAI_FALLBACK_MODEL=gpt
```

**Note:** Since you're using Claude in VS Code right now, you can use the same Anthropic API key.

### 3. Test the System

```bash
python test_roundtable_ai.py
```

You should see:
```
✓ Round Table AI initialized successfully
✓ Total agents: 3
✓ Registered agents:
  - The Archivist
  - The Sentinel
  - The Lorekeeper
```

### 4. Start Haven-UI Server

```bash
cd Haven-UI
python -m uvicorn src.control_room_api:app --host 0.0.0.0 --port 8000 --reload
```

## Testing the API

### Check System Status

```bash
curl http://localhost:8000/api/rtai/status
```

Response:
```json
{
  "status": "operational",
  "statistics": {
    "total_agents": 3,
    "total_tasks": 0,
    "pending_tasks": 0,
    "completed_tasks": 0,
    "agents": [...]
  }
}
```

### Analyze Discoveries

```bash
curl -X POST "http://localhost:8000/api/rtai/analyze/discoveries?limit=10"
```

This triggers The Archivist to analyze recent discoveries for patterns!

### Get Community Health Report

```bash
curl "http://localhost:8000/api/rtai/health-report?days=7"
```

The Sentinel provides engagement metrics and recommendations.

### Get Pattern Analysis Report

```bash
curl "http://localhost:8000/api/rtai/pattern-report?days=7"
```

The Archivist generates a comprehensive pattern report.

### Review Keeper Bot Response

```bash
curl -X POST http://localhost:8000/api/rtai/keeper/review \
  -H "Content-Type: application/json" \
  -d '{
    "keeper_response": "Interesting... this artifact bears markings similar to others found in the region.",
    "discovery": {
      "discovery_type": "artifact",
      "description": "Ancient artifact with strange symbols"
    }
  }'
```

The Lorekeeper reviews the response for lore accuracy!

### Suggest Keeper Response

```bash
curl -X POST http://localhost:8000/api/rtai/keeper/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "discovery_type": "artifact",
    "description": "Ancient monolith with glowing symbols",
    "location_name": "Serenity-3"
  }'
```

The Lorekeeper suggests an in-character response.

## Monitoring AI Activity

### Real-Time Chat Monitor

Navigate to: **http://localhost:8000/rtai** (in your browser)

Or connect via WebSocket:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/rtai');
ws.onmessage = (event) => {
  console.log('AI Activity:', event.data);
};
```

### View Chat Logs

```bash
curl http://localhost:8000/api/rtai/history
```

Or check the log file:
```bash
tail -f Haven-UI/logs/ai_chat.log
```

## File Structure

```
Haven_mdev/
├── src/roundtable_ai/
│   ├── __init__.py
│   ├── README.md              # Detailed documentation
│   ├── requirements.txt       # Python dependencies
│   ├── api_integration.py     # FastAPI integration
│   │
│   ├── core/                  # Core framework
│   │   ├── __init__.py
│   │   ├── ai_interface.py    # Claude/GPT interface
│   │   ├── base_agent.py      # Base agent class
│   │   └── conductor.py       # Orchestrator
│   │
│   ├── data_access/           # Data layer
│   │   ├── __init__.py
│   │   └── haven_data.py      # Database access
│   │
│   └── agents/                # AI agents
│       ├── __init__.py
│       ├── archivist.py       # Pattern analysis
│       ├── sentinel.py        # Community monitoring
│       └── lorekeeper.py      # Narrative consistency
│
├── src/control_room_api.py    # ← Updated with RTAI endpoints
├── test_roundtable_ai.py      # Test script
└── ROUNDTABLE_AI_SETUP.md     # This file
```

## Usage Examples

### From Python

```python
import asyncio
from pathlib import Path
from src.roundtable_ai.api_integration import get_round_table_ai

async def main():
    # Initialize
    rtai = get_round_table_ai(Path("Haven-UI"))

    # Analyze discoveries
    result = await rtai.analyze_discoveries(limit=20)
    print(f"Patterns found: {len(result['patterns'])}")

    # Get health report
    health = await rtai.get_community_health_report(days=7)
    print(f"Engagement: {health['engagement']['status']}")

    # Review Keeper response
    review = await rtai.review_keeper_response(
        keeper_response="Intriguing discovery, traveler...",
        discovery={"discovery_type": "artifact", "description": "..."}
    )
    print(f"Score: {review.get('overall_score', 0)}/100")

asyncio.run(main())
```

### From Haven-UI Frontend (React)

```javascript
// Trigger discovery analysis
async function analyzeDiscoveries() {
  const response = await fetch('/api/rtai/analyze/discoveries?limit=10', {
    method: 'POST'
  });
  const result = await response.json();
  console.log(result.message);
}

// Get health report
async function getHealthReport() {
  const response = await fetch('/api/rtai/health-report?days=7');
  const report = await response.json();
  console.log('Engagement:', report.engagement);
}
```

## API Endpoints Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/rtai/status` | GET | System status and statistics |
| `/api/rtai/analyze/discoveries` | POST | Trigger discovery analysis |
| `/api/rtai/health-report` | GET | Community health report |
| `/api/rtai/pattern-report` | GET | Pattern analysis report |
| `/api/rtai/keeper/review` | POST | Review Keeper response |
| `/api/rtai/keeper/suggest` | POST | Suggest Keeper response |
| `/api/rtai/history` | GET | Chat log history |
| `/api/rtai/clear` | POST | Clear chat log |
| `/ws/rtai` | WebSocket | Real-time chat stream |

## How It Works

### Discovery Analysis Workflow

```
1. POST /api/rtai/analyze/discoveries?limit=10
           ↓
2. Conductor delegates to The Archivist
           ↓
3. Archivist fetches unanalyzed discoveries from haven_ui.db
           ↓
4. Statistical pattern detection (type frequency, location clustering, keywords)
           ↓
5. AI-powered deep pattern analysis (thematic, narrative, temporal patterns)
           ↓
6. Update discovery records with analysis results
           ↓
7. Log activity to ai_chat.log
           ↓
8. Return results with patterns, insights, recommendations
```

### Real-Time Monitoring

```
All AI actions → HavenDataAccess.log_ai_activity()
                        ↓
                Haven-UI/logs/ai_chat.log
                        ↓
                WebSocket /ws/rtai
                        ↓
                React UI Component (RTAI.jsx)
```

## Customization

### Adding Custom Prompts

Edit agent files in `src/roundtable_ai/agents/`:

```python
# Example: Custom Archivist prompt
async def _detect_ai_patterns(self, discoveries):
    prompt = f"""
    YOUR CUSTOM PROMPT HERE

    Analyze these discoveries: {discoveries}
    """
    return self.ask_ai_json(prompt=prompt)
```

### Adjusting Analysis Thresholds

In `archivist.py`:

```python
# Change pattern detection sensitivity
if count >= 3:  # Change this threshold
    patterns.append(...)
```

### Rate Limiting

In `ai_interface.py`:

```python
self.min_request_interval = 1.0  # Seconds between AI requests
```

## Troubleshooting

### "No AI API keys configured"

**Solution:** Create `Haven-UI/.env` with:
```env
ANTHROPIC_API_KEY=sk-ant-...
```

### "Haven UI database not found"

**Solution:** Ensure `Haven-UI/data/haven_ui.db` exists. The database should be created when you use Haven-UI normally.

### "Failed to initialize Round Table AI"

**Solution:** Check logs at `Haven-UI/logs/control-room-web.log` for specific error.

### AI requests failing

**Solution:**
1. Check API key is valid
2. Check internet connection
3. Verify you haven't hit rate limits
4. Check API provider status (status.anthropic.com)

## Cost Estimation

Using Claude (Anthropic):
- Pattern analysis of 20 discoveries: ~$0.01-0.03
- Health report: ~$0.005-0.01
- Keeper response review: ~$0.002-0.005

**Estimated monthly cost:**
- Light usage (1-2 analyses/day): $1-5
- Moderate usage (5-10 analyses/day): $10-20
- Heavy usage (20+ analyses/day): $30-50

**Tip:** Start with small limits (`?limit=5`) to minimize costs during testing.

## Next Steps

### Immediate
1. ✅ Set up API keys
2. ✅ Run `test_roundtable_ai.py`
3. ✅ Start Haven-UI server
4. ✅ Test API endpoints

### Short-term
- Integrate discovery analysis into Haven-UI frontend
- Add button to trigger analysis from Discoveries page
- Display pattern reports in admin dashboard
- Implement Keeper bot integration for auto-review

### Long-term (Future Agents)
- **The Cartographer**: Map quality analysis
- **The Scribe**: Automated story beat generation
- **The Oracle**: Predictive planning
- **The Curator**: Asset management
- **The Investigator**: Deep NLP analysis
- **The Chronicler**: Auto documentation

## Support

For questions or issues:
1. Check logs at `Haven-UI/logs/ai_chat.log`
2. Review full documentation at `src/roundtable_ai/README.md`
3. Test with `python test_roundtable_ai.py`

---

**🎉 Congratulations! The Round Table AI is ready to use!**

The system is designed to grow with your project. Start with simple discovery analysis and expand from there.
