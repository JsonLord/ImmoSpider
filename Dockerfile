FROM python:3.10-slim-buster

WORKDIR /app

COPY . /app

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY yacrontab.yaml /etc/yacron.d/yacrontab.yaml

# Expose ports for yacron (8000) and Gradio (7860)
EXPOSE 8000 7860

# Start both yacron and Gradio app
CMD ["/bin/sh", "-c", "yacron -c /etc/yacron.d/yacrontab.yaml & uvicorn api.main:app --host 0.0.0.0 --port 7860 > /app/app.log 2>&1"]
