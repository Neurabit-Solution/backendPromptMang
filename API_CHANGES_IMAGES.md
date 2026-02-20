# API Changes & Image Handling Guide

## 🚨 Critical Update: Image Handling
The backend now serves all images (styles, categories, user creations) through a **proxy endpoint**. 
**Do NOT access S3 URLs directly.** All API responses that previously contained raw S3 links now return backend proxy paths.

### 1. New Image Endpoint
There is a new public endpoint to fetch images:
`GET /api/images/{s3_key_path}`

- **Usage**: The frontend acts as if the backend is the image server.
- **Example**: 
  - Backend URL: `http://localhost:8000`
  - Image Path from API: `/api/images/styles/thumbnails/oil-painting.png`
  - **Final Src**: `http://localhost:8000/api/images/styles/thumbnails/oil-painting.png`

---

## 2. Updated API Responses

### A. Styles API (`GET /api/styles`, `GET /api/styles/trending`)
The `preview_url` field is no longer a full https://s3... URL. It is now a relative path.

**Old Response:**
```json
{
  "preview_url": "https://bucket.s3.amazonaws.com/styles/thumbnails/art.jpg"
}
```

**New Response:**
```json
{
  "preview_url": "/api/images/styles/thumbnails/art.jpg"
}
```

### B. Categories API (`GET /api/categories`)
Same change for category icons/covers.

**New Response:**
```json
{
  "preview_url": "/api/images/categories/thumbnails/anime.jpg"
}
```

### C. Creations API (`GET /api/creations/mine`, `POST /api/creations/generate`)
All image fields (`original_image_url`, `generated_image_url`, `thumbnail_url`) are now relative proxy paths.

**New Response:**
```json
{
  "original_image_url": "/api/images/creations/originals/1/abc.jpg",
  "generated_image_url": "/api/images/creations/generated/1/xyz.jpg",
  "thumbnail_url": "/api/images/creations/generated/1/xyz.jpg"
}
```

---

## 3. Frontend Implementation Guide (React/JS)

You need a helper function to resolve these paths to full URLs.

```javascript
// utils/image.js
const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export const getImageUrl = (path) => {
  if (!path) return "/placeholder.png";
  
  // If it's already a full URL (external image), return as is
  if (path.startsWith("http")) return path;
  
  // Otherwise, prepend backend base URL
  return `${API_BASE_URL}${path}`;
};
```

**Component Usage:**

```jsx
import { getImageUrl } from '../utils/image';

function StyleCard({ style }) {
  return (
    <div className="card">
      <img 
        src={getImageUrl(style.preview_url)} 
        alt={style.name} 
      />
      <h3>{style.name}</h3>
    </div>
  );
}
```

---

## 4. Why This Changed?
- **Security**: The S3 bucket is now fully private. No public access is allowed.
- **Authentication**: The backend uses its credentials to fetch images securely.
- **Simplicity**: The frontend doesn't need to worry about S3 signatures or presigned URLs expiring.
