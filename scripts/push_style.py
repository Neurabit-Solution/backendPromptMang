#!/usr/bin/env python3
"""
Push a new style to the database for an existing category.
Uploads the provided image to S3 and creates a Style record.

Usage:
    python scripts/push_style.py \
        --name "Ghibli Soft" \
        --category "anime" \
        --image path/to/image.jpg \
        --prompt "Transform this photo into Ghibli style..." \
        --tags "ghibli,soft,anime" \
        --credits 1
"""

import argparse
import mimetypes
import sys
import re
from pathlib import Path

# Allow importing app when run as script from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.core import s3 as s3_service
from app.models import user  # noqa: F401 — Keep SQLAlchemy mapping happy
from app.models.style import Category, Style

def get_image_bytes_and_type(path: Path) -> tuple[bytes, str]:
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {path}")

    content_type, _ = mimetypes.guess_type(str(path))
    allowed = {"image/jpeg", "image/png", "image/webp"}
    if content_type not in allowed:
        ext = path.suffix.lower()
        if ext in (".jpg", ".jpeg"):
            content_type = "image/jpeg"
        elif ext == ".png":
            content_type = "image/png"
        elif ext == ".webp":
            content_type = "image/webp"
        else:
            raise ValueError(f"Unsupported image type: {ext}. Use .jpg, .png, or .webp.")

    data = path.read_bytes()
    if not data:
        raise ValueError(f"Image file is empty: {path}")
    return data, content_type

def push_style(name, category_slug, image_path, prompt, negative_prompt, slug, description, tags, credits, trending, is_new, is_active, display_order):
    image_path = Path(image_path).resolve()
    image_bytes, content_type = get_image_bytes_and_type(image_path)
    
    if not slug:
        slug = name.lower().strip()
        slug = slug.replace(" ", "-")
        slug = re.sub(r'[^a-z0-9\-]', '', slug)
        slug = re.sub(r'-+', '-', slug)

    db = SessionLocal()
    try:
        # Check if category exists
        cat = db.query(Category).filter(Category.slug == category_slug).first()
        if not cat:
            print(f"Error: Category with slug '{category_slug}' not found.")
            sys.exit(1)

        print(f"Uploading image for '{name}' to S3...")
        preview_url = s3_service.upload_style_thumbnail(image_bytes, slug, content_type)
        
        # Parse tags
        tag_list = [t.strip() for t in tags.split(",")] if tags else []

        # Check if style slug already exists — if so, update it
        style = db.query(Style).filter(Style.slug == slug).first()
        if style:
            print(f"Slug '{slug}' already exists (ID: {style.id}). Updating existing record...")
            style.category_id = cat.id
            style.name = name
            style.preview_url = preview_url
            style.prompt_template = prompt
            style.negative_prompt = negative_prompt or ""
            style.description = description or ""
            style.tags = tag_list
            style.credits_required = credits
            style.is_trending = trending
            style.is_new = is_new
            style.is_active = is_active
            style.display_order = display_order
        else:
            style = Style(
                category_id=cat.id,
                name=name,
                slug=slug,
                description=description or "",
                preview_url=preview_url,
                prompt_template=prompt,
                negative_prompt=negative_prompt or "",
                tags=tag_list,
                credits_required=credits,
                is_trending=trending,
                is_new=is_new,
                is_active=is_active,
                display_order=display_order
            )
            db.add(style)

        db.commit()
        print(f"Successfully processed style!")
        print(f"  Name:     {name}")
        print(f"  Slug:     {slug}")
        print(f"  Category: {cat.name} ({cat.slug})")
        print(f"  Preview:  {preview_url}")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description="Push a new style to the database.")
    parser.add_argument("--name", required=True, help="Display name of the style")
    parser.add_argument("--category", required=True, help="Slug of the category it belongs to")
    parser.add_argument("--image", required=True, help="Path to the style preview image")
    parser.add_argument("--prompt", required=True, help="AI prompt template")
    parser.add_argument("--negative-prompt", help="AI negative prompt")
    parser.add_argument("--slug", help="Slug for the style (auto-generated if not provided)")
    parser.add_argument("--description", help="Short description of the style")
    parser.add_argument("--tags", help="Comma-separated tags (e.g. 'anime,dark,glow')")
    parser.add_argument("--credits", type=int, default=1, help="Credits required (default 1)")
    parser.add_argument("--trending", action="store_true", help="Mark style as trending")
    parser.add_argument("--old", action="store_true", help="Mark style as not new (default is new)")
    parser.add_argument("--inactive", action="store_true", help="Mark style as inactive")
    parser.add_argument("--display-order", type=int, default=0, help="Display order (default 0)")

    args = parser.parse_args()
    
    push_style(
        name=args.name,
        category_slug=args.category,
        image_path=args.image,
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        slug=args.slug,
        description=args.description,
        tags=args.tags,
        credits=args.credits,
        trending=args.trending,
        is_new=not args.old,
        is_active=not args.inactive,
        display_order=args.display_order
    )

if __name__ == "__main__":
    main()
