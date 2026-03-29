#!/usr/bin/env python3
"""
Push a new category to the database.
Uploads the provided image to S3 and creates a Category record in the database.

Usage:
    python scripts/push_category.py --name "Anime" --icon "🎌" --image path/to/image.jpg --description "Anime art styles"
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
from app.models import user  # noqa: F401
from app.models.style import Category

def get_image_bytes_and_type(path: Path) -> tuple[bytes, str]:
    """Read image file and return (bytes, content_type)."""
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {path}")

    content_type, _ = mimetypes.guess_type(str(path))
    allowed = {"image/jpeg", "image/png", "image/webp"}
    
    if content_type not in allowed:
        # Try by extension if mimetypes failed
        ext = path.suffix.lower()
        if ext in (".jpg", ".jpeg"):
            content_type = "image/jpeg"
        elif ext == ".png":
            content_type = "image/png"
        elif ext == ".webp":
            content_type = "image/webp"
        else:
            raise ValueError(
                f"Unsupported image type: {ext}. Use .jpg, .png, or .webp."
            )

    data = path.read_bytes()
    if not data:
        raise ValueError(f"Image file is empty: {path}")
    return data, content_type

def push_category(name, slug, icon, description, image_path, display_order, is_active):
    """Business logic to upload image and create Category in DB."""
    image_path = Path(image_path).resolve()
    image_bytes, content_type = get_image_bytes_and_type(image_path)
    
    # Generate slug if not provided
    if not slug:
        slug = name.lower().strip()
        slug = slug.replace(" ", "-")
        slug = re.sub(r'[^a-z0-9\-]', '', slug)
        # remove double dashes
        slug = re.sub(r'-+', '-', slug)

    db = SessionLocal()
    try:
        # Check if slug or name already exists
        existing_slug = db.query(Category).filter(Category.slug == slug).first()
        if existing_slug:
            print(f"Error: Category with slug '{slug}' already exists (ID: {existing_slug.id}).")
            sys.exit(1)
            
        existing_name = db.query(Category).filter(Category.name == name).first()
        if existing_name:
            print(f"Error: Category with name '{name}' already exists (ID: {existing_name.id}).")
            sys.exit(1)

        print(f"Uploading image for '{name}' to S3...")
        preview_url = s3_service.upload_category_thumbnail(image_bytes, slug, content_type)
        
        cat = Category(
            name=name,
            slug=slug,
            icon=icon or "",
            description=description or "",
            preview_url=preview_url,
            display_order=display_order,
            is_active=is_active
        )
        db.add(cat)
        db.commit()
        print(f"Successfully created category!")
        print(f"  Name:     {name}")
        print(f"  Slug:     {slug}")
        print(f"  Icon:     {icon or 'None'}")
        print(f"  Order:    {display_order}")
        print(f"  Preview:  {preview_url}")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description="Push a new category to the database.")
    parser.add_argument("--name", required=True, help="Display name of the category")
    parser.add_argument("--slug", help="Slug for the category (generated from name if not provided)")
    parser.add_argument("--icon", help="Emoji or icon name for the category")
    parser.add_argument("--description", help="Short description of the category")
    parser.add_argument("--image", required=True, help="Path to the cover/preview image file")
    parser.add_argument("--display-order", type=int, default=0, help="Order in which it appears (default 0)")
    parser.add_argument("--inactive", action="store_true", help="Mark category as inactive")

    args = parser.parse_args()
    
    push_category(
        name=args.name,
        slug=args.slug,
        icon=args.icon,
        description=args.description,
        image_path=args.image,
        display_order=args.display_order,
        is_active=not args.inactive
    )

if __name__ == "__main__":
    main()
