import os
import requests
import random
import base64
from config import Config

class ImageService:
    @staticmethod
    def generate_image(prompt, style="Realistic", size="1024x1024", seed=None, image_file=None, strength=0.7):
        """
        Generates an image using SiliconFlow API.
        Optimized for FLUX.1-dev with smart anatomy injection for hands.
        """
        api_key = Config.SILICONFLOW_API_KEY
        
        if not api_key:
            raise Exception("Configuration Error: SiliconFlow API Key is missing in .env or config.py")

        url = "https://api.siliconflow.com/v1/images/generations"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # --- PROMPT ENGINEERING LOGIC ---
        
        # 1. Identify intent
        clean_style = style.strip()
        user_prompt_lower = prompt.lower()
        
        # Default settings
        guidance_val = 3.0
        
        # 2. Detect Context
        
        # CONTEXT A: HANDS (The hardest anatomy test)
        hand_keywords = ["hand", "finger", "thumb", "palm", "fist", "holding", "grasping", "touching", "interacting"]
        has_hands = any(k in user_prompt_lower for k in hand_keywords)
        
        # CONTEXT B: FACES (The realism test)
        face_keywords = ["face", "portrait", "headshot", "close-up", "woman", "man", "person", "girl", "boy", "eye", "smile"]
        has_face = any(k in user_prompt_lower for k in face_keywords)

        if has_hands:
            # QA FIX 1: Texture & Waxiness
            # We inject specific texture keywords to fight the smooth/plastic look
            anatomy_prompt = "perfect anatomy, anatomically correct hands, detailed fingers, accurate limb structure, 5 fingers, realistic proportions, fine skin texture, visible micro wrinkles, pore detail"
            
            # QA FIX 2: Lower Guidance
            # Lowering CFG to 2.5 allows more natural noise, reducing the "waxy" over-processed look
            guidance_val = 2.5
            
            # SPECIAL FIX: Abstract/Loose styles
            if clean_style.lower() in ["sketch", "pop art", "watercolor", "impressionist", "oil painting"]:
                anatomy_prompt += ", sharp focus, precise lines, high detail, clear outlines"

            # SPECIAL FIX: Holographic/UI Interaction
            tech_keywords = ["hologram", "holographic", "interface", "dashboard", "ui", "screen", "glass", "transparent", "cyberspace", "futuristic"]
            if any(k in user_prompt_lower for k in tech_keywords):
                anatomy_prompt += ", opaque hands, solid fingers, natural skin texture, visible knuckles, hands in front of screen"
        
        elif has_face:
            # QA FIX 3: Face Realism
            # Killing the "beauty filter" effect by forcing imperfections
            anatomy_prompt = "perfect anatomy, high quality, natural skin imperfections, uneven skin texture, subtle blemishes, real skin pores, non-smooth skin, authentic look"
        
        else:
            anatomy_prompt = "perfect anatomy, high quality"

        # 3. Construct the prompt
        # Anatomy/Structure ALWAYS First -> User Content -> Style
        
        if clean_style and clean_style.lower() not in ["realistic", "none", "generated", "photorealistic"]:
            full_prompt = f"{anatomy_prompt}, {prompt}, {clean_style} style"
        else:
            full_prompt = f"{anatomy_prompt}, {prompt}"

        # 4. Refined Negative Prompt for Flux
        negative_prompt = "extra fingers, missing fingers, fused fingers, malformed limbs, mutated hands, poorly drawn hands, bad anatomy, wrong anatomy, extra limbs, floating limbs, disconnected limbs, mutation, ugly, disgusting, blurry, amputation, messy lines, loose strokes, plastic skin, airbrushed, too smooth"
        
        # Add specific negatives for holographic interactions
        if has_hands and any(k in user_prompt_lower for k in ["hologram", "holographic", "glass", "transparent"]):
             negative_prompt += ", transparent hands, see-through fingers, ghost hands, glitchy fingers, fingers blending with background, wireframe hands"

        # Seed logic
        if seed is None or seed == "":
            final_seed = random.randint(0, 4294967295)
        else:
            try:
                final_seed = int(seed)
            except (ValueError, TypeError):
                final_seed = random.randint(0, 4294967295)

        # Using FLUX.1-dev (Best for anatomy/hands)
        model = "black-forest-labs/FLUX.1-dev"

        payload = {
            "model": model,
            "prompt": full_prompt,
            "negative_prompt": negative_prompt, 
            "image_size": size,
            "seed": final_seed,
            "num_inference_steps": 50,  # High step count for complex anatomy
            "guidance_scale": guidance_val # Dynamic guidance based on subject (2.5 for hands, 3.0 otherwise)
        }

        # Handle Image Input (Image-to-Image)
        if image_file:
            encoded_image = base64.b64encode(image_file).decode('utf-8')
            payload["image"] = encoded_image
            payload["strength"] = strength

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120) 
            
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

            if 'images' in result and len(result['images']) > 0:
                return result['images'][0]['url']
            else:
                raise Exception(f"Unexpected response format from API: {result}")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network Connection Error: {str(e)}")