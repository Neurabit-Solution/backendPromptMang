# Styles, Categories & AI Image Generation — Implementation Overview

> This document explains everything that was built to support the MagicPic home screen
> (style cards like "Ghibli Art", "Red Saree", "Neon Glow") and the AI image generation flow.

---

## Table of Contents

1. [What Was Built](#1-what-was-built)
2. [Database Models](#2-database-models)
3. [S3 Bucket Structure](#3-s3-bucket-structure)
4. [Services](#4-services)
5. [API Endpoints](#5-api-endpoints)
6. [Configuration](#6-configuration)
7. [Dependencies Added](#7-dependencies-added)
8. [How Everything Connects](#8-how-everything-connects)
9. [Next Steps](#9-next-steps)

---

## 1. What Was Built

The goal was to power two main product flows:

**Flow A — Home Screen (Style Discovery)**
> User opens the app → sees style cards (Ghibli Art, Red Saree, etc.) with thumbnail images → these come from the backend, not hardcoded in the frontend.

**Flow B — Image Generation**
> User picks a style → uploads their photo → backend sends the photo + the style's AI prompt to Gemini → Gemini returns a transformed image → both images are saved to S3 → URLs are stored in the database → result is returned to the user.

### Files Created

| File | Role |
|---|---|
| `app/models/style.py` | Database table definitions for `Category`, `Style`, `Creation` |
| `app/core/s3.py` | Service to upload images to AWS S3 |
| `app/core/gemini.py` | Service to call Google Gemini AI for image transformation |
| `app/schemas/style.py` | Pydantic models that define the shape of API request/response data |
| `app/api/styles.py` | REST endpoints for listing styles and categories |
| `app/api/creations.py` | REST endpoint for generating an AI image |

### Files Modified

| File | What Changed |
|---|---|
| `app/models/user.py` | Added `creations` relationship so SQLAlchemy can link users to their creations |
| `app/core/config.py` | Added AWS S3 and Gemini API key settings |
| `app/main.py` | Registered the three new routers; imported all models so tables are auto-created |
| `config.properties` | Added `[aws]` and `[gemini]` config sections |
| `requirements.txt` | Added `boto3` and `google-generativeai` packages |

---

## 2. Database Models

Three new tables are created automatically when the server starts (`Base.metadata.create_all()`).

### `categories` table
Groups styles into logical sections shown in the UI (e.g. "Trending", "Anime", "Traditional").

| Column | Type | Description |
|---|---|---|
| `id` | Integer PK | Auto-incremented unique ID |
| `name` | String(100) | Display name, e.g. "Trending" |
| `slug` | String(100) | URL-safe identifier, e.g. "trending" — used for filtering |
| `icon` | String(10) | Emoji or icon name shown in the UI |
| `description` | String(200) | Short subtitle for the category |
| `preview_url` | String(500) | S3 URL of the category cover image |
| `display_order` | Integer | Controls sort order in the UI |
| `is_active` | Boolean | Soft toggle to hide/show without deleting |

### `styles` table
Each row is one style card the user sees (e.g. "Ghibli Art", "Red Saree", "Neon Glow").

| Column | Type | Description |
|---|---|---|
| `id` | Integer PK | Auto-incremented unique ID |
| `category_id` | FK → categories | Which category this style belongs to |
| `name` | String(100) | Display name, e.g. "Ghibli Art" |
| `slug` | String(100) | URL-safe identifier, e.g. "ghibli-art" — also used as S3 filename |
| `description` | String(500) | Short description of the style |
| `preview_url` | String(500) | **S3 URL** of the thumbnail image shown on the card |
| `prompt_template` | Text | **The AI prompt** sent to Gemini when this style is selected |
| `negative_prompt` | Text | What Gemini should avoid (optional) |
| `tags` | JSON | List of keywords, e.g. `["anime", "artistic"]` |
| `credits_required` | Integer | Credits deducted per generation (default: 50) |
| `uses_count` | Integer | Auto-incremented on each use; drives popularity |
| `is_trending` | Boolean | Flag for "Hot Right Now" section |
| `is_new` | Boolean | Flag to show "NEW" badge on the card |
| `is_active` | Boolean | Soft toggle to hide/show |
| `display_order` | Integer | Controls sort order |
| `created_at` | DateTime | When the style was added |

### `creations` table
One row per AI generation. Records the full audit trail of every image transformation.

| Column | Type | Description |
|---|---|---|
| `id` | Integer PK | Auto-incremented unique ID |
| `user_id` | FK → users | Who made this creation |
| `style_id` | FK → styles | Which style was applied |
| `original_image_url` | String(500) | S3 URL of the user's uploaded photo |
| `generated_image_url` | String(500) | S3 URL of the AI-transformed result |
| `thumbnail_url` | String(500) | S3 URL of a smaller version (for feeds) |
| `mood` | String(50) | Optional: happy / sad / romantic / dramatic |
| `weather` | String(50) | Optional: sunny / rainy / snowy / night |
| `dress_style` | String(50) | Optional: casual / formal / fantasy |
| `custom_prompt` | String(200) | Optional extra instructions from the user |
| `prompt_used` | Text | **Full final prompt** sent to Gemini (for debugging) |
| `credits_used` | Integer | Credits deducted for this specific generation |
| `processing_time` | Float | Seconds Gemini took to generate |
| `likes_count` | Integer | Social likes received |
| `views_count` | Integer | View count |
| `is_public` | Boolean | Whether it appears in the community feed |
| `is_featured` | Boolean | Admin flag to highlight exceptional results |
| `is_deleted` | Boolean | Soft-delete (row stays in DB for audit) |
| `created_at` | DateTime | When the generation happened |

---

## 3. S3 Bucket Structure

All images are stored in a single S3 bucket. The folder structure separates concerns clearly.

```
magicpic-bucket/
│
├── styles/
│   └── thumbnails/
│       ├── ghibli-art.jpg          ← uploaded by admin service
│       ├── red-saree.jpg
│       ├── ice-look.jpg
│       └── neon-glow.jpg
│           URL pattern: https://<bucket>.s3.<region>.amazonaws.com/styles/thumbnails/<slug>.jpg
│           Stored in: styles.preview_url
│
└── creations/
    ├── originals/
    │   └── <user_id>/
    │       └── <uuid>.jpg          ← user's raw uploaded photo
    │           URL pattern: .../creations/originals/<user_id>/<uuid>.jpg
    │           Stored in: creations.original_image_url
    │
    └── generated/
        └── <user_id>/
            └── <uuid>.jpg          ← AI-transformed result from Gemini
                URL pattern: .../creations/generated/<user_id>/<uuid>.jpg
                Stored in: creations.generated_image_url
```

**Why this structure?**
- `styles/thumbnails/` is managed by the **admin service** only. Frontend reads these URLs from the DB.
- `creations/originals/<user_id>/` keeps each user's uploads isolated.
- `creations/generated/<user_id>/` keeps results isolated and easy to query per user.
- Using `<uuid>` as the filename prevents collisions and makes URLs unguessable.

---

## 4. Services

### `app/core/s3.py` — S3 Upload Service

Three upload functions, one for each folder:

```python
upload_style_thumbnail(file_bytes, slug, content_type)
    → "https://.../styles/thumbnails/ghibli-art.jpg"

upload_creation_original(file_bytes, user_id, content_type)
    → "https://.../creations/originals/42/550e8400-....jpg"

upload_creation_generated(file_bytes, user_id, content_type)
    → "https://.../creations/generated/42/7c9e6679-....jpg"
```

All functions return the full public HTTPS URL which is then saved to the database.

### `app/core/gemini.py` — Gemini AI Service

Two functions:

**`build_final_prompt(prompt_template, mood, weather, dress_style, custom_prompt)`**
Merges the style's base prompt with the user's optional customisations into one final string.

Example output:
```
"Transform this photo into a Studio Ghibli anime illustration with soft watercolor
backgrounds and expressive anime eyes. The mood should feel romantic. The weather/environment
should look rainy. Maintain the subject's facial features and identity. Output only the
transformed image."
```

**`transform_image(image_bytes, image_mime, prompt)`**
Sends the image + prompt to Gemini's `gemini-2.0-flash-preview-image-generation` model and returns `(generated_image_bytes, processing_time_seconds)`.

---

## 5. API Endpoints

### Styles & Categories
- `GET /api/styles` — All active styles (supports filtering)
- `GET /api/styles/trending` — Top 10 trending styles
- `GET /api/categories` — All active categories

### Creations
- `POST /api/creations/generate` — Generate an AI image *(requires auth)*
- `GET /api/creations/mine` — User's generation history *(requires auth)*

*(See `STYLES_AND_CREATIONS_API_REFERENCE.md` for full request/response details)*

---

## 6. Configuration

Add your real credentials to `config.properties`:

```ini
[aws]
aws_access_key_id     = AKIA...
aws_secret_access_key = ...
aws_region            = ap-south-1
aws_s3_bucket         = magicpic-bucket

[gemini]
gemini_api_key = AIza...
```

These can also be set as environment variables (uppercased), which takes priority over the file.

---

## 7. Dependencies Added

```
boto3              — AWS SDK for Python (S3 uploads)
google-generativeai — Official Google Gemini SDK
```

Install with:
```bash
pip install boto3 google-generativeai
```

---

## 8. How Everything Connects

```
Frontend (React Native App)
        │
        │  GET /api/styles/trending
        ▼
   styles.py router
        │  queries DB → styles table (with category join)
        │  returns preview_url (S3 URL of thumbnail)
        ▼
   Frontend renders style cards with images from S3

        │
        │  User picks "Ghibli Art", uploads photo
        │  POST /api/creations/generate
        ▼
   creations.py router
        │
        ├─ 1. Validates image (type, size)
        ├─ 2. Checks user credits ≥ style.credits_required
        ├─ 3. Uploads original photo → S3 (creations/originals/)
        ├─ 4. Builds final prompt (style.prompt_template + user options)
        ├─ 5. Calls Gemini API → returns generated image bytes
        ├─ 6. Uploads result → S3 (creations/generated/)
        ├─ 7. Saves Creation row to DB (both S3 URLs stored)
        ├─ 8. Deducts credits from user, increments style.uses_count
        └─ 9. Returns JSON with both image URLs + credits remaining
```

---

## 9. Next Steps

1. **Fill in credentials** in `config.properties` (AWS keys + Gemini API key)
2. **Install dependencies**: `pip install boto3 google-generativeai`
3. **Restart the server** — new tables are auto-created on startup
4. **Admin service** should insert styles into the `styles` table with their `prompt_template` and upload thumbnails to `styles/thumbnails/<slug>.jpg` in S3
5. **Make S3 bucket public** (or use pre-signed URLs) so the frontend can load thumbnail images directly
6. Consider adding a **thumbnail resize step** after Gemini returns the image (e.g. using `Pillow`) before uploading to S3
