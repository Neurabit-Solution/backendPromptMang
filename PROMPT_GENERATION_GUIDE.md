# AI Prompt Generation & Storage Guide

This document explains how AI prompts are created, combined, and stored for image generation in MagicPic.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Where Prompts Are Stored](#where-prompts-are-stored)
3. [Prompt Template Structure](#prompt-template-structure)
4. [Prompt Generation Process](#prompt-generation-process)
5. [Example Styles & Prompts](#example-styles--prompts)
6. [Database Schema](#database-schema)
7. [Implementation](#implementation)
8. [Best Practices](#best-practices)

---

## Overview

The AI prompt generation system uses a **template-based approach** where:

1. **Admin/Developer** creates base prompt templates for each style
2. **User** selects optional parameters (mood, weather, dress style, custom text)
3. **System** combines template + user inputs → final prompt
4. **Gemini AI** receives the final prompt and generates the image
5. **Database** saves both the template and the final used prompt for audit/debugging

---

## Where Prompts Are Stored

### Primary Storage: `styles` Table

All base prompt templates are stored in the **`styles` table** in PostgreSQL.

```
┌─────────────────────────────────────────────────────────┐
│                    STYLES TABLE                         │
├─────────────────────────────────────────────────────────┤
│ id  │ name          │ prompt_template                   │
├─────┼───────────────┼───────────────────────────────────┤
│ 1   │ Ghibli Art    │ Transform this image into...      │
│ 2   │ Watercolor    │ Convert this photo into...        │
│ 3   │ Oil Painting  │ Render this image as a...         │
│ 4   │ Anime Style   │ Convert person in image to...     │
└─────┴───────────────┴───────────────────────────────────┘
```

**Key Fields:**
- `prompt_template` (TEXT, 2000 chars max) - Base AI instruction
- `negative_prompt` (TEXT, 1000 chars max, nullable) - What to avoid
- `tags` (JSON array) - Keywords for search/discovery

### Secondary Storage: `creations` Table

When an image is generated, the **final combined prompt** is saved in the **`creations` table**.

```
┌────────────────────────────────────────────────────────────┐
│                   CREATIONS TABLE                          │
├────────────────────────────────────────────────────────────┤
│ id  │ style_id │ prompt_used                               │
├─────┼──────────┼───────────────────────────────────────────┤
│ 100 │ 1        │ Transform this image into Studio Ghibli...│
│ 101 │ 2        │ Convert this photo into watercolor art... │
└─────┴──────────┴───────────────────────────────────────────┘
```

**Why Save Both?**
- **`styles.prompt_template`** - Reusable base template (1 for all)
- **`creations.prompt_used`** - Exact prompt sent to AI (1 per generation)
  - Debugging failed generations
  - Understanding what worked well
  - Legal/compliance audit trail
  - Reproducing results

---

## Prompt Template Structure

### Basic Template Format

Each style has a carefully crafted prompt template optimized for Gemini AI.

**Template Components:**

```
[Base Instruction] + [Style Details] + [Quality Parameters] + [Safety Guards]
```

**Example - Ghibli Art Style:**

```text
Transform this image into Studio Ghibli anime art style. 
Use soft pastel colors, dreamy atmosphere, and painterly textures 
characteristic of Hayao Miyazaki films. Maintain the subject's 
key features while applying the whimsical, hand-drawn aesthetic. 
Use soft lighting and a gentle, nostalgic mood.
```

### Advanced Template with Variables

Templates can include **placeholder variables** that get replaced with user selections:

```text
Transform this image into {STYLE_NAME} style with {MOOD} mood 
and {WEATHER} atmosphere. Apply {DRESS_STYLE} clothing aesthetic 
if featuring people. {CUSTOM_PROMPT}
```

### Negative Prompts (Optional)

What to **avoid** in generation:

```text
Avoid: distorted faces, extra limbs, blurry quality, watermarks, 
text overlays, oversaturation, cartoon proportions
```

---

## Prompt Generation Process

### Step-by-Step Flow

```
┌────────────────────────────────────────────────────────────────┐
│  1. USER INITIATES GENERATION                                  │
│     - Uploads photo (selfie.jpg)                               │
│     - Selects style (Ghibli Art)                              │
│     - Chooses optional params:                                 │
│       • mood = "happy"                                         │
│       • weather = "sunny"                                      │
│       • dress_style = "casual"                                 │
│       • custom_prompt = "add cherry blossoms in background"    │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│  2. BACKEND RETRIEVES STYLE TEMPLATE                           │
│     Query: SELECT prompt_template, negative_prompt             │
│            FROM styles WHERE id = 1                            │
│                                                                 │
│     Result:                                                     │
│     prompt_template = "Transform this image into Studio        │
│                        Ghibli anime art style..."              │
│     negative_prompt = "Avoid distorted faces, extra limbs..."  │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│  3. SYSTEM BUILDS FINAL PROMPT                                 │
│     Base Template:                                              │
│       "Transform this image into Studio Ghibli anime art       │
│        style. Use soft pastel colors, dreamy atmosphere..."    │
│                                                                 │
│     + User Parameters:                                          │
│       "Apply a happy mood with bright expressions."            │
│       "Set the scene in sunny daytime lighting."               │
│       "Use casual clothing style for the person."              │
│       "Add cherry blossoms in the background."                 │
│                                                                 │
│     + Quality Enhancers:                                        │
│       "High quality, detailed, professional artwork."          │
│                                                                 │
│     + Safety Instructions:                                      │
│       "Maintain appropriate content, avoid nudity or violence."│
│                                                                 │
│     FINAL PROMPT:                                               │
│     "Transform this image into Studio Ghibli anime art style.  │
│      Use soft pastel colors, dreamy atmosphere, and painterly  │
│      textures characteristic of Hayao Miyazaki films. Apply a  │
│      happy mood with bright expressions. Set the scene in      │
│      sunny daytime lighting. Use casual clothing style for     │
│      the person. Add cherry blossoms in the background.        │
│      Maintain the subject's key features while applying the    │
│      whimsical, hand-drawn aesthetic. High quality, detailed,  │
│      professional artwork. Maintain appropriate content."      │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│  4. SEND TO GEMINI AI                                          │
│     API Call:                                                   │
│       gemini.generateContent({                                 │
│         contents: [                                             │
│           { text: FINAL_PROMPT },                              │
│           { inline_data: { mime_type: "image/jpeg",            │
│                            data: base64_image } }              │
│         ]                                                       │
│       })                                                        │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│  5. SAVE TO DATABASE                                           │
│     INSERT INTO creations (                                     │
│       user_id, style_id,                                        │
│       prompt_used,     ← SAVE THE COMPLETE FINAL PROMPT       │
│       mood, weather, dress_style, custom_prompt,               │
│       original_image_url, generated_image_url,                 │
│       ...                                                       │
│     ) VALUES (...)                                             │
└────────────────────────────────────────────────────────────────┘
```

---

## Example Styles & Prompts

### 1. Studio Ghibli Art Style

**Category**: Artistic

**Database Record:**
```sql
INSERT INTO styles (category_id, name, description, prompt_template, tags, credits_required)
VALUES (
  3, -- Artistic category
  'Studio Ghibli Art',
  'Transform into whimsical anime art style inspired by Studio Ghibli films',
  'Transform this image into Studio Ghibli anime art style. Use soft pastel colors, dreamy atmosphere, and painterly textures characteristic of Hayao Miyazaki films. Maintain the subject''s key features while applying the whimsical, hand-drawn aesthetic. Create gentle, nostalgic mood with soft lighting and natural outdoor settings when possible.',
  '["anime", "ghibli", "artistic", "whimsical", "painterly", "pastel"]'::json,
  50
);
```

**When User Generates:**
```
User Input:
- Photo: portrait.jpg
- Style: Studio Ghibli Art
- Mood: happy
- Weather: sunny
- Custom: "add flying birds"

Final Prompt Sent to Gemini:
"Transform this image into Studio Ghibli anime art style. Use soft pastel 
colors, dreamy atmosphere, and painterly textures characteristic of Hayao 
Miyazaki films. Apply a happy, joyful mood with bright expressions. Set 
the scene in sunny daytime with warm natural lighting. Add flying birds. 
Maintain the subject's key features while applying the whimsical, hand-drawn 
aesthetic. High quality, detailed artwork."
```

---

### 2. Professional Watercolor Portrait

**Category**: Artistic

**Database Record:**
```sql
INSERT INTO styles (category_id, name, description, prompt_template, negative_prompt, tags)
VALUES (
  3,
  'Watercolor Portrait',
  'Convert photo into elegant watercolor painting with flowing colors',
  'Convert this photograph into a beautiful watercolor painting. Use flowing, translucent colors with visible brush strokes and paper texture. Apply soft edges and color bleeding effects typical of watercolor medium. Create artistic interpretation while preserving recognizable features. Use elegant color palette.',
  'Avoid: harsh lines, digital appearance, photorealistic details, over-saturation, muddy colors',
  '["watercolor", "painting", "artistic", "elegant", "soft"]'::json
);
```

**Final Prompt Example:**
```
"Convert this photograph into a beautiful watercolor painting. Use flowing, 
translucent colors with visible brush strokes and paper texture. Apply a 
romantic mood with gentle expressions. Set in cloudy weather with diffused, 
soft lighting. Use formal clothing style. Apply soft edges and color bleeding 
effects typical of watercolor medium. Create artistic interpretation while 
preserving recognizable features. Use elegant color palette."

Negative: "Avoid harsh lines, digital appearance, photorealistic details, 
over-saturation, muddy colors."
```

---

### 3. Oil Painting - Renaissance Style

**Category**: Artistic

**Database Record:**
```sql
INSERT INTO styles (category_id, name, description, prompt_template, tags)
VALUES (
  3,
  'Renaissance Oil Painting',
  'Transform into classical oil painting similar to Renaissance masters',
  'Render this image as a classical Renaissance oil painting in the style of Leonardo da Vinci or Raphael. Use rich, deep colors with dramatic chiaroscuro lighting. Apply visible brushwork and canvas texture. Create timeless, dignified composition with attention to anatomical accuracy and classical beauty. Use golden hour lighting and baroque aesthetic.',
  '["oil painting", "renaissance", "classical", "dramatic", "baroque"]'::json
);
```

---

### 4. Anime Character Style

**Category**: Artistic

**Database Record:**
```sql
INSERT INTO styles (category_id, name, description, prompt_template, negative_prompt, tags)
VALUES (
  3,
  'Modern Anime Character',
  'Convert person into modern anime/manga character with big eyes and vibrant colors',
  'Convert the person in this image into a modern anime character. Use large expressive eyes, vibrant hair colors, smooth cel-shaded coloring, and clean line art. Apply typical anime facial proportions and features. Create dynamic pose if possible. Use bright, saturated color palette.',
  'Avoid: realistic proportions, Western cartoon style, 3D rendering, dull colors',
  '["anime", "manga", "character design", "vibrant", "modern"]'::json
);
```

---

### 5. Wedding Invitation Card Style

**Category**: Wedding

**Database Record:**
```sql
INSERT INTO styles (category_id, name, description, prompt_template, tags)
VALUES (
  1, -- Wedding category
  'Elegant Wedding Card',
  'Transform into elegant wedding invitation card design with floral borders',
  'Transform this image into an elegant wedding invitation card design. Frame the photo with beautiful floral borders, delicate patterns, and ornate decorative elements. Use soft romantic colors like blush pink, cream, and gold. Add subtle vignette effect. Create sophisticated, timeless design suitable for formal wedding invitations. Apply dreamy, romantic aesthetic.',
  '["wedding", "invitation", "romantic", "elegant", "floral", "formal"]'::json
);
```

**Final Prompt with User Input:**
```
"Transform this image into an elegant wedding invitation card design. Frame 
the photo with beautiful floral borders, delicate patterns, and ornate 
decorative elements. Apply romantic mood with soft, loving expressions. Set 
in evening golden hour lighting. Use formal traditional clothing style. Use 
soft romantic colors like blush pink, cream, and gold. Add roses and jasmine 
flowers in the border. Add subtle vignette effect. Create sophisticated, 
timeless design suitable for formal wedding invitations."
```

---

### 6. Educational Textbook Illustration

**Category**: Education

**Database Record:**
```sql
INSERT INTO styles (category_id, name, description, prompt_template, tags)
VALUES (
  2, -- Education category
  'Textbook Illustration',
  'Convert into clear, educational illustration style for textbooks',
  'Convert this image into a clear, educational illustration suitable for textbooks. Use clean lines, simplified forms, and clear labeling aesthetic. Apply flat colors with subtle shading for depth. Remove background distractions and focus on the main subject. Create informative, easy-to-understand visual that works well in print.',
  '["educational", "illustration", "textbook", "clear", "simplified"]'::json
);
```

---

### 7. Cyberpunk Neon Style

**Category**: Artistic

**Database Record:**
```sql
INSERT INTO styles (category_id, name, description, prompt_template, negative_prompt, tags)
VALUES (
  3,
  'Cyberpunk Neon',
  'Transform into futuristic cyberpunk style with neon lights and tech aesthetics',
  'Transform this image into cyberpunk futuristic style. Apply neon lighting effects in pink, blue, and purple. Add holographic elements, digital glitches, and tech augmentations. Create dark, moody atmosphere with dramatic neon contrasts. Use rain-slicked surfaces and urban night setting aesthetic. Apply sci-fi, dystopian visual elements.',
  'Avoid: bright daylight, natural colors, rural settings, vintage aesthetics',
  '["cyberpunk", "neon", "futuristic", "sci-fi", "tech", "dark"]'::json
);
```

---

### 8. Vintage Polaroid Photo

**Category**: Artistic

**Database Record:**
```sql
INSERT INTO styles (category_id, name, description, prompt_template, tags)
VALUES (
  3,
  'Vintage Polaroid',
  'Transform into nostalgic vintage polaroid photograph from the 1970s',
  'Transform this image into a vintage polaroid photograph from the 1970s-80s. Apply characteristic polaroid border, slightly faded colors with warm yellow-orange tint, subtle light leaks, and soft focus. Add slight grain and vignetting. Create nostalgic, retro aesthetic with that distinctive instant film look.',
  '["vintage", "polaroid", "retro", "nostalgic", "70s", "film"]'::json
);
```

---

## Database Schema

### Complete Schema for Prompt Storage

```sql
-- STYLES TABLE (stores prompt templates)
CREATE TABLE styles (
    id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    
    -- Basic Info
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500) NOT NULL,
    preview_url VARCHAR(500) NOT NULL,
    
    -- PROMPT STORAGE (main focus)
    prompt_template TEXT NOT NULL,          -- Base AI instruction (max 2000 chars)
    negative_prompt TEXT,                   -- What to avoid (max 1000 chars, nullable)
    
    -- Metadata
    tags JSON DEFAULT '[]',                 -- Keywords for search
    credits_required INTEGER DEFAULT 50,
    uses_count INTEGER DEFAULT 0,
    
    -- Status flags
    is_trending BOOLEAN DEFAULT FALSE,
    is_new BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CREATIONS TABLE (stores final used prompts)
CREATE TABLE creations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    style_id INTEGER NOT NULL REFERENCES styles(id),
    
    -- Image URLs
    original_image_url VARCHAR(500) NOT NULL,
    generated_image_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500) NOT NULL,
    
    -- User's generation options
    mood VARCHAR(50),              -- happy, sad, romantic, dramatic, peaceful
    weather VARCHAR(50),           -- sunny, rainy, snowy, cloudy, night
    dress_style VARCHAR(50),       -- casual, formal, traditional, fantasy
    custom_prompt VARCHAR(200),    -- User's additional instructions
    
    -- PROMPT STORAGE (audit trail)
    prompt_used TEXT NOT NULL,     -- COMPLETE final prompt sent to Gemini AI
    
    -- Other metadata
    credits_used INTEGER DEFAULT 50,
    processing_time FLOAT,
    likes_count INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Implementation

### Backend Code Example (Python/FastAPI)

```python
# services/prompt_builder.py

class PromptBuilder:
    """Service to build final AI prompts from templates and user inputs"""
    
    MOOD_INSTRUCTIONS = {
        'happy': 'Apply a happy, joyful mood with bright expressions and cheerful atmosphere.',
        'sad': 'Apply a melancholic mood with somber expressions and subdued atmosphere.',
        'romantic': 'Apply a romantic mood with soft, loving expressions and intimate atmosphere.',
        'dramatic': 'Apply a dramatic mood with intense expressions and powerful atmosphere.',
        'peaceful': 'Apply a peaceful, serene mood with calm expressions and tranquil atmosphere.'
    }
    
    WEATHER_INSTRUCTIONS = {
        'sunny': 'Set the scene in sunny daytime with warm, natural bright lighting.',
        'rainy': 'Set the scene in rainy weather with wet surfaces and moody lighting.',
        'snowy': 'Set the scene in snowy winter setting with cool tones and soft white lighting.',
        'cloudy': 'Set the scene in overcast weather with diffused, soft lighting.',
        'night': 'Set the scene at nighttime with dramatic artificial or moonlight.'
    }
    
    DRESS_STYLE_INSTRUCTIONS = {
        'casual': 'Use casual, everyday clothing style for any people in the image.',
        'formal': 'Use formal, elegant clothing style for any people in the image.',
        'traditional': 'Use traditional cultural clothing style for any people in the image.',
        'fantasy': 'Use fantasy, creative costume design for any people in the image.'
    }
    
    @staticmethod
    def build_prompt(
        style: Style,
        mood: str | None = None,
        weather: str | None = None,
        dress_style: str | None = None,
        custom_prompt: str | None = None
    ) -> str:
        """
        Build final AI prompt by combining template with user inputs
        
        Args:
            style: Style object with prompt_template
            mood: Optional mood selection
            weather: Optional weather setting
            dress_style: Optional dress style
            custom_prompt: Optional custom instructions from user
            
        Returns:
            Complete prompt string ready to send to Gemini AI
        """
        
        # Start with base template
        prompt_parts = [style.prompt_template]
        
        # Add mood if specified
        if mood and mood in PromptBuilder.MOOD_INSTRUCTIONS:
            prompt_parts.append(PromptBuilder.MOOD_INSTRUCTIONS[mood])
        
        # Add weather if specified
        if weather and weather in PromptBuilder.WEATHER_INSTRUCTIONS:
            prompt_parts.append(PromptBuilder.WEATHER_INSTRUCTIONS[weather])
        
        # Add dress style if specified
        if dress_style and dress_style in PromptBuilder.DRESS_STYLE_INSTRUCTIONS:
            prompt_parts.append(PromptBuilder.DRESS_STYLE_INSTRUCTIONS[dress_style])
        
        # Add custom prompt if provided
        if custom_prompt and custom_prompt.strip():
            # Sanitize custom prompt to prevent prompt injection
            sanitized = PromptBuilder._sanitize_custom_prompt(custom_prompt)
            prompt_parts.append(sanitized)
        
        # Add quality enhancers
        prompt_parts.append(
            "High quality, detailed, professional artwork. "
            "Maintain appropriate content suitable for all audiences."
        )
        
        # Join all parts with proper spacing
        final_prompt = " ".join(prompt_parts)
        
        return final_prompt
    
    @staticmethod
    def _sanitize_custom_prompt(text: str) -> str:
        """Sanitize user's custom prompt to prevent abuse"""
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Limit length
        max_length = 200
        if len(text) > max_length:
            text = text[:max_length].rsplit(' ', 1)[0] + '...'
        
        # Remove potentially harmful patterns
        harmful_patterns = [
            'ignore previous instructions',
            'disregard above',
            'forget everything',
            'new instructions:',
            'system:',
            'admin:',
        ]
        
        text_lower = text.lower()
        for pattern in harmful_patterns:
            if pattern in text_lower:
                # Return empty string if malicious pattern detected
                return ""
        
        return text


# api/creations.py
from services.prompt_builder import PromptBuilder
from services.gemini_service import GeminiService
from models import Creation, Style

router = APIRouter()

@router.post("/creations/generate")
async def generate_creation(
    file: UploadFile = File(...),
    style_id: int = Form(...),
    mood: str | None = Form(None),
    weather: str | None = Form(None),
    dress_style: str | None = Form(None),
    custom_prompt: str | None = Form(None),
    is_public: bool = Form(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI-transformed image"""
    
    # 1. Get style from database
    style = db.query(Style).filter(Style.id == style_id).first()
    if not style:
        raise HTTPException(404, "Style not found")
    
    # 2. Check user has enough credits
    if current_user.credits < style.credits_required:
        raise HTTPException(402, "Insufficient credits")
    
    # 3. Upload original image to S3
    original_url = await storage_service.upload(file, f"originals/{current_user.id}")
    
    # 4. Build final prompt using template + user inputs
    final_prompt = PromptBuilder.build_prompt(
        style=style,
        mood=mood,
        weather=weather,
        dress_style=dress_style,
        custom_prompt=custom_prompt
    )
    
    print(f"Final prompt to send to Gemini: {final_prompt}")
    
    # 5. Call Gemini AI with the final prompt
    start_time = time.time()
    generated_image_bytes = await GeminiService.generate_image(
        image_file=file,
        prompt=final_prompt,
        negative_prompt=style.negative_prompt
    )
    processing_time = time.time() - start_time
    
    # 6. Upload generated image to S3
    generated_url = await storage_service.upload_bytes(
        generated_image_bytes, 
        f"generated/{current_user.id}"
    )
    
    # 7. Create thumbnail
    thumbnail_url = await storage_service.create_thumbnail(generated_image_bytes)
    
    # 8. Save creation to database WITH THE COMPLETE PROMPT
    creation = Creation(
        user_id=current_user.id,
        style_id=style.id,
        original_image_url=original_url,
        generated_image_url=generated_url,
        thumbnail_url=thumbnail_url,
        mood=mood,
        weather=weather,
        dress_style=dress_style,
        custom_prompt=custom_prompt,
        prompt_used=final_prompt,  # ← SAVE THE COMPLETE FINAL PROMPT
        credits_used=style.credits_required,
        processing_time=processing_time,
        is_public=is_public
    )
    db.add(creation)
    
    # 9. Deduct credits
    current_user.credits -= style.credits_required
    
    # 10. Log credit transaction
    transaction = CreditTransaction(
        user_id=current_user.id,
        amount=-style.credits_required,
        type='creation',
        description=f'Generated {style.name} image',
        reference_id=str(creation.id),
        balance_after=current_user.credits
    )
    db.add(transaction)
    
    # 11. Update style usage count
    style.uses_count += 1
    
    db.commit()
    db.refresh(creation)
    
    return {
        "success": True,
        "data": {
            "creation": creation,
            "credits_used": style.credits_required,
            "credits_remaining": current_user.credits,
            "processing_time": processing_time
        },
        "message": "Image generated successfully!"
    }
```

---

## Best Practices

### 1. **Template Design**

✅ **DO:**
- Be specific and descriptive
- Include quality indicators ("high quality", "detailed")
- Mention the art medium/style clearly
- Add safety/content guidelines
- Test prompts thoroughly before deploying

❌ **DON'T:**
- Use vague language
- Make templates too long (>2000 chars)
- Include contradictory instructions
- Forget negative prompts for sensitive styles

### 2. **Custom Prompt Handling**

✅ **DO:**
- Sanitize user input
- Limit length (200 chars recommended)
- Check for prompt injection attempts
- Append user prompts at the end (less risky)

❌ **DON'T:**
- Trust user input blindly
- Allow unlimited length
- Let users override safety instructions

### 3. **Storage Strategy**

✅ **DO:**
- Save complete final prompts in `creations.prompt_used`
- Use TEXT fields for prompts (not VARCHAR)
- Index `styles.name` for quick lookup
- Keep prompt templates versioned (future enhancement)

❌ **DON'T:**
- Only save style_id without the full prompt
- Use small VARCHAR fields
- Delete old prompts (keep for audit)

### 4. **Performance Optimization**

✅ **DO:**
- Cache style templates in Redis (read-heavy)
- Preload mood/weather instructions in memory
- Use database indexes on `style_id`
- Batch-load styles for listing pages

❌ **DON'T:**
- Query database for each prompt build
- Build prompts synchronously during API call
- Store huge binary data in prompts

---

## Summary

### Where Prompts Are Stored

| Location | What's Stored | Purpose |
|----------|---------------|---------|
| **`styles.prompt_template`** | Base AI instruction template | Reusable template for all users |
| **`styles.negative_prompt`** | What to avoid | Quality control |
| **`creations.prompt_used`** | Complete final prompt sent to AI | Audit trail, debugging, reproducibility |
| **`creations.custom_prompt`** | User's additional instructions | User customization record |
| **`creations.mood/weather/dress_style`** | User's selections | Generation parameters |

### Prompt Flow

```
Style Template (DB) 
    ↓
+ User Parameters (API request)
    ↓
= Final Prompt (built in memory)
    ↓
→ Gemini AI (API call)
    ↓
→ Save to creations.prompt_used (DB)
```

### Key Takeaways

1. **Templates stored in `styles` table** - One template per style, reusable
2. **Final prompts stored in `creations` table** - One per generation, complete audit trail
3. **Dynamic building** - System combines template + user inputs on-the-fly
4. **Safety first** - Sanitize user inputs, include content guidelines
5. **Extensible** - Easy to add new styles or modify existing ones

This architecture allows maximum flexibility while maintaining control over AI behavior and providing complete traceability of all generations.
