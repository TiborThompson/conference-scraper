#!/bin/bash
# Start only the FastAPI backend

echo "Starting FastAPI backend..."
cd "$(dirname "$0")/.."

# Check if speakers data exists
if [ ! -f "data/speakers.json" ]; then
    echo "Error: Speaker data not found!"
    echo "Please run ./z/scrape.sh first."
    exit 1
fi

source venv/bin/activate
python backend.py
