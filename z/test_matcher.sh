#!/bin/bash
# Test the speaker matcher

echo "Testing Speaker Matcher..."
cd "$(dirname "$0")/.."

# Check if speakers data exists
if [ ! -f "data/speakers.json" ]; then
    echo "Error: Speaker data not found!"
    echo "Please run ./z/scrape.sh first."
    exit 1
fi

source venv/bin/activate
python tests/test_matcher.py
