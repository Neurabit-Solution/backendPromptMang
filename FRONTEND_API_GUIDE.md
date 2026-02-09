# MagicPic Admin API - Frontend Integration Guide

This document provides the necessary information for frontend developers to integrate with the MagicPic Admin API.

## 🚀 Getting Started

- **Base URL**: `http://localhost:8000/api/admin`
- **Authentication**: JWT Bearer Token

## 🔑 Authentication

### 1. Login
`POST /auth/login`

**Request Body:**
```json
{
  "email": "admin@magicpic.app",
  "password": "strongpassword"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "admin": {
      "id": 1,
      "email": "admin@magicpic.app",
      "name": "Admin User",
      "role": "super_admin",
      "permissions": ["all"]
    },
    "access_token": "eyJhbG...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

**Header for Authenticated Requests:**
`Authorization: Bearer <access_token>`

---

## 👥 User Management

### 1. List Users
`GET /users`

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 50)
- `search`: Search by name or email
- `is_verified`: Filter by verification status (true/false)
- `is_active`: Filter by active status (true/false)
- `sort_by`: Field to sort by (default: "created_at")
- `sort_order`: "asc" or "desc"

**Response:**
```json
{
  "success": true,
  "data": {
    "users": [...],
    "pagination": {
      "total": 1250,
      "total_pages": 25,
      "page": 1,
      "limit": 50
    }
  }
}
```

### 2. Create User
`POST /users`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "userpass123",
  "name": "John Doe",
  "phone": "+1234567890",
  "credits": 2500,
  "is_verified": true
}
```

---

## 🛠️ Implementation Notes

1. **Error Handling**: All errors follow the structure:
   ```json
   {
     "success": false,
     "error": {
       "code": "ERROR_CODE",
       "message": "Human readable message"
     }
   }
   ```
2. **Date Format**: ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`)
3. **Roles**: `super_admin`, `admin`, `moderator`
4. **Permissions**: Typical permissions include `users.view`, `users.create`, `credits.manage`, `styles.edit`, etc.

## 📡 API Documentation (Swagger)
Once the server is running, you can access the interactive Swagger UI at:
`http://localhost:8000/docs`
