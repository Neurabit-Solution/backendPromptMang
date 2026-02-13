# MagicPic Admin API - Comprehensive Documentation

> **Complete API Reference for MagicPic Admin Panel**  
> This document provides detailed information about all available APIs, their requirements, and expected responses.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
   - [Root Endpoint](#root-endpoint)
   - [Authentication APIs](#authentication-apis)
   - [User Management APIs](#user-management-apis)
4. [Error Handling](#error-handling)
5. [Data Models](#data-models)
6. [Implementation Examples](#implementation-examples)

---

## Overview

**Base URL**: `http://localhost:8000`  
**API Prefix**: `/api/admin`  
**Authentication**: JWT Bearer Token  
**Content-Type**: `application/json`

### Available Roles
- `super_admin`: Full access to all features
- `admin`: Standard admin access with most permissions
- `moderator`: Limited access for content moderation

### Permission System
The API uses a granular permission system. Common permissions include:
- `users.view`, `users.create`, `users.edit`, `users.delete`
- `credits.manage`, `styles.manage`
- `analytics.view`, `system.settings`

---

## Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <access_token>
```

The token is obtained through the login or register endpoints and expires after 30 minutes (configurable).

---

## API Endpoints

### Root Endpoint

#### GET /

**Description**: Health check and welcome message

**Authentication**: None required

**Headers**: None required

**Response**:
```json
{
  "message": "Welcome to MagicPic Admin API",
  "version": "1.0.0"
}
```

---

### Authentication APIs

#### POST /api/admin/auth/login

**Description**: Authenticate admin user and receive access token

**Authentication**: None required

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "admin@example.com",
  "password": "your_password"
}
```

**Request Body Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string (email) | Yes | Valid email address |
| password | string | Yes | Plain text password |

**Success Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "admin": {
      "id": 1,
      "user_id": 2,
      "email": "admin@example.com",
      "name": "Admin Name",
      "avatar_url": null,
      "role": "admin",
      "permissions": [
        "users.view",
        "users.create",
        "credits.manage",
        "styles.manage"
      ],
      "created_at": "2024-03-20T10:00:00Z",
      "last_login": null
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

**Error Responses (200 OK with success: false)**:

*Invalid Credentials*:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password"
  }
}
```

*Not Admin*:
```json
{
  "success": false,
  "error": {
    "code": "NOT_ADMIN",
    "message": "You do not have admin privileges"
  }
}
```

*Admin Inactive*:
```json
{
  "success": false,
  "error": {
    "code": "ADMIN_INACTIVE",
    "message": "Admin account is deactivated"
  }
}
```

---

#### POST /api/admin/auth/register

**Description**: Register a new admin user

**Authentication**: None required

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "newadmin@example.com",
  "password": "securePassword123",
  "name": "New Admin",
  "role": "admin"
}
```

**Request Body Schema**:
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| email | string (email) | Yes | - | Valid email address |
| password | string | Yes | - | Plain text password |
| name | string | Yes | - | Display name |
| role | string | No | "admin" | Role: "admin" or "super_admin" |

**Success Response (200 OK)**:
Same structure as login response with the newly created admin data.

**Error Responses (200 OK with success: false)**:

*Email Already Exists*:
```json
{
  "success": false,
  "error": {
    "code": "EMAIL_EXISTS",
    "message": "Email already registered"
  }
}
```

---

### User Management APIs

#### GET /api/admin/users

**Description**: Retrieve paginated list of users with filtering and search capabilities

**Authentication**: Required - JWT Bearer Token

**Required Permission**: `users.view` (or `super_admin` role)

**Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page | integer | No | 1 | Page number (1-based) |
| limit | integer | No | 50 | Items per page |
| search | string | No | - | Search in name and email (case-insensitive) |
| is_verified | boolean | No | - | Filter by verification status |
| is_active | boolean | No | - | Filter by active status |
| sort_by | string | No | "created_at" | Field to sort by |
| sort_order | string | No | "desc" | Sort order: "asc" or "desc" |

**Example Request**:
```
GET /api/admin/users?page=1&limit=10&search=john&is_active=true&sort_by=created_at&sort_order=desc
```

**Success Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": 1,
        "email": "user@example.com",
        "name": "John Doe",
        "phone": "+1234567890",
        "credits": 2500,
        "is_verified": true,
        "is_active": true,
        "created_at": "2024-03-20T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 100,
      "total_pages": 10,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

**Error Responses**:

*Unauthorized (403)*:
```json
{
  "detail": "Could not validate credentials"
}
```

*Insufficient Permissions (403)*:
```json
{
  "detail": "Not enough permissions"
}
```

*Admin Not Found (404)*:
```json
{
  "detail": "Admin not found"
}
```

*Inactive Admin (400)*:
```json
{
  "detail": "Inactive admin"
}
```

---

#### POST /api/admin/users

**Description**: Create a new user account

**Authentication**: Required - JWT Bearer Token

**Required Permission**: `users.create` (or `super_admin` role)

**Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "newuser@example.com",
  "password": "userPassword123",
  "name": "New User",
  "phone": "+1234567890",
  "credits": 2500,
  "is_verified": true,
  "is_active": true
}
```

**Request Body Schema**:
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| email | string (email) | Yes | - | Valid email address |
| password | string | Yes | - | Plain text password |
| name | string | Yes | - | Display name |
| phone | string | No | null | Phone number |
| credits | integer | No | 2500 | Initial credit balance |
| is_verified | boolean | No | true | Email verification status |
| is_active | boolean | No | true | Account active status |

**Success Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 5,
      "email": "newuser@example.com",
      "name": "New User",
      "phone": "+1234567890",
      "credits": 2500,
      "is_verified": true,
      "is_active": true,
      "created_at": "2024-03-20T12:00:00Z"
    }
  },
  "message": "User created successfully"
}
```

**Error Responses**:

*Email Already Exists (400)*:
```json
{
  "detail": "The user with this email already exists"
}
```

*Validation Error (422)*:
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "email"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

---

## Error Handling

### Standard Error Response Format

Most application-level errors follow this format:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message"
  }
}
```

### HTTP Status Codes

| Status | Description | When |
|--------|-------------|------|
| 200 | OK | Successful request (even for application errors) |
| 400 | Bad Request | Invalid request data or business logic error |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Valid auth but insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Request validation failed |
| 500 | Internal Server Error | Server-side error |

### Common Error Codes

| Code | Description |
|------|-------------|
| INVALID_CREDENTIALS | Wrong email/password combination |
| NOT_ADMIN | User exists but is not an admin |
| ADMIN_INACTIVE | Admin account is deactivated |
| EMAIL_EXISTS | Email already registered |
| PERMISSION_DENIED | Insufficient permissions for action |

---

## Data Models

### Admin Model
```typescript
interface Admin {
  id: number;
  user_id: number;
  email: string;
  name: string;
  avatar_url: string | null;
  role: "super_admin" | "admin" | "moderator";
  permissions: string[];
  created_at: string; // ISO 8601
  last_login: string | null; // ISO 8601
}
```

### User Model
```typescript
interface User {
  id: number;
  email: string;
  name: string;
  phone: string | null;
  credits: number;
  is_verified: boolean;
  is_active: boolean;
  created_at: string; // ISO 8601
}
```

### Pagination Model
```typescript
interface Pagination {
  page: number;
  limit: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}
```

---

## Implementation Examples

### JavaScript/TypeScript Example

```javascript
// Login function
async function loginAdmin(email, password) {
  const response = await fetch('http://localhost:8000/api/admin/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });
  
  const data = await response.json();
  
  if (data.success) {
    // Store token for future requests
    localStorage.setItem('admin_token', data.data.access_token);
    return data.data;
  } else {
    throw new Error(data.error.message);
  }
}

// Get users with authentication
async function getUsers(page = 1, limit = 50) {
  const token = localStorage.getItem('admin_token');
  
  const response = await fetch(
    `http://localhost:8000/api/admin/users?page=${page}&limit=${limit}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }
  );
  
  if (response.status === 403) {
    throw new Error('Unauthorized - please login again');
  }
  
  const data = await response.json();
  return data.data;
}

// Create new user
async function createUser(userData) {
  const token = localStorage.getItem('admin_token');
  
  const response = await fetch('http://localhost:8000/api/admin/users', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });
  
  const data = await response.json();
  
  if (data.success) {
    return data.data.user;
  } else {
    throw new Error(data.message || 'Failed to create user');
  }
}
```

### Python Example

```python
import requests
import json

class MagicPicAdminAPI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
    
    def login(self, email, password):
        url = f"{self.base_url}/api/admin/auth/login"
        data = {"email": email, "password": password}
        
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get("success"):
            self.token = result["data"]["access_token"]
            return result["data"]
        else:
            raise Exception(result["error"]["message"])
    
    def get_headers(self):
        if not self.token:
            raise Exception("Not authenticated. Please login first.")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def get_users(self, page=1, limit=50, **filters):
        url = f"{self.base_url}/api/admin/users"
        params = {"page": page, "limit": limit, **filters}
        
        response = requests.get(url, headers=self.get_headers(), params=params)
        
        if response.status_code == 403:
            raise Exception("Unauthorized - please login again")
        
        return response.json()["data"]
    
    def create_user(self, user_data):
        url = f"{self.base_url}/api/admin/users"
        
        response = requests.post(url, headers=self.get_headers(), json=user_data)
        result = response.json()
        
        if result.get("success"):
            return result["data"]["user"]
        else:
            raise Exception(result.get("message", "Failed to create user"))

# Usage example
api = MagicPicAdminAPI()
admin_data = api.login("admin@example.com", "password")
users = api.get_users(page=1, limit=10, is_active=True)
```

---

## Testing with cURL

### Login
```bash
curl -X POST "http://localhost:8000/api/admin/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "your_password"
  }'
```

### Get Users (with token)
```bash
curl -X GET "http://localhost:8000/api/admin/users?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

### Create User
```bash
curl -X POST "http://localhost:8000/api/admin/users" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "userPassword123",
    "name": "New User",
    "credits": 2500
  }'
```

---

This documentation covers all the currently implemented APIs in your MagicPic Admin system. The APIs follow RESTful conventions and provide comprehensive error handling and response structures for reliable integration.