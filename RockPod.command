#!/bin/bash

# RockPod Menu Bar Launcher
# Double-click this file to run the RockPod menu bar app

# Change to the script directory
cd "$(dirname "$0")"

# Kill any existing instances
pkill -f rockpod_menu.py 2>/dev/null

echo "🎙️  Starting RockPod Menu Bar..."
echo "================================"
echo ""
echo "The app will appear in your menu bar at the top of the screen."
echo ""
echo "To quit: Click 'Quit RockPod' from the menu"
echo "To close this window: Press Cmd+Q or close the Terminal window"
echo ""

# Run the menu bar app
./venv/bin/python rockpod_menu.py