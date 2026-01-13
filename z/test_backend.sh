#!/bin/bash
# Test the FastAPI backend endpoints

echo "Testing FastAPI Backend..."
echo "Make sure the backend is running first: ./z/start_backend.sh"
echo ""

cd "$(dirname "$0")/.."
source venv/bin/activate
python tests/test_backend.py
