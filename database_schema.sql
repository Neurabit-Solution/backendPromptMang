-- ============================================================
-- MagicPic Database Schema
-- PostgreSQL 16
-- ============================================================
-- This script creates all necessary tables for the MagicPic application
-- Run this after creating the database
-- ============================================================

-- Drop existing tables (if any) in correct order due to foreign keys
DROP TABLE IF EXISTS ad_watches CASCADE;
DROP TABLE IF EXISTS credit_transactions CASCADE;
DROP TABLE IF EXISTS likes CASCADE;
DROP TABLE IF EXISTS votes CASCADE;
DROP TABLE IF EXISTS battles CASCADE;
DROP TABLE IF EXISTS creations CASCADE;
DROP TABLE IF EXISTS styles CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================================
-- 1. USERS TABLE
-- ============================================================
-- Stores user accounts, authentication, and credits

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    avatar_url VARCHAR(500),
    credits INTEGER DEFAULT 2500 CHECK (credits >= 0),
    referral_code VARCHAR(10) UNIQUE NOT NULL,
    referred_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for users table
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_referral_code ON users(referral_code);
CREATE INDEX idx_users_referred_by ON users(referred_by_id);

COMMENT ON TABLE users IS 'User accounts with authentication and credit balance';
COMMENT ON COLUMN users.credits IS 'Available credits for image generation (default 2500 on signup)';
COMMENT ON COLUMN users.referral_code IS 'Unique referral code for this user to share';
COMMENT ON COLUMN users.referred_by_id IS 'ID of user who referred them (earns referral bonus)';

-- ============================================================
-- 2. CATEGORIES TABLE
-- ============================================================
-- Style categories (Wedding, Education, Artistic, etc.)

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    icon VARCHAR(10) NOT NULL,
    description VARCHAR(200) NOT NULL,
    preview_url VARCHAR(500),
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_categories_slug ON categories(slug);
CREATE INDEX idx_categories_display_order ON categories(display_order);

COMMENT ON TABLE categories IS 'Style categories for organizing different AI styles';
COMMENT ON COLUMN categories.slug IS 'URL-friendly version of name (e.g., "wedding", "education")';
COMMENT ON COLUMN categories.icon IS 'Emoji icon for display (e.g., "💒", "📚")';

-- ============================================================
-- 3. STYLES TABLE
-- ============================================================
-- AI transformation styles with prompt templates

CREATE TABLE styles (
    id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500) NOT NULL,
    preview_url VARCHAR(500) NOT NULL,
    prompt_template TEXT NOT NULL,
    negative_prompt TEXT,
    tags JSON DEFAULT '[]',
    credits_required INTEGER DEFAULT 50,
    uses_count INTEGER DEFAULT 0 CHECK (uses_count >= 0),
    is_trending BOOLEAN DEFAULT FALSE,
    is_new BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_styles_category_id ON styles(category_id);
CREATE INDEX idx_styles_name ON styles(name);
CREATE INDEX idx_styles_is_trending ON styles(is_trending);
CREATE INDEX idx_styles_is_active ON styles(is_active);

COMMENT ON TABLE styles IS 'AI transformation styles with prompt templates for Gemini';
COMMENT ON COLUMN styles.prompt_template IS 'Base AI prompt template (combined with user options)';
COMMENT ON COLUMN styles.negative_prompt IS 'What to avoid in generation';
COMMENT ON COLUMN styles.tags IS 'JSON array of search tags';
COMMENT ON COLUMN styles.uses_count IS 'Number of times this style has been used (for trending)';

-- ============================================================
-- 4. CREATIONS TABLE
-- ============================================================
-- AI-generated images with metadata

CREATE TABLE creations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    style_id INTEGER NOT NULL REFERENCES styles(id) ON DELETE CASCADE,
    
    -- Image URLs
    original_image_url VARCHAR(500) NOT NULL,
    generated_image_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500) NOT NULL,
    
    -- Generation options
    mood VARCHAR(50),
    weather VARCHAR(50),
    dress_style VARCHAR(50),
    custom_prompt VARCHAR(200),
    
    -- Prompt storage
    prompt_used TEXT NOT NULL,
    
    -- Metadata
    credits_used INTEGER DEFAULT 50,
    processing_time FLOAT,
    
    -- Stats
    likes_count INTEGER DEFAULT 0 CHECK (likes_count >= 0),
    views_count INTEGER DEFAULT 0 CHECK (views_count >= 0),
    
    -- Status
    is_public BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_creations_user_id ON creations(user_id);
CREATE INDEX idx_creations_style_id ON creations(style_id);
CREATE INDEX idx_creations_is_public ON creations(is_public);
CREATE INDEX idx_creations_created_at ON creations(created_at DESC);
CREATE INDEX idx_creations_likes_count ON creations(likes_count DESC);

COMMENT ON TABLE creations IS 'AI-generated images created by users';
COMMENT ON COLUMN creations.prompt_used IS 'Complete final prompt sent to Gemini AI (for audit)';
COMMENT ON COLUMN creations.mood IS 'Optional: happy, sad, romantic, dramatic, peaceful';
COMMENT ON COLUMN creations.weather IS 'Optional: sunny, rainy, snowy, cloudy, night';
COMMENT ON COLUMN creations.dress_style IS 'Optional: casual, formal, traditional, fantasy';

