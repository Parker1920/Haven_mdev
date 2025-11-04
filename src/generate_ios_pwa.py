"""
Generate Haven iOS PWA - Mobile Progressive Web App
Creates a self-contained HTML file with:
- 3D map viewer (touch-optimized)
- Data entry form (mobile-friendly)
- Local storage persistence
- Offline capability
- Install to home screen support
"""

from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
import logging

from common.paths import data_path, dist_dir, config_dir

def generate_ios_pwa(output_path: Path | None = None, include_data: bool = True, embed_three: bool = False) -> Path:
    """
    Generate mobile PWA HTML bundle.
    
    Args:
        output_path: Where to write the HTML (default: dist/Haven_iOS.html)
        include_data: Whether to pre-load existing data.json
    
    Returns:
        Path to generated HTML file
    """
    if output_path is None:
        output_path = dist_dir() / 'Haven_iOS.html'
    
    # Load existing data if requested
    initial_data = []
    if include_data:
        try:
            data_file = data_path('data.json')
            if data_file.exists():
                raw = json.loads(data_file.read_text(encoding='utf-8'))
                if isinstance(raw, dict) and 'data' in raw:
                    initial_data = raw['data']
                elif isinstance(raw, list):
                    initial_data = raw
        except Exception as e:
            logging.warning(f"Could not load data.json for iOS PWA: {e}")
    
    # Generate the PWA HTML
    html = generate_pwa_html(initial_data, embed_three=embed_three)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding='utf-8')
    
    logging.info(f"Generated iOS PWA: {output_path}")
    return output_path


def generate_pwa_html(initial_data: list, embed_three: bool = False) -> str:
    """Generate the complete PWA HTML with embedded JS and CSS."""
    
    initial_data_json = json.dumps(initial_data, ensure_ascii=False, indent=2)
    # Try to inline three.js if requested
    three_inline = None
    if embed_three:
        try:
            vendor_dir = config_dir() / 'vendor'
            candidates = [
                vendor_dir / 'three.r128.min.js',
                vendor_dir / 'three.min.js',
                vendor_dir / 'three-0.128.0.min.js'
            ]
            for c in candidates:
                if c.exists():
                    three_inline = c.read_text(encoding='utf-8')
                    break
        except Exception as e:
            logging.warning(f"Offline PWA: could not read local three.js: {e}")
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Haven Galaxy">
    <meta name="theme-color" content="#0a0e27">
    <title>Haven Galaxy - Mobile</title>
    <!-- iOS Home Screen Icon -->
    <link rel="apple-touch-icon" sizes="180x180" href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO4sUuUAAAAASUVORK5CYII=">
    <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }}
        
        body {{
            font-family: 'Rajdhani', sans-serif;
            background: linear-gradient(135deg, #0a0e27 0%, #1a1a2e 50%, #0f0f1e 100%);
            color: #ffffff;
            overflow-x: hidden;
            touch-action: pan-x pan-y;
            -webkit-user-select: none;
            user-select: none;
        }}
        
        /* Safe area insets for iPhone notch */
        body {{
            padding-top: env(safe-area-inset-top);
            padding-bottom: env(safe-area-inset-bottom);
        }}
        
        /* Header */
        #app-header {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: rgba(10, 14, 39, 0.95);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(0, 206, 209, 0.3);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 16px;
            z-index: 1000;
            padding-top: env(safe-area-inset-top);
        }}
        
        #app-title {{
            font-size: 18px;
            font-weight: 700;
            color: #00d9ff;
            letter-spacing: 1px;
        }}
        
        /* Tab navigation */
        #tab-nav {{
            display: flex;
            gap: 8px;
        }}
        
        .tab-btn {{
            padding: 8px 16px;
            background: rgba(0, 206, 209, 0.1);
            border: 1px solid rgba(0, 206, 209, 0.3);
            border-radius: 6px;
            color: #00d9ff;
            font-family: 'Rajdhani', sans-serif;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .tab-btn.active {{
            background: rgba(0, 206, 209, 0.3);
            border-color: #00d9ff;
        }}
        
        /* Main content */
        #app-content {{
            position: fixed;
            top: 60px;
            left: 0;
            right: 0;
            bottom: 0;
            overflow-y: auto;
            -webkit-overflow-scrolling: touch;
        }}
        
        /* Map view */
        #map-view {{
            width: 100%;
            height: 100%;
            position: relative;
        }}
        
        #map-canvas {{
            width: 100%;
            height: 100%;
            display: block;
            touch-action: none;
        }}
        
        #map-info {{
            position: absolute;
            top: 16px;
            left: 16px;
            right: 16px;
            background: rgba(10, 20, 40, 0.9);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 206, 209, 0.4);
            border-radius: 12px;
            padding: 12px;
            max-height: 200px;
            overflow-y: auto;
            display: none;
        }}
        
        #map-info h3 {{
            color: #00d9ff;
            font-size: 16px;
            margin-bottom: 8px;
        }}
        
        #map-info p {{
            font-size: 13px;
            line-height: 1.6;
            margin: 4px 0;
        }}
        
    #map-controls {{
            position: absolute;
            bottom: 16px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 8px;
            background: rgba(10, 20, 40, 0.9);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 206, 209, 0.4);
            border-radius: 24px;
            padding: 8px 16px;
        }}
        
        .map-btn {{
            padding: 8px 12px;
            background: rgba(0, 206, 209, 0.2);
            border: 1px solid rgba(0, 206, 209, 0.4);
            border-radius: 6px;
            color: #00d9ff;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
        }}

        /* Map select */
        .map-select {{
            padding: 6px 10px;
            background: rgba(0, 206, 209, 0.15);
            border: 1px solid rgba(0, 206, 209, 0.4);
            border-radius: 6px;
            color: #00d9ff;
            font-size: 12px;
            font-weight: 600;
        }}
        
        /* Segmented view toggle */
        .segmented {{
            display: inline-flex;
            border: 1px solid rgba(0, 206, 209, 0.4);
            border-radius: 8px;
            overflow: hidden;
        }}
        .segmented button {{
            padding: 6px 10px;
            background: transparent;
            border: none;
            color: #00d9ff;
            font-weight: 700;
        }}
        .segmented button.active {{
            background: rgba(0, 206, 209, 0.25);
            color: #0a0e27;
        }}
        
        /* Data entry view */
        #data-view {{
            padding: 20px 16px;
            max-width: 600px;
            margin: 0 auto;
            display: none;
        }}
        
        .form-section {{
            background: rgba(20, 27, 61, 0.6);
            border: 1px solid rgba(0, 206, 209, 0.3);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
        }}
        
        .form-section h3 {{
            color: #00d9ff;
            font-size: 16px;
            margin-bottom: 12px;
            font-weight: 600;
        }}
        
        .form-field {{
            margin-bottom: 12px;
        }}
        
        .form-field label {{
            display: block;
            color: #8892b0;
            font-size: 13px;
            margin-bottom: 6px;
            font-weight: 500;
        }}
        
        .form-field input,
        .form-field select,
        .form-field textarea {{
            width: 100%;
            padding: 12px;
            background: rgba(10, 14, 39, 0.8);
            border: 1px solid rgba(0, 206, 209, 0.3);
            border-radius: 8px;
            color: #ffffff;
            font-family: 'Rajdhani', sans-serif;
            font-size: 14px;
        }}
        
        .form-field textarea {{
            resize: vertical;
            min-height: 80px;
        }}
        
        .form-actions {{
            display: flex;
            gap: 12px;
            margin-top: 16px;
        }}
        
        .btn {{
            flex: 1;
            padding: 14px;
            border-radius: 8px;
            font-family: 'Rajdhani', sans-serif;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            border: none;
            transition: all 0.2s;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #00d9ff 0%, #00a3cc 100%);
            color: #0a0e27;
        }}
        
        .btn-secondary {{
            background: rgba(0, 206, 209, 0.2);
            border: 1px solid rgba(0, 206, 209, 0.4);
            color: #00d9ff;
        }}
        
        .btn-danger {{
            background: rgba(255, 0, 110, 0.2);
            border: 1px solid rgba(255, 0, 110, 0.4);
            color: #ff006e;
        }}
        
        /* Systems list */
        #systems-list {{
            margin-top: 16px;
        }}
        
        .system-item {{
            background: rgba(10, 14, 39, 0.6);
            border: 1px solid rgba(0, 206, 209, 0.2);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .system-item:active {{
            background: rgba(0, 206, 209, 0.1);
        }}
        
        .system-item h4 {{
            color: #00d9ff;
            font-size: 15px;
            margin-bottom: 4px;
        }}
        
        .system-item p {{
            color: #8892b0;
            font-size: 13px;
        }}
        
        /* Toast notifications */
        #toast {{
            position: fixed;
            bottom: 80px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 206, 209, 0.95);
            color: #0a0e27;
            padding: 12px 24px;
            border-radius: 24px;
            font-weight: 600;
            display: none;
            z-index: 2000;
        }}
        
        /* Loading overlay */
        #loading {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(10, 14, 39, 0.95);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        }}
        
        .spinner {{
            width: 48px;
            height: 48px;
            border: 4px solid rgba(0, 206, 209, 0.2);
            border-top-color: #00d9ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        
        #loading p {{
            margin-top: 20px;
            color: #00d9ff;
            font-size: 16px;
            letter-spacing: 1px;
        }}
        
        /* Utility classes */
        .hidden {{ display: none !important; }}
    </style>
