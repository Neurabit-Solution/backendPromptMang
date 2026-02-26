# Guest Free Trial API Documentation

This document outlines the API endpoint for providing a one-time free AI generation trial to non-authenticated users based on their device ID.

## Base URL
`http://localhost:8000/api` (Local)
`https://your-api-domain.com/api` (Production)

---

## 1. Free Trial Generation (One-time)
Apply an AI style to a photo without logging in.

- **URL:** `/guest/generate`
- **Method:** `POST`
- **Auth Required:** NO (Public)
- **Content-Type:** `multipart/form-data`

### Request Parameters
| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `device_id` | String | Yes | Unique identifier for the device (see "Identifying Android Devices" below) |
| `style_id` | Integer | Yes | The ID of the style to apply (get these from `/api/styles`) |
| `image` | File | Yes | Image file (JPG, PNG, or WebP). Max 10MB. |

### Identifying Android Devices
For Android applications, use the **`ANDROID_ID`**. This is a 64-bit number that remains constant for the life of the device (unless factory reset).

**How to get it in code:**
```java
import android.provider.Settings.Secure;

String deviceId = Secure.getString(getContext().getContentResolver(), Secure.ANDROID_ID);
```
*Note: Do NOT use IMEI or MAC Address as these are restricted in newer Android versions.*

---

### Response Success
- **Status Code:** `200 OK`
- **Body:** Binary Image Data (image/jpeg)
- **Note:** Unlike the standard user API, this endpoint returns the **raw image bytes**. You should display this directly in your `ImageView` / `Image` component. It is **not** saved to S3 and no URL is provided.

### Response Errors

#### 1. Trial Already Used
The device has already used its one free creation.
- **Status Code:** `403 Forbidden`
- **Body:**
```json
{
  "success": false,
  "error": {
    "code": "TRIAL_EXHAUSTED",
    "message": "Your free trial has ended. Please sign up or log in to continue creating!"
  }
}
```

#### 2. Style Not Found
- **Status Code:** `404 Not Found`
- **Body:**
```json
{
  "success": false,
  "error": {
    "code": "STYLE_NOT_FOUND",
    "message": "Style not found."
  }
}
```

#### 3. Invalid Image
- **Status Code:** `400 Bad Request` or `413 Payload Too Large`
- **Body:**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_IMAGE",
    "message": "Only JPG, PNG, and WebP images are supported."
  }
}
```

---

## Implementation Notes for Frontend Devs
1. **Initial Load**: Use the existing public `GET /api/styles` to fetch the list of gallery styles for the user to choose from.
2. **One-Time Check**: You don't need to check "if used" beforehand. Simply attempt the call; if you get a `403 TRIAL_EXHAUSTED`, show a "Signup Required" popup/modal.
3. **Data Handling**: Since the response is binary, handle it as a `Blob` (Web) or `InputStream` (Mobile) to render the image.
