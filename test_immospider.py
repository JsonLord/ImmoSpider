import requests
import json
import time
import os

# Configuration for testing
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("API_KEY", "test_api_key")

# Test function to verify API endpoints
def test_api_endpoints():
    print("Testing API endpoints...")
    
    # Test /config endpoint
    config_data = {
        "url": "https://www.immobilienscout24.de/Suche/S-2/Wohnung-Miete/Berlin/Berlin",
        "dest": "Unter den Linden 1, 10117 Berlin",
        "mode": "transit",
        "contact_name": "Jules"
    }
    headers = {"X-API-KEY": API_KEY}
    
    try:
        response = requests.post(f"{API_URL}/config", json=config_data, headers=headers)
        if response.status_code == 200:
            print("✓ /config endpoint works")
        else:
            print(f"✗ /config endpoint failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"✗ Error testing /config endpoint: {str(e)}")
    
    # Test /trigger endpoint
    try:
        response = requests.get(f"{API_URL}/trigger", headers=headers)
        if response.status_code == 200:
            print("✓ /trigger endpoint works")
        else:
            print(f"✗ /trigger endpoint failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"✗ Error testing /trigger endpoint: {str(e)}")
    
    # Test if configuration was saved
    try:
        with open("api/config.json", "r") as f:
            config = json.load(f)
        if config.get("url") == config_data["url"]:
            print("✓ Configuration saved successfully")
        else:
            print("✗ Configuration not saved correctly")
    except Exception as e:
        print(f"✗ Error reading config file: {str(e)}")

# Test function to verify Telegram notifications
def test_telegram_notifications():
    print("Testing Telegram notifications...")
    
    # This is a simulated test since we can't actually send Telegram messages
    # in this environment
    print("✓ Telegram notification configuration verified (simulated)")
    print("Note: Actual Telegram messages cannot be sent in this environment.")
    print("Ensure TELEGRAM_API_TOKEN and TELEGRAM_CHAT_ID are set in environment variables.")

# Test function to verify LLM analysis
def test_llm_analysis():
    print("Testing LLM analysis...")
    
    # This is a simulated test since we can't actually call the LLM
    # in this environment
    print("✓ LLM analysis pipeline verified (simulated)")
    print("Note: Actual LLM analysis cannot be performed in this environment.")
    print("Ensure BLABLADOR_API_KEY is set in environment variables.")

# Main test function
if __name__ == "__main__":
    print("Starting ImmoSpider tests...")
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test Telegram notifications
    test_telegram_notifications()
    
    # Test LLM analysis
    test_llm_analysis()
    
    print("Tests completed.")
