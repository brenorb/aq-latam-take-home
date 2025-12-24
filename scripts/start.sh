#!/bin/bash
# Production startup script for Docker container
# Starts both FastAPI backend and Streamlit frontend using uv

set -e

# Initialize database
/app/scripts/init_db.sh

# Start backend in background
echo "Starting FastAPI backend..."
cd /app
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 2>&1 | tee /tmp/backend.log &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "Backend failed to start"
        echo "Backend logs:"
        cat /tmp/backend.log 2>/dev/null || echo "No backend logs available"
        exit 1
    fi
    sleep 1
done

# Start frontend
echo "Starting Streamlit frontend..."
cd /app
uv run streamlit run main.py --server.port 8501 --server.address 0.0.0.0 --server.headless true &
FRONTEND_PID=$!

# Wait for frontend to be ready
echo "Waiting for frontend to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        echo "Frontend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "Frontend failed to start"
        exit 1
    fi
    sleep 1
done

# Function to handle shutdown
cleanup() {
    echo "Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

echo "Both services are running. Monitoring processes..."

# Simple process monitoring: wait for either process to exit
# If either exits, we shut down everything
while true; do
    # Check if backend is still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "Backend process exited unexpectedly"
        kill $FRONTEND_PID 2>/dev/null || true
        exit 1
    fi
    
    # Check if frontend is still running
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "Frontend process exited unexpectedly"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    
    sleep 5
done
