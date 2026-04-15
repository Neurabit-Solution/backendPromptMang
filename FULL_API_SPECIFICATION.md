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

### 1.7 GET /auth/profile/{user_id}
**Functionality**: Returns public information about any user for profile sharing.  
**Usage**: Powers the "Public Profile" view. Returns basic stats and a shareable URL.
- **Auth**: ❌ Public (No token required)
- **Response Success**:
  ```json
  {
    "success": true,
    "data": {
      "user": { "id": 1, "name": "John", "avatar_url": "...", "created_at": "..." },
      "total_likes": 250,
      "creations_count": 45,
      "share_url": "https://magicpic.app/p/1"
    }
  }
  ```

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
  - `user_id`: (Integer, Optional) Filter by a specific user to show their public gallery.
- **Response**: List of `CreationOut` objects sorted by popularity/likes.

### 3.3 GET /creations/liked
**Functionality**: Returns a list of all creations the currently logged-in user has liked.
- **Auth**: ✅ Required
- **Query Params**: `skip`, `limit`.
- **Response**: List of `CreationOut` objects (newest likes first).

### 3.4 GET /creations/mine
**Functionality**: Returns the history of all images generated by the current user.  
**Usage**: Used to populate the "My Gallery" or "History" page. Shows both public and private images owned by the requester.
- **Auth**: ✅ Required
- **Query Params**: `skip`, `limit`.
- **Response**: List of user's own `CreationOut` objects.

### 3.5 POST /creations/{id}/like
**Functionality**: Adds a "like" to a specific creation (once per user).  
**Usage**: Triggered when a user taps the heart icon on a creation card. Returns an error if the user has already liked it — use the unlike endpoint to remove.
- **Auth**: ✅ Required
- **Payload**: None (creation ID in URL path)
- **Response Success**: `{"success": true, "likes_count": 13, "message": "Liked successfully"}`
- **Response (already liked)**: `{"success": false, "likes_count": 13, "message": "You have already liked this creation"}`

### 3.6 DELETE /creations/{id}/like
**Functionality**: Removes the current user's like from a specific creation.  
**Usage**: Triggered when a user taps the heart icon again to unlike. Decrements the like counter and removes the record from the database.
- **Auth**: ✅ Required
- **Payload**: None (creation ID in URL path)
- **Response Success**:
  ```json
  {
    "success": true,
    "message": "Like removed successfully",
    "likes_count": 12,
    "is_liked": false
  }
  ```
- **Response (not previously liked)**: `{"success": false, "likes_count": 12, "is_liked": false, "message": "You have not liked this creation"}`

### 3.7 PATCH /creations/{id}/visibility
**Functionality**: Toggles a creation between Public (seen in feed) and Private (only for owner).  
**Usage**: Used when a user wants to hide an existing image from the community gallery without deleting it.
- **Auth**: ✅ Required
- **Payload (Form-data)**:
  - `is_public`: (Boolean, Required)
- **Response**: `{"success": true, "is_public": false}`

---

## 4. Challenges (`/challenges`)

### 4.1 GET /challenges/current
**Functionality**: Returns details of the overall "active" challenge.  
**Usage**: Used for the primary banner on the home screen. It prioritizes the latest "Mystery Prompt" challenge if multiple are active.
- **Response Success**: 
  ```json
  {
    "id": 5,
    "name": "Ghibli Mastery",
    "description": "Recapture the magic of Studio Ghibli...",
    "target_image_url": "https://...",
    "challenge_type": "mystery",
    "starts_at": "2024-03-24T00:00:00Z",
    "ends_at": "2024-03-24T23:59:59Z",
    "is_active": true
  }
  ```

### 4.2 GET /challenges/collaborative/current
**Functionality**: Specifically returns the active "Collaborative Story" challenge for today.  
**Usage**: Used to drive the multi-day story mode.
- **Response Success**: Same format as `4.1`, but with `challenge_type: "collaborative"`.

### 4.3 GET /challenges/collaborative/story/{group_id}
**Functionality**: Returns the winning images from previous days in a multi-day story sequence.  
**Usage**: Used on the "Story Progress" screen to show the community-built narrative so far.
- **Response**:
  ```json
  [
    { "day": 1, "image_url": "...", "winner_name": "Alice", "likes": 45 },
    { "day": 2, "image_url": "...", "winner_name": "Bob", "likes": 32 }
  ]
  ```

### 4.4 POST /challenges/{id}/submit
**Functionality**: Participates in a challenge by uploading a photo.  
**Usage**: Automatically uses the challenge's hidden prompt to generate an image. Costs 1 credit (prioritizing daily free credits).
- **Payload (Multipart)**:
  - `image`: (File, Required)
- **Response Success**:
  ```json
  {
    "success": true,
    "data": {
      "id": 505,
      "similarity_score": 89.5,
      "generated_image_url": "https://...",
      "message": "Submitted successfully! Match score: 89.5%"
    }
  }
  ```

