# MagicPic Backend – API Documentation

This document describes all API endpoints for the **MagicPic Backend** so the frontend can integrate with them.

---

## Base URL & Headers

- **Base URL:** Use your backend base URL (e.g. `http://localhost:8000` in development).
- **Content-Type:**  
  - `application/json` for JSON request bodies (auth, etc.).  
  - `multipart/form-data` for image upload (creations generate).
- **Authentication:** For protected routes, send the JWT in the header:
  ```http
  Authorization: Bearer <access_token>
  ```

---

## Common Response Shapes

### Success (typical)

```json
{
  "success": true,
  "data": { ... },
  "message": "..."
}
```

Some list endpoints also include `"total": number`.

### Error (4xx / 5xx)

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message"
  }
}
```

**Common error codes:**  
`INVALID_REQUEST`, `INVALID_EMAIL`, `WEAK_PASSWORD`, `EMAIL_EXISTS`, `INVALID_CREDENTIALS`, `INVALID_IMAGE`, `IMAGE_TOO_LARGE`, `STYLE_NOT_FOUND`, `INSUFFICIENT_CREDITS`, `S3_UPLOAD_ERROR`, `AI_SERVICE_ERROR`, `INTERNAL_SERVER_ERROR`.

---

## 1. Authentication

All auth routes are under `/api/auth`.

### 1.1 Sign up

**`POST /api/auth/signup`**

Creates a new user and returns user + tokens.

**Auth required:** No

**Request body (JSON):**

| Field           | Type   | Required | Notes                          |
|----------------|--------|----------|---------------------------------|
| `email`        | string | Yes      | Valid email                     |
| `password`     | string | Yes      | Min 8 characters                |
| `name`         | string | Yes      | Display name                    |
| `phone`        | string | No       | Optional                        |
| `referral_code`| string | No       | Optional referral code          |

**Success (200):**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "John",
      "phone": null,
      "avatar_url": null,
      "credits": 2500,
      "is_verified": false,
      "referral_code": "ABC12XYZ",
      "created_at": "2025-02-22T12:00:00"
    },
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 1800
  },
  "message": "Account created successfully. Please verify your email."
}
```

**Errors:**

- **409** – `EMAIL_EXISTS`: An account with this email already exists.
- **400** – `INVALID_EMAIL` / `WEAK_PASSWORD` / `INVALID_REQUEST`: Validation failed.

---

### 1.2 Login

**`POST /api/auth/login`**

Authenticates user and returns user + tokens.

**Auth required:** No

**Request body (JSON):**

| Field        | Type   | Required | Notes        |
|-------------|--------|----------|--------------|
| `email`     | string | Yes      | Valid email  |
| `password`  | string | Yes      | Non-empty    |
| `device_info` | object | No     | Optional     |

**Success (200):** Same shape as signup success; `message`: `"Login successful"`.

**Errors:**

- **401** – `INVALID_CREDENTIALS`: Email or password is incorrect.

---

### 1.3 Refresh token

**`POST /api/auth/refresh`**

Returns a new access token using the refresh token.

**Auth required:** Yes – send **refresh token** in `Authorization: Bearer <refresh_token>`.

**Request body:** None (token from header).

**Success (200):**

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Errors:**

- **401** – Invalid or expired refresh token, or user not found.

---

## 2. Styles

Base path: `/api/styles`.

### 2.1 List styles

**`GET /api/styles`**

Returns all active styles (for home screen style grid). Each style includes S3 thumbnail URL and category.

**Auth required:** No

**Query parameters:**

| Parameter     | Type    | Required | Description                    |
|--------------|---------|----------|--------------------------------|
| `category`   | string  | No       | Filter by category **slug**    |
| `category_id`| integer | No       | Filter by category **id** (overrides `category` if both set) |
| `trending`   | boolean | No       | If `true`, only trending styles |
| `search`     | string  | No       | Search by style name (case-insensitive) |

