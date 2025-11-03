#!/usr/bin/env python3
"""
Migrate data/data.json to the new container schema (top-level map):
{ "_meta": {...}, "<system name>": {name, region, x,y,z, attributes, planets: [...]} }

- Preserves photos/paths as-is
- Drops legacy region placeholder entries
- Backs up the original to data.json.bak if not already

Usage:
    python scripts/migrate_to_systems_map.py
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "data.json"


def main() -> int:
    if not DATA_FILE.exists():
        print("data.json not found:", DATA_FILE)
        return 1
    try:
        raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print("Failed to read data.json:", e)
        return 1

    out_meta: Dict[str, Any] = {"version": "3.0.0"}
    out_map: Dict[str, Any] = {}

    try:
        if isinstance(raw, dict) and isinstance(raw.get("systems"), dict):
            # unwrap to top-level map
            out_meta = raw.get("_meta", out_meta) or out_meta
            for name, it in raw["systems"].items():
                if isinstance(it, dict):
                    cp = dict(it)
                    cp.setdefault("name", name)
                    out_map[name] = cp
            # fall through to write
        # Legacy {_meta, data: [...]}
        if isinstance(raw, dict) and isinstance(raw.get("data"), list):
            out_meta = raw.get("_meta", out_meta) or out_meta
            for it in raw["data"]:
                if not isinstance(it, dict):
                    continue
                if it.get("type") == "region":
                    continue
                name = it.get("name") or f"SYS_{len(out_map)+1}"
                cp = dict(it)
                cp.pop("type", None)
                out_map[name] = cp
        # Heuristic: dict map { name: {x,y,z..} }
        elif isinstance(raw, dict):
            vals = list(raw.values())
            if vals and all(isinstance(v, dict) for v in vals) and any(("x" in v or "y" in v or "z" in v or "planets" in v) for v in vals):
                out_meta = raw.get("_meta", out_meta) or out_meta
                for name, it in raw.items():
                    if not isinstance(it, dict):
                        continue
                    cp = dict(it)
                    cp.setdefault("name", name)
                    out_map[name] = cp
            else:
                # region map { region: [ systems ] }
                for region, arr in raw.items():
                    if not isinstance(arr, list):
                        continue
                    for it in arr:
                        if not isinstance(it, dict):
                            continue
                        cp = dict(it)
                        cp.setdefault("region", region)
                        if cp.get("type") == "region":
                            continue
                        name = cp.get("name") or f"SYS_{len(out_map)+1}"
                        out_map[name] = cp
        else:
            print("Unrecognized format; aborting.")
            return 2

        # Backup then write
        bk = DATA_FILE.with_suffix(".json.bak")
        if not bk.exists():
            bk.write_text(DATA_FILE.read_text(encoding="utf-8"), encoding="utf-8")
        # Compose final as top-level map with _meta
        final = {"_meta": out_meta}
        final.update(out_map)
        DATA_FILE.write_text(json.dumps(final, indent=2), encoding="utf-8")
        print(f"Migrated {len(out_map)} system(s) to new container format (top-level map).")
        return 0
    except Exception as e:
        print("Migration error:", e)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
