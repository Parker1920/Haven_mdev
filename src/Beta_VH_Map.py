"""Beta VH Map - Three.js-based interactive 3D star map visualization.

Fully data-driven architecture: reads all object types and properties from data.json
and renders them with professional 3D effects.

Creates two views:
- Galaxy View: Shows region centroids, click to explore
- System View: Shows individual systems within a region

Usage:
    python Beta_VH_Map.py            # generate plot.html and open it
    python Beta_VH_Map.py --out my.html
    python Beta_VH_Map.py --no-open
"""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from common.paths import data_path, logs_dir, dist_dir

def _setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    # File handler
    try:
        log_dir = logs_dir()
        log_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime('%Y-%m-%d')
        fh = RotatingFileHandler(log_dir / f'map-{ts}.log', maxBytes=2_000_000, backupCount=5, encoding='utf-8')
        logging.getLogger().addHandler(fh)
    except Exception:
        # If logging to file fails, continue with console only
        pass

_setup_logging()

import argparse
import json
import math
import shutil
import subprocess
import webbrowser
from typing import List, Optional
from pathlib import Path

import pandas as pd


# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_FILE = data_path("data.json")


# ============================================================================
# DATA LOADING AND NORMALIZATION (Same as before)
# ============================================================================

def normalize_record(record: dict, region: Optional[str] = None) -> dict:
    """Normalize a system record by mapping legacy field names to standard names."""
    """
    Normalize a system record by mapping legacy field names to standard names.
    Args:
        record: The system or region record as a dict.
        region: Optional region name to override.
    Returns:
        Normalized record dict.
    """
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
    # Set region (override if provided)
    if region is not None:
        r["region"] = region
    else:
        r.setdefault("region", r.get("region", "Unknown"))
    return r


def load_systems(path: Path = DATA_FILE) -> pd.DataFrame:
    """
    Load systems from the data file, supporting new and legacy formats.
    Args:
        path: Path to the data.json file.
    Returns:
        DataFrame of normalized system/region records.
    Raises:
        ValueError: If the JSON format is not supported.
    """
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        logging.error(f"Failed to read or parse {path}: {e}")
        raise
    records = []
    # Support formats in order of preference:
    # 1) New container map: { systems: { <systemName>: {name, region, x,y,z, planets: [...] } } }
    # 2) New container map without wrapper: { <systemName>: { ... } }
    # 3) Legacy list wrapper: { _meta, data: [ ... ] }
    # 4) Legacy region map: { <regionName>: [ { ...system... }, ... ] }
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
        # Heuristic: if values look like system objects (dicts with any of x/y/z/planets), treat as system map
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
        else:
            # Assume legacy region map
            for region, items in raw.items():
                for item in items:
                    records.append(normalize_record(item, region=region))
    elif isinstance(raw, list):
        for item in raw:
            records.append(normalize_record(item))
    else:
        logging.error("Unsupported JSON format for systems")
        raise ValueError("Unsupported JSON format for systems")
    df = pd.DataFrame(records)
    for c in ("id", "name", "x", "y", "z", "region", "fauna", "flora", "sentinel", "materials", "base_location", "planets"):
        if c not in df.columns:
            df[c] = None
    df["x"] = pd.to_numeric(df["x"], errors="coerce")
    df["y"] = pd.to_numeric(df["y"], errors="coerce")
    df["z"] = pd.to_numeric(df["z"], errors="coerce")
    logging.info(f"Loaded {len(df)} records from {path}")
    return df


def safe_filename(s: str) -> str:
    return "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in (s or "")).strip().replace(" ", "_")


def cartesian_to_orbital(x: float, y: float, z: float):
    """Convert cartesian coordinates to orbital positions."""
    radius = math.sqrt(x**2 + y**2 + z**2)
    if radius < 0.01:
        return 0.1, 0, 0
    theta = math.atan2(y, x)
    phi = math.acos(z / radius) if radius > 0 else 0
    return (
        radius * math.sin(phi) * math.cos(theta),
        radius * math.sin(phi) * math.sin(theta),
        radius * math.cos(phi)
    )


# ============================================================================
# THREE.JS HTML TEMPLATE
# ============================================================================

THREEJS_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Haven Galaxy - 3D Star Map</title>
    <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Rajdhani', sans-serif;
            background: radial-gradient(ellipse at center, #1a1a2e 0%, #0f0f1e 50%, #000000 100%);
            overflow: hidden;
            animation: fadeIn 0.8s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        #canvas-container {
            width: 100vw;
            height: 100vh;
            position: relative;
        }
        
        /* Loading overlay */
        #loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.95);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            animation: fadeOut 0.5s ease-out 2s forwards;
        }
        
        @keyframes fadeOut {
            to {
                opacity: 0;
                pointer-events: none;
            }
        }
        
        .spinner {
            width: 60px;
            height: 60px;
            border: 4px solid rgba(0, 206, 209, 0.2);
            border-top-color: rgba(0, 206, 209, 1);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        #loading-overlay p {
            color: rgba(0, 206, 209, 1);
            margin-top: 20px;
            font-size: 18px;
            font-weight: 500;
            letter-spacing: 2px;
        }
        
        /* Title overlay */
        #title-overlay {
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 20, 40, 0.85);
            padding: 12px 40px;
            border: 2px solid rgba(0, 206, 209, 0.5);
            border-radius: 4px;
            box-shadow: 0 0 20px rgba(0, 206, 209, 0.3);
            z-index: 100;
            backdrop-filter: blur(10px);
        }
        
        #title-overlay h1 {
            margin: 0;
            font-size: 28px;
            font-weight: 600;
            color: rgba(0, 206, 209, 1);
            text-shadow: 0 0 10px rgba(0, 206, 209, 0.5);
            letter-spacing: 2px;
        }
        
        /* Info panel */
        #info-panel {
            position: fixed;
            top: 100px;
            right: 20px;
            background: rgba(0, 20, 40, 0.92);
            padding: 20px;
            border-radius: 8px;
            border: 2px solid rgba(0, 206, 209, 0.4);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(10px);
            z-index: 100;
            max-width: 320px;
            max-height: calc(100vh - 140px);
            overflow-y: auto;
            color: #e0e0e0;
        }
        
        #info-panel h3 {
            color: rgba(0, 206, 209, 1);
            font-size: 20px;
            margin-bottom: 15px;
            text-shadow: 0 0 10px rgba(0, 206, 209, 0.5);
            border-bottom: 2px solid rgba(0, 206, 209, 0.3);
            padding-bottom: 10px;
        }
        
        #info-panel p {
            margin: 8px 0;
            line-height: 1.6;
        }
        
        #info-panel strong {
            color: rgba(0, 206, 209, 0.9);
        }
        
        /* Legend */
        #legend {
            position: fixed;
            bottom: 30px;
            left: 30px;
            background: rgba(0, 20, 40, 0.85);
            padding: 15px 20px;
            border-radius: 8px;
            border: 1px solid rgba(0, 206, 209, 0.3);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(10px);
            z-index: 100;
        }
        
        #legend h4 {
            margin: 0 0 10px 0;
            color: rgba(0, 206, 209, 1);
            font-size: 16px;
            font-weight: 600;
            letter-spacing: 1px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            margin: 6px 0;
            color: #e0e0e0;
        }
        
        .legend-icon {
            width: 20px;
            height: 20px;
            margin-right: 12px;
            border-radius: 50%;
            box-shadow: 0 0 10px currentColor;
        }
        
        .legend-icon.system {
            background: radial-gradient(circle, rgba(0, 255, 255, 1) 0%, rgba(0, 206, 209, 0.6) 100%);
        }
        
        .legend-icon.moon {
            background: radial-gradient(circle, rgba(200, 200, 220, 1) 0%, rgba(150, 150, 170, 0.6) 100%);
        }
        
        .legend-icon.station {
            background: radial-gradient(circle, rgba(218, 112, 214, 1) 0%, rgba(148, 0, 211, 0.6) 100%);
            border-radius: 2px;
        }
        
        .legend-icon.sun {
            background: radial-gradient(circle, rgba(255, 215, 0, 1) 0%, rgba(255, 140, 0, 0.6) 100%);
        }
        
        /* Controls hint */
        #controls-hint {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: rgba(0, 20, 40, 0.85);
            padding: 12px 18px;
            border-radius: 6px;
            border: 1px solid rgba(0, 206, 209, 0.3);
            z-index: 10000;
            color: rgba(0, 206, 209, 0.9);
            font-size: 14px;
            backdrop-filter: blur(10px);
        }
        
        #controls-hint div {
            margin: 4px 0;
        }
        
        /* Hover tooltip */
        #hover-tooltip {
            position: fixed;
            top: 0; left: 0;
            display: none;
            padding: 10px 14px;
            background: rgba(0, 20, 40, 0.95);
            color: #e0ffff;
            border: 1px solid rgba(0, 206, 209, 0.5);
            border-radius: 8px;
            font-size: 13px;
            line-height: 1.6;
            z-index: 10001;
            pointer-events: none;
            box-shadow: 0 6px 16px rgba(0,0,0,0.7);
            backdrop-filter: blur(8px);
            max-width: 280px;
        }

        #hover-tooltip .tooltip-title {
            font-weight: bold;
            font-size: 14px;
            color: #00CED1;
            margin-bottom: 6px;
            border-bottom: 1px solid rgba(0, 206, 209, 0.3);
            padding-bottom: 4px;
        }

        #hover-tooltip .tooltip-line {
            margin: 3px 0;
            color: #b0e0e6;
        }

        #hover-tooltip .tooltip-label {
            color: #7eb8bb;
            font-size: 11px;
        }

        /* Settings Panel */
        #settings-backdrop {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            z-index: 9998;
            display: none;
            opacity: 0;
            transition: opacity 0.3s ease;
            backdrop-filter: blur(4px);
        }

        #settings-backdrop.show {
            display: block;
            opacity: 1;
        }

        #settings-panel {
            position: fixed;
            top: 0;
            right: -400px;
            width: 380px;
            height: 100%;
            background: rgba(10, 20, 35, 0.98);
            border-left: 2px solid rgba(0, 206, 209, 0.5);
            z-index: 9999;
            overflow-y: auto;
            transition: right 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: -4px 0 20px rgba(0, 0, 0, 0.8);
        }

        #settings-panel.open {
            right: 0;
        }

        #settings-panel .settings-header {
            padding: 24px 20px;
            border-bottom: 1px solid rgba(0, 206, 209, 0.3);
            background: rgba(0, 206, 209, 0.08);
        }

        #settings-panel .settings-header h2 {
            margin: 0;
            color: #00CED1;
            font-family: 'Rajdhani', sans-serif;
            font-size: 24px;
            font-weight: 700;
            letter-spacing: 2px;
        }

        #settings-panel .settings-section {
            padding: 20px;
            border-bottom: 1px solid rgba(0, 206, 209, 0.15);
        }

        #settings-panel .settings-section h3 {
            margin: 0 0 16px 0;
            color: #7eb8bb;
            font-family: 'Rajdhani', sans-serif;
            font-size: 16px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        #settings-panel .setting-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 12px 0;
            padding: 10px;
            background: rgba(0, 206, 209, 0.05);
            border-radius: 6px;
            transition: background 0.2s ease;
        }

        #settings-panel .setting-item:hover {
            background: rgba(0, 206, 209, 0.1);
        }

        #settings-panel .setting-label {
            color: #b0e0e6;
            font-family: 'Rajdhani', sans-serif;
            font-size: 14px;
        }

        #settings-panel .setting-toggle {
            position: relative;
            width: 50px;
            height: 26px;
            background: rgba(100, 100, 100, 0.4);
            border-radius: 13px;
            cursor: pointer;
            transition: background 0.3s ease;
        }

        #settings-panel .setting-toggle.active {
            background: rgba(0, 206, 209, 0.6);
        }

        #settings-panel .setting-toggle-slider {
            position: absolute;
            top: 3px;
            left: 3px;
            width: 20px;
            height: 20px;
            background: white;
            border-radius: 50%;
            transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
        }

        #settings-panel .setting-toggle.active .setting-toggle-slider {
            left: 27px;
        }

        #settings-panel .settings-footer {
            padding: 20px;
            display: flex;
            gap: 12px;
        }

        #settings-panel .btn-settings {
            flex: 1;
            padding: 12px 20px;
            border: none;
            border-radius: 6px;
            font-family: 'Rajdhani', sans-serif;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        #settings-panel .btn-save {
            background: rgba(0, 206, 209, 0.8);
            color: #0a0a14;
        }

        #settings-panel .btn-save:hover {
            background: rgba(0, 206, 209, 1);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 206, 209, 0.4);
        }

        #settings-panel .btn-cancel {
            background: rgba(100, 100, 100, 0.4);
            color: #b0e0e6;
        }

        #settings-panel .btn-cancel:hover {
            background: rgba(100, 100, 100, 0.6);
        }

        #btn-settings {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: rgba(0, 20, 40, 0.85);
            color: rgba(0, 206, 209, 1);
            border: 1px solid rgba(0, 206, 209, 0.4);
            padding: 10px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-family: 'Rajdhani', sans-serif;
            letter-spacing: 1px;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s ease;
        }

        #btn-settings:hover {
            background: rgba(0, 206, 209, 0.2);
            border-color: rgba(0, 206, 209, 0.8);
            transform: translateY(-1px);
        }

        /* Download logs button */
        #download-logs {
            position: fixed;
            right: 20px;
            bottom: 20px;
            z-index: 110;
            background: rgba(0, 20, 40, 0.85);
            color: rgba(0, 206, 209, 1);
            border: 1px solid rgba(0, 206, 209, 0.4);
            padding: 10px 14px;
            border-radius: 6px;
            cursor: pointer;
            font-family: 'Rajdhani', sans-serif;
            letter-spacing: 1px;
        }
    </style>
