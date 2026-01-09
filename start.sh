#!/bin/bash

# Start the FastAPI backend on port 8000 in the background
echo "Starting FastAPI backend server on port 8000..."
uvicorn api.main:app --host 0.0.0.0 --port 8000 &

# Start the Gradio frontend on port 7860 in the foreground
echo "Starting Gradio frontend server on port 7860..."
python app.py
