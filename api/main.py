import fastapi
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import os
import requests
import logging
import telegram
import json
from jina_analyzer import get_flat_details

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Environment Variables ---
API_KEY = os.getenv("API_KEY")
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.0-pro:generateContent?key={GEMINI_API_KEY}"


# --- API Security ---
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header)):
    if not API_KEY or api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key

app = FastAPI()

# --- LLM Analysis ---
def analyze_description(description: str) -> dict:
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not set.")
        return {"error": "LLM API key not configured."}

    headers = {
        "Content-Type": "application/json",
    }

    prompt = f"""
    Analyze the following apartment description. Provide a summary as a JSON object with the following keys: "strengths", "problems", "location", "rating", "message_points", "personalized_message".

    Description:
    {description}
    """

    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=data)
        response.raise_for_status()

        # Correctly parse the JSON response from Gemini
        result = response.json()
        result_json_str = result["candidates"][0]["content"]["parts"][0]["text"]

        # Handle the case where the response is wrapped in markdown
        if result_json_str.strip().startswith("```json"):
            result_json_str = result_json_str.strip()[7:-3].strip()

        analysis_dict = json.loads(result_json_str)

        return analysis_dict
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Gemini API: {e}")
        logger.error(f"Response body: {response.text}")
        return {"error": f"LLM API request failed: {e}"}
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        logger.error(f"Error parsing Gemini response: {e}")
        logger.error(f"Raw response text: {response.text}")
        return {"error": "Invalid LLM API response format."}


# --- Telegram Notifications ---
async def send_telegram_message(message: str):
    if not TELEGRAM_API_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Telegram API Token or Chat ID not set.")
        return

    try:
        bot = telegram.Bot(token=TELEGRAM_API_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
        logger.info("Telegram message sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")

class AnalyzeRequest(BaseModel):
    url: str

@app.post("/analyze")
async def analyze_url(request: AnalyzeRequest, api_key: str = Depends(get_api_key)):
    try:
        logger.info(f"Received analysis request for URL: {request.url}")
        
        flat_description = get_flat_details(request.url)
        if not flat_description:
            raise HTTPException(status_code=500, detail="Failed to get flat details from Jina.")
        
        analysis_result = analyze_description(flat_description)
        if "error" in analysis_result:
            raise HTTPException(status_code=500, detail=analysis_result["error"])

        message = f"""
        *New Flat Analysis:*
        *URL:* {request.url}

        *Strengths:* {analysis_result.get('strengths', 'N/A')}
        *Biggest Problems:* {analysis_result.get('problems', 'N/A')}
        *Location Assessment:* {analysis_result.get('location', 'N/A')}
        *Price-to-Benefits Rating:* {analysis_result.get('rating', 'N/A')}

        *Personalized Message:*
        {analysis_result.get('personalized_message', 'N/A')}
        """
        await send_telegram_message(message)
        
        return {"message": "Analysis complete and notification sent."}

    except Exception as e:
        logger.error(f"An error occurred during analysis: {e}")
        await send_telegram_message(f"An error occurred during analysis for {request.url}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
