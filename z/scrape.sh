#!/bin/bash
# Scrape SOFWeek conference speakers

echo "Starting SOFWeek speaker scraper..."
cd "$(dirname "$0")/.."
source venv/bin/activate
python src/scrapers/conference_scraper.py
echo ""
echo "Scraping complete! Data saved to data/speakers.json"
