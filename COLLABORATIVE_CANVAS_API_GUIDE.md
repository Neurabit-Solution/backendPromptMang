# Collaborative Canvas Challenge — API Guide

This document describes the API endpoints for the **Collaborative Canvas** feature (Challenge #4). 

In this challenge, the community builds a visual story together over 7 days. Each day, users submit images inspired by the previous day's winner. The most liked image of the day becomes the "Target Image" or inspiration for the next day's prompt.

---

## 1. Get Current Story Challenge
Retrieve the active collaborative challenge (the current "page" of the story).

- **URL**: `/api/challenges/collaborative/current`
- **Method**: `GET`
- **Auth**: None (Public)
- **Response**: Returns the challenge details, including `day_number` (1-7) and the `target_image_url` (the previous winner).

### 1.1 Success Response
Status: `200 OK`
```json
{
  "id": 101,
  "name": "The Great Space Odyssey - Day 2",
  "description": "The community decided our hero reached the moon. Now, where do they go next?",
  "target_image_url": "https://s3.../creations/winner_day1.jpg",
  "challenge_type": "collaborative",
  "day_number": 2,
  "group_id": 7,
  "starts_at": "2026-03-24T00:00:00Z",
  "ends_at": "2026-03-24T23:59:59Z",
  "is_active": true
}
```

---

## 2. Submit Entry to Collaborative Story
Participate in the current day's story by uploading a photo.

- **URL**: `/api/challenges/{challenge_id}/submit`
- **Method**: `POST`
- **Auth**: Required (`Authorization: Bearer <access_token>`)
- **Body**: `multipart/form-data`
  - `image`: The user's photo (File)
- **Logic**: 
  - Deducts **1 credit** from the user.
  - Generates an image using the user's photo and the challenge prompt.
  - Automatically calculates a "Similarity Score" using Gemini (comparing it to the inspiration image).

### 2.1 Success Response
Status: `200 OK`
```json
{
  "success": true,
  "data": {
    "id": 5002,
    "similarity_score": 85.5,
    "generated_image_url": "https://s3.../creations/gen_5002.jpg",
    "message": "Submitted successfully! Your vision is part of the story."
  }
}
```

---

## 3. Get Story Evolution (History)
Retrieve the sequence of winners that form the 7-day story.

- **URL**: `/api/challenges/collaborative/story/{group_id}`
- **Method**: `GET`
- **Auth**: None (Public)
- **Purpose**: Displays the linear story progress to the users.

### 3.1 Success Response
Status: `200 OK`
```json
[
  {
    "day": 1,
    "image_url": "https://s3.../creations/winner1.jpg",
    "winner_name": "Alice",
    "likes": 1250
  },
  {
    "day": 2,
    "image_url": "https://s3.../creations/winner2.jpg",
    "winner_name": "Bob",
    "likes": 980
  }
]
```

---

## 4. Like a Submission
Vote for a specific entry. The entry with the most likes at the end of the day usually becomes the winner for the next step.

- **URL**: `/api/creations/{creation_id}/like`
- **Method**: `POST`
- **Auth**: Required (`Authorization: Bearer <access_token>`)
- **Response**: Returns the updated like count.

### 4.1 Success Response
Status: `200 OK`
```json
{
  "success": true,
  "message": "Liked successfully",
  "likes_count": 1251
}
```

---

## 5. Admin: Set Daily Winner
Manually select the winning creation for a specific day to advance the story.

- **URL**: `/api/challenges/{challenge_id}/set_winner`
- **Method**: `POST`
- **Auth**: Admin Required (currently open for testing)
- **Payload**:
  - `creation_id`: ID of the creation to be set as the winner.

### 5.1 Success Response
Status: `200 OK`
```json
{
  "success": true,
  "message": "Winner set successfully."
}
```

---

## Error Codes
- `404 Not Found`: No active collaborative challenge found.
- `400 Bad Request`: Challenge already expired or invalid ID.
- `402 Payment Required`: Insufficient user credits.
- `401 Unauthorized`: Token missing or expired.
- `503 Service Unavailable`: Gemini AI generation failed.
