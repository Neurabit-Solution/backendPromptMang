
import os
from google import genai
from jproperties import Properties

configs = Properties()
with open('config.properties', 'rb') as config_file:
    configs.load(config_file)

GEMINI_API_KEY = configs.get("gemini_api_key").data

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
