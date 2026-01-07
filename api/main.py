from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import json
import subprocess
import gradio as gr
import os
import requests

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
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
    with open("api/config.json", "w") as f:
        json.dump(config.dict(), f)
    return {"message": "Configuration updated successfully."}

@app.get("/trigger")
def trigger_spider(api_key: str = Depends(get_api_key)):
    try:
        subprocess.Popen(["scrapy", "crawl", "immoscout"])
        return {"message": "Spider run triggered."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def create_gradio_ui():
    def update_config_ui(url, dest, mode, contact_name):
        config = {"url": url, "dest": dest, "mode": mode, "contact_name": contact_name}
        headers = {API_KEY_NAME: API_KEY}
        response = requests.post(f"{API_URL}/config", json=config, headers=headers)
        return response.json()["message"]

    with open("api/config.json", "r") as f:
        config = json.load(f)

    with gr.Blocks() as demo:
        gr.Markdown("## Spider Configuration")
        with gr.Row():
            url = gr.Textbox(label="URL", value=config["url"])
        with gr.Row():
            dest = gr.Textbox(label="Destination", value=config["dest"])
            mode = gr.Textbox(label="Mode", value=config["mode"])
            contact_name = gr.Textbox(label="Contact Name", value=config["contact_name"])
        update_button = gr.Button("Update Configuration")
        update_button.click(update_config_ui, inputs=[url, dest, mode, contact_name], outputs=gr.Textbox(label="Status"))
    return demo

app = gr.mount_gradio_app(app, create_gradio_ui(), path="/")
