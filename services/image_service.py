import os
import requests
import random
import base64
from config import Config

class ImageService:
    @staticmethod
    def generate_image(prompt, style="Realistic", size="1024x1024", seed=None, image_file=None, strength=0.7):
        """
        Generates an image using SiliconFlow API (FLUX.1-dev).
        
        UPDATED (QA REPORT IMPLEMENTATION):
        - Implemented 'Asymmetry Bias' for hands to fix mirroring.
        - Added 'Procedural Noise' injection for architecture to fix tiling.
        - Added 'Semantic Grounding' for text/code contexts.
        - tuned guidance scales based on subject density.
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
        
        # 2. Context Detection & QA Fixes
        
        # CONTEXT A: HANDS (QA Fix: Symmetry Bias & Micro-Blur)
        hand_keywords = ["hand", "finger", "thumb", "palm", "fist", "holding", "grasping", "touching", "interacting"]
        has_hands = any(k in user_prompt_lower for k in hand_keywords)
        
        # CONTEXT B: FACES (QA Fix: Over-Smoothing/Beauty Bias)
        face_keywords = ["face", "portrait", "headshot", "close-up", "woman", "man", "person", "girl", "boy", "eye", "smile"]
        has_face = any(k in user_prompt_lower for k in face_keywords)

        # CONTEXT C: ARCHITECTURE (QA Fix: Tiling/Repetition)
        arch_keywords = ["library", "tower", "building", "city", "skyscraper", "shelves", "structure", "bridge", "castle"]
        has_arch = any(k in user_prompt_lower for k in arch_keywords)

        # CONTEXT D: UI/CODE/TEXT (QA Fix: Semantic/Logic coherence)
        text_keywords = ["code", "ui", "interface", "dashboard", "screen", "monitor", "hologram", "sign", "neon", "text"]
        has_text = any(k in user_prompt_lower for k in text_keywords)

        # --- INJECTION LOGIC ---

        base_quality = "perfect anatomy, high quality"
        injections = []

        if has_hands:
            # Fix: "Finger tension symmetry" -> Force asymmetry
            # Fix: "Micro-wrinkle blur" -> Request high-frequency detail
            injections.append("anatomically correct hands, asymmetrical hand positioning, distinct finger joints, visible knuckle creases, raw skin texture, micro-details, no smoothing")
            guidance_val = 2.5 # Lower guidance allows more natural noise (less plastic)

        if has_face:
            # Fix: "Over-perfect skin zones" -> Request imperfections and subsurface scattering
            # Fix: "Hair-root transition" -> Request follicle depth
            injections.append("natural skin imperfections, visible pores, uneven skin tone, subsurface scattering, micro-shadows on face, realistic hair root transition, unpolished raw beauty")

        if has_arch:
            # Fix: "Structural repetition/Tiling" -> Request procedural variation
            injections.append("unique architectural details, procedural variation, randomized object placement, no repetitive tiling, complex depth map, organic structural flow")

        if has_text:
            # Fix: "Text semantics/Pseudo-language" -> Request legible text
            # Fix: "UI layer blending" -> Request sharp edges
            injections.append("legible text, correct syntax, sharp UI edges, monospaced font, semantic consistency, coherent interface, vector-sharp graphics")
            guidance_val = 3.5 # Higher guidance forces better text adherence

        # Combine Injections
        anatomy_prompt = f"{base_quality}, {', '.join(injections)}" if injections else base_quality

        # 3. Construct the prompt
        if clean_style and clean_style.lower() not in ["realistic", "none", "generated", "photorealistic"]:
            full_prompt = f"{anatomy_prompt}, {prompt}, {clean_style} style"
        else:
            full_prompt = f"{anatomy_prompt}, {prompt}"

        # 4. Refined Negative Prompt (Targeting specific QA failures)
        # Added: "mirrored limbs" (for hands), "tiling textures" (for library), "nonsense text" (for UI)
        negative_prompt = "extra fingers, missing fingers, fused fingers, malformed limbs, mutated hands, poorly drawn hands, bad anatomy, wrong anatomy, extra limbs, floating limbs, disconnected limbs, mutation, ugly, disgusting, blurry, amputation, messy lines, loose strokes, plastic skin, airbrushed, too smooth, mirrored limbs, symmetry bias, repetitive tiling, tiling textures, glitchy UI, nonsense text, melting text, pseudo-language"
        
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

        # Using FLUX.1-dev
        model = "black-forest-labs/FLUX.1-dev"

        payload = {
            "model": model,
            "prompt": full_prompt,
            "negative_prompt": negative_prompt, 
            "image_size": size,
            "seed": final_seed,
            "num_inference_steps": 50,
            "guidance_scale": guidance_val
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