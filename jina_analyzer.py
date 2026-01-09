import requests
import os

JINA_API_URL = "https://r.jina.ai/"
JINA_API_TOKEN = os.getenv("JINA_API_TOKEN")

def get_flat_details(url: str):
    if not JINA_API_TOKEN:
        raise ValueError("JINA_API_TOKEN environment variable not set.")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {JINA_API_TOKEN}"
    }
    data = {
        "url": url
    }
    response = requests.post(JINA_API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.text
