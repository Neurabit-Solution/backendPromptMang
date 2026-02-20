# API Curl Commands

Here are the curl commands to test the public endpoints for Styles and Categories.

## Base URLs
- **Local:** `http://localhost:8000`
- **Deployed:** `http://35.154.148.0:8000`

---

## 1. Get All Styles
Fetches a list of all available styles with their image proxy URLs.

**Local:**
```bash
curl http://localhost:8000/api/styles
```

**Deployed:**
```bash
curl http://35.154.148.0:8000/api/styles
```

---

## 2. Get Trending Styles
Fetches the top trending styles (e.g., for the "Hot Right Now" section).

**Local:**
```bash
curl http://localhost:8000/api/styles/trending
```

**Deployed:**
```bash
curl http://35.154.148.0:8000/api/styles/trending
```

---

## 3. Get All Categories
Fetches all style categories (e.g., Anime, Realistic, 3D) with their cover images.

**Local:**
```bash
curl http://localhost:8000/api/categories
```

**Deployed:**
```bash
curl http://35.154.148.0:8000/api/categories
```
