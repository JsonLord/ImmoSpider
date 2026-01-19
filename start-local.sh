#!/bin/bash

# Stop any processes that might be running on the required ports
echo "Stopping any existing services on ports 8000 and 7860..."
kill $(lsof -t -i :8000) 2>/dev/null || true
kill $(lsof -t -i :7860) 2>/dev/null || true

# Start the FastAPI backend in the background
echo "Starting FastAPI backend..."
uvicorn api.main:app --host 127.0.0.1 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for the backend to be ready by polling the port
echo "Waiting for backend to launch on port 8000..."
while ! lsof -i :8000 -sTCP:LISTEN -t >/dev/null; do
    # Check if the backend process has crashed
    if ! ps -p $BACKEND_PID > /dev/null; then
        echo "Backend failed to start. See backend.log for details."
        exit 1
    fi
    sleep 1
done
echo "Backend is running."

# Start the Gradio frontend in the foreground
echo "Starting Gradio frontend..."
python app.py

# When the user stops the frontend (Ctrl+C), also stop the backend
echo "Shutting down backend..."
kill $BACKEND_PID
