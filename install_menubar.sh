#!/bin/bash

# Install RockPod Menu Bar as a Launch Agent

PLIST_NAME="com.rockpod.menubar"
PLIST_FILE="$PLIST_NAME.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

echo "🚀 Installing RockPod Menu Bar App"
echo "=================================="
echo ""

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$LAUNCH_AGENTS_DIR"

# Copy the plist file
cp "$PLIST_FILE" "$LAUNCH_AGENTS_DIR/"

# Unload if already loaded (ignore errors)
launchctl unload "$LAUNCH_AGENTS_DIR/$PLIST_FILE" 2>/dev/null

# Load the new agent
launchctl load "$LAUNCH_AGENTS_DIR/$PLIST_FILE"

echo "✅ RockPod Menu Bar installed!"
echo ""
echo "The app will now:"
echo "• Start automatically when you log in"
echo "• Restart if it crashes"
echo "• Run in the background"
echo ""
echo "To check status:"
echo "  launchctl list | grep rockpod"
echo ""
echo "To stop the app:"
echo "  launchctl unload ~/Library/LaunchAgents/$PLIST_FILE"
echo ""
echo "To uninstall completely:"
echo "  launchctl unload ~/Library/LaunchAgents/$PLIST_FILE"
echo "  rm ~/Library/LaunchAgents/$PLIST_FILE"
echo ""
echo "Logs are available at:"
echo "  /tmp/rockpod.log"
echo "  /tmp/rockpod.error.log"