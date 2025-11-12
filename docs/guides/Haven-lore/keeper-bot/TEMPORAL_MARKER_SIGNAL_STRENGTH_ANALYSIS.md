# Temporal Marker & Signal Strength Analysis

**Found in:** Discovery Analysis Embed (after submitting `/discovery-report`)
**Status:** ⚠️ COSMETIC ONLY - No functional purpose

---

## Current Implementation

### What They Display

After submitting a discovery, The Keeper shows an analysis embed with these fields:

```
📍 Coordinates: `Planet Name`
🕐 Temporal Marker: `Unknown Era`
⚡ Signal Strength: `Indeterminate`
```

### Where The Data Comes From

**File:** `keeper_personality.py` lines 223-232

```python
embed.add_field(
    name="🕐 Temporal Marker",
    value=f"`{discovery_data.get('time_period', 'Unknown Era')}`",
    inline=True
)

embed.add_field(
    name="⚡ Signal Strength",
    value=f"`{discovery_data.get('condition', 'Indeterminate')}`",
    inline=True
)
```

### The Problem

**Neither field is actually collected from users!**

1. **time_period** - Has a column in database but is never populated by modals
2. **condition** - Has a column in database but is never populated by modals

**Current values:**
- Temporal Marker: Always shows `"Unknown Era"` (default fallback)
- Signal Strength: Always shows `"Indeterminate"` (default fallback)

---

## Why They're Not Populated

### Discovery Modals Don't Collect These Fields

Each discovery type modal (Ancient Bones, Ruins, Tech, etc.) has **specific fields**:
- Ancient Bones: `species_type`, `size_scale`, `preservation_quality`, `estimated_age`
- Ruins: `structure_type`, `architectural_style`, `structural_integrity`
- Tech: `tech_category`, `operational_status`, `power_source`

But **NONE** of them have universal `time_period` or `condition` fields.

### Type-Specific Fields Get Lost

Some modals DO collect similar data:
- Ancient Bones → `estimated_age` (e.g., "Ancient", "Millions of years")
- Crashed Ships → `hull_condition` (e.g., "Heavily Damaged")

BUT these are stored in type-specific columns, not in `time_period` or `condition`.

---

## What They COULD Do

### Option 1: Map Type-Specific Fields (Easiest)

**Implementation:** Map existing fields to these display values

```python
# For Temporal Marker
if discovery_data.get('estimated_age'):  # Ancient Bones
    temporal_marker = discovery_data['estimated_age']
elif discovery_data.get('update_name'):  # NMS Update content
    temporal_marker = f"Post-{discovery_data['update_name']}"
else:
    temporal_marker = "Current Era"

# For Signal Strength
if discovery_data.get('preservation_quality'):  # Ancient Bones
    signal_strength = discovery_data['preservation_quality']
elif discovery_data.get('hull_condition'):  # Crashed Ships
    signal_strength = discovery_data['hull_condition']
elif discovery_data.get('operational_status'):  # Tech
    signal_strength = discovery_data['operational_status']
elif discovery_data.get('structural_integrity'):  # Ruins
    signal_strength = discovery_data['structural_integrity']
else:
    signal_strength = "Signal Detected"
```

**Result:** Uses existing modal data, shows relevant info

---

### Option 2: Add Universal Fields to ALL Modals

**Add these fields to every discovery modal:**

```python
time_period = discord.ui.TextInput(
    label="🕐 Estimated Age/Era",
    placeholder="e.g., Ancient, Pre-Gek, Recent, Unknown",
    max_length=100,
    required=False
)

condition = discord.ui.TextInput(
    label="⚡ Condition/Integrity",
    placeholder="e.g., Pristine, Damaged, Degraded, Fragmented",
    max_length=100,
    required=False
)
```

**Pros:**
- Standardized data collection
- Works for all discovery types
- Direct database mapping

**Cons:**
- Adds 2 more fields to EVERY modal (already have 4-5 fields)
- Some redundancy with type-specific fields
- Discord modals limited to 5 text inputs (would need to remove others)

---

### Option 3: Calculate from Discovery Context (Smart Analysis)

**Make them ACTUALLY meaningful based on analysis:**

#### Temporal Marker - Calculated Age/Era
Based on:
- Discovery type patterns
- System/region age indicators
- Cross-referenced with other discoveries
- Pattern matching with historical data

```python
def calculate_temporal_marker(discovery_data):
    # Check for pattern matches
    pattern_age = get_pattern_temporal_context(discovery_data)
    if pattern_age:
        return pattern_age

    # Analyze discovery type
    if discovery_type == '🦴':  # Ancient Bones
        return "Pre-Convergence Era"
    elif discovery_type == '🏛️':  # Ruins
        return "First Spawn Era"
    elif discovery_type == '🆕':  # Update Content
        return "Post-Atlas Awakening"
    else:
        return "Current Iteration"
```

#### Signal Strength - Quality/Importance Score
Based on:
- Description length/detail
- Evidence photo attached (yes/no)
- Pattern match confidence
- User's tier level
- Community significance

