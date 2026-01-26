import os
import requests
import random
from config import Config

class ImageService:
    @staticmethod
    def generate_image(prompt, style="Realistic", size="1024x1024", seed=None):
        """
        Generates an image using SiliconFlow API (Flux Model).
        Raises an Exception with the specific error message on failure.
        """
        api_key = Config.SILICONFLOW_API_KEY
        
        if not api_key:
            raise Exception("Configuration Error: SiliconFlow API Key is missing in .env or config.py")

        url = "https://api.siliconflow.com/v1/images/generations"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Enhancing prompt - Flux works better with descriptive keywords
        full_prompt = f"{style} style, high quality, detailed: {prompt}"
        
        # Determine Seed
        final_seed = None
        if seed is not None and str(seed).strip() != "":
            try:
                final_seed = int(seed)
            except ValueError:
                final_seed = random.randint(0, 4294967295)
        else:
            final_seed = random.randint(0, 4294967295)

        # Payload
        payload = {
            "model": "black-forest-labs/FLUX.1-schnell",
            "prompt": full_prompt,
            "image_size": size,
            "seed": final_seed
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            # Check for HTTP errors
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', response.text)
                    if isinstance(error_data.get('error'), dict):
                        error_msg = error_data['error'].get('message', error_msg)
                except:
                    error_msg = response.text
                
                raise Exception(f"SiliconFlow API Error ({response.status_code}): {error_msg}")

            result = response.json()
            
            # Extract image URL
            if 'images' in result and len(result['images']) > 0:
                return result['images'][0]['url']
            else:
                raise Exception(f"Unexpected response format from API: {result}")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network Connection Error: {str(e)}")