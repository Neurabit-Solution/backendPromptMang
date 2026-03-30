# Admin Asset Guidelines: Styles & Categories

This document outlines the required file structure and S3 naming conventions for the Admin service when uploading content to the MagicPic ecosystem. Adhering to these paths ensures the Backend API and Frontend can correctly locate and display artistic styles.

---

## 1. Directory Overview

All assets must be stored within the `prompt-management-system` S3 bucket using the following directory structure:

```text
prompt-management-system/
├── categories/
│   └── thumbnails/          # Cover images for Category groups
├── styles/
│   └── thumbnails/          # Preview cards for individual AI Styles
└── challenges/
    └── targets/             # Reference images for Mystery Prompt Challenges
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

## 4. Challenge Assets (Mystery Prompt)

Challenges are time-limited events where users try to match a target image.

### **S3 Storage Rule**
*   **Path:** `challenges/targets/`
*   **Filename:** Use a descriptive name based on the **Challenge Name**.
*   **Format:** Highest quality possible for best AI similarity scoring (`.jpg` or `.png`).

| Field | Example Value | Resulting S3 Key |
| :--- | :--- | :--- |
| Name | "Ghibli Mastery" | — |
| Slug | `ghibli-mastery` | `challenges/targets/ghibli-mastery.jpg` |

### **Database Entry**
The `target_image_url` column in the `challenges` table must contain the full public HTTPS URL.

---

## 5. Admin API Workflow (New)

Admins should now use the **Admin API endpoints** instead of manual database pushes to ensure data integrity and automatic S3 cleanup:

1.  **Categories**: Use `POST /api/admin/categories` to handle the data and upload in one go.
2.  **Styles**: Use `POST /api/admin/styles` — ensure your `prompt_template` is clear and include a `negative_prompt` to avoid common AI glitches.
3.  **Challenges**: Use `POST /api/admin/challenges` to set up new Mystery Prompts. Remember to set the duration (default: 1 day).

---

## 6. Technical Specification

| Environment Variable | Recommended Value |
| :--- | :--- |
| **Max Image Size** | 2MB (for fast UI loading) |
| **Dimensions (Category)** | 800 x 400 px (Landscape) |
| **Dimensions (Style)** | 600 x 600 px or 600 x 800 px |
| **Mime Types** | `image/jpeg`, `image/png`, `image/webp` |
