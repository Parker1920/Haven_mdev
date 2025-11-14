# Haven Control Room - Stress Testing Suite

## Overview

The Haven Control Room includes a comprehensive stress testing suite to validate performance with massive datasets (100K+ systems).

### Quick Start

```bash
# Generate 100,000 system dataset
python tests/stress_testing/generate_100k_stress_test.py

# Run stress test (shows memory optimization)
python tests/stress_testing/quick_stress_test.py --data-file tests/stress_testing/STRESS-100K.json

# Generate map visualization
python src/Beta_VH_Map.py --data-file tests/stress_testing/STRESS-100K.json --no-open
```

**Expected Results:**
- ✅ 100,000 systems loaded in ~9 seconds
- ✅ 55.6% memory reduction
- ✅ 100,001 HTML files generated

---

## Test Files

### 📊 Data Generation
- **`generate_100k_stress_test.py`** - Create massive test datasets
  - Standard: 100K systems (~691 MB)
  - Small: 50K systems (--small flag)
  - Massive: 250K systems (--massive flag)

### 🧪 Performance Testing
- **`quick_stress_test.py`** - Fast performance measurement
  - Tests `optimize_dataframe()` function
  - Shows memory savings
  - Reports timing breakdown
  - Works with any dataset size

- **`stress_test_performance.py`** - Full performance analysis
  - Detailed memory profiling
  - Before/after optimization comparison
  - Data type analysis

### 📈 Original Test Suite
- **`generate_test_data.py`** - Original 500-system test generator
- **`TESTING.json`** - Pre-generated small test dataset

---

## Generated Datasets

### STRESS-100K.json
- **Systems**: 100,000
- **Size**: 691.3 MB
- **Creation Time**: 5-10 seconds
- **Use Case**: Standard stress testing

### STRESS-50K.json
- **Systems**: 50,000
- **Size**: ~350 MB
- **Creation Time**: 3-5 seconds
- **Use Case**: Faster testing

### STRESS-250K.json
- **Systems**: 250,000
- **Size**: ~1.7 GB
- **Creation Time**: 15-20 seconds
- **Use Case**: Extreme load testing

---

## Key Findings

### Memory Optimization Results

**100K Systems Test:**
```
📈 Memory Usage:
   Before: 62.77 MB
   After:  27.90 MB
   Saved:  34.87 MB (55.6%)

✅ Optimization EFFECTIVE!
```

**Scaling to 1M Systems:**
- Memory before: ~628 MB
- Memory after: ~280 MB
- **Savings: ~348 MB (55.6%)**

---

## Documentation

### User Guides
- **`STRESS_TESTING_GUIDE.md`** - Complete testing instructions and troubleshooting
- **`STRESS_TEST_RESULTS_100K.md`** - Detailed results and analysis

### In Source Files
- `src/common/optimize_datasets.py` - Optimization implementation (500+ lines)
- `src/Beta_VH_Map.py` - Map generation with optimization
- `src/system_entry_wizard.py` - System entry with backup/undo features

---

## Running Stress Tests

### Minimal Setup (5 minutes)
```bash
# Generate small dataset
python tests/stress_testing/generate_100k_stress_test.py --small

# Run test
python tests/stress_testing/quick_stress_test.py \
  --data-file tests/stress_testing/STRESS-50K.json

# Generate map
python src/Beta_VH_Map.py \
  --data-file tests/stress_testing/STRESS-50K.json --no-open
```

### Standard Testing (30 minutes)
```bash
# Generate standard dataset
python tests/stress_testing/generate_100k_stress_test.py

# Run all tests
python tests/stress_testing/quick_stress_test.py \
  --data-file tests/stress_testing/STRESS-100K.json

# Generate map
python src/Beta_VH_Map.py \
  --data-file tests/stress_testing/STRESS-100K.json --no-open

# Count output files
ls dist/system_*.html | wc -l  # Should show ~100,000
```

### Extreme Testing (60+ minutes)
```bash
# Generate massive dataset
python tests/stress_testing/generate_100k_stress_test.py --massive

# Run test
python tests/stress_testing/quick_stress_test.py \
  --data-file tests/stress_testing/STRESS-250K.json

# Generate map (takes 2-3 minutes)
python src/Beta_VH_Map.py \
  --data-file tests/stress_testing/STRESS-250K.json --no-open
```

---

## What Gets Tested

✅ **Data Generation**
- Realistic system attributes
- Variable planets/moons per system
- Proper JSON formatting
- Large file handling (691+ MB)

✅ **Memory Optimization**
- Type conversion efficiency
- Memory savings calculation
- Data integrity preservation
- Per-system memory reduction

✅ **Map Generation**
- Loading massive datasets
- DataFrame optimization
- HTML rendering
- Static file copying
- Moon visualization injection

✅ **Performance**
- Load time for 100K+ systems
- Memory usage tracking
- Processing speed
- Scalability characteristics

---

## Troubleshooting

### "Out of memory" error
- Use smaller dataset: `--small` flag
- Close other applications
- Check available RAM (4GB+ recommended)

### "Map generation is slow"
- This is normal (30-45 seconds for 100K is typical)
- Use `--no-open` flag to skip browser opening
- Check CPU/RAM usage

### "File not found" error
- Generate dataset first: `python generate_100k_stress_test.py`
- Check file exists: `ls tests/stress_testing/STRESS-*.json`

---

## Performance Benchmarks

| Metric | Value |
|--------|-------|
| Systems loaded | 100,000 |
| Load time | 9.08 seconds |
| Memory before | 62.77 MB |
| Memory after | 27.90 MB |
| Memory saved | 34.87 MB (55.6%) |
| Per-system time | 91 microseconds |
| Per-system memory | 292.59 bytes |

---

## Architecture

```
Tests/Stress Testing/
├── generate_100k_stress_test.py    # Create 100K+ datasets
├── quick_stress_test.py             # Fast performance test
├── stress_test_performance.py       # Full performance analysis
├── generate_test_data.py            # Original test generator
├── TESTING.json                     # Pre-built small dataset
└── STRESS-*.json                    # Generated test datasets

Integration Points:
├── src/Beta_VH_Map.py               # Map generation (uses optimize_dataframe)
├── src/system_entry_wizard.py       # Data entry (uses optimization)
└── src/common/optimize_datasets.py  # Optimization module
```

---

## Summary

The stress testing suite validates:
- ✅ **Scalability**: 100K+ systems handled efficiently
- ✅ **Performance**: 9 seconds to load 100K systems
- ✅ **Memory**: 55.6% reduction through optimization
- ✅ **Reliability**: No data loss or corruption
- ✅ **Integration**: Seamless pipeline integration

---

## References

- **Main Guide**: `STRESS_TESTING_GUIDE.md`
- **Results**: `STRESS_TEST_RESULTS_100K.md`
- **Module**: `src/common/optimize_datasets.py`
- **Integration**: `src/Beta_VH_Map.py` line 172
