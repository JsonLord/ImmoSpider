FROM python:3.10-slim-buster

WORKDIR /app

COPY . /app

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports for the API (8000) and the Gradio UI (7860)
EXPOSE 8000 7860

# Copy and make the start script executable
COPY start.sh .
RUN chmod +x start.sh

# Set the entrypoint to the start script
CMD ["./start.sh"]
