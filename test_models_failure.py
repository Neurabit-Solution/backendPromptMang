
import os
import base64
from google import genai
from google.genai import types
from jproperties import Properties

# Load config
configs = Properties()
with open('config.properties', 'rb') as config_file:
    configs.load(config_file)
GEMINI_API_KEY = configs.get("gemini_api_key").data

client = genai.Client(api_key=GEMINI_API_KEY)

# Use the most likely successful model from the list
test_model = "gemini-2.0-flash-exp-image-generation"

# Tiny 1x1 black pixel in base64 to avoid huge upload
tiny_img_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
img_bytes = base64.b64decode(tiny_img_b64)

print(f"Testing {test_model} with IMAGE response modality...")

try:
    response = client.models.generate_content(
        model=test_model,
        contents=[
            types.Part.from_text(text="Transform this to a watercolor painting"),
            types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
        ],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )
    print("Success!")
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                print(f"Got image back: {part.inline_data.mime_type}")
except Exception as e:
    print(f"Failed: {e}")

# Test the other models mentioned by user
for m in ["gemini-2.5-flash-image", "gemini-3-pro-image-preview"]:
    print(f"\nTesting {m}...")
    try:
        response = client.models.generate_content(
            model=m,
            contents=[
                types.Part.from_text(text="Transform this to a watercolor painting"),
                types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
            ],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )
        print(f"Success with {m}!")
    except Exception as e:
        print(f"Failed {m}: {e}")
