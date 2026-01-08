from huggingface_hub import HfApi
import os

HF_TOKEN = os.environ.get("HF_TOKEN")
REPO_ID = "Leon4gr45/ImmoSpider"
LOCAL_PATH = "."
REPO_TYPE = "space"
COMMIT_MESSAGE = "Update Space with latest changes from local repository"

if not HF_TOKEN:
    print("HF_TOKEN environment variable not set.")
    exit(1)

api = HfApi(token=HF_TOKEN)

try:
    api.upload_folder(
        folder_path=LOCAL_PATH,
        repo_id=REPO_ID,
        repo_type=REPO_TYPE,
        commit_message=COMMIT_MESSAGE,
        ignore_patterns=[".git*", ".hf_token"], # Ignore git files and the token file if it exists locally
        create_pr=True,
    )
    print(f"Successfully uploaded folder '{LOCAL_PATH}' to '{REPO_ID}' of type '{REPO_TYPE}'.")
    print(f"Check your Space here: https://huggingface.co/{REPO_ID}")
except Exception as e:
    print(f"An error occurred during upload: {e}")
