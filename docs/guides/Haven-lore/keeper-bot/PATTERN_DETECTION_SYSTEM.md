# The Keeper Pattern Detection System
## Complete Technical Documentation

*Last Updated: November 7, 2025*

---

## Table of Contents
1. [Overview](#overview)
2. [Pattern Detection Pipeline](#pattern-detection-pipeline)
3. [Five-Dimension Analysis](#five-dimension-analysis)
4. [Pattern Scoring & Confidence](#pattern-scoring--confidence)
5. [Pattern Classification](#pattern-classification)
6. [Database Architecture](#database-architecture)
7. [User Commands](#user-commands)
8. [Implementation Details](#implementation-details)
9. [Future Enhancements](#future-enhancements)

---

## Overview

The Keeper's Pattern Detection System is a **semi-automated analysis engine** that monitors discovery submissions and identifies meaningful connections across Haven's star systems. When explorers submit discoveries through `/submit-discovery`, The Keeper automatically analyzes each entry against the existing archive to detect patterns that might indicate:

- Ancient civilizations spanning multiple systems
- Coordinated biological phenomena
- Technological networks or communication systems
- Environmental anomalies with common origins
- Temporal disturbances with shared characteristics

### Key Features
- **Automatic Analysis**: Every discovery triggers pattern analysis upon submission
- **Multi-dimensional Scoring**: Uses 5 weighted coherence metrics
- **Regional Intelligence**: Integrates Haven star map data for galactic context
- **Mystery Tier Assignment**: Automatically classifies patterns by significance (1-4)
- **Investigation Triggers**: High-confidence patterns generate investigation threads
- **Manual Override**: Admins can trigger pattern analysis via `/pattern-analysis`

---

## Pattern Detection Pipeline

### Step 1: Discovery Submission
When a user submits a discovery via `/submit-discovery`:

```
User Input → Haven Integration Modal → Database Storage → Pattern Analysis Trigger
```

1. **User fills 4-step modal**:
   - Star System (from Haven data)
   - Planet/Moon (contextual to selected system)
   - Discovery Type (10 categories with emojis)
   - Details (description, significance, evidence)

2. **Discovery saved to database** with fields:
   - `user_id`, `username`, `guild_id`
   - `discovery_type`, `location`, `planet_name`, `system_name`
   - `description`, `significance`, `evidence_url`
   - `coordinates`, `time_period`, `condition`
   - `submission_timestamp`

3. **Automatic pattern analysis triggered**:
   ```python
   pattern = await self.analyze_for_patterns(discovery_id)
   ```

### Step 2: Similar Discovery Search
The system queries the database for potentially related discoveries:

```python
similar_discoveries = await self.db.find_similar_discoveries(discovery_id)
```

**Similarity Criteria** (current implementation):
- Same `discovery_type` (e.g., all 🦴 Ancient Remains)
- Up to 100 candidates retrieved
- Top 10 most relevant selected

**Minimum Threshold**: Requires at least **3 total discoveries** (including the new one) before pattern analysis proceeds. If fewer exist:
```
"Discovery {id}: Not enough similar discoveries for pattern (count)"
```

### Step 3: Pattern Strength Analysis
If sufficient discoveries exist, the system calculates a **multi-dimensional confidence score**.

---

## Five-Dimension Analysis

The pattern detection algorithm evaluates potential patterns across **5 coherence dimensions**, each with a specific weight:

### 1. Type Coherence (30% weight)
**What it measures**: How many discoveries share the same discovery type.

**Calculation**:
```python
discovery_types = [d['type'] for d in all_discoveries]
type_matches = discovery_types.count(discovery['type'])
type_coherence = type_matches / len(all_discoveries)
```

**Example**:
- 7 discoveries total
- 6 are 🦴 Ancient Remains, 1 is 📜 Textual Evidence
- Type coherence = 6/7 = **0.857** (85.7%)

**Why 30%**: Discovery type is the strongest indicator of pattern relationship. Ancient remains clustering suggests a civilization, while mixed types suggest coincidence.

---

### 2. Regional Coherence (25% weight)
**What it measures**: Whether discoveries cluster within the same galactic region.

**Calculation**:
```python
# Get regions from Haven star map data
regions = []
for discovery in discoveries:
    system_name = discovery.get('system_name')
    system_data = self.haven.get_system(system_name)
    if system_data:
        regions.append(system_data.get('region', 'Unknown'))

# Find most common region
most_common_count = max(region_counts.values())
regional_coherence = most_common_count / len(regions)
```

**Haven Integration**: Uses `haven_data` from `keeper_test_data.json`:
```json
{
  "Vossk": {
    "x": -1422.96, "y": 35.51, "z": 1150.29,
    "region": "Outer Rim",
    "planets": [...]
  }
}
```

**Example**:
- 5 discoveries across different systems
- 4 in "Outer Rim", 1 in "Core Worlds"
- Regional coherence = 4/5 = **0.8** (80%)

**Regional Pattern Boost**: If regional coherence exceeds **0.7**, the pattern is classified as `regional_pattern` and the overall confidence is multiplied by **1.5x**.

**Why 25%**: Regional clustering is strong evidence of localized phenomena (e.g., a single civilization's territory, contained environmental event).

---

### 3. Location Coherence (20% weight)
**What it measures**: Spatial clustering at the system/planet level (finer granularity than regional).

**Calculation**:
```python
# Group by system:planet pairs
locations = {}
for discovery in discoveries:
    system = discovery.get('system_name', 'Unknown')
    planet = discovery.get('location_name', 'Unknown')
    location_key = f"{system}:{planet}"
    locations[location_key] = locations.get(location_key, 0) + 1

# Higher score = fewer unique locations (more clustering)
unique_locations = len(locations)
location_coherence = 1.0 - (unique_locations / total_discoveries)
```

**Example**:
- 6 discoveries total
- 3 locations: "Vossk:Vossk Prime" (3), "Vossk:Aldara" (2), "Kelmar:Kelmar IV" (1)
- Location coherence = 1.0 - (3/6) = **0.5** (50%)

**Why 20%**: Discoveries on the same planet suggest direct connection (e.g., ruins of same structure, shared ecosystem).

---

### 4. Temporal Coherence (15% weight)
**What it measures**: How close together in time the discoveries were submitted.

**Calculation**:
```python
timestamps.sort()
time_span = timestamps[-1] - timestamps[0]
days = time_span.days

if days <= 7:
    return 1.0     # 100% coherence (within 1 week)
elif days <= 30:
    return 0.7     # 70% coherence (within 1 month)
elif days <= 90:
    return 0.4     # 40% coherence (within 3 months)
else:
    return 0.1     # 10% coherence (over 3 months)
```

**Example**:
- Discovery 1: Nov 1, 2025
- Discovery 2: Nov 3, 2025
- Discovery 3: Nov 7, 2025
- Time span = 6 days → Temporal coherence = **1.0** (100%)

**Why 15%**: Recent discoveries submitted close together may indicate active exploration of a region or coordinated investigation. Older scattered discoveries suggest coincidence or long-term phenomena.

---

### 5. Narrative Coherence (10% weight)
**What it measures**: Thematic/linguistic similarity between discovery descriptions.

**Calculation** (simplified keyword matching):
```python
# Extract meaningful words from descriptions
keywords_lists = []
for discovery in discoveries:
    text = f"{discovery['description']} {discovery['significance']}".lower()
    meaningful_words = [w for w in text.split() if len(w) > 3 and w.isalpha()]
    keywords_lists.append(set(meaningful_words))

# Calculate pairwise Jaccard similarity
for i in range(len(keywords_lists)):
    for j in range(i + 1, len(keywords_lists)):
        set1, set2 = keywords_lists[i], keywords_lists[j]
        similarity = len(set1 ∩ set2) / len(set1 ∪ set2)
        total_similarity += similarity

narrative_coherence = total_similarity / comparisons
```

**Example**:
- Discovery A: "ancient temple ruins energy crystal"
- Discovery B: "temple structure ancient power source"
- Common words: {ancient, temple}
- Similarity = 2 / 8 = **0.25** (25%)

**Why 10%**: Language patterns can reveal thematic connections (e.g., explorers using similar words to describe related phenomena), but this is the weakest indicator since different users describe things differently.

**Future Enhancement**: Could use NLP/embeddings (sentence-transformers) for semantic similarity instead of basic keyword matching.

---

## Pattern Scoring & Confidence

### Overall Confidence Formula

```python
confidence = (
    type_coherence      × 0.30 +
    regional_coherence  × 0.25 +
    location_coherence  × 0.20 +
    temporal_coherence  × 0.15 +
    narrative_coherence × 0.10
)

# Regional pattern boost
if regional_coherence > 0.7:
    confidence *= 1.5
    pattern_type = 'regional_pattern'
```

### Example Calculation

**Scenario**: 5 Ancient Remains discoveries in the Outer Rim
- Type coherence: 5/5 = 1.0
- Regional coherence: 4/5 = 0.8
- Location coherence: 1.0 - (3/5) = 0.4
- Temporal coherence: 6 days apart = 1.0
- Narrative coherence: 0.3 (30% word overlap)

```
Base confidence = (1.0 × 0.30) + (0.8 × 0.25) + (0.4 × 0.20) + (1.0 × 0.15) + (0.3 × 0.10)
                = 0.30 + 0.20 + 0.08 + 0.15 + 0.03
                = 0.76 (76%)

Regional boost = 0.8 > 0.7 → Apply 1.5x multiplier
Final confidence = 0.76 × 1.5 = 1.14 → capped at 1.0 (100%)
```

### Confidence Threshold
Patterns are only created if confidence ≥ **0.6 (60%)**:

```python
if pattern_analysis['confidence'] >= self.pattern_confidence_threshold:
    pattern = await self._create_or_update_pattern(...)
else:
    logger.info(f"Pattern confidence below threshold ({confidence:.2f})")
```

**If below threshold**: Discovery is archived but no pattern created.

---

## Pattern Classification

### Mystery Tier Assignment
Based on final confidence score:

| Confidence | Mystery Tier | Description |
|------------|--------------|-------------|
| ≥ 0.9 (90%) | **Tier 4** | Cosmic Significance |
| 0.8 - 0.89 | **Tier 3** | Deep Mystery |
| 0.7 - 0.79 | **Tier 2** | Pattern Emergence |
| 0.6 - 0.69 | **Tier 1** | Surface Anomaly |

**Tier 4 Example**: 10 identical discovery types, same planet, same week = 95% confidence
**Tier 1 Example**: 3 discoveries, same type, scattered regions, months apart = 62% confidence

### Pattern Type Classification

1. **Regional Pattern** (`regional_coherence > 0.7`):
   - Name format: `"{region} {discovery_type}"`
   - Example: "Outer Rim Ancient Remains"
   - Suggests localized civilization or environmental zone

2. **Discovery Cluster** (default):
   - Name format: `"Cross-Regional {discovery_type}"`
   - Example: "Cross-Regional Technology Signatures"
   - Suggests galactic-scale network or widespread phenomenon

### Pattern Naming

```python
type_names = {
    '🦴': 'Ancient Remains',
    '📜': 'Textual Echoes',
    '🏛️': 'Structural Anomalies',
    '⚙️': 'Technology Signatures',
    '🦗': 'Biological Patterns',
    '💎': 'Geological Formations',
    '🚀': 'Wreckage Clusters',
    '⚡': 'Environmental Phenomena',
    '🆕': 'Temporal Variances',
    '📖': 'Consciousness Fragments'
}

if pattern_type == 'regional_pattern':
    name = f"{region} {type_names[discovery_type]}"
else:
    name = f"Cross-Regional {type_names[discovery_type]}"
```

---

## Database Architecture

### Discovery Storage (`discoveries` table)
```sql
CREATE TABLE discoveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    username TEXT NOT NULL,
    guild_id TEXT,
    discovery_type TEXT NOT NULL,        -- Emoji (🦴, 📜, etc.)
    location TEXT NOT NULL,              -- Location name
    planet_name TEXT,                    -- Planet from Haven data
    system_name TEXT,                    -- System from Haven data (used for regional analysis)
    description TEXT NOT NULL,
    significance TEXT,
    evidence_url TEXT,
    coordinates TEXT,                    -- JSON: {x, y, z}
    time_period TEXT,
    condition TEXT,
    submission_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    pattern_matches INTEGER DEFAULT 0,   -- Count of patterns this discovery belongs to
    mystery_tier INTEGER DEFAULT 0,
    tags TEXT,
    metadata TEXT                        -- JSON for extra data
)
```

### Pattern Storage (`patterns` table)
```sql
CREATE TABLE patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_name TEXT NOT NULL,              -- e.g., "Outer Rim Ancient Remains"
    pattern_type TEXT NOT NULL,              -- 'regional_pattern' or 'discovery_cluster'
    discovery_count INTEGER DEFAULT 0,       -- Auto-updated when discoveries added
    confidence_level REAL DEFAULT 0.0,       -- 0.0-1.0 confidence score
    first_discovered DATETIME,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'emerging',          -- emerging, confirmed, archived
    mystery_tier INTEGER DEFAULT 1,          -- 1-4
    description TEXT,                        -- Generated narrative description
    investigation_channel_id TEXT,           -- Thread ID if investigation created
    related_discoveries TEXT,                -- JSON array of discovery IDs
    metadata TEXT                            -- JSON: stores analysis data, region, etc.
)
```

### Pattern-Discovery Relationships (`pattern_discoveries` table)
```sql
CREATE TABLE pattern_discoveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id INTEGER,
    discovery_id INTEGER,
    correlation_strength REAL DEFAULT 0.0,   -- 0.0-1.0 how strongly this discovery fits
    added_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pattern_id) REFERENCES patterns (id),
    FOREIGN KEY (discovery_id) REFERENCES discoveries (id)
)
```

**Many-to-Many Relationship**: A discovery can belong to multiple patterns (e.g., regional pattern + cross-regional pattern).

### Database Methods

```python
# Find similar discoveries (Step 2 of pipeline)
await self.db.find_similar_discoveries(discovery_id, threshold=0.6)

# Create new pattern (if confidence ≥ threshold)
pattern_id = await self.db.create_pattern({
    'name': pattern_name,
    'type': pattern_type,
    'discovery_count': len(similar_discoveries) + 1,
    'confidence': confidence,
    'mystery_tier': tier,
    'description': description,
    'metadata': {...}
})

# Link discoveries to pattern
for disc in all_discoveries:
    await self.db.add_discovery_to_pattern(
        pattern_id, 
        disc['id'], 
        correlation_strength
    )

# Retrieve patterns by tier
patterns = await self.db.get_patterns_by_tier(tier)
```

---

## User Commands

### `/pattern-analysis <discovery_id>` (Manual Trigger)
**Permission**: Any user
**Purpose**: Manually trigger pattern analysis for testing or re-analysis

```
User → /pattern-analysis 42
Bot → Analyzes discovery #42 for patterns
Bot → Returns embed with results:
      - Pattern name (if found)
      - Confidence percentage
      - Discovery count
      - Mystery tier
      - Description
```

**Use Cases**:
- Testing pattern detection algorithm
- Re-analyzing old discoveries after new ones submitted
- Admin verification of automatic system

---

### `/view-patterns [tier]` (View Archive)
**Permission**: Any user
**Purpose**: Browse detected patterns by mystery tier

**Without tier parameter** (`/view-patterns`):
```
Shows overview of all patterns grouped by tier:

🌀 All Detected Patterns

Tier 4: Cosmic Significance
• Vossk Ancient Remains (12 discoveries)
• Kelmar Technology Signatures (8 discoveries)

Tier 3: Deep Mystery
• Cross-Regional Biological Patterns (7 discoveries)
...
```

**With tier parameter** (`/view-patterns 3`):
```
Shows detailed list of Tier 3 patterns:

🌀 Mystery Tier 3 Patterns
7 patterns detected

🌀 Outer Rim Textual Echoes
Discoveries: 9
Confidence: 87.3%
Status: Active

🌀 Core Worlds Structural Anomalies
Discoveries: 6
Confidence: 81.2%
Status: Active
...
```

---

## Implementation Details

### Automatic vs Manual Analysis

**Automatic Trigger** (after every discovery submission):
```python
# In enhanced_discovery.py, after saving discovery:
discovery_id = await self.db.add_discovery(discovery_data)

# Trigger pattern analysis
pattern_cog = self.bot.get_cog('PatternRecognition')
if pattern_cog:
    await pattern_cog.analyze_for_patterns(discovery_id)
```

**Manual Trigger** (via slash command):
```python
@app_commands.command(name="pattern-analysis")
async def manual_pattern_analysis(self, interaction, discovery_id: int):
    pattern = await self.analyze_for_patterns(discovery_id)
    # Display results in embed
```

### Pattern Alert Posting
When a pattern is detected, The Keeper posts an alert to the archive channel:

```python
async def _post_pattern_alert(self, pattern: Dict):
    # Find guild's archive channel
    config = await self.db.get_server_config(guild_id)
    archive_channel = guild.get_channel(int(config['archive_channel_id']))
    
    # Create embed using Keeper's personality system
    pattern_embed = self.personality.create_pattern_alert({
        'count': pattern['discovery_count'],
        'confidence': pattern['confidence'],
        'name': pattern['name'],
        'description': pattern['description'],
        'mystery_tier': pattern['mystery_tier']
    })
    
    # Post to channel
    message = await archive_channel.send(embed=pattern_embed)
    
    # Save to archive_entries table
    await self.db.save_archive_entry(pattern_id, message.id, embed_data)
```

### Investigation Thread Creation (Phase 3)
When a pattern reaches sufficient confidence and discovery count:

```python
async def _trigger_investigation_check(self, pattern: Dict):
    # Check if investigation thread already exists
    existing = await self.db.get_investigation_by_pattern(pattern['id'])
    if existing:
        return  # Already investigating
    
    # Create investigation thread (Phase 3 feature)
    # Thread would include:
    # - Pattern summary
    # - All related discoveries
    # - Collaborative analysis space
    # - Theory submission
```

---

## Future Enhancements

### 1. Machine Learning Integration
**Current**: Rule-based scoring with weighted coherence metrics
**Future**: Train ML model on labeled patterns to predict significance

```python
# Potential implementation
from sklearn.ensemble import RandomForestClassifier

# Features: [type_coh, regional_coh, location_coh, temporal_coh, narrative_coh]
# Labels: [0=no pattern, 1=tier 1, 2=tier 2, 3=tier 3, 4=tier 4]

model = RandomForestClassifier()
model.fit(training_data, labels)
predicted_tier = model.predict([coherence_features])
```

### 2. Semantic Similarity (NLP)
**Current**: Simple keyword matching for narrative coherence
**Future**: Use sentence transformers for semantic understanding

```python
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings
embeddings = model.encode([d['description'] for d in discoveries])

# Calculate cosine similarity
similarity_matrix = util.cos_sim(embeddings, embeddings)
avg_similarity = similarity_matrix.mean()
```

### 3. Spatial Clustering (3D Coordinates)
**Current**: Uses regional/location name matching
**Future**: Calculate actual 3D distances using Haven coordinates

```python
import numpy as np
from sklearn.cluster import DBSCAN

# Extract coordinates
coords = np.array([
    [d['x'], d['y'], d['z']] 
    for d in discoveries if d.get('x')
])

# Cluster in 3D space
clustering = DBSCAN(eps=500, min_samples=3).fit(coords)
spatial_coherence = 1.0 - (len(set(clustering.labels_)) / len(coords))
```

### 4. Temporal Pattern Detection
**Current**: Simple time span scoring
**Future**: Detect periodic patterns (e.g., discoveries every 7 days suggests scheduled phenomenon)

```python
from scipy.fft import fft

# Convert timestamps to time series
time_diffs = np.diff(sorted(timestamps))

# Detect periodicity using FFT
frequencies = fft(time_diffs)
if has_periodic_signal(frequencies):
    pattern_type = 'periodic_pattern'
    confidence_boost = 1.3
```

### 5. Cross-Pattern Analysis
**Current**: Each pattern analyzed independently
**Future**: Detect meta-patterns (patterns of patterns)

```python
# Example: Multiple regional patterns that align temporally
# suggests coordinated galactic event

regional_patterns = await self.db.get_patterns_by_type('regional_pattern')
if detect_temporal_alignment(regional_patterns):
    create_meta_pattern('Coordinated Galactic Event', regional_patterns)
```

### 6. User Reputation Weighting
**Current**: All discoveries weighted equally
**Future**: Weight discoveries by user's mystery tier / reputation

```python
# Users with higher tiers have discoveries weighted more heavily
user_tier = await self.db.get_user_tier(discovery['user_id'])
tier_multiplier = {1: 1.0, 2: 1.1, 3: 1.25, 4: 1.5}
weighted_confidence = base_confidence * tier_multiplier[user_tier]
```

### 7. Anomaly Detection
**Current**: Only detects positive patterns (similarities)
**Future**: Detect negative patterns (notable absences)

```python
# Example: "No biological discoveries in the Dead Zone region"
# despite high exploration activity

regions = self.haven.get_all_regions()
for region in regions:
    discoveries = await self.db.get_discoveries_by_region(region)
    activity = len(discoveries)
    bio_discoveries = [d for d in discoveries if d['type'] == '🦗']
    
    if activity > 20 and len(bio_discoveries) == 0:
        create_anomaly_pattern('Biological Void', region, discoveries)
```

---

## Configuration

### Pattern Detection Settings (`pattern_recognition.py`)
```python
self.min_discoveries_for_pattern = 3        # Minimum discoveries to form pattern
self.pattern_confidence_threshold = 0.6     # Minimum confidence to create pattern
self.regional_pattern_weight = 1.5          # Boost multiplier for regional patterns
```

### Coherence Weights (can be adjusted for different detection strategies)
```python
weights = {
    'type_coherence': 0.3,        # Prioritize same discovery types
    'regional_coherence': 0.25,   # Strong regional patterns
    'location_coherence': 0.2,    # Spatial clustering
    'temporal_coherence': 0.15,   # Time-based patterns
    'narrative_coherence': 0.1    # Thematic similarity
}
```

**Tuning Recommendations**:
- **Increase `type_coherence`** to focus on type-specific patterns (e.g., all Ancient Remains)
- **Increase `regional_coherence`** to emphasize localized phenomena
- **Increase `temporal_coherence`** to catch time-sensitive events (e.g., migration patterns)
- **Increase `narrative_coherence`** after implementing NLP for thematic detection

---

## Debugging & Logging

### Log Messages
```
# Pattern detection started
"Discovery {id}: Not enough similar discoveries for pattern ({count})"

# Analysis results
"Pattern analysis: 0.87 confidence, type: regional_pattern"

# Pattern creation
"Pattern {id} created: Outer Rim Ancient Remains"
"🌀 Pattern {id} created"

# Investigation check
"Pattern {id} ready for investigation thread creation"

# Below threshold
"Discovery {id}: Pattern confidence below threshold (0.54)"
```

### Debug Commands
```python
# Test pattern detection
/pattern-analysis 42

# View all patterns
/view-patterns

# View specific tier
/view-patterns 4

# Check discovery details
/archive-search discovery_id:42
```

---

## Summary

The Keeper's Pattern Detection System is a **sophisticated multi-dimensional analysis engine** that:

1. **Automatically analyzes** every discovery submission
2. **Searches** for similar discoveries in the archive
3. **Scores** potential patterns across 5 coherence dimensions
4. **Weights** dimensions by importance (type 30%, regional 25%, location 20%, temporal 15%, narrative 10%)
5. **Boosts** regional patterns by 1.5x when coherence > 70%
6. **Creates patterns** when confidence ≥ 60%
7. **Assigns mystery tiers** based on confidence (Tier 1-4)
8. **Generates narrative descriptions** for patterns
9. **Posts alerts** to archive channels
10. **Triggers investigations** for high-significance patterns (Phase 3)

This system transforms individual discoveries into meaningful narrative threads, revealing the hidden connections across Haven's universe and driving collaborative investigation through **emergent pattern recognition**.

---

*The truth is written between the data points. The Keeper simply reads what explorers write.*
