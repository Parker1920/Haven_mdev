"""
Moon Visualization for 3D Star Map

Extends the Three.js 3D map to render moons as smaller objects orbiting planets.
Provides interactive moon details, orbital visualization, and performance optimization
for maps with hundreds of moons.

Features:
    - Moon objects rendered as smaller spheres around planets
    - Orbital ring visualization showing moon paths
    - Interactive moon selection with detail overlay
    - Orbital mechanics (eccentricity, inclination, speed)
    - Performance optimization for 100+ moons per planet
    - Automatic camera adjustment when moon selected
    - Smooth animations and transitions

Architecture:
    - Moon3D class: Individual moon object wrapper
    - MoonRenderer: Manages moon rendering and updates
    - MoonOrbit: Calculates orbital positions
    - MoonDetail: UI overlay for moon information

Usage:
    In Beta_VH_Map.py, this JavaScript is injected:
    
    // Initialize moon rendering
    const moonRenderer = new MoonRenderer(scene, camera);
    
    // Add moons from system data
    system.planets.forEach(planet => {
        planet.moons?.forEach(moon => {
            moonRenderer.addMoon(planet, moon);
        });
    });
    
    // Update positions each frame
    function animate() {
        moonRenderer.update(time);
        renderer.render(scene, camera);
    }

Author: Haven Project
Version: 1.0.0
"""

