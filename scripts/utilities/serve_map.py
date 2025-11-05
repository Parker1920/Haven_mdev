"""
Simple HTTP Server to view the generated map

Opens the map in a web server so JavaScript files load properly.
The file:// protocol has CORS restrictions that prevent loading external scripts.

Usage:
    python scripts/utilities/serve_map.py
    
Or from project root:
    python -m scripts.utilities.serve_map
"""

import http.server
import socketserver
import webbrowser
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from common.constants import ServerConstants

# Configuration
PORT = ServerConstants.DEFAULT_PORT
# Navigate up to project root, then to dist/
PROJECT_ROOT = Path(__file__).parent.parent.parent
DIRECTORY = PROJECT_ROOT / "dist"

def serve():
    """Start a simple HTTP server and open the map."""

    # Set UTF-8 for Windows console
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    # Change to dist directory
    import os
    os.chdir(DIRECTORY)

    # Create server
    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/TEST-Map.html"
        print(f"\n{'='*70}")
        print(f"[SERVER] Haven Starmap Server")
        print(f"{'='*70}")
        print(f"  Server running at: http://localhost:{PORT}")
        print(f"  Serving from: {DIRECTORY}")
        print(f"\n  Opening map: {url}")
        print(f"\n  Press Ctrl+C to stop the server")
        print(f"{'='*70}\n")

        # Open browser
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"  Could not open browser automatically: {e}")
            print(f"  Please open manually: {url}")

        # Serve forever
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n\n{'='*70}")
            print("  Server stopped.")
            print(f"{'='*70}\n")
            sys.exit(0)

if __name__ == "__main__":
    if not DIRECTORY.exists():
        print(f"ERROR: dist directory not found at {DIRECTORY}")
        print("Please generate the map first using Beta_VH_Map.py")
        sys.exit(1)

    serve()
