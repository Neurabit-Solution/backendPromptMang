## Google Sign-In / Sign-Up API Guide

This document explains how the frontend should implement **Google sign-in & sign-up** using Firebase on the client and the existing backend endpoint.

---

### Backend Endpoint

- **URL**: `/api/auth/google`
- **Method**: `POST`
- **Auth**: No auth required (public endpoint)
- **Purpose**:
  - If the Google email is **new** → creates a user (sign-up) and logs them in.
  - If the Google email **already exists** → logs the user in.

#### Request Body

Content-Type: `application/json`

```json
{
  "id_token": "FIREBASE_GOOGLE_ID_TOKEN",
  "device_info": {
    "device": "web",
    "userAgent": "optional-user-agent-or-device-string"
  }
}
```

- **id_token**: Firebase ID token obtained from the Google sign-in flow on the client.
- **device_info**: Optional object for metadata; can be omitted or customized.

#### Success Response

Status: `200 OK`

```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "User Name",
      "phone": null,
      "avatar_url": "https://example.com/avatar.png",
      "credits": 2500,
      "is_verified": true,
      "referral_code": "ABCD1234",
      "created_at": "2026-03-05T10:00:00Z"
    },
    "access_token": "JWT_ACCESS_TOKEN",
    "refresh_token": "JWT_REFRESH_TOKEN",
    "token_type": "bearer",
    "expires_in": 1800
  },
  "message": "Login with Google successful"
}
```

#### Error Responses

- **Invalid token**

  ```json
  {
    "success": false,
    "error": {
      "code": "INVALID_GOOGLE_TOKEN",
      "message": "Google authentication failed. Please try again."
    }
  }
  ```

- **Google account has no email**

  ```json
  {
    "success": false,
    "error": {
      "code": "EMAIL_NOT_PROVIDED",
      "message": "Google account does not have a valid email."
    }
  }
  ```

---

### Frontend Implementation (Firebase + Fetch)

Below is a reference flow using **Firebase Web SDK** and `fetch`. Adapt as needed (React, Next.js, plain JS, etc.).

#### 1. Get Google ID token from Firebase

Example (TypeScript/JavaScript):

```ts
import { signInWithPopup, GoogleAuthProvider } from "firebase/auth";
import { auth } from "./firebase"; // your initialized Firebase auth

const googleProvider = new GoogleAuthProvider();

export async function signInWithGoogle() {
  const result = await signInWithPopup(auth, googleProvider);
  const idToken = await result.user.getIdToken(); // <-- send this to backend
  return idToken;
}
```

#### 2. Call the backend `/api/auth/google` endpoint

```ts
export async function loginOrSignupWithGoogle() {
  const idToken = await signInWithGoogle();

  const response = await fetch("https://<BACKEND_DOMAIN>/api/auth/google", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      id_token: idToken,
      device_info: {
        device: "web",
        userAgent: typeof navigator !== "undefined" ? navigator.userAgent : "unknown"
      }
    })
  });

  const data = await response.json();

  if (!response.ok || !data.success) {
    // Handle error states here (show toast, etc.)
    throw new Error(data?.error?.message || "Google sign-in failed");
  }

  // Persist tokens & user info in your auth store
  const {
    access_token,
    refresh_token,
    token_type,
    expires_in,
    user
  } = data.data;

  // Example:
  // authStore.setSession({ access_token, refresh_token, token_type, expires_in, user });

  return data.data;
}
```

---

### Using Tokens After Google Login

- **Access token**:
  - Use in `Authorization` header for authenticated API calls:

    ```http
    Authorization: Bearer <access_token>
    ```

- **Refresh token**:
  - When access token expires, call:
    - **Endpoint**: `POST /api/auth/refresh`
    - **Headers**:

      ```http
      Authorization: Bearer <refresh_token>
      ```

    - Response (simplified):

      ```json
      {
        "access_token": "NEW_ACCESS_TOKEN",
        "refresh_token": "SAME_OR_NEW_REFRESH_TOKEN",
        "token_type": "bearer",
        "expires_in": 1800
      }
      ```

---

### Backend Configuration Requirements (for Google / Firebase)

The backend verifies Google/Firebase ID tokens via **Firebase Admin SDK**. Make sure the following is set in environment/config (one of these is enough):

- **Option 1 (recommended)**: `FIREBASE_SERVICE_ACCOUNT_B64`  
  - Base64-encoded contents of your Firebase service account JSON.
- **Option 2**: `FIREBASE_SERVICE_ACCOUNT_JSON`  
  - Raw JSON string of the service account.
- **Option 3**: `FIREBASE_SERVICE_ACCOUNT_PATH`  
  - Filesystem path to the service account JSON file.

The Firebase project used by the **frontend** must match the project configured via these credentials so that ID tokens validate correctly.

---

### Quick Checklist for Frontend Dev

- [ ] Set up Firebase Web app with **Google sign-in** enabled.
- [ ] Implement Google sign-in to get **`id_token`** from Firebase.
- [ ] Call `POST /api/auth/google` with `{ id_token, device_info }`.
- [ ] On success, store `access_token`, `refresh_token`, and `user`.
- [ ] Use `Authorization: Bearer <access_token>` for subsequent API calls.
- [ ] Use `POST /api/auth/refresh` with the refresh token when needed.

