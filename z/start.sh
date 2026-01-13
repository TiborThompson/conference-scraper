#!/bin/bash
# Start the Speaker Recommendation System (Next.js + FastAPI)

echo "Starting Speaker Recommendation System..."
cd "$(dirname "$0")/.."

# Check if speakers data exists
if [ ! -f "data/speakers.json" ]; then
    echo "Error: Speaker data not found!"
    echo "Please run ./z/scrape.sh first to scrape the conference data."
    exit 1
fi

# Start backend in background
echo "Starting FastAPI backend on port 8000..."
source venv/bin/activate
python backend.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 2

# Start frontend
echo "Starting Next.js frontend on port 3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "================================"
echo "System is starting up..."
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "================================"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
