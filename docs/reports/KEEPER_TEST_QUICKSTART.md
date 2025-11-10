# 🌌 KEEPER BOT TEST DATA - QUICK START

## ✅ What Was Generated

**10 fully detailed star systems** ready for Discord bot testing:
- 📍 All within 20x20x5 area around origin (0,0,0)
- 🌍 43 planets with full environmental data
- 🌙 49 moons with orbital designations
- 📝 Lore-rich discovery hooks on 50% of bodies
- 🎯 Pattern recognition ready with regional grouping

## 📂 Files Created

| File | Purpose |
|------|---------|
| `data/keeper_test_data.json` | **Main test data** - Use this for bot testing |
| `generate_keeper_test_data.py` | Generator script - Run again to create fresh data |
| `KEEPER_TEST_DATA_REPORT.md` | Full documentation with testing scenarios |
| `dist/VH-Map.html` | 3D map visualization (already generated) |

## 🚀 Next Steps

### 1. Configure The Keeper Bot

**Option A: Environment Variable (Recommended)**
```bash
# In keeper-bot/.env file
HAVEN_DATA_PATH=C:/Users/parke/OneDrive/Desktop/Haven_mdev/data/keeper_test_data.json
```

**Option B: Direct Path Update**
Edit `docs/guides/Haven-lore/keeper-bot/src/core/haven_integration.py`:
```python
# Add to possible_paths list
possible_paths = [
    "C:/Users/parke/OneDrive/Desktop/Haven_mdev/data/keeper_test_data.json",
    # ... other paths
]
```

### 2. Test the Integration

```bash
# Navigate to keeper bot
cd docs/guides/Haven-lore/keeper-bot/src

# Start the bot
python main.py
```

### 3. Run Test Commands in Discord

```
/discovery-report
```

You should now see **10 test systems** in the dropdown:
- ORACLE OMEGA
- VESTIGE ZETA
- ORACLE ZETA
- KEEPER EPSILON
- CIPHER SECUNDUS
- ARCHIVE BETA
- NEXUS BETA
- VAULT ZETA
- VAULT GAMMA
- VAULT NOVA

## 🧪 Quick Test Scenarios

### Test 1: Basic Discovery
1. `/discovery-report`
2. Choose "ORACLE OMEGA"
3. Select planet "ORACLE OMEGA-A" (Toxic Wasteland)
4. Submit discovery report
5. ✅ Keeper should respond with analysis

### Test 2: Pattern Recognition
1. Submit 3 discoveries with "ancient bones" on different planets in **Euclid Core**
2. ✅ Bot should detect regional pattern

### Test 3: Lore Integration
1. Find planet with note: "Text logs reference 'The First Spawn'"
2. Submit text log discovery
3. ✅ Keeper should respond with lore-appropriate analysis

## 📊 System Distribution

| Region | Systems | Good For Testing |
|--------|---------|------------------|
| Euclid Core | 2 | Regional patterns |
| Eissentam Paradise | 3 | Cross-system patterns |
| Hilbert Dimension | 2 | Regional patterns |
| Budullangr Void | 2 | Regional patterns |
| Calypso Expanse | 1 | Isolated discoveries |

## 🎯 Key Features to Test

- [x] System selection dropdown works
- [x] Planet/moon selection shows all bodies
- [x] Space anomaly locations appear
- [x] Discovery submission saves to database
- [x] Pattern recognition triggers (3+ similar discoveries)
- [x] Regional grouping works
- [x] Keeper personality responds appropriately
- [x] Tier progression tracks correctly
- [x] Investigation threads auto-create

## 🔄 Need Fresh Data?

Run the generator again:
```bash
py generate_keeper_test_data.py
```

This will create 10 NEW systems with different:
- Names
- Coordinates (still in 20x20x5 box)
- Planet configurations
- Material distributions
- Discovery hooks

## 🗺️ View the Map

The map was already generated. Open it:
```bash
# Windows
start dist/VH-Map.html

# Or just double-click the file
```

You'll see all 10 systems in 3D space, clustered around the origin.

## ❓ Questions to Ask Yourself

1. **Does the bot see all 10 systems?**
   - Check `/discovery-report` dropdown

2. **Can you select planets and moons?**
   - Each system should show 3-6 planets plus space locations

3. **Do discoveries save?**
   - Check keeper bot database after submission

4. **Does pattern recognition work?**
   - Submit 3+ similar discoveries in same region

5. **Are Keeper responses appropriate?**
   - Match the lore/personality documented in Keeper files

## 💡 Pro Tips

- **Start with "ORACLE OMEGA"** - Has interesting attributes and 4 moons
- **Test regional patterns with "Euclid Core"** - Has 2 systems close together
- **Use "VESTIGE ZETA"** for complex testing - Has 6 planets and 11 moons
- **Check "KEEPER EPSILON"** - Named after The Keeper, fitting for lore tests

## 🐛 Troubleshooting

**Bot can't find Haven data:**
- Check HAVEN_DATA_PATH in .env
- Verify file path is correct for Windows (forward slashes or double backslashes)
- Try absolute path: `C:/Users/parke/OneDrive/Desktop/Haven_mdev/data/keeper_test_data.json`

**No systems showing in dropdown:**
- Check bot logs for "Loaded X Haven systems" message
- Verify JSON is valid (already tested by map generator)
- Restart bot after changing .env

**Pattern recognition not triggering:**
- Need 3+ discoveries with similar attributes
- Must be in same region for regional patterns
- Check pattern threshold settings in bot config

## 📝 Summary

✅ **Data Generated**: 10 systems, 43 planets, 49 moons  
✅ **Map Tested**: Successfully generates VH-Map.html  
✅ **Bot Ready**: Configure HAVEN_DATA_PATH and test  
✅ **Documentation**: Full report in KEEPER_TEST_DATA_REPORT.md  

---

**Need More Help?** Check:
- `KEEPER_TEST_DATA_REPORT.md` - Detailed testing scenarios
- `docs/guides/Haven-lore/KEEPER_BOT_COMMANDS_GUIDE.md` - Bot commands
- `docs/guides/Haven-lore/keeper-bot/README.md` - Bot setup guide
