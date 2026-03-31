# MagicPic — Full API Specification

This document provides a comprehensive reference for all MagicPic API endpoints, including authentication, content discovery, AI generation, challenges, and administration.

## 🚀 Base URL
- **Local Development**: `http://localhost:8000/api`
- **Production**: `https://your-api-domain.com/api`

## 🔑 Authentication
Most endpoints require a **Bearer Token** in the `Authorization` header:
`Authorization: Bearer <access_token>`

---

## 1. Authentication & User Profile (`/auth`)

Manage user accounts, Google login, and profile updates.

### 1.1 POST /auth/signup
**Functionality**: Registers a new user with an email and password.  
**Usage**: Used when a user first joins the app and doesn't want to use Google Sign-in. It creates their initial credit balance and generates their unique referral code.
- **Payload (JSON)**:
  - `email`: (String, Required) User's unique email.
  - `password`: (String, Required) Minimum length 6 recommended.
  - `name`: (String, Required) Full user name.
  - `phone`: (String, Optional) Phone number.
  - `referral_code`: (String, Optional) Code from a friend.
- **Response Success (201 Created)**:
  ```json
  {
    "success": true,
    "data": {
      "user": { "id": 1, "email": "...", "credits": 2, "referral_code": "AB123", ... },
      "access_token": "eyJhbGci...", 
      "refresh_token": "...",
      "token_type": "bearer",
      "expires_in": 1800
    },
    "message": "Account created successfully."
  }
  ```

### 1.2 POST /auth/login
**Functionality**: Authenticates an existing user and returns fresh access/refresh tokens.  
**Usage**: Used for the standard login screen. It also updates the 'last_login' timestamp to track user activity.
- **Payload (JSON)**:
  - `email`: (String, Required)
  - `password`: (String, Required)
- **Response**: Same format as Signup.

### 1.3 POST /auth/google
**Functionality**: Authenticates a user using their Google/Firebase ID token.  
**Usage**: Used for "One-tap" login on Android. If the user doesn't exist, it automatically signs them up and applies referral rewards if a code was provided.
- **Payload (JSON)**:
  - `id_token`: (String, Required) Verified via Firebase.
  - `platform`: (String, Optional) Should be "android".
  - `referral_code`: (String, Optional)
- **Response**: Same format as Signup.

### 1.4 GET /auth/me
**Functionality**: Returns the profile details of the currently logged-in user.  
**Usage**: Used to update the user's local state, check current credit balance, and retrieve the referral code for the "Settings" or "Profile" page.
- **Auth**: ✅ Required
- **Response**: `{"success": true, "data": {"user": {...}}}`

### 1.5 PUT /auth/profile
**Functionality**: Updates basic user information like name and phone number.  
**Usage**: Used on the "Edit Profile" screen to allow users to change their public-facing details.
- **Payload (JSON)**:
  - `name`, `phone`, `avatar_url`: (all String, Optional)
- **Response**: `{"success": true, "message": "Profile updated successfully"}`

### 1.6 POST /auth/profile/avatar
**Functionality**: Uploads a new profile picture file to the S3 bucket.  
**Usage**: Triggered when a user picks a photo from their gallery to use as their avatar. The server returns the final public S3 URL of the image.
- **Payload (Multipart)**:
  - `file`: (File, Required) The image file.
- **Response**: `{"success": true, "data": {"avatar_url": "https://..."}}`

---

## 2. Styles & Categories

Used for the home screen gallery and filter tabs.

### 2.1 GET /categories
**Functionality**: Returns a list of all active style categories.  
**Usage**: Used to populate the horizontal filter tabs on the home screen (e.g., "Trending", "Anime", "Fusion").
- **Payload**: None (GET)
- **Response**: `{"success": true, "data": [{"id": 1, "name": "Anime", "slug": "anime", "icon": "👺", "styles_count": 12}]}`

### 2.2 GET /styles
**Functionality**: Returns a list of all available AI artistic filters.  
**Usage**: Used to render the main grid of styles that users can click on to start generating art. Supports filtering by category and text search.
- **Query Params**:
  - `category_id`: (Integer, Optional) Filter by specific ID.
  - `category`: (String, Optional) Filter by category slug (e.g. "anime").
  - `trending`: (Boolean, Optional) If true, only shows featured "hot" styles.
  - `search`: (String, Optional) Search term for style name.
- **Response**: `{"success": true, "data": [...], "total": 45}`

---

## 3. Image Generation & Creations (`/creations`)

### 3.1 POST /creations/generate
**Functionality**: Sends a user's photo + style to Gemini for AI transformation.  
**Usage**: The core "Create" action. It handles credit deduction, S3 storage of both images, and optional visual modifiers (mood, weather, etc.).
- **Auth**: ✅ Required
- **Payload (Multipart/Form-data)**:
  - `style_id`: (Integer, Required)
  - `image`: (File, Required) User's photo.
  - `mood`: (String, Optional) e.g. "Romantic", "Happy".
  - `weather`: (String, Optional) e.g. "Rainy", "Sunny".
  - `dress_style`: (String, Optional) e.g. "Casual", "Traditional".
  - `is_public`: (Boolean, Optional) Default: true.