</head>
<body>
    <!-- Loading overlay -->
    <div id="loading-overlay">
        <div class="spinner"></div>
        <p>INITIALIZING GALAXY MAP...</p>
    </div>
    
    <!-- Title -->
    <div id="title-overlay">
        <h1 id="view-title">HAVEN GALAXY - 3D STAR MAP</h1>
    </div>
    
    <!-- Back button (shown in System View) -->
    <button id="back-btn" style="display: none; position: fixed; top: 10px; left: 10px; padding: 10px 20px; background: rgba(0, 206, 209, 0.2); color: rgba(0, 206, 209, 1); border: 2px solid rgba(0, 206, 209, 0.6); border-radius: 4px; font-family: 'Rajdhani', sans-serif; font-weight: 600; font-size: 16px; z-index: 1000; cursor: pointer; backdrop-filter: blur(10px);">← Back to Galaxy View</button>
    <button id="download-logs" title="Download browser logs">Download Logs</button>

    <!-- Settings button -->
    <button id="btn-settings">⚙️ Settings</button>

    <!-- Settings backdrop -->
    <div id="settings-backdrop"></div>

    <!-- Settings panel -->
    <div id="settings-panel">
        <div class="settings-header">
            <h2>⚙️ VIEW SETTINGS</h2>
        </div>

        <div class="settings-section">
            <h3>UI Visibility</h3>
            <div class="setting-item">
                <span class="setting-label">Show Legend</span>
                <div class="setting-toggle active" data-setting="showLegend">
                    <div class="setting-toggle-slider"></div>
                </div>
            </div>
            <div class="setting-item">
                <span class="setting-label">Show Info Panel</span>
                <div class="setting-toggle active" data-setting="showInfoPanel">
                    <div class="setting-toggle-slider"></div>
                </div>
            </div>
            <div class="setting-item">
                <span class="setting-label">Show Compass & Scale</span>
                <div class="setting-toggle active" data-setting="showCompass">
                    <div class="setting-toggle-slider"></div>
                </div>
            </div>
        </div>

        <div class="settings-footer">
            <button class="btn-settings btn-cancel" id="btn-settings-cancel">Cancel</button>
            <button class="btn-settings btn-save" id="btn-settings-save">Save</button>
        </div>
    </div>
    
    <!-- Info panel -->
    <div id="info-panel">
        <h3>System Information</h3>
        <p id="info-content">Click on a system to see details</p>
    </div>
    
    <!-- Legend (dynamically populated) -->
    <div id="legend">
        <h4>LEGEND</h4>
        <div id="legend-items"></div>
    </div>
    
    <!-- HUD container: controls, compass, scale -->
    <div id="controls-hint">
        <div style="display:flex; gap:8px; align-items:center; justify-content:space-between;">
            <div style="display:flex; gap:8px;">
                <button id="btn-controls" style="background:#0a0a14; color:#00CED1; border:1px solid #00CED1; padding:4px 8px; border-radius:4px; cursor:pointer;">Controls</button>
                <button id="btn-grid" style="background:#0a0a14; color:#00CED1; border:1px solid #00CED1; padding:4px 8px; border-radius:4px; cursor:pointer;">Grid: On</button>
                <button id="btn-screenshot" style="background:#0a0a14; color:#00CED1; border:1px solid #00CED1; padding:4px 8px; border-radius:4px; cursor:pointer;">Screenshot</button>
            </div>
        </div>
        <div id="controls-panel" style="display:none; margin-top:8px; border-top:1px solid rgba(0,206,209,0.2); padding-top:8px;">
            <div style="display:flex; gap:12px; align-items:center; flex-wrap: wrap;">
                <label style="display:flex; align-items:center; gap:4px;">
                    <input id="toggle-autorotate" type="checkbox" /> Auto-rotate
                </label>
                <label style="display:flex; align-items:center; gap:4px;">
                    <input id="toggle-stats" type="checkbox" /> Stats
                </label>
                <button id="btn-labels" style="background:#0a0a14; color:#00CED1; border:1px solid #00CED1; padding:4px 8px; border-radius:4px; cursor:pointer;">Labels: Off</button>
                <button id="btn-regions" style="background:#0a0a14; color:#00CED1; border:1px solid #00CED1; padding:4px 8px; border-radius:4px; cursor:pointer;">Regions: Off</button>
            </div>
        </div>
        <div style="display:flex; gap:10px; align-items:center; margin-top:8px;">
            <canvas id="compass-canvas" width="64" height="64" style="background: rgba(0, 20, 40, 0.35); border: 1px solid rgba(0,206,209,0.3); border-radius:6px;"></canvas>
            <div id="scale-text" style="color:#00CED1; font-family: Rajdhani, sans-serif; font-size:12px; background: rgba(0, 20, 40, 0.35); border: 1px solid rgba(0,206,209,0.3); padding:6px 10px; border-radius:6px;">Scale: major grid = …</div>
        </div>
    </div>
    
    <!-- Hover tooltip -->
    <div id="hover-tooltip"></div>
    
    <!-- Canvas container -->
    <div id="canvas-container"></div>
    
    <!-- Three.js library -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <!-- Optional stats.js -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/stats.js/r17/Stats.min.js"></script>
    
    <script>
        // Browser-side diagnostics: capture console and errors, bind Download Logs button
        (function(){
            const logs = [];
            const meta = {
                tsStart: new Date().toISOString(),
                userAgent: navigator.userAgent,
                url: location.href
            };
            function ts(){ return new Date().toISOString(); }
            const orig = {
                log: console.log,
                warn: console.warn,
                error: console.error,
                info: console.info,
                debug: console.debug
            };
            ['log','warn','error','info','debug'].forEach(level => {
                console[level] = function(...args){
                    try {
                        const msg = args.map(a => {
                            try {
                                if (a instanceof Error) { return a.stack || a.message; }
                                return typeof a === 'string' ? a : JSON.stringify(a, null, 2);
                            } catch { return String(a); }
                        }).join(' ');
                        logs.push({ t: ts(), level, msg });
                    } catch {}
                    return orig[level].apply(console, args);
                };
            });
            window.addEventListener('error', function(e){
                try { logs.push({ t: ts(), level: 'error', msg: `Uncaught: ${e.message} at ${e.filename}:${e.lineno}:${e.colno}` }); } catch {}
            });
            window.addEventListener('unhandledrejection', function(e){
                try {
                    const reason = e.reason;
                    const msg = reason && (reason.stack || reason.message || String(reason));
                    logs.push({ t: ts(), level: 'error', msg: 'Unhandled promise rejection: ' + (msg || '') });
                } catch {}
            });
            function download(){
                const header = [
                    'Haven Galaxy Map - Browser Diagnostics',
                    `Started: ${meta.tsStart}`,
                    `View: ${typeof VIEW_MODE !== 'undefined' ? VIEW_MODE : 'unknown'}`,
                    `Region: ${typeof REGION_NAME !== 'undefined' ? REGION_NAME : ''}`,
                    `User-Agent: ${meta.userAgent}`,
                    `URL: ${meta.url}`,
                    ''
                ].join('\n');
                const body = logs.map(l => `[${l.t}] ${l.level.toUpperCase()}: ${l.msg}`).join('\n');
                const blob = new Blob([header, body], {type: 'text/plain;charset=utf-8'});
                const a = document.createElement('a');
                const now = new Date();
                const filename = `browser-logs_${typeof VIEW_MODE !== 'undefined' ? VIEW_MODE : 'map'}_${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}_${String(now.getHours()).padStart(2,'0')}${String(now.getMinutes()).padStart(2,'0')}${String(now.getSeconds()).padStart(2,'0')}.txt`;
                a.href = URL.createObjectURL(blob);
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 0);
            }
            window.__HAVEN_BROWSER_LOGS__ = { logs, download };
            window.addEventListener('DOMContentLoaded', () => {
                try {
                    const btn = document.getElementById('download-logs');
                    if (btn) btn.addEventListener('click', download);
                } catch {}
            });
        })();

    // Data injected by Python
    const SYSTEM_DATA = __SYSTEM_DATA__;
    const VIEW_MODE = '__VIEW_MODE__';  // 'galaxy' or 'system'
    const REGION_NAME = '__REGION_NAME__';
    const SYSTEM_META = __SYSTEM_META__;

        // ========== Settings Management ==========
        const SETTINGS_KEY = 'havenMapSettings';
        let uiSettings = {
            showLegend: true,
            showInfoPanel: true,
            showCompass: true
        };

        // Load settings from localStorage
        function loadSettings() {
            try {
                const saved = localStorage.getItem(SETTINGS_KEY);
                if (saved) {
                    uiSettings = { ...uiSettings, ...JSON.parse(saved) };
                }
            } catch (e) {
                console.warn('Failed to load settings:', e);
            }
        }

        // Save settings to localStorage
        function saveSettings() {
            try {
                localStorage.setItem(SETTINGS_KEY, JSON.stringify(uiSettings));
            } catch (e) {
                console.warn('Failed to save settings:', e);
            }
        }

        // Apply settings to UI
        function applySettings() {
            const legend = document.getElementById('legend');
            const infoPanel = document.getElementById('info-panel');
            const controlsHint = document.getElementById('controls-hint');

            if (legend) legend.style.display = uiSettings.showLegend ? 'block' : 'none';
            if (infoPanel) infoPanel.style.display = uiSettings.showInfoPanel ? 'block' : 'none';
            if (controlsHint) controlsHint.style.display = uiSettings.showCompass ? 'block' : 'none';
        }

        // Initialize settings on page load
        loadSettings();

        // Settings panel controls
        window.addEventListener('DOMContentLoaded', () => {
            const settingsBtn = document.getElementById('btn-settings');
            const settingsPanel = document.getElementById('settings-panel');
            const settingsBackdrop = document.getElementById('settings-backdrop');
            const saveBtn = document.getElementById('btn-settings-save');
            const cancelBtn = document.getElementById('btn-settings-cancel');
            const toggles = document.querySelectorAll('.setting-toggle');

            // Update toggle states from current settings
            function updateToggles() {
                toggles.forEach(toggle => {
                    const setting = toggle.getAttribute('data-setting');
                    if (uiSettings[setting]) {
                        toggle.classList.add('active');
                    } else {
                        toggle.classList.remove('active');
                    }
                });
            }

            // Open settings panel
            function openSettings() {
                updateToggles();
                settingsBackdrop.classList.add('show');
                setTimeout(() => {
                    settingsPanel.classList.add('open');
                }, 10);
            }

            // Close settings panel
            function closeSettings() {
                settingsPanel.classList.remove('open');
                setTimeout(() => {
                    settingsBackdrop.classList.remove('show');
                }, 400);
            }

            // Toggle setting
            toggles.forEach(toggle => {
                toggle.addEventListener('click', () => {
                    const setting = toggle.getAttribute('data-setting');
                    const isActive = toggle.classList.contains('active');

                    if (isActive) {
                        toggle.classList.remove('active');
                        uiSettings[setting] = false;
                    } else {
                        toggle.classList.add('active');
                        uiSettings[setting] = true;
                    }
                });
            });

            // Save and apply settings
            saveBtn.addEventListener('click', () => {
                saveSettings();
                applySettings();
                closeSettings();
            });

            // Cancel without saving
            cancelBtn.addEventListener('click', () => {
                // Reload settings from storage to discard changes
                loadSettings();
                closeSettings();
            });

            // Close on backdrop click
            settingsBackdrop.addEventListener('click', () => {
                loadSettings();
                closeSettings();
            });

            // Open settings button
            settingsBtn.addEventListener('click', openSettings);

            // Apply initial settings
            applySettings();
        });

        // Visual configuration for different object types (fully configurable)
        const VISUAL_CONFIG = {
            region: {
                geometry: 'octahedron',
                size: 1.2,
                color: 0x008b8d,
                emissive: 0x005f60,
                emissiveIntensity: 0.15,
                glowSize: 1.8,
                glowColor: 0x00ffff,
                glowOpacity: 0.12,
                hitRadius: 2.0,
                showLabel: true
            },
            system: {
                geometry: 'sphere',
                size: 0.8,
                color: 0x008b8d,
                emissive: 0x005f60,
                emissiveIntensity: 0.15,
                glowSize: 1.2,
                glowColor: 0x00ffff,
                glowOpacity: 0.15,
                hitRadius: 1.2,
                showLabel: false
            },
            planet: {
                geometry: 'sphere',
                size: 0.8,
                color: 0x008b8d,
                emissive: 0x005f60,
                emissiveIntensity: 0.15,
                glowSize: 1.2,
                glowColor: 0x00ffff,
                glowOpacity: 0.15,
                hitRadius: 1.2,
                showLabel: false
            },
            moon: {
                geometry: 'sphere',
                size: 0.4,
                color: 0xb4b4c8,
                emissive: 0x7a7a8a,
                emissiveIntensity: 0.1,
                opacity: 0.9,
                showLabel: false
            },
            station: {
                geometry: 'box',
                size: 0.27,
                color: 0x9400d3,
                emissive: 0x9400d3,
                emissiveIntensity: 0.4,
                glowSize: 0.38,
                glowColor: 0xda70d6,
                glowOpacity: 0.2,
                rotation: [Math.PI / 4, Math.PI / 4, 0],
                showLabel: false
            },
            sun: {
                geometry: 'sphere',
                size: 0.5,
                color: 0xffd700,
                showLabel: false
            }
        };
        // Galaxy controls state
        let showRegions = false;
        let labelsMode = 'off'; // 'off' | 'on' (hover reserved)
        
        // Scene setup
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x000000);
        scene.fog = new THREE.FogExp2(0x000000, 0.002);
        
        // Camera
        const camera = new THREE.PerspectiveCamera(
            60,
            window.innerWidth / window.innerHeight,
            0.1,
            10000
        );
        camera.position.set(50, 50, 50);
        camera.lookAt(0, 0, 0);
        
        // Renderer
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        if (renderer.outputEncoding !== undefined) {
            renderer.outputEncoding = THREE.sRGBEncoding;
        }
        if (renderer.toneMapping !== undefined) {
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.0;
        }
        document.getElementById('canvas-container').appendChild(renderer.domElement);

        // HUD: compass and scale (embedded in container)
        const compassCanvas = document.getElementById('compass-canvas');
        const compassCtx = compassCanvas.getContext('2d');
        function drawCompass(angleRad){
            const ctx = compassCtx; const w=64,h=64; ctx.clearRect(0,0,w,h);
            ctx.save();
            ctx.translate(w/2,h/2);
            ctx.rotate(angleRad);
            ctx.strokeStyle = '#00CED1'; ctx.lineWidth = 2;
            ctx.beginPath(); ctx.moveTo(0,-20); ctx.lineTo(0,20); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(0,-20); ctx.lineTo(-5,-10); ctx.lineTo(5,-10); ctx.closePath(); ctx.stroke();
            ctx.restore();
            ctx.fillStyle = '#00CED1'; ctx.font = '10px Rajdhani, sans-serif'; ctx.textAlign='center';
            ctx.fillText('N', w/2, 10);
        }
        const scaleDiv = document.getElementById('scale-text');
        // Initialize HUD drawings/text
    drawCompass(0);
        scaleDiv.textContent = 'Scale: major grid = 12.5 units';
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
        
        // Lighting
        const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
        scene.add(ambientLight);
        
        const sunLight = new THREE.PointLight(0xffd700, 2, 500);
        sunLight.position.set(0, 0, 0);
        scene.add(sunLight);
        
        const fillLight = new THREE.DirectionalLight(0x00ced1, 0.3);
        fillLight.position.set(50, 50, 50);
        scene.add(fillLight);
        
        // Particle starfield background
        const starsGeometry = new THREE.BufferGeometry();
        const starsMaterial = new THREE.PointsMaterial({
            color: 0xffffff,
            size: 0.7,
            transparent: true,
            opacity: 0.8
        });
        
        const starsVertices = [];
        for (let i = 0; i < 5000; i++) {
            const x = (Math.random() - 0.5) * 2000;
            const y = (Math.random() - 0.5) * 2000;
            const z = (Math.random() - 0.5) * 2000;
            starsVertices.push(x, y, z);
        }
        
        starsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starsVertices, 3));
        const starField = new THREE.Points(starsGeometry, starsMaterial);
        scene.add(starField);
        
    // Old-style layered grid (minor + major), no axes
    const minorGrid = new THREE.GridHelper(200, 80, 0x003a3a, 0x003a3a);
    minorGrid.material.transparent = true;
    minorGrid.material.opacity = 0.15;
    scene.add(minorGrid);

    const majorGrid = new THREE.GridHelper(200, 16, 0x00ced1, 0x00ced1);
    majorGrid.material.transparent = true;
    majorGrid.material.opacity = 0.25;
    scene.add(majorGrid);
        
        // Build legend dynamically from VISUAL_CONFIG and current view (regions disabled by default)
        function buildLegend() {
            const legendContainer = document.getElementById('legend-items');
            const legendLabels = {
                sun: 'Central Star',
                system: 'Star System',
                planet: 'Planet',
                moon: 'Moon',
                station: 'Space Station',
                region: 'Region'
            };
            
            // Determine which types to show based on view mode
            const typesToShow = VIEW_MODE === 'galaxy' ? ['system'] : ['sun', 'planet', 'moon', 'station'];
            legendContainer.innerHTML = '';
            
            typesToShow.forEach(type => {
                if (!VISUAL_CONFIG[type]) return;
                
                const config = VISUAL_CONFIG[type];
                const item = document.createElement('div');
                item.className = 'legend-item';
                
                const icon = document.createElement('div');
                icon.className = 'legend-icon';
                icon.style.background = `#${config.color.toString(16).padStart(6, '0')}`;
                
                // Apply shape-specific styling
                if (config.geometry === 'box') {
                    icon.style.borderRadius = '2px';
                } else {
                    icon.style.borderRadius = '50%';
                }
                
                const label = document.createElement('span');
                label.textContent = legendLabels[type] || type;
                
                item.appendChild(icon);
                item.appendChild(label);
                legendContainer.appendChild(item);
            });
        }
        
        buildLegend();
        
        // Update UI based on view mode
        if (VIEW_MODE === 'system' && REGION_NAME) {
            document.getElementById('view-title').textContent = `SYSTEM VIEW - ${REGION_NAME}`;
            document.getElementById('back-btn').style.display = 'block';
            document.getElementById('back-btn').addEventListener('click', () => {
                window.location.href = 'VH-Map.html';
            });
        } else {
            document.getElementById('view-title').textContent = 'GALAXY OVERVIEW';
            document.getElementById('info-content').textContent = 'Click on a system to view its solar layout';
        }
        
        // Create objects from data
    const objects = [];
    const systemLabelSprites = [];
    const regionMeshes = [];
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        let selectedObject = null;
        let autoRotate = false;
        const tooltip = document.getElementById('hover-tooltip');
        // Helper: resolve photo href to correct path when files are under dist/
        function resolvePhotoHref(p) {
            try {
                if (!p) return null;
                if (/^https?:/i.test(p)) return p; // absolute URL
                if (p.startsWith('/')) return p;    // root-relative
                // If current HTML is in /dist/, photos live one level up
                var path = (window.location && window.location.pathname) ? window.location.pathname.replace(/\\/g,'/') : '';
                if (path.indexOf('/dist/') !== -1) {
                    return '../' + p.replace(/^\/+/, '');
                }
                return p;
            } catch (e) { return p; }
        }
        // Controls panel toggle
        const controlsBtn = document.getElementById('btn-controls');
        const controlsPanel = document.getElementById('controls-panel');
        controlsBtn.addEventListener('click', () => {
            const visible = controlsPanel.style.display !== 'none';
            controlsPanel.style.display = visible ? 'none' : 'block';
        });
        // Grid toggle
        let gridOn = true;
        const gridBtn = document.getElementById('btn-grid');
        gridBtn.addEventListener('click', () => {
            gridOn = !gridOn;
            minorGrid.visible = gridOn;
            majorGrid.visible = gridOn;
            gridBtn.textContent = gridOn ? 'Grid: On' : 'Grid: Off';
        });
        const autoRotateCheckbox = document.getElementById('toggle-autorotate');
        autoRotateCheckbox.addEventListener('change', () => { autoRotate = autoRotateCheckbox.checked; });
        // Labels toggle
        const labelsBtn = document.getElementById('btn-labels');
        labelsBtn.addEventListener('click', () => {
            labelsMode = (labelsMode === 'off') ? 'on' : 'off';
            labelsBtn.textContent = `Labels: ${labelsMode === 'on' ? 'On' : 'Off'}`;
            updateSystemLabelsVisibility && updateSystemLabelsVisibility();
        });
        // Regions toggle removed from UI usage (kept code paths idle)
        document.getElementById('btn-screenshot').addEventListener('click', () => {
            renderer.render(scene, camera);
            const url = renderer.domElement.toDataURL('image/png');
            const a = document.createElement('a');
            a.href = url; a.download = (VIEW_MODE === 'galaxy' ? 'galaxy' : `system_${REGION_NAME}`) + '.png';
            a.click();
        });
        let stats = null;
        const statsCheckbox = document.getElementById('toggle-stats');
        statsCheckbox.addEventListener('change', () => {
            if (statsCheckbox.checked) {
                stats = new Stats();
                stats.showPanel(0);
                document.body.appendChild(stats.dom);
                stats.dom.style.top = 'auto';
                stats.dom.style.bottom = '0px';
                stats.dom.style.left = 'auto';
                stats.dom.style.right = '0px';
            } else if (stats) {
                stats.dom.remove();
                stats = null;
            }
        });
        
    // Sun at center (only in System View) - data-driven
        let sun = null;
        if (VIEW_MODE === 'system' && VISUAL_CONFIG.sun) {
            const config = VISUAL_CONFIG.sun;
            const sunGeometry = new THREE.SphereGeometry(config.size, 32, 32);
            const sunMaterial = new THREE.MeshBasicMaterial({ color: config.color });
            sun = new THREE.Mesh(sunGeometry, sunMaterial);
            sun.userData = {
                type: 'sun',
                name: 'Central Star',
                data: { name: 'Central Star', type: 'Star' }
            };
            scene.add(sun);
            objects.push(sun);
        }
        
        // Create objects from data - fully data-driven based on JSON type field
        SYSTEM_DATA.forEach(item => {
            const x = item.x || 0;
            const y = item.y || 0;
            const z = item.z || 0;
            const itemType = item.type || 'system'; // Default to system if no type specified
            
            // Skip if no visual config for this type
            if (!VISUAL_CONFIG[itemType]) {
                console.warn(`No visual config for type: ${itemType}`, item);
                return;
            }
            
            // Skip rendering in wrong view mode
            if (VIEW_MODE === 'galaxy' && itemType !== 'system') return;
            if (VIEW_MODE === 'system' && (itemType === 'region' || itemType === 'system')) return; // in system view, use 'planet' for planets
            
            // Skip system markers too close to origin (avoid overlapping sun)
            if (VIEW_MODE === 'system' && itemType === 'system') {
                const distToOrigin = Math.sqrt(x*x + y*y + z*z);
                if (distToOrigin < 1.0) return;
            }
            
            const config = VISUAL_CONFIG[itemType];
            
            // Create geometry based on config
            let geometry;
            switch (config.geometry) {
                case 'octahedron':
                    geometry = new THREE.OctahedronGeometry(config.size, 0);
                    break;
                case 'sphere':
                    geometry = new THREE.SphereGeometry(config.size, 16, 16);
                    break;
                case 'box':
                    geometry = new THREE.BoxGeometry(config.size, config.size, config.size);
                    break;
                default:
                    geometry = new THREE.SphereGeometry(config.size, 16, 16);
            }
            
            // Create material based on config
            const materialProps = {
                color: config.color,
                transparent: true,
                opacity: config.opacity !== undefined ? config.opacity : 0.95
            };
            
            if (config.emissive !== undefined) {
                materialProps.emissive = config.emissive;
                materialProps.emissiveIntensity = config.emissiveIntensity || 0.2;
                materialProps.shininess = 100;
            }
            
            const material = new THREE.MeshPhongMaterial(materialProps);
            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.set(x, y, z);
            
            // Apply rotation if specified
            if (config.rotation) {
                mesh.rotation.set(...config.rotation);
            }
            
            // Set user data (preserve all JSON fields)
            mesh.userData = {
                type: itemType,
                name: item.name || itemType,
                data: item
            };
            
            // Add region field for navigation
            if (item.region) {
                mesh.userData.region = item.region;
            }
            
            scene.add(mesh);
            objects.push(mesh);
            
            // Add subtle outline for depth (for octahedron/diamond shapes)
            if (config.geometry === 'octahedron' && (itemType === 'region' || itemType === 'system' || itemType === 'planet')) {
                const outlineGeometry = new THREE.OctahedronGeometry(config.size * 1.05, 0);
                const outlineMaterial = new THREE.MeshBasicMaterial({
                    color: 0x00ffff,
                    transparent: true,
                    opacity: 0.3,
                    side: THREE.BackSide
                });
                const outline = new THREE.Mesh(outlineGeometry, outlineMaterial);
                mesh.add(outline);
            }
            
            // Add invisible hit area if specified
            if (config.hitRadius) {
                const hitGeo = new THREE.SphereGeometry(config.hitRadius, 8, 8);
                const hitMat = new THREE.MeshBasicMaterial({ visible: false });
                const hitMesh = new THREE.Mesh(hitGeo, hitMat);
                hitMesh.position.set(0, 0, 0);
                hitMesh.userData = { ...mesh.userData, target: mesh };
                mesh.add(hitMesh);
                objects.push(hitMesh);
            }
            
            // Glow layer removed per user request
            
            // Add text label if specified (disabled for galaxy systems by default)
            if (false && config.showLabel && VIEW_MODE === 'galaxy' && itemType === 'system') {
                const canvas = document.createElement('canvas');
                const context = canvas.getContext('2d');
                canvas.width = 512;
                canvas.height = 128;
                context.font = 'Bold 48px Rajdhani, Arial';
                context.fillStyle = 'rgba(0, 206, 209, 1)';
                context.textAlign = 'center';
                context.textBaseline = 'middle';
                const labelText = item.name;
                context.fillText(labelText, 256, 64);
                
                const texture = new THREE.CanvasTexture(canvas);
                const spriteMaterial = new THREE.SpriteMaterial({ map: texture, transparent: true });
                const sprite = new THREE.Sprite(spriteMaterial);
                sprite.scale.set(8, 2, 1);
                sprite.position.set(x, y + 3.5, z);
                scene.add(sprite);
            }
        });
        
        // Build region centroid meshes (galaxy view) - disabled unless explicitly enabled
        function buildRegionsFromSystems() {
            const map = new Map();
            objects.forEach(o => {
                if (!o.userData || o.userData.type !== 'system') return;
                const r = o.userData.region || (o.userData.data && o.userData.data.region);
                if (!r) return;
                if (!map.has(r)) map.set(r, []);
                map.get(r).push(o.position.clone());
            });
            // Clear existing meshes
            while (regionMeshes.length) {
                const m = regionMeshes.pop();
                try { scene.remove(m); } catch {}
            }
            const cfg = VISUAL_CONFIG.region;
            if (!cfg) return;
            map.forEach((positions, name) => {
                const c = new THREE.Vector3(0,0,0);
                positions.forEach(p => c.add(p));
                c.multiplyScalar(1 / positions.length);
                const geo = new THREE.OctahedronGeometry(cfg.size, 0);
                const mat = new THREE.MeshPhongMaterial({ color: cfg.color, emissive: cfg.emissive || 0x000000, emissiveIntensity: cfg.emissiveIntensity || 0.15, transparent: true, opacity: cfg.opacity || 0.95 });
                const mesh = new THREE.Mesh(geo, mat);
                mesh.position.copy(c);
                mesh.visible = false;
                mesh.userData = { type: 'region', name, region: name, data: { name, count: positions.length } };
                scene.add(mesh);
                regionMeshes.push(mesh);
            });
        }

        function setRegionsVisible(v) { regionMeshes.forEach(m => m.visible = v); }

        // Build system labels (galaxy view)
        function buildSystemLabels() {
            // Clear
            while (systemLabelSprites.length) {
                const s = systemLabelSprites.pop();
                try { scene.remove(s.sprite || s); } catch {}
            }
            const makeLabel = (text) => {
                const canvas = document.createElement('canvas');
                const context = canvas.getContext('2d');
                canvas.width = 256; canvas.height = 64;
                context.font = 'Bold 28px Rajdhani, Arial';
                context.fillStyle = 'rgba(0, 206, 209, 1)';
                context.textAlign = 'center'; context.textBaseline = 'middle';
                context.fillText(text, 128, 32);
                const texture = new THREE.CanvasTexture(canvas);
                const spriteMaterial = new THREE.SpriteMaterial({ map: texture, transparent: true, depthWrite: false });
                const sprite = new THREE.Sprite(spriteMaterial);
                sprite.scale.set(4, 1, 1);
                return sprite;
            };
            objects.forEach(o => {
                if (!o.userData || o.userData.type !== 'system') return;
                const name = o.userData.name || 'System';
                const sprite = makeLabel(name);
                sprite.position.copy(o.position.clone().add(new THREE.Vector3(0, 2.5, 0)));
                sprite.visible = false;
                scene.add(sprite);
                systemLabelSprites.push({ sprite, target: o });
            });
        }

        function updateSystemLabelsVisibility() {
            if (VIEW_MODE !== 'galaxy') {
                systemLabelSprites.forEach(({sprite}) => sprite.visible = false);
                return;
            }
            const on = (labelsMode === 'on');
            // Simple declutter: show closest N labels within a distance
            const maxLabels = 30;
            const maxDist = 250;
            const list = systemLabelSprites.map(entry => ({ entry, d: camera.position.distanceTo(entry.target.position) }))
                .filter(x => x.d <= maxDist)
                .sort((a,b) => a.d - b.d)
                .slice(0, maxLabels)
                .map(x => x.entry);
            const allowed = new Set(list);
            systemLabelSprites.forEach((entry) => {
                const { sprite, target } = entry;
                sprite.position.copy(target.position.clone().add(new THREE.Vector3(0, 2.5, 0)));
                sprite.visible = on && allowed.has(entry);
            });
        }

        if (VIEW_MODE === 'galaxy') {
            // Regions disabled by default; can be re-enabled later via code toggle
            // buildRegionsFromSystems();
            buildSystemLabels();
        }

        // Draw orbit rings and set camera preset in system view
        if (VIEW_MODE === 'system') {
            const radii = new Set();
            objects.forEach(o => {
                if (o.userData && o.userData.type === 'system') {
                    const r = Math.sqrt(o.position.x*o.position.x + o.position.z*o.position.z);
                    const key = Math.round(r * 100) / 100;
                    if (key > 0.5) radii.add(key);
                }
            });
            radii.forEach(r => {
                const ringGeo = new THREE.RingGeometry(Math.max(0, r - 0.02), r + 0.02, 64);
                const ringMat = new THREE.MeshBasicMaterial({ color: 0x00ced1, side: THREE.DoubleSide, transparent: true, opacity: 0.15 });
                const ring = new THREE.Mesh(ringGeo, ringMat);
                ring.rotation.x = Math.PI / 2;
                scene.add(ring);
            });
            let maxR = 40;
            radii.forEach(r => { if (r > maxR) maxR = r; });
            const dist = Math.max(40, maxR * 2.4);
            camera.position.set(dist * 0.7, dist * 0.5, dist * 0.7);
            camera.lookAt(0,0,0);
        }
        
    // Mouse controls
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };
    const cameraTarget = new THREE.Vector3(0, 0, 0);
        
        renderer.domElement.addEventListener('mousedown', (e) => {
            isDragging = true;
            previousMousePosition = { x: e.clientX, y: e.clientY };
        });
        
        renderer.domElement.addEventListener('mousemove', (e) => {
            if (isDragging) {
                const deltaX = e.clientX - previousMousePosition.x;
                const deltaY = e.clientY - previousMousePosition.y;
                
                if (e.buttons === 1) { // Left click - rotate around target
                    camera.position.sub(cameraTarget);
                    camera.position.applyAxisAngle(new THREE.Vector3(0, 1, 0), deltaX * 0.005);
                    const axis = new THREE.Vector3().crossVectors(camera.up, camera.position).normalize();
                    camera.position.applyAxisAngle(axis, deltaY * 0.005);
                    camera.position.add(cameraTarget);
                    camera.lookAt(cameraTarget);
                } else if (e.buttons === 2) { // Right click - pan
                    const distance = camera.position.clone().sub(cameraTarget).length();
                    const panFactor = distance * 0.001;
                    camera.position.x -= deltaX * panFactor;
                    camera.position.y += deltaY * panFactor;
                    cameraTarget.x -= deltaX * panFactor;
                    cameraTarget.y += deltaY * panFactor;
                    camera.lookAt(cameraTarget);
                }
                
                previousMousePosition = { x: e.clientX, y: e.clientY };
                // Hide tooltip while dragging
                tooltip.style.display = 'none';
            } else {
                // Hover picking for tooltip when not dragging
                mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
                mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
                raycaster.setFromCamera(mouse, camera);
                const intersects = raycaster.intersectObjects(objects, true);
                if (intersects.length > 0) {
                    let object = intersects[0].object;
                    while (object.parent && !object.userData.type) {
                        object = object.parent;
                    }
                    const ud = object.userData || {};
                    const data = ud.data || {};
                    let html = '';

                    // Galaxy View: System hover info
                    if (VIEW_MODE === 'galaxy' && ud.type === 'system') {
                        const name = ud.name || 'Unknown System';
                        const region = data.region || 'Unknown Region';
                        const x = typeof data.x === 'number' ? data.x.toFixed(1) : 'N/A';
                        const y = typeof data.y === 'number' ? data.y.toFixed(1) : 'N/A';
                        const z = typeof data.z === 'number' ? data.z.toFixed(1) : 'N/A';

                        // Count planets and moons
                        let planetCount = 0;
                        let moonCount = 0;
                        if (data.planets && Array.isArray(data.planets)) {
                            planetCount = data.planets.length;
                            data.planets.forEach(p => {
                                if (p.moons && Array.isArray(p.moons)) {
                                    moonCount += p.moons.length;
                                }
                            });
                        }

                        html = `<div class="tooltip-title">${name}</div>`;
                        html += `<div class="tooltip-line"><span class="tooltip-label">Region:</span> ${region}</div>`;
                        html += `<div class="tooltip-line"><span class="tooltip-label">Planets:</span> ${planetCount}</div>`;
                        html += `<div class="tooltip-line"><span class="tooltip-label">Moons:</span> ${moonCount}</div>`;
                        html += `<div class="tooltip-line"><span class="tooltip-label">Coords:</span> (${x}, ${y}, ${z})</div>`;
                    }
                    // Galaxy View: Region hover info
                    else if (VIEW_MODE === 'galaxy' && ud.type === 'region') {
                        const count = ud.data && typeof ud.data.count === 'number' ? ud.data.count : undefined;
                        html = `<div class="tooltip-title">${ud.name}</div>`;
                        if (count !== undefined) {
                            html += `<div class="tooltip-line"><span class="tooltip-label">Systems:</span> ${count}</div>`;
                        }
                    }
                    // System View: Sun/Central Star
                    else if (VIEW_MODE === 'system' && ud.type === 'sun') {
                        const sysName = SYSTEM_META && SYSTEM_META.name ? SYSTEM_META.name : 'Unknown System';
                        const region = SYSTEM_META && SYSTEM_META.region ? SYSTEM_META.region : 'Unknown';
                        const x = SYSTEM_META && typeof SYSTEM_META.x === 'number' ? SYSTEM_META.x.toFixed(1) : 'N/A';
                        const y = SYSTEM_META && typeof SYSTEM_META.y === 'number' ? SYSTEM_META.y.toFixed(1) : 'N/A';
                        const z = SYSTEM_META && typeof SYSTEM_META.z === 'number' ? SYSTEM_META.z.toFixed(1) : 'N/A';

                        // Count planets in system
                        const planetCount = (SYSTEM_DATA || []).filter(it => it && it.type === 'planet').length;

                        html = `<div class="tooltip-title">⭐ Central Star</div>`;
                        html += `<div class="tooltip-line"><span class="tooltip-label">System:</span> ${sysName}</div>`;
                        html += `<div class="tooltip-line"><span class="tooltip-label">Region:</span> ${region}</div>`;
                        html += `<div class="tooltip-line"><span class="tooltip-label">Planets:</span> ${planetCount}</div>`;
                        html += `<div class="tooltip-line"><span class="tooltip-label">Coords:</span> (${x}, ${y}, ${z})</div>`;
                    }
                    // System View: Planet
                    else if (VIEW_MODE === 'system' && ud.type === 'planet') {
                        const name = ud.name || 'Unknown Planet';
                        const sentinel = data.sentinel || 'N/A';
                        const fauna = data.fauna || 'N/A';
                        const flora = data.flora || 'N/A';

                        // Count moons
                        let moonCount = 0;
                        if (data.moons && Array.isArray(data.moons)) {
                            moonCount = data.moons.length;
                        }

                        html = `<div class="tooltip-title">🪐 ${name}</div>`;
                        html += `<div class="tooltip-line"><span class="tooltip-label">Moons:</span> ${moonCount}</div>`;
                        html += `<div class="tooltip-line"><span class="tooltip-label">Sentinel:</span> ${sentinel}</div>`;
                        html += `<div class="tooltip-line"><span class="tooltip-label">Fauna:</span> ${fauna}</div>`;
                        html += `<div class="tooltip-line"><span class="tooltip-label">Flora:</span> ${flora}</div>`;
                    }
                    // System View: Moon
                    else if (VIEW_MODE === 'system' && ud.type === 'moon') {
                        const name = ud.name || 'Unknown Moon';
                        const sentinel = data.sentinel || 'N/A';
                        const fauna = data.fauna || 'N/A';
                        const flora = data.flora || 'N/A';

                        html = `<div class="tooltip-title">🌙 ${name}</div>`;
                        html += `<div class="tooltip-line"><span class="tooltip-label">Sentinel:</span> ${sentinel}</div>`;
                        html += `<div class="tooltip-line"><span class="tooltip-label">Fauna:</span> ${fauna}</div>`;
                        html += `<div class="tooltip-line"><span class="tooltip-label">Flora:</span> ${flora}</div>`;
                    }
                    // System View: Space Station
                    else if (VIEW_MODE === 'system' && ud.type === 'station') {
                        const name = ud.name || 'Space Station';
                        const x = typeof data.x === 'number' ? data.x.toFixed(1) : 'N/A';
                        const y = typeof data.y === 'number' ? data.y.toFixed(1) : 'N/A';
                        const z = typeof data.z === 'number' ? data.z.toFixed(1) : 'N/A';

                        html = `<div class="tooltip-title">🛸 ${name}</div>`;
                        html += `<div class="tooltip-line"><span class="tooltip-label">Coords:</span> (${x}, ${y}, ${z})</div>`;
                    }

                    if (html) {
                        tooltip.innerHTML = html;
                        const offset = 14;
                        let x = e.clientX + offset;
                        let y = e.clientY + offset;
                        // Keep inside viewport right/bottom edges
                        const rect = { w: 280, h: 150 };
                        if (x + rect.w > window.innerWidth - 8) x = e.clientX - rect.w - offset;
                        if (y + rect.h > window.innerHeight - 8) y = window.innerHeight - rect.h - 8;
                        tooltip.style.left = x + 'px';
                        tooltip.style.top = y + 'px';
                        tooltip.style.display = 'block';
                    } else {
                        tooltip.style.display = 'none';
                    }
                } else {
                    tooltip.style.display = 'none';
                }
            }
        });
        
        renderer.domElement.addEventListener('mouseup', () => {
            isDragging = false;
        });
        renderer.domElement.addEventListener('mouseleave', () => {
            tooltip.style.display = 'none';
        });
        
        renderer.domElement.addEventListener('wheel', (e) => {
            e.preventDefault();
            const direction = camera.position.clone().normalize();
            const distance = Math.max(10, camera.position.length() - e.deltaY * 0.05);
            camera.position.copy(direction.multiplyScalar(distance));
            camera.lookAt(cameraTarget);
        });
        
        renderer.domElement.addEventListener('contextmenu', (e) => e.preventDefault());
        
        // Click selection
        renderer.domElement.addEventListener('click', (e) => {
            if (isDragging) return;
            
            mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
            
            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(objects, true);
            
            if (intersects.length > 0) {
                // Find the parent object with userData
                let object = intersects[0].object;
                while (object.parent && !object.userData.type) {
                    object = object.parent;
                }
                
                // In galaxy view, clicking a system navigates to system view
                if (VIEW_MODE === 'galaxy' && object.userData.type === 'system') {
                    const systemName = object.userData.name || 'system';
                    // Match Python safe_filename: preserve case, allow alphanumeric/space/dash/underscore, replace spaces with underscore
                    const safeName = systemName.split('').map(c => /[a-zA-Z0-9 \-_]/.test(c) ? c : '_').join('').trim().replace(/ /g, '_');
                    window.location.href = `system_${safeName}.html`;
                } else if (VIEW_MODE === 'system') {
                    // In system view, show details (don't allow clicks in galaxy view for non-regions)
                    selectObject(object.userData.target ? object.userData.target : object);
                }
            } else {
                // Background click clears selection
                if (selectedObject) {
                    const prev = selectedObject;
                    if (
                        prev.userData && prev.userData.type === 'system' &&
                        prev.material && typeof prev.material.emissiveIntensity === 'number'
                    ) {
                        const orig = prev.userData.originalIntensity;
                        prev.material.emissiveIntensity = (typeof orig === 'number') ? orig : 0.3;
                    }
                    selectedObject = null;
                    document.getElementById('info-content').innerHTML = 'Click an object to see details';
                }
            }
        });
        
    function selectObject(object) {
            // Deselect previous selection (restore original look for planets)
            if (selectedObject) {
                const prev = selectedObject;
                if (
                    prev.userData && prev.userData.type === 'system' &&
                    prev.material && typeof prev.material.emissiveIntensity === 'number'
                ) {
                    const orig = prev.userData.originalIntensity;
                    prev.material.emissiveIntensity = (typeof orig === 'number') ? orig : 0.3;
                }
            }

            selectedObject = object;

            // Highlight only planets
            if (
                selectedObject && selectedObject.userData && selectedObject.userData.type === 'planet' &&
                selectedObject.material && typeof selectedObject.material.emissiveIntensity === 'number'
            ) {
                selectedObject.userData.originalIntensity = selectedObject.material.emissiveIntensity;
                selectedObject.material.emissiveIntensity = 1;
            }

            // Update info panel
            const ud = object.userData || {};
            const data = ud.data || {};
            let heading = 'Details';
            if (ud.type === 'sun') heading = 'System Details';
            else if (ud.type === 'planet') heading = 'Planet Details';
            else if (ud.type === 'moon') heading = 'Moon Details';
            let html = `<h3>${heading}</h3>`;

            // System center (sun) shows system meta
            if (ud.type === 'sun' && SYSTEM_META) {
                const m = SYSTEM_META || {};
                const planetCount = (SYSTEM_DATA || []).filter(it => it && it.type === 'system').length;
                html += `<p><strong>Name:</strong> ${m.name || ''}</p>`;
                html += `<p><strong>Region:</strong> ${m.region || ''}</p>`;
                if (m.attributes) html += `<p><strong>System Attributes:</strong> ${m.attributes}</p>`;
                if (typeof m.x === 'number' && typeof m.y === 'number' && typeof m.z === 'number') {
                    html += `<p><strong>Coordinates:</strong> (${m.x}, ${m.y}, ${m.z})</p>`;
                }
                html += `<p><strong>Planets:</strong> ${planetCount}</p>`;
                document.getElementById('info-content').innerHTML = html;
                return;
            }
            
            // Priority fields to show first
            const priorityFields = ['type', 'id', 'region', 'system', 'attributes'];
            const skipFields = ['name', 'x', 'y', 'z', 'planets', 'photo', 'moons', 'space_station', 'space_stations', 'count'];
            
            // Show priority fields first
            priorityFields.forEach(field => {
                if (data[field] !== undefined && data[field] !== null && data[field] !== '') {
                    const label = field.charAt(0).toUpperCase() + field.slice(1).replace(/_/g, ' ');
                    html += `<p><strong>${label}:</strong> ${data[field]}</p>`;
                }
            });
            
            // Show all other fields dynamically
            Object.keys(data).forEach(key => {
                if (!priorityFields.includes(key) && !skipFields.includes(key)) {
                    const value = data[key];
                    if (value !== undefined && value !== null && value !== '') {
                        const label = key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ');
                        html += `<p><strong>${label}:</strong> ${value}</p>`;
                    }
                }
            });
            
            // Show planets list if available (support both string array and object array)
            if (data.planets && Array.isArray(data.planets) && data.planets.length > 0) {
                html += `<p><strong>Planets:</strong></p><ul style="margin: 5px 0; padding-left: 20px;">`;
                data.planets.forEach(planet => {
                    if (typeof planet === 'string') {
                        // Legacy format: just string names
                        html += `<li>${planet}</li>`;
                    } else if (typeof planet === 'object' && planet.name) {
                        // New format: planet objects with moons
                        const moonCount = planet.moons ? planet.moons.length : 0;
                        const moonText = moonCount > 0 ? ` <span style="color: #888;">(${moonCount} moon${moonCount !== 1 ? 's' : ''})</span>` : '';
                        html += `<li>${planet.name}${moonText}</li>`;
                    }
                });
                html += `</ul>`;
            }
            
            // For planet detail, list its moons if present
            if (ud.type === 'planet' && data.moons && Array.isArray(data.moons) && data.moons.length > 0) {
                html += `<p><strong>Moons:</strong></p><ul style="margin: 5px 0; padding-left: 20px;">`;
                data.moons.forEach(m => {
                    const n = (typeof m === 'string') ? m : (m && m.name) ? m.name : 'Moon';
                    html += `<li>${n}</li>`;
                });
                html += `</ul>`;
            }

            // Show photo if available
            if (data.photo) {
                const href = resolvePhotoHref(data.photo);
                if (href) {
                    html += `<p><strong>Photo:</strong> <a href="${href}" target="_blank" style="color: #00CED1;">View</a></p>`;
                }
            }
            
            document.getElementById('info-content').innerHTML = html;
        }
        
        // Keyboard navigation
        window.addEventListener('keydown', (e) => {
            const pan = 2.0;
            const up = new THREE.Vector3(0,1,0);
            const forward = camera.getWorldDirection(new THREE.Vector3());
            forward.y = 0; forward.normalize();
            const right = new THREE.Vector3().crossVectors(forward, up).normalize();
            switch (e.key.toLowerCase()) {
                case 'w':
                    camera.position.addScaledVector(forward, pan);
                    cameraTarget.addScaledVector(forward, pan);
                    break;
                case 's':
                    camera.position.addScaledVector(forward, -pan);
                    cameraTarget.addScaledVector(forward, -pan);
                    break;
                case 'a':
                    camera.position.addScaledVector(right, -pan);
                    cameraTarget.addScaledVector(right, -pan);
                    break;
                case 'd':
                    camera.position.addScaledVector(right, pan);
                    cameraTarget.addScaledVector(right, pan);
                    break;
                case 'q':
                    camera.position.y -= pan; cameraTarget.y -= pan; break;
                case 'e':
                    camera.position.y += pan; cameraTarget.y += pan; break;
                case 'c':
                    camera.position.set(50,50,50);
                    cameraTarget.set(0,0,0);
                    camera.lookAt(cameraTarget);
                    break;
            }
        });

        // Animation loop
        function animate() {
            requestAnimationFrame(animate);
            
            // Rotate sun (if it exists)
            if (sun) {
                sun.rotation.y += 0.001;
            }
            
            // Slowly rotate starfield
            starField.rotation.y += 0.0001;
            
            // Auto-rotate camera (optional)
            if (autoRotate) {
                const v = camera.position.clone().sub(cameraTarget);
                v.applyAxisAngle(new THREE.Vector3(0,1,0), 0.002);
                camera.position.copy(v.add(cameraTarget));
                camera.lookAt(cameraTarget);
            }

            // Animate objects - data-driven based on config
            objects.forEach(obj => {
                if (!obj.userData || !obj.userData.type) return;
                
                const objType = obj.userData.type;
                
                // Rotate the main diamond/planet icons themselves
                if (VIEW_MODE === 'galaxy' && objType === 'region') {
                    obj.rotation.y += 0.003;
                }
                
                if (VIEW_MODE === 'system' && objType === 'planet') {
                    obj.rotation.y += 0.003;
                }
            });
            
            // Update compass and scale HUD
            const dir = camera.getWorldDirection(new THREE.Vector3());
            const yaw = Math.atan2(dir.x, dir.z); // heading
            drawCompass(yaw);
            const majorSize = 200, majorDiv = 16; const cell = majorSize / majorDiv;
            scaleDiv.textContent = `Scale: major grid = ${cell.toFixed(1)} units`;
            if (typeof updateSystemLabelsVisibility === 'function') updateSystemLabelsVisibility();

            if (stats) stats.begin();
            renderer.render(scene, camera);
            if (stats) stats.end();
        }
        
        // Handle window resize handled above to also layout HUD
        
        // Start animation
        animate();
        
        console.log('Three.js Star Map initialized with', SYSTEM_DATA.length, 'objects');
    </script>
