from huggingface_hub import HfApi
import os

HF_TOKEN = os.environ.get("HF_TOKEN")
REPO_ID = "Leon4gr45/ImmoSpider"
REPO_TYPE = "space"

if not HF_TOKEN:
    print("HF_TOKEN environment variable not set.")
    exit(1)

api = HfApi(token=HF_TOKEN)

try:
    files = api.list_repo_files(repo_id=REPO_ID, repo_type=REPO_TYPE)
    print(f"Successfully listed files in '{REPO_ID}':")
    for file in files:
        print(f"- {file}")
except Exception as e:
    print(f"An error occurred while listing files: {e}")
