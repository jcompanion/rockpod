#!/bin/bash

# RockPod Setup Script
# Sets up the Python environment and installs dependencies

set -e

echo "🚀 RockPod Setup"
echo "================"
echo ""

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "   Please install Python 3.8 or later from python.org"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Create virtual environment
VENV_DIR="venv"

if [ -d "$VENV_DIR" ]; then
    echo "✓ Virtual environment already exists"
else
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To use RockPod:"
echo "1. Edit config.yaml to add your podcast feeds"
echo "2. Run the sync:"
echo ""
echo "   source venv/bin/activate"
echo "   python rockpod_sync.py sync"
echo ""
echo "Commands:"
echo "  python rockpod_sync.py fetch      # Download new episodes"
echo "  python rockpod_sync.py sync       # Download + sync to iPod"
echo "  python rockpod_sync.py sync-only  # Just sync to iPod"
echo ""
echo "Make sure your Rockbox iPod is connected before syncing!"