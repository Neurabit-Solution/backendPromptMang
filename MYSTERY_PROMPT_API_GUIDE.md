# Mystery Prompt Challenge — API Guide

This document describes the endpoints for the **Mystery Prompt Challenge** feature.

---

## 1. Get Current Active Challenge
Retrieve the currently ongoing challenge that users should participate in.

- **URL**: `/api/challenges/current`
- **Method**: `GET`
- **Auth**: None (Public)
- **Purpose**: Get challenge details including the target image and timeframe.

### 1.1 Success Response
Status: `200 OK`

```json
{
  "id": 1,
  "name": "Studio Ghibli Mastery",
  "description": "Can you match the whimsical aesthetic of Hayao Miyazaki?",
  "target_image_url": "https://s3.../styles/ghibli_reference.jpg",
  "starts_at": "2026-03-20T14:48:15Z",
  "ends_at": "2026-03-27T14:48:15Z",
  "is_active": true,
  "created_at": "2026-03-20T14:48:15Z"
}
```

---

## 2. Submit Challenge Entry
Upload a photo to participate in a specific challenge and get an AI similarity score.

- **URL**: `/api/challenges/{challenge_id}/submit`
- **Method**: `POST`
- **Auth**: Required (`Authorization: Bearer <access_token>`)
- **Body**: `multipart/form-data`
  - `image`: The user's portrait photo (File)

### 2.1 Behavior
1. Deducts **1 credit** from user (daily credits used first).
2. Transforms the user's photo using the **hidden prompt template** of the challenge.
3. Uses Gemini vision and AI to compare the result with the **Target Image**.
4. Returns a **Similarity Score** (0-100%).

### 2.2 Success Response
Status: `200 OK`

```json
{
  "success": true,
  "data": {
    "id": 152,
    "similarity_score": 88.5,
    "generated_image_url": "https://s3.../creations/generated/output.jpg",
    "message": "Submitted successfully! Match score: 88.5%"
  }
}
```

---

## 3. Challenge Leaderboard
See the top-ranking submissions for a specific challenge.

- **URL**: `/api/challenges/{challenge_id}/leaderboard`
- **Method**: `GET`
- **Auth**: None (Public)
- **Purpose**: Show users with the highest similarity scores.

### 3.1 Success Response
Status: `200 OK`

```json
[
  {
    "id": 152,
    "user_name": "Mritunjay Pandey",
    "avatar_url": "https://.../avatar.png",
    "similarity_score": 88.5,
    "generated_image_url": "https://s3.../creations/generated/output.jpg",
    "created_at": "2026-03-23T12:00:00Z"
  },
  {
    "id": 149,
    "user_name": "Subham Agrawal",
    "avatar_url": null,
    "similarity_score": 82.1,
    "generated_image_url": "https://s3.../creations/generated/other.jpg",
    "created_at": "2026-03-23T11:30:00Z"
  }
]
```

---

## Error Codes
- `404 Not Found`: No active challenge exists or invalid challenge ID.
- `400 Bad Request`: Submission attempted after challenge `ends_at`.
- `402 Payment Required`: User has 0 credits.
- `401 Unauthorized`: Missing or invalid token.
- `503 Service Unavailable`: AI transformation or similarity scoring failed.
