-- ============================================================
-- MagicPic Sample Data
-- ============================================================
-- This script inserts sample data to get started
-- Run this AFTER database_schema.sql
-- ============================================================

-- ============================================================
-- SAMPLE CATEGORIES
-- ============================================================

INSERT INTO categories (name, slug, icon, description, display_order) VALUES
('Artistic', 'artistic', '🎨', 'Creative and artistic transformations', 1),
('Wedding', 'wedding', '💒', 'Wedding invitations and romantic styles', 2),
('Education', 'education', '📚', 'Educational illustrations and diagrams', 3),
('Professional', 'professional', '💼', 'Professional headshots and portraits', 4),
('Fun & Creative', 'fun-creative', '🎭', 'Fun and creative transformations', 5);

-- ============================================================
-- SAMPLE STYLES
-- ============================================================

-- Artistic Styles
INSERT INTO styles (category_id, name, description, preview_url, prompt_template, negative_prompt, tags, display_order, is_trending) VALUES
(
    1,
    'Studio Ghibli Art',
    'Transform into whimsical anime art style inspired by Studio Ghibli films',
    'https://placeholder-url.com/ghibli-preview.jpg',
    'Transform this image into Studio Ghibli anime art style. Use soft pastel colors, dreamy atmosphere, and painterly textures characteristic of Hayao Miyazaki films. Maintain the subject''s key features while applying the whimsical, hand-drawn aesthetic. Create gentle, nostalgic mood with soft lighting.',
    'Avoid: harsh lines, photorealistic details, dark themes, violence',
    '["anime", "ghibli", "artistic", "whimsical", "painterly", "pastel"]'::json,
    1,
    true
),
(
    1,
    'Watercolor Portrait',
    'Convert photo into elegant watercolor painting with flowing colors',
    'https://placeholder-url.com/watercolor-preview.jpg',
    'Convert this photograph into a beautiful watercolor painting. Use flowing, translucent colors with visible brush strokes and paper texture. Apply soft edges and color bleeding effects typical of watercolor medium. Create artistic interpretation while preserving recognizable features.',
    'Avoid: harsh lines, digital appearance, photorealistic details, over-saturation',
    '["watercolor", "painting", "artistic", "elegant", "soft"]'::json,
    2,
    true
),
(
    1,
    'Oil Painting - Renaissance',
    'Transform into classical oil painting similar to Renaissance masters',
    'https://placeholder-url.com/oil-preview.jpg',
    'Render this image as a classical Renaissance oil painting in the style of Leonardo da Vinci or Raphael. Use rich, deep colors with dramatic chiaroscuro lighting. Apply visible brushwork and canvas texture. Create timeless, dignified composition with classical beauty.',
    'Avoid: modern elements, bright neon colors, cartoon style',
    '["oil painting", "renaissance", "classical", "dramatic", "baroque"]'::json,
    3,
    false
),
(
    1,
    'Modern Anime Character',
    'Convert person into modern anime/manga character',
    'https://placeholder-url.com/anime-preview.jpg',
    'Convert the person in this image into a modern anime character. Use large expressive eyes, vibrant hair colors, smooth cel-shaded coloring, and clean line art. Apply typical anime facial proportions and features. Use bright, saturated color palette.',
    'Avoid: realistic proportions, Western cartoon style, 3D rendering, dull colors',
    '["anime", "manga", "character design", "vibrant", "modern"]'::json,
    4,
    true
),
(
    1,
    'Cyberpunk Neon',
    'Transform into futuristic cyberpunk style with neon lights',
    'https://placeholder-url.com/cyberpunk-preview.jpg',
    'Transform this image into cyberpunk futuristic style. Apply neon lighting effects in pink, blue, and purple. Add holographic elements and tech augmentations. Create dark, moody atmosphere with dramatic neon contrasts. Use rain-slicked surfaces and urban night setting aesthetic.',
    'Avoid: bright daylight, natural colors, rural settings, vintage aesthetics',
    '["cyberpunk", "neon", "futuristic", "sci-fi", "tech", "dark"]'::json,
    5,
    false
);

-- Wedding Styles
INSERT INTO styles (category_id, name, description, preview_url, prompt_template, tags, display_order) VALUES
(
    2,
    'Elegant Wedding Card',
    'Transform into elegant wedding invitation card design',
    'https://placeholder-url.com/wedding-preview.jpg',
    'Transform this image into an elegant wedding invitation card design. Frame the photo with beautiful floral borders, delicate patterns, and ornate decorative elements. Use soft romantic colors like blush pink, cream, and gold. Create sophisticated, timeless design suitable for formal wedding invitations.',
    '["wedding", "invitation", "romantic", "elegant", "floral", "formal"]'::json,
    1
),
(
    2,
    'Romantic Portrait',
    'Create romantic dreamy portrait perfect for couples',
    'https://placeholder-url.com/romantic-preview.jpg',
    'Create a romantic, dreamy portrait from this image. Use soft focus, warm golden tones, and gentle lighting. Add subtle bokeh effects and romantic atmosphere. Perfect for couples and engagement photos. Use pastel colors and ethereal aesthetic.',
    '["romantic", "couple", "dreamy", "soft", "bokeh", "warm"]'::json,
    2
);

-- Education Styles
INSERT INTO styles (category_id, name, description, preview_url, prompt_template, tags, display_order) VALUES
(
    3,
    'Textbook Illustration',
    'Convert into clear, educational illustration style',
    'https://placeholder-url.com/textbook-preview.jpg',
    'Convert this image into a clear, educational illustration suitable for textbooks. Use clean lines, simplified forms, and clear labeling aesthetic. Apply flat colors with subtle shading for depth. Remove background distractions and focus on the main subject.',
    '["educational", "illustration", "textbook", "clear", "simplified"]'::json,
    1
),
(
    3,
    'Diagram Sketch',
    'Transform into technical diagram or sketch style',
    'https://placeholder-url.com/diagram-preview.jpg',
    'Transform this image into a technical diagram or educational sketch. Use clean line art, labels, and annotations. Apply simple monochrome or limited color palette. Focus on clarity and educational value.',
    '["diagram", "sketch", "technical", "educational", "line art"]'::json,
    2
);

-- Professional Styles
INSERT INTO styles (category_id, name, description, preview_url, prompt_template, tags, display_order) VALUES
(
    4,
    'Professional Headshot',
    'Enhance into professional business headshot',
    'https://placeholder-url.com/headshot-preview.jpg',
    'Enhance this image into a professional business headshot. Use clean, professional lighting with subtle retouching. Apply neutral background (gray or white). Ensure sharp focus on face with professional, approachable expression. Suitable for LinkedIn and corporate profiles.',
    '["professional", "headshot", "business", "corporate", "clean"]'::json,
    1
);

-- Fun & Creative Styles
INSERT INTO styles (category_id, name, description, preview_url, prompt_template, tags, display_order) VALUES
(
    5,
    'Vintage Polaroid',
    'Transform into nostalgic vintage polaroid photograph',
    'https://placeholder-url.com/polaroid-preview.jpg',
    'Transform this image into a vintage polaroid photograph from the 1970s-80s. Apply characteristic polaroid border, slightly faded colors with warm yellow-orange tint, subtle light leaks, and soft focus. Add slight grain and vignetting. Create nostalgic, retro aesthetic.',
    '["vintage", "polaroid", "retro", "nostalgic", "70s", "film"]'::json,
    1
),
(
    5,
    'Pop Art Style',
    'Transform into vibrant pop art like Andy Warhol',
    'https://placeholder-url.com/popart-preview.jpg',
    'Transform this image into vibrant pop art style similar to Andy Warhol. Use bold, saturated colors, high contrast, and graphic design elements. Apply halftone dots and screen print aesthetic. Create striking, contemporary art piece with vibrant color blocking.',
    '["pop art", "warhol", "vibrant", "graphic", "bold", "contemporary"]'::json,
    2
);

-- ============================================================
-- SAMPLE USER (for testing)
-- ============================================================
-- Password: "Test123456" (hashed with bcrypt)
-- Note: You should use your actual password hashing in production

INSERT INTO users (email, hashed_password, name, phone, referral_code, credits, is_verified) VALUES
(
    'demo@magicpic.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5F1yPtszHqVCi', -- "Test123456"
    'Demo User',
    '+919999999999',
    'DEMO1234',
    2500,
    true
);

-- Log the signup bonus transaction
INSERT INTO credit_transactions (user_id, amount, type, description, balance_after) VALUES
(1, 2500, 'signup_bonus', 'Welcome bonus for new account', 2500);

-- ============================================================
-- COMPLETED!
-- ============================================================
-- Sample data inserted successfully
-- You can now test the application with:
--   Email: demo@magicpic.com
--   Password: Test123456
-- ============================================================

SELECT 
    'Database setup complete!' as status,
    (SELECT COUNT(*) FROM categories) as categories_count,
    (SELECT COUNT(*) FROM styles) as styles_count,
    (SELECT COUNT(*) FROM users) as users_count;
