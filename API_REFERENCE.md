# MagicPic Admin API — Complete API Reference

This document describes every API in the codebase: what to send (headers, body, query) and what to expect in success and error responses.

**Base URL (example):** `http://localhost:8000`  
**API prefix:** `/api/admin`

---

## Table of Contents

1. [Authentication Overview](#1-authentication-overview)
2. [Root](#2-root)
3. [Auth APIs](#3-auth-apis)
4. [Users APIs](#4-users-apis)
5. [Common Error Responses](#5-common-error-responses)
6. [Quick Reference Table](#6-quick-reference-table)

---

## 1. Authentication Overview

- **Public endpoints** (no token): `GET /`, `POST /api/admin/auth/login`, `POST /api/admin/auth/register`
- **Protected endpoints**: require header  
  **`Authorization: Bearer <access_token>`**  
  Use the `access_token` from the login/register response.
- **Permissions**: Some protected routes require specific permissions (e.g. `users.view`, `users.create`). `super_admin` bypasses permission checks.

---

## 2. Root

### GET /

**Description:** Health/welcome endpoint.

**Auth:** None.

**Request**

- **Headers:** None required.
- **Body:** None.

**Success response:** `200 OK`

```json
{
  "message": "Welcome to MagicPic Admin API",
  "version": "1.0.0"
}
```

---

## 3. Auth APIs

Base path: **`/api/admin/auth`**

---

### POST /api/admin/auth/login

**Description:** Admin login. Returns admin profile and JWT access token.

**Auth:** None.

**Request**

- **Headers:**
  - `Content-Type: application/json` (required)
- **Body (JSON):**

| Field     | Type   | Required | Description        |
|----------|--------|----------|--------------------|
| `email`  | string | Yes      | Valid email format |
| `password` | string | Yes    | Plain text password |

**Example:**

```json
{
  "email": "admin@example.com",
  "password": "your_password"
}
```

**Success response:** `200 OK`

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
      "permissions": ["users.view", "users.create", "credits.manage", "styles.manage"],
      "created_at": "2025-02-11T10:00:00",
      "last_login": null
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  },
  "error": null
}
```

| Field | Type | Description |
|-------|------|-------------|
| `data.admin.id` | number | Admin record ID |
| `data.admin.user_id` | number | Underlying user ID |
| `data.admin.email` | string | Email |
| `data.admin.name` | string | Display name |
| `data.admin.avatar_url` | string \| null | Avatar URL |
| `data.admin.role` | string | `admin` or `super_admin` |
| `data.admin.permissions` | string[] | List of permission strings |
| `data.admin.created_at` | string (ISO 8601) | Creation time |
| `data.admin.last_login` | string \| null | Last login time |
| `data.access_token` | string | JWT — use in `Authorization: Bearer <token>` |
| `data.token_type` | string | Always `"bearer"` |
| `data.expires_in` | number | Token lifetime in **seconds** |

**Error responses:** All with `200 OK` and `success: false`.

| Condition | `error.code` | `error.message` |
|-----------|--------------|------------------|
| User not found or wrong password | `INVALID_CREDENTIALS` | Invalid email or password |
| User exists but no admin record | `NOT_ADMIN` | You do not have admin privileges |
| Admin exists but inactive | `ADMIN_INACTIVE` | Admin account is deactivated |

**Example error body:**

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password"
  }
}
```

**Validation errors (422):** Invalid body (e.g. missing/invalid `email` or `password`) return FastAPI validation detail, not the above shape.

---

### POST /api/admin/auth/register

**Description:** Register a new admin (creates User + Admin and returns token).

**Auth:** None.

**Request**

- **Headers:**
  - `Content-Type: application/json` (required)
- **Body (JSON):**

| Field     | Type   | Required | Default   | Description        |
|----------|--------|----------|-----------|--------------------|
| `email`  | string | Yes      | —         | Valid email format |
| `password` | string | Yes    | —         | Plain text password |
| `name`   | string | Yes      | —         | Display name       |
| `role`   | string | No       | `"admin"` | `admin` or `super_admin` |

**Example:**

```json
{
  "email": "newadmin@example.com",
  "password": "securePassword123",
  "name": "New Admin",
  "role": "admin"
}
```

**Success response:** `200 OK`

Same structure as login success:

```json
{
  "success": true,
  "data": {
    "admin": { ... },
    "access_token": "...",
    "token_type": "bearer",
    "expires_in": 1800
  },
  "error": null
}
```

**Error responses:** `200 OK` with `success: false`.

| Condition | `error.code` | `error.message` |
|-----------|--------------|------------------|
| Email already registered | `EMAIL_EXISTS` | Email already registered |

**Example:**

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "EMAIL_EXISTS",
    "message": "Email already registered"
  }
}
```

**Validation errors (422):** Invalid/missing body fields return FastAPI validation detail.

---

## 4. Users APIs

Base path: **`/api/admin/users`**

All users endpoints require a valid JWT and the appropriate permission unless stated otherwise.

**Required header for all requests:**

- `Authorization: Bearer <access_token>`

---

### GET /api/admin/users

**Description:** List users with optional filtering, search, and pagination.

**Auth:** Required. Permission: **`users.view`** (or `super_admin`).

**Request**

- **Headers:**
  - `Authorization: Bearer <access_token>` (required)
  - `Content-Type: application/json` (optional)
- **Query parameters:**

| Parameter    | Type    | Required | Default     | Description                                      |
|-------------|---------|----------|-------------|--------------------------------------------------|
| `page`      | integer | No       | `1`         | Page number (1-based)                            |
| `limit`     | integer | No       | `50`        | Items per page                                   |
| `search`    | string  | No       | —           | Search in `name` and `email` (case-insensitive)  |
| `is_verified` | boolean | No     | —           | Filter by verification status                    |
| `is_active` | boolean | No      | —           | Filter by active status                          |
| `sort_by`   | string  | No       | `created_at`| Field to sort by (e.g. `created_at`, `name`, `email`) |
| `sort_order`| string  | No       | `desc`      | `asc` or `desc`                                 |

**Example:**

```
GET /api/admin/users?page=1&limit=10&search=john&is_active=true&sort_by=created_at&sort_order=desc
```

**Success response:** `200 OK`

```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": 1,
        "email": "user@example.com",
        "name": "User Name",
        "phone": null,
        "credits": 2500,
        "is_verified": true,
        "is_active": true,
        "created_at": "2025-02-11T10:00:00"
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

| Field | Type | Description |
|-------|------|-------------|
| `data.users` | array | List of user objects |
| `data.users[].id` | number | User ID |
| `data.users[].email` | string | Email |
| `data.users[].name` | string | Display name |
| `data.users[].phone` | string \| null | Phone |
| `data.users[].credits` | number | Credit balance |
| `data.users[].is_verified` | boolean | Verification status |
| `data.users[].is_active` | boolean | Active status |
| `data.users[].created_at` | string (ISO 8601) | Creation time |
| `data.pagination.page` | number | Current page |
| `data.pagination.limit` | number | Page size |
| `data.pagination.total` | number | Total count of users |
| `data.pagination.total_pages` | number | Total pages |
| `data.pagination.has_next` | boolean | More pages after this |
| `data.pagination.has_prev` | boolean | Previous page exists |

**Error responses**

| HTTP | Condition | Body (typical) |
|------|-----------|----------------|
| 403 | No/invalid token | `{"detail": "Could not validate credentials"}` |
| 403 | Valid token but missing permission | `{"detail": "Not enough permissions"}` |
| 404 | Token valid but admin not in DB | `{"detail": "Admin not found"}` |
| 400 | Admin inactive | `{"detail": "Inactive admin"}` |

---

### POST /api/admin/users

**Description:** Create a new (app) user.

**Auth:** Required. Permission: **`users.create`** (or `super_admin`).

**Request**

- **Headers:**
  - `Authorization: Bearer <access_token>` (required)
  - `Content-Type: application/json` (required)
- **Body (JSON):**

| Field        | Type    | Required | Default | Description        |
|-------------|---------|----------|---------|--------------------|
| `email`     | string  | Yes      | —       | Valid email format |
| `password`  | string  | Yes      | —       | Plain text password |
| `name`      | string  | Yes      | —       | Display name       |
| `phone`     | string  | No       | null    | Phone              |
| `credits`   | integer | No       | 2500    | Initial credits    |
| `is_verified` | boolean | No     | true    | Verified flag      |
| `is_active` | boolean | No      | true    | Active flag        |

**Example:**

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

**Success response:** `200 OK`

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
      "created_at": "2025-02-11T12:00:00"
    }
  },
  "message": "User created successfully"
}
```

**Error responses**

| HTTP | Condition | Body (typical) |
|------|-----------|----------------|
| 400 | Email already exists | `{"detail": "The user with this email already exists"}` |
| 403 | No/invalid token | `{"detail": "Could not validate credentials"}` |
| 403 | Not enough permission | `{"detail": "Not enough permissions"}` |
| 404 | Admin not found | `{"detail": "Admin not found"}` |
| 400 | Inactive admin | `{"detail": "Inactive admin"}` |
| 422 | Validation error (body) | FastAPI validation error detail |

---

## 5. Common Error Responses

### Authentication / authorization (protected routes)

| HTTP | `detail` | When |
|------|----------|------|
| 403 | Could not validate credentials | Missing/invalid/expired JWT or wrong signature |
| 403 | Not enough permissions | Valid admin but missing required permission |
| 404 | Admin not found | Token valid but admin ID not in DB |
| 400 | Inactive admin | Admin record exists but `is_active` is false |

### Validation (422)

For invalid request body or query (e.g. invalid email, missing required field), the response is FastAPI’s default validation error, e.g.:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "email"],
      "msg": "Field required",
      "input": { ... }
    }
  ]
}
```

### OAuth2PasswordBearer (no token)

If the client calls a protected endpoint without `Authorization: Bearer ...`:

- **HTTP 403**
- Body shape depends on FastAPI/OAuth2; often includes `detail` and possibly `headers` (e.g. `WWW-Authenticate`).

---

## 6. Quick Reference Table

| Method | Path | Auth | Permission | Purpose |
|--------|------|------|------------|---------|
| GET | `/` | No | — | Welcome / health |
| POST | `/api/admin/auth/login` | No | — | Admin login |
| POST | `/api/admin/auth/register` | No | — | Admin registration |
| GET | `/api/admin/users` | Bearer | `users.view` | List users |
| POST | `/api/admin/users` | Bearer | `users.create` | Create user |

**To get a proper response:**

1. **Public auth:** Send valid JSON body; check `success` and use `data` or `error` accordingly.
2. **Protected routes:** Send `Authorization: Bearer <access_token>` with a token from login/register; ensure the admin has the required permission and is active.

---

*Generated from the current codebase. OpenAPI schema is also available at `/api/admin/openapi.json`.*
