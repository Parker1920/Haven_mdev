# Stress Testing Guide: 100K+ Dataset Optimization

## Overview

This guide demonstrates how the Haven Control Room handles massive datasets (100K+ systems) using the `optimize_dataframe()` function. The stress tests verify that the application can efficiently process and visualize large-scale data.

## What is optimize_dataframe()?

The `optimize_dataframe()` function is part of the **Dataset Optimization** feature and performs intelligent data type conversion to reduce memory usage:

- **int64 → int32**: For integers within normal range
- **float64 → float32**: For floating-point numbers  
- **object → category**: For string columns with < 50% unique values
- **Skips unhashable types**: Lists and dicts (like planet/moon data)

### Memory Savings
- **Typical reduction**: 30-50% memory savings
- **At 100K systems**: Can save 500MB+ of RAM
- **Per-system**: ~5-10KB reduction per system

## Running the Stress Tests

### Prerequisites
```bash
# Make sure you have the required packages
pip install -r config/requirements.txt
```

### 1. Generate Test Dataset (100K Systems)

```bash
# Standard: 100,000 systems (~691 MB file)
python tests/stress_testing/generate_100k_stress_test.py

# Small: 50,000 systems (~350 MB, faster)
python tests/stress_testing/generate_100k_stress_test.py --small

# Massive: 250,000 systems (~1.7 GB, very large)
python tests/stress_testing/generate_100k_stress_test.py --massive

# Custom: Generate specific number
python tests/stress_testing/generate_100k_stress_test.py 50000
```

**Output Files:**
- `tests/stress_testing/STRESS-100K.json` (691 MB)
- `tests/stress_testing/STRESS-50K.json` (350 MB)
- `tests/stress_testing/STRESS-250K.json` (1.7 GB)

### 2. Run Performance Stress Test

```bash
# Test with 100K dataset
python tests/stress_testing/stress_test_performance.py --data-file tests/stress_testing/STRESS-100K.json

# Test with custom file
python tests/stress_testing/stress_test_performance.py --data-file tests/stress_testing/STRESS-250K.json
```

**Output:**
```
================================================================================
HAVEN CONTROL ROOM - STRESS TEST: optimize_dataframe() Performance
================================================================================

📊 Data File: STRESS-100K.json
   Size: 691.3 MB

Phase 1: Loading data WITHOUT optimization...
   ✓ Loaded 100,000 systems
   ✓ DataFrame memory: 2.84 GB
   ✓ Peak allocation: 3.02 GB

Phase 2: Loading data WITH optimize_dataframe()...
   ✓ Loaded 100,000 systems
   ✓ DataFrame memory: 1.76 GB
   ✓ Peak allocation: 1.94 GB

================================================================================
RESULTS - optimize_dataframe() Effectiveness
================================================================================

📈 Memory Statistics:
   Before optimization: 2.84 GB
   After optimization:  1.76 GB
   Memory saved:        1.08 GB (38.0%)

✅ OPTIMIZATION EFFECTIVE!
   Successfully reduced memory usage by 38.0%
   Equivalent to: 1.08 GB
```

### 3. Generate Map from Massive Dataset

```bash
# Generate map visualization from 100K dataset (no browser open)
python src/Beta_VH_Map.py --data-file tests/stress_testing/STRESS-100K.json --no-open

# Generate and view in browser
python src/Beta_VH_Map.py --data-file tests/stress_testing/STRESS-100K.json
```

**Expected Output:**
```
[2025-11-04 23:50:39] INFO: Loaded 100000 records from tests\stress_testing\STRESS-100K.json
[2025-11-04 23:50:39] INFO: Copied static files
[2025-11-04 23:50:45] INFO: Wrote Galaxy Overview: VH-Map.html
[2025-11-04 23:50:52] INFO: Wrote System View for STRESS-ALPHA-000001: system_STRESS-ALPHA-000001.html
...
[2025-11-04 23:51:30] INFO: Wrote System View for STRESS-OMEGA-100000: system_STRESS-OMEGA-100000.html
```

This creates 100,001 HTML files (1 galaxy view + 100K system views) in `dist/` folder.

## Dataset Specifications

### 100K Standard Dataset
- **File size**: ~691 MB
- **Number of systems**: 100,000
- **Average planets per system**: 4-5
- **Average moons per planet**: 2-3
- **Total objects**: ~500,000-600,000
- **Estimated generation time**: 5-10 seconds
- **Memory usage**: 2.84 GB (unoptimized) → 1.76 GB (optimized)

### 50K Small Dataset
- **File size**: ~350 MB
- **Number of systems**: 50,000
- **Estimated generation time**: 3-5 seconds
- **Memory usage**: 1.42 GB (unoptimized) → 0.88 GB (optimized)

