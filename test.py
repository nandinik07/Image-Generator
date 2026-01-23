import os
import sys
import requests

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config

def test_generation():
    print("="*50)
    print("   PIXEL MASTER - GLOBAL API TEST")
    print("="*50)

    key = Config.SILICONFLOW_API_KEY
    if not key:
        print("❌ ERROR: No API Key found in .env")
        return
    
    print(f"✅ Key loaded: {key[:5]}...{key[-4:]}")

    # Correct Global URL
    url = "https://api.siliconflow.com/v1/images/generations"
    print(f"👉 Target: {url}")

    try:
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "black-forest-labs/FLUX.1-schnell",
            "prompt": "Neon sign saying Hello World",
            "image_size": "1024x1024",
            "seed": 12345
        }
        
        print("🚀 Sending request...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            print("✅ SUCCESS! Image generated.")
            print(f"🔗 URL: {response.json()['images'][0]['url']}")
        else:
            print(f"❌ FAILED ({response.status_code})")
            print(f"Reason: {response.text}")

    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_generation()