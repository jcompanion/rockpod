#!/bin/bash

# Simple RockPod Launcher
# Usage: ./launch_rockpod.sh

cd "$(dirname "$0")"

# Kill any existing instances
pkill -f rockpod_menu.py 2>/dev/null

# Run in background so script exits immediately
nohup ./venv/bin/python rockpod_menu.py > /dev/null 2>&1 &

echo "🎙️ RockPod menu bar app started!"
echo "Look for it in your menu bar at the top of the screen."