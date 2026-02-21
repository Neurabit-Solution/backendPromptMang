# Frontend Integration Guide: Styles & Categories Management

This document provides instructions for the frontend team to integrate with the new Styles and Categories management APIs. These APIs now support direct image uploads to S3 and database persistence.

## 1. Authentication
All requests must include the Admin Authorization header:
```http
Authorization: Bearer <admin_access_token>
```

---

## 2. Categories API

### **Create a Category**
*   **Endpoint:** `POST /api/admin/categories/`
*   **Content-Type:** `multipart/form-data`
*   **Form Fields:**
    *   `name` (string, required): Display name (e.g., "Trending")
    *   `icon` (string, required): Emoji icon (e.g., "🔥")
    *   `description` (string, required): Brief description
    *   `display_order` (integer, optional): Sort priority (default: 0)
    *   `is_active` (boolean, optional): Active status (default: true)
    *   `preview_image` (file, optional): Image file (JPG/PNG)

### **Update a Category**
*   **Endpoint:** `PUT /api/admin/categories/{id}`
*   **Content-Type:** `multipart/form-data`
*   **Form Fields:** Same as Create (all fields are optional).

### **Get All Categories**
*   **Endpoint:** `GET /api/admin/categories/`

---

## 3. Styles API

### **Create a Style**
*   **Endpoint:** `POST /api/admin/styles/`
*   **Content-Type:** `multipart/form-data`
*   **Form Fields:**
    *   `category_id` (integer, required): ID of the category this style belongs to.
    *   `name` (string, required): Style name (e.g., "Neon Cyberpunk")
    *   `description` (string, required): Description for users.
    *   `prompt_template` (string, required): The AI prompt (e.g., "Cyberpunk style, neon lights...")
    *   `negative_prompt` (string, optional): What to avoid.
    *   `tags` (string, optional): JSON array of tags (e.g., `["sci-fi", "digital"]`).
    *   `credits_required` (integer, optional): Cost per use (default: 50).
    *   `display_order` (integer, optional): Sort priority (default: 0).
    *   `is_trending` (boolean, optional): Mark as trending.
    *   `is_new` (boolean, optional): Mark as new.
    *   `is_active` (boolean, optional): Is it available for users.
    *   `preview_image` (file, **required**): The image demonstrating this style.

### **Update a Style**
*   **Endpoint:** `PUT /api/admin/styles/{id}`
*   **Content-Type:** `multipart/form-data`
*   **Form Fields:** Same as Create (all fields are optional).

---

## 4. Implementation Details (Frontend)

### **Handling Multipart Form Data**
Since we are sending files, you MUST use `FormData` object in your fetch/axios request:

```javascript
const formData = new FormData();
formData.append('name', 'Pencil Sketch');
formData.append('category_id', 1);
formData.append('description', 'A hand-drawn pencil art style');
formData.append('prompt_template', 'pencil sketch, graphite, detailed lines');
formData.append('preview_image', fileInput.files[0]); // The actual File object

// Note: Do NOT set Content-Type header manually when using FormData; 
// the browser will set it to multipart/form-data with the correct boundary.
axios.post('/api/admin/styles/', formData, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### **Slug Warning**
The backend automatically generates slugs from the `name` field for S3 storage (e.g., "Pencil Sketch" -> `pencil-sketch`). You do not need to provide a slug unless you want to override the default (available in Categories API).

---

## 5. Success/Error Responses

### **Success (200/201)**
Returns the created/updated object with the full `preview_url` (pointing to S3).
```json
{
  "id": 1,
  "name": "Pencil Sketch",
  "preview_url": "https://prompt-management-system.s3.ap-south-1.amazonaws.com/styles/thumbnails/pencil-sketch.jpg",
  ...
}
```

### **Errors**
*   `400 Bad Request`: Validation error or duplicate slug.
*   `404 Not Found`: Referenced Category ID does not exist.
*   `500 Internal Server Error`: S3 upload failure (check AWS credentials).
