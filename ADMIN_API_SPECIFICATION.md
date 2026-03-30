# MagicPic — Admin API Specification

This document outlines the proposed Admin endpoints for managing categories, styles, and users. These endpoints require a higher level of authorization (e.g., an `is_admin` flag on the `User` model) and handle critical data mutations.

---

## 🔒 Security Requirements (Recommendations)

1. **Schema Update**: Add an `is_admin` boolean column to the `users` table (default: `false`).
2. **Middleware**: A `get_current_admin` dependency that verifies the JWT *and* checks if `user.is_admin == True`.
3. **Audit Logging**: Admin actions should ideally be logged to a separate `admin_logs` table for traceability.

---

## 1. Category Management

Allows administrators to organize styles into visual buckets.

### GET /api/admin/categories
Returns all categories, including inactive ones.
- **Auth**: Admin JWT

### POST /api/admin/categories
Create a new category.
- **Method**: `POST`
- **Body**: `multipart/form-data`
  - `name`: (string) "Artistic"
  - `slug`: (string) "artistic"
  - `icon`: (string) "🎨"
  - `description`: (string) "Creative AI styles"
  - `display_order`: (integer) 1
  - `cover_image`: (file) Optional. Uploaded to S3 `styles/thumbnails/cover_<slug>.jpg`

### PUT /api/admin/categories/{id}
Update an existing category.
- **Method**: `PUT`
- **Body**: `multipart/form-data` (Supports partial updates)

### DELETE /api/admin/categories/{id}
Soft-delete or fully remove a category.
- **Note**: Deleting a category should ideally cascade to making associated styles `is_active=false`.

---

## 2. Style Management

The core of the app. Admins can update the prompt templates that Gemini uses.

### POST /api/admin/styles
Add a new AI style card.
- **Method**: `POST`
- **Body**: `multipart/form-data`
  - `category_id`: (integer) FK to categories
  - `name`: (string) "Pencil Sketch"
  - `slug`: (string) "pencil-sketch"
  - `description`: (string) "Detailed hand-drawn look"
  - `prompt_template`: (text) The actual AI instruction.
  - `negative_prompt`: (text) Optional.
  - `preview_image`: (file) **Required**. S3: `styles/thumbnails/<slug>.jpg`
  - `credits_required`: (integer) Default: 50
  - `tags`: (JSON string) `["sketch", "black-white"]`

### PUT /api/admin/styles/{id}
Update a style. Useful for "tuning" the prompt template for better results.
- **Method**: `PUT`
- **Fields**: Supports updating `prompt_template`, `is_trending`, `is_new`, etc.

### DELETE /api/admin/styles/{id}
Set `is_active=false` to hide the style from the user grid without breaking past creations.

---

## 3. User Management & Moderation

### GET /api/admin/users
List all users with search (by email) and stats.
- **Purpose**: Monitor user growth and credit balances.

### DELETE /api/admin/users/{id}
Permanently delete a user account.
- **Cascading Policy**:
  - Delete all `creations` from DB.
  - (Optional) Clean up user's S3 folders: `creations/originals/<id>/` and `creations/generated/<id>/`.
  - Delete `credit_transactions` and `likes` associated with this user.
  - Ensure the `email` can be reused if they sign up again.

### POST /api/admin/users/{id}/credits
Grant or revoke credits manually.
- **Body**: `{"amount": 1000, "reason": "Compensation for AI failure"}`

---

## 4. Engagement Management (Battles & Challenges)

### POST /api/admin/challenges
Create a new daily/weekly challenge.
- **Fields**: `name`, `description`, `target_image` (S3), `prompt_template`, `starts_at`, `ends_at`, `challenge_type`.
- **Logic**: Automatically expires the old active challenge of the same type.

### GET /api/admin/challenges/{id}/leaderboard
View all entries, not just top 20.
- **Admin Feature**: Select a winner manually if AI scoring isn't sufficient.

### POST /api/admin/battles
Create a "Style Battle" between two specific creations or random high-quality items.
- **Body**: `{"creation_a_id": 123, "creation_b_id": 456, "duration_hours": 24}`

---

## 5. Content Moderation

### PATCH /api/admin/creations/{id}/featured
Mark a public creation as "Featured" to show it at the top of the feed.

### DELETE /api/admin/creations/{id}
Remove any public creation that violates safety guidelines. Sets `is_deleted=true`.

---

## Database Design Notes for Implementation

- **Table: `styles`**: Keep `uses_count` as read-only for admins (only system increments).
- **S3 Strategy**: Admin uploads for `styles/preview_url` should be optimized/resized to small JPGs before storage to reduce frontend load time.
- **Referrals**: Admins should be able to see the referral chain in the User List.
