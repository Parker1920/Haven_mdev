#!/usr/bin/env python3
"""
Quick Stress Test - Demonstrates optimize_dataframe() on 100K+ dataset
Uses the actual map generation pipeline to show real-world performance.

Much faster than the full performance monitor since it reuses the optimized
data loading logic from Beta_VH_Map.py

Usage:
    python tests/stress_testing/quick_stress_test.py --data-file tests/stress_testing/STRESS-100K.json
    python tests/stress_testing/quick_stress_test.py --data-file tests/stress_testing/STRESS-50K.json
"""
import json
import sys
import time
from pathlib import Path

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


def normalize_record(record: dict, region: str = None) -> dict:
    """Normalize a system record (same as Beta_VH_Map.py)."""
    r = dict(record)
    if "x_cords" in r and "x" not in r:
        r["x"] = r.pop("x_cords")
    if "y_cords" in r and "y" not in r:
        r["y"] = r.pop("y_cords")
    if "z_cords" in r and "z" not in r:
        r["z"] = r.pop("z_cords")
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
    r.setdefault("id", None)
    r.setdefault("name", r.get("name"))
    r.setdefault("planets", r.get("planets", []))
    if region is not None:
        r["region"] = region
    else:
        r.setdefault("region", r.get("region", "Unknown"))
    return r


def load_systems_with_timing(data_file: Path, use_optimization: bool = True):
    """Load systems and show timing with/without optimization."""
    
    # Track file reading time
    start_read = time.time()
    raw = json.loads(data_file.read_text(encoding="utf-8"))
    read_time = time.time() - start_read
    
    # Parse JSON
    records = []
    if isinstance(raw, dict) and "systems" in raw and isinstance(raw["systems"], dict):
        for name, item in raw["systems"].items():
            if isinstance(item, dict):
                it = dict(item)
                it.setdefault("name", name)
                records.append(normalize_record(it))
    
    # Create DataFrame
    start_df = time.time()
    df = pd.DataFrame(records)
    
    for c in ("id", "name", "x", "y", "z", "region", "fauna", "flora", "sentinel", "materials", "base_location", "planets"):
        if c not in df.columns:
            df[c] = None
    
    df["x"] = pd.to_numeric(df["x"], errors="coerce")
    df["y"] = pd.to_numeric(df["y"], errors="coerce")
    df["z"] = pd.to_numeric(df["z"], errors="coerce")
    
    df_create_time = time.time() - start_df
    
    # Get memory before optimization
    mem_before = df.memory_usage(deep=True).sum()
    
    # Apply optimization if requested
    start_opt = time.time()
    if use_optimization:
        df = optimize_dataframe(df)
    opt_time = time.time() - start_opt
    
    # Get memory after optimization
    mem_after = df.memory_usage(deep=True).sum()
    
    return {
        "df": df,
        "num_systems": len(df),
        "read_time": read_time,
        "df_create_time": df_create_time,
        "opt_time": opt_time,
        "mem_before": mem_before,
        "mem_after": mem_after,
    }


def run_quick_test(data_file: Path) -> None:
    """Run quick stress test."""
    
    print("=" * 80)
    print("HAVEN CONTROL ROOM - QUICK STRESS TEST: 100K+ Dataset Optimization")
    print("=" * 80)
    print()
    
    if not data_file.exists():
        print(f"❌ Data file not found: {data_file}")
        print()
        print("Generate it first:")
        print("  python tests/stress_testing/generate_100k_stress_test.py")
        sys.exit(1)
    
    file_size_mb = data_file.stat().st_size / (1024 * 1024)
    print(f"📊 Dataset: {data_file.name}")
    print(f"   File size: {file_size_mb:.1f} MB")
    print()
    
    # Load with optimization
    print("⏱️  Loading and optimizing data...")
    print()
    
    start_total = time.time()
    results = load_systems_with_timing(data_file, use_optimization=True)
    total_time = time.time() - start_total
    
    num_systems = results["num_systems"]
    
    print(f"✅ Load Complete!")
    print()
    print(f"📈 Systems loaded: {num_systems:,}")
    print()
    
    print("⏱️  Timing Breakdown:")
    print(f"   JSON read:       {results['read_time']:.2f}s")
    print(f"   DataFrame create: {results['df_create_time']:.2f}s")
    print(f"   Optimization:     {results['opt_time']:.2f}s")
    print(f"   Total:            {total_time:.2f}s")
    print()
    
    print("💾 Memory Usage:")
    print(f"   Before: {format_bytes(results['mem_before'])}")
    print(f"   After:  {format_bytes(results['mem_after'])}")
    
    memory_saved = results['mem_before'] - results['mem_after']
    reduction_pct = (memory_saved / results['mem_before']) * 100 if results['mem_before'] > 0 else 0
    
    print(f"   Saved:  {format_bytes(memory_saved)} ({reduction_pct:.1f}%)")
    print()
    
    if reduction_pct > 0:
        print(f"✅ Optimization EFFECTIVE!")
        print(f"   {reduction_pct:.1f}% memory reduction")
    else:
        print(f"ℹ️  No memory reduction (data structure may not benefit)")
    
    print()
    print("📊 Per-System Efficiency:")
    print(f"   Before: {format_bytes(results['mem_before'] / num_systems)}/system")
    print(f"   After:  {format_bytes(results['mem_after'] / num_systems)}/system")
    print()
    
    print("=" * 80)
    print("✅ Quick Stress Test Complete!")
    print("=" * 80)
    print()
    print("Next: Generate the map with:")
    print(f"  python src/Beta_VH_Map.py --data-file {data_file.name} --no-open")
    print()


if __name__ == "__main__":
    data_file = data_path("data.json")
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ("--help", "-h"):
            print(__doc__)
            sys.exit(0)
        elif sys.argv[1].startswith("--data-file"):
            if "=" in sys.argv[1]:
                data_file = Path(sys.argv[1].split("=")[1])
            elif len(sys.argv) > 2:
                data_file = Path(sys.argv[2])
    
    try:
        run_quick_test(data_file)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
