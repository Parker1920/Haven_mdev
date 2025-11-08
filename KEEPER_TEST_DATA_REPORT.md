# Keeper Bot Test Data - Generation Report

## 📊 Summary

Successfully generated **10 richly detailed star systems** specifically designed for testing The Keeper Discord bot's discovery and pattern recognition features.

### Statistics

- **Star Systems**: 10
- **Total Planets**: 43
- **Total Moons**: 49
- **Total Celestial Bodies**: 102
- **Average Planets per System**: 4.3
- **Average Moons per Planet**: 1.1

### Coordinate Distribution

All systems placed within a **20x20x5 area** centered on origin (0,0,0):
- **X Range**: -10 to +10
- **Y Range**: -10 to +10  
- **Z Range**: -2.5 to +2.5

## 🌌 Generated Systems

| System Name | Coordinates | Region | Planets | Moons |
|-------------|-------------|--------|---------|-------|
| ORACLE OMEGA | (9.57, -4.52, 0.61) | Euclid Core | 3 | 4 |
| VESTIGE ZETA | (1.97, -4.4, 2.5) | Euclid Core | 6 | 11 |
| ORACLE ZETA | (9.91, -8.88, 0.07) | Eissentam Paradise | 5 | 3 |
| KEEPER EPSILON | (5.57, -7.12, -0.43) | Budullangr Void | 4 | 4 |
| CIPHER SECUNDUS | (-4.43, -8.55, 0.18) | Calypso Expanse | 4 | 7 |
| ARCHIVE BETA | (-6.18, -8.87, -1.56) | Eissentam Paradise | 3 | 3 |
| NEXUS BETA | (2.68, 7.57, -0.72) | Eissentam Paradise | 5 | 4 |
| VAULT ZETA | (7.4, 1.16, 2.3) | Hilbert Dimension | 3 | 3 |
| VAULT GAMMA | (7.41, -0.05, 0.82) | Budullangr Void | 4 | 2 |
| VAULT NOVA | (-0.76, 1.26, 2.03) | Hilbert Dimension | 6 | 8 |

## 🎯 Lore-Rich Features

### System-Level Attributes
Every system includes:
- ✅ **Full coordinates** (x, y, z)
- ✅ **Galactic region** (for pattern recognition)
- ✅ **Sentinel activity levels** (None → Aggressive)
- ✅ **Fauna/Flora ratings** (None → Rich/Lush)
- ✅ **Material lists** (Common, Uncommon, Rare)
- ✅ **Discovery attributes** (2-4 per system):
  - Ancient ruins detected
  - Unusual signal patterns
  - Atmospheric anomalies
  - Remnant structures
  - High predator concentration
  - Sentinel activity notes
  - Archaeological sites
  - And more...

### Planet-Level Detail
Each planet features:
- ✅ **Planet type** (Lush Paradise, Toxic Wasteland, etc.)
- ✅ **Sentinel levels**
- ✅ **Fauna/Flora ratings**
- ✅ **Material deposits**
- ✅ **Base locations** (40% have established bases)
- ✅ **Discovery notes** (50% include lore hooks):
  - Ancient bone deposits
  - Text log references
  - Korvax data fragments
  - Crashed freighters
  - Genetic manipulation signs
  - Boundary failures
  - Atlas interface coordinates

### Moon Characteristics
Moons include:
- ✅ **Orbital designation** (M1, M2, M3)
- ✅ **Terrain types** (Rocky, Icy, Barren, Volcanic, Cratered)
- ✅ **Full environmental data**
- ✅ **Discovery notes** (60% include findings):
  - Fossil deposits
  - Recovered text logs
  - Mysterious ruins
  - Abandoned technology
  - Biological anomalies
  - High sentinel zones

## 🔍 Pattern Recognition Ready

### Regional Grouping
Systems distributed across **5 different regions** for cross-system pattern testing:
- **Euclid Core**: 2 systems
- **Eissentam Paradise**: 3 systems
- **Hilbert Dimension**: 2 systems
- **Budullangr Void**: 2 systems
- **Calypso Expanse**: 1 system

### Discovery Types Present
The dataset includes hooks for all Keeper bot discovery categories:
1. ✅ **Ancient Bones & Fossils** - Multiple planets have bone deposit notes
2. ✅ **Text Logs** - Several references to encrypted/recovered logs
3. ✅ **Ruins & Structures** - Korvax/ancient ruins mentioned
4. ✅ **Technology** - Abandoned tech and crashed ships
5. ✅ **Biological** - Genetic anomalies and unusual flora/fauna
6. ✅ **Environmental** - Storm activity, atmospheric anomalies
7. ✅ **Atlas/Boundary** - Interface coordinates, boundary failures
8. ✅ **Sentinel Activity** - Various threat levels documented

## 📁 File Locations

**Primary Test Data:**
```
data/keeper_test_data.json
```

**Generator Script:**
```
generate_keeper_test_data.py
```