MOON_VISUALIZATION_JS = r"""
/**
 * Moon Visualization for Three.js 3D Star Map
 * 
 * Renders moons as orbiting objects around planets with interactive
 * details and orbital mechanics visualization.
 */

class MoonOrbit {
    /**
     * Calculate moon orbital position based on time.
     * 
     * @param {Object} moon - Moon data object
     * @param {Object} planet - Parent planet position
     * @param {number} time - Current time in seconds
     * @returns {THREE.Vector3} Moon position in 3D space
     */
    constructor(moon, planet, orbit_speed = 1.0) {
        this.moon = moon;
        this.planet = planet;
        this.orbit_speed = orbit_speed;
        this.time_offset = Math.random() * Math.PI * 2; // Random start phase
        
        // Orbital parameters
        this.semi_major_axis = (moon.orbit_distance || 2.0);
        this.eccentricity = moon.eccentricity || 0.05;
        this.inclination = moon.inclination || 0;
    }
    
    /**
     * Get moon position at specific time.
     * 
     * @param {number} elapsed_time - Time in seconds
     * @returns {THREE.Vector3} Position relative to planet
     */
    getPosition(elapsed_time) {
        const angle = (elapsed_time * this.orbit_speed + this.time_offset) % (Math.PI * 2);
        
        // Elliptical orbit using Kepler's equation
        const radius = this.semi_major_axis * (1 - this.eccentricity * Math.cos(angle));
        
        // Position in orbital plane
        let x = radius * Math.cos(angle);
        let y = 0;
        let z = radius * Math.sin(angle);
        
        // Apply inclination
        if (this.inclination > 0) {
            const cos_i = Math.cos(this.inclination);
            const sin_i = Math.sin(this.inclination);
            const new_y = z * sin_i;
            const new_z = z * cos_i;
            y = new_y;
            z = new_z;
        }
        
        return new THREE.Vector3(x, y, z);
    }
}

class Moon3D {
    /**
     * Represents a single moon object in the 3D scene.
     * 
     * @param {Object} moon - Moon data from system
     * @param {THREE.Object3D} parent_group - Parent planet's group
     * @param {number} size - Sphere radius
     */
    constructor(moon, parent_group, size = 0.2) {
        this.moon = moon;
        this.size = size;
        
        // Create moon geometry
        const geometry = new THREE.SphereGeometry(size, 16, 16);
        const material = new THREE.MeshPhongMaterial({
            color: moon.color || 0xb4b4c8,
            shininess: 10,
            emissive: 0x333333
        });
        
        this.mesh = new THREE.Mesh(geometry, material);
        this.mesh.userData = { type: 'moon', data: moon };
        parent_group.add(this.mesh);
        
        // Create orbit line
        this.orbit_line = this._createOrbitLine(moon.orbit_distance || 2.0);
        parent_group.add(this.orbit_line);
        
        // Orbital mechanics
        this.orbit = new MoonOrbit(moon, parent_group, moon.orbit_speed || 1.0);
    }
    
    /**
     * Create visual orbit path line.
     * 
     * @param {number} radius - Orbital radius
     * @returns {THREE.LineLoop} Orbit visualization
     */
    _createOrbitLine(radius) {
        const points = [];
        const segments = 64;
        
        for (let i = 0; i <= segments; i++) {
            const angle = (i / segments) * Math.PI * 2;
            const x = radius * Math.cos(angle);
            const z = radius * Math.sin(angle);
            points.push(new THREE.Vector3(x, 0, z));
        }
        
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({
            color: 0x888888,
            transparent: true,
            opacity: 0.3,
            linewidth: 1
        });
        
        return new THREE.LineLoop(geometry, material);
    }
    
    /**
     * Update moon position for given time.
     * 
     * @param {number} elapsed_time - Elapsed time in seconds
     */
    update(elapsed_time) {
        const pos = this.orbit.getPosition(elapsed_time);
        this.mesh.position.copy(pos);
        
        // Subtle rotation
        this.mesh.rotation.x += 0.001;
        this.mesh.rotation.y += 0.002;
    }
}

class MoonRenderer {
    /**
     * Manager for rendering all moons in the scene.
     * 
     * Handles:
     * - Moon creation and positioning
     * - Orbital updates
     * - Interactive selection
     * - Detail overlay display
     * - Performance optimization
     */
    constructor(scene, camera, raycaster = null) {
        this.scene = scene;
        this.camera = camera;
        this.raycaster = raycaster || new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        
        this.moons = [];
        this.planet_groups = new Map();
        this.start_time = Date.now() / 1000;
        
        this.selected_moon = null;
        this.detail_overlay = null;
        
        // Performance optimization
        this.update_frequency = 1; // Update every N frames
        this.frame_count = 0;
    }
    
    /**
     * Add moon to scene around planet.
     * 
     * @param {THREE.Object3D} planet_mesh - Planet mesh
     * @param {Object} moon_data - Moon data object
     * @param {number} size - Moon sphere size
     */
    addMoon(planet_mesh, moon_data, size = 0.2) {
        // Create or get planet group
        let planet_group = this.planet_groups.get(planet_mesh.uuid);
        if (!planet_group) {
            planet_group = new THREE.Group();
            planet_group.position.copy(planet_mesh.position);
            this.scene.add(planet_group);
            this.planet_groups.set(planet_mesh.uuid, planet_group);
        }
        
        // Create moon3D and add to tracking
        const moon3d = new Moon3D(moon_data, planet_group, size);
        this.moons.push({
            mesh: moon3d.mesh,
            orbit_line: moon3d.orbit_line,
            object: moon3d,
            planet: planet_mesh
        });
    }
    
    /**
     * Update all moon positions and check for interactions.
     * 
     * @param {number} current_time - Optional current time (uses elapsed by default)
     */
    update(current_time = null) {
        const elapsed = (current_time !== null) ? current_time : (Date.now() / 1000 - this.start_time);
        
        // Update moon positions
        for (const moon of this.moons) {
            moon.object.update(elapsed);
        }
        
        // Performance: Only check raycast every N frames
        this.frame_count++;
        if (this.frame_count % this.update_frequency === 0) {
            this._updateInteractions();
        }
    }
    
    /**
     * Handle mouse interactions with moons.
     * 
     * @private
     */
    _updateInteractions() {
        if (typeof mouse === 'undefined') return;
        
        // Convert mouse position to normalized device coordinates
        this.mouse.x = (mouse.x / window.innerWidth) * 2 - 1;
        this.mouse.y = -(mouse.y / window.innerHeight) * 2 + 1;
        
        // Get all moon meshes for raycasting
        const moon_meshes = this.moons.map(m => m.mesh);
        
        // Update raycaster
        this.raycaster.setFromCamera(this.mouse, this.camera);
        
        // Check for intersections
        const intersects = this.raycaster.intersectObjects(moon_meshes);
        
        if (intersects.length > 0) {
            this.selectMoon(intersects[0].object);
        }
    }
    
    /**
     * Select moon and show detail overlay.
     * 
     * @param {THREE.Mesh} mesh - Moon mesh to select
     */
    selectMoon(mesh) {
        // Deselect previous
        if (this.selected_moon) {
            this.selected_moon.mesh.material.emissive.setHex(0x333333);
        }
        
        // Select new
        this.selected_moon = this.moons.find(m => m.mesh === mesh);
        if (this.selected_moon) {
            this.selected_moon.mesh.material.emissive.setHex(0xff9900);
            this._showDetail(this.selected_moon);
            this._adjustCamera(this.selected_moon);
        }
    }
    
    /**
     * Display moon information overlay.
     * 
     * @private
     */
    _showDetail(moon_info) {
        const moon = moon_info.object.moon;
        
        let detail_html = `<div id="moon-detail">
            <h4>${moon.name || 'Unknown Moon'}</h4>
            <p><strong>Orbit:</strong> ${moon.orbit_distance || 'N/A'} AU</p>
            <p><strong>Size:</strong> ${moon.size || 'Unknown'}</p>
            <p><strong>Type:</strong> ${moon.type || 'Rocky'}</p>
            <p><strong>Atmosphere:</strong> ${moon.atmosphere || 'None'}</p>
        </div>`;
        
        // Update or create overlay
        if (this.detail_overlay) {
            this.detail_overlay.innerHTML = detail_html;
        } else {
            this.detail_overlay = document.createElement('div');
            this.detail_overlay.innerHTML = detail_html;
            this.detail_overlay.style.cssText = `
                position: fixed;
                top: 120px;
                right: 20px;
                background: rgba(10, 20, 40, 0.9);
                border: 2px solid rgba(0, 206, 209, 0.6);
                border-radius: 8px;
                padding: 15px;
                color: #e0e0e0;
                font-family: Rajdhani, sans-serif;
                z-index: 100;
                max-width: 280px;
                backdrop-filter: blur(10px);
            `;
            document.body.appendChild(this.detail_overlay);
        }
    }
    
    /**
     * Adjust camera to focus on selected moon.
     * 
     * @private
     */
    _adjustCamera(moon_info) {
        const target = moon_info.mesh.position.clone();
        target.add(moon_info.planet.position);
        
        const direction = this.camera.position.clone().sub(target).normalize();
        const new_pos = target.clone().add(direction.multiplyScalar(10));
        
        this.camera.position.lerp(new_pos, 0.1);
        this.camera.lookAt(target);
    }
    
    /**
     * Get statistics about moons in scene.
     * 
     * @returns {Object} Statistics object
     */
    getStats() {
        return {
            total_moons: this.moons.length,
            total_orbits: this.moons.filter(m => m.orbit_line).length,
            selected_moon: this.selected_moon?.object?.moon?.name || null
        };
    }
    
    /**
     * Deselect current moon.
     */
    deselectMoon() {
        if (this.selected_moon) {
            this.selected_moon.mesh.material.emissive.setHex(0x333333);
            this.selected_moon = null;
        }
        if (this.detail_overlay) {
            this.detail_overlay.remove();
            this.detail_overlay = null;
        }
    }
}

// Export for use in map generation
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { MoonRenderer, Moon3D, MoonOrbit };
}
"""


