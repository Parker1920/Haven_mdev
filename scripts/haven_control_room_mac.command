#!/bin/bash
cd "$(dirname "$0")/.."
clear
while true; do
  echo "=============================================="
  echo "        Haven Control Room (Launcher)"
  echo "=============================================="
  echo
  # Show environment info
  PYVER=$(python3 --version 2>&1 || echo "Not installed")
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
    COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    echo "  Environment: $PYVER | Branch: $BRANCH ($COMMIT)"
  else
    echo "  Environment: $PYVER | Not a Git repository"
  fi
  echo
  echo "  1) Open Galactic Archive Terminal (GUI)"
  echo "  2) Run Atlas Array (Build 3D Map)"
  echo "  3) Holo-Net Update (Pull + Dependencies)"
  echo "  4) Exit"
  echo
  read -rp "Select an option [1-4]: " CHOICE
  case "$CHOICE" in
    1)
      ./scripts/run_haven_mac.command ;;
    2)
      ./scripts/build_map_mac.command ;;
    3)
      ./scripts/holo_net_update_mac.command ;;
    4)
      exit 0 ;;
    *)
      echo "Invalid choice. Please select 1-4." ;;
  esac
  echo
  read -rp "Press Enter to return to the menu..." _
  clear
done
