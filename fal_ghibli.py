import argparse
import os
import sys
import fal_client
from jproperties import Properties

# ==========================================
# Configuration Loader
# ==========================================
def load_config():
    """Load API key from config.properties."""
    config_path = os.path.join(os.path.dirname(__file__), "config.properties")
    configs = Properties()
    if os.path.exists(config_path):
        with open(config_path, "rb") as f:
            configs.load(f)
        return configs
    else:
        print(f"Error: {config_path} not found.")
        sys.exit(1)



# Proper Ghibli prompt instructions
GHIBLI_PROMPT = (
    "Studio Ghibli art style, whimsical characters, soft lighting, vibrant pastel colors, "
    "lush greens, hand-drawn aesthetic, high detail, masterpiece, "
    "inspired by Hayao Miyazaki, dreamy atmosphere, nostalgic feeling."
)

def generate_ghibli_art(image_path):
    """Transform a local image into Ghibli art using Fal.ai."""
    
    # 1. Verification
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.")
        return

    # 2. Setup Authentication
    configs = load_config()
    fal_api_key = configs.get("fal_api_key").data if configs.get("fal_api_key") else None
    
    if not fal_api_key:
        print("Error: 'fal_api_key' not found in [fal] section of config.properties.")
        sys.exit(1)
        
    # Set FAL_KEY for the client session
    os.environ["FAL_KEY"] = fal_api_key

    print(f"🎨 Initializing Ghibli transformation for: {image_path}")
    
    try:
        # 3. Upload local file to Fal's temporary storage
        print("📤 Uploading image to Fal storage...")
        image_url = fal_client.upload_file(image_path)
        print(f"🌐 Image hosted at: {image_url}")

        # 4. Run the transformation
        # Using 'fal-ai/flux/dev/image-to-image' for high-quality prompt-based stylization
        print("🚀 Submitting request to Fal API (this may take 10-30 seconds)...")
        
        result = fal_client.subscribe(
            "fal-ai/flux/dev/image-to-image",
            arguments={
                "image_url": image_url,
                "prompt": GHIBLI_PROMPT,
                "strength": 0.55,  # Higher = more stylistic change, Lower = more original content
                "num_images": 1,
                "output_format": "jpeg"
            },
            with_logs=True,
            on_queue_update=lambda update: print(f"  [Queue] {update.logs[-1]['message']}") if isinstance(update, fal_client.InProgress) and update.logs else None
        )

        # 5. Handle Results
        if "images" in result and len(result["images"]) > 0:
            rendered_image_url = result["images"][0]["url"]
            print(f"✅ Success! Transformed image: {rendered_image_url}")
            
            # Simple download using requests
            import requests
            
            # Save in the same directory as the input image
            input_dir = os.path.dirname(os.path.abspath(image_path))
            output_filename = os.path.join(input_dir, f"ghibli_fal_{os.path.basename(image_path)}")
            
            img_data = requests.get(rendered_image_url).content
            with open(output_filename, "wb") as f:
                f.write(img_data)
            print(f"💾 Transformation saved as: {output_filename}")
        else:
            print(f"❓ Unexpected response format: {result}")

    except Exception as e:
        print(f"❌ An error occurred during processing: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Studio Ghibli art from an image using Fal API.")
    parser.add_argument("image_path", help="Path to the source image file")
    
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    args = parser.parse_args()
    generate_ghibli_art(args.image_path)
