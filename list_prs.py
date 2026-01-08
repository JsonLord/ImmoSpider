from huggingface_hub import get_repo_discussions
import os

HF_TOKEN = os.environ.get("HF_TOKEN")
REPO_ID = "Leon4gr45/ImmoSpider"
REPO_TYPE = "space"

if not HF_TOKEN:
    print("HF_TOKEN environment variable not set.")
    exit(1)

try:
    print(f"Listing open pull requests for {REPO_ID} (type: {REPO_TYPE})...")
    prs = get_repo_discussions(
        repo_id=REPO_ID,
        repo_type=REPO_TYPE,
        token=HF_TOKEN,
        discussion_type="pull_request",
        discussion_status="open",
    )
    
    if not prs:
        print("No open pull requests found.")
    else:
        for discussion in prs:
            print(f"PR Number: {discussion.num}, Title: {discussion.title}, Status: {discussion.status}")

except Exception as e:
    print(f"An error occurred while listing pull requests: {e}")
