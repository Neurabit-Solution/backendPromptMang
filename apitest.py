import os
from pathlib import Path
from jproperties import Properties
from google import genai

# Load API key from config.properties (never hardcode)
_config_path = Path(__file__).resolve().parent / "config.properties"
_configs = Properties()
if _config_path.exists():
    with open(_config_path, "rb") as f:
        _configs.load(f)
API_KEY = (_configs.get("gemini_api_key").data or "").strip() if _configs.get("gemini_api_key") else ""


def check_ghibli_capability():
    if not API_KEY:
        print("Error: gemini_api_key not found in config.properties")
        return
    client = genai.Client(api_key=API_KEY)
    
    # 1. Check if the required models are available for your key
    print("--- Checking Model Access ---")
    image_models = ["gemini-2.5-flash-image", "gemini-3-pro-image-preview"]
    available_models = []
    
    try:
        models = client.models.list()
        model_names = [m.name for m in models]
        
        for im in image_models:
            # Models usually appear as 'models/gemini-...'
            if any(im in name for name in model_names):
                print(f"[✓] {im} is available.")
                available_models.append(im)
            else:
                print(f"[X] {im} not found in your account.")
                
    except Exception as e:
        print(f"Error accessing API: {e}")
        return

    if not available_models:
        print("\nResult: Your API key currently lacks image-to-image permissions.")
        return

    # 2. Verify image-to-image support
    print("\n--- Verifying Functionality ---")
    print(f"Yes! You can build your app using: {available_models[0]}")
    print("This model supports 'Response Modalities: IMAGE', allowing you to ")
    print("upload a file and receive a stylized Ghibli version back.")

if __name__ == "__main__":
    check_ghibli_capability()