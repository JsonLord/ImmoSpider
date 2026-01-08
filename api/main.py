import fastapi
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import json
import subprocess
import gradio as gr
import os
import requests
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- DEBUGGING INFORMATION ---
logger.info(f"--- API/MAIN.PY STARTUP DEBUG ---")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Environment variable API_URL: {os.getenv('API_URL')}")
logger.info(f"Environment variable API_KEY: {os.getenv('API_KEY')}")

# Print content of api/main.py
try:
    with open("api/main.py", "r") as f:
        logger.info("\n--- api/main.py content at runtime ---\n" + f.read() + "\n--- End api/main.py content ---")
except Exception as e:
    logger.error(f"Could not read api/main.py: {e}")

# Print content of yacrontab.yaml
try:
    with open("yacrontab.yaml", "r") as f:
        logger.info("\n--- yacrontab.yaml content at runtime ---\n" + f.read() + "\n--- End yacrontab.yaml content ---")
except Exception as e:
    logger.error(f"Could not read yacrontab.yaml: {e}")

logger.info(f"--- END API/MAIN.PY STARTUP DEBUG ---")
# --- END DEBUGGING INFORMATION ---

# Get API URL and API key from environment
API_URL = os.getenv("API_URL", "http://127.0.0.1:7860")
API_KEY_NAME = "X-API-KEY"
API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI()

async def get_api_key(api_key: str = Depends(api_key_header)):
    if not API_KEY or api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key

class SpiderConfig(BaseModel):
    url: str
    dest: str
    mode: str
    contact_name: str

@app.post("/config")
def update_config(config: SpiderConfig, api_key: str = Depends(get_api_key)):
    try:
        with open("api/config.json", "w") as f:
            json.dump(config.dict(), f)
        logger.info(f"Configuration updated to: {config.dict()}")
        return {"message": "Configuration updated successfully."}
    except Exception as e:
        logger.error(f"Error updating configuration file: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating configuration file: {e}")

@app.get("/trigger")
def trigger_spider(api_key: str = Depends(get_api_key)):
    try:
        logger.info("Triggering spider via subprocess.Popen")
        subprocess.Popen(["scrapy", "crawl", "immoscout"])
        return {"message": "Spider run triggered."}
    except Exception as e:
        logger.error(f"Error triggering spider: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Function to update configuration via API (for Gradio UI)
def update_config_ui(url, dest, mode, contact_name):
    config = {
        "url": url,
        "dest": dest,
        "mode": mode,
        "contact_name": contact_name
    }
    headers = {API_KEY_NAME: API_KEY}
    target_url = f"http://127.0.0.1:7860/config"
    logger.info(f"Gradio UI calling API: POST {target_url} with data: {config}")
    try:
        response = requests.post(target_url, json=config, headers=headers)
        logger.info(f"Gradio UI POST response status: {response.status_code}, text: {response.text}")
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()["message"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Gradio UI POST request failed to {target_url}: {e}")
        return f"Error updating configuration: {e}"

# Function to trigger spider manually (for Gradio UI)
def trigger_spider_ui():
    headers = {API_KEY_NAME: API_KEY}
    target_url = f"http://127.0.0.1:7860/trigger"
    logger.info(f"Gradio UI calling API: GET {target_url}")
    try:
        response = requests.get(target_url, headers=headers)
        logger.info(f"Gradio UI GET response status: {response.status_code}, text: {response.text}")
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()["message"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Gradio UI GET request failed to {target_url}: {e}")
        return f"Error triggering spider: {e}"

# Load current configuration
try:
    with open("api/config.json", "r") as f:
        config = json.load(f)
except FileNotFoundError:
    # Default configuration if file doesn't exist
    config = {
        "url": "https://www.immobilienscout24.de/Suche/S-2/Wohnung-Miete/Berlin/Berlin",
        "dest": "Unter den Linden 1, 10117 Berlin",
        "mode": "transit",
        "contact_name": "Jules"
    }

# Create Gradio interface
with gr.Blocks(title="ImmoSpider Configuration") as demo:
    gr.Markdown("# ImmoSpider Configuration & Control Panel")
    
    with gr.Tab("Configuration"):
        gr.Markdown("## Search Parameters")
        with gr.Row():
            url = gr.Textbox(label="Search URL", value=config.get("url", ""), lines=3)
        with gr.Row():
            dest = gr.Textbox(label="Destination Address", value=config.get("dest", ""), lines=2)
        with gr.Row():
            mode = gr.Textbox(label="Travel Mode (transit/car/walking)", value=config.get("mode", ""))
        with gr.Row():
            contact_name = gr.Textbox(label="Contact Name", value=config.get("contact_name", ""))
        
        update_btn = gr.Button("Update Configuration")
        update_output = gr.Textbox(label="Status")
        
        update_btn.click(
            fn=update_config_ui,
            inputs=[url, dest, mode, contact_name],
            outputs=update_output
        )
    
    with gr.Tab("Control"):
        gr.Markdown("## Manual Trigger")
        trigger_btn = gr.Button("Trigger Spider Manually")
        trigger_output = gr.Textbox(label="Result")
        
        trigger_btn.click(
            fn=trigger_spider_ui,
            inputs=[],
            outputs=trigger_output
        )
    
    with gr.Tab("About"):
        gr.Markdown("## About ImmoSpider")
        gr.Markdown("ImmoSpider is a web scraper for Immoscout24 that can run at regular intervals and send notifications.")
        gr.Markdown("It can analyze apartment descriptions using LLMs and generate personalized messages.")
        
        gr.Markdown("### Features Implemented:")
        gr.Markdown("- Telegram notifications for spider runs")
        gr.Markdown("- LLM analysis of apartment descriptions")
        gr.Markdown("- Gradio web interface for configuration")
        gr.Markdown("- Enhanced safety net with failure monitoring")

app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
