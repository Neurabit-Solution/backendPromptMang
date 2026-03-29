# Styles & Creations API Reference

> **Styles and categories** (GET /api/styles, GET /api/styles/trending, GET /api/categories) work **without authentication**.
> **Creations** (POST /api/creations/generate, GET /api/creations/mine) require the user to be **logged in** and the JWT in the header.

---

## Authentication Header (Required only for Creations)

For creation endpoints, include the `access_token` from `/api/auth/login` or `/api/auth/signup`:

```
Authorization: Bearer <access_token>
Content-Type: application/json        (for JSON requests)
Content-Type: multipart/form-data     (for file upload requests)
```

---

## Table of Contents

1. [GET /api/styles](#1-get-apistyles)
2. [GET /api/styles/trending](#2-get-apisylestrending)
3. [GET /api/categories](#3-get-apicategories)
4. [POST /api/creations/generate](#4-post-apicreationsgenerate)
5. [GET /api/creations/mine](#5-get-apicreationsmine)
6. [GET /api/creations/feed](#6-get-apicreationsfeed)
7. [POST /api/creations/{id}/like](#7-post-apicreationsidlike)
8. [GET /api/creations/{id}](#8-get-apicreationsid)
9. [PATCH /api/creations/{id}/visibility](#9-patch-apicreationsidvisibility)
10. [Error Reference](#10-error-reference)

---

## 1. GET /api/styles

Returns all active styles. Used to render the home screen style grid.

**Auth required:** No

### Request

```
GET /api/styles
```

#### Optional Query Parameters

| Parameter | Type | Description | Example |
|---|---|---|---|
| `category` | string | Filter by category slug | `?category=anime` |
| `trending` | boolean | Only return trending styles | `?trending=true` |
| `search` | string | Search styles by name | `?search=ghibli` |

#### Example Requests

```bash
# All styles
GET /api/styles

# Only trending styles
GET /api/styles?trending=true

# Styles in the "traditional" category
GET /api/styles?category=traditional

# Search by name
GET /api/styles?search=neon
```

### Response — 200 OK

```json
{
  "success": true,
  "total": 4,
  "data": [
    {
      "id": 1,
      "name": "Ghibli Art",
      "slug": "ghibli-art",
      "description": "Transform your photo into a dreamy Studio Ghibli anime illustration",
      "preview_url": "https://magicpic-bucket.s3.ap-south-1.amazonaws.com/styles/thumbnails/ghibli-art.jpg",
      "category": {
        "id": 1,
        "name": "Trending",
        "slug": "trending",
        "icon": "🔥",
        "description": "Most popular styles right now",
        "preview_url": "https://magicpic-bucket.s3.ap-south-1.amazonaws.com/styles/thumbnails/trending-cover.jpg",
        "display_order": 1,
        "styles_count": 0
      },
      "uses_count": 15420,
      "is_trending": true,
      "is_new": false,
      "tags": ["anime", "artistic", "colorful"],
      "credits_required": 50
    },
    {
      "id": 2,
      "name": "Red Saree",
      "slug": "red-saree",
      "description": "Dress up in a stunning red traditional saree",
      "preview_url": "https://magicpic-bucket.s3.ap-south-1.amazonaws.com/styles/thumbnails/red-saree.jpg",
      "category": {
        "id": 2,
        "name": "Traditional",
        "slug": "traditional",
        "icon": "🪷",
        "description": "Indian traditional looks",
        "preview_url": null,
        "display_order": 2,
        "styles_count": 0
      },
      "uses_count": 9800,
      "is_trending": true,
      "is_new": false,
      "tags": ["saree", "traditional", "indian"],
      "credits_required": 50
    }
  ]
}
```

---

## 2. GET /api/styles/trending

Returns the top 10 trending styles for the **"Hot Right Now"** section on the home screen. Sorted by `uses_count` descending.

**Auth required:** No

### Request

```
GET /api/styles/trending
```

No query parameters needed.

### Response — 200 OK

Same shape as `GET /api/styles`, but always limited to 10 results and only `is_trending = true` styles.

```json
{
  "success": true,
  "total": 4,
  "data": [
    {
      "id": 1,
      "name": "Ghibli Art",
      "slug": "ghibli-art",
      "description": "Transform your photo into a dreamy Studio Ghibli anime illustration",
      "preview_url": "https://magicpic-bucket.s3.ap-south-1.amazonaws.com/styles/thumbnails/ghibli-art.jpg",
      "category": { ... },
      "uses_count": 15420,
      "is_trending": true,
      "is_new": false,
      "tags": ["anime", "artistic"],
      "credits_required": 50
    },
    {
      "id": 4,
      "name": "Neon Glow",
      "slug": "neon-glow",
      "description": "Cyberpunk neon city vibes",
      "preview_url": "https://magicpic-bucket.s3.ap-south-1.amazonaws.com/styles/thumbnails/neon-glow.jpg",
      "category": { ... },
      "uses_count": 11200,
      "is_trending": true,
      "is_new": true,
      "tags": ["cyberpunk", "neon", "futuristic"],
      "credits_required": 50
    }
  ]
}
```

---

## 3. GET /api/categories

Returns all active categories. Used to render the category filter tabs in the UI.

**Auth required:** No

### Request

```
GET /api/categories
```

No query parameters needed.

### Response — 200 OK

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Trending",
      "slug": "trending",
      "icon": "🔥",
      "description": "Most popular styles right now",
      "preview_url": "https://magicpic-bucket.s3.ap-south-1.amazonaws.com/styles/thumbnails/trending-cover.jpg",
      "display_order": 1,
      "styles_count": 6
    },
    {
      "id": 2,
      "name": "Traditional",
      "slug": "traditional",
      "icon": "🪷",
      "description": "Indian traditional looks",
      "preview_url": null,
      "display_order": 2,
      "styles_count": 4
    },
    {
      "id": 3,
      "name": "Fantasy",
      "slug": "fantasy",
      "icon": "✨",
      "description": "Magical and otherworldly styles",
      "preview_url": null,
      "display_order": 3,
      "styles_count": 3
    }
  ]
}
```

---

## 4. POST /api/creations/generate

**The core feature.** User selects a style, uploads their photo, and the backend:
1. Validates the image
2. Checks the user has enough credits
3. Uploads the original photo to S3
4. Builds the final AI prompt (style template + user options)
5. Sends image + prompt to Google Gemini
6. Uploads the AI-generated result to S3
7. Saves the creation record to the database
8. Deducts credits from the user

### Request

```
POST /api/creations/generate
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

#### Form Fields (multipart/form-data)

| Field | Type | Required | Description |
|---|---|---|---|
| `image` | File | ✅ Yes | User's photo. Accepted: JPG, PNG, WebP. Max size: 10 MB |
| `style_id` | integer | ✅ Yes | ID of the style to apply (from `/api/styles`) |
| `mood` | string | ❌ No | Emotional tone: `happy`, `sad`, `romantic`, `dramatic`, `peaceful` |
| `weather` | string | ❌ No | Environment feel: `sunny`, `rainy`, `snowy`, `cloudy`, `night` |
| `dress_style` | string | ❌ No | Clothing preference: `casual`, `formal`, `traditional`, `fantasy` |
| `custom_prompt` | string | ❌ No | Extra instruction from user (max 200 characters) |
| `is_public` | boolean | ❌ No | Whether to show in community feed. Default: `true` |

#### Example cURL

```bash
curl -X POST https://api.magicpic.app/api/creations/generate \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -F "image=@/path/to/my-photo.jpg" \
  -F "style_id=1" \
  -F "mood=romantic" \
  -F "weather=rainy" \
  -F "is_public=true"
```

#### Example with custom prompt

```bash
curl -X POST https://api.magicpic.app/api/creations/generate \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -F "image=@/path/to/my-photo.jpg" \
  -F "style_id=2" \
  -F "dress_style=traditional" \
  -F "custom_prompt=Add golden jewelry and flower garland"
```

### Response — 200 OK (Success)

```json
{
  "success": true,
  "message": "Image generated successfully!",
  "data": {
    "id": 101,
    "original_image_url": "https://magicpic-bucket.s3.ap-south-1.amazonaws.com/creations/originals/42/550e8400-e29b-41d4-a716-446655440000.jpg",
    "generated_image_url": "https://magicpic-bucket.s3.ap-south-1.amazonaws.com/creations/generated/42/7c9e6679-7425-40de-944b-e07fc1f90ae7.jpg",
    "thumbnail_url": "https://magicpic-bucket.s3.ap-south-1.amazonaws.com/creations/generated/42/7c9e6679-7425-40de-944b-e07fc1f90ae7.jpg",
    "style": {
      "id": 1,
      "name": "Ghibli Art",
      "slug": "ghibli-art",
      "description": "Transform your photo into a dreamy Studio Ghibli anime illustration",
      "preview_url": "https://magicpic-bucket.s3.ap-south-1.amazonaws.com/styles/thumbnails/ghibli-art.jpg",
      "category": {
        "id": 1,
        "name": "Trending",
        "slug": "trending",
        "icon": "🔥",
        "description": "Most popular styles right now",
        "preview_url": null,
        "display_order": 1,
        "styles_count": 0
      },
      "uses_count": 15421,
      "is_trending": true,
      "is_new": false,
      "tags": ["anime", "artistic", "colorful"],
      "credits_required": 50
    },
    "mood": "romantic",
    "weather": "rainy",
    "dress_style": null,
    "user_name": "Jane Doe",
    "likes_count": 0,
    "is_liked": false,
    "is_public": true,
    "credits_used": 50,
    "credits_remaining": 2450,
    "processing_time": 14.32,
    "created_at": "2026-02-18T06:29:40.000Z"
  }
}
```

### Response — Error Cases

#### 402 — Not Enough Credits

```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_CREDITS",
    "message": "You need 50 credits. You have 30."
  }
}
```

#### 400 — Invalid Image Format

```json
{
  "success": false,
  "error": {
    "code": "INVALID_IMAGE",
    "message": "Only JPG, PNG, and WebP images are supported."
  }
}
```

#### 413 — Image Too Large

```json
{
  "success": false,
  "error": {
    "code": "IMAGE_TOO_LARGE",
    "message": "Image must be under 10 MB."
  }
}
```

#### 404 — Style Not Found

```json
{
  "success": false,
  "error": {
    "code": "STYLE_NOT_FOUND",
    "message": "Style not found."
  }
}
```

#### 503 — Gemini AI Failed

```json
{
  "success": false,
  "error": {
    "code": "AI_SERVICE_ERROR",
    "message": "AI generation failed: <reason>"
  }
}
```

#### 401 — Not Logged In / Token Expired

```json
{
  "detail": "Invalid or expired token"
}
```

---

## 5. GET /api/creations/mine

Returns the current user's full creation history, newest first. Includes both original and generated image URLs.

### Request

```
GET /api/creations/mine
Authorization: Bearer <access_token>
```

No query parameters needed.

### Response — 200 OK

```json
{
  "success": true,
  "total": 2,
  "data": [
    {
      "id": 101,
      "original_image_url": "https://magicpic-bucket.s3.ap-south-1.amazonaws.com/creations/originals/42/550e8400-....jpg",
      "generated_image_url": "https://magicpic-bucket.s3.ap-south-1.amazonaws.com/creations/generated/42/7c9e6679-....jpg",
      "thumbnail_url": "https://magicpic-bucket.s3.ap-south-1.amazonaws.com/creations/generated/42/7c9e6679-....jpg",
      "style": {
        "id": 1,
        "name": "Ghibli Art",
        "slug": "ghibli-art",
        "description": "Transform your photo into a dreamy Studio Ghibli anime illustration",
        "preview_url": "https://magicpic-bucket.s3.ap-south-1.amazonaws.com/styles/thumbnails/ghibli-art.jpg",
        "category": { ... },
        "uses_count": 15421,
        "is_trending": true,
        "is_new": false,
        "tags": ["anime", "artistic"],
        "credits_required": 50
      },
      "mood": "romantic",
      "weather": "rainy",
      "dress_style": null,
      "user_name": "Jane Doe",
      "likes_count": 12,
      "is_liked": true,
      "is_public": true,
      "credits_used": 50,
      "credits_remaining": 2450,
      "processing_time": 14.32,
      "created_at": "2026-02-18T06:29:40.000Z"
    },
    {
      "id": 98,
      "original_image_url": "https://magicpic-bucket.s3.ap-south-1.amazonaws.com/creations/originals/42/aabbcc-....jpg",
      "generated_image_url": "https://magicpic-bucket.s3.ap-south-1.amazonaws.com/creations/generated/42/ddeeff-....jpg",
      "thumbnail_url": "https://magicpic-bucket.s3.ap-south-1.amazonaws.com/creations/generated/42/ddeeff-....jpg",
      "style": {
        "id": 2,
        "name": "Red Saree",
        "slug": "red-saree",
        ...
      },
      "mood": null,
      "weather": null,
      "dress_style": "traditional",
      "user_name": "Jane Doe",
      "likes_count": 5,
      "is_liked": false,
      "is_public": false,
      "credits_used": 50,
      "credits_remaining": 2500,
      "processing_time": 11.05,
      "created_at": "2026-02-17T14:10:22.000Z"
    }
  ]
}
```

---

## 6. GET /api/creations/feed

Returns public creations from all users, sorted by the highest like count first. Used to render the "Explore" or "Community" section.

**Auth required:** Optional (Include token to receive `is_liked` status for each item).

### Request

```
GET /api/creations/feed
Authorization: Bearer <access_token> (Optional)
```

#### Optional Query Parameters

| Parameter | Type | Description | Example |
|---|---|---|---|
| `skip` | integer | Number of items to skip (pagination) | `?skip=20` |
| `limit` | integer | Max number of items to return | `?limit=50` |

### Response — 200 OK

```json
{
  "success": true,
  "total": 20,
  "data": [
    {
      "id": 105,
      "original_image_url": "...",
      "generated_image_url": "...",
      "thumbnail_url": "...",
      "style": { ... },
      "user_name": "Rohan Sharma",
      "likes_count": 1250,
      "is_liked": true,
      "mood": "happy",
      "is_public": true,
      "created_at": "2026-03-15T10:00:00.000Z"
    },
    {
      "id": 120,
      "original_image_url": "...",
      "generated_image_url": "...",
      "thumbnail_url": "...",
      "style": { ... },
      "user_name": "Anonymous",
      "likes_count": 980,
      "is_liked": false,
      "mood": "dramatic",
      "is_public": true,
      "created_at": "2026-03-14T12:30:00.000Z"
    }
  ]
}
```

---

## 7. POST /api/creations/{id}/like

Increments the like count for a specific creation.

**Auth required:** Yes (User must be logged in to like)

### Request

```
POST /api/creations/105/like
Authorization: Bearer <access_token>
```

### Response — 200 OK

```json
{
  "success": true,
  "message": "Liked successfully",
  "likes_count": 1251
}
```

---

## 8. GET /api/creations/{id}

Returns details of a single creation. Includes privacy protection.

**Auth required:** Optional (Owner can see private creations, others cannot).

### Request

```
GET /api/creations/105
Authorization: Bearer <access_token> (Optional)
```

### Response Success — 200 OK

Returns a standard `CreationOut` object.

### Response Error — 403 Forbidden

```json
{
  "detail": "This creation is private"
}
```

---

## 9. PATCH /api/creations/{id}/visibility

Update whether a creation is public or private.

**Auth required:** Yes (User must own the creation).

### Request

```
PATCH /api/creations/105/visibility
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

#### Form Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `is_public` | boolean | ✅ | `true` for public, `false` for private |

### Response Success — 200 OK

```json
{
  "success": true,
  "message": "Creation visibility updated to private",
  "is_public": false
}
```

---

## 10. Error Reference

### Common Error Codes

| HTTP Status | Error Code | When It Happens |
|---|---|---|
| `401` | — | Token missing, expired, or invalid |
| `402` | `INSUFFICIENT_CREDITS` | User doesn't have enough credits |
| `400` | `INVALID_IMAGE` | Image format not JPG/PNG/WebP |
| `413` | `IMAGE_TOO_LARGE` | Image exceeds 10 MB |
| `404` | `STYLE_NOT_FOUND` | `style_id` doesn't exist or is inactive |
| `503` | `AI_SERVICE_ERROR` | Gemini API call failed |

### Token Expiry

Access tokens expire after **30 minutes**. When you get a `401`, call `/api/auth/refresh` with the refresh token to get a new access token without re-logging in.

```
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

## Quick Reference — All Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/styles` | ❌ | All styles (filterable) |
| `GET` | `/api/styles/trending` | ❌ | Top 10 trending styles |
| `GET` | `/api/categories` | ❌ | All categories |
| `POST` | `/api/creations/generate` | ✅ | Generate AI image |
| `GET` | `/api/creations/mine` | ✅ | My creation history |
| `GET` | `/api/creations/feed` | ❌ (Optional) | Community Feed (sorted by likes) |
| `GET` | `/api/creations/{id}` | ❌ (Optional) | Single creation view (Owner/Public) |
| `PATCH` | `/api/creations/{id}/visibility` | ✅ | Change public/private toggle |
| `POST` | `/api/creations/{id}/like` | ✅ | Like a creation |
| `POST` | `/api/auth/login` | ❌ | Login |
| `POST` | `/api/auth/signup` | ❌ | Register |
| `POST` | `/api/auth/refresh` | ✅ (refresh token) | Refresh access token |
