import os
from pathlib import Path
from google import genai
from jproperties import Properties

# Load API key from config.properties only (do not hardcode)
_config_path = Path(__file__).resolve().parent / "config.properties"
configs = Properties()
if _config_path.exists():
    with open(_config_path, "rb") as config_file:
        configs.load(config_file)
GEMINI_API_KEY = (configs.get("gemini_api_key").data or "").strip() if configs.get("gemini_api_key") else ""
if not GEMINI_API_KEY:
    raise SystemExit("gemini_api_key not set in config.properties")

client = genai.Client(api_key=GEMINI_API_KEY)

try:
    # Just list models to test connectivity
    models = list(client.models.list())
    print(f"Connection successful! Found {len(models)} models.")
    for m in models:
        if "gemini-2.0-flash-preview-image-generation" in m.name:
            print(f"Found target model: {m.name}")
except Exception as e:
    print(f"Gemini Error: {e}")
