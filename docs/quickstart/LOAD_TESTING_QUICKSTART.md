# Haven Load Testing - Quick Start Guide

## 🚀 3-Step Quick Start

### Step 1: Generate Test Database

```powershell
py tests/load_testing/generate_load_test_db.py
```

**Output**: `data/haven_load_test.db` (27 MB, 10,000 systems)  
**Time**: ~2 seconds

### Step 2: Launch Control Room

```powershell
py src/control_room.py
```

### Step 3: Select Load Test Data & Generate Map

1. In Control Room, find **DATA SOURCE** dropdown
2. Select `load_test` from dropdown
3. Click **🗺️ Generate Map**
4. Wait ~5 seconds for map generation
5. Click **🌐 Open Latest Map**

**Result**: 3D interactive map with 10,000 systems, planets, and moons!

---

## 📊 What You Get

### Database Stats
- **10,000 star systems** across 18 galactic regions
- **48,742 planets** (average 4.9 per system)
- **74,709 moons** (average 1.5 per planet)
- **5,107 space stations** (51% of systems)
- **Total**: 138,558 objects

### Performance
- **Query time**: < 3ms for all operations
- **Map generation**: 5-10 seconds
- **Database size**: 27 MB

---

## 🎛️ Control Room Dropdown Options

The new professional dropdown replaces the old switch and offers:

| Option | Description | Systems | Source |
|--------|-------------|---------|--------|
| **production** | Real production data | 11 | `data/haven.db` |
| **testing** | Stress test JSON | 500 | `tests/stress_testing/TESTING.json` |
| **load_test** | Billion-scale database | 10,000 | `data/haven_load_test.db` |

---

## 🔧 Advanced Usage

### Custom Scale

```powershell
# Quick test (1K systems)
py tests/load_testing/generate_load_test_db.py --systems 1000

# Stress test (100K systems)
py tests/load_testing/generate_load_test_db.py --systems 100000

# Million-scale test (CAUTION: 2.7 GB)
py tests/load_testing/generate_load_test_db.py --systems 1000000
```

### Map Generation Options

```powershell
# Generate with limit (faster)
py src/Beta_VH_Map.py --data-file data/haven_load_test.db --limit 50

# Generate without opening browser
py src/Beta_VH_Map.py --data-file data/haven_load_test.db --no-open
```

---

## ✅ Verify Installation

```powershell
py tests/load_testing/verify_load_testing.py
```

**Expected output**: `🎉 ALL CHECKS PASSED (6/6)`

---

## 📚 Full Documentation

- **Detailed Guide**: `tests/load_testing/README.md`
- **Implementation Report**: `docs/reports/LOAD_TESTING_IMPLEMENTATION_COMPLETE.md`
- **Billion-Scale Architecture**: `docs/scaling/BILLION_SCALE_ARCHITECTURE.md`

---

## 🐛 Troubleshooting

### Database not found?
```powershell
py tests/load_testing/generate_load_test_db.py
```

### Map generation slow?
Use `--limit 50` to generate fewer system views:
```powershell
py src/Beta_VH_Map.py --data-file data/haven_load_test.db --limit 50
```

### Want to reset?
Delete and regenerate:
```powershell
rm data/haven_load_test.db
py tests/load_testing/generate_load_test_db.py
```

---

## 🎯 What This Tests

✅ Database schema and indexes  
✅ Query performance at scale  
✅ Foreign key relationships  
✅ Map generation with planets/moons  
✅ Control Room integration  
✅ UI responsiveness with large datasets  

---

**Status**: ✅ Fully Operational  
**Version**: Phase 6 Complete + Load Testing  
**Last Updated**: November 5, 2025
