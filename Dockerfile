FROM kennethreitz/pipenv

COPY . /app

COPY yacrontab.yaml /etc/yacron.d/yacrontab.yaml

# Install Gradio
RUN pip install gradio

# Expose ports for yacron (8000) and Gradio (7860)
EXPOSE 8000 7860

# Start both yacron and Gradio app
CMD ["/bin/sh", "-c", "yacron -c /etc/yacron.d/yacrontab.yaml & python app.py"]
