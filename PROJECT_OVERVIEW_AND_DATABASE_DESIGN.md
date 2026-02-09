# MagicPic Project Overview & Database Design

## 📖 Project Overview

**MagicPic** is an AI-powered mobile application that transforms user photos into artistic images using various styles. Think of it as an Instagram meets AI art generator with gamification elements.

### What Does MagicPic Do?

1. **AI Image Transformation**: Users upload their photos and select artistic styles (like "Anime", "Watercolor", "Ghibli Art", etc.) to transform them using Google's Gemini AI
2. **Credit System**: Virtual currency system where users spend credits to generate images and earn credits through ads, referrals, or purchases
3. **Battle System**: Gamified voting where users' creations compete against each other, with winners climbing leaderboards
4. **Social Features**: Users can like, share, and discover other users' creations

### Core User Journeys

```
Journey 1: New User
Signup → Get 2500 Free Credits → Browse Styles → Upload Photo → 
Generate AI Image (costs 50 credits) → Share Creation → Enter Battle

Journey 2: Existing User
Login → Check Credits → Watch Ad (earn 50 credits) → 
Generate Image → Vote in Battles

Journey 3: Voter
Browse Active Battles → Vote for Favorite → 
See Results → Climb Leaderboard
```

### Technology Stack

**Backend:**
- FastAPI (Python web framework)
- PostgreSQL (Database)
- SQLAlchemy/SQLModel (ORM)
- JWT (Authentication)
- Bcrypt (Password hashing)
- Gemini AI API (Image generation)
- Redis (Caching - future)
- Celery (Background tasks - future)

**Storage:**
- S3 / Cloudinary (Image storage)

**Payment:**
- Razorpay (Indian payment gateway)

**Frontend (Mobile):**
- React Native
- Expo

---

## 🗄️ Database Structure

The application requires **9 main tables** to support all features. Below is the complete database schema:

### Entity Relationship Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│     ┌──────────┐                                                │
│     │   User   │ (Central entity)                               │
│     └────┬─────┘                                                │
│          │                                                       │
│    ┌─────┼─────────┬──────────┬────────────┐                   │
│    │     │         │          │            │                    │
│    ▼     ▼         ▼          ▼            ▼                    │
│ ┌────┐ ┌──────┐ ┌─────┐  ┌────────┐  ┌─────────┐              │
│ │Vote│ │Like  │ │AdWat│  │Creation│  │CreditTx │              │
│ └────┘ └──────┘ │ch   │  └───┬────┘  └─────────┘              │
│                  └─────┘      │                                 │
│                               │                                 │
│                          ┌────┴────┐                           │
│                          │         │                            │
│                          ▼         ▼                            │
│                      ┌───────┐  ┌────────┐                     │
│                      │ Style │  │ Battle │                     │
│                      └───┬───┘  └────────┘                     │
│                          │                                      │
│                          ▼                                      │
│                    ┌──────────┐                                │
│                    │ Category │                                │
│                    └──────────┘                                │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📋 Complete Database Tables

### 1. **users** Table (Core User Data)

**Purpose**: Store all user account information, authentication, and credits

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Auto-increment user ID |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEXED | User's email (login credential) |
| `phone` | VARCHAR(20) | UNIQUE, NULLABLE | Phone number (optional) |
| `password_hash` | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| `name` | VARCHAR(100) | NOT NULL | User's full name |
| `avatar_url` | VARCHAR(500) | NULLABLE | Profile picture URL (S3/Cloudinary) |
| `credits` | INTEGER | DEFAULT 2500, >= 0 | Available credits balance |
| `referral_code` | VARCHAR(10) | UNIQUE, NOT NULL | User's unique referral code (auto-generated) |
| `referred_by_id` | INTEGER | FOREIGN KEY → users.id, NULLABLE | ID of user who referred them |
| `is_verified` | BOOLEAN | DEFAULT FALSE | Email verification status |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account active status |
| `last_login` | TIMESTAMP | NULLABLE | Last login timestamp |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Account creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Last profile update |

**Indexes:**
- `idx_email` on `email`
- `idx_referral_code` on `referral_code`

**Sample Data:**
```sql
INSERT INTO users (email, password_hash, name, credits, referral_code)
VALUES ('john@example.com', '$2b$12$...', 'John Doe', 2500, 'JOHN1234');
```

---

### 2. **categories** Table (Style Categories)

