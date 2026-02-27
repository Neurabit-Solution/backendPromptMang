#!/usr/bin/env python3
"""

"""

import argparse
import mimetypes
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.gemini import transform_image


def get_mime(path: Path) -> str:
    guessed = mimetypes.guess_type(str(path))[0]
    if guessed and guessed.startswith("image/"):
        return guessed
    ext = path.suffix.lower()
    if ext in (".jpg", ".jpeg"):
        return "image/jpeg"
    if ext == ".png":
        return "image/png"
    if ext == ".webp":
        return "image/webp"
    return "image/jpeg"


def main():
    # parser = argparse.ArgumentParser(description="Convert image to Ghibli art via Gemini")
    parser.add_argument("image", type=Path, help="Path to input image")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output path (default: <input>_ghibli.jpg)")
    args = parser.parse_args()

    if not args.image.exists():
        print(f"Error: file not found: {args.image}")
        sys.exit(1)
    if not args.image.is_file():
        print(f"Error: not a file: {args.image}")
        sys.exit(1)

    prompt = (
        "Transform this photo into a Studio Ghibli anime illustration. "
        "Soft colors, gentle lighting, whimsical style. "
        "Maintain the subject's facial features and identity. "
        "Output only the transformed image."
    )

    image_bytes = args.image.read_bytes()
    mime = get_mime(args.image)

    if args.output is not None:
        out_path = Path(args.output)
    else:
        stem = args.image.stem
        out_path = args.image.parent / f"{stem}_ghibli.jpg"

    print(f"Input: {args.image} ({len(image_bytes)} bytes)")
    print("Calling Gemini (Ghibli style, model: gemini-3-pro-image-preview)...")
    out_bytes, elapsed = transform_image(
        image_bytes, mime, prompt, model="models/gemini-3-pro-image-preview"
    )
    out_path.write_bytes(out_bytes)
    print(f"Done in {elapsed}s. Saved: {out_path} ({len(out_bytes)} bytes)")


if __name__ == "__main__":
    main()
