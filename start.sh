#!/bin/bash

# Kill existing bot processes
pkill -f "python.*main.py" 2>/dev/null
pkill -f "python.*bot" 2>/dev/null

# Wait for processes to terminate
sleep 2

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed!"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Create necessary files if they don't exist
if [ ! -f "user_data.json" ]; then
    echo "{}" > user_data.json
    echo "✅ Created user_data.json"
fi

if [ ! -f "admins.json" ]; then
    echo "[7612918437]" > admins.json
    echo "✅ Created admins.json"
fi

# Run the bot
echo "🤖 Starting NeuroSnare Checker v6.3..."
python3 main.py