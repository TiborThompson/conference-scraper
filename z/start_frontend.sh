#!/bin/bash
# Start only the Next.js frontend

echo "Starting Next.js frontend..."
cd "$(dirname "$0")/../frontend"
npm run dev