</head>
<body>
    <!-- Loading overlay -->
    <div id="loading">
        <div class="spinner"></div>
        <p>INITIALIZING...</p>
        <p id="loading-detail" style="font-size:12px; margin-top:10px; color:#8892b0;"></p>
        <button id="retry-btn" style="display:none; margin-top:20px; padding:12px 24px; background:#00d9ff; color:#0a0e27; border:none; border-radius:8px; font-weight:700; font-size:14px;">Retry</button>
        <button id="skip-map-btn" style="display:none; margin-top:10px; padding:12px 24px; background:rgba(0,206,209,0.2); border:1px solid rgba(0,206,209,0.4); color:#00d9ff; border-radius:8px; font-weight:600; font-size:14px;">Skip Map, Use Data Entry Only</button>
    </div>
    
    <!-- App header -->
    <header id="app-header">
        <div id="app-title">HAVEN GALAXY</div>
        <div id="tab-nav">
            <button class="tab-btn active" data-tab="map">Map</button>
            <button class="tab-btn" data-tab="data">Data</button>
        </div>
    </header>
    
    <!-- Main content -->
    <div id="app-content">
        <!-- Map view -->
        <div id="map-view">
            <div id="map-canvas"></div>
            <div id="map-info">
                <h3 id="map-info-title">System Information</h3>
                <div id="map-info-content">Tap a system to view details</div>
            </div>
            <div id="map-controls">
                <div class="segmented" id="view-toggle">
                    <button id="btn-view-galaxy" class="active">Galaxy</button>
                    <button id="btn-view-system" disabled>System</button>
                </div>
                <select id="region-filter" class="map-select">
                    <option value="All">All Regions</option>
                </select>
                <button class="map-btn" id="btn-reset">Reset View</button>
                <button class="map-btn" id="btn-grid">Grid</button>
            </div>
        </div>
        
        <!-- Data entry view -->
        <div id="data-view">
            <!-- System form -->
            <div class="form-section">
                <h3 id="form-title">Add New System</h3>
                <div class="form-field">
                    <label>System Name *</label>
                    <input type="text" id="input-name" placeholder="e.g., Kepler-442" required>
                </div>
                <div class="form-field">
                    <label>Region</label>
                    <input type="text" id="input-region" placeholder="e.g., Orion Arm">
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px;">
                    <div class="form-field">
                        <label>X Coordinate *</label>
                        <input type="number" step="any" id="input-x" placeholder="0.0" required>
                    </div>
                    <div class="form-field">
                        <label>Y Coordinate *</label>
                        <input type="number" step="any" id="input-y" placeholder="0.0" required>
                    </div>
                    <div class="form-field">
                        <label>Z Coordinate *</label>
                        <input type="number" step="any" id="input-z" placeholder="0.0" required>
                    </div>
                </div>
                <div class="form-field">
                    <label>Planets (comma-separated)</label>
                    <input type="text" id="input-planets" placeholder="e.g., Terra, Mars">
                </div>
                <div class="form-field">
                    <label>Fauna Count</label>
                    <input type="number" id="input-fauna" placeholder="0">
                </div>
                <div class="form-field">
                    <label>Flora Count</label>
                    <input type="number" id="input-flora" placeholder="0">
                </div>
                <div class="form-field">
                    <label>Sentinel Level</label>
                    <select id="input-sentinel">
                        <option value="">None</option>
                        <option value="Low">Low</option>
                        <option value="Medium">Medium</option>
                        <option value="High">High</option>
                        <option value="Aggressive">Aggressive</option>
                    </select>
                </div>
                <div class="form-field">
                    <label>Materials</label>
                    <textarea id="input-materials" placeholder="List key materials..."></textarea>
                </div>
                <div class="form-field">
                    <label>Base Location</label>
                    <input type="text" id="input-base" placeholder="e.g., Planet 2, Coordinates 123,456">
                </div>
                <div class="form-actions">
                    <button class="btn btn-secondary" id="btn-clear">Clear</button>
                    <button class="btn btn-primary" id="btn-save">Save</button>
                </div>
            </div>
            
            <!-- Systems list -->
            <div class="form-section">
                <h3>Your Systems (<span id="system-count">0</span>)</h3>
                <div id="systems-list"></div>
                <div class="form-actions">
                    <button class="btn btn-secondary" id="btn-export">Export JSON</button>
                    <button class="btn btn-secondary" id="btn-import">Import JSON</button>
                </div>
                <input type="file" id="file-input" accept=".json" style="display:none;">
            </div>
        </div>
    </div>
    
    <!-- Toast notification -->
    <div id="toast"></div>
    
    <!-- Three.js loader: inline if available, else multi-CDN fallback -->
    {(r'''<script>
// Offline mode enabled
window.HAVEN_OFFLINE = true;
</script>
<script>
/* three.js r128 (MIT) — embedded for offline use */
''' + three_inline.replace('\\','\\\\').replace('</','<\\/') + '\n</script>') if three_inline else '''
    <script>
        (function() {{
            window.HAVEN_OFFLINE = false;
            var cdnList = [
                'https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js',
                'https://unpkg.com/three@0.128.0/build/three.min.js',
                'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js'
            ];
            var loading = document.getElementById('loading');
            var detail = document.getElementById('loading-detail');
            var timeoutHandle = null;
            function setDetail(msg) {{ if (detail) detail.textContent = msg; }}
            function loadScript(url, onload, onerror, timeoutMs) {{
                var s = document.createElement('script');
                s.src = url; s.crossOrigin = 'anonymous'; s.onload = onload; s.onerror = onerror;
                document.head.appendChild(s);
                timeoutHandle = setTimeout(function() {{ onerror(new Error('timeout')); }}, timeoutMs || 10000);
            }}
            function tryIndex(i) {{
                if (i >= cdnList.length) {{
                    if (loading) {{
                        loading.querySelector('p').textContent = 'ERROR: 3D Library Unavailable';
                        setDetail('Unable to load 3D library. Use Retry or Skip Map. If opened from Mail preview, use Open in Safari.');
                        var spinner = loading.querySelector('.spinner'); if (spinner) spinner.style.display = 'none';
                        var retryBtn = document.getElementById('retry-btn'); var skipBtn = document.getElementById('skip-map-btn');
                        if (retryBtn) retryBtn.style.display = 'inline-block'; if (skipBtn) skipBtn.style.display = 'inline-block';
                    }}
                    return; }}
                var url = cdnList[i]; setDetail('Loading 3D library (' + (i+1) + '/' + cdnList.length + ')…');
                loadScript(url, function() {{ if (timeoutHandle) {{ clearTimeout(timeoutHandle); timeoutHandle = null; }} setDetail('3D library loaded.'); }}, function() {{ if (timeoutHandle) {{ clearTimeout(timeoutHandle); timeoutHandle = null; }} tryIndex(i+1); }}, 10000);
            }}
            tryIndex(0);
        }})();
    </script>'''}

    <!-- Mode indicator: show if offline or online loading path -->
    <script>
        (function() {{
            try {{
                var detail = document.getElementById('loading-detail');
                if (typeof window.HAVEN_OFFLINE !== 'undefined' && window.HAVEN_OFFLINE) {{
                    if (detail) detail.textContent = 'Offline mode: embedded 3D library loaded.';
                }}
            }} catch (e) {{}}
        }})();
    </script>
    
    <script>
        // Error handling for iOS
        window.addEventListener('error', function(e) {{
            console.error('Global error:', e.message, e.filename, e.lineno);
            var detail = document.getElementById('loading-detail');
            if (detail) {{
                detail.textContent = 'Error: ' + e.message + ' at line ' + e.lineno;
            }}
        }});
        
        // Log diagnostics for iOS debugging
        var detail = document.getElementById('loading-detail');
        if (detail) detail.textContent = 'Loading 3D library...';
        
        // === Data Management ===
        const STORAGE_KEY = 'haven_systems_data';
        var systemsData = {initial_data_json};
        var currentView = 'galaxy'; // 'galaxy' | 'system'
        var selectedSystemIndex = null;
        
        function saveData() {{
            try {{
                localStorage.setItem(STORAGE_KEY, JSON.stringify(systemsData));
                return true;
            }} catch (e) {{
                console.error('Failed to save data:', e);
                return false;
            }}
        }}
        
        function loadData() {{
            try {{
                const stored = localStorage.getItem(STORAGE_KEY);
                if (stored) {{
                    systemsData = JSON.parse(stored);
                }}
            }} catch (e) {{
                console.error('Failed to load data:', e);
            }}
        }}
        
        function showToast(message, duration = 2000) {{
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.style.display = 'block';
            setTimeout(() => {{
                toast.style.display = 'none';
            }}, duration);
        }}
        
        // === Tab Navigation ===
        const tabBtns = document.querySelectorAll('.tab-btn');
        const mapView = document.getElementById('map-view');
        const dataView = document.getElementById('data-view');
        
        tabBtns.forEach(btn => {{
            btn.addEventListener('click', () => {{
                const tab = btn.dataset.tab;
                tabBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                if (tab === 'map') {{
                    mapView.style.display = 'block';
                    dataView.style.display = 'none';
                    if (window.map3d) window.map3d.resize();
                }} else {{
                    mapView.style.display = 'none';
                    dataView.style.display = 'block';
                    renderSystemsList();
                }}
            }});
        }});
        
        // === 3D Map Setup ===
        class Map3D {{
            constructor(container) {{
                if (!container) {{
                    throw new Error('Map container not found');
                }}
                
                this.container = container;
                this.scene = new THREE.Scene();
                this.scene.background = new THREE.Color(0x0a0e27);
                
                var width = container.clientWidth || window.innerWidth;
                var height = container.clientHeight || window.innerHeight;
                
                this.camera = new THREE.PerspectiveCamera(
                    60,
                    width / height,
                    0.1,
                    1000
                );
                this.camera.position.set(30, 30, 30);
                this.camera.lookAt(0, 0, 0);
                
                // iOS-friendly WebGL settings
                var rendererOptions = {{ 
                    antialias: true,
                    alpha: false,
                    powerPreference: 'high-performance'
                }};
                
                this.renderer = new THREE.WebGLRenderer(rendererOptions);
                this.renderer.setSize(width, height);
                this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // Limit for iOS performance
                container.appendChild(this.renderer.domElement);
                
                // Lighting
                const ambient = new THREE.AmbientLight(0x404040, 0.6);
                this.scene.add(ambient);
                
                const point = new THREE.PointLight(0xffd700, 1.5, 300);
                point.position.set(0, 0, 0);
                this.scene.add(point);
                
                // Starfield
                this.addStarfield();
                
                // Grid
                this.gridVisible = true;
                this.grid = new THREE.GridHelper(100, 20, 0x00ced1, 0x003a3a);
                this.grid.material.transparent = true;
                this.grid.material.opacity = 0.3;
                this.scene.add(this.grid);
                
                // Touch controls
                this.setupTouchControls();
                
                // Objects
                this.objects = [];
                this.raycaster = new THREE.Raycaster();
                this.selectedObject = null;
                
                this.animate();
            }}
            
            addStarfield() {{
                const geometry = new THREE.BufferGeometry();
                const vertices = [];
                for (let i = 0; i < 2000; i++) {{
                    vertices.push(
                        (Math.random() - 0.5) * 500,
                        (Math.random() - 0.5) * 500,
                        (Math.random() - 0.5) * 500
                    );
                }}
                geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
                const material = new THREE.PointsMaterial({{ color: 0xffffff, size: 0.5, transparent: true, opacity: 0.7 }});
                const stars = new THREE.Points(geometry, material);
                this.scene.add(stars);
            }}
            
            setupTouchControls() {{
                const canvas = this.renderer.domElement;
                let touches = {{}};
                let lastDist = 0;
                let lastAngle = 0;
                
                canvas.addEventListener('touchstart', (e) => {{
                    e.preventDefault();
                    Array.from(e.touches).forEach(t => {{
                        touches[t.identifier] = {{ x: t.clientX, y: t.clientY }};
                    }});
                    
                    if (e.touches.length === 1) {{
                        // Single touch: check for tap
                        this.handleTap(e.touches[0]);
                    }} else if (e.touches.length === 2) {{
                        const dx = touches[1].x - touches[0].x;
                        const dy = touches[1].y - touches[0].y;
                        lastDist = Math.sqrt(dx*dx + dy*dy);
                        lastAngle = Math.atan2(dy, dx);
                    }}
                }}, {{ passive: false }});
                
                canvas.addEventListener('touchmove', (e) => {{
                    e.preventDefault();
                    const newTouches = {{}};
                    Array.from(e.touches).forEach(t => {{
                        newTouches[t.identifier] = {{ x: t.clientX, y: t.clientY }};
                    }});
                    
                    if (e.touches.length === 1 && touches[0]) {{
                        // Pan/rotate
                        const dx = newTouches[0].x - touches[0].x;
                        const dy = newTouches[0].y - touches[0].y;
                        
                        const angle = Math.atan2(this.camera.position.z, this.camera.position.x);
                        const radius = Math.sqrt(this.camera.position.x**2 + this.camera.position.z**2);
                        
                        this.camera.position.x = radius * Math.cos(angle - dx * 0.01);
                        this.camera.position.z = radius * Math.sin(angle - dx * 0.01);
                        this.camera.position.y += dy * 0.1;
                        this.camera.lookAt(0, 0, 0);
                    }} else if (e.touches.length === 2 && touches[0] && touches[1]) {{
                        // Pinch zoom
                        const dx = newTouches[1].x - newTouches[0].x;
                        const dy = newTouches[1].y - newTouches[0].y;
                        const newDist = Math.sqrt(dx*dx + dy*dy);
                        
                        if (lastDist > 0) {{
                            const scale = newDist / lastDist;
                            const len = Math.sqrt(
                                this.camera.position.x**2 +
                                this.camera.position.y**2 +
                                this.camera.position.z**2
                            );
                            const newLen = Math.max(10, Math.min(100, len / scale));
                            const factor = newLen / len;
                            this.camera.position.multiplyScalar(factor);
                        }}
                        lastDist = newDist;
                    }}
                    
                    touches = newTouches;
                }}, {{ passive: false }});
                
                canvas.addEventListener('touchend', (e) => {{
                    e.preventDefault();
                    touches = {{}};
                    lastDist = 0;
                }}, {{ passive: false }});
            }}
            
            handleTap(touch) {{
                const rect = this.renderer.domElement.getBoundingClientRect();
                const x = ((touch.clientX - rect.left) / rect.width) * 2 - 1;
                const y = -((touch.clientY - rect.top) / rect.height) * 2 + 1;
                
                this.raycaster.setFromCamera({{ x, y }}, this.camera);
                const intersects = this.raycaster.intersectObjects(this.objects.map(o => o.mesh));
                
                if (intersects.length > 0) {{
                    const obj = this.objects.find(o => o.mesh === intersects[0].object);
                    if (obj) {{
                        if (currentView === 'galaxy') {{
                            // Attempt to find the selected system by exact coordinate match
                            const pos = obj.mesh.position;
                            const idx = systemsData.findIndex(s => s && s.x === pos.x && s.y === pos.y && s.z === pos.z);
                            selectedSystemIndex = idx >= 0 ? idx : null;
                            // Enable System view button if a system is selected
                            const sysBtn = document.getElementById('btn-view-system');
                            if (sysBtn) sysBtn.disabled = (selectedSystemIndex === null);
                            this.showSystemInfo(obj.data);
                                if (selectedSystemIndex !== null) {{
                                    // Auto-switch to system view for mobile convenience
                                    if (typeof setView === 'function') setView('system');
                                }}
                        }} else {{
                            // Planet/system detail taps could be handled here if desired
                        }}
                    }}
                }} else {{
                    document.getElementById('map-info').style.display = 'none';
                }}
            }}
            
            showSystemInfo(system) {{
                const info = document.getElementById('map-info');
                const title = document.getElementById('map-info-title');
                const content = document.getElementById('map-info-content');
                
                title.textContent = system.name || 'Unknown System';
                
                let html = '';
                if (system.region) html += `<p><strong>Region:</strong> ${{system.region}}</p>`;
                html += `<p><strong>Coordinates:</strong> X:${{system.x}}, Y:${{system.y}}, Z:${{system.z}}</p>`;
                if (system.planets && system.planets.length) {{
                    html += `<p><strong>Planets:</strong> ${{system.planets.join(', ')}}</p>`;
                }}
                if (system.fauna) html += `<p><strong>Fauna:</strong> ${{system.fauna}}</p>`;
                if (system.flora) html += `<p><strong>Flora:</strong> ${{system.flora}}</p>`;
                if (system.sentinel) html += `<p><strong>Sentinels:</strong> ${{system.sentinel}}</p>`;
                
                content.innerHTML = html;
                info.style.display = 'block';
            }}
            
            loadGalaxy(systems) {{
                // Clear existing objects
                this.objects.forEach(obj => {{
                    this.scene.remove(obj.mesh);
                    if (obj.glow) this.scene.remove(obj.glow);
                }});
                this.objects = [];
                
                // Create objects for each system
                systems.forEach(sys => {{
                    if (sys.x == null || sys.y == null || sys.z == null) return;
                    
                    const geometry = new THREE.OctahedronGeometry(0.5);
                    const material = new THREE.MeshPhongMaterial({{
                        color: 0x00ced1,
                        emissive: 0x005f60,
                        emissiveIntensity: 0.2
                    }});
                    const mesh = new THREE.Mesh(geometry, material);
                    mesh.position.set(sys.x, sys.y, sys.z);
                    this.scene.add(mesh);
                    
                    // Glow
                    const glowGeometry = new THREE.OctahedronGeometry(0.8);
                    const glowMaterial = new THREE.MeshBasicMaterial({{
                        color: 0x00ffff,
                        transparent: true,
                        opacity: 0.15
                    }});
                    const glow = new THREE.Mesh(glowGeometry, glowMaterial);
                    glow.position.copy(mesh.position);
                    this.scene.add(glow);
                    
                    this.objects.push({{ mesh, glow, data: sys }});
                }});
            }}

            loadSystem(system) {{
                // Clear existing objects
                this.objects.forEach(obj => {{
                    this.scene.remove(obj.mesh);
                    if (obj.glow) this.scene.remove(obj.glow);
                }});
                this.objects = [];

                // Star at origin
                const starGeo = new THREE.SphereGeometry(1.2, 24, 24);
                const starMat = new THREE.MeshPhongMaterial({{ color: 0xffd27f, emissive: 0x6b3e00, emissiveIntensity: 0.6 }});
                const star = new THREE.Mesh(starGeo, starMat);
                this.scene.add(star);

                // Planets
                const names = (system && system.planets && system.planets.length) ? system.planets : ['Planet A','Planet B'];
                const baseRadius = 4;
                names.forEach((name, idx) => {{
                    const orbitR = baseRadius + idx * 3.2;
                    const ringGeo = new THREE.RingGeometry(orbitR - 0.02, orbitR + 0.02, 64);
                    const ringMat = new THREE.MeshBasicMaterial({{ color: 0x00ced1, transparent: true, opacity: 0.25, side: THREE.DoubleSide }});
                    const ring = new THREE.Mesh(ringGeo, ringMat);
                    ring.rotation.x = Math.PI / 2;
                    this.scene.add(ring);

                    const pGeo = new THREE.SphereGeometry(0.6 + (idx % 3) * 0.15, 18, 18);
                    const colors = [0x66ccff, 0x99ff99, 0xff99cc, 0xffcc66];
                    // Use unlit material to avoid grey/specular shading artifacts on iOS
                    const pMat = new THREE.MeshBasicMaterial({{ color: colors[idx % colors.length] }});
                    const planet = new THREE.Mesh(pGeo, pMat);
                    planet.position.set(orbitR, 0, 0);
                    this.scene.add(planet);

                    this.objects.push({{ mesh: planet, data: {{ type: 'planet', name }} }});
                }});

                this.camera.position.set(0, 15, 18);
                this.camera.lookAt(0, 0, 0);
            }}
            
            resetView() {{
                if (currentView === 'galaxy') {{
                    this.camera.position.set(30, 30, 30);
                }} else {{
                    this.camera.position.set(0, 15, 18);
                }}
                this.camera.lookAt(0, 0, 0);
            }}
            
            toggleGrid() {{
                this.gridVisible = !this.gridVisible;
                this.grid.visible = this.gridVisible;
                return this.gridVisible;
            }}
            
            resize() {{
                const width = this.container.clientWidth;
                const height = this.container.clientHeight;
                this.camera.aspect = width / height;
                this.camera.updateProjectionMatrix();
                this.renderer.setSize(width, height);
            }}
            
            animate() {{
                requestAnimationFrame(() => this.animate());
                
                // Rotate glow effects
                this.objects.forEach(obj => {{
                    if (obj.glow) {{
                        obj.glow.rotation.y += 0.01;
                    }}
                }});
                
                this.renderer.render(this.scene, this.camera);
            }}
        }}
        
        // === Data Entry Functions ===
        let editingIndex = null;
        
        function clearForm() {{
            editingIndex = null;
            document.getElementById('form-title').textContent = 'Add New System';
            document.getElementById('input-name').value = '';
            document.getElementById('input-region').value = '';
            document.getElementById('input-x').value = '';
            document.getElementById('input-y').value = '';
            document.getElementById('input-z').value = '';
            document.getElementById('input-planets').value = '';
            document.getElementById('input-fauna').value = '';
            document.getElementById('input-flora').value = '';
            document.getElementById('input-sentinel').value = '';
            document.getElementById('input-materials').value = '';
            document.getElementById('input-base').value = '';
        }}
        
        function loadFormData(index) {{
            editingIndex = index;
            const sys = systemsData[index];
            document.getElementById('form-title').textContent = 'Edit System';
            document.getElementById('input-name').value = sys.name || '';
            document.getElementById('input-region').value = sys.region || '';
            document.getElementById('input-x').value = sys.x || '';
            document.getElementById('input-y').value = sys.y || '';
            document.getElementById('input-z').value = sys.z || '';
            document.getElementById('input-planets').value = (sys.planets || []).join(', ');
            document.getElementById('input-fauna').value = sys.fauna || '';
            document.getElementById('input-flora').value = sys.flora || '';
            document.getElementById('input-sentinel').value = sys.sentinel || '';
            document.getElementById('input-materials').value = sys.materials || '';
            document.getElementById('input-base').value = sys.base_location || '';
            
            // Scroll to top
            dataView.scrollTop = 0;
        }}
        
        function saveSystem() {{
            const name = document.getElementById('input-name').value.trim();
            const x = parseFloat(document.getElementById('input-x').value);
            const y = parseFloat(document.getElementById('input-y').value);
            const z = parseFloat(document.getElementById('input-z').value);
            
            if (!name || isNaN(x) || isNaN(y) || isNaN(z)) {{
                showToast('Name and coordinates are required', 3000);
                return;
            }}
            
            const system = {{
                name,
                region: document.getElementById('input-region').value.trim(),
                x, y, z,
                planets: document.getElementById('input-planets').value.split(',').map(p => p.trim()).filter(p => p),
                fauna: parseInt(document.getElementById('input-fauna').value) || null,
                flora: parseInt(document.getElementById('input-flora').value) || null,
                sentinel: document.getElementById('input-sentinel').value || null,
                materials: document.getElementById('input-materials').value.trim() || null,
                base_location: document.getElementById('input-base').value.trim() || null
            }};
            
            if (editingIndex !== null) {{
                systemsData[editingIndex] = system;
                showToast('System updated');
            }} else {{
                systemsData.push(system);
                showToast('System added');
            }}
            
            saveData();
            clearForm();
            renderSystemsList();
            
            // Update map if visible
            if (window.map3d) {{
                if (currentView === 'galaxy') {{
                    window.map3d.loadGalaxy(getFilteredSystems());
                }} else if (selectedSystemIndex != null) {{
                    window.map3d.loadSystem(systemsData[selectedSystemIndex]);
                }}
            }}
        }}
        
        function deleteSystem(index) {{
            if (confirm('Delete this system?')) {{
                systemsData.splice(index, 1);
                saveData();
                renderSystemsList();
                showToast('System deleted');
                
                if (window.map3d) {{
                    if (currentView === 'galaxy') {{
                        window.map3d.loadGalaxy(getFilteredSystems());
                    }} else if (selectedSystemIndex != null) {{
                        window.map3d.loadSystem(systemsData[selectedSystemIndex]);
                    }}
                }}
            }}
        }}
        
        function renderSystemsList() {{
            const list = document.getElementById('systems-list');
            const count = document.getElementById('system-count');
            count.textContent = systemsData.length;
            
            if (systemsData.length === 0) {{
                list.innerHTML = '<p style="color:#8892b0; text-align:center; padding:20px;">No systems yet</p>';
                return;
            }}
            
            list.innerHTML = systemsData.map((sys, i) => `
                <div class="system-item">
                    <h4>${{sys.name || 'Unnamed'}}</h4>
                    <p>X:${{sys.x}}, Y:${{sys.y}}, Z:${{sys.z}}</p>
                    <div style="display:flex; gap:8px; margin-top:8px;">
                        <button class="btn btn-secondary" style="flex:1; padding:8px; font-size:13px;" onclick="loadFormData(${{i}})">Edit</button>
                        <button class="btn btn-danger" style="flex:1; padding:8px; font-size:13px;" onclick="deleteSystem(${{i}})">Delete</button>
                    </div>
                </div>
            `).join('');
        }}
        
        function exportData() {{
            const json = JSON.stringify(systemsData, null, 2);
            const blob = new Blob([json], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `haven_systems_${{new Date().toISOString().split('T')[0]}}.json`;
            a.click();
            URL.revokeObjectURL(url);
            showToast('Data exported');
        }}
        
        function importData() {{
            document.getElementById('file-input').click();
        }}
        
        document.getElementById('file-input').addEventListener('change', (e) => {{
            const file = e.target.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = (ev) => {{
                try {{
                    const data = JSON.parse(ev.target.result);
                    if (Array.isArray(data)) {{
                        systemsData = data;
                    }} else if (data.data && Array.isArray(data.data)) {{
                        systemsData = data.data;
                    }} else {{
                        throw new Error('Invalid format');
                    }}
                    saveData();
                    renderSystemsList();
                    showToast('Data imported');
                    
                    if (window.map3d) {{
                        if (currentView === 'galaxy') {{
                            window.map3d.loadGalaxy(getFilteredSystems());
                        }} else if (selectedSystemIndex != null) {{
                            window.map3d.loadSystem(systemsData[selectedSystemIndex]);
                        }}
                    }}
                }} catch (err) {{
                    showToast('Import failed: Invalid JSON', 3000);
                    console.error(err);
                }}
            }};
            reader.readAsText(file);
            e.target.value = '';
        }});
        
        // === Event Listeners ===
        document.getElementById('btn-clear').addEventListener('click', clearForm);
        document.getElementById('btn-save').addEventListener('click', saveSystem);
        document.getElementById('btn-export').addEventListener('click', exportData);
        document.getElementById('btn-import').addEventListener('click', importData);
        
        document.getElementById('btn-reset').addEventListener('click', () => {{
            if (window.map3d) window.map3d.resetView();
        }});
        
        document.getElementById('btn-grid').addEventListener('click', () => {{
            if (window.map3d) {{
                const visible = window.map3d.toggleGrid();
                document.getElementById('btn-grid').textContent = visible ? 'Grid' : 'Grid Off';
            }}
        }});
        
        window.addEventListener('resize', () => {{
            if (window.map3d) window.map3d.resize();
        }});
        
        // View toggle
        function setView(mode) {{
            currentView = mode;
            const gBtn = document.getElementById('btn-view-galaxy');
            const sBtn = document.getElementById('btn-view-system');
            if (gBtn && sBtn) {{
                gBtn.classList.toggle('active', mode === 'galaxy');
                sBtn.classList.toggle('active', mode === 'system');
            }}
            if (!window.map3d) return;
            if (mode === 'galaxy') {{
                window.map3d.loadGalaxy(getFilteredSystems());
            }} else {{
                if (selectedSystemIndex == null && systemsData.length) selectedSystemIndex = 0;
                if (selectedSystemIndex != null) window.map3d.loadSystem(systemsData[selectedSystemIndex]);
            }}
        }}
        const gBtn = document.getElementById('btn-view-galaxy');
        const sBtn = document.getElementById('btn-view-system');
        if (gBtn) gBtn.addEventListener('click', () => setView('galaxy'));
        if (sBtn) sBtn.addEventListener('click', () => {{ if (!sBtn.disabled) setView('system'); }});
        
        // Region filter helpers
        function uniqueRegions() {{
            const set = new Set();
            (systemsData || []).forEach(s => {{ if (s && s.region) set.add(s.region); }});
            return Array.from(set).sort();
        }}
        function refreshRegionOptions() {{
            const sel = document.getElementById('region-filter');
            if (!sel) return;
            const current = sel.value || 'All';
            const options = ['All', ...uniqueRegions()];
            sel.innerHTML = options.map(r => `<option value="${{r}}">${{r === 'All' ? 'All Regions' : r}}</option>`).join('');
            sel.value = options.includes(current) ? current : 'All';
        }}
        function getFilteredSystems() {{
            const sel = document.getElementById('region-filter');
            const region = sel ? sel.value : 'All';
            if (!region || region === 'All') return systemsData;
            return systemsData.filter(s => (s.region || '') === region);
        }}

        // === Initialize App ===
        function initializeApp(skipMap) {{
            try {{
                var detail = document.getElementById('loading-detail');
                if (detail) detail.textContent = 'Loading data...';
                
                loadData();
                renderSystemsList();
                refreshRegionOptions();
                
                if (skipMap) {{
                    // Skip map initialization, go straight to data entry
                    if (detail) detail.textContent = 'Map skipped - Data entry ready!';
                    
                    // Switch to data tab
                    var tabBtns = document.querySelectorAll('.tab-btn');
                    tabBtns.forEach(function(b) {{ b.classList.remove('active'); }});
                    tabBtns[1].classList.add('active');
                    
                    var mapView = document.getElementById('map-view');
                    var dataView = document.getElementById('data-view');
                    mapView.style.display = 'none';
                    dataView.style.display = 'block';
                    
                    setTimeout(function() {{
                        var loading = document.getElementById('loading');
                        if (loading) loading.style.display = 'none';
                    }}, 500);
                    return;
                }}
                
                if (detail) detail.textContent = 'Checking 3D library...';
                
                // Check if Three.js loaded
                if (typeof THREE === 'undefined') {{
                    var loading = document.getElementById('loading');
                    var retryBtn = document.getElementById('retry-btn');
                    var skipBtn = document.getElementById('skip-map-btn');
                    if (loading) {{
                        loading.querySelector('p').textContent = 'ERROR: 3D library failed to load';
                        if (detail) detail.textContent = 'Internet connection required for 3D map. You can retry or skip the map and use data entry only.';
                        var spinner = loading.querySelector('.spinner');
                        if (spinner) spinner.style.display = 'none';
                        if (retryBtn) retryBtn.style.display = 'inline-block';
                        if (skipBtn) skipBtn.style.display = 'inline-block';
                    }}
                    console.error('THREE.js failed to load');
                    return;
                }}
                
                if (detail) detail.textContent = 'Initializing 3D map...';
                
                // Initialize 3D map
                var mapContainer = document.getElementById('map-canvas');
                if (!mapContainer) {{
                    throw new Error('Map container not found');
                }}
                
                window.map3d = new Map3D(mapContainer);
                window.map3d.loadGalaxy(getFilteredSystems());
                
                if (detail) detail.textContent = 'Ready!';
                
                // Hide loading
                setTimeout(function() {{
                    var loading = document.getElementById('loading');
                    if (loading) loading.style.display = 'none';
                }}, 500);
            }} catch (err) {{
                console.error('Initialization error:', err);
                var loading = document.getElementById('loading');
                var retryBtn = document.getElementById('retry-btn');
                var skipBtn = document.getElementById('skip-map-btn');
                if (loading) {{
                    loading.querySelector('p').textContent = 'ERROR: ' + err.message;
                    var detail = document.getElementById('loading-detail');
                    if (detail) detail.textContent = 'An error occurred. You can retry or skip the map.';
                    var spinner = loading.querySelector('.spinner');
                    if (spinner) spinner.style.display = 'none';
                    if (retryBtn) retryBtn.style.display = 'inline-block';
                    if (skipBtn) skipBtn.style.display = 'inline-block';
                }}
            }}
        }}
        
        window.addEventListener('load', function() {{
            initializeApp(false);
        }});
        
        // Retry button handler
        var retryBtn = document.getElementById('retry-btn');
        if (retryBtn) {{
            retryBtn.addEventListener('click', function() {{
                location.reload();
            }});
        }}
        
        // Skip map button handler
        var skipBtn = document.getElementById('skip-map-btn');
        if (skipBtn) {{
            skipBtn.addEventListener('click', function() {{
                initializeApp(true);
            }});
        }}

        // Filter change
        const regionSel = document.getElementById('region-filter');
        if (regionSel) {{
            regionSel.addEventListener('change', () => {{
                if (currentView === 'galaxy' && window.map3d) {{
                    window.map3d.loadGalaxy(getFilteredSystems());
                }}
            }});
        }}
        
        // PWA service worker registration (disabled for iOS compatibility)
        // iOS Safari has strict service worker requirements
        if (false && 'serviceWorker' in navigator) {{
            var swCode = 'const CACHE_NAME="haven-v1";self.addEventListener("install",e=>{{e.waitUntil(caches.open(CACHE_NAME));self.skipWaiting();}});self.addEventListener("fetch",e=>{{e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)));}});';
            try {{
                navigator.serviceWorker.register('data:text/javascript;base64,' + btoa(swCode))
                    .catch(e => console.log('SW registration failed:', e));
            }} catch (e) {{
                console.log('SW not supported:', e);
            }}
        }}
    </script>
</body>
</html>
'''


if __name__ == '__main__':
    import sys
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Support --out and --no-data flags
    out = None
    include_data = True
    for i, arg in enumerate(sys.argv[1:]):
        if arg == '--out' and i+2 < len(sys.argv):
            out = Path(sys.argv[i+2])
        elif arg == '--no-data':
            include_data = False
    
    result = generate_ios_pwa(out, include_data)
    print(f"Generated: {result}")
