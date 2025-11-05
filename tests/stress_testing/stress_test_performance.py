#!/usr/bin/env python3
"""
Stress Test Performance Monitor - Demonstrates optimize_dataframe() effectiveness
Compares memory usage before and after optimization on large datasets.

This script:
1. Generates or loads a large dataset (100K systems)
2. Measures memory without optimization
3. Applies optimize_dataframe()
4. Measures memory with optimization
5. Reports memory savings and performance impact

Usage:
    python tests/stress_testing/stress_test_performance.py
    python tests/stress_testing/stress_test_performance.py --data-file tests/stress_testing/STRESS-100K.json
    python tests/stress_testing/stress_test_performance.py --generate-only
"""
import json
import sys
import tracemalloc
from pathlib import Path
from typing import Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

import pandas as pd
from common.optimize_datasets import optimize_dataframe
from common.paths import data_path


def format_bytes(bytes_val: float) -> str:
    """Format bytes as human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.2f} TB"


def get_dataframe_memory(df: pd.DataFrame) -> int:
    """Get memory usage of a DataFrame in bytes."""
    return df.memory_usage(deep=True).sum()


def normalize_record(record: dict, region: str = None) -> dict:
    """Normalize a system record (same as Beta_VH_Map.py)."""
    r = dict(record)
    # Map coordinate fields
    if "x_cords" in r and "x" not in r:
        r["x"] = r.pop("x_cords")
    if "y_cords" in r and "y" not in r:
        r["y"] = r.pop("y_cords")
    if "z_cords" in r and "z" not in r:
        r["z"] = r.pop("z_cords")
    # Map other legacy fields
    if "fauna #" in r and "fauna" not in r:
        r["fauna"] = r.pop("fauna #")
    if "flura #" in r and "flora" not in r:
        r["flora"] = r.pop("flura #")
    if "Sentinel level" in r and "sentinel" not in r:
        r["sentinel"] = r.pop("Sentinel level")
    if "Materials" in r and "materials" not in r:
        r["materials"] = r.pop("Materials")
    if "Base location" in r and "base_location" not in r:
        r["base_location"] = r.pop("Base location")
    # Set defaults
    r.setdefault("id", None)
    r.setdefault("name", r.get("name"))
    r.setdefault("planets", r.get("planets", []))
    if region is not None:
        r["region"] = region
    else:
        r.setdefault("region", r.get("region", "Unknown"))
    return r


def load_systems_unoptimized(data_file: Path) -> pd.DataFrame:
    """Load systems WITHOUT optimization (for comparison)."""
    try:
        raw = json.loads(data_file.read_text(encoding="utf-8"))
    except Exception as e:
        raise ValueError(f"Failed to read {data_file}: {e}")
    
    records = []
    
    # Support multiple formats
    if isinstance(raw, dict) and "systems" in raw and isinstance(raw["systems"], dict):
        for name, item in raw["systems"].items():
            if isinstance(item, dict):
                it = dict(item)
                it.setdefault("name", name)
                records.append(normalize_record(it))
    elif isinstance(raw, dict) and "data" in raw and isinstance(raw["data"], list):
        for item in raw["data"]:
            records.append(normalize_record(item))
    elif isinstance(raw, dict):
        values = list(raw.values())
        if values and all(isinstance(v, dict) for v in values) and any(
            ("x" in v or "y" in v or "z" in v or "planets" in v) for v in values
        ):
            for name, item in raw.items():
                if name == "_meta" or (isinstance(name, str) and name.startswith("_")):
                    continue
                if isinstance(item, dict):
                    it = dict(item)
                    it.setdefault("name", name)
                    records.append(normalize_record(it))
    
    df = pd.DataFrame(records)
    
    # Add columns but DON'T optimize
    for c in ("id", "name", "x", "y", "z", "region", "fauna", "flora", "sentinel", "materials", "base_location", "planets"):
        if c not in df.columns:
            df[c] = None
    
    df["x"] = pd.to_numeric(df["x"], errors="coerce")
    df["y"] = pd.to_numeric(df["y"], errors="coerce")
    df["z"] = pd.to_numeric(df["z"], errors="coerce")
    
    return df


def run_stress_test(data_file: Path) -> None:
    """Run comprehensive stress test."""
    print("=" * 80)
    print("HAVEN CONTROL ROOM - STRESS TEST: optimize_dataframe() Performance")
    print("=" * 80)
    print()
    
    if not data_file.exists():
        print(f"❌ Data file not found: {data_file}")
        print()
        print("Generate a stress test dataset first:")
        print("  python tests/stress_testing/generate_100k_stress_test.py")
        sys.exit(1)
    
    file_size_mb = data_file.stat().st_size / (1024 * 1024)
    print(f"📊 Data File: {data_file.name}")
    print(f"   Size: {file_size_mb:.1f} MB")
    print()
    
    # ========================================================================
    # PHASE 1: Load WITHOUT optimization
    # ========================================================================
    print("Phase 1: Loading data WITHOUT optimization...")
    print("   (Measuring baseline memory usage)")
    print()
    
    tracemalloc.start()
    df_unoptimized = load_systems_unoptimized(data_file)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    mem_unoptimized = get_dataframe_memory(df_unoptimized)
    num_systems = len(df_unoptimized)
    
    print(f"   ✓ Loaded {num_systems:,} systems")
    print(f"   ✓ DataFrame memory: {format_bytes(mem_unoptimized)}")
    print(f"   ✓ Peak allocation: {format_bytes(peak)}")
    print()
    
    # ========================================================================
    # PHASE 2: Load WITH optimization
    # ========================================================================
    print("Phase 2: Loading data WITH optimize_dataframe()...")
    print("   (Measuring optimized memory usage)")
    print()
    
    tracemalloc.start()
    df_optimized = load_systems_unoptimized(data_file)
    df_optimized = optimize_dataframe(df_optimized)  # APPLY OPTIMIZATION
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    mem_optimized = get_dataframe_memory(df_optimized)
    
    print(f"   ✓ Loaded {num_systems:,} systems")
    print(f"   ✓ DataFrame memory: {format_bytes(mem_optimized)}")
    print(f"   ✓ Peak allocation: {format_bytes(peak)}")
    print()
    
    # ========================================================================
    # RESULTS
    # ========================================================================
    print("=" * 80)
    print("RESULTS - optimize_dataframe() Effectiveness")
    print("=" * 80)
    print()
    
    memory_saved = mem_unoptimized - mem_optimized
    reduction_pct = (memory_saved / mem_unoptimized) * 100
    
    print(f"📈 Memory Statistics:")
    print(f"   Before optimization: {format_bytes(mem_unoptimized)}")
    print(f"   After optimization:  {format_bytes(mem_optimized)}")
    print(f"   Memory saved:        {format_bytes(memory_saved)} ({reduction_pct:.1f}%)")
    print()
    
    if reduction_pct > 0:
        print(f"✅ OPTIMIZATION EFFECTIVE!")
        print(f"   Successfully reduced memory usage by {reduction_pct:.1f}%")
        print(f"   Equivalent to: {format_bytes(memory_saved)}")
    else:
        print(f"⚠️  No memory reduction detected (data structure may not benefit)")
    
    print()
    print("📊 Per-System Memory:")
    mem_per_system_before = mem_unoptimized / num_systems
    mem_per_system_after = mem_optimized / num_systems
    print(f"   Before: {format_bytes(mem_per_system_before)} per system")
    print(f"   After:  {format_bytes(mem_per_system_after)} per system")
    print()
    
    # ========================================================================
    # DTYPE ANALYSIS
    # ========================================================================
    print("📋 Data Type Analysis:")
    print()
    
    # Show dtypes for unoptimized
    print("   Unoptimized dtypes:")
    for col in df_unoptimized.columns[:10]:  # First 10 columns
        print(f"      {col}: {df_unoptimized[col].dtype}")
    
    print()
    
    # Show dtypes for optimized
    print("   Optimized dtypes:")
    for col in df_optimized.columns[:10]:
        print(f"      {col}: {df_optimized[col].dtype}")
    
    print()
    print("=" * 80)
    print("✅ Stress Test Complete!")
    print("=" * 80)
    print()
    print("Key Findings:")
    print(f"  • {num_systems:,} systems processed")
    print(f"  • Memory reduction: {reduction_pct:.1f}%")
    print(f"  • Optimization function: optimize_dataframe()")
    print(f"  • Module: src/common/optimize_datasets.py")
    print()


if __name__ == "__main__":
    # Parse args
    data_file = data_path("data.json")
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--help" or arg == "-h":
            print(__doc__)
            sys.exit(0)
        elif arg.startswith("--data-file"):
            if "=" in arg:
                data_file = Path(arg.split("=")[1])
            elif len(sys.argv) > 2:
                data_file = Path(sys.argv[2])
    
    try:
        run_stress_test(data_file)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
