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

# Monitor processes and wait for them
echo "Both services are running. Monitoring processes..."

# Create temporary files to track exit codes
BACKEND_EXIT_FILE=$(mktemp)
FRONTEND_EXIT_FILE=$(mktemp)
trap "rm -f $BACKEND_EXIT_FILE $FRONTEND_EXIT_FILE" EXIT

# Wait for backend in background and capture exit code
(
    wait $BACKEND_PID
    echo $? > $BACKEND_EXIT_FILE
    BACKEND_EXIT=$(cat $BACKEND_EXIT_FILE)
    echo "Backend process exited with code $BACKEND_EXIT"
    if [ $BACKEND_EXIT -ne 0 ]; then
        echo "Backend crashed. Shutting down frontend..."
        kill $FRONTEND_PID 2>/dev/null || true
    fi
) &
BACKEND_WAIT_PID=$!

# Wait for frontend in background and capture exit code
(
    wait $FRONTEND_PID
    echo $? > $FRONTEND_EXIT_FILE
    FRONTEND_EXIT=$(cat $FRONTEND_EXIT_FILE)
    echo "Frontend process exited with code $FRONTEND_EXIT"
    if [ $FRONTEND_EXIT -ne 0 ]; then
        echo "Frontend crashed. Shutting down backend..."
        kill $BACKEND_PID 2>/dev/null || true
    fi
) &
FRONTEND_WAIT_PID=$!

# Wait for both wait processes to complete
wait $BACKEND_WAIT_PID
wait $FRONTEND_WAIT_PID

# Read exit codes from files
BACKEND_EXIT=$(cat $BACKEND_EXIT_FILE)
FRONTEND_EXIT=$(cat $FRONTEND_EXIT_FILE)

# Determine final exit code
if [ $BACKEND_EXIT -ne 0 ] || [ $FRONTEND_EXIT -ne 0 ]; then
    echo "One or more services exited with error (backend: $BACKEND_EXIT, frontend: $FRONTEND_EXIT)"
    cleanup
    exit 1
else
    echo "Both services exited normally"
    exit 0
fi

