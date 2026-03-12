## Google Sign-In / Sign-Up API Guide (Android Only)

This document explains how the **Android app** should implement **Google sign-in & sign-up** using Firebase and the existing backend endpoint.

> ⚠️ **Important**: This endpoint is configured for **Android app usage only**. Requests from web browsers or other platforms will be rejected.

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
  "platform": "android",
  "device_info": {
    "device": "android",
    "model": "Pixel 7"
  },
  "referral_code": "OPTIONAL_REFERRAL_CODE"
}
```

| Field          | Type   | Required | Description                                          |
|----------------|--------|----------|------------------------------------------------------|
| `id_token`     | string | ✅ Yes   | Firebase ID token from `GoogleSignInAccount.getIdToken()` |
| `platform`     | string | ✅ Yes   | Must be `"android"`. Other values are rejected.      |
| `device_info`  | object | No       | Optional metadata (device model, OS, etc.)           |
| `referral_code`| string | No       | Referral code of the user who invited this user      |

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
      "credits": 2,
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

- **Non-Android platform**

  ```json
  {
    "success": false,
    "error": {
      "code": "PLATFORM_NOT_ALLOWED",
      "message": "Google sign-in is only supported on the Android app."
    }
  }
  ```

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

### Android Implementation (Kotlin + Firebase)

#### 1. Add dependencies (`build.gradle.kts`)

```kotlin
implementation("com.google.firebase:firebase-auth-ktx")
implementation("com.google.android.gms:play-services-auth:21.0.0")
```

#### 2. Configure Google Sign-In

```kotlin
val gso = GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
    .requestIdToken(getString(R.string.default_web_client_id)) // from google-services.json
    .requestEmail()
    .build()

val googleSignInClient = GoogleSignIn.getClient(this, gso)
```

#### 3. Launch the sign-in flow

```kotlin
// In your Activity or Fragment:
private val signInLauncher = registerForActivityResult(
    ActivityResultContracts.StartActivityForResult()
) { result ->
    val task = GoogleSignIn.getSignedInAccountFromIntent(result.data)
    handleSignInResult(task)
}

fun launchGoogleSignIn() {
    signInLauncher.launch(googleSignInClient.signInIntent)
}
```

#### 4. Handle result and call backend

```kotlin
private fun handleSignInResult(task: Task<GoogleSignInAccount>) {
    try {
        val account = task.getResult(ApiException::class.java)
        val googleIdToken = account.idToken ?: throw Exception("ID Token is null")
        firebaseAuthWithGoogle(googleIdToken)
    } catch (e: ApiException) {
        Log.w(TAG, "Google sign-in failed: ${e.statusCode}")
    }
}

private fun firebaseAuthWithGoogle(googleIdToken: String) {
    val credential = GoogleAuthProvider.getCredential(googleIdToken, null)
    FirebaseAuth.getInstance().signInWithCredential(credential)
        .addOnSuccessListener { authResult ->
            authResult.user?.getIdToken(false)?.addOnSuccessListener { tokenResult ->
                val firebaseIdToken = tokenResult.token ?: return@addOnSuccessListener
                sendTokenToBackend(firebaseIdToken)
            }
        }
        .addOnFailureListener { e ->
            Log.e(TAG, "Firebase auth failed", e)
        }
}

private fun sendTokenToBackend(firebaseIdToken: String) {
    // Use your HTTP client (Retrofit / OkHttp / Ktor) to POST to the backend
    val body = mapOf(
        "id_token" to firebaseIdToken,
        "platform" to "android",
        "device_info" to mapOf(
            "device" to "android",
            "model" to android.os.Build.MODEL
        )
    )

    // Example using a coroutine + your ApiService:
    viewModelScope.launch {
        val response = apiService.googleLogin(body)
        if (response.success) {
            // Store response.data.access_token, refresh_token, user
        }
    }
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

    - Response:

      ```json
      {
        "access_token": "NEW_ACCESS_TOKEN",
        "refresh_token": "SAME_OR_NEW_REFRESH_TOKEN",
        "token_type": "bearer",
        "expires_in": 1800
      }
      ```

---

### Backend Configuration (GitHub Secrets)

The backend verifies Google/Firebase ID tokens via **Firebase Admin SDK** and optionally enforces that only Android app tokens are accepted. Configure these secrets in **GitHub → Repository Settings → Secrets and variables → Actions**:

| Secret Name                    | Value                                                              | Required |
|--------------------------------|--------------------------------------------------------------------|----------|
| `FIREBASE_PROJECT_ID`          | Your Firebase project ID (e.g. `my-app-12345`)                    | ✅ Yes   |
| `FIREBASE_SERVICE_ACCOUNT_B64` | Base64-encoded Firebase service account JSON *(see below)*        | ✅ Yes   |
| `FIREBASE_ANDROID_CLIENT_ID`   | Android OAuth2 client ID from `google-services.json` *(see below)*| ✅ Recommended |

#### How to get `FIREBASE_SERVICE_ACCOUNT_B64`

1. Firebase Console → Project Settings → Service accounts → **Generate new private key**
2. Download the JSON file.
3. Base64-encode it:
   ```bash
   base64 -w 0 firebase-service-account.json
   ```
4. Paste the output as the `FIREBASE_SERVICE_ACCOUNT_B64` secret.

#### How to get `FIREBASE_ANDROID_CLIENT_ID`

1. Open your `google-services.json` (download from Firebase Console → Project Settings → Your Android app).
2. Find the `oauth_client` array and look for `"client_type": 3` (that's the Android client).
3. Copy the `client_id` value — it looks like:
   ```
   123456789012-abcdefghijklmnopqrstuvwxyz012345.apps.googleusercontent.com
   ```
4. Add it as the `FIREBASE_ANDROID_CLIENT_ID` GitHub secret.

> When `FIREBASE_ANDROID_CLIENT_ID` is set, the backend verifies that the token's `aud` claim matches this ID, rejecting any token issued from a web or other platform Firebase project.

---

### Quick Checklist for Android Dev

- [ ] Add `google-services.json` to the Android app module.
- [ ] Enable **Google** sign-in in Firebase Console → Authentication → Sign-in methods.
- [ ] Implement Google sign-in flow to get the Firebase `id_token`.
- [ ] Call `POST /api/auth/google` with `{ id_token, platform: "android", device_info }`.
- [ ] On success, store `access_token`, `refresh_token`, and `user`.
- [ ] Use `Authorization: Bearer <access_token>` for subsequent API calls.
- [ ] Use `POST /api/auth/refresh` with the refresh token when needed.
- [ ] Add `FIREBASE_ANDROID_CLIENT_ID` to GitHub secrets for production enforcement.
