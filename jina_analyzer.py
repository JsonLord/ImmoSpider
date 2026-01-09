import requests
import os

JINA_API_URL = "https://r.jina.ai/"
JINA_API_TOKEN = os.getenv("JINA_API_TOKEN", "jina_ad6af853c6b345b3a4adf75a8059287adrTdXzZAKPgUgW4IpxwoZecs7nCj")

def get_flat_details(url: str):
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
