import gradio as gr
import requests
import os

# Get API URL and API key from environment
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "X-API-KEY"

# Function to trigger analysis via API
def analyze_url_ui(url):
    headers = {API_KEY_NAME: API_KEY}
    try:
        response = requests.post(f"{API_URL}/analyze", json={"url": url}, headers=headers)
        if response.status_code == 200:
            return "Analysis triggered successfully. Check your Telegram for the report."
        else:
            return f"Error triggering analysis: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="Flat Analyzer") as demo:
    gr.Markdown("# Flat Analyzer")
    
    with gr.Tab("Analyze"):
        gr.Markdown("## Enter the URL of the flat listing to analyze.")
        with gr.Row():
            url_input = gr.Textbox(label="Flat Listing URL", lines=3, placeholder="https://www.immobilienscout24.de/expose/...")
        
        analyze_btn = gr.Button("Analyze")
        analysis_output = gr.Textbox(label="Status")
        
        analyze_btn.click(
            fn=analyze_url_ui,
            inputs=[url_input],
            outputs=analysis_output
        )
    
    with gr.Tab("About"):
        gr.Markdown("## About Flat Analyzer")
        gr.Markdown("This tool uses the Jina API to read a flat listing, analyzes it with an LLM, and sends a detailed report to your Telegram.")

# Launch the app
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
