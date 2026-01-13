#!/bin/bash

set -e

echo "Setting up the webscraper..."

cd "$(dirname "$0")/.."

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "Installing Playwright browsers..."
playwright install chromium

echo ""
echo "Checking API keys..."
python tests/test_api_keys.py

echo ""
echo "=" * 60
echo "Setup complete!"
echo "=" * 60
echo ""
echo "Quick start:"
echo "  source venv/bin/activate"
echo "  python demo.py https://example.com"
echo ""
echo "Available examples:"
echo "  - python examples/basic_scrape.py"
echo "  - python examples/llm_extraction.py"
echo "  - python examples/full_pipeline.py"
echo ""
