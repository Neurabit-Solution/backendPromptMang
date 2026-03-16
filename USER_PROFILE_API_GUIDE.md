# User Profile & Account Management API Guide

This document provides details for the newly implemented User Profile management and Account Deletion APIs.

---

## 🔒 Authentication
All endpoints below require a valid **Bearer Access Token**.
- **Header**: `Authorization: Bearer <your_access_token>`

---

## 1. Update Profile (Text Data)
**Endpoint**: `PUT /api/auth/profile`  
**Purpose**: Update basic user information like name and phone number.

### Request Payload (JSON)
All fields are optional; only provide what you want to change.
```json
{
  "name": "Jane Doe",
  "phone": "+919876543210",
  "avatar_url": "https://example.com/manual-avatar.jpg"
}
```

### Response (Success)
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 123,
      "email": "user@example.com",
      "name": "Jane Doe",
      "phone": "+919876543210",
      "avatar_url": "https://example.com/manual-avatar.jpg",
      "credits": 2500,
      "is_verified": true,
      ...
    }
  },
  "message": "Profile updated successfully"
}
```

---

## 2. Upload Profile Avatar (Image File)
**Endpoint**: `POST /api/auth/profile/avatar`  
**Purpose**: Upload an image file to S3 and set it as the user's avatar.

### Request Payload (Multipart/Form-Data)
- **Field Name**: `file`
- **Type**: Image file (JPG, PNG, or WebP)
- **Limit**: Max 5 MB

### Response (Success)
```json
{
  "success": true,
  "data": {
    "avatar_url": "https://magicpic-bucket.s3.region.amazonaws.com/users/avatars/123/avatar.jpg"
  },
  "message": "Avatar uploaded successfully"
}
```

---

## 3. Delete Account
**Endpoint**: `DELETE /api/auth/account`  
**Purpose**: Permanently remove user account and all associated data.

### Request Payload
- No body required.

### Response (Success)
```json
{
  "success": true,
  "message": "Account and all associated data have been permanently deleted."
}
```

### ⚠️ Important Notes on Deletion:
- **Files**: All original and generated images stored in S3 are deleted.
- **Database**: All creations, likes, votes, and credit history are removed via cascading delete.
- **Irreversible**: This action cannot be undone.