**Purpose**: Group styles into categories like "Wedding", "Education", "Artistic"

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Category ID |
| `name` | VARCHAR(100) | UNIQUE, NOT NULL | Category name ("Wedding", "Education") |
| `slug` | VARCHAR(100) | UNIQUE, NOT NULL, INDEXED | URL-friendly name ("wedding", "education") |
| `icon` | VARCHAR(10) | NOT NULL | Emoji icon ("💒", "📚") |
| `description` | VARCHAR(200) | NOT NULL | Short description |
| `preview_url` | VARCHAR(500) | NULLABLE | Category thumbnail image |
| `display_order` | INTEGER | DEFAULT 0 | Sort order for display |
| `is_active` | BOOLEAN | DEFAULT TRUE | Whether category is visible |

**Sample Data:**
```sql
INSERT INTO categories (name, slug, icon, description, display_order)
VALUES 
  ('Wedding', 'wedding', '💒', 'Invitations & Cards', 1),
  ('Education', 'education', '📚', 'Study Materials', 2),
  ('Artistic', 'artistic', '🎨', 'Creative Styles', 3);
```

---

### 3. **styles** Table (AI Transformation Styles)

**Purpose**: Store all available AI styles that users can apply to their photos

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Style ID |
| `category_id` | INTEGER | FOREIGN KEY → categories.id, INDEXED | Parent category |
| `name` | VARCHAR(100) | NOT NULL, INDEXED | Style name ("Ghibli Art", "Watercolor") |
| `description` | VARCHAR(500) | NOT NULL | What this style does |
| `preview_url` | VARCHAR(500) | NOT NULL | Sample image showing this style |
| `prompt_template` | TEXT(2000) | NOT NULL | AI prompt template for Gemini |
| `negative_prompt` | TEXT(1000) | NULLABLE | What to avoid in generation |
| `tags` | JSON | DEFAULT [] | Search tags ["anime", "colorful"] |
| `credits_required` | INTEGER | DEFAULT 50 | Cost to use this style |
| `uses_count` | INTEGER | DEFAULT 0 | How many times used (for trending) |
| `is_trending` | BOOLEAN | DEFAULT FALSE | Manually marked as trending |
| `is_new` | BOOLEAN | DEFAULT FALSE | Marked as new (< 7 days) |
| `is_active` | BOOLEAN | DEFAULT TRUE | Whether available for use |
| `display_order` | INTEGER | DEFAULT 0 | Sort order |
| `created_at` | TIMESTAMP | DEFAULT NOW() | When style was added |

**Indexes:**
- `idx_category_id` on `category_id`
- `idx_name` on `name`
- `idx_is_trending` on `is_trending`

**Sample Data:**
```sql
INSERT INTO styles (category_id, name, description, preview_url, prompt_template, tags)
VALUES (
  3,
  'Ghibli Style',
  'Transform into Studio Ghibli anime art',
  'https://s3.../ghibli-preview.jpg',
  'Transform this image into Studio Ghibli anime art style with soft colors and dreamy atmosphere',
  '["anime", "artistic", "ghibli", "colorful"]'::json
);
```

---

### 4. **creations** Table (Generated Images)

**Purpose**: Store all AI-generated images created by users

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Creation ID |
| `user_id` | INTEGER | FOREIGN KEY → users.id, INDEXED | Who created it |
| `style_id` | INTEGER | FOREIGN KEY → styles.id, INDEXED | Style used |
| `original_image_url` | VARCHAR(500) | NOT NULL | User's uploaded photo |
| `generated_image_url` | VARCHAR(500) | NOT NULL | AI-generated result |
| `thumbnail_url` | VARCHAR(500) | NOT NULL | Small preview (for lists) |
| `mood` | VARCHAR(50) | NULLABLE | Optional: happy, sad, romantic |
| `weather` | VARCHAR(50) | NULLABLE | Optional: sunny, rainy, snowy |
| `dress_style` | VARCHAR(50) | NULLABLE | Optional: casual, formal, traditional |
| `custom_prompt` | VARCHAR(200) | NULLABLE | User's additional instructions |
| `prompt_used` | TEXT(2000) | NOT NULL | Full AI prompt sent to Gemini |
| `credits_used` | INTEGER | DEFAULT 50 | Credits deducted for this |
| `processing_time` | FLOAT | NULLABLE | Generation time in seconds |
| `likes_count` | INTEGER | DEFAULT 0 | Cached like count |
| `views_count` | INTEGER | DEFAULT 0 | How many times viewed |
| `is_public` | BOOLEAN | DEFAULT TRUE | Visible to others |
| `is_featured` | BOOLEAN | DEFAULT FALSE | Editor's pick |
| `is_deleted` | BOOLEAN | DEFAULT FALSE | Soft delete flag |
| `created_at` | TIMESTAMP | DEFAULT NOW() | When generated |

