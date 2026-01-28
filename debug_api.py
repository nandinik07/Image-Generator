import os
import sys
import requests
from dotenv import load_dotenv

# Load env variables
load_dotenv()

def debug_connection():
    print("="*60)
    print("   PIXEL MASTER - HAND QUALITY TEST")
    print("="*60)

    # 1. Check API Key
    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key:
        print("❌ CRITICAL: 'SILICONFLOW_API_KEY' not found in .env file")
        return
    
    masked_key = f"{api_key[:6]}...{api_key[-4:]}"
    print(f"🔑 API Key Loaded: {masked_key}")

    # 2. Define Endpoint & Payload
    url = "https://api.siliconflow.com/v1/images/generations"
    
    # Updated test prompt to specifically check finger/hand quality
    payload = {
        "model": "black-forest-labs/FLUX.1-schnell",
        "prompt": "Close up photo of hands holding a coffee cup, detailed anatomy, 5 fingers, realistic skin texture, 8k, cinematic lighting",
        "image_size": "1024x1024",
        "seed": 42
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    print(f"📡 Connecting to: {url}")
    print(f"📦 Payload: {payload}")
    print("-" * 60)

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"🔄 HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'images' in data and len(data['images']) > 0:
                print("✅ SUCCESS! Image generated.")
                print(f"🔗 URL: {data['images'][0]['url']}")
            else:
                print("⚠️  200 OK, but unexpected format:")
                print(data)
        else:
            print("❌ FAILURE")
            print(f"Response: {response.text}")
            
            if response.status_code == 401:
                print("\n💡 TIP: Your API key might be invalid.")
            elif response.status_code == 402 or response.status_code == 403:
                print("\n💡 TIP: Check your account balance (Credits).")
            elif response.status_code == 500:
                print("\n💡 TIP: Server Error. If this persists, the 'image_size' or 'model' might be temporarily unavailable.")

    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

if __name__ == "__main__":
    debug_connection()