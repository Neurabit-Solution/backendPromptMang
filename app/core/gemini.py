"""
Gemini Service — sends the user's image + style prompt to Google Gemini
and returns the generated image bytes.

Uses the new official `google-genai` SDK (google-generativeai is deprecated).
Model: gemini-2.0-flash-preview-image-generation
  (supports image input + image output in a single call)
"""

import base64
import time
from google import genai
from google.genai import types
from app.core.config import settings


def _get_client() -> genai.Client:
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def transform_image(
    image_bytes: bytes,
    image_mime: str,
    prompt: str,
) -> tuple[bytes, float]:
    """
    Send image + prompt to Gemini and return (generated_image_bytes, processing_time_seconds).

    Parameters
    ----------
    image_bytes : raw bytes of the user's uploaded photo
    image_mime  : MIME type, e.g. "image/jpeg" or "image/png"
    prompt      : the fully-assembled style prompt

    Returns
    -------
    (image_bytes, seconds_taken)
    """
    client = _get_client()

    start = time.time()

    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=[
            types.Part.from_text(text=prompt),
            types.Part.from_bytes(data=image_bytes, mime_type=image_mime),
        ],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        ),
    )

    elapsed = round(time.time() - start, 2)

    # Extract the image bytes from the response
    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.mime_type.startswith("image/"):
            return base64.b64decode(part.inline_data.data), elapsed

    raise ValueError("Gemini did not return an image in its response.")


def build_final_prompt(
    prompt_template: str,
    mood: str | None = None,
    weather: str | None = None,
    dress_style: str | None = None,
    custom_prompt: str | None = None,
) -> str:
    """
    Merge the style's base prompt template with the user's optional customisations
    into one final string sent to Gemini.
    """
    parts = [prompt_template]

    if mood:
        parts.append(f"The mood should feel {mood}.")
    if weather:
        parts.append(f"The weather/environment should look {weather}.")
    if dress_style:
        parts.append(f"The subject's clothing style should be {dress_style}.")
    if custom_prompt:
        parts.append(f"Additional instruction: {custom_prompt}")

    parts.append(
        "Maintain the subject's facial features and identity. Output only the transformed image."
    )

    return " ".join(parts)
