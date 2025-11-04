# Haven Control Room - User Guide

Welcome to Haven Control Room! This application helps you manage and visualize your No Man's Sky galaxy systems.

## Quick Start

### Windows Users
1. Double-click `Haven Control Room.bat` to launch the application
2. The Control Room interface will open

### Mac Users
1. Double-click `haven_control_room_mac.command` to launch the application
2. The Control Room interface will open

### iOS Users
1. Open the `Haven_iOS.html` file from the `dist` folder
2. Add to your home screen for the full PWA experience

## What Can You Do?

### 1. Enter System Data
- Add new star systems with coordinates
- Document planets, moons, resources, and points of interest
- Upload photos of your discoveries
- Organize systems by region

### 2. View Your Galaxy Map
- Interactive 3D visualization of all your systems
- Click on systems to see detailed information
- Filter by region or attributes

### 3. Export Your Data
- Generate standalone HTML maps for sharing
- Create iOS-compatible web apps
- Export system data

## Main Features

### System Entry Wizard
The System Entry Wizard is a two-page interface for adding new systems:
- **Page 1:** Basic system info (name, region, coordinates)
- **Page 2:** Detailed planet and moon information

### Galaxy Map
View all your systems in an interactive 3D map with:
- Color-coded regions
- System information on hover
- Clickable systems for detailed views

### Control Room
Your central hub for:
- Quick access to System Entry and Map Generator
- Export tools for sharing your discoveries
- Settings and preferences

## Need Help?

### Documentation
Check the `docs/user/` folder for detailed guides:
- [Control Room Guide](control_room_guide.md) - Master interface overview
- [System Entry Guide](system_entry_wizard_guide.md) - How to add systems
- [Galaxy Map Guide](galaxy_map_guide.md) - Using the 3D map
- [Quick Reference](wizard_quick_reference.md) - Common tasks
- [iOS PWA Guide](iOS_PWA_Guide.md) - Using on iOS devices

### Tips
1. **Backup your data:** Your system data is stored in `data/data.json`
2. **Photos:** Place images in the `photos/` folder
3. **Coordinates:** Use format X, Y, Z (e.g., +3.86, -129.37, +2.14)

## System Requirements

- **Windows:** Windows 10 or later
- **Mac:** macOS 10.14 or later
- **iOS:** Safari on iOS 14 or later

## Troubleshooting

### Application Won't Start
- Make sure all files and folders are intact
- Check that you have the latest version

### Can't See My Data
- Verify `data/data.json` exists and isn't empty
- Check the `logs/` folder for error messages

### Map Won't Load
- Ensure you have at least one system entered
- Clear your browser cache and try again

## About

Haven Control Room is designed to help No Man's Sky explorers catalog and visualize their discoveries across the galaxy. Whether you're a solo explorer or part of a community, this tool makes it easy to keep track of your adventures.

**Happy Exploring!**

---

For technical documentation and development information, see the main README.md file.
