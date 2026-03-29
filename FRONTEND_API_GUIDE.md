# MagicPic Frontend API Guide

This document aggregates all necessary API endpoints for the MagicPic frontend, including Authentication, User Profile Management, Styles, and Creations.

---

## 🔒 Authentication Overview

Most endpoints (except for viewing styles and the community feed) require a valid **Bearer Access Token**.

- **Header**: `Authorization: Bearer <your_access_token>`
- **Token Expiry**: Access tokens expire after 30 minutes. Use the refresh token to get a new one.

---

## 1. User Account & Profile

### Login
**Endpoint**: `POST /api/auth/login`  
**Purpose**: Authenticate user and receive tokens.

### Signup
**Endpoint**: `POST /api/auth/signup`  
**Purpose**: Create a new account.

### Update Profile
**Endpoint**: `PUT /api/auth/profile`  
**Auth Required**: ✅ Yes
**Purpose**: Update basic user information like name, phone, and avatar URL manually.

#### Request Payload (JSON)
```json
{
  "name": "Jane Doe",
  "phone": "+919876543210",
  "avatar_url": "https://example.com/manual-avatar.jpg"
}
```

### Upload Profile Avatar
**Endpoint**: `POST /api/auth/profile/avatar`  
**Auth Required**: ✅ Yes
**Purpose**: Upload an image file to S3 and set it as the user's avatar.

#### Request Payload (Multipart/Form-Data)
- **Field Name**: `file`
- **Type**: Image file (JPG, PNG, or WebP)
- **Limit**: Max 5 MB

### Delete Account
**Endpoint**: `DELETE /api/auth/account`  
**Auth Required**: ✅ Yes
**Purpose**: Permanently remove user account and all associated data.

---

## 2. Styles & Discover

### Get All Styles
**Endpoint**: `GET /api/styles`  
**Auth Required**: ❌ No
**Purpose**: Returns all active styles for the home screen grid.

#### Optional Query Parameters
| Parameter | Type | Description |
|---|---|---|
| `category` | string | Filter by category slug |
| `trending` | boolean | Only return trending styles |
| `search` | string | Search styles by name |

### Get Trending Styles
**Endpoint**: `GET /api/styles/trending`  
**Auth Required**: ❌ No
**Purpose**: Returns the top 10 trending styles.

### Get All Categories
**Endpoint**: `GET /api/categories`  
**Auth Required**: ❌ No
**Purpose**: Returns active categories for UI filter tabs.

---

## 3. Creations

### Generate AI Image
**Endpoint**: `POST /api/creations/generate`  
**Auth Required**: ✅ Yes
**Purpose**: Transform user photo using AI.

#### Request Payload (Multipart/Form-Data)
| Field | Type | Required | Description |
|---|---|---|---|
| `image` | File | ✅ Yes | User's photo (JPG/PNG/WebP, Max 10 MB) |
| `style_id` | integer | ✅ Yes | ID of the style |
| `mood` | string | ❌ No | e.g., `happy`, `romantic` |
| `weather` | string | ❌ No | e.g., `sunny`, `rainy` |
| `dress_style` | string | ❌ No | e.g., `casual`, `formal` |
| `custom_prompt`| string | ❌ No | Extra user text (max 200 chars) |
| `is_public` | boolean | ❌ No | Show in feed? Default: `true` |

### My Creations History
**Endpoint**: `GET /api/creations/mine`  
**Auth Required**: ✅ Yes
**Purpose**: Returns the user's personal creation history, newest first.

### Community Feed (Explore)
**Endpoint**: `GET /api/creations/feed`  
**Auth Required**: ❌ No (Optional)
**Purpose**: Returns public creations sorted by **highest like count first**. If a token is provided, `is_liked` will indicate if the user has liked each item.

#### Optional Query Parameters
| Parameter | Type | Description |
|---|---|---|
| `skip` | integer | Pagination (items to skip) |
| `limit` | integer | Pagination (max items) |

#### Response Shape
```json
{
  "success": true,
  "data": [
    {
      "id": 105,
      "original_image_url": "...",
      "generated_image_url": "...",
      "thumbnail_url": "...",
      "user_name": "Rohan Sharma",
      "likes_count": 1250,
      "is_liked": true,
      "created_at": "..."
    }
  ]
}
```

### Like a Creation
**Endpoint**: `POST /api/creations/{id}/like`  
**Auth Required**: ✅ Yes
**Purpose**: Increments the like count. Each user can only like a creation **once**.

#### Response (Success)
```json
{
  "success": true,
  "message": "Liked successfully",
  "likes_count": 1251
}
```

#### Response (Already Liked)
```json
{
  "success": false,
  "message": "You have already liked this creation",
  "likes_count": 1250
}
```

### Get Creation Details
**Endpoint**: `GET /api/creations/{id}`  
**Auth Required**: ❌ No (Optional)
**Purpose**: View a single creation. If it's private, only the owner can see it.

### Toggle Visibility
**Endpoint**: `PATCH /api/creations/{id}/visibility`  
**Auth Required**: ✅ Yes
**Purpose**: Make an existing creation public or private.

#### Request Payload (Multipart/Form-Data)
- **Field Name**: `is_public`
- **Type**: Boolean (`true` or `false`)

---

## 4. Error Reference

| HTTP Status | Error Code | Description |
|---|---|---|
| `401` | — | Token missing or expired |
| `402` | `INSUFFICIENT_CREDITS` | Not enough credits to generate |
| `400` | `INVALID_IMAGE` | Unsupported format |
| `413` | `IMAGE_TOO_LARGE` | File exceeds limit |
| `404` | `STYLE_NOT_FOUND` | Invalid style ID |
| `503` | `AI_SERVICE_ERROR`| Gemini API error |
