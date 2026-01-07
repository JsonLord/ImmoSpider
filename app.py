import gradio as gr
import requests
import json
import os

# Get API URL and API key from environment
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "X-API-KEY"

# Function to update configuration via API
def update_config_ui(url, dest, mode, contact_name):
    config = {
        "url": url,
        "dest": dest,
        "mode": mode,
        "contact_name": contact_name
    }
    headers = {API_KEY_NAME: API_KEY}
    try:
        response = requests.post(f"{API_URL}/config", json=config, headers=headers)
        if response.status_code == 200:
            return "Configuration updated successfully."
        else:
            return f"Error updating configuration: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

# Function to trigger spider manually
def trigger_spider_ui():
    headers = {API_KEY_NAME: API_KEY}
    try:
        response = requests.get(f"{API_URL}/trigger", headers=headers)
        if response.status_code == 200:
            return "Spider triggered successfully."
        else:
            return f"Error triggering spider: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

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

# Launch the app
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
