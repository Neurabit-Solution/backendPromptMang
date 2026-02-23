import os
from pathlib import Path
from jproperties import Properties
from google import genai
from google.genai import types

# Load API key from config.properties (never hardcode)
_config_path = Path(__file__).resolve().parent / "config.properties"
_configs = Properties()
if _config_path.exists():
    with open(_config_path, "rb") as f:
        _configs.load(f)
API_KEY = (_configs.get("gemini_api_key").data or "").strip() if _configs.get("gemini_api_key") else ""


def check_new_key():
    if not API_KEY:
        print("Error: gemini_api_key not found in config.properties")
        return
    client = genai.Client(api_key=API_KEY)
    
    print(f"--- Checking Models for New Key ---")
    try:
        models = list(client.models.list())
        model_names = [m.name for m in models]
        
        target_models = [
            "gemini-2.5-flash-image", 
            "gemini-3-pro-image-preview",
            "gemini-2.0-flash-exp-image-generation"
        ]
        
        found_any = False
        for tm in target_models:
            match = [name for name in model_names if tm in name]
            if match:
                print(f"[✓] {tm} is available as: {match[0]}")
                found_any = True
                
                # Try a tiny functionality test if found
                print(f"    Testing functionality for {tm}...")
                try:
                    # 1x1 black pixel
                    img_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
                    import base64
                    response = client.models.generate_content(
                        model=match[0],
                        contents=[
                            types.Part.from_text(text="Transform to watercolor"),
                            types.Part.from_bytes(data=base64.b64decode(img_data), mime_type="image/png"),
                        ],
                        config=types.GenerateContentConfig(
                            response_modalities=["IMAGE"],
                        ),
                    )
                    print(f"    [SUCCESS] {tm} supports IMAGE modality!")
                except Exception as e:
                    print(f"    [FAILED] {tm} test: {str(e)[:100]}...")
            else:
                print(f"[X] {tm} not found.")

        if not found_any:
            print("\nNo image generation models found for this key.")

    except Exception as e:
        print(f"Error accessing API with this key: {e}")

if __name__ == "__main__":
    check_new_key()