- **Response Success (200 OK)**:
  ```json
  {
    "success": true,
    "data": {
      "id": 202,
      "generated_image_url": "https://...",
      "credits_remaining": 450,
      "likes_count": 0,
      "is_liked": false
    }
  }
  ```

### 3.2 GET /creations/feed
**Functionality**: Returns a paginated list of all public images created by the community.  
**Usage**: Powers the "Discover" or "Community" feed where users can see what others have created and like their work.
- **Auth**: ❌ Optional (Pass token to get `is_liked` flags).
- **Query Params**:
  - `skip`: (Integer, Optional) For pagination.
  - `limit`: (Integer, Optional) Number of items per page. Default: 20.
- **Response**: List of `CreationOut` objects sorted by popularity/likes.

### 3.3 GET /creations/mine
**Functionality**: Returns the history of all images generated by the current user.  
**Usage**: Used to populate the "My Gallery" or "History" page. Shows both public and private images owned by the requester.
- **Auth**: ✅ Required
- **Query Params**: `skip`, `limit`.
- **Response**: List of user's own `CreationOut` objects.

### 3.4 POST /creations/{id}/like
**Functionality**: Adds or removes a "like" from a specific creation.  
**Usage**: Triggered when a user clicks the heart icon on any creation card (Community feed or Detail view).
- **Auth**: ✅ Required
- **Payload**: None (Implicit in URL {id})
- **Response**: `{"success": true, "likes_count": 12, "message": "Liked successfully"}`

### 3.5 PATCH /creations/{id}/visibility
**Functionality**: Toggles a creation between Public (seen in feed) and Private (only for owner).  
**Usage**: Used when a user wants to hide an existing image from the community gallery without deleting it.
- **Auth**: ✅ Required
- **Payload (Form-data)**:
  - `is_public`: (Boolean, Required)
- **Response**: `{"success": true, "is_public": false}`

---

## 4. Challenges (`/challenges`)

### 4.1 GET /challenges/current
**Functionality**: Returns details about the active "Mystery Prompt" or "Collaborative Story".  
**Usage**: Used to show the main challenge banner on the home screen with the target image to match.
- **Response Success**: `{"id": 5, "name": "Ghibli Mastery", "target_image_url": "...", ...}`

### 4.2 POST /challenges/{id}/submit
**Functionality**: Participates in a challenge by uploading a photo and getting an AI score.  
**Usage**: Triggered when a user attempts a challenge. It calculates how similar their transformation is to the goal image.
- **Payload (Multipart)**:
  - `image`: (File, Required) The photo to match.
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "id": 505,
      "similarity_score": 89.5,
      "generated_image_url": "https://...",
      "message": "Submitted! Match score: 89.5%"
    }
  }
  ```

### 4.3 GET /challenges/{id}/leaderboard
**Functionality**: Lists the top participants for a specific challenge ranked by AI score.  
**Usage**: Used on the challenge "Rankings" page to show who matched the aesthetic most accurately.
- **Query Params**: None.
- **Response**: `[{"user_name": "...", "avatar_url": "...", "similarity_score": 98.2, "generated_image_url": "..."}]`

---

## 5. Guest Mode (`/guest`)

### 5.1 POST /guest/generate
**Functionality**: Allows one free AI generation without creating an account.  
**Usage**: Used for the 'Free Trial' CTA for first-time visitors before they even sign up. It uses the device ID to prevent multiple trials.
- **Payload (Form-data)**:
  - `device_id`: (String, Required) Unique identifier for the handset.
  - `style_id`: (Integer, Required)
  - `image`: (File, Required)
- **Response**: Raw Binary Image Data (Content-Type: `image/jpeg`).

---

## 6. Administration (`/admin`)

Requires `is_admin: true` in user record.

### 6.1 POST /admin/styles
**Functionality**: Creates a brand new style with a custom AI prompt.  
**Usage**: Used by admins to add new artistic filters to the app catalog instantly without code changes.
- **Payload (Multipart)**:
  - `category_id`, `name`, `slug`, `prompt_template`, `negative_prompt`, `preview_image` (File).
- **Response**: `{"success": true, "style": {...}}`

---

## 7. Error Reference
All errors following: `{"success": false, "error": {"code": "...", "message": "..."}}`
- `INSUFFICIENT_CREDITS`: (402) Triggered when a user tries to generate art but has 0 remaining credits. 
- `STYLE_NOT_FOUND`: (404) Means the requested style ID has been disabled or deleted by an admin.
- `INVALID_GOOGLE_TOKEN`: (401) Happens when the Android app provides an expired or forged Firebase ID token.
- `WEAK_PASSWORD`: (400) Password validation failed during signup.