### 4.5 GET /challenges/{id}/leaderboard
**Functionality**: Returns top submissions ranked by similarity score.  
**Usage**: Powers the challenge rankings page.
- **Response**:
  ```json
  [
    {
      "id": 505,
      "user_name": "AestheticKing",
      "avatar_url": "...",
      "similarity_score": 98.2,
      "generated_image_url": "...",
      "created_at": "..."
    }
  ]
  ```

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

### 6.2 POST /challenges/{id}/set_winner
**Functionality**: Manually designates a specific creation as the winner for a story day.  
**Usage**: Used by admins to finalize the community choice and advance the story to the next day's prompt.
- **Payload (Form-data)**:
  - `creation_id`: (Integer, Required)
- **Response**: `{"success": true, "message": "Winner set successfully"}`

---

## 7. Error Reference
All errors following: `{"success": false, "error": {"code": "...", "message": "..."}}`
- `INSUFFICIENT_CREDITS`: (402) Triggered when a user tries to generate art but has 0 remaining credits. 
- `STYLE_NOT_FOUND`: (404) Means the requested style ID has been disabled or deleted by an admin.
- `INVALID_GOOGLE_TOKEN`: (401) Happens when the Android app provides an expired or forged Firebase ID token.
- `WEAK_PASSWORD`: (400) Password validation failed during signup.


---

## 8. Collections (Playlists) (`/collections`)

Allows users to organize their creations into named "Playlists" or folders.

### 8.1 POST /collections
**Functionality**: Creates a new empty collection.
- **Auth**: ✅ Required
- **Payload (JSON)**:
  - `name`: (String, Required) e.g., "My Anime Vibes"
  - `description`: (String, Optional)
  - `cover_url`: (String, Optional)
- **Response**: `{"id": 1, "name": "...", "user_id": 101}`

### 8.2 GET /collections
**Functionality**: Returns all collections owned by the user.
- **Auth**: ✅ Required
- **Response**: `{"success": true, "data": [{...}], "total": 5}`

### 8.3 GET /collections/{id}
**Functionality**: Returns details of a specific collection including all its creations.
- **Auth**: ✅ Required
- **Response**:
  ```json
  {
    "id": 1,
    "name": "My Anime Vibes",
    "creations": [
        { "id": 101, "generated_image_url": "...", "style": {...} }
    ],
    "creations_count": 1
  }
  ```

### 8.4 POST /collections/{id}/items
**Functionality**: Adds a creation to a collection.
- **Auth**: ✅ Required
- **Payload (JSON)**:
  - `creation_id`: (Integer, Required)
- **Response**: `{"success": true, "message": "Creation added to collection"}`

### 8.5 DELETE /collections/{id}/items/{creation_id}
**Functionality**: Removes a creation from a collection.
- **Response**: `{"success": true, "message": "Creation removed"}`

### 8.6 DELETE /collections/{id}
**Functionality**: Deletes a collection (does not delete the actual images).
- **Response**: `{"success": true, "message": "Collection deleted"}`

---

## 9. Payments (`/payments`)

Handles credit purchases via Razorpay.

### 9.1 GET /payments/pricing
**Functionality**: Returns the current price per credit and package options.
- **Response**: `{"credits": 100, "price_inr": 100.0, "currency": "INR"}`

### 9.2 POST /payments/create-order
**Functionality**: Creates a Razorpay order.
- **Auth**: ✅ Required
- **Payload (JSON)**:
  - `credits`: (Integer, Required) Number of credits to buy.
- **Response**: 
  ```json
  {
    "success": true,
    "order_id": "order_...",
    "amount": 100.0,
    "currency": "INR",
    "key_id": "rzp_test_..."
  }
  ```

### 9.3 POST /payments/verify-payment
**Functionality**: Verifies Razorpay payment signature and adds credits to user account.
- **Auth**: ✅ Required
- **Payload (JSON)**:
  - `razorpay_order_id`: (String, Required)
  - `razorpay_payment_id`: (String, Required)
  - `razorpay_signature`: (String, Required)
- **Response**: `{"success": true, "message": "Successfully added 100 credits", "credits_added": 100, "total_credits": 150}`

### 9.4 GET /payments/history
**Functionality**: Returns the history of successful credit purchases for the current user.
- **Auth**: ✅ Required
- **Response**:
  ```json
  {
    "success": true,
    "history": [
      {
        "id": 1,
        "order_id": "order_Hn4S6K9vL2nZ",
        "payment_id": "pay_Hn4S7L7vM3mY",
        "amount_inr": 100.0,
        "credits_purchased": 100,
        "status": "success",
        "created_at": "2024-04-15T12:00:00Z"
      }
    ]
  }
  ```
