# Collaborative Canvas API Guide

This guide covers the backend API endpoints for Challenge #4: **Community "Collaborative Canvas"**.

## Feature Overview
The community builds a visual story together over 7 days. Every day, users submit images based on the current prompt (which was inspired by the previous day's winner). The "Most Liked" image of the day becomes the inspiration for the next day.

## Endpoints

### 1. Get Current Story Challenge
Returns the active challenge for the collaborative story.

**URL:** `/api/challenges/collaborative/current`
**Method:** `GET`
**Auth Required:** Optional

**Response:**
```json
{
  "id": 101,
  "name": "The Great Space Odyssey - Day 2",
  "description": "The community decided our hero reached the moon. Now, where do they go next?",
  "target_image_url": "https://s3.amazonaws.com/magicpic/creations/winner_day1.jpg",
  "challenge_type": "collaborative",
  "day_number": 2,
  "group_id": 7,
  "starts_at": "2024-03-24T00:00:00Z",
  "ends_at": "2024-03-24T23:59:59Z",
  "is_active": true
}
```

### 2. Submit Entry to Collaborative Challenge
Participate in the current story by uploading a photo.

**URL:** `/api/challenges/{challenge_id}/submit`
**Method:** `POST`
**Auth Required:** Yes (Access Token)
**Content-Type:** `multipart/form-data`

**Payload:**
- `image`: File (The user's photo)

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 5002,
    "similarity_score": 85.5,
    "generated_image_url": "https://s3.amazonaws.com/magicpic/creations/gen_5002.jpg",
    "message": "Submitted successfully! Your vision is part of the story."
  }
}
```

### 3. Get Story Evolution (Past Winners)
View the visual story built by the community so far.

**URL:** `/api/challenges/collaborative/story/{group_id}`
**Method:** `GET`
**Auth Required:** Optional

**Response:**
```json
[
  {
    "day": 1,
    "image_url": "https://s3.amazonaws.com/magicpic/creations/winner1.jpg",
    "winner_name": "Alice",
    "likes": 1250
  },
  {
    "day": 2,
    "image_url": "https://s3.amazonaws.com/magicpic/creations/winner2.jpg",
    "winner_name": "Bob",
    "likes": 980
  }
]
```

### 4. Like a Submission
Vote for your favorite vision to become the next day's inspiration.

**URL:** `/api/creations/{creation_id}/like`
**Method:** `POST`
**Auth Required:** Yes (Access Token)

**Response:**
```json
{
  "success": true,
  "message": "Liked successfully",
  "likes_count": 1251
}
```

## Admin: Setting the Winner
To advance the story, an admin (or automated script) selects the winner of the day.

**URL:** `/api/challenges/{challenge_id}/set_winner`
**Method:** `POST`
**Parameters:**
- `creation_id`: The ID of the winning creation.