**Success (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Style Name",
      "slug": "style-slug",
      "description": "Optional description",
      "preview_url": "https://...",
      "category": {
        "id": 1,
        "name": "Category Name",
        "slug": "category-slug",
        "icon": null,
        "description": null,
        "preview_url": "https://...",
        "display_order": 0
      },
      "uses_count": 100,
      "is_trending": true,
      "is_new": false,
      "tags": ["tag1", "tag2"],
      "credits_required": 50
    }
  ],
  "total": 1
}
```

---

### 2.2 Trending styles

**`GET /api/styles/trending`**

Returns top trending styles for “Hot Right Now” (max 10, ordered by usage).

**Auth required:** No

**Query parameters:** None

**Success (200):** Same shape as list styles (`data` array + `total`).

---

## 3. Categories

**`GET /api/categories`**

Returns all active categories for filter tabs. Each category includes `styles_count` (active styles in that category).

**Auth required:** No

**Query parameters:** None

**Success (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Category Name",
      "slug": "category-slug",
      "icon": null,
      "description": null,
      "preview_url": "https://...",
      "display_order": 0,
      "styles_count": 5
    }
  ]
}
```

---

## 4. Creations

Base path: `/api/creations`. All creation endpoints require authentication (`Authorization: Bearer <access_token>`).

### 4.1 Generate image

**`POST /api/creations/generate`**

Uploads a photo, applies the selected style via AI, and returns the generated image and creation record.

**Auth required:** Yes

**Content-Type:** `multipart/form-data`

**Form fields:**

| Field           | Type   | Required | Notes                                      |
|----------------|--------|----------|--------------------------------------------|
| `style_id`     | integer| Yes      | ID of the style to apply                    |
| `image`        | file   | Yes      | User photo; JPG, PNG, or WebP; max 10 MB   |
| `mood`         | string | No       | Optional mood                              |
| `weather`      | string | No       | Optional weather                           |
| `dress_style`  | string | No       | Optional dress style                       |
| `custom_prompt`| string | No       | Optional; max 200 chars                    |
| `is_public`    | boolean| No       | Default `true`                             |

**Success (200):**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "original_image_url": "https://...",
    "generated_image_url": "https://...",
    "thumbnail_url": "https://...",
    "style": { /* same StyleOut as in /api/styles */ },
    "mood": null,
    "weather": null,
    "dress_style": null,
    "is_public": true,
    "credits_used": 50,
    "credits_remaining": 2450,
    "processing_time": 3.2,
    "created_at": "2025-02-22T12:00:00"
  },
  "message": "Image generated successfully!"
}
```

**Errors:**

- **400** – `INVALID_IMAGE`: Only JPG, PNG, and WebP supported.
- **413** – `IMAGE_TOO_LARGE`: Image must be under 10 MB.
- **404** – `STYLE_NOT_FOUND`: Style not found.
- **402** – `INSUFFICIENT_CREDITS`: Not enough credits (message includes required vs current).
- **500** – `S3_UPLOAD_ERROR`: Upload failed.
- **503** – `AI_SERVICE_ERROR`: AI generation failed.

---

### 4.2 My creations

**`GET /api/creations/mine`**

Returns the current user’s creation history (newest first).

**Auth required:** Yes

**Query parameters:** None

**Success (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "original_image_url": "https://...",
      "generated_image_url": "https://...",
      "thumbnail_url": "https://...",
      "style": { /* StyleOut */ },
      "mood": null,
      "weather": null,
      "dress_style": null,
      "is_public": true,
      "credits_used": 50,
      "credits_remaining": 2450,
      "processing_time": 3.2,
      "created_at": "2025-02-22T12:00:00"
    }
  ],
  "total": 1
}
```

**Errors:**

- **401** – Invalid or expired access token.

---

## 5. Quick reference

| Method | Path                      | Auth | Description                |
|--------|---------------------------|------|----------------------------|
| POST   | `/api/auth/signup`        | No   | Register new user          |
| POST   | `/api/auth/login`         | No   | Login                      |
| POST   | `/api/auth/refresh`       | Yes (refresh) | Refresh access token |
| GET    | `/api/styles`             | No   | List styles (with filters) |
| GET    | `/api/styles/trending`    | No   | Trending styles            |
| GET    | `/api/categories`         | No   | List categories            |
| POST   | `/api/creations/generate` | Yes  | Generate image (multipart)  |
| GET    | `/api/creations/mine`     | Yes  | User’s creation history    |

---

## 6. Root

**`GET /`**  
Returns: `{"message": "Welcome to MagicPic API"}`.

---

*Generated for MagicPic Backend. For interactive docs, run the server and open `/docs` (Swagger UI) or `/redoc` (ReDoc).*
