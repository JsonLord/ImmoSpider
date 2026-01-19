import requests
import os

FIRECRAWL_API_URL = "https://api.firecrawl.dev/v2/scrape"
FIRECRAWL_API_TOKEN = os.getenv("FIRECRAWL_API_TOKEN")

def get_flat_details(url: str):
    if not FIRECRAWL_API_TOKEN:
        raise ValueError("FIRECRAWL_API_TOKEN environment variable not set.")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {FIRECRAWL_API_TOKEN}"
    }
    data = {
        "url": url
    }
    response = requests.post(FIRECRAWL_API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json().get('data', {}).get('markdown')
