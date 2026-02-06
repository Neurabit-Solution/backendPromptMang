# MagicPic - Complete Backend Integration Guide

> **Note**: This is the complete API specification for the MagicPic application. The current implementation includes only the authentication system. Other features are documented here for future development.

# MagicPic - Complete Backend Integration Guide

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Authentication Flow](#authentication-flow)
4. [API Contracts](#api-contracts)
5. [Data Models & Relationships](#data-models--relationships)
6. [Frontend Integration Requirements](#frontend-integration-requirements)
7. [State Management](#state-management)
8. [Error Handling](#error-handling)
9. [Caching Strategy](#caching-strategy)
10. [Real-time Features](#real-time-features)
11. [File Upload Flow](#file-upload-flow)
12. [Payment Integration](#payment-integration)
13. [Push Notifications](#push-notifications)
14. [Analytics & Tracking](#analytics--tracking)
15. [Testing Requirements](#testing-requirements)
16. [Deployment Checklist](#deployment-checklist)

---

## Overview

MagicPic is an AI-powered image transformation app that allows users to apply artistic styles to their photos. The backend must support:

- **User Management**: Registration, authentication, profiles
- **AI Image Generation**: Gemini API integration for style transfer
- **Credit System**: Virtual currency for generations
- **Gamification**: Style battles, voting, leaderboards
- **Content Discovery**: Trending styles, categories, search

### Core User Journeys

```
1. New User → Signup → Get 2500 Credits → Browse Styles → Upload Photo → Generate → Share
2. Returning User → Login → Check Credits → Watch Ad (earn 50) → Generate → Enter Battle
3. Voter → Browse Battles → Vote → See Results → Climb Leaderboard
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           MOBILE APP (React Native)                      │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Screens   │  │ Components  │  │   Hooks     │  │   Context   │    │
│  │  - Home     │  │  - Header   │  │  - useAuth  │  │  - Auth     │    │
│  │  - Create   │  │  - Grid     │  │  - useAPI   │  │  - Credits  │    │
│  │  - Battles  │  │  - Cards    │  │  - useCredits│ │  - Theme    │    │
│  │  - Profile  │  │  - Buttons  │  │  - useBattle │ │             │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
│                              │                                           │
│                    ┌─────────▼─────────┐                                │
│                    │   API Service     │                                │
│                    │   (Axios/Fetch)   │                                │
│                    └─────────┬─────────┘                                │
└──────────────────────────────┼──────────────────────────────────────────┘
                               │ HTTPS
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           API GATEWAY                                    │
│                    (Rate Limiting, CORS, Auth)                          │
└─────────────────────────────┬───────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│                         FASTAPI BACKEND                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        API ROUTERS                                │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │   │
│  │  │  Auth   │ │  Users  │ │ Styles  │ │Creates  │ │ Battles │   │   │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘   │   │
│  └───────┼───────────┼───────────┼───────────┼───────────┼────────┘   │
│          │           │           │           │           │             │
│  ┌───────▼───────────▼───────────▼───────────▼───────────▼────────┐   │
│  │                       SERVICES LAYER                            │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │   │
│  │  │  JWT    │ │ Credits │ │ Gemini  │ │ Storage │ │ Payment │  │   │
│  │  │ Service │ │ Service │ │ Service │ │ Service │ │ Service │  │   │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘  │   │
│  └───────┼───────────┼───────────┼───────────┼───────────┼────────┘   │
│          │           │           │           │           │             │
│  ┌───────▼───────────▼───────────▼───────────▼───────────▼────────┐   │
│  │                      DATA ACCESS LAYER                          │   │
│  │                   (SQLAlchemy / SQLModel)                       │   │
│  └─────────────────────────────┬──────────────────────────────────┘   │
└────────────────────────────────┼──────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  PostgreSQL   │      │    Redis      │      │  S3/Cloudinary│
│   Database    │      │    Cache      │      │    Storage    │
└───────────────┘      └───────────────┘      └───────────────┘
                                 │
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  Celery       │      │  Gemini AI    │      │   Razorpay    │
│  Workers      │      │     API       │      │   Payments    │
└───────────────┘      └───────────────┘      └───────────────┘
```

---

## Authentication Flow

### 1. Signup Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Mobile  │     │   API    │     │ Database │     │  Email   │
│   App    │     │  Server  │     │          │     │ Service  │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │  POST /signup  │                │                │
     │───────────────>│                │                │
     │                │ Check email    │                │
     │                │ exists         │                │
     │                │───────────────>│                │
     │                │<───────────────│                │
     │                │                │                │
     │                │ Hash password  │                │
     │                │ Create user    │                │
     │                │ Add 2500 credits               │
     │                │───────────────>│                │
     │                │<───────────────│                │
     │                │                │                │
     │                │ Send verification              │
     │                │───────────────────────────────>│
     │                │                │                │
     │  JWT tokens +  │                │                │
     │  user data     │                │                │
     │<───────────────│                │                │
     │                │                │                │
```

### 2. Login Flow

```
POST /api/auth/login

Request:
{
  "email": "user@example.com",
  "password": "securepass123"
}

Response (Success - 200):
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe",
      "avatar_url": "https://...",
      "credits": 2500,
      "is_verified": true
    },
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 1800  // 30 minutes
  }
}

Response (Error - 401):
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Email or password is incorrect"
  }
}
```

### 3. Token Refresh Flow

```
POST /api/auth/refresh

Headers:
  Authorization: Bearer <refresh_token>

Response (Success - 200):
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 1800
  }
}
```

### Token Storage (Mobile App)

```typescript
// Use secure storage for tokens
import * as SecureStore from 'expo-secure-store';
// OR
import EncryptedStorage from 'react-native-encrypted-storage';

// Store tokens
await SecureStore.setItemAsync('access_token', accessToken);
await SecureStore.setItemAsync('refresh_token', refreshToken);

// Retrieve tokens
const accessToken = await SecureStore.getItemAsync('access_token');
```

---

## API Contracts

### Base Configuration

```typescript
// API Base URL
const API_BASE_URL = 'https://api.magicpic.app/api';

// Request Headers
const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${accessToken}`,
  'X-App-Version': '1.0.0',
  'X-Platform': 'ios' // or 'android'
};
```

---

### 1. Authentication APIs

#### POST `/api/auth/signup`

**Purpose**: Register new user with email/password

```typescript
// Request
interface SignupRequest {
  email: string;        // Required, valid email format
  password: string;     // Required, min 8 chars, 1 uppercase, 1 number
  name: string;         // Required, 2-50 chars
  phone?: string;       // Optional, E.164 format (+91XXXXXXXXXX)
  referral_code?: string; // Optional, existing user's code
}

// Response
interface SignupResponse {
  success: true;
  data: {
    user: User;
    access_token: string;
    refresh_token: string;
    token_type: 'bearer';
    expires_in: number;
  };
  message: 'Account created successfully. Please verify your email.';
}

// Errors
type SignupErrors = 
  | 'EMAIL_EXISTS'           // 409 - Email already registered
  | 'INVALID_EMAIL'          // 400 - Invalid email format
  | 'WEAK_PASSWORD'          // 400 - Password doesn't meet requirements
  | 'INVALID_REFERRAL_CODE'; // 400 - Referral code doesn't exist
```

#### POST `/api/auth/login`

```typescript
// Request
interface LoginRequest {
  email: string;
  password: string;
  device_info?: {
    device_id: string;
    device_name: string;
    platform: 'ios' | 'android';
    push_token?: string;
  };
}

// Response - same as signup
```

#### POST `/api/auth/forgot-password`

```typescript
// Request
{ "email": "user@example.com" }

// Response
{
  "success": true,
  "message": "Password reset OTP sent to your email"
}
```

#### POST `/api/auth/reset-password`

```typescript
// Request
{
  "email": "user@example.com",
  "otp": "123456",
  "new_password": "newSecurePass123"
}

// Response
{
  "success": true,
  "message": "Password reset successfully. Please login."
}
```

---

### 2. User APIs

#### GET `/api/users/profile`

**Purpose**: Get current user's complete profile with stats

```typescript
// Response
interface ProfileResponse {
  success: true;
  data: {
    id: number;
    email: string;
    name: string;
    avatar_url: string | null;
    phone: string | null;
    credits: number;
    is_verified: boolean;
    referral_code: string;      // User's own referral code
    created_at: string;
    stats: {
      creations_count: number;   // Total images generated
      public_creations: number;  // Shared publicly
      total_likes: number;       // Likes received
      battle_wins: number;       // Battles won
      battle_participations: number;
      votes_cast: number;
      current_streak: number;    // Daily login streak
      longest_streak: number;
    };
    achievements: Achievement[];
    recent_creations: Creation[]; // Last 5
  };
}
```

#### PUT `/api/users/profile`

```typescript
// Request (multipart/form-data for avatar upload)
interface UpdateProfileRequest {
  name?: string;
  avatar?: File;  // Image file
  phone?: string;
}

// Response
{
  "success": true,
  "data": User,
  "message": "Profile updated successfully"
}
```

---

### 3. Styles & Categories APIs

#### GET `/api/categories`

**Purpose**: Get all style categories for the home screen

```typescript
// Response
interface CategoriesResponse {
  success: true;
  data: Array<{
    id: number;
    name: string;           // "Wedding", "Education"
    slug: string;           // "wedding", "education"
    icon: string;           // "💒" or icon name
    description: string;    // "Invitation & Cards"
    preview_url: string;    // Category thumbnail
    styles_count: number;   // Number of styles in category
    display_order: number;
  }>;
}
```

#### GET `/api/styles`

**Purpose**: Get styles with filtering and pagination

```typescript
// Query Parameters
interface StylesQuery {
  category?: string;      // Category slug
  trending?: boolean;     // Only trending styles
  new?: boolean;          // Styles added in last 7 days
  search?: string;        // Search by name
  sort?: 'popular' | 'newest' | 'name';
  page?: number;          // Default: 1
  limit?: number;         // Default: 20, Max: 50
}

// Response
interface StylesResponse {
  success: true;
  data: Array<{
    id: number;
    name: string;           // "Ghibli Art"
    description: string;
    preview_url: string;    // Style preview image
    category: {
      id: number;
      name: string;
      slug: string;
    };
    uses_count: number;     // Times used
    is_trending: boolean;
    is_new: boolean;
    tags: string[];         // ["anime", "artistic", "colorful"]
    credits_required: number; // Usually 50
  }>;
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}
```

#### GET `/api/styles/trending`

**Purpose**: Get hot/trending styles for homepage "Hot Right Now" section

```typescript
// Response - Limited to top 10
interface TrendingStylesResponse {
  success: true;
  data: Array<Style & {
    rank: number;           // 1-10
    trend_score: number;    // Calculated from recent uses
    weekly_uses: number;
  }>;
}
```

#### GET `/api/styles/{id}`

**Purpose**: Get single style details

```typescript
// Response
interface StyleDetailResponse {
  success: true;
  data: {
    ...Style,
    prompt_template: string;     // AI prompt (may be partial for security)
    sample_outputs: string[];    // Sample generated images
    related_styles: Style[];     // Similar styles
    user_creations: Creation[];  // Recent public creations with this style
  };
}
```

---

### 4. Creation APIs (Core Feature)

#### POST `/api/creations/generate`

**Purpose**: Generate AI-transformed image - THE MAIN FEATURE

```typescript
// Request (multipart/form-data)
interface GenerateRequest {
  image: File;              // User's photo (max 10MB, JPG/PNG)
  style_id: number;         // Selected style
  mood?: 'happy' | 'sad' | 'romantic' | 'dramatic' | 'peaceful';
  weather?: 'sunny' | 'rainy' | 'snowy' | 'cloudy' | 'night';
  dress_style?: 'casual' | 'formal' | 'traditional' | 'fantasy';
  custom_prompt?: string;   // Additional instructions (max 200 chars)
  is_public?: boolean;      // Share publicly (default: true)
}

// Response (Success)
interface GenerateResponse {
  success: true;
  data: {
    creation: {
      id: number;
      original_image_url: string;
      generated_image_url: string;
      thumbnail_url: string;
      style: Style;
      mood: string | null;
      weather: string | null;
      dress_style: string | null;
      is_public: boolean;
      created_at: string;
    };
    credits_used: 50;
    credits_remaining: number;
    processing_time: number;  // Seconds
  };
  message: 'Image generated successfully!';
}

// Errors
type GenerateErrors =
  | 'INSUFFICIENT_CREDITS'    // 402 - Need more credits
  | 'INVALID_IMAGE'           // 400 - Unsupported format/corrupt
  | 'IMAGE_TOO_LARGE'         // 413 - Exceeds 10MB
  | 'STYLE_NOT_FOUND'         // 404 - Invalid style_id
  | 'NSFW_DETECTED'           // 400 - Inappropriate content
  | 'AI_SERVICE_ERROR'        // 503 - Gemini API failed
  | 'RATE_LIMITED';           // 429 - Too many requests
```

**Backend Processing Flow**:

```
1. Validate Request
   ├── Check authentication
   ├── Validate image (type, size)
   ├── Check style exists
   └── Verify credits >= 50

2. Upload Original Image
   ├── Compress if needed
   ├── Upload to S3/Cloudinary
   └── Generate thumbnail

3. Build AI Prompt
   ├── Get style's prompt_template
   ├── Inject mood/weather/dress options
   ├── Add safety guidelines
   └── Format for Gemini

4. Call Gemini API
   ├── Send image + prompt
   ├── Wait for generation (10-30s)
   ├── Handle errors/retries
   └── Validate output

5. Save Result
   ├── Upload generated image
   ├── Create Creation record
   ├── Deduct 50 credits
   ├── Log transaction
   └── Update style uses_count

6. Return Response
```

#### GET `/api/creations`

**Purpose**: Get public creations feed

```typescript
// Query Parameters
interface CreationsQuery {
  style_id?: number;
  user_id?: number;
  sort?: 'newest' | 'popular' | 'trending';
  page?: number;
  limit?: number;
}

// Response
interface CreationsResponse {
  success: true;
  data: Array<{
    id: number;
    generated_image_url: string;
    thumbnail_url: string;
    style: { id: number; name: string };
    user: { id: number; name: string; avatar_url: string };
    likes_count: number;
    is_liked: boolean;      // Current user has liked
    created_at: string;
  }>;
  pagination: Pagination;
}
```

#### GET `/api/creations/mine`

**Purpose**: Get current user's creations

```typescript
// Response includes private creations
interface MyCreationsResponse {
  success: true;
  data: Array<{
    id: number;
    original_image_url: string;
    generated_image_url: string;
    thumbnail_url: string;
    style: Style;
    mood: string | null;
    weather: string | null;
    dress_style: string | null;
    is_public: boolean;
    likes_count: number;
    in_battle: boolean;     // Currently in active battle
    battle_wins: number;
    created_at: string;
  }>;
  pagination: Pagination;
}
```

#### POST `/api/creations/{id}/like`

```typescript
// Response
{
  "success": true,
  "data": {
    "likes_count": 46,
    "is_liked": true
  }
}
```

#### DELETE `/api/creations/{id}/like`

```typescript
// Response
{
  "success": true,
  "data": {
    "likes_count": 45,
    "is_liked": false
  }
}
```

#### DELETE `/api/creations/{id}`

```typescript
// Only owner can delete
// Response
{
  "success": true,
  "message": "Creation deleted successfully"
}

// Error if in active battle
{
  "success": false,
  "error": {
    "code": "CREATION_IN_BATTLE",
    "message": "Cannot delete creation while in active battle"
  }
}
```

---

### 5. Battles APIs

#### GET `/api/battles/current`

**Purpose**: Get a battle for the user to vote on

```typescript
// Response
interface BattleResponse {
  success: true;
  data: {
    id: number;
    creation_a: {
      id: number;
      image_url: string;
      thumbnail_url: string;
      style_name: string;
      user: { id: number; name: string; avatar_url: string };
    };
    creation_b: {
      id: number;
      image_url: string;
      thumbnail_url: string;
      style_name: string;
      user: { id: number; name: string; avatar_url: string };
    };
    total_votes: number;
    ends_at: string;          // ISO datetime
    time_remaining: number;   // Seconds
    user_vote: number | null; // creation_id if voted, null if not
  };
}

// No battles available
{
  "success": true,
  "data": null,
  "message": "No battles available. Check back soon!"
}
```

#### POST `/api/battles/{id}/vote`

```typescript
// Request
{ "creation_id": 123 }

// Response
{
  "success": true,
  "data": {
    "votes_a": 156,
    "votes_b": 142,
    "user_vote": 123,
    "vote_percentage": {
      "a": 52.3,
      "b": 47.7
    }
  },
  "message": "Vote recorded!"
}

// Errors
type VoteErrors =
  | 'ALREADY_VOTED'      // 409 - User already voted in this battle
  | 'BATTLE_ENDED'       // 400 - Battle has ended
  | 'INVALID_CREATION'   // 400 - Creation not in this battle
  | 'OWN_CREATION';      // 400 - Can't vote for own creation
```

#### GET `/api/battles/next`

**Purpose**: Skip current battle and get another

```typescript
// Query
?exclude_id=45  // Don't show this battle again

// Response - Same as /current
```

#### GET `/api/battles/leaderboard`

**Purpose**: Get top creators by battle wins

```typescript
// Query
?period=weekly | monthly | all_time

// Response
interface LeaderboardResponse {
  success: true;
  data: {
    period: 'weekly' | 'monthly' | 'all_time';
    leaders: Array<{
      rank: number;
      user: {
        id: number;
        name: string;
        avatar_url: string;
      };
      wins: number;
      total_battles: number;
      win_rate: number;       // Percentage
      badge: '🥇' | '🥈' | '🥉' | null;
      is_current_user: boolean;
    }>;
    current_user_rank: {
      rank: number;
      wins: number;
      total_battles: number;
    } | null;
  };
}
```

#### GET `/api/battles/history`

**Purpose**: Get user's battle participation history

```typescript
// Response
interface BattleHistoryResponse {
  success: true;
  data: Array<{
    id: number;
    my_creation: {
      id: number;
      thumbnail_url: string;
      votes: number;
    };
    opponent_creation: {
      id: number;
      thumbnail_url: string;
      votes: number;
      user: { name: string; avatar_url: string };
    };
    result: 'won' | 'lost' | 'tie';
    ended_at: string;
  }>;
  pagination: Pagination;
}
```

#### POST `/api/battles/enter`

**Purpose**: Submit a creation to battle pool

```typescript
// Request
{ "creation_id": 123 }

// Response
{
  "success": true,
  "message": "Creation entered into battle pool! You'll be matched soon."
}

// Errors
| 'CREATION_NOT_FOUND'
| 'NOT_OWNER'
| 'ALREADY_IN_BATTLE'
| 'CREATION_PRIVATE'  // Must be public
```

---

### 6. Credits APIs

#### GET `/api/credits/balance`

```typescript
// Response
{
  "success": true,
  "data": {
    "balance": 2350,
    "pending": 0,              // Credits being processed
    "lifetime_earned": 5000,
    "lifetime_spent": 2650
  }
}
```

#### GET `/api/credits/history`

```typescript
// Query
?type=all | earned | spent
&page=1
&limit=20

// Response
interface CreditHistoryResponse {
  success: true;
  data: Array<{
    id: number;
    amount: number;            // Positive = earned, Negative = spent
    type: 'signup_bonus' | 'ad_watch' | 'purchase' | 'creation' | 'referral' | 'battle_win';
    description: string;       // "Watched ad", "Created Ghibli Art image"
    balance_after: number;
    created_at: string;
  }>;
  pagination: Pagination;
}
```

#### POST `/api/credits/earn/ad`

**Purpose**: Reward credits for watching ad

```typescript
// Request
{
  "ad_provider": "admob",
  "ad_unit_id": "ca-app-pub-xxxxx/xxxxx",
  "reward_token": "xxxxx",      // Verification token from ad SDK
  "ad_type": "rewarded_video"
}

// Response
{
  "success": true,
  "data": {
    "credits_earned": 50,
    "new_balance": 2400,
    "daily_ads_watched": 2,
    "daily_ads_limit": 5,
    "ads_remaining_today": 3,
    "next_ad_available_at": null  // or ISO datetime if cooldown
  },
  "message": "You earned 50 credits!"
}

// Errors
| 'DAILY_LIMIT_REACHED'    // 429 - Already watched 5 ads today
| 'INVALID_AD_TOKEN'       // 400 - Token verification failed
| 'AD_COOLDOWN'            // 429 - Must wait before next ad
```

#### GET `/api/credits/packages`

**Purpose**: Get purchasable credit packages

```typescript
// Response
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Starter Pack",
      "credits": 500,
      "price": 49,
      "currency": "INR",
      "price_formatted": "₹49",
      "per_credit_cost": 0.098,
      "popular": false,
      "discount_percent": 0
    },
    {
      "id": 2,
      "name": "Value Pack",
      "credits": 1500,
      "price": 129,
      "currency": "INR",
      "price_formatted": "₹129",
      "per_credit_cost": 0.086,
      "popular": true,
      "discount_percent": 12,
      "badge": "Best Value"
    },
    {
      "id": 3,
      "name": "Pro Pack",
      "credits": 5000,
      "price": 399,
      "currency": "INR",
      "price_formatted": "₹399",
      "per_credit_cost": 0.08,
      "popular": false,
      "discount_percent": 18
    }
  ]
}
```

#### POST `/api/credits/purchase`

**Purpose**: Purchase credits (initiate payment)

```typescript
// Request
{
  "package_id": 2,
  "payment_method": "razorpay"  // or "google_pay", "apple_pay"
}

// Response
{
  "success": true,
  "data": {
    "order_id": "order_xxxxx",
    "razorpay_key": "rzp_live_xxxxx",
    "amount": 12900,            // In paise
    "currency": "INR",
    "prefill": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  }
}
```

#### POST `/api/credits/purchase/verify`

**Purpose**: Verify payment and credit account

```typescript
// Request
{
  "order_id": "order_xxxxx",
  "payment_id": "pay_xxxxx",
  "signature": "xxxxx"
}

// Response
{
  "success": true,
  "data": {
    "credits_added": 1500,
    "new_balance": 3900,
    "transaction_id": "txn_xxxxx"
  },
  "message": "Payment successful! 1500 credits added."
}
```

---

### 7. Discover/Search APIs

#### GET `/api/discover`

**Purpose**: Get homepage discovery content

```typescript
// Response
interface DiscoverResponse {
  success: true;
  data: {
    trending_styles: Style[];         // Top 5 trending
    new_styles: Style[];              // Latest 5
    featured_creations: Creation[];   // Editor picks
    popular_categories: Category[];   // Top 4 categories
    daily_challenge?: {
      id: number;
      title: string;
      style: Style;
      participants: number;
      ends_at: string;
    };
  };
}
```

#### GET `/api/discover/search`

**Purpose**: Global search across styles, categories, users

```typescript
// Query
?q=wedding&type=all | styles | categories | users

// Response
{
  "success": true,
  "data": {
    "styles": Style[],
    "categories": Category[],
    "users": Array<{
      id: number;
      name: string;
      avatar_url: string;
      creations_count: number;
    }>,
    "total_results": number
  }
}
```

---

## Data Models & Relationships

### Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  ┌──────────┐       ┌──────────────┐       ┌──────────────┐    │
│  │   User   │───────│   Creation   │───────│    Style     │    │
│  └──────────┘   1:N └──────────────┘   N:1 └──────────────┘    │
│       │                   │                       │             │
│       │                   │                       │             │
│       │              ┌────┴────┐                  │             │
│       │              │         │                  │             │
│       ▼              ▼         ▼                  ▼             │
│  ┌──────────┐   ┌────────┐ ┌────────┐      ┌──────────┐        │
│  │  Credit  │   │  Like  │ │ Battle │      │ Category │        │
│  │Transaction│  └────────┘ └────────┘      └──────────┘        │
│  └──────────┘                  │                                │
│       │                        │                                │
│       │                        ▼                                │
│       │                   ┌────────┐                            │
│       │                   │  Vote  │                            │
│       │                   └────────┘                            │
│       │                                                         │
│       ▼                                                         │
│  ┌──────────┐                                                   │
│  │ AdWatch  │                                                   │
│  └──────────┘                                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Complete Data Models

```python
# models/user.py
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: int = Field(primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    phone: str | None = Field(unique=True, nullable=True, max_length=20)
    password_hash: str = Field(max_length=255)
    name: str = Field(max_length=100)
    avatar_url: str | None = Field(nullable=True, max_length=500)
    credits: int = Field(default=2500, ge=0)
    referral_code: str = Field(unique=True, max_length=10)  # Auto-generated
    referred_by_id: int | None = Field(foreign_key="users.id", nullable=True)
    is_verified: bool = Field(default=False)
    is_active: bool = Field(default=True)
    last_login: datetime | None = Field(nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    creations: list["Creation"] = Relationship(back_populates="user")
    credit_transactions: list["CreditTransaction"] = Relationship(back_populates="user")


# models/creation.py
class Creation(SQLModel, table=True):
    __tablename__ = "creations"
    
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    style_id: int = Field(foreign_key="styles.id", index=True)
    
    # Images
    original_image_url: str = Field(max_length=500)
    generated_image_url: str = Field(max_length=500)
    thumbnail_url: str = Field(max_length=500)
    
    # Generation options
    mood: str | None = Field(nullable=True, max_length=50)
    weather: str | None = Field(nullable=True, max_length=50)
    dress_style: str | None = Field(nullable=True, max_length=50)
    custom_prompt: str | None = Field(nullable=True, max_length=200)
    
    # Metadata
    prompt_used: str = Field(max_length=2000)  # Full prompt sent to AI
    credits_used: int = Field(default=50)
    processing_time: float | None = Field(nullable=True)  # Seconds
    
    # Stats
    likes_count: int = Field(default=0, ge=0)
    views_count: int = Field(default=0, ge=0)
    
    # Status
    is_public: bool = Field(default=True)
    is_featured: bool = Field(default=False)
    is_deleted: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="creations")
    style: "Style" = Relationship(back_populates="creations")
    likes: list["Like"] = Relationship(back_populates="creation")


# models/style.py
class Style(SQLModel, table=True):
    __tablename__ = "styles"
    
    id: int = Field(primary_key=True)
    category_id: int = Field(foreign_key="categories.id", index=True)
    
    name: str = Field(max_length=100, index=True)
    description: str = Field(max_length=500)
    preview_url: str = Field(max_length=500)
    
    # AI Prompt
    prompt_template: str = Field(max_length=2000)
    negative_prompt: str | None = Field(nullable=True, max_length=1000)
    
    # Metadata
    tags: list[str] = Field(default=[], sa_column=Column(JSON))
    credits_required: int = Field(default=50)
    
    # Stats
    uses_count: int = Field(default=0, ge=0)
    
    # Status
    is_trending: bool = Field(default=False)
    is_new: bool = Field(default=False)
    is_active: bool = Field(default=True)
    display_order: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    category: "Category" = Relationship(back_populates="styles")
    creations: list[Creation] = Relationship(back_populates="style")


# models/category.py
class Category(SQLModel, table=True):
    __tablename__ = "categories"
    
    id: int = Field(primary_key=True)
    name: str = Field(max_length=100, unique=True)
    slug: str = Field(max_length=100, unique=True, index=True)
    icon: str = Field(max_length=10)  # Emoji
    description: str = Field(max_length=200)
    preview_url: str | None = Field(nullable=True, max_length=500)
    display_order: int = Field(default=0)
    is_active: bool = Field(default=True)
    
    # Relationships
    styles: list[Style] = Relationship(back_populates="category")


# models/battle.py
class Battle(SQLModel, table=True):
    __tablename__ = "battles"
    
    id: int = Field(primary_key=True)
    creation_a_id: int = Field(foreign_key="creations.id", index=True)
    creation_b_id: int = Field(foreign_key="creations.id", index=True)
    
    votes_a: int = Field(default=0, ge=0)
    votes_b: int = Field(default=0, ge=0)
    
    status: str = Field(default="pending")  # pending, active, completed
    winner_id: int | None = Field(foreign_key="creations.id", nullable=True)
    
    starts_at: datetime = Field(default_factory=datetime.utcnow)
    ends_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    creation_a: Creation = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Battle.creation_a_id]"}
    )
    creation_b: Creation = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Battle.creation_b_id]"}
    )
    votes: list["Vote"] = Relationship(back_populates="battle")


# models/vote.py
class Vote(SQLModel, table=True):
    __tablename__ = "votes"
    __table_args__ = (
        UniqueConstraint("user_id", "battle_id", name="unique_user_battle_vote"),
    )
    
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    battle_id: int = Field(foreign_key="battles.id", index=True)
    voted_for_id: int = Field(foreign_key="creations.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship()
    battle: Battle = Relationship(back_populates="votes")


# models/like.py
class Like(SQLModel, table=True):
    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint("user_id", "creation_id", name="unique_user_creation_like"),
    )
    
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    creation_id: int = Field(foreign_key="creations.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship()
    creation: Creation = Relationship(back_populates="likes")


# models/credit.py
class CreditTransaction(SQLModel, table=True):
    __tablename__ = "credit_transactions"
    
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    amount: int  # Positive = earned, Negative = spent
    type: str = Field(max_length=50)  # signup_bonus, ad_watch, purchase, creation, referral, battle_win
    description: str = Field(max_length=200)
    reference_id: str | None = Field(nullable=True, max_length=100)  # Related entity ID
    balance_after: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="credit_transactions")


class AdWatch(SQLModel, table=True):
    __tablename__ = "ad_watches"
    __table_args__ = (
        Index("idx_user_watched_date", "user_id", "watched_date"),
    )
    
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    ad_provider: str = Field(max_length=50)  # admob, unity
    ad_unit_id: str = Field(max_length=100)
    credits_earned: int = Field(default=50)
    watched_date: date = Field(default_factory=date.today)
    watched_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship()
```

---

## Frontend Integration Requirements

### API Service Setup

```typescript
// src/services/api.ts
import axios, { AxiosError, AxiosInstance } from 'axios';
import * as SecureStore from 'expo-secure-store';

const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000/api'
  : 'https://api.magicpic.app/api';

class ApiService {
  private client: AxiosInstance;
  private refreshPromise: Promise<string> | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor - add auth token
    this.client.interceptors.request.use(
      async (config) => {
        const token = await SecureStore.getItemAsync('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            const newToken = await this.refreshToken();
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return this.client(originalRequest);
          } catch (refreshError) {
            // Refresh failed - logout user
            await this.logout();
            throw refreshError;
          }
        }
        
        return Promise.reject(error);
      }
    );
  }

  private async refreshToken(): Promise<string> {
    // Prevent multiple simultaneous refresh calls
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = (async () => {
      const refreshToken = await SecureStore.getItemAsync('refresh_token');
      const response = await axios.post(`${API_BASE_URL}/auth/refresh`, null, {
        headers: { Authorization: `Bearer ${refreshToken}` },
      });
      
      const { access_token } = response.data.data;
      await SecureStore.setItemAsync('access_token', access_token);
      return access_token;
    })();

    try {
      return await this.refreshPromise;
    } finally {
      this.refreshPromise = null;
    }
  }

  private async logout() {
    await SecureStore.deleteItemAsync('access_token');
    await SecureStore.deleteItemAsync('refresh_token');
    // Navigate to login screen
  }

  // Auth
  async signup(data: SignupRequest) {
    const response = await this.client.post('/auth/signup', data);
    await this.saveTokens(response.data.data);
    return response.data;
  }

  async login(data: LoginRequest) {
    const response = await this.client.post('/auth/login', data);
    await this.saveTokens(response.data.data);
    return response.data;
  }

  private async saveTokens(data: { access_token: string; refresh_token: string }) {
    await SecureStore.setItemAsync('access_token', data.access_token);
    await SecureStore.setItemAsync('refresh_token', data.refresh_token);
  }

  // User
  async getProfile() {
    const response = await this.client.get('/users/profile');
    return response.data;
  }

  // Styles
  async getStyles(params: StylesQuery) {
    const response = await this.client.get('/styles', { params });
    return response.data;
  }

  async getTrendingStyles() {
    const response = await this.client.get('/styles/trending');
    return response.data;
  }

  // Creations
  async generateImage(formData: FormData) {
    const response = await this.client.post('/creations/generate', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000, // 60 seconds for generation
    });
    return response.data;
  }

  async getCreations(params: CreationsQuery) {
    const response = await this.client.get('/creations', { params });
    return response.data;
  }

  async likeCreation(id: number) {
    const response = await this.client.post(`/creations/${id}/like`);
    return response.data;
  }

  // Battles
  async getCurrentBattle() {
    const response = await this.client.get('/battles/current');
    return response.data;
  }

  async voteBattle(battleId: number, creationId: number) {
    const response = await this.client.post(`/battles/${battleId}/vote`, {
      creation_id: creationId,
    });
    return response.data;
  }

  async getLeaderboard(period: 'weekly' | 'monthly' | 'all_time') {
    const response = await this.client.get('/battles/leaderboard', {
      params: { period },
    });
    return response.data;
  }

  // Credits
  async getCreditsBalance() {
    const response = await this.client.get('/credits/balance');
    return response.data;
  }

  async earnCreditsFromAd(adData: AdWatchRequest) {
    const response = await this.client.post('/credits/earn/ad', adData);
    return response.data;
  }

  async getCreditPackages() {
    const response = await this.client.get('/credits/packages');
    return response.data;
  }
}

export const api = new ApiService();
```

### React Native Hooks

```typescript
// src/hooks/useAuth.ts
import { useState, useEffect, createContext, useContext } from 'react';
import { api } from '../services/api';
import * as SecureStore from 'expo-secure-store';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (data: SignupRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuthState();
  }, []);

  const checkAuthState = async () => {
    try {
      const token = await SecureStore.getItemAsync('access_token');
      if (token) {
        const { data } = await api.getProfile();
        setUser(data);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const { data } = await api.login({ email, password });
    setUser(data.user);
  };

  const signup = async (signupData: SignupRequest) => {
    const { data } = await api.signup(signupData);
    setUser(data.user);
  };

  const logout = async () => {
    await SecureStore.deleteItemAsync('access_token');
    await SecureStore.deleteItemAsync('refresh_token');
    setUser(null);
  };

  const refreshUser = async () => {
    const { data } = await api.getProfile();
    setUser(data);
  };

  return (
    <AuthContext.Provider value={{
      user,
      isLoading,
      isAuthenticated: !!user,
      login,
      signup,
      logout,
      refreshUser,
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};


// src/hooks/useCredits.ts
import { useState, useCallback } from 'react';
import { api } from '../services/api';
import { useAuth } from './useAuth';

export const useCredits = () => {
  const { user, refreshUser } = useAuth();
  const [isEarning, setIsEarning] = useState(false);

  const balance = user?.credits ?? 0;

  const earnFromAd = useCallback(async (adData: AdWatchRequest) => {
    setIsEarning(true);
    try {
      const { data } = await api.earnCreditsFromAd(adData);
      await refreshUser(); // Update user credits
      return data;
    } finally {
      setIsEarning(false);
    }
  }, [refreshUser]);

  const hasEnoughCredits = useCallback((required: number) => {
    return balance >= required;
  }, [balance]);

  return {
    balance,
    isEarning,
    earnFromAd,
    hasEnoughCredits,
  };
};


// src/hooks/useGeneration.ts
import { useState } from 'react';
import { api } from '../services/api';
import { useCredits } from './useCredits';

interface GenerationState {
  isGenerating: boolean;
  progress: number;
  error: string | null;
  result: Creation | null;
}

export const useGeneration = () => {
  const [state, setState] = useState<GenerationState>({
    isGenerating: false,
    progress: 0,
    error: null,
    result: null,
  });
  const { balance, hasEnoughCredits } = useCredits();

  const generate = async (params: GenerateParams) => {
    // Pre-check credits
    if (!hasEnoughCredits(50)) {
      setState(s => ({ ...s, error: 'Insufficient credits. You need 50 credits.' }));
      return null;
    }

    setState({ isGenerating: true, progress: 0, error: null, result: null });

    try {
      // Simulate progress (actual progress would come from backend)
      const progressInterval = setInterval(() => {
        setState(s => ({ ...s, progress: Math.min(s.progress + 10, 90) }));
      }, 2000);

      const formData = new FormData();
      formData.append('image', {
        uri: params.imageUri,
        type: 'image/jpeg',
        name: 'photo.jpg',
      });
      formData.append('style_id', params.styleId.toString());
      if (params.mood) formData.append('mood', params.mood);
      if (params.weather) formData.append('weather', params.weather);
      if (params.dressStyle) formData.append('dress_style', params.dressStyle);

      const { data } = await api.generateImage(formData);
      
      clearInterval(progressInterval);
      setState({ isGenerating: false, progress: 100, error: null, result: data.creation });
      
      return data.creation;
    } catch (error) {
      const message = error.response?.data?.error?.message || 'Generation failed';
      setState({ isGenerating: false, progress: 0, error: message, result: null });
      return null;
    }
  };

  const reset = () => {
    setState({ isGenerating: false, progress: 0, error: null, result: null });
  };

  return {
    ...state,
    generate,
    reset,
  };
};
```

---

## State Management

### Global State Structure

```typescript
// Using Zustand for state management
// src/store/index.ts
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface AppState {
  // Auth
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  
  // Credits
  credits: number;
  setCredits: (credits: number) => void;
  deductCredits: (amount: number) => void;
  
  // Styles cache
  trendingStyles: Style[];
  categories: Category[];
  setTrendingStyles: (styles: Style[]) => void;
  setCategories: (categories: Category[]) => void;
  
  // User's creations
  myCreations: Creation[];
  addCreation: (creation: Creation) => void;
  removeCreation: (id: number) => void;
  
  // Battle state
  currentBattle: Battle | null;
  setCurrentBattle: (battle: Battle | null) => void;
  
  // UI state
  isLoading: boolean;
  setLoading: (loading: boolean) => void;
}

export const useStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Auth
      user: null,
      isAuthenticated: false,
      setUser: (user) => set({ 
        user, 
        isAuthenticated: !!user,
        credits: user?.credits ?? 0 
      }),
      
      // Credits
      credits: 0,
      setCredits: (credits) => set({ credits }),
      deductCredits: (amount) => set({ credits: get().credits - amount }),
      
      // Styles
      trendingStyles: [],
      categories: [],
      setTrendingStyles: (trendingStyles) => set({ trendingStyles }),
      setCategories: (categories) => set({ categories }),
      
      // Creations
      myCreations: [],
      addCreation: (creation) => set({ 
        myCreations: [creation, ...get().myCreations] 
      }),
      removeCreation: (id) => set({
        myCreations: get().myCreations.filter(c => c.id !== id)
      }),
      
      // Battle
      currentBattle: null,
      setCurrentBattle: (currentBattle) => set({ currentBattle }),
      
      // UI
      isLoading: false,
      setLoading: (isLoading) => set({ isLoading }),
    }),
    {
      name: 'magicpic-storage',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        // Only persist these fields
        trendingStyles: state.trendingStyles,
        categories: state.categories,
      }),
    }
  )
);
```

---

## Error Handling

### Error Codes & Handling

```typescript
// src/utils/errors.ts
export const ErrorCodes = {
  // Auth errors (401)
  INVALID_TOKEN: 'Token is invalid or expired',
  INVALID_CREDENTIALS: 'Email or password is incorrect',
  
  // Validation errors (400)
  INVALID_EMAIL: 'Please enter a valid email address',
  WEAK_PASSWORD: 'Password must be at least 8 characters with 1 uppercase and 1 number',
  INVALID_IMAGE: 'Please upload a valid JPG or PNG image',
  IMAGE_TOO_LARGE: 'Image must be less than 10MB',
  NSFW_DETECTED: 'Image contains inappropriate content',
  
  // Resource errors (404)
  STYLE_NOT_FOUND: 'This style is no longer available',
  CREATION_NOT_FOUND: 'Creation not found',
  BATTLE_NOT_FOUND: 'Battle not found',
  
  // Conflict errors (409)
  EMAIL_EXISTS: 'An account with this email already exists',
  ALREADY_VOTED: 'You have already voted in this battle',
  ALREADY_IN_BATTLE: 'This creation is already in a battle',
  
  // Payment errors (402)
  INSUFFICIENT_CREDITS: 'You need more credits. Watch an ad or purchase credits.',
  PAYMENT_FAILED: 'Payment could not be processed. Please try again.',
  
  // Rate limiting (429)
  RATE_LIMITED: 'Too many requests. Please wait a moment.',
  DAILY_AD_LIMIT: 'You\'ve reached the daily ad limit. Try again tomorrow.',
  
  // Server errors (500+)
  AI_SERVICE_ERROR: 'AI service is temporarily unavailable. Please try again.',
  SERVER_ERROR: 'Something went wrong. Please try again later.',
} as const;

export const handleApiError = (error: AxiosError): string => {
  if (!error.response) {
    return 'Network error. Please check your connection.';
  }

  const errorCode = error.response.data?.error?.code;
  const customMessage = error.response.data?.error?.message;
  
  // Return custom message if provided
  if (customMessage) return customMessage;
  
  // Return mapped message for known codes
  if (errorCode && ErrorCodes[errorCode]) {
    return ErrorCodes[errorCode];
  }
  
  // Default messages by status code
  switch (error.response.status) {
    case 400: return 'Invalid request. Please check your input.';
    case 401: return 'Please log in again.';
    case 403: return 'You don\'t have permission to do this.';
    case 404: return 'Not found.';
    case 429: return 'Too many requests. Please slow down.';
    case 500: return 'Server error. Please try again later.';
    default: return 'Something went wrong.';
  }
};

// Usage in components
import { Alert } from 'react-native';

const handleSubmit = async () => {
  try {
    await api.generateImage(formData);
  } catch (error) {
    const message = handleApiError(error);
    Alert.alert('Error', message);
    
    // Special handling for specific errors
    if (error.response?.data?.error?.code === 'INSUFFICIENT_CREDITS') {
      navigation.navigate('BuyCredits');
    }
  }
};
```

---

## Caching Strategy

### Cache Layers

```typescript
// 1. In-Memory Cache (React Query)
// src/services/queryClient.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,      // 5 minutes
      gcTime: 30 * 60 * 1000,         // 30 minutes (formerly cacheTime)
      retry: 2,
      retryDelay: 1000,
    },
  },
});

// Query key factories
export const queryKeys = {
  user: ['user'] as const,
  profile: () => [...queryKeys.user, 'profile'] as const,
  
  styles: ['styles'] as const,
  stylesList: (params: StylesQuery) => [...queryKeys.styles, params] as const,
  styleDetail: (id: number) => [...queryKeys.styles, id] as const,
  trendingStyles: () => [...queryKeys.styles, 'trending'] as const,
  
  categories: ['categories'] as const,
  
  creations: ['creations'] as const,
  creationsFeed: (params: CreationsQuery) => [...queryKeys.creations, 'feed', params] as const,
  myCreations: () => [...queryKeys.creations, 'mine'] as const,
  
  battles: ['battles'] as const,
  currentBattle: () => [...queryKeys.battles, 'current'] as const,
  leaderboard: (period: string) => [...queryKeys.battles, 'leaderboard', period] as const,
  
  credits: ['credits'] as const,
  balance: () => [...queryKeys.credits, 'balance'] as const,
  packages: () => [...queryKeys.credits, 'packages'] as const,
};


// 2. Cache TTL by endpoint
const CACHE_CONFIG = {
  // Frequently updated - short cache
  '/credits/balance': { staleTime: 30 * 1000 },        // 30 seconds
  '/battles/current': { staleTime: 60 * 1000 },        // 1 minute
  '/creations': { staleTime: 2 * 60 * 1000 },          // 2 minutes
  
  // Moderately updated
  '/styles/trending': { staleTime: 5 * 60 * 1000 },    // 5 minutes
  '/battles/leaderboard': { staleTime: 5 * 60 * 1000 }, // 5 minutes
  
  // Rarely updated - long cache
  '/categories': { staleTime: 60 * 60 * 1000 },        // 1 hour
  '/styles': { staleTime: 30 * 60 * 1000 },            // 30 minutes
  '/credits/packages': { staleTime: 60 * 60 * 1000 },  // 1 hour
};


// 3. Using queries in components
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Fetching trending styles
export const useTrendingStyles = () => {
  return useQuery({
    queryKey: queryKeys.trendingStyles(),
    queryFn: () => api.getTrendingStyles(),
    staleTime: 5 * 60 * 1000,
  });
};

// Generating image with cache invalidation
export const useGenerateImage = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: api.generateImage,
    onSuccess: (data) => {
      // Invalidate related caches
      queryClient.invalidateQueries({ queryKey: queryKeys.myCreations() });
      queryClient.invalidateQueries({ queryKey: queryKeys.balance() });
      
      // Optimistically add to creations list
      queryClient.setQueryData(queryKeys.myCreations(), (old: Creation[]) => 
        [data.creation, ...(old || [])]
      );
    },
  });
};

// Voting with optimistic update
export const useVoteBattle = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ battleId, creationId }: { battleId: number; creationId: number }) =>
      api.voteBattle(battleId, creationId),
    onMutate: async ({ battleId, creationId }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: queryKeys.currentBattle() });
      
      // Snapshot previous value
      const previousBattle = queryClient.getQueryData(queryKeys.currentBattle());
      
      // Optimistically update
      queryClient.setQueryData(queryKeys.currentBattle(), (old: Battle) => ({
        ...old,
        user_vote: creationId,
        votes_a: creationId === old.creation_a.id ? old.votes_a + 1 : old.votes_a,
        votes_b: creationId === old.creation_b.id ? old.votes_b + 1 : old.votes_b,
      }));
      
      return { previousBattle };
    },
    onError: (err, variables, context) => {
      // Rollback on error
      queryClient.setQueryData(queryKeys.currentBattle(), context?.previousBattle);
    },
    onSettled: () => {
      // Refetch to ensure sync
      queryClient.invalidateQueries({ queryKey: queryKeys.currentBattle() });
    },
  });
};
```

---

## Real-time Features

### WebSocket Integration

```typescript
// src/services/websocket.ts
import { io, Socket } from 'socket.io-client';
import { useStore } from '../store';

class WebSocketService {
  private socket: Socket | null = null;
  
  connect(token: string) {
    this.socket = io('wss://api.magicpic.app', {
      auth: { token },
      transports: ['websocket'],
    });
    
    this.setupListeners();
  }
  
  private setupListeners() {
    if (!this.socket) return;
    
    // Battle updates
    this.socket.on('battle:vote_update', (data: { 
      battle_id: number; 
      votes_a: number; 
      votes_b: number 
    }) => {
      const currentBattle = useStore.getState().currentBattle;
      if (currentBattle?.id === data.battle_id) {
        useStore.getState().setCurrentBattle({
          ...currentBattle,
          votes_a: data.votes_a,
          votes_b: data.votes_b,
        });
      }
    });
    
    this.socket.on('battle:ended', (data: { 
      battle_id: number; 
      winner_id: number 
    }) => {
      // Show battle result notification
      // Fetch new battle
    });
    
    // Creation events
    this.socket.on('creation:liked', (data: { 
      creation_id: number; 
      likes_count: number 
    }) => {
      // Update creation in cache
    });
    
    // Credit updates
    this.socket.on('credits:updated', (data: { balance: number }) => {
      useStore.getState().setCredits(data.balance);
    });
  }
  
  // Join battle room for real-time updates
  joinBattle(battleId: number) {
    this.socket?.emit('battle:join', { battle_id: battleId });
  }
  
  leaveBattle(battleId: number) {
    this.socket?.emit('battle:leave', { battle_id: battleId });
  }
  
  disconnect() {
    this.socket?.disconnect();
    this.socket = null;
  }
}

export const wsService = new WebSocketService();
```

---

## File Upload Flow

### Image Upload with Compression

```typescript
// src/utils/imageUtils.ts
import { manipulateAsync, SaveFormat } from 'expo-image-manipulator';
import * as FileSystem from 'expo-file-system';

interface CompressOptions {
  maxWidth?: number;
  maxHeight?: number;
  quality?: number;
  maxSizeMB?: number;
}

export const compressImage = async (
  uri: string, 
  options: CompressOptions = {}
): Promise<string> => {
  const {
    maxWidth = 1920,
    maxHeight = 1920,
    quality = 0.8,
    maxSizeMB = 5,
  } = options;
  
  // Get original dimensions
  const info = await FileSystem.getInfoAsync(uri);
  const originalSize = info.size / (1024 * 1024); // MB
  
  // Compress
  const result = await manipulateAsync(
    uri,
    [{ resize: { width: maxWidth, height: maxHeight } }],
    { compress: quality, format: SaveFormat.JPEG }
  );
  
  // Check size and re-compress if needed
  const newInfo = await FileSystem.getInfoAsync(result.uri);
  const newSize = newInfo.size / (1024 * 1024);
  
  if (newSize > maxSizeMB && quality > 0.3) {
    // Recursively compress with lower quality
    return compressImage(result.uri, {
      ...options,
      quality: quality - 0.2,
    });
  }
  
  return result.uri;
};

// Upload with progress tracking
export const uploadImage = async (
  uri: string,
  onProgress?: (progress: number) => void
): Promise<string> => {
  const compressedUri = await compressImage(uri);
  
  const formData = new FormData();
  formData.append('image', {
    uri: compressedUri,
    type: 'image/jpeg',
    name: 'image.jpg',
  } as any);
  
  const response = await fetch(`${API_BASE_URL}/upload/image`, {
    method: 'POST',
    headers: {
      'Content-Type': 'multipart/form-data',
      Authorization: `Bearer ${await getToken()}`,
    },
    body: formData,
  });
  
  const data = await response.json();
  return data.data.url;
};
```

---

## Payment Integration

### Razorpay Flow (India)

```typescript
// src/services/payment.ts
import RazorpayCheckout from 'react-native-razorpay';
import { api } from './api';

interface PurchaseResult {
  success: boolean;
  credits_added?: number;
  error?: string;
}

export const purchaseCredits = async (packageId: number): Promise<PurchaseResult> => {
  try {
    // 1. Create order on backend
    const { data: orderData } = await api.createCreditPurchase({ package_id: packageId });
    
    // 2. Open Razorpay checkout
    const options = {
      key: orderData.razorpay_key,
      amount: orderData.amount,
      currency: orderData.currency,
      name: 'MagicPic',
      description: 'Credit Purchase',
      order_id: orderData.order_id,
      prefill: orderData.prefill,
      theme: { color: '#9b87f5' },
    };
    
    const paymentData = await RazorpayCheckout.open(options);
    
    // 3. Verify payment on backend
    const { data: verifyData } = await api.verifyCreditPurchase({
      order_id: orderData.order_id,
      payment_id: paymentData.razorpay_payment_id,
      signature: paymentData.razorpay_signature,
    });
    
    return {
      success: true,
      credits_added: verifyData.credits_added,
    };
  } catch (error) {
    if (error.code === 'PAYMENT_CANCELLED') {
      return { success: false, error: 'Payment cancelled' };
    }
    return { success: false, error: 'Payment failed. Please try again.' };
  }
};
```

---

## Push Notifications

### FCM Setup

```typescript
// src/services/notifications.ts
import messaging from '@react-native-firebase/messaging';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from './api';

export const setupNotifications = async () => {
  // Request permission
  const authStatus = await messaging().requestPermission();
  const enabled = authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
                  authStatus === messaging.AuthorizationStatus.PROVISIONAL;
  
  if (!enabled) return;
  
  // Get FCM token
  const fcmToken = await messaging().getToken();
  
  // Check if token changed
  const storedToken = await AsyncStorage.getItem('fcm_token');
  if (fcmToken !== storedToken) {
    await api.registerDevice({
      token: fcmToken,
      platform: Platform.OS,
    });
    await AsyncStorage.setItem('fcm_token', fcmToken);
  }
  
  // Handle token refresh
  messaging().onTokenRefresh(async (newToken) => {
    await api.registerDevice({
      token: newToken,
      platform: Platform.OS,
    });
    await AsyncStorage.setItem('fcm_token', newToken);
  });
};

// Notification types from backend
type NotificationType = 
  | 'creation_liked'      // Someone liked your creation
  | 'battle_started'      // Your creation entered a battle
  | 'battle_ending'       // Battle ending in 1 hour
  | 'battle_won'          // You won a battle!
  | 'credits_low'         // Credits running low
  | 'new_style'           // New trending style
  | 'achievement';        // New achievement unlocked

// Handle notification tap
messaging().onNotificationOpenedApp((remoteMessage) => {
  const { type, data } = remoteMessage.data;
  
  switch (type) {
    case 'battle_started':
    case 'battle_won':
      navigation.navigate('Battles');
      break;
    case 'creation_liked':
      navigation.navigate('CreationDetail', { id: data.creation_id });
      break;
    case 'credits_low':
      navigation.navigate('BuyCredits');
      break;
  }
});
```

---

## Analytics & Tracking

### Event Tracking

```typescript
// src/services/analytics.ts
import analytics from '@react-native-firebase/analytics';

export const Analytics = {
  // Screen views
  logScreenView: (screenName: string) => {
    analytics().logScreenView({ screen_name: screenName });
  },
  
  // Auth events
  logSignUp: (method: 'email' | 'google' | 'apple') => {
    analytics().logSignUp({ method });
  },
  
  logLogin: (method: string) => {
    analytics().logLogin({ method });
  },
  
  // Creation events
  logGeneration: (styleId: number, styleName: string) => {
    analytics().logEvent('image_generated', {
      style_id: styleId,
      style_name: styleName,
    });
  },
  
  // Credits events
  logAdWatch: () => {
    analytics().logEvent('ad_watched', { credits_earned: 50 });
  },
  
  logPurchase: (packageId: number, amount: number, currency: string) => {
    analytics().logPurchase({
      value: amount,
      currency,
      items: [{ item_id: `pack_${packageId}` }],
    });
  },
  
  // Battle events
  logVote: (battleId: number) => {
    analytics().logEvent('battle_vote', { battle_id: battleId });
  },
  
  logBattleEnter: (creationId: number) => {
    analytics().logEvent('battle_enter', { creation_id: creationId });
  },
  
  // User properties
  setUserCredits: (credits: number) => {
    analytics().setUserProperty('credits_balance', credits.toString());
  },
  
  setUserCreationsCount: (count: number) => {
    analytics().setUserProperty('creations_count', count.toString());
  },
};
```

---

## Testing Requirements

### Backend Tests

```python
# tests/test_auth.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_signup():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/auth/signup", json={
            "email": "test@example.com",
            "password": "SecurePass123",
            "name": "Test User"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["data"]["user"]["credits"] == 2500
        assert "access_token" in data["data"]

@pytest.mark.asyncio
async def test_signup_weak_password():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/auth/signup", json={
            "email": "test@example.com",
            "password": "weak",
            "name": "Test User"
        })
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "WEAK_PASSWORD"

# tests/test_generation.py
@pytest.mark.asyncio
async def test_generate_insufficient_credits():
    # Setup user with 0 credits
    user = await create_test_user(credits=0)
    token = create_access_token(user)
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/creations/generate",
            headers={"Authorization": f"Bearer {token}"},
            files={"image": ("test.jpg", test_image, "image/jpeg")},
            data={"style_id": 1}
        )
        assert response.status_code == 402
        assert response.json()["error"]["code"] == "INSUFFICIENT_CREDITS"
```

### Mobile Tests

```typescript
// __tests__/api.test.ts
describe('API Service', () => {
  it('should login successfully', async () => {
    const response = await api.login({
      email: 'test@example.com',
      password: 'password123',
    });
    
    expect(response.success).toBe(true);
    expect(response.data.user).toBeDefined();
    expect(response.data.access_token).toBeDefined();
  });
  
  it('should handle invalid credentials', async () => {
    await expect(api.login({
      email: 'wrong@example.com',
      password: 'wrongpass',
    })).rejects.toThrow();
  });
});

// __tests__/components/CreditDisplay.test.tsx
describe('CreditDisplay', () => {
  it('shows low credits warning when below 100', () => {
    render(<CreditDisplay balance={50} />);
    expect(screen.getByText(/running low/i)).toBeTruthy();
  });
});
```

---

## Deployment Checklist

### Backend Deployment

- [ ] **Infrastructure**
  - [ ] PostgreSQL database (RDS/Cloud SQL)
  - [ ] Redis instance for caching/queues
  - [ ] S3 bucket or Cloudinary account
  - [ ] SSL certificates configured
  
- [ ] **API Configuration**
  - [ ] Environment variables set
  - [ ] CORS origins configured
  - [ ] Rate limiting enabled (100 req/min/user)
  - [ ] Request logging enabled
  
- [ ] **External Services**
  - [ ] Gemini API key configured
  - [ ] Razorpay keys (test → production)
  - [ ] Firebase Cloud Messaging setup
  - [ ] AdMob verification enabled
  
- [ ] **Security**
  - [ ] JWT secret key generated (256-bit)
  - [ ] Password hashing verified (bcrypt)
  - [ ] SQL injection prevention tested
  - [ ] File upload validation tested
  - [ ] NSFW detection enabled
  
- [ ] **Monitoring**
  - [ ] Sentry error tracking
  - [ ] Application metrics (Prometheus)
  - [ ] Database monitoring
  - [ ] API latency alerts
  
- [ ] **Database**
  - [ ] Migrations applied
  - [ ] Indexes created
  - [ ] Backup schedule configured
  - [ ] Connection pooling enabled

### Mobile Release

- [ ] **Configuration**
  - [ ] Production API URL set
  - [ ] Analytics in production mode
  - [ ] Crash reporting enabled
  
- [ ] **Store Preparation**
  - [ ] App icons (all sizes)
  - [ ] Screenshots (all devices)
  - [ ] Privacy policy URL
  - [ ] Terms of service URL
  
- [ ] **Testing**
  - [ ] Full E2E test pass
  - [ ] Payment flow tested
  - [ ] Deep links working
  - [ ] Push notifications working

---

## Summary

This document covers all backend requirements and frontend integration patterns for MagicPic. Key points:

1. **Authentication**: JWT-based with refresh tokens, secure storage
2. **Core Feature**: Image generation with credit deduction, Gemini AI
3. **Gamification**: Battle system with voting and leaderboards
4. **Monetization**: Ad rewards (50 credits) + credit purchases
5. **Caching**: React Query with appropriate TTLs
6. **Real-time**: WebSocket for battle updates
7. **Analytics**: Firebase for tracking user behavior

For questions or clarifications, contact the development team.
