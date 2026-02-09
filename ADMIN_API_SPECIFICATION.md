# MagicPic Admin Panel - API Specification

> **Complete API documentation for the Admin Panel backend implementation**  
> This document provides all the information needed to implement the Admin APIs for the MagicPic application.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Admin Database Schema](#admin-database-schema)
3. [Authentication & Authorization](#authentication--authorization)
4. [API Contracts](#api-contracts)
   - [Admin Authentication](#1-admin-authentication)
   - [User Management](#2-user-management-apis)
   - [Credits Management](#3-credits-management-apis)
   - [Styles Management](#4-styles-management-apis)
   - [Creations Management](#5-creations-management-apis)
   - [Categories Management](#6-categories-management-apis)
   - [Analytics & Reports](#7-analytics--reports-apis)
   - [System Settings](#8-system-settings-apis)
5. [Error Codes](#error-codes)
6. [Implementation Checklist](#implementation-checklist)

---

## Overview

The Admin Panel provides comprehensive management capabilities for the MagicPic platform. The admin should be able to:

- ✅ **User Management**: View all users, manage their accounts, credits, and permissions
- ✅ **Credits Management**: Add/deduct credits, view transaction history, set credit policies
- ✅ **Styles Management**: Create, edit, delete AI styles and their prompts
- ✅ **Creations Management**: View, moderate, feature or delete user creations
- ✅ **Categories Management**: Create and manage style categories
- ✅ **Analytics**: View platform statistics, revenue, user engagement metrics
- ✅ **Content Moderation**: Review flagged content, manage reports

### Base URL

```
Production: https://api.magicpic.app/api/admin
Development: http://localhost:8000/api/admin
```

### Global Headers

```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer <admin_access_token>",
  "X-Admin-ID": "<admin_user_id>",
  "X-Request-ID": "<unique_request_id>"
}
```

---

## Admin Database Schema

First, extend the existing database schema with admin-specific tables:

```sql
-- ============================================================
-- ADMIN TABLES
-- ============================================================

-- 1. Admins Table
CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('super_admin', 'admin', 'moderator')),
    permissions JSON DEFAULT '[]',  -- Array of permission strings
    created_by INTEGER REFERENCES admins(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_admins_user_id ON admins(user_id);
CREATE INDEX idx_admins_role ON admins(role);

COMMENT ON TABLE admins IS 'Admin users with special permissions';
COMMENT ON COLUMN admins.role IS 'super_admin (full access), admin (most access), moderator (limited)';
COMMENT ON COLUMN admins.permissions IS 'JSON array of specific permissions like ["users.create", "credits.manage"]';

-- 2. Admin Activity Logs
CREATE TABLE admin_activity_logs (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER NOT NULL REFERENCES admins(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,  -- 'user.created', 'credits.added', 'style.deleted', etc.
    resource_type VARCHAR(50) NOT NULL,  -- 'user', 'style', 'creation', 'credits'
    resource_id INTEGER,
    details JSON,  -- Additional context about the action
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_admin_logs_admin_id ON admin_activity_logs(admin_id);
CREATE INDEX idx_admin_logs_action ON admin_activity_logs(action);
CREATE INDEX idx_admin_logs_resource ON admin_activity_logs(resource_type, resource_id);
CREATE INDEX idx_admin_logs_created_at ON admin_activity_logs(created_at DESC);

COMMENT ON TABLE admin_activity_logs IS 'Audit log of all admin actions for security and compliance';

-- 3. System Settings
CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSON NOT NULL,
    description VARCHAR(500),
    updated_by INTEGER REFERENCES admins(id) ON DELETE SET NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_system_settings_key ON system_settings(key);

COMMENT ON TABLE system_settings IS 'System-wide configuration settings';

-- Sample settings
INSERT INTO system_settings (key, value, description) VALUES
('credits.signup_bonus', '2500', 'Initial credits given on signup'),
('credits.ad_watch_reward', '50', 'Credits earned per ad watch'),
('credits.max_ads_per_day', '5', 'Maximum ads a user can watch per day'),
('credits.referral_bonus', '500', 'Credits for successful referral'),
('creation.default_cost', '50', 'Default credits cost for image generation'),
('features.battles_enabled', 'true', 'Enable/disable battles feature'),
('features.maintenance_mode', 'false', 'Put app in maintenance mode');

-- 4. Content Reports (for moderation)
CREATE TABLE content_reports (
    id SERIAL PRIMARY KEY,
    reporter_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reported_creation_id INTEGER REFERENCES creations(id) ON DELETE CASCADE,
    reason VARCHAR(50) NOT NULL CHECK (reason IN ('nsfw', 'spam', 'copyright', 'harassment', 'other')),
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'reviewing', 'resolved', 'dismissed')),
    reviewed_by INTEGER REFERENCES admins(id) ON DELETE SET NULL,
    resolution_note TEXT,
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reports_status ON content_reports(status);
CREATE INDEX idx_reports_creation ON content_reports(reported_creation_id);
CREATE INDEX idx_reports_created_at ON content_reports(created_at DESC);

-- 5. Trigger for admin updated_at
CREATE TRIGGER update_admins_updated_at
    BEFORE UPDATE ON admins
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_settings_updated_at
    BEFORE UPDATE ON system_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## Authentication & Authorization

### Admin Roles & Permissions

```typescript
enum AdminRole {
  SUPER_ADMIN = 'super_admin',  // Full access to everything
  ADMIN = 'admin',                // Can manage users, styles, credits
  MODERATOR = 'moderator'         // Can only moderate content
}

// Permission strings
const PERMISSIONS = {
  // User Management
  'users.view': 'View user list and details',
  'users.create': 'Create new users',
  'users.edit': 'Edit user information',
  'users.delete': 'Delete users',
  'users.verify': 'Verify user accounts',
  
  // Credits Management
  'credits.view': 'View credit transactions',
  'credits.add': 'Add credits to users',
  'credits.deduct': 'Deduct credits from users',
  'credits.refund': 'Refund credits',
  
  // Styles Management
  'styles.view': 'View all styles',
  'styles.create': 'Create new styles',
  'styles.edit': 'Edit existing styles',
  'styles.delete': 'Delete styles',
  
  // Creations Management
  'creations.view': 'View all creations',
  'creations.feature': 'Feature/unfeature creations',
  'creations.delete': 'Delete creations',
  'creations.moderate': 'Moderate reported content',
  
  // Categories Management
  'categories.view': 'View categories',
  'categories.create': 'Create categories',
  'categories.edit': 'Edit categories',
  'categories.delete': 'Delete categories',
  
  // Analytics
  'analytics.view': 'View analytics and reports',
  
  // System
  'system.settings': 'Manage system settings',
  'admins.manage': 'Manage admin users'
};

// Default permissions by role
const ROLE_PERMISSIONS = {
  super_admin: Object.keys(PERMISSIONS),  // All permissions
  admin: [
    'users.view', 'users.create', 'users.edit', 'users.verify',
    'credits.view', 'credits.add', 'credits.deduct',
    'styles.view', 'styles.create', 'styles.edit',
    'creations.view', 'creations.feature', 'creations.moderate',
    'categories.view', 'categories.create', 'categories.edit',
    'analytics.view'
  ],
  moderator: [
    'users.view',
    'creations.view', 'creations.moderate',
    'analytics.view'
  ]
};
```

### Admin Login Flow

```
1. Admin logs in with their USER credentials
2. Backend checks if user_id exists in admins table and is_active=true
3. Generate admin_access_token with admin_id and role in payload
4. Return token + admin profile
```

---

## API Contracts

---

## 1. Admin Authentication

### POST `/api/admin/auth/login`

**Purpose**: Authenticate admin user

```typescript
// Request
interface AdminLoginRequest {
  email: string;
  password: string;
  device_info?: {
    device_name: string;
    ip_address: string;
    user_agent: string;
  };
}

// Response (Success - 200)
interface AdminLoginResponse {
  success: true;
  data: {
    admin: {
      id: number;
      user_id: number;
      email: string;
      name: string;
      avatar_url: string | null;
      role: 'super_admin' | 'admin' | 'moderator';
      permissions: string[];
      created_at: string;
      last_login: string;
    };
    access_token: string;
    refresh_token: string;
    token_type: 'bearer';
    expires_in: number;  // 3600 (1 hour)
  };
}

// Errors
type AdminLoginErrors =
  | 'INVALID_CREDENTIALS'     // 401 - Wrong email/password
  | 'NOT_ADMIN'               // 403 - User is not an admin
  | 'ADMIN_INACTIVE'          // 403 - Admin account is deactivated
  | 'ACCOUNT_LOCKED';         // 403 - Too many failed attempts

// Error Response Example
{
  "success": false,
  "error": {
    "code": "NOT_ADMIN",
    "message": "You do not have admin privileges"
  }
}
```

### POST `/api/admin/auth/verify-token`

**Purpose**: Verify admin token validity

```typescript
// Headers
Authorization: Bearer <admin_access_token>

// Response (Success - 200)
{
  "success": true,
  "data": {
    "valid": true,
    "admin_id": 1,
    "role": "super_admin",
    "expires_at": "2024-03-20T15:30:00Z"
  }
}
```

---

## 2. User Management APIs

### GET `/api/admin/users`

**Purpose**: Get paginated list of all users with filters

```typescript
// Query Parameters
interface GetUsersQuery {
  page?: number;                    // Default: 1
  limit?: number;                   // Default: 50, Max: 100
  search?: string;                  // Search by name, email, phone
  is_verified?: boolean;            // Filter by verification status
  is_active?: boolean;              // Filter by active status
  min_credits?: number;             // Users with credits >= value
  max_credits?: number;             // Users with credits <= value
  sort_by?: 'created_at' | 'credits' | 'name' | 'last_login';
  sort_order?: 'asc' | 'desc';      // Default: desc
  created_after?: string;           // ISO date
  created_before?: string;          // ISO date
}

// Response
interface GetUsersResponse {
  success: true;
  data: {
    users: Array<{
      id: number;
      email: string;
      name: string;
      phone: string | null;
      avatar_url: string | null;
      credits: number;
      is_verified: boolean;
      is_active: boolean;
      referral_code: string;
      referred_by: {
        id: number;
        name: string;
      } | null;
      stats: {
        creations_count: number;
        total_spent: number;        // Total credits spent
        total_earned: number;       // Total credits earned (referrals, ads)
        last_generation: string | null;  // ISO date of last creation
      };
      last_login: string | null;
      created_at: string;
      updated_at: string;
    }>;
    pagination: {
      page: number;
      limit: number;
      total: number;
      total_pages: number;
      has_next: boolean;
      has_prev: boolean;
    };
    summary: {
      total_users: number;
      active_users: number;
      verified_users: number;
      total_credits_in_system: number;
    };
  };
}

// Example Request
GET /api/admin/users?page=1&limit=50&search=john&is_verified=true&sort_by=created_at&sort_order=desc
```

### GET `/api/admin/users/{id}`

**Purpose**: Get detailed information about a specific user

```typescript
// Response
interface GetUserDetailResponse {
  success: true;
  data: {
    user: {
      id: number;
      email: string;
      name: string;
      phone: string | null;
      avatar_url: string | null;
      credits: number;
      is_verified: boolean;
      is_active: boolean;
      referral_code: string;
      referred_by: {
        id: number;
        name: string;
        email: string;
      } | null;
      referred_users: Array<{
        id: number;
        name: string;
        email: string;
        created_at: string;
      }>;
      last_login: string | null;
      created_at: string;
      updated_at: string;
    };
    stats: {
      total_creations: number;
      public_creations: number;
      private_creations: number;
      deleted_creations: number;
      total_likes_received: number;
      total_likes_given: number;
      battle_wins: number;
      battle_losses: number;
      battle_win_rate: number;     // Percentage
      votes_cast: number;
      total_credits_earned: number;
      total_credits_spent: number;
      net_credits: number;          // earned - spent
    };
    recent_activity: {
      recent_creations: Array<{
        id: number;
        style_name: string;
        thumbnail_url: string;
        credits_used: number;
        created_at: string;
      }>;  // Last 10
      recent_transactions: Array<{
        id: number;
        type: string;
        amount: number;
        description: string;
        balance_after: number;
        created_at: string;
      }>;  // Last 20
      recent_logins: Array<{
        timestamp: string;
        ip_address: string;
        device_info: string;
      }>;  // Last 10
    };
  };
}
```

### POST `/api/admin/users`

**Purpose**: Create new user from admin panel

```typescript
// Request
interface CreateUserRequest {
  email: string;
  password: string;
  name: string;
  phone?: string;
  credits?: number;               // Default: 2500
  is_verified?: boolean;          // Default: true (admin-created)
  is_active?: boolean;            // Default: true
  referral_code?: string;         // Auto-generated if not provided
}

// Response (Success - 201)
interface CreateUserResponse {
  success: true;
  data: {
    user: User;
    initial_credits: number;
    send_welcome_email: boolean;
  };
  message: 'User created successfully';
}

// Errors
type CreateUserErrors =
  | 'EMAIL_EXISTS'          // 409
  | 'INVALID_EMAIL'         // 400
  | 'WEAK_PASSWORD'         // 400
  | 'PERMISSION_DENIED';    // 403
```

### PUT `/api/admin/users/{id}`

**Purpose**: Update user information

```typescript
// Request
interface UpdateUserRequest {
  email?: string;
  name?: string;
  phone?: string;
  is_verified?: boolean;
  is_active?: boolean;
  avatar_url?: string;
}

// Response
{
  "success": true,
  "data": {
    "user": User,
    "changes": {
      "field": "old_value -> new_value"
    }
  },
  "message": "User updated successfully"
}
```

### DELETE `/api/admin/users/{id}`

**Purpose**: Soft delete user account

```typescript
// Response
{
  "success": true,
  "data": {
    "user_id": 123,
    "deleted_at": "2024-03-20T10:30:00Z",
    "cleanup_summary": {
      "creations_deleted": 45,
      "likes_removed": 23,
      "votes_removed": 67
    }
  },
  "message": "User account deleted successfully"
}

// Note: This should set is_active=false, not actually delete the record
// Keep data for audit purposes
```

### POST `/api/admin/users/{id}/reset-password`

**Purpose**: Force reset user password

```typescript
// Request
interface ResetPasswordRequest {
  new_password: string;
  send_email?: boolean;     // Send new password to user, default: true
}

// Response
{
  "success": true,
  "message": "Password reset successfully. Email sent to user."
}
```

### POST `/api/admin/users/{id}/verify`

**Purpose**: Manually verify user account

```typescript
// Response
{
  "success": true,
  "data": {
    "user_id": 123,
    "is_verified": true,
    "verified_at": "2024-03-20T10:30:00Z"
  },
  "message": "User verified successfully"
}
```

---

## 3. Credits Management APIs

### GET `/api/admin/credits/transactions`

**Purpose**: Get all credit transactions with filters

```typescript
// Query Parameters
interface GetTransactionsQuery {
  user_id?: number;
  type?: 'signup_bonus' | 'ad_watch' | 'purchase' | 'creation' | 'referral' | 'battle_win' | 'admin_adjustment';
  start_date?: string;          // ISO date
  end_date?: string;            // ISO date
  min_amount?: number;
  max_amount?: number;
  page?: number;
  limit?: number;
  sort_by?: 'created_at' | 'amount';
  sort_order?: 'asc' | 'desc';
}

// Response
interface GetTransactionsResponse {
  success: true;
  data: {
    transactions: Array<{
      id: number;
      user_id: number;
      user_name: string;
      user_email: string;
      amount: number;               // Positive = earned, Negative = spent
      type: string;
      description: string;
      reference_id: string | null;
      balance_before: number;
      balance_after: number;
      created_at: string;
    }>;
    pagination: Pagination;
    summary: {
      total_transactions: number;
      total_credits_added: number;
      total_credits_spent: number;
      net_change: number;
      breakdown_by_type: {
        [type: string]: {
          count: number;
          total_amount: number;
        };
      };
    };
  };
}
```

### POST `/api/admin/credits/add`

**Purpose**: Add credits to a user

```typescript
// Request
interface AddCreditsRequest {
  user_id: number;
  amount: number;               // Must be positive
  reason: string;               // Description for the transaction
  reference_id?: string;        // Optional reference (e.g., ticket ID)
  notify_user?: boolean;        // Send notification, default: true
}

// Response (Success - 200)
{
  "success": true,
  "data": {
    "transaction_id": 456,
    "user_id": 123,
    "amount": 500,
    "balance_before": 1200,
    "balance_after": 1700,
    "description": "Admin adjustment: Refund for failed generation",
    "created_at": "2024-03-20T10:30:00Z"
  },
  "message": "500 credits added to user successfully"
}

// Errors
type AddCreditsErrors =
  | 'USER_NOT_FOUND'        // 404
  | 'INVALID_AMOUNT'        // 400 - amount <= 0
  | 'PERMISSION_DENIED';    // 403
```

### POST `/api/admin/credits/deduct`

**Purpose**: Deduct credits from a user

```typescript
// Request
interface DeductCreditsRequest {
  user_id: number;
  amount: number;               // Must be positive
  reason: string;
  reference_id?: string;
  notify_user?: boolean;
  force?: boolean;              // Allow negative balance, default: false
}

// Response
{
  "success": true,
  "data": {
    "transaction_id": 457,
    "user_id": 123,
    "amount": -200,
    "balance_before": 1700,
    "balance_after": 1500,
    "description": "Admin adjustment: Abuse penalty",
    "created_at": "2024-03-20T10:30:00Z"
  },
  "message": "200 credits deducted from user successfully"
}

// Errors
type DeductCreditsErrors =
  | 'USER_NOT_FOUND'          // 404
  | 'INVALID_AMOUNT'          // 400
  | 'INSUFFICIENT_CREDITS'    // 400 - User doesn't have enough (when force=false)
  | 'PERMISSION_DENIED';      // 403
```

### GET `/api/admin/credits/stats`

**Purpose**: Get overall credits statistics

```typescript
// Query Parameters
interface GetCreditsStatsQuery {
  period?: 'today' | 'week' | 'month' | 'year' | 'all';
}

// Response
interface GetCreditsStatsResponse {
  success: true;
  data: {
    period: string;
    overview: {
      total_credits_in_system: number;      // Sum of all user balances
      total_credits_issued: number;         // Total ever given out
      total_credits_spent: number;          // Total ever spent
      average_balance_per_user: number;
      users_with_zero_balance: number;
      users_with_negative_balance: number;  // Should be 0 normally
    };
    transactions: {
      total_count: number;
      by_type: {
        signup_bonus: { count: number; total_amount: number };
        ad_watch: { count: number; total_amount: number };
        purchase: { count: number; total_amount: number };
        creation: { count: number; total_amount: number };
        referral: { count: number; total_amount: number };
        battle_win: { count: number; total_amount: number };
        admin_adjustment: { count: number; total_amount: number };
      };
    };
    trends: {
      daily_credits_spent: Array<{
        date: string;
        amount: number;
      }>;  // Last 30 days
      daily_credits_earned: Array<{
        date: string;
        amount: number;
      }>;  // Last 30 days
    };
  };
}
```

---

## 4. Styles Management APIs

### GET `/api/admin/styles`

**Purpose**: Get all styles with admin-specific details

```typescript
// Query Parameters
interface GetStylesQuery {
  category_id?: number;
  is_active?: boolean;
  is_trending?: boolean;
  is_new?: boolean;
  search?: string;
  sort_by?: 'created_at' | 'uses_count' | 'name';
  sort_order?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}

// Response
interface GetStylesAdminResponse {
  success: true;
  data: {
    styles: Array<{
      id: number;
      name: string;
      description: string;
      category: {
        id: number;
        name: string;
        slug: string;
      };
      preview_url: string;
      prompt_template: string;      // Full prompt visible to admin
      negative_prompt: string | null;
      tags: string[];
      credits_required: number;
      uses_count: number;
      is_trending: boolean;
      is_new: boolean;
      is_active: boolean;
      display_order: number;
      created_at: string;
      updated_at: string;
      stats: {
        total_uses: number;
        unique_users: number;
        avg_rating: number | null;
        total_likes_on_creations: number;
      };
    }>;
    pagination: Pagination;
  };
}
```

### GET `/api/admin/styles/{id}`

**Purpose**: Get detailed style information

```typescript
// Response
interface GetStyleDetailAdminResponse {
  success: true;
  data: {
    style: {
      id: number;
      name: string;
      description: string;
      category_id: number;
      category: Category;
      preview_url: string;
      prompt_template: string;
      negative_prompt: string | null;
      tags: string[];
      credits_required: number;
      uses_count: number;
      is_trending: boolean;
      is_new: boolean;
      is_active: boolean;
      display_order: number;
      created_at: string;
      updated_at: string;
    };
    usage_stats: {
      total_uses: number;
      unique_users: number;
      uses_this_week: number;
      uses_this_month: number;
      peak_usage_day: {
        date: string;
        count: number;
      };
      usage_trend: Array<{
        date: string;
        count: number;
      }>;  // Last 30 days
    };
    top_creations: Array<{
      id: number;
      thumbnail_url: string;
      likes_count: number;
      created_at: string;
    }>;  // Top 10 most liked
  };
}
```

### POST `/api/admin/styles`

**Purpose**: Create new AI style

```typescript
// Request (multipart/form-data)
interface CreateStyleRequest {
  category_id: number;
  name: string;                     // Max 100 chars
  description: string;              // Max 500 chars
  preview_image: File;              // Image file for preview
  prompt_template: string;          // AI prompt template
  negative_prompt?: string;
  tags?: string[];                  // For search
  credits_required?: number;        // Default: 50
  is_trending?: boolean;            // Default: false
  is_new?: boolean;                 // Default: true
  is_active?: boolean;              // Default: true
  display_order?: number;          // Default: 0
}

// Response (Success - 201)
{
  "success": true,
  "data": {
    "style": Style,
    "preview_url": "https://cdn.magicpic.app/styles/preview-123.jpg"
  },
  "message": "Style created successfully"
}

// Errors
type CreateStyleErrors =
  | 'CATEGORY_NOT_FOUND'      // 404
  | 'INVALID_PREVIEW_IMAGE'   // 400
  | 'DUPLICATE_NAME'          // 409
  | 'INVALID_PROMPT'          // 400
  | 'PERMISSION_DENIED';      // 403
```

### PUT `/api/admin/styles/{id}`

**Purpose**: Update existing style

```typescript
// Request (multipart/form-data)
interface UpdateStyleRequest {
  category_id?: number;
  name?: string;
  description?: string;
  preview_image?: File;             // New preview image
  prompt_template?: string;
  negative_prompt?: string;
  tags?: string[];
  credits_required?: number;
  is_trending?: boolean;
  is_new?: boolean;
  is_active?: boolean;
  display_order?: number;
}

// Response
{
  "success": true,
  "data": {
    "style": Style,
    "changes": {
      "prompt_template": "old_value -> new_value",
      "credits_required": "50 -> 75"
    }
  },
  "message": "Style updated successfully"
}
```

### DELETE `/api/admin/styles/{id}`

**Purpose**: Delete style (soft delete if creations exist)

```typescript
// Query Parameters
?force=true  // Force delete even if creations exist

// Response
{
  "success": true,
  "data": {
    "style_id": 45,
    "deleted_at": "2024-03-20T10:30:00Z",
    "creations_affected": 234,  // Number of creations using this style
    "action_taken": "soft_delete"  // or "hard_delete" if no creations
  },
  "message": "Style deleted successfully"
}

// Error if has creations and force=false
{
  "success": false,
  "error": {
    "code": "STYLE_IN_USE",
    "message": "Cannot delete style with existing creations. Use force=true to soft delete.",
    "details": {
      "creations_count": 234
    }
  }
}
```

### POST `/api/admin/styles/{id}/toggle-trending`

**Purpose**: Toggle trending status

```typescript
// Response
{
  "success": true,
  "data": {
    "style_id": 45,
    "is_trending": true
  },
  "message": "Style marked as trending"
}
```

### POST `/api/admin/styles/{id}/duplicate`

**Purpose**: Create a copy of existing style

```typescript
// Request
{
  "new_name": "Style Name Copy",
  "category_id"?: number  // Optional, use original if not provided
}

// Response
{
  "success": true,
  "data": {
    "original_style_id": 45,
    "new_style": Style
  },
  "message": "Style duplicated successfully"
}
```

---

## 5. Creations Management APIs

### GET `/api/admin/creations`

**Purpose**: Get all creations with admin filters

```typescript
// Query Parameters
interface GetCreationsAdminQuery {
  user_id?: number;
  style_id?: number;
  is_public?: boolean;
  is_featured?: boolean;
  is_deleted?: boolean;
  min_likes?: number;
  max_likes?: number;
  created_after?: string;
  created_before?: string;
  sort_by?: 'created_at' | 'likes_count' | 'views_count';
  sort_order?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}

// Response
interface GetCreationsAdminResponse {
  success: true;
  data: {
    creations: Array<{
      id: number;
      user: {
        id: number;
        name: string;
        email: string;
      };
      style: {
        id: number;
        name: string;
      };
      original_image_url: string;
      generated_image_url: string;
      thumbnail_url: string;
      prompt_used: string;          // Full prompt
      mood: string | null;
      weather: string | null;
      dress_style: string | null;
      custom_prompt: string | null;
      credits_used: number;
      processing_time: number;
      likes_count: number;
      views_count: number;
      is_public: boolean;
      is_featured: boolean;
      is_deleted: boolean;
      reports_count: number;        // Number of reports
      created_at: string;
    }>;
    pagination: Pagination;
    summary: {
      total_creations: number;
      public_creations: number;
      featured_creations: number;
      deleted_creations: number;
      reported_creations: number;
    };
  };
}
```

### GET `/api/admin/creations/{id}`

**Purpose**: Get detailed creation information

```typescript
// Response
interface GetCreationDetailAdminResponse {
  success: true;
  data: {
    creation: {
      id: number;
      user: User;
      style: Style;
      original_image_url: string;
      generated_image_url: string;
      thumbnail_url: string;
      prompt_used: string;
      mood: string | null;
      weather: string | null;
      dress_style: string | null;
      custom_prompt: string | null;
      credits_used: number;
      processing_time: number;
      likes_count: number;
      views_count: number;
      is_public: boolean;
      is_featured: boolean;
      is_deleted: boolean;
      created_at: string;
    };
    analytics: {
      total_likes: number;
      total_views: number;
      unique_viewers: number;
      engagement_rate: number;      // (likes + views) / impressions
      shares_count: number;
    };
    reports: Array<{
      id: number;
      reporter: {
        id: number;
        name: string;
        email: string;
      };
      reason: string;
      description: string;
      status: string;
      created_at: string;
    }>;
    battles: Array<{
      id: number;
      opponent_creation_id: number;
      votes_received: number;
      opponent_votes: number;
      status: string;
      is_winner: boolean;
    }>;
  };
}
```

### PUT `/api/admin/creations/{id}/feature`

**Purpose**: Feature/unfeature creation

```typescript
// Request
{
  "is_featured": true
}

// Response
{
  "success": true,
  "data": {
    "creation_id": 123,
    "is_featured": true
  },
  "message": "Creation featured successfully"
}
```

### DELETE `/api/admin/creations/{id}`

**Purpose**: Delete creation (admin override)

```typescript
// Request
{
  "reason": "Violates community guidelines",
  "notify_user": true
}

// Response
{
  "success": true,
  "data": {
    "creation_id": 123,
    "deleted_at": "2024-03-20T10:30:00Z",
    "user_notified": true
  },
  "message": "Creation deleted successfully"
}
```

### GET `/api/admin/creations/reported`

**Purpose**: Get creations with pending reports

```typescript
// Query Parameters
{
  "status": "pending" | "reviewing" | "resolved" | "dismissed",
  "reason": "nsfw" | "spam" | "copyright" | "harassment" | "other",
  "page": number,
  "limit": number
}

// Response
interface GetReportedCreationsResponse {
  success: true;
  data: {
    reports: Array<{
      id: number;
      creation: Creation;
      reporter: User;
      reason: string;
      description: string;
      status: string;
      created_at: string;
      reports_count: number;  // Total reports for this creation
    }>;
    pagination: Pagination;
    summary: {
      pending_reports: number;
      reviewing_reports: number;
      total_unique_creations: number;
    };
  };
}
```

### POST `/api/admin/creations/reports/{id}/resolve`

**Purpose**: Resolve content report

```typescript
// Request
{
  "status": "resolved" | "dismissed",
  "action": "delete_creation" | "warn_user" | "no_action",
  "resolution_note": "Reviewed content, found to violate policy X"
}

// Response
{
  "success": true,
  "data": {
    "report_id": 456,
    "status": "resolved",
    "action_taken": "delete_creation",
    "reviewed_by": 1,
    "reviewed_at": "2024-03-20T10:30:00Z"
  },
  "message": "Report resolved successfully"
}
```

---

## 6. Categories Management APIs

### GET `/api/admin/categories`

**Purpose**: Get all categories with admin details

```typescript
// Response
interface GetCategoriesAdminResponse {
  success: true;
  data: {
    categories: Array<{
      id: number;
      name: string;
      slug: string;
      icon: string;
      description: string;
      preview_url: string;
      display_order: number;
      is_active: boolean;
      created_at: string;
      stats: {
        styles_count: number;
        total_uses: number;          // All styles in category
        active_styles: number;
      };
    }>;
  };
}
```

### POST `/api/admin/categories`

**Purpose**: Create new category

```typescript
// Request (multipart/form-data)
interface CreateCategoryRequest {
  name: string;                     // "Wedding"
  slug?: string;                    // Auto-generated if not provided
  icon: string;                     // "💒" or icon name
  description: string;              // "Invitation & Cards"
  preview_image?: File;             // Category preview
  display_order?: number;
  is_active?: boolean;
}

// Response (Success - 201)
{
  "success": true,
  "data": {
    "category": Category
  },
  "message": "Category created successfully"
}
```

### PUT `/api/admin/categories/{id}`

**Purpose**: Update category

```typescript
// Request
interface UpdateCategoryRequest {
  name?: string;
  slug?: string;
  icon?: string;
  description?: string;
  preview_image?: File;
  display_order?: number;
  is_active?: boolean;
}

// Response
{
  "success": true,
  "data": {
    "category": Category,
    "changes": {...}
  },
  "message": "Category updated successfully"
}
```

### DELETE `/api/admin/categories/{id}`

**Purpose**: Delete category

```typescript
// Query
?force=true  // Delete even if has styles

// Response
{
  "success": true,
  "data": {
    "category_id": 5,
    "deleted_at": "2024-03-20T10:30:00Z",
    "styles_affected": 12
  },
  "message": "Category deleted successfully"
}

// Error if has styles and force=false
{
  "success": false,
  "error": {
    "code": "CATEGORY_HAS_STYLES",
    "message": "Cannot delete category with existing styles",
    "details": {
      "styles_count": 12
    }
  }
}
```

### POST `/api/admin/categories/{id}/reorder`

**Purpose**: Reorder category display order

```typescript
// Request
{
  "new_order": 3
}

// Response
{
  "success": true,
  "data": {
    "category_id": 5,
    "old_order": 5,
    "new_order": 3
  },
  "message": "Category reordered successfully"
}
```

---

## 7. Analytics & Reports APIs

### GET `/api/admin/analytics/dashboard`

**Purpose**: Get overview analytics for admin dashboard

```typescript
// Query Parameters
{
  "period": "today" | "week" | "month" | "year" | "all"
}

// Response
interface GetDashboardAnalyticsResponse {
  success: true;
  data: {
    period: string;
    users: {
      total: number;
      new_signups: number;
      active_users: number;          // Users who generated in period
      verified_users: number;
      growth_rate: number;            // Percentage
    };
    creations: {
      total: number;
      public: number;
      private: number;
      featured: number;
      avg_per_user: number;
    };
    credits: {
      total_in_system: number;
      issued: number;
      spent: number;
      avg_balance: number;
    };
    styles: {
      total: number;
      active: number;
      trending: number;
      most_popular: Array<{
        id: number;
        name: string;
        uses_count: number;
      }>;  // Top 5
    };
    battles: {
      total: number;
      active: number;
      completed: number;
      total_votes: number;
    };
    reports: {
      total: number;
      pending: number;
      resolved: number;
      dismissed: number;
    };
    revenue: {
      total: number;              // If payment integration exists
      this_period: number;
      growth: number;
    };
    system_health: {
      avg_generation_time: number;   // Seconds
      success_rate: number;           // Percentage
      error_rate: number;
      uptime: number;                 // Percentage
    };
  };
}
```

### GET `/api/admin/analytics/users`

**Purpose**: Detailed user analytics

```typescript
// Query Parameters
{
  "period": "week" | "month" | "year",
  "metric": "signups" | "active_users" | "retention"
}

// Response
interface GetUserAnalyticsResponse {
  success: true;
  data: {
    period: string;
    metric: string;
    chart_data: Array<{
      date: string;
      value: number;
    }>;
    insights: {
      total: number;
      average_per_day: number;
      peak_day: {
        date: string;
        value: number;
      };
      trend: "up" | "down" | "stable";
      change_percentage: number;
    };
    demographics: {
      by_platform: {
        android: number;
        ios: number;
        web: number;
      };
      by_verification_status: {
        verified: number;
        unverified: number;
      };
      by_activity: {
        very_active: number;      // >10 creations
        active: number;           // 3-10 creations
        occasional: number;       // 1-2 creations
        inactive: number;         // 0 creations
      };
    };
  };
}
```

### GET `/api/admin/analytics/revenue`

**Purpose**: Revenue and monetization analytics

```typescript
// Query Parameters
{
  "period": "week" | "month" | "quarter" | "year"
}

// Response
interface GetRevenueAnalyticsResponse {
  success: true;
  data: {
    period: string;
    total_revenue: number;
    revenue_by_source: {
      credit_purchases: number;
      subscriptions: number;
      ads: number;
      other: number;
    };
    chart_data: Array<{
      date: string;
      revenue: number;
      transactions: number;
    }>;
    insights: {
      avg_transaction_value: number;
      total_transactions: number;
      paying_users: number;
      conversion_rate: number;       // % of users who paid
      churn_rate: number;
      ltv: number;                   // Lifetime value per user
    };
    top_purchasers: Array<{
      user_id: number;
      user_name: string;
      total_spent: number;
      transactions_count: number;
    }>;  // Top 10
  };
}
```

### GET `/api/admin/analytics/creations`

**Purpose**: Creation analytics

```typescript
// Response
interface GetCreationAnalyticsResponse {
  success: true;
  data: {
    period: string;
    total_creations: number;
    public_vs_private: {
      public: number;
      private: number;
      public_percentage: number;
    };
    by_style_category: Array<{
      category_name: string;
      count: number;
      percentage: number;
    }>;
    top_styles: Array<{
      style_id: number;
      style_name: string;
      uses_count: number;
      unique_users: number;
    }>;  // Top 10
    engagement: {
      avg_likes_per_creation: number;
      avg_views_per_creation: number;
      total_likes: number;
      total_views: number;
    };
    trends: Array<{
      date: string;
      count: number;
      avg_processing_time: number;
    }>;  // Daily for period
  };
}
```

### GET `/api/admin/analytics/export`

**Purpose**: Export analytics data

```typescript
// Query Parameters
{
  "type": "users" | "creations" | "transactions" | "all",
  "period": "week" | "month" | "year" | "all",
  "format": "csv" | "xlsx" | "json"
}

// Response (File Download)
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="analytics-export-2024-03-20.csv"

// Or JSON response with download URL
{
  "success": true,
  "data": {
    "download_url": "https://cdn.magicpic.app/exports/analytics-123.csv",
    "expires_at": "2024-03-20T15:00:00Z",
    "file_size": 2450000,
    "records_count": 15420
  }
}
```

---

## 8. System Settings APIs

### GET `/api/admin/settings`

**Purpose**: Get all system settings

```typescript
// Response
interface GetSettingsResponse {
  success: true;
  data: {
    settings: Array<{
      id: number;
      key: string;
      value: any;                   // JSON value
      description: string;
      updated_by: {
        id: number;
        name: string;
      } | null;
      updated_at: string;
    }>;
    categories: {
      credits: Array<Setting>;
      features: Array<Setting>;
      limits: Array<Setting>;
      ai: Array<Setting>;
      notifications: Array<Setting>;
    };
  };
}
```

### PUT `/api/admin/settings/{key}`

**Purpose**: Update system setting

```typescript
// Request
{
  "value": any  // New value (will be stored as JSON)
}

// Response
{
  "success": true,
  "data": {
    "key": "credits.signup_bonus",
    "old_value": 2500,
    "new_value": 3000,
    "updated_by": 1,
    "updated_at": "2024-03-20T10:30:00Z"
  },
  "message": "Setting updated successfully"
}

// Example: Enable maintenance mode
PUT /api/admin/settings/features.maintenance_mode
{
  "value": true
}
```

### GET `/api/admin/activity-logs`

**Purpose**: Get admin activity audit logs

```typescript
// Query Parameters
interface GetActivityLogsQuery {
  admin_id?: number;
  action?: string;
  resource_type?: string;
  resource_id?: number;
  start_date?: string;
  end_date?: string;
  page?: number;
  limit?: number;
}

// Response
interface GetActivityLogsResponse {
  success: true;
  data: {
    logs: Array<{
      id: number;
      admin: {
        id: number;
        name: string;
        role: string;
      };
      action: string;               // 'user.created', 'credits.added', etc.
      resource_type: string;        // 'user', 'style', 'creation'
      resource_id: number | null;
      details: any;                 // JSON with action details
      ip_address: string;
      user_agent: string;
      created_at: string;
    }>;
    pagination: Pagination;
  };
}

// Example log entry
{
  "id": 1234,
  "admin": {
    "id": 1,
    "name": "Admin User",
    "role": "super_admin"
  },
  "action": "credits.added",
  "resource_type": "user",
  "resource_id": 456,
  "details": {
    "user_email": "user@example.com",
    "amount": 500,
    "reason": "Refund for failed generation",
    "balance_before": 1200,
    "balance_after": 1700
  },
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "created_at": "2024-03-20T10:30:00Z"
}
```

---

## Error Codes

All API errors follow this format:

```typescript
interface ErrorResponse {
  success: false;
  error: {
    code: string;           // Machine-readable error code
    message: string;        // Human-readable message
    details?: any;          // Additional error context
    field?: string;         // Field that caused error (for validation)
  };
  timestamp: string;
  request_id: string;       // For debugging
}
```

### Common Error Codes

```typescript
// Authentication & Authorization
'UNAUTHORIZED'              // 401 - No/invalid token
'PERMISSION_DENIED'         // 403 - Insufficient permissions
'ADMIN_INACTIVE'            // 403 - Admin account deactivated
'INVALID_TOKEN'             // 401 - Malformed token
'TOKEN_EXPIRED'             // 401 - Token expired

// Resource Errors
'NOT_FOUND'                 // 404 - Resource doesn't exist
'ALREADY_EXISTS'            // 409 - Duplicate resource
'INVALID_INPUT'             // 400 - Validation failed
'MISSING_FIELD'             // 400 - Required field missing

// Business Logic
'INSUFFICIENT_CREDITS'      // 402 - User lacks credits
'STYLE_IN_USE'              // 400 - Can't delete used style
'CATEGORY_HAS_STYLES'       // 400 - Can't delete category with styles
'CREATION_IN_BATTLE'        // 400 - Can't delete creation in battle

// System
'INTERNAL_ERROR'            // 500 - Unexpected error
'SERVICE_UNAVAILABLE'       // 503 - Service down
'RATE_LIMITED'              // 429 - Too many requests
```

---

## Implementation Checklist

### Phase 1: Core Admin Infrastructure
- [ ] Create admin database tables
- [ ] Implement admin authentication middleware
- [ ] Set up role-based access control (RBAC)
- [ ] Create activity logging system
- [ ] Set up error handling and logging

### Phase 2: User Management
- [ ] Implement GET /api/admin/users (list)
- [ ] Implement GET /api/admin/users/{id} (details)
- [ ] Implement POST /api/admin/users (create)
- [ ] Implement PUT /api/admin/users/{id} (update)
- [ ] Implement DELETE /api/admin/users/{id} (delete)
- [ ] Implement POST /api/admin/users/{id}/reset-password
- [ ] Implement POST /api/admin/users/{id}/verify

### Phase 3: Credits Management
- [ ] Implement GET /api/admin/credits/transactions
- [ ] Implement POST /api/admin/credits/add
- [ ] Implement POST /api/admin/credits/deduct
- [ ] Implement GET /api/admin/credits/stats
- [ ] Add credit transaction validation
- [ ] Add user notifications for credit changes

### Phase 4: Styles Management
- [ ] Implement GET /api/admin/styles
- [ ] Implement GET /api/admin/styles/{id}
- [ ] Implement POST /api/admin/styles (create)
- [ ] Implement PUT /api/admin/styles/{id} (update)
- [ ] Implement DELETE /api/admin/styles/{id}
- [ ] Implement POST /api/admin/styles/{id}/toggle-trending
- [ ] Implement POST /api/admin/styles/{id}/duplicate
- [ ] Add image upload handling for previews

### Phase 5: Creations Management
- [ ] Implement GET /api/admin/creations
- [ ] Implement GET /api/admin/creations/{id}
- [ ] Implement PUT /api/admin/creations/{id}/feature
- [ ] Implement DELETE /api/admin/creations/{id}
- [ ] Implement GET /api/admin/creations/reported
- [ ] Implement POST /api/admin/creations/reports/{id}/resolve
- [ ] Add content moderation workflow

### Phase 6: Categories Management
- [ ] Implement GET /api/admin/categories
- [ ] Implement POST /api/admin/categories
- [ ] Implement PUT /api/admin/categories/{id}
- [ ] Implement DELETE /api/admin/categories/{id}
- [ ] Implement POST /api/admin/categories/{id}/reorder

### Phase 7: Analytics & Reporting
- [ ] Implement GET /api/admin/analytics/dashboard
- [ ] Implement GET /api/admin/analytics/users
- [ ] Implement GET /api/admin/analytics/creations
- [ ] Implement GET /api/admin/analytics/revenue
- [ ] Implement GET /api/admin/analytics/export
- [ ] Set up data aggregation jobs

### Phase 8: System Settings
- [ ] Implement GET /api/admin/settings
- [ ] Implement PUT /api/admin/settings/{key}
- [ ] Implement GET /api/admin/activity-logs
- [ ] Add setting validation
- [ ] Add real-time setting updates

### Phase 9: Testing & Documentation
- [ ] Write unit tests for all endpoints
- [ ] Write integration tests
- [ ] Load testing for analytics endpoints
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Create Postman collection

### Phase 10: Security & Optimization
- [ ] Rate limiting for admin endpoints
- [ ] IP whitelisting (optional)
- [ ] Audit log retention policy
- [ ] Database query optimization
- [ ] Caching for analytics
- [ ] Two-factor authentication for admins

---

## Technology Stack Recommendations

### Backend Framework
- **FastAPI** (Python) - High performance, async support
- **Express.js** (Node.js) - Alternative if team prefers JS
- **Django** (Python) - If need robust admin panel out-of-box

### Database
- **PostgreSQL 16** - Already in use
- **Redis** - For caching analytics, sessions

### File Storage
- **AWS S3** or **Cloudinary** - For style previews, category images

### Authentication
- **JWT** with refresh tokens
- **bcrypt** for password hashing
- **Role-based permissions**

### Additional Libraries
- **SQLAlchemy** / **Prisma** - ORM
- **Pydantic** / **Joi** - Validation
- **Pandas** - Data analytics
- **Celery** - Background jobs for heavy analytics

---

## Security Best Practices

1. **Authentication**
   - Use strong JWT secrets
   - Implement token rotation
   - Set appropriate expiry times (1 hour access, 7 days refresh)
   - Store refresh tokens in database for revocation

2. **Authorization**
   - Check permissions on EVERY endpoint
   - Use middleware for RBAC
   - Log all admin actions
   - Implement IP whitelisting for sensitive operations

3. **Input Validation**
   - Validate ALL user inputs
   - Sanitize before database queries
   - Use parameterized queries (prevent SQL injection)
   - Validate file uploads (type, size, content)

4. **Audit Logging**
   - Log every admin action
   - Include timestamp, admin ID, IP, action, resource
   - Store logs for minimum 1 year
   - Set up alerts for suspicious activity

5. **Rate Limiting**
   - Implement per-IP rate limits
   - Stricter limits for sensitive endpoints
   - Use Redis for distributed rate limiting

6. **Data Protection**
   - Encrypt sensitive data at rest
   - Use HTTPS for all API calls
   - Hash passwords with bcrypt (min 10 rounds)
   - Mask sensitive data in logs

---

## Sample Implementation Code

### Admin Middleware (FastAPI)

```python
from functools import wraps
from fastapi import HTTPException, Depends
from jose import JWTError, jwt

async def get_current_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id = payload.get("admin_id")
        role = payload.get("role")
        
        if not admin_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Check if admin is active
        admin = db.query(Admin).filter(Admin.id == admin_id, Admin.is_active == True).first()
        if not admin:
            raise HTTPException(status_code=403, detail="Admin account inactive")
        
        return admin
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_permission(permission: str):
    async def permission_checker(admin = Depends(get_current_admin)):
        if admin.role == "super_admin":
            return admin  # Super admin has all permissions
        
        if permission not in admin.permissions:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        return admin
    return permission_checker
```

### Usage in Route

```python
@router.post("/api/admin/credits/add")
async def add_credits(
    request: AddCreditsRequest,
    admin = Depends(require_permission("credits.add"))
):
    # Log admin action
    log_admin_activity(
        admin_id=admin.id,
        action="credits.added",
        resource_type="user",
        resource_id=request.user_id,
        details={
            "amount": request.amount,
            "reason": request.reason
        }
    )
    
    # Add credits logic...
    transaction = add_credits_to_user(
        user_id=request.user_id,
        amount=request.amount,
        description=f"Admin adjustment: {request.reason}"
    )
    
    return {
        "success": True,
        "data": transaction,
        "message": f"{request.amount} credits added successfully"
    }
```

### Activity Logger

```python
def log_admin_activity(
    admin_id: int,
    action: str,
    resource_type: str,
    resource_id: int = None,
    details: dict = None,
    ip_address: str = None,
    user_agent: str = None
):
    log = AdminActivityLog(
        admin_id=admin_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address or get_client_ip(),
        user_agent=user_agent or get_user_agent()
    )
    db.add(log)
    db.commit()
```

---

## Questions to Consider

Before implementation, clarify these points:

1. **Admin User Creation**: How will the first admin be created? Manual database insert?
2. **Permissions**: Should permissions be customizable per admin or fixed by role?
3. **Audit Retention**: How long should activity logs be kept?
4. **Notifications**: Should admins receive alerts for critical events?
5. **Bulk Operations**: Need endpoints for bulk user/style operations?
6. **Export Format**: Which export formats are needed (CSV, Excel, JSON)?
7. **Real-time Updates**: Should dashboard use websockets for live updates?
8. **Two-Factor Auth**: Required for admin login?

---

## Next Steps

1. **Review this specification** with your team
2. **Prioritize features** based on business needs
3. **Set up development environment** (database, API framework)
4. **Implement Phase 1** (core infrastructure)
5. **Test each phase** before moving to next
6. **Deploy to staging** for admin testing
7. **Collect feedback** and iterate

---

**This specification is ready to be given to any AI or development team for implementation. It includes all necessary details for database schema, API contracts, error handling, security, and best practices.**

For questions or clarifications, please refer to the main project documentation or contact the development team.