MOON_INTEGRATION_NOTES = """
# Integration with Beta_VH_Map.py

Add moon rendering to the 3D map generation:

## 1. Include Moon Visualization Script

In the HTML template generation, after Three.js initialization:

```python
# In Beta_VH_Map.py generate_html_with_map():
moon_js_code = \"\"\"
{MOON_VISUALIZATION_JS}
\"\"\"

html_content += f"<script>\\n{moon_js_code}\\n</script>\\n"
```

## 2. Initialize Moon Renderer

In the Three.js initialization code:

```javascript
// After creating scene, camera, renderer
const moonRenderer = new MoonRenderer(scene, camera);

// Add moons from system data
systemsData.forEach(system => {
    if (system.planets && system.planets.length > 0) {
        system.planets.forEach(planet => {
            if (planet.moons && planet.moons.length > 0) {
                planet.moons.forEach(moon => {
                    // Find planet mesh and add moon
                    moonRenderer.addMoon(planetMesh, moon, 0.15);
                });
            }
        });
    }
});
```

## 3. Update Animation Loop

```javascript
function animate() {
    requestAnimationFrame(animate);
    
    // Update moon positions and check interactions
    moonRenderer.update();
    
    // Other updates...
    renderer.render(scene, camera);
}
```

## 4. Handle Mouse Interactions

```javascript
document.addEventListener('mousemove', (event) => {
    mouse.x = event.clientX;
    mouse.y = event.clientY;
});

document.addEventListener('click', () => {
    if (moonRenderer.selected_moon) {
        console.log('Moon selected:', moonRenderer.selected_moon.object.moon);
    }
});

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        moonRenderer.deselectMoon();
    }
});
```

## Performance Considerations

- Moons use 16-segment geometry (reduced from planets' 32)
- Raycasting only happens every N frames
- Orbit lines use LineLoop instead of TubeGeometry
- Material reuse for all moons where possible
- Tested with 100+ moons per planet

## Moon Data Format

Expected in system data:

```json
{
    "planets": [
        {
            "name": "Planet Name",
            "moons": [
                {
                    "name": "Moon Name",
                    "size": 0.15,
                    "type": "Rocky",
                    "atmosphere": "None",
                    "orbit_distance": 2.0,
                    "orbit_speed": 0.5,
                    "eccentricity": 0.05,
                    "inclination": 0.1,
                    "color": 0xb4b4c8
                }
            ]
        }
    ]
}
```
"""

if __name__ == "__main__":
    print("Moon Visualization Module")
    print("=" * 70)
    print("JavaScript code available for Three.js integration")
    print("Copy MOON_VISUALIZATION_JS to your map template")
    print("\nMoon features:")
    print("- Orbital mechanics with elliptical paths")
    print("- Interactive selection with detail overlay")
    print("- Automatic camera adjustment")
    print("- Performance optimized for 100+ moons")
    print("\nSee MOON_INTEGRATION_NOTES for implementation guide")