### 250K Massive Dataset
- **File size**: ~1.7 GB
- **Number of systems**: 250,000
- **Estimated generation time**: 15-20 seconds
- **Memory usage**: 7.1 GB (unoptimized) → 4.4 GB (optimized)

## What Gets Tested

### Data Generation
- ✅ 100,000+ unique systems with random attributes
- ✅ Variable planets per system (0-15)
- ✅ Variable moons per planet (0-5)
- ✅ Random coordinates and properties
- ✅ Realistic material/fauna/flora attributes
- ✅ Proper JSON formatting and structure

### Optimization
- ✅ Memory reduction calculation
- ✅ Data type conversion efficiency
- ✅ Peak memory allocation tracking
- ✅ Per-system memory optimization

### Map Generation
- ✅ Loading 100K+ systems from JSON
- ✅ DataFrame optimization during load
- ✅ Galaxy view rendering (100K+ points)
- ✅ Individual system HTML generation (100K+ files)
- ✅ Moon visualization injection
- ✅ Static file copying

## Performance Expectations

### Loading Time
- **100K systems**: 2-3 seconds (with optimization)
- **250K systems**: 5-8 seconds (with optimization)

### Memory Usage
- **100K unoptimized**: ~2.84 GB
- **100K optimized**: ~1.76 GB
- **Savings**: ~1.08 GB (38%)

### Map Generation
- **100K systems map**: 30-45 seconds
- **Output files**: 100,001 HTML files (~3-4 GB total)

## Integration Points

The `optimize_dataframe()` function is automatically called:

1. **In Beta_VH_Map.py** (line 172):
   ```python
   df = optimize_dataframe(df)  # Reduce memory, improve performance
   ```

2. **Triggered when**:
   - Loading any data file with 1000+ systems
   - Any map generation command
   - Any system entry wizard operation

3. **Benefits**:
   - Reduced memory footprint
   - Faster processing
   - Better support for large datasets
   - Automatic optimization (no manual setup required)

## Troubleshooting

### Issue: "Data file not found"
```
Solution: Generate the dataset first
python tests/stress_testing/generate_100k_stress_test.py
```

### Issue: "Out of memory" error
```
Solutions:
1. Use smaller dataset (--small flag)
2. Close other applications
3. Check available RAM (need at least 4GB for 100K)
4. Use 32-bit Python? (try 64-bit)
```

### Issue: Map generation is very slow
```
Solutions:
1. This is normal for 100K systems (30-45 seconds is typical)
2. Use --no-open flag to skip browser opening
3. Check system resources (CPU/RAM usage)
```

### Issue: Optimization shows 0% savings
```
Reasons:
1. Data structure already efficient
2. Mostly lists/dicts (unhashable, skipped)
3. Very small dataset

This is OK - optimization is still applied but may not show
significant savings for certain data structures.
```

## Testing Checklist

- [ ] Generate 100K dataset: `python tests/stress_testing/generate_100k_stress_test.py`
- [ ] Verify file created: `ls tests/stress_testing/STRESS-100K.json`
- [ ] Run performance test: `python tests/stress_testing/stress_test_performance.py --data-file tests/stress_testing/STRESS-100K.json`
- [ ] Check memory reduction: Should see 30-50% savings
- [ ] Generate map: `python src/Beta_VH_Map.py --data-file tests/stress_testing/STRESS-100K.json --no-open`
- [ ] Verify output: Check `dist/VH-Map.html` exists and is valid
- [ ] Count system files: `ls dist/system_*.html | wc -l` (should show ~100,000)

## Files Reference

### Test Scripts
- `tests/stress_testing/generate_100k_stress_test.py` - Generate massive datasets
- `tests/stress_testing/stress_test_performance.py` - Performance monitoring
- `tests/stress_testing/generate_test_data.py` - Original 500-system test data generator

### Modules Used
- `src/common/optimize_datasets.py` - Optimization functions (500+ lines)
- `src/Beta_VH_Map.py` - Map generation with optimization
- `src/common/paths.py` - Path management

### Output
- `tests/stress_testing/STRESS-*.json` - Generated test datasets
- `dist/VH-Map.html` - Galaxy overview
- `dist/system_*.html` - Individual system views (100K+ files)

## Summary

The Haven Control Room can efficiently handle **100,000+ systems** with automatic memory optimization:

1. **Generate large dataset**: Creates 100,000 unique systems in seconds
2. **Optimize automatically**: `optimize_dataframe()` reduces memory by 30-50%
3. **Generate map**: Produces 100,001 HTML files with moon visualization
4. **Monitor performance**: Real-time memory tracking and statistics

This demonstrates production-ready scalability for large-scale sci-fi universe data.
