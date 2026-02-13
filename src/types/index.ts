export interface User {
  id: number
  email: string
  name: string
  phone?: string
  credits: number
  is_verified: boolean
  is_active: boolean
  created_at: string
  last_login?: string
  avatar?: string
  referral_code: string
  total_creations: number
  total_likes_received: number
  total_likes_given: number
  battle_wins: number
  battle_losses: number
  net_credits: number
}

export interface Admin {
  id: number
  user_id: number
  email: string
  name: string
  avatar_url: string | null
  role: 'super_admin' | 'admin' | 'moderator'
  permissions: string[]
  created_at: string
  last_login: string | null
}

export interface Style {
  id: number
  name: string
  description: string
  category_id: number
  category_name: string
  prompt_template: string
  negative_prompt?: string
  credits_required: number
  is_active: boolean
  is_trending: boolean
  is_new: boolean
  display_order: number
  usage_count: number
  preview_image?: string
  tags: string[]
  created_at: string
}

export interface Creation {
  id: number
  user_id: number
  user_name: string
  user_email: string
  style_id: number
  style_name: string
  prompt: string
  image_url: string
  is_public: boolean
  is_featured: boolean
  likes_count: number
  views_count: number
  reports_count: number
  credits_spent: number
  processing_time: number
  created_at: string
}

export interface CreditTransaction {
  id: number
  user_id: number
  user_name: string
  user_email: string
  type: 'signup_bonus' | 'ad_watch' | 'purchase' | 'creation_cost' | 'referral_bonus' | 'battle_win' | 'admin_adjustment' | 'refund'
  amount: number
  description: string
  balance_before: number
  balance_after: number
  reference_id?: string
  created_at: string
}

export interface Category {
  id: number
  name: string
  slug: string
  description?: string
  display_order: number
  is_active: boolean
  styles_count: number
}

export interface Report {
  id: number
  reporter_id: number
  reporter_name: string
  reporter_email: string
  content_id: number
  content_type: 'creation'
  reason: string
  description?: string
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
  reviewed_at?: string
  reviewed_by?: number
}

export interface DashboardStats {
  users: {
    total: number
    new_today: number
    new_this_week: number
    active_last_30_days: number
    verified_ratio: number
  }
  credits: {
    total_in_system: number
    spent_today: number
    spent_this_week: number
    average_per_user: number
  }
  content: {
    total_creations: number
    public_creations: number
    private_creations: number
    featured_creations: number
    pending_reports: number
  }
  system: {
    api_response_time: number
    active_admin_sessions: number
    recent_errors: number
    uptime_percentage: number
  }
}

export interface PaginationMeta {
  page: number
  limit: number
  total: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

export interface ApiResponse<T> {
  success: boolean
  data: T
  error?: {
    code: string
    message: string
  }
}

export interface PaginatedResponse<T> {
  items: T[]
  pagination: PaginationMeta
}

export interface UserListResponse {
  users: User[]
  pagination: PaginationMeta
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  admin: Admin
  access_token: string
  token_type: string
  expires_in: number
}

export interface CreateUserRequest {
  email: string
  password: string
  name: string
  phone?: string
  credits?: number
  is_verified?: boolean
  is_active?: boolean
}

export interface AddCreditsRequest {
  user_id: number
  amount: number
  description: string
  reference_id?: string
  notify_user?: boolean
}