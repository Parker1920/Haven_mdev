==============================================================================
HOW TO VIEW THE GENERATED MAP
==============================================================================

IMPORTANT: Do NOT open the HTML file directly by double-clicking it!

The map uses external JavaScript files that won't load properly when opened
directly from the file system (file:// protocol) due to browser security
restrictions (CORS).

==============================================================================
SOLUTION: Use the Local Web Server
==============================================================================

From the project root directory, run:

    python serve_map.py

This will:
  1. Start a local web server on port 8000
  2. Automatically open the map in your default browser
  3. Serve the map properly with all JavaScript files loading correctly

==============================================================================
ALTERNATIVE: Use Python's Built-in Server
==============================================================================

If you prefer, you can also run:

    cd dist
    python -m http.server 8000

Then open your browser to: http://localhost:8000/TEST-Map.html
(or VH-Map.html if you generated the production map)

Press Ctrl+C to stop the server when done.

==============================================================================
WHY IS THIS NECESSARY?
==============================================================================

Modern browsers block loading local JavaScript files for security reasons
when viewing HTML files directly (file:// URLs). This is a security feature
called CORS (Cross-Origin Resource Sharing).

By running a local web server, the files are served via HTTP (http://),
which allows the JavaScript files to load properly.

==============================================================================
