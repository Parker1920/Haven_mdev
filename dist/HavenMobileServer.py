#!/usr/bin/env python3
"""
Haven Mobile Explorer - Simple Local Server
Serves Haven_Mobile_Explorer.html on local network for iOS devices

Usage:
    python3 HavenMobileServer.py

Or on Windows:
    python HavenMobileServer.py

Or just double-click if Python is installed!

Press Ctrl+C to stop the server.
"""

import http.server
import socketserver
import socket
import os
import sys
from pathlib import Path

# Configuration
PORT = 8080
HTML_FILE = "Haven_Mobile_Explorer.html"

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Create a socket to find local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def check_html_exists():
    """Check if Haven_Mobile_Explorer.html exists in current directory"""
    if not Path(HTML_FILE).exists():
        print(f"\n❌ ERROR: {HTML_FILE} not found!")
        print(f"Make sure {HTML_FILE} is in the same folder as this script.\n")
        return False
    return True

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve the HTML file with proper headers"""

    def end_headers(self):
        # Add CORS headers for mobile browsers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def log_message(self, format, *args):
        # Custom log format
        print(f"📱 {self.address_string()} - {format % args}")

def main():
    # Check if HTML file exists
    if not check_html_exists():
        input("Press Enter to exit...")
        sys.exit(1)

    # Get local IP
    local_ip = get_local_ip()

    # Print banner
    print("=" * 60)
    print("    HAVEN MOBILE EXPLORER - LOCAL SERVER")
    print("=" * 60)
    print()
    print("✅ Server starting...")
    print(f"✅ Serving: {HTML_FILE}")
    print()

    # Create server
    try:
        with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
            print("🌐 SERVER RUNNING AT:")
            print()
            print(f"   http://{local_ip}:{PORT}")
            print()
            print("📱 OPEN THIS URL ON YOUR iPHONE:")
            print(f"   http://{local_ip}:{PORT}")
            print()
            print("🔧 Make sure your iPhone is on the same WiFi network")
            print()
            print("⏹️  Press Ctrl+C to stop the server")
            print("=" * 60)
            print()
            print("Waiting for connections...")
            print()

            # Serve forever
            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n\n⏹️  Server stopped by user")
        print("=" * 60)
        sys.exit(0)
    except OSError as e:
        if "address already in use" in str(e).lower():
            print(f"\n❌ ERROR: Port {PORT} is already in use!")
            print("Either:")
            print("1. Close other program using this port")
            print("2. Or change PORT variable in this script")
        else:
            print(f"\n❌ ERROR: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