-- ============================================================
-- 5. BATTLES TABLE
-- ============================================================
-- Style battles for voting/gamification

CREATE TABLE battles (
    id SERIAL PRIMARY KEY,
    creation_a_id INTEGER NOT NULL REFERENCES creations(id) ON DELETE CASCADE,
    creation_b_id INTEGER NOT NULL REFERENCES creations(id) ON DELETE CASCADE,
    
    votes_a INTEGER DEFAULT 0 CHECK (votes_a >= 0),
    votes_b INTEGER DEFAULT 0 CHECK (votes_b >= 0),
    
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'completed')),
    winner_id INTEGER REFERENCES creations(id) ON DELETE SET NULL,
    
    starts_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ends_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT different_creations CHECK (creation_a_id != creation_b_id)
);

CREATE INDEX idx_battles_status ON battles(status);
CREATE INDEX idx_battles_ends_at ON battles(ends_at);
CREATE INDEX idx_battles_creation_a ON battles(creation_a_id);
CREATE INDEX idx_battles_creation_b ON battles(creation_b_id);

COMMENT ON TABLE battles IS 'Style battles where users vote between two creations';
COMMENT ON COLUMN battles.status IS 'pending (scheduled), active (voting open), completed (ended)';
COMMENT ON COLUMN battles.winner_id IS 'ID of winning creation (set when battle ends)';

-- ============================================================
-- 6. VOTES TABLE
-- ============================================================
-- User votes in battles

CREATE TABLE votes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    battle_id INTEGER NOT NULL REFERENCES battles(id) ON DELETE CASCADE,
    voted_for_id INTEGER NOT NULL REFERENCES creations(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_user_battle_vote UNIQUE (user_id, battle_id)
);

CREATE INDEX idx_votes_user_id ON votes(user_id);
CREATE INDEX idx_votes_battle_id ON votes(battle_id);
CREATE INDEX idx_votes_voted_for_id ON votes(voted_for_id);

COMMENT ON TABLE votes IS 'User votes in battles (one vote per user per battle)';
COMMENT ON COLUMN votes.voted_for_id IS 'ID of creation the user voted for';

-- ============================================================
-- 7. LIKES TABLE
-- ============================================================
-- User likes on creations

CREATE TABLE likes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    creation_id INTEGER NOT NULL REFERENCES creations(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_user_creation_like UNIQUE (user_id, creation_id)
);

CREATE INDEX idx_likes_user_id ON likes(user_id);
CREATE INDEX idx_likes_creation_id ON likes(creation_id);

COMMENT ON TABLE likes IS 'User likes on creations (similar to Instagram hearts)';

-- ============================================================
-- 8. CREDIT_TRANSACTIONS TABLE
-- ============================================================
-- Complete audit log of all credit changes

CREATE TABLE credit_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN (
        'signup_bonus', 'ad_watch', 'purchase', 'creation', 
        'referral', 'battle_win', 'admin_adjustment'
    )),
    description VARCHAR(200) NOT NULL,
    reference_id VARCHAR(100),
    balance_after INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_credit_transactions_user_id ON credit_transactions(user_id);
CREATE INDEX idx_credit_transactions_type ON credit_transactions(type);
CREATE INDEX idx_credit_transactions_created_at ON credit_transactions(created_at DESC);

COMMENT ON TABLE credit_transactions IS 'Audit log of all credit earnings and expenses';
COMMENT ON COLUMN credit_transactions.amount IS 'Positive = earned, Negative = spent';
COMMENT ON COLUMN credit_transactions.type IS 'Type of transaction (signup_bonus, ad_watch, etc.)';
COMMENT ON COLUMN credit_transactions.reference_id IS 'Related entity ID (creation_id, battle_id, etc.)';
COMMENT ON COLUMN credit_transactions.balance_after IS 'User balance after this transaction';

-- ============================================================
-- 9. AD_WATCHES TABLE
-- ============================================================
-- Track ad viewing for daily limit enforcement

CREATE TABLE ad_watches (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ad_provider VARCHAR(50) NOT NULL,
    ad_unit_id VARCHAR(100) NOT NULL,
    credits_earned INTEGER DEFAULT 50,
    watched_date DATE NOT NULL DEFAULT CURRENT_DATE,
    watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ad_watches_user_watched_date ON ad_watches(user_id, watched_date);
CREATE INDEX idx_ad_watches_user_id ON ad_watches(user_id);

COMMENT ON TABLE ad_watches IS 'Track ad viewing to enforce daily limits (5 ads/day)';
COMMENT ON COLUMN ad_watches.watched_date IS 'Date only (for daily limit checking)';
COMMENT ON COLUMN ad_watches.watched_at IS 'Exact timestamp of ad watch';

-- ============================================================
-- TRIGGER: Auto-update updated_at timestamp
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_styles_updated_at
    BEFORE UPDATE ON styles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- COMPLETED!
-- ============================================================
-- All tables created successfully
-- Next step: Insert sample data (see sample_data.sql)
-- ============================================================

