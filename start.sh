#!/bin/bash
set -e

echo "Starting FastAPI backend..."
# Start the backend in the background
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Waiting for backend to be ready..."
# Simple wait loop until the health endpoint is reachable
until curl -s http://localhost:8000/health > /dev/null; do
  sleep 1
done
echo "Backend is ready!"

echo "Starting Streamlit frontend..."
# Environment variable for Streamlit to know where the backend is
export BACKEND_URL="http://localhost:8000"

# Start the frontend in the foreground
streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true --browser.gatherUsageStats false &
FRONTEND_PID=$!

# Wait for any process to exit
wait -n $BACKEND_PID $FRONTEND_PID

# Exit with status of process that exited first
exit $?
