import argparse
import base64
import os
import requests
import sys

# ==========================================
# Configuration
# ==========================================
API_KEY = "key_CYmSWb2qtpqM7G5ddZLAd"
# The official AIML API endpoint for generation
API_URL = "https://api.aimlapi.com/v1/images/generations"

# Proper Ghibli prompt as requested
GHIBLI_PROMPT = (
    "Studio Ghibli art style, whimsical characters, soft lighting, vibrant pastel colors, "
    "lush greens, hand-drawn aesthetic, high detail, masterpiece, "
    "inspired by Hayao Miyazaki, dreamy atmosphere, nostalgic feeling."
)

def image_to_data_uri(image_path):
    """Convert local image file to base64 data URI"""
    try:
        ext = os.path.splitext(image_path)[1].lower().replace('.', '')
        if ext == 'jpg': ext = 'jpeg'
        mime_type = f"image/{ext}"
        with open(image_path, "rb") as image_file:
            img_b64 = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:{mime_type};base64,{img_b64}"
    except Exception as e:
        print(f"Error reading image file: {e}")
        sys.exit(1)

def generate_ghibli_art(input_image_path):
    """Send image to Flux API for Ghibli stylization"""
    
    if not os.path.exists(input_image_path):
        print(f"Error: File '{input_image_path}' not found.")
        return

    print(f"🎨 Initializing Ghibli transformation for: {input_image_path}")
    print(f"📝 Prompt: {GHIBLI_PROMPT}")

    # Encode image to base64 data URI
    img_data_uri = image_to_data_uri(input_image_path)

    # Prepare payload for AIML API
    payload = {
        "model": "flux/dev/image-to-image",
        "prompt": GHIBLI_PROMPT,
        "image_url": img_data_uri,
        "strength": 0.55,
        "num_images": 1,
        "steps": 30
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    print("🚀 Sending request to AIML API (this may take 10-30 seconds)...")
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        
        # Check for HTTP errors
        if response.status_code != 200:
            print(f"❌ API Error ({response.status_code}): {response.text}")
            return

        result = response.json()

        # Handle the standard OpenAI-style image response
        if "data" in result and len(result["data"]) > 0:
            image_data = result["data"][0]
            
            output_filename = f"ghibli_{os.path.basename(input_image_path)}"
            
            if "url" in image_data:
                image_url = image_data["url"]
                print(f"✅ Success! Image generated at: {image_url}")
                # Download the image
                img_res = requests.get(image_url)
                with open(output_filename, "wb") as f:
                    f.write(img_res.content)
                print(f"💾 Downloaded and saved as: {output_filename}")
            elif "b64_json" in image_data:
                # Assume it's base64
                with open(output_filename, "wb") as f:
                    f.write(base64.b64decode(image_data["b64_json"]))
                print(f"✅ Success! Saved transformation as: {output_filename}")
        else:
            print(f"❓ Unexpected response format: {result}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    # Parsing the input image path as requested
    parser = argparse.ArgumentParser(description="Create Studio Ghibli art from an image using Flux API.")
    parser.add_argument("image_path", help="Path to the source image file")
    
    # If no arguments are provided, show help
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    args = parser.parse_args()
    
    generate_ghibli_art(args.image_path)
