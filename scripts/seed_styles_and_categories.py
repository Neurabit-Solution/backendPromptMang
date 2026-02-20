#!/usr/bin/env python3
"""
Seed the database with dummy categories and styles.

Uses a single image file (passed as argument) as the preview/thumbnail for
all categories and all styles. Uploads that image to S3 under
categories/thumbnails/<slug>.jpg and styles/thumbnails/<slug>.jpg, then
inserts Category and Style rows with the returned URLs.

Usage (run standalone from project root; no PYTHONPATH needed):
    python scripts/seed_styles_and_categories.py path/to/image.jpg

Or from anywhere, passing the script path:
    python /path/to/backendPromptMang/scripts/seed_styles_and_categories.py path/to/image.jpg

Supported image types: .jpg, .jpeg, .png, .webp
"""

import argparse
import mimetypes
import sys
from pathlib import Path

# Allow importing app when run as script from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.core import s3 as s3_service
from app.models import user  # noqa: F401 — register User so Creation.user relationship resolves
from app.models.style import Category, Style


# Dummy categories: (name, slug, icon, description, display_order)
DUMMY_CATEGORIES = [
    ("Anime", "anime", "🎌", "Anime and manga inspired art styles", 0),
    ("Traditional", "traditional", "🪷", "Classical and traditional art styles", 1),
    ("Fantasy", "fantasy", "🐉", "Fantasy and mythical themes", 2),
]

# Dummy styles: (name, slug, description, prompt_template, category_slug, credits, is_trending, is_new, display_order, tags)
DUMMY_STYLES = [
    # Anime
    (
        "Ghibli Art",
        "ghibli-art",
        "Studio Ghibli inspired soft anime illustration",
        "Transform this photo into a Studio Ghibli anime illustration. Soft colors, gentle lighting, whimsical style.",
        "anime",
        50,
        True,
        True,
        0,
        ["anime", "ghibli", "soft"],
    ),
    (
        "Neon Anime",
        "neon-anime",
        "Vibrant neon-lit anime style",
        "Transform this photo into a vibrant neon anime style with glowing outlines and cyberpunk vibes.",
        "anime",
        50,
        True,
        False,
        1,
        ["anime", "neon", "cyberpunk"],
    ),
    (
        "Manga Portrait",
        "manga-portrait",
        "Black and white manga portrait style",
        "Transform this photo into a classic black and white manga portrait with clear linework and screentone.",
        "anime",
        30,
        False,
        True,
        2,
        ["anime", "manga", "bw"],
    ),
    # Traditional
    (
        "Oil Painting",
        "oil-painting",
        "Classical oil painting style",
        "Transform this photo into a classical oil painting with visible brushstrokes and rich colors.",
        "traditional",
        50,
        True,
        False,
        0,
        ["traditional", "oil", "classical"],
    ),
    (
        "Watercolor",
        "watercolor",
        "Soft watercolor illustration",
        "Transform this photo into a soft watercolor painting with flowing washes and gentle edges.",
        "traditional",
        40,
        False,
        True,
        1,
        ["traditional", "watercolor", "soft"],
    ),
    (
        "Pencil Sketch",
        "pencil-sketch",
        "Detailed pencil sketch style",
        "Transform this photo into a detailed pencil sketch with fine shading and realistic texture.",
        "traditional",
        30,
        False,
        False,
        2,
        ["traditional", "sketch", "pencil"],
    ),
    # Fantasy
    (
        "Dragon Rider",
        "dragon-rider",
        "Epic fantasy dragon rider theme",
        "Transform this photo into an epic fantasy scene as a dragon rider with dramatic lighting and scale.",
        "fantasy",
        60,
        True,
        True,
        0,
        ["fantasy", "dragon", "epic"],
    ),
    (
        "Elf Portrait",
        "elf-portrait",
        "Ethereal elf fantasy portrait",
        "Transform this photo into an ethereal elf portrait with pointed ears, mystical glow, and forest vibes.",
        "fantasy",
        50,
        False,
        True,
        1,
        ["fantasy", "elf", "ethereal"],
    ),
    (
        "Cosmic",
        "cosmic",
        "Space and cosmic themed art",
        "Transform this photo into a cosmic portrait with stars, nebulae, and otherworldly atmosphere.",
        "fantasy",
        50,
        True,
        False,
        2,
        ["fantasy", "cosmic", "space"],
    ),
]