```python
def calculate_signal_strength(discovery_data, user_tier, pattern_confidence):
    score = 0

    # Description quality
    if len(discovery_data.get('description', '')) > 200:
        score += 25

    # Photo evidence
    if discovery_data.get('evidence_url'):
        score += 25

    # Pattern match
    if pattern_confidence:
        score += pattern_confidence * 50

    # User tier bonus
    score += user_tier * 10

    # Convert to signal strength
    if score >= 80:
        return "⚡⚡⚡ Strong (Cosmic Significance)"
    elif score >= 60:
        return "⚡⚡ Moderate (Notable Pattern)"
    elif score >= 40:
        return "⚡ Weak (Initial Data)"
    else:
        return "Static (Requires Verification)"
```

**Result:** These become REAL metrics showing discovery quality and age

---

### Option 4: Pattern-Based Temporal Assignment

**Link to Pattern Recognition system:**

When patterns are detected, assign temporal classifications:
- Pattern Tier 1 → "Recent Era"
- Pattern Tier 2 → "Middle Era"
- Pattern Tier 3 → "Ancient Era"
- Pattern Tier 4 → "Primordial Era"

Signal Strength = Pattern confidence score:
- 60-74% → "Weak Signal"
- 75-84% → "Moderate Signal"
- 85-89% → "Strong Signal"
- 90%+ → "Cosmic Resonance"

---

## Recommended Implementation

### Best Approach: **Hybrid of Options 1 & 3**

**Phase 1 (Quick Fix):**
1. Map existing type-specific fields → Display values
2. Shows relevant existing data immediately
3. No modal changes needed

**Phase 2 (Enhanced):**
1. Add quality scoring for Signal Strength
2. Add pattern-based temporal context
3. Make fields MEAN something beyond cosmetic

### Example Output After Implementation:

**Before (Current):**
```
🕐 Temporal Marker: `Unknown Era`
⚡ Signal Strength: `Indeterminate`
```

**After (Option 1 - Mapping):**
```
🕐 Temporal Marker: `Millions of years old`  ← from estimated_age
⚡ Signal Strength: `Excellent Preservation`  ← from preservation_quality
```

**After (Option 3 - Smart Analysis):**
```
🕐 Temporal Marker: `Pre-Convergence Era (Ancient)`
⚡ Signal Strength: `⚡⚡⚡ Strong (87% pattern match, photo evidence)`
```

---

## Implementation Code Samples

### Option 1: Map Existing Fields

```python
def get_temporal_marker(discovery_data):
    """Get temporal marker from existing discovery data."""
    # Check type-specific age fields
    if discovery_data.get('estimated_age'):
        return discovery_data['estimated_age']

    # Check update context
    if discovery_data.get('update_name'):
        return f"Post-{discovery_data['update_name']} Era"

    # Default fallback
    return "Current Iteration"

def get_signal_strength(discovery_data):
    """Get signal strength from existing condition-like fields."""
    # Priority order - check type-specific fields
    for field in ['preservation_quality', 'hull_condition',
                  'operational_status', 'structural_integrity']:
        if discovery_data.get(field):
            return discovery_data[field]

    # Fallback based on evidence
    if discovery_data.get('evidence_url'):
        return "Clear Signal (Evidence Provided)"
    else:
        return "Standard Signal"
```

### Option 3: Quality Scoring

```python
def calculate_discovery_quality_score(discovery_data, user_tier=1, pattern_confidence=0):
    """Calculate quality score for signal strength."""
    score = 0

    # Description length (max 30 points)
    desc_len = len(discovery_data.get('description', ''))
    if desc_len > 300:
        score += 30
    elif desc_len > 150:
        score += 20
    elif desc_len > 50:
        score += 10

    # Evidence attachment (25 points)
    if discovery_data.get('evidence_url'):
        score += 25

    # Pattern confidence (30 points)
    score += pattern_confidence * 30

    # User tier bonus (max 15 points)
    score += min(user_tier * 5, 15)

    return score

def score_to_signal_strength(score):
    """Convert quality score to signal strength display."""
    if score >= 80:
        return "⚡⚡⚡ Cosmic Resonance"
    elif score >= 60:
        return "⚡⚡ Strong Signal"
    elif score >= 40:
        return "⚡ Moderate Signal"
    elif score >= 20:
        return "Weak Signal"
    else:
        return "Faint Trace"
```

---

## Summary

### Current Status:
- **Temporal Marker:** Shows "Unknown Era" (useless)
- **Signal Strength:** Shows "Indeterminate" (useless)
- **Purpose:** Pure flavor text, no function

### What They SHOULD Do:

**Temporal Marker:**
- Show actual age/era of discovery
- Map from existing fields OR calculate from context
- Add historical significance

**Signal Strength:**
- Show discovery quality/confidence
- Based on evidence, description, patterns, user tier
- Indicate how "strong" the discovery is

### Recommendation:
Implement **Option 1** (mapping) immediately for quick wins, then add **Option 3** (smart analysis) for enhanced functionality.

---

**Would you like me to implement any of these options?**