**Indexes:**
- `idx_user_id` on `user_id`
- `idx_style_id` on `style_id`
- `idx_is_public` on `is_public`
- `idx_created_at` on `created_at`

**What Gets Saved:**
1. **Original Image**: User's uploaded photo (stored in S3/Cloudinary)
2. **Generated Image**: AI transformation result (stored in S3/Cloudinary)
3. **Thumbnail**: Smaller version for faster loading
4. **Generation Options**: mood, weather, dress_style chosen by user
5. **Full Prompt**: Complete prompt sent to Gemini AI
6. **Metadata**: Processing time, credits used, view/like counts

**Example Flow:**
```
User uploads selfie.jpg → Upload to S3 → Get URL
User selects "Ghibli Style" + mood="happy" + weather="sunny"
Backend builds prompt: "Transform this selfie into Ghibli art, happy mood, sunny weather"
Send to Gemini AI → Get generated image → Upload to S3
Save all URLs and metadata to 'creations' table
Deduct 50 credits from user
Return generated image to user
```

---

### 5. **battles** Table (Style Battle System)

**Purpose**: Pit two creations against each other for voting

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Battle ID |
| `creation_a_id` | INTEGER | FOREIGN KEY → creations.id, INDEXED | First creation |
| `creation_b_id` | INTEGER | FOREIGN KEY → creations.id, INDEXED | Second creation |
| `votes_a` | INTEGER | DEFAULT 0 | Votes for creation A |
| `votes_b` | INTEGER | DEFAULT 0 | Votes for creation B |
| `status` | VARCHAR(20) | DEFAULT 'pending' | pending, active, completed |
| `winner_id` | INTEGER | FOREIGN KEY → creations.id, NULLABLE | ID of winning creation |
| `starts_at` | TIMESTAMP | DEFAULT NOW() | Battle start time |
| `ends_at` | TIMESTAMP | NOT NULL | Battle end time (e.g., 24 hours later) |
| `created_at` | TIMESTAMP | DEFAULT NOW() | When battle was created |

**Indexes:**
- `idx_status` on `status`
- `idx_ends_at` on `ends_at`

**How Battles Work:**
1. Users can submit their public creations to battle pool
2. System randomly pairs two creations
3. Other users vote for their favorite (1 vote per battle per user)
4. Battle runs for 24 hours (configurable)
5. At `ends_at`, winner is determined by most votes
6. Winner gets bonus credits and leaderboard points

**Sample Battle:**
```sql
INSERT INTO battles (creation_a_id, creation_b_id, status, ends_at)
VALUES (123, 456, 'active', NOW() + INTERVAL '24 hours');
```

---

### 6. **votes** Table (User Votes in Battles)

**Purpose**: Track which user voted for which creation in each battle

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Vote ID |
| `user_id` | INTEGER | FOREIGN KEY → users.id, INDEXED | Who voted |
| `battle_id` | INTEGER | FOREIGN KEY → battles.id, INDEXED | Which battle |
| `voted_for_id` | INTEGER | FOREIGN KEY → creations.id | Which creation they chose |
| `created_at` | TIMESTAMP | DEFAULT NOW() | When they voted |

**Unique Constraint:**
```sql
UNIQUE (user_id, battle_id)  -- One vote per user per battle
```

**Indexes:**
- `idx_user_id` on `user_id`
- `idx_battle_id` on `battle_id`

**Business Rules:**
- Users can only vote once per battle
- Users cannot vote for their own creations
- Votes are final (cannot change vote)

---

### 7. **likes** Table (Creation Likes)

**Purpose**: Track which users liked which creations (like Instagram hearts)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Like ID |
| `user_id` | INTEGER | FOREIGN KEY → users.id, INDEXED | Who liked it |
| `creation_id` | INTEGER | FOREIGN KEY → creations.id, INDEXED | Which creation |
| `created_at` | TIMESTAMP | DEFAULT NOW() | When liked |

**Unique Constraint:**
```sql
UNIQUE (user_id, creation_id)  -- One like per user per creation
```

**Indexes:**
- `idx_user_id` on `user_id`
- `idx_creation_id` on `creation_id`