def get_image_bytes_and_type(path: Path) -> tuple[bytes, str]:
    """Read image file and return (bytes, content_type)."""
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {path}")

    content_type, _ = mimetypes.guess_type(str(path))
    allowed = {"image/jpeg", "image/png", "image/webp"}
    if content_type not in allowed:
        # Try by extension
        ext = path.suffix.lower()
        if ext in (".jpg", ".jpeg"):
            content_type = "image/jpeg"
        elif ext == ".png":
            content_type = "image/png"
        elif ext == ".webp":
            content_type = "image/webp"
        else:
            raise ValueError(
                f"Unsupported image type. Use one of: {', '.join(allowed)}. Got: {path.suffix or content_type}"
            )

    data = path.read_bytes()
    if not data:
        raise ValueError(f"Image file is empty: {path}")
    return data, content_type


def seed(image_path: str) -> None:
    image_path = Path(image_path).resolve()
    print(f"Using image: {image_path}")

    image_bytes, content_type = get_image_bytes_and_type(image_path)
    print(f"Image size: {len(image_bytes)} bytes, type: {content_type}")

    db = SessionLocal()
    try:
        category_by_slug: dict[str, Category] = {}

        # 1. Create categories and upload same image as category thumbnail
        print("\n--- Categories ---")
        for name, slug, icon, description, display_order in DUMMY_CATEGORIES:
            existing = db.query(Category).filter(Category.slug == slug).first()
            if existing:
                print(f"  Skip (exists): {name} ({slug})")
                category_by_slug[slug] = existing
                continue

            preview_url = s3_service.upload_category_thumbnail(
                image_bytes, slug, content_type
            )
            cat = Category(
                name=name,
                slug=slug,
                icon=icon,
                description=description,
                preview_url=preview_url,
                display_order=display_order,
                is_active=True,
            )
            db.add(cat)
            db.flush()  # get cat.id
            category_by_slug[slug] = cat
            print(f"  Created: {name} ({slug}) -> {preview_url[:60]}...")

        # 2. Create styles and upload same image as style thumbnail
        print("\n--- Styles ---")
        for (
            name,
            slug,
            description,
            prompt_template,
            cat_slug,
            credits,
            is_trending,
            is_new,
            display_order,
            tags,
        ) in DUMMY_STYLES:
            existing = db.query(Style).filter(Style.slug == slug).first()
            if existing:
                print(f"  Skip (exists): {name} ({slug})")
                continue

            cat = category_by_slug.get(cat_slug)
            if not cat:
                print(f"  Skip (unknown category {cat_slug}): {name}")
                continue

            preview_url = s3_service.upload_style_thumbnail(
                image_bytes, slug, content_type
            )
            style = Style(
                category_id=cat.id,
                name=name,
                slug=slug,
                description=description,
                preview_url=preview_url,
                prompt_template=prompt_template,
                credits_required=credits,
                is_trending=is_trending,
                is_new=is_new,
                is_active=True,
                display_order=display_order,
                tags=tags,
            )
            db.add(style)
            print(f"  Created: {name} ({slug}) in {cat_slug} -> {preview_url[:60]}...")

        db.commit()
        print("\nDone. Categories and styles seeded; your image is used as thumbnail for all.")
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed dummy categories and styles; use one image as preview for all."
    )
    parser.add_argument(
        "image",
        type=str,
        help="Path to image file (e.g. image.jpg). Used as thumbnail for all categories and styles.",
    )
    args = parser.parse_args()

    try:
        seed(args.image)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