</body>
</html>
"""


# ============================================================================
# BUILD FUNCTIONS
# ============================================================================

def prepare_galaxy_systems_data(df: pd.DataFrame) -> List[dict]:
    """Prepare one point per system for Galaxy Overview."""
    items: List[dict] = []
    for _, row in df.iterrows():
        # Skip region metadata entries
        if row.get("type") == "region":
            continue
        try:
            x, y, z = cartesian_to_orbital(
                float(row.get("x", 0) or 0),
                float(row.get("y", 0) or 0),
                float(row.get("z", 0) or 0)
            )
        except Exception:
            x = y = z = 0.0
        item = {
            "type": "system",
            "name": row.get("name"),
            "region": row.get("region"),
            "x": x,
            "y": z,
            "z": y,
        }
        # Include a few fields for hover/detail (even though we navigate on click)
        for key in ("id", "attributes", "planets"):
            val = row.get(key)
            if val is not None:
                item[key] = val
        items.append(item)
    return items

def _angle_from_name(name: str, seed: float = 0.0) -> float:
    import hashlib, math as _m
    if not name:
        return (seed % 1.0) * 2 * _m.pi
    h = hashlib.sha256(name.encode("utf-8")).hexdigest()
    # Take first 8 hex digits to int, normalize 0..1
    v = int(h[:8], 16) / 0xFFFFFFFF
    return (v % 1.0) * 2 * _m.pi

def prepare_single_system_solar(row: dict) -> List[dict]:
    """Prepare planets and moons in a synthetic solar layout for a single system record."""
    data: List[dict] = []
    sys_name = row.get("name", "")
    region = row.get("region", "")
    # Planets may be objects or strings
    planets = row.get("planets") or []
    if planets and isinstance(planets, list) and len(planets) > 0 and isinstance(planets[0], str):
        planets = [{"name": p, "moons": []} for p in planets]
    # Layout params
    base_r = 3.0
    step_r = 2.0
    for i, p in enumerate(planets):
        pname = p.get("name", f"Planet {i+1}")
        r = base_r + i * step_r
        ang = _angle_from_name(f"{sys_name}:{pname}")
        x = r * math.cos(ang)
        z = r * math.sin(ang)
        y = 0.0
        item = {
            "type": "planet",
            "name": pname,
            "region": region,
            "x": x,
            "y": y,
            "z": z,
        }
        # Keep planet attributes for the info panel
        for key, val in p.items():
            if key not in ("x", "y", "z"):
                item[key] = val
        data.append(item)
        # Moons
        moons = p.get("moons") or []
        for j, m in enumerate(moons):
            mname = m.get("name", f"Moon {j+1}")
            mr = r + 0.6 + j * 0.25
            mang = _angle_from_name(f"{sys_name}:{pname}:{mname}")
            mx = mr * math.cos(mang)
            mz = mr * math.sin(mang)
            my = 0.0
            mitem = {
                "type": "moon",
                "name": mname,
                "region": region,
                "x": mx,
                "y": my,
                "z": mz,
            }
            for key, val in m.items():
                if key not in ("x", "y", "z"):
                    mitem[key] = val
            data.append(mitem)
    return data


def prepare_system_data(df: pd.DataFrame, region_filter: Optional[str] = None) -> List[dict]:
    """Prepare system data for System View - fully data-driven."""
    data = []
    
    # Filter by region if specified
    if region_filter:
        df = df[df["region"] == region_filter]
    
    for _, row in df.iterrows():
        # Skip region metadata entries
        if row.get("type") == "region":
            continue
            
        x, y, z = cartesian_to_orbital(
            float(row.get("x", 0) or 0),
            float(row.get("y", 0) or 0),
            float(row.get("z", 0) or 0)
        )
        
        # Build base item with all fields from JSON (data-driven)
        item = {
            "type": row.get("type", "system"),  # Use type from JSON or default to "system"
            "x": x,
            "y": z,  # Swap y and z for Three.js coordinate system
            "z": y,
        }
        
        # Copy all other fields from the row (data-driven approach)
        for key, value in row.items():
            if key not in ("x", "y", "z", "moons", "space_station", "space_stations"):
                # Handle different value types
                if isinstance(value, (list, dict)):
                    if value:  # Only add non-empty lists/dicts
                        item[key] = value
                elif pd.notna(value):
                    item[key] = value
        
        data.append(item)
        
        # Add moons if present
        moons = row.get("moons")
        if moons and isinstance(moons, list):
            for moon in moons:
                mx, my, mz = cartesian_to_orbital(
                    float(moon.get("x", 0) or 0),
                    float(moon.get("y", 0) or 0),
                    float(moon.get("z", 0) or 0)
                )
                moon_item = {
                    "type": "moon",
                    "x": mx,
                    "y": mz,
                    "z": my,
                }
                # Copy all moon fields
                for key, value in moon.items():
                    if key not in ("x", "y", "z"):
                        moon_item[key] = value
                data.append(moon_item)
        
        # Add space stations (handle both "space_station" singular and "space_stations" plural)
        station = row.get("space_station")
        stations = row.get("space_stations", [])
        
        # Convert singular to list
        if station and isinstance(station, dict):
            stations = [station]
        
        if stations and isinstance(stations, list):
            for station in stations:
                sx, sy, sz = cartesian_to_orbital(
                    float(station.get("x", 0) or 0),
                    float(station.get("y", 0) or 0),
                    float(station.get("z", 0) or 0)
                )
                station_item = {
                    "type": "station",
                    "x": sx,
                    "y": sz,
                    "z": sy,
                    "system": row.get("name")
                }
                # Copy all station fields
                for key, value in station.items():
                    if key not in ("x", "y", "z"):
                        station_item[key] = value
                data.append(station_item)
    
    return data



# ============================================================================
# RENDERING AND EXPORTING
# ============================================================================
def write_galaxy_and_system_views(df: pd.DataFrame, output: Path):
    """Generate Galaxy Overview (one point per system) and System View for each system."""
    # Galaxy overview
    galaxy_data = prepare_galaxy_systems_data(df)
    html = THREEJS_TEMPLATE.replace("__SYSTEM_DATA__", json.dumps(galaxy_data, indent=2))
    html = html.replace("__VIEW_MODE__", "galaxy")
    html = html.replace("__REGION_NAME__", "")
    html = html.replace("__SYSTEM_META__", json.dumps({}, indent=2))
    output.write_text(html, encoding="utf-8")
    print(f"Wrote Galaxy Overview: {output}")

    # Per-system solar view pages
    for _, row in df.iterrows():
        if row.get("type") == "region":
            continue
        system_name = row.get("name") or "system"
        system_file = output.parent / f"system_{safe_filename(system_name)}.html"
        solar = prepare_single_system_solar(row)
        # System meta for sun panel
        meta = {
            "name": system_name,
            "region": row.get("region"),
            "attributes": row.get("attributes"),
            "x": row.get("x"),
            "y": row.get("y"),
            "z": row.get("z"),
        }
        html = THREEJS_TEMPLATE.replace("__SYSTEM_DATA__", json.dumps(solar, indent=2))
        html = html.replace("__VIEW_MODE__", "system")
        html = html.replace("__REGION_NAME__", system_name)
        html = html.replace("__SYSTEM_META__", json.dumps(meta, indent=2))
        system_file.write_text(html, encoding="utf-8")
        print(f"Wrote System View for {system_name}: {system_file.name}")



# ============================================================================
# BROWSER UTILITIES
# ============================================================================

def find_msedge() -> Optional[str]:
    candidates = [
        shutil.which("msedge"),
        r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        r"C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
    ]
    for c in candidates:
        if c and Path(c).exists():
            return str(c)
    return None


def open_in_edge(path: Path, debug: bool = False) -> bool:
    msedge = find_msedge()
    uri = path.resolve().as_uri()
    if msedge:
        try:
            subprocess.Popen([msedge, "--new-window", uri], shell=False)
            return True
        except Exception as e:
            if debug:
                print("msedge launch failed:", e)
    try:
        webbrowser.open_new(uri)
        return True
    except Exception:
        return False



# ============================================================================
# COMMAND LINE INTERFACE / MAIN ENTRY POINT
# ============================================================================

def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", "-o", default=str(dist_dir() / "VH-Map.html"))
    p.add_argument("--no-open", action="store_true", help="Don't open the output after writing")
    p.add_argument("--debug", action="store_true")
    p.add_argument("--only", nargs="*", help="Only include systems with these names (case-sensitive)")
    p.add_argument("--limit", type=int, help="Limit to first N systems after filtering")
    p.add_argument("--data-file", default=str(DATA_FILE), help="Path to data JSON file (default: data/data.json)")
    args = p.parse_args(argv)

    data_file_path = Path(args.data_file)
    if not data_file_path.exists():
        print("Data file not found:", data_file_path)
        return 1

    df = load_systems(data_file_path)
    # Optional filtering
    if args.only:
        try:
            df = df[df["name"].isin(args.only)]
        except Exception:
            pass
    if args.limit and args.limit > 0:
        df = df.head(args.limit)
    out = Path(args.out)
    # Ensure output directory exists
    out.parent.mkdir(parents=True, exist_ok=True)
    write_galaxy_and_system_views(df, out)

    if not args.no_open:
        opened = open_in_edge(out, debug=args.debug)
        if not opened:
            print("Could not open in Edge; try opening", out)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