**Denormalization Note:**
The `creations.likes_count` field is a cached counter. When a like is added/removed:
```sql
-- Add like
INSERT INTO likes (user_id, creation_id) VALUES (1, 100);
UPDATE creations SET likes_count = likes_count + 1 WHERE id = 100;

-- Remove like
DELETE FROM likes WHERE user_id = 1 AND creation_id = 100;
UPDATE creations SET likes_count = likes_count - 1 WHERE id = 100;
```

---

### 8. **credit_transactions** Table (Credit History)

**Purpose**: Audit log of all credit earnings and expenses

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Transaction ID |
| `user_id` | INTEGER | FOREIGN KEY → users.id, INDEXED | Whose transaction |
| `amount` | INTEGER | NOT NULL | Positive = earned, Negative = spent |
| `type` | VARCHAR(50) | NOT NULL | Transaction type (see below) |
| `description` | VARCHAR(200) | NOT NULL | Human-readable description |
| `reference_id` | VARCHAR(100) | NULLABLE | Related entity ID (creation_id, battle_id, etc.) |
| `balance_after` | INTEGER | NOT NULL | User's balance after this transaction |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Transaction timestamp |

**Transaction Types:**
- `signup_bonus` - Initial 2500 credits on signup
- `ad_watch` - +50 credits for watching ad
- `purchase` - Bought credits with real money
- `creation` - -50 credits for generating image
- `referral` - +100 credits for successful referral
- `battle_win` - +25 credits for winning battle
- `admin_adjustment` - Manual credit adjustment

**Indexes:**
- `idx_user_id` on `user_id`
- `idx_type` on `type`
- `idx_created_at` on `created_at`

**Sample Transactions:**
```sql
-- User signs up
INSERT INTO credit_transactions (user_id, amount, type, description, balance_after)
VALUES (1, 2500, 'signup_bonus', 'Welcome bonus', 2500);

-- User generates image
INSERT INTO credit_transactions (user_id, amount, type, description, reference_id, balance_after)
VALUES (1, -50, 'creation', 'Generated Ghibli Art image', '123', 2450);

-- User watches ad
INSERT INTO credit_transactions (user_id, amount, type, description, balance_after)
VALUES (1, 50, 'ad_watch', 'Watched rewarded video ad', 2500);
```

**Important Business Rule:**
Every credit change MUST be logged here. This provides:
- Complete audit trail
- Usage analytics
- User history display
- Fraud detection

---

### 9. **ad_watches** Table (Ad Watching Limits)

**Purpose**: Track ad viewing to enforce daily limits and prevent abuse

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Record ID |
| `user_id` | INTEGER | FOREIGN KEY → users.id, INDEXED | Who watched |
| `ad_provider` | VARCHAR(50) | NOT NULL | AdMob, Unity Ads, etc. |
| `ad_unit_id` | VARCHAR(100) | NOT NULL | Specific ad unit identifier |
| `credits_earned` | INTEGER | DEFAULT 50 | Credits rewarded |
| `watched_date` | DATE | NOT NULL | Date only (for daily limit) |
| `watched_at` | TIMESTAMP | DEFAULT NOW() | Exact timestamp |

**Composite Index:**
```sql
CREATE INDEX idx_user_watched_date ON ad_watches (user_id, watched_date);
```

**Business Logic:**
```sql
-- Check if user can watch ad today
SELECT COUNT(*) FROM ad_watches 
WHERE user_id = 1 
  AND watched_date = CURRENT_DATE;
-- If count < 5, allow ad watch
-- If count >= 5, return "DAILY_LIMIT_REACHED"
```

**Ad Watching Flow:**
1. User clicks "Watch Ad" button
2. Backend checks: `SELECT COUNT(*) FROM ad_watches WHERE user_id = ? AND watched_date = TODAY`
3. If count < 5 (daily limit), allow ad
4. User watches ad on mobile
5. App gets reward token from ad SDK
6. App sends token to backend for verification
7. Backend verifies token with ad provider
8. If valid:
   - Insert into `ad_watches`
   - Insert into `credit_transactions` (+50)
   - Update `users.credits` (+50)
   - Return success

---

## 🔗 Database Relationships

### One-to-Many Relationships

1. **User → Creations**: One user creates many images
   ```sql
   user (1) ──── (N) creations
   ```

2. **User → Credit Transactions**: One user has many transactions
   ```sql
   user (1) ──── (N) credit_transactions
   ```

3. **User → Ad Watches**: One user watches many ads
   ```sql
   user (1) ──── (N) ad_watches
   ```

4. **Category → Styles**: One category contains many styles
   ```sql
   category (1) ──── (N) styles
   ```

