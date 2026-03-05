## Auth, Credits & Referrals – Frontend Guide

This document describes the request **payloads** and **responses** for:

- Email/password signup with configurable initial credits
- Google signup/login with optional referral
- Referral rewards
- Daily expiring credits and their effect on image generation

All examples assume the API is mounted under `/api`.

---

## 1. Email/Password Signup

- **URL**: `/api/auth/signup`
- **Method**: `POST`
- **Auth**: Public (no token required)
- **Purpose**:
  - Create a new user account with email/password.
  - Assign initial credits (configured on backend).
  - Optionally attribute signup to a referrer using their `referral_code`.

### 1.1 Request Payload

Content-Type: `application/json`

```json
{
  "email": "newuser@example.com",
  "name": "New User",
  "phone": "+1-555-123-4567",
  "password": "strongpassword123",
  "referral_code": "ABCD1234"
}
```

- **email** (required): User email (must be unique).
- **name** (required).
- **phone** (optional).
- **password** (required): Minimum 8 characters.
- **referral_code** (optional):
  - Code belonging to an existing user.
  - If valid:
    - The **new user** is marked as "referred by" that user.
    - The **referrer** receives additional credits (see Referral Credits below).

> If `referral_code` is omitted or invalid, signup still succeeds; no referral reward is given.

### 1.2 Success Response

Status: `201 Created` or `200 OK` (depending on current implementation)

```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "newuser@example.com",
      "name": "New User",
      "phone": "+1-555-123-4567",
      "avatar_url": null,
      "credits": 2,
      "is_verified": false,
      "referral_code": "REF12345",
      "daily_credits": 0,
      "daily_credits_date": null,
      "created_at": "2026-03-05T10:00:00Z"
    },
    "access_token": "JWT_ACCESS_TOKEN",
    "refresh_token": "JWT_REFRESH_TOKEN",
    "token_type": "bearer",
    "expires_in": 1800
  },
  "message": "Account created successfully. Please verify your email."
}
```

Notes for frontend:

- **`data.user.credits`**:
  - Initial non-expiring credits.
  - Value is configured on backend (example shows `2`).
- **`data.user.daily_credits` / `daily_credits_date`**:
  - Daily credits are not granted at signup; they are granted lazily on use (see Daily Credits section).
- **`data.user.referral_code`**:
  - Unique code that this user can share with others.

### 1.3 Error Responses

- **Email already exists**

```json
{
  "success": false,
  "error": {
    "code": "EMAIL_EXISTS",
    "message": "An account with this email already exists"
  }
}
```

- **Invalid email / weak password / validation errors**