## 🚀 Usage Instructions

### For Keeper Discord Bot Testing

1. **Update Bot Configuration**
   ```bash
   # In keeper-bot/.env or config
   HAVEN_DATA_PATH=C:/Users/parke/OneDrive/Desktop/Haven_mdev/data/keeper_test_data.json
   ```

2. **Restart The Keeper Bot**
   ```bash
   cd docs/guides/Haven-lore/keeper-bot/src
   python main.py
   ```

3. **Test Discovery Commands**
   - Run `/discovery-report` in Discord
   - Bot should now show all 10 test systems
   - Each system has 3-6 planets/moons to choose from
   - Submit discoveries to test pattern recognition

### For Haven Control Room

To use this data in the Haven Control Room application:

1. **Option A: Replace Current Data (Backup First!)**
   ```bash
   # Backup existing data
   cp data/data.json data/data.json.backup
   
   # Use test data
   cp data/keeper_test_data.json data/data.json
   ```

2. **Option B: Load as Separate Dataset**
   - Keep as `keeper_test_data.json`
   - Manually load in Control Room when needed

3. **Generate Map**
   - Run Control Room
   - Click "Generate Map"
   - View all 10 systems in 3D space

## 🧪 Testing Scenarios

### Scenario 1: Basic Discovery Submission
1. Submit discovery on `ORACLE OMEGA-A` (Toxic Wasteland)
2. Note: Has "Ancient Temple Complex" base
3. Check if Keeper responds with appropriate analysis

### Scenario 2: Pattern Recognition (Same Region)
1. Submit fossil discovery on planet in `Euclid Core`
2. Submit another fossil discovery on different planet in `Euclid Core`
3. Bot should detect regional pattern
4. Investigation thread should trigger after 3+ similar discoveries

### Scenario 3: Cross-System Patterns
1. Submit "ancient bones" discoveries across different systems
2. Look for notes like "Multiple ancient bone deposits - potential pattern connection"
3. Test if bot correlates findings across regions

### Scenario 4: Lore Integration
1. Find planets with specific notes:
   - "Text logs reference 'The First Spawn'"
   - "Korvax historical data fragments"
   - "Atlas interface coordinates"
2. Submit discoveries referencing these notes
3. Verify Keeper's personality responses align with lore

### Scenario 5: High Activity Testing
1. Multiple users submit discoveries simultaneously
2. Test pattern detection under load
3. Verify database integrity
4. Check tier progression system

## 🎨 Data Quality Features

### Realistic Distributions
- **Sentinel Levels**: Weighted toward Low/Medium (realistic)
- **Moon Counts**: 0-3 per planet (matches NMS averages)
- **Material Rarity**: Common materials always present, rare materials ~30%
- **Base Locations**: ~60% of planets have bases (realistic colonization)
- **Discovery Notes**: ~50% have lore hooks (keeps it special)

### Naming Conventions
- **Systems**: KEEPER-themed names (ORACLE, VESTIGE, ARCHIVE, etc.)
- **Planets**: System name + letter designation (A, B, C...)
- **Moons**: Planet name + M1, M2, M3...
- **IDs**: SYS_KEEPER_TEST_001 format

### Lore Consistency
All discovery notes align with:
- The Keeper's narrative voice
- No Man's Sky canonical lore
- Pattern recognition objectives
- Community engagement goals

## 🔄 Regenerating Data

To create a fresh dataset:

```bash
# Run the generator again
py generate_keeper_test_data.py

# This will overwrite keeper_test_data.json
# Previous data will be lost unless backed up
```

## 📝 Notes

- All coordinates are within visible range on the Haven map
- Systems are spread out enough to avoid clustering
- Regional distribution supports pattern testing
- Material lists include both common and rare items for variety
- Discovery hooks are varied enough to test all bot features

## ✅ Validation Checklist

- [x] 10 systems generated
- [x] All within 20x20x5 coordinate box
- [x] All systems have valid IDs
- [x] All systems have regions
- [x] All planets have sentinel/fauna/flora data
- [x] Moons properly nested under planets
- [x] Discovery attributes present
- [x] Material lists realistic
- [x] Lore notes included
- [x] JSON validates against Haven schema
- [x] Compatible with Keeper bot haven_integration.py

## 🎯 Success Criteria

The data is ready for bot testing when:
1. ✅ Keeper bot can load all 10 systems
2. ✅ `/discovery-report` shows system selector with all systems
3. ✅ Each system shows correct planet/moon options
4. ✅ Discoveries save to keeper_db.py database
5. ✅ Pattern recognition activates after 3+ similar discoveries
6. ✅ Regional grouping works correctly
7. ✅ Keeper personality responds appropriately to each discovery type
8. ✅ Haven Control Room can generate map from this data

---

**Generated**: November 7, 2025  
**Purpose**: Discord bot testing for The Keeper  
**Version**: 1.0.0  
**Status**: Ready for production testing