5. **Style → Creations**: One style used in many creations
   ```sql
   style (1) ──── (N) creations
   ```

### Many-to-Many Relationships

1. **Users ↔ Creations (via Likes)**
   - Users can like many creations
   - Creations can be liked by many users
   ```sql
   users (N) ──── likes ──── (N) creations
   ```

2. **Users ↔ Battles (via Votes)**
   - Users can vote in many battles
   - Battles receive votes from many users
   ```sql
   users (N) ──── votes ──── (N) battles
   ```

### Self-Referential Relationship

**User → User (Referrals)**
```sql
users.referred_by_id → users.id
```

Example:
- Alice (id=1) has referral code "ALICE123"
- Bob signs up with code "ALICE123"
- Bob's record: `referred_by_id = 1`
- Alice gets +100 credits (referral bonus)

---

## 💾 What Needs to Be Saved (Complete List)

### User Account Data
- ✅ Email, password hash, name, phone
- ✅ Profile picture URL
- ✅ Current credit balance
- ✅ Unique referral code
- ✅ Who referred them
- ✅ Verification status
- ✅ Last login timestamp

### Image Generation Data
- ✅ Original uploaded photo URL
- ✅ AI-generated image URL
- ✅ Thumbnail URL
- ✅ Style used
- ✅ Generation options (mood, weather, dress)
- ✅ Custom prompt from user
- ✅ Full AI prompt sent to Gemini
- ✅ Processing time
- ✅ Credits spent
- ✅ Public/private status
- ✅ Like count, view count

### Style Catalog Data
- ✅ Style name, description
- ✅ Preview image
- ✅ Category assignment
- ✅ AI prompt template
- ✅ Tags for search
- ✅ Usage statistics
- ✅ Trending/new flags

### Battle & Voting Data
- ✅ Which creations are battling
- ✅ Vote counts for each
- ✅ Battle status and duration
- ✅ Winner determination
- ✅ Individual user votes
- ✅ Vote timestamps

### Credit System Data
- ✅ Every credit transaction (type, amount)
- ✅ Balance after each transaction
- ✅ Transaction descriptions
- ✅ Reference to related entity
- ✅ Ad watch events
- ✅ Daily ad limits tracking

### Social Features Data
- ✅ Who liked which creation
- ✅ Like timestamps
- ✅ Creation view counts

---

## 📊 Database Schema SQL (PostgreSQL)

```sql
-- 1. USERS TABLE
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    avatar_url VARCHAR(500),
    credits INTEGER DEFAULT 2500 CHECK (credits >= 0),
    referral_code VARCHAR(10) UNIQUE NOT NULL,
    referred_by_id INTEGER REFERENCES users(id),
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_referral_code ON users(referral_code);

-- 2. CATEGORIES TABLE
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    icon VARCHAR(10) NOT NULL,
    description VARCHAR(200) NOT NULL,
    preview_url VARCHAR(500),
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_categories_slug ON categories(slug);

-- 3. STYLES TABLE
CREATE TABLE styles (
    id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES categories(id),
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_styles_category_id ON styles(category_id);
CREATE INDEX idx_styles_name ON styles(name);
CREATE INDEX idx_styles_is_trending ON styles(is_trending);

-- 4. CREATIONS TABLE
CREATE TABLE creations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    style_id INTEGER NOT NULL REFERENCES styles(id),
    original_image_url VARCHAR(500) NOT NULL,
    generated_image_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500) NOT NULL,
    mood VARCHAR(50),
    weather VARCHAR(50),
    dress_style VARCHAR(50),
    custom_prompt VARCHAR(200),
    prompt_used TEXT NOT NULL,
    credits_used INTEGER DEFAULT 50,
    processing_time FLOAT,
    likes_count INTEGER DEFAULT 0 CHECK (likes_count >= 0),
    views_count INTEGER DEFAULT 0 CHECK (views_count >= 0),
    is_public BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_creations_user_id ON creations(user_id);
CREATE INDEX idx_creations_style_id ON creations(style_id);
CREATE INDEX idx_creations_is_public ON creations(is_public);
CREATE INDEX idx_creations_created_at ON creations(created_at);

-- 5. BATTLES TABLE
CREATE TABLE battles (
    id SERIAL PRIMARY KEY,
    creation_a_id INTEGER NOT NULL REFERENCES creations(id),
    creation_b_id INTEGER NOT NULL REFERENCES creations(id),
    votes_a INTEGER DEFAULT 0 CHECK (votes_a >= 0),
    votes_b INTEGER DEFAULT 0 CHECK (votes_b >= 0),
    status VARCHAR(20) DEFAULT 'pending',
    winner_id INTEGER REFERENCES creations(id),
    starts_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ends_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_battles_status ON battles(status);
CREATE INDEX idx_battles_ends_at ON battles(ends_at);

-- 6. VOTES TABLE
CREATE TABLE votes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    battle_id INTEGER NOT NULL REFERENCES battles(id),
    voted_for_id INTEGER NOT NULL REFERENCES creations(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_battle_vote UNIQUE (user_id, battle_id)
);

CREATE INDEX idx_votes_user_id ON votes(user_id);
CREATE INDEX idx_votes_battle_id ON votes(battle_id);

-- 7. LIKES TABLE
CREATE TABLE likes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    creation_id INTEGER NOT NULL REFERENCES creations(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_creation_like UNIQUE (user_id, creation_id)
);

CREATE INDEX idx_likes_user_id ON likes(user_id);
CREATE INDEX idx_likes_creation_id ON likes(creation_id);

-- 8. CREDIT_TRANSACTIONS TABLE
CREATE TABLE credit_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    amount INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL,
    description VARCHAR(200) NOT NULL,
    reference_id VARCHAR(100),
    balance_after INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_credit_transactions_user_id ON credit_transactions(user_id);
CREATE INDEX idx_credit_transactions_type ON credit_transactions(type);
CREATE INDEX idx_credit_transactions_created_at ON credit_transactions(created_at);

-- 9. AD_WATCHES TABLE
CREATE TABLE ad_watches (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    ad_provider VARCHAR(50) NOT NULL,
    ad_unit_id VARCHAR(100) NOT NULL,
    credits_earned INTEGER DEFAULT 50,
    watched_date DATE NOT NULL DEFAULT CURRENT_DATE,
    watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ad_watches_user_watched_date ON ad_watches(user_id, watched_date);
```