These are normalized by the global validation handler. Typical examples:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_EMAIL",
    "message": "Invalid request. Please check your input."
  }
}
```

```json
{
  "success": false,
  "error": {
    "code": "WEAK_PASSWORD",
    "message": "Invalid request. Please check your input."
  }
}
```

---

## 2. Google Sign-In / Sign-Up (with Optional Referral)

This extends the existing Google auth doc (`googlesignup-in.md`) with referral support and credit behavior.

- **URL**: `/api/auth/google`
- **Method**: `POST`
- **Auth**: Public
- **Purpose**:
  - If Google email is **new** → sign up user, assign initial credits, optional referral.
  - If Google email **already exists** → log user in.

### 2.1 Request Payload

Content-Type: `application/json`

```json
{
  "id_token": "FIREBASE_GOOGLE_ID_TOKEN",
  "device_info": {
    "device": "web",
    "userAgent": "optional-user-agent-or-device-string"
  },
  "referral_code": "ABCD1234"
}
```

- **id_token** (required): Firebase ID token from Google sign-in.
- **device_info** (optional): Any metadata you want to send.
- **referral_code** (optional):
  - Only used when this results in a **new account**.
  - Same semantics as email/password signup:
    - If valid, the referrer gets referral credits.
    - If invalid or missing, signup still works; no referral reward.

### 2.2 Success Response

Status: `200 OK`

```json
{
  "success": true,
  "data": {
    "user": {
      "id": 2,
      "email": "googleuser@example.com",
      "name": "Google User",
      "phone": null,
      "avatar_url": "https://example.com/avatar.png",
      "credits": 2,
      "is_verified": true,
      "referral_code": "REF67890",
      "daily_credits": 0,
      "daily_credits_date": null,
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

Notes:

- For **first-time Google signup**, `credits` will be the configured initial credits (e.g. `2`).
- For **returning users**, `credits` reflects their existing balance.
- Daily credits are granted/updated lazily when generating creations (see below), not on login.

### 2.3 Error Responses

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

## 3. Referral Credits (Behavior)

There is no separate "referral API" — referral logic is triggered during **signup** when a valid `referral_code` is provided.

- When a new user signs up (email/password or Google) with a **valid** `referral_code`:
  - The **new user** is created as normal (with initial credits).
  - The **referrer** (owner of that `referral_code`) receives **referral reward credits** added to their `credits`.
  - These referral reward credits do **not** expire daily; they are part of the main `credits` balance.

Frontend implications:

- To show "You earned X credits from referrals", you may need a separate endpoint/stats in the future; currently the API only exposes total `credits`, not the breakdown.
- You can surface referral UX on signup by:
  - Showing the user’s own `referral_code` from `data.user.referral_code`.
  - Accepting a `referral_code` field on your signup/Google-connect UI and passing it through.

---

## 4. Daily Free Credits (Expiring per Day)

Daily credits are **not** requested via a dedicated endpoint. They are granted/updated automatically when a user performs a credit-consuming action (image generation).

### 4.1 Model Fields (in `user`)

The user object includes:

- **`daily_credits`**: Number of free credits currently available for **today**.
- **`daily_credits_date`**: Timestamp indicating the day those `daily_credits` belong to.

Behavior (server-side, conceptual for frontend):

- On the first generate request each UTC day:
  - If `daily_credits_date` is not **today**, backend sets:
    - `daily_credits = DAILY_FREE_CREDITS` (configurable, e.g. `5`)
    - `daily_credits_date = now`
- When spending credits on `/api/creations/generate`:
  - Backend uses **`daily_credits` first**.
  - Any remaining cost is taken from normal `credits`.
  - `daily_credits` do **not** roll over; they are effectively reset each new day.

### 4.2 How Frontend Should Use It

- Treat `daily_credits` as **bonus credits for today**:
  - Display them if helpful (e.g. "5 free credits today").
  - Expect them to change once the user generates images.
- To compute the user’s **total available credits** at any given moment based on the last known user object:

```ts
const totalCredits =
  (user.credits ?? 0) +
  ((user.daily_credits && user.daily_credits_date) ? user.daily_credits : 0);
```

Actual enforcement still happens server-side (see next section).

---

## 5. Image Generation & Credit Enforcement

- **URL**: `/api/creations/generate`
- **Method**: `POST` (multipart/form-data)
- **Auth**: Requires access token (`Authorization: Bearer <access_token>`)
- **Purpose**:
  - Generate a new creation and deduct credits (daily first, then main balance).

### 5.1 Relevant Request Fields

Payload fields (simplified to credit-relevant parts; full spec is in existing docs):

- **`style_id`**: Style to apply.
- **`image`**: Uploaded image.

### 5.2 Success Response (Excerpt)

On success, backend returns the `GenerateResponse`. The important credit-related fields are:

```json
{
  "success": true,
  "data": {
    "id": 123,
    "credits_used": 1,
    "credits_remaining": 6,
    "...": "... other creation fields ..."
  },
  "message": "Image generated successfully!"
}
```

- **`credits_used`**: How many credits this generation cost (from style).
- **`credits_remaining`**: Total credits remaining after this generation.
  - This is the **combined** remaining credits (normal + remaining daily for today) after deduction.

> The frontend can use `credits_remaining` to keep its local view in sync after a generation, even if it doesn’t know exactly how much came from daily vs main credits.

### 5.3 Insufficient Credits Response

If the user does not have enough **total** credits (normal + daily):

Status: `402 Payment Required`

```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_CREDITS",
    "message": "You need 3 credits. You have 1."
  }
}
```

- The `"You have X."` part reflects the **total** available credits at the time of the request.
- Frontend can show this message directly, and/or use the `"code"` field to branch UI behavior.

---

## 6. Configuration Summary (For Reference)

These values are **configurable on the backend**; frontend should not hard-code them, but may want to reflect them in static copy if they are stable:

- **Initial signup credits**: `SIGNUP_INITIAL_CREDITS` (default example: `2`)
- **Referral reward credits**: `REFERRAL_REWARD_CREDITS` (default example: `5`)
- **Daily free credits**: `DAILY_FREE_CREDITS` (default example: `5`)

Always rely on the `user` object and responses to know the user’s real-time balance, not on assumed static numbers.

