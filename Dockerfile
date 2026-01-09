FROM python:3.10-slim-buster

WORKDIR /app

COPY . /app

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports for the API (8000) and the Gradio UI (7860)
EXPOSE 8000 7860

# Start both the API server and the Gradio app
CMD ["/bin/sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port 8000 & python app.py"]