---

## 🔄 Key Business Logic

### Credit Management
```python
# When user generates image
def generate_image(user_id, style_id, image_file):
    user = get_user(user_id)
    style = get_style(style_id)
    
    # Check credits
    if user.credits < style.credits_required:
        raise InsufficientCreditsError()
    
    # Generate image (call Gemini AI)
    result = gemini_api.generate(image_file, style.prompt_template)
    
    # Save creation
    creation = Creation(
        user_id=user_id,
        style_id=style_id,
        original_image_url=upload_to_s3(image_file),
        generated_image_url=upload_to_s3(result.image),
        ...
    )
    db.add(creation)
    
    # Deduct credits
    user.credits -= style.credits_required
    
    # Log transaction
    transaction = CreditTransaction(
        user_id=user_id,
        amount=-style.credits_required,
        type='creation',
        description=f'Generated {style.name} image',
        reference_id=str(creation.id),
        balance_after=user.credits
    )
    db.add(transaction)
    
    # Update style usage
    style.uses_count += 1
    
    db.commit()
    return creation
```

### Daily Ad Limit
```python
def can_watch_ad(user_id):
    today = date.today()
    count = db.query(AdWatch).filter(
        AdWatch.user_id == user_id,
        AdWatch.watched_date == today
    ).count()
    
    DAILY_LIMIT = 5
    return count < DAILY_LIMIT, DAILY_LIMIT - count
```

---

## 📈 Performance Considerations

### Indexes Created
- All foreign keys are indexed
- Frequently queried columns (email, status, created_at)
- Composite indexes where needed (user_id + watched_date)

### Caching Strategy (Future)
- Cache trending styles (Redis, 1 hour TTL)
- Cache user profile (Redis, session lifetime)
- Cache active battles (Redis, 5 minutes TTL)

### Denormalization
- `creations.likes_count` - cached from likes table
- `styles.uses_count` - cached creation count
- `battles.votes_a/votes_b` - cached from votes table

---

## 🎯 Summary

**Total Tables**: 9

1. `users` - User accounts and authentication
2. `categories` - Style categories
3. `styles` - AI transformation styles
4. `creations` - Generated images
5. `battles` - Style battles
6. `votes` - Battle voting
7. `likes` - Creation likes
8. `credit_transactions` - Credit audit log
9. `ad_watches` - Ad viewing tracking

**What Gets Saved**: Everything! User data, images, AI prompts, credits, votes, likes, battles, ad views, and complete audit trails.

**Why This Structure**: Supports all features (AI generation, gamification, social, monetization) with proper relationships, constraints, and audit trails.
