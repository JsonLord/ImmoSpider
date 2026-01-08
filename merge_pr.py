from huggingface_hub import HfApi
import os

HF_TOKEN = os.environ.get("HF_TOKEN")
REPO_ID = "Leon4gr45/ImmoSpider"
PULL_REQUEST_NUMBER = 15 # Identified from previous step
REPO_TYPE = "space"

if not HF_TOKEN:
    print("HF_TOKEN environment variable not set.")
    exit(1)

api = HfApi(token=HF_TOKEN)

try:
    print(f"Attempting to merge Pull Request #{PULL_REQUEST_NUMBER} in {REPO_ID}...")
    api.merge_pull_request(
        repo_id=REPO_ID,
        discussion_num=PULL_REQUEST_NUMBER,
        repo_type=REPO_TYPE,
    )
    print(f"Pull Request #{PULL_REQUEST_NUMBER} in {REPO_ID} merged successfully.")
except Exception as e:
    print(f"An error occurred while merging Pull Request: {e}")
