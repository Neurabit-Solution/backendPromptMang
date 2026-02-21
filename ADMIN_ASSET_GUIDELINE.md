# Admin Asset Guidelines: Styles & Categories

This document outlines the required file structure and S3 naming conventions for the Admin service when uploading content to the MagicPic ecosystem. Adhering to these paths ensures the Backend API and Frontend can correctly locate and display artistic styles.

---

## 1. Directory Overview

All assets must be stored within the `prompt-management-system` S3 bucket using the following directory structure:

```text
magicpic-bucket/
├── categories/
│   └── thumbnails/          # Cover images for Category groups
└── styles/
    └── thumbnails/          # Preview cards for individual AI Styles
```

---

## 2. Category (Collection) Assets

Categories group multiple styles together (e.g., "Trending", "Traditional").

### **S3 Storage Rule**
*   **Path:** `categories/thumbnails/`
*   **Filename:** Must match the **Category Slug**.
*   **Format:** Preferred `.jpg` or `.png`.

| Field | Example Value | Resulting S3 Key |
| :--- | :--- | :--- |
| Name | "Wedding Special" | — |
| Slug | `wedding-special` | `categories/thumbnails/wedding-special.jpg` |

### **Database Entry**
When saving to the `categories` table, the `preview_url` column must contain the full public HTTPS URL:
`https://<bucket>.s3.<region>.amazonaws.com/categories/thumbnails/wedding-special.jpg`

---

## 3. Style Assets

Styles are the individual artistic filters the user selects.

### **S3 Storage Rule**
*   **Path:** `styles/thumbnails/`
*   **Filename:** Must match the **Style Slug**.
*   **Format:** Highly recommended `.jpg` (1:1 or 4:5 aspect ratio for UI consistency).

| Field | Example Value | Resulting S3 Key |
| :--- | :--- | :--- |
| Name | "Dragon Rider" | — |
| Slug | `dragon-rider` | `styles/thumbnails/dragon-rider.jpg` |

### **Database Entry**
When saving to the `styles` table, the `preview_url` column must contain the full public HTTPS URL:
`https://<bucket>.s3.<region>.amazonaws.com/styles/thumbnails/dragon-rider.jpg`

---

## 4. Admin Checklist for Uploading

When your admin code processes a new Style or Category:

1.  **Generate Slug:** Convert the name to lowercase, replace spaces with hyphens, and remove special characters (e.g., "Neon Glow!" -> `neon-glow`).
2.  **Rename File:** Rename the local image file to `<slug>.jpg` before uploading.
3.  **Upload to S3:**
    *   Use the `ContentType` header: `image/jpeg`.
    *   Ensure the ACL is set to `public-read` (if bucket policy requires it).
4.  **Save to DB:** Use the helper function provided in the backend (`_build_url`) or manually concatenate the bucket URL with the key to populate the `preview_url` field.

---

## 5. Technical Specification

| Environment Variable | Recommended Value |
| :--- | :--- |
| **Max Image Size** | 2MB (for fast UI loading) |
| **Dimensions (Category)** | 800 x 400 px (Landscape) |
| **Dimensions (Style)** | 600 x 600 px or 600 x 800 px |
| **Mime Types** | `image/jpeg`, `image/png`, `image/webp` |
