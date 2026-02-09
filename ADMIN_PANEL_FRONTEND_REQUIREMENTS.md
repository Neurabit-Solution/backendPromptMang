# MagicPic Admin Panel - Frontend Requirements

> **Complete guide for building the MagicPic Admin Panel frontend interface**  
> This document outlines all the components, features, and functionality needed for the admin panel.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication & Layout](#authentication--layout)
3. [Dashboard](#dashboard)
4. [User Management](#user-management)
5. [Credits Management](#credits-management)
6. [Styles Management](#styles-management)
7. [Creations Management](#creations-management)
8. [Categories Management](#categories-management)
9. [Content Moderation](#content-moderation)
10. [Analytics & Reports](#analytics--reports)
11. [System Settings](#system-settings)
12. [Admin Management](#admin-management)
13. [Technical Requirements](#technical-requirements)

---

## Overview

The MagicPic Admin Panel is a comprehensive web interface for managing the MagicPic platform. It provides tools for user management, content moderation, analytics, and system configuration.

### Key Features
- **Role-based access control** (Super Admin, Admin, Moderator)
- **Real-time data updates** and notifications
- **Responsive design** for desktop and tablet
- **Advanced filtering and search** capabilities
- **Bulk operations** for efficiency
- **Audit logging** for all admin actions
- **Data export** functionality

### User Roles & Permissions
- **Super Admin**: Full access to all features
- **Admin**: User management, styles, credits, analytics
- **Moderator**: Content moderation, user viewing only

---

## Authentication & Layout

### Login Page
**Route**: `/admin/login`

**Components Needed**:
- Login form with email/password fields
- "Remember me" checkbox
- Password visibility toggle
- Loading states and error handling
- Forgot password link (if applicable)

**Features**:
- Form validation with real-time feedback
- Secure token storage (localStorage/sessionStorage)
- Redirect to dashboard on successful login
- Error messages for invalid credentials, inactive accounts

### Main Layout
**Components Needed**:
- **Sidebar Navigation** with collapsible menu
- **Top Header** with user info, notifications, logout
- **Breadcrumb Navigation** for current page context
- **Main Content Area** with consistent padding/spacing

**Sidebar Menu Structure**:
```
📊 Dashboard
👥 Users
   ├── All Users
   ├── Create User
   └── User Reports
💰 Credits
   ├── Transactions
   ├── Add Credits
   └── Credit Stats
🎨 Styles
   ├── All Styles
   ├── Create Style
   └── Categories
🖼️ Creations
   ├── All Creations
   ├── Featured
   └── Reported Content
📊 Analytics
   ├── Overview
   ├── User Analytics
   └── Revenue Reports
⚙️ Settings
   ├── System Settings
   └── Admin Management
```

---

## Dashboard

**Route**: `/admin/dashboard`

### Key Metrics Cards
Display overview statistics in card format:

1. **Users Overview**
   - Total users count
   - New users today/this week
   - Active users (logged in last 30 days)
   - Verified vs unverified ratio

2. **Credits Overview**
   - Total credits in system
   - Credits spent today/this week
   - Average credits per user
   - Top credit earners

3. **Content Overview**
   - Total creations
   - Public vs private creations
   - Featured creations count
   - Reported content pending review

4. **System Health**
   - API response time
   - Active admin sessions
   - Recent errors/issues
   - System uptime

### Recent Activity Feed
- Recent user registrations
- Recent admin actions
- Recent content reports
- System alerts and notifications

### Quick Actions
- Create new user
- Add credits to user
- Feature a creation
- Review reported content

### Charts & Graphs
- User registration trend (last 30 days)
- Credits usage trend
- Content creation trend
- Revenue/engagement metrics

---

## User Management

### All Users Page
**Route**: `/admin/users`

**Components Needed**:
- **Advanced Search & Filters**:
  - Search by name, email, phone
  - Filter by verification status
  - Filter by active/inactive status
  - Filter by credit range
  - Filter by registration date range
  - Sort by various fields

- **Users Data Table**:
  - Pagination (50 users per page)
  - Sortable columns
  - Bulk selection checkboxes
  - Quick action buttons per row

**Table Columns**:
- Avatar thumbnail
- Name & Email
- Phone number
- Credits balance
- Verification status badge
- Active status badge
- Registration date
- Last login
- Actions (View, Edit, Delete)

**Bulk Actions**:
- Verify selected users
- Deactivate/activate selected users
- Export selected users to CSV
- Send bulk email notifications

### User Detail Page
**Route**: `/admin/users/{id}`

**Sections Needed**:

1. **User Profile Card**
   - Avatar, name, email, phone
   - Credits balance (with add/deduct buttons)
   - Verification and active status toggles
   - Registration date and last login
   - Referral code and referral stats

2. **User Statistics**
   - Total creations count
   - Public vs private creations
   - Total likes received/given
   - Battle wins/losses and win rate
   - Total credits earned/spent
   - Net credits (earned - spent)

3. **Recent Activity Timeline**
   - Recent creations with thumbnails
   - Recent credit transactions
   - Recent logins with IP addresses
   - Recent battles participated

4. **User Actions Panel**
   - Reset password button
   - Verify account button
   - Add/deduct credits
   - Send notification
   - View user's creations
   - Deactivate/delete account

### Create User Page
**Route**: `/admin/users/create`

**Form Fields**:
- Email (required, validated)
- Password (required, strength indicator)
- Full name (required)
- Phone number (optional, formatted)
- Initial credits (default: 2500)
- Verification status checkbox
- Active status checkbox
- Send welcome email checkbox

**Features**:
- Real-time form validation
- Password strength indicator
- Email availability check
- Auto-generate referral code
- Success/error notifications

---

## Credits Management

### Transactions Page
**Route**: `/admin/credits/transactions`

**Components Needed**:
- **Advanced Filters**:
  - Filter by user (searchable dropdown)
  - Filter by transaction type
  - Filter by date range
  - Filter by amount range
  - Sort by date, amount, user

- **Transactions Table**:
  - User info (name, email)
  - Transaction type badge
  - Amount (positive/negative styling)
  - Description
  - Balance before/after
  - Date and time
  - Reference ID (if applicable)

**Transaction Types**:
- Signup bonus
- Ad watch reward
- Purchase
- Creation cost
- Referral bonus
- Battle win
- Admin adjustment
- Refund

### Add Credits Page
**Route**: `/admin/credits/add`

**Form Components**:
- User search/select dropdown
- Amount input (positive only)
- Reason/description textarea
- Reference ID (optional)
- Notify user checkbox
- Preview of transaction before confirmation

### Credit Statistics Page
**Route**: `/admin/credits/stats`

**Sections Needed**:
1. **Overview Cards**
   - Total credits in system
   - Credits issued vs spent
   - Average balance per user
   - Users with zero balance

2. **Transaction Breakdown**
   - Pie chart by transaction type
   - Daily credits spent/earned trends
   - Top credit spenders/earners

3. **Credit Flow Analysis**
   - Credits added vs consumed over time
   - Seasonal trends
   - User behavior patterns

---

## Styles Management

### All Styles Page
**Route**: `/admin/styles`

**Components Needed**:
- **Style Grid/List View Toggle**
- **Filters & Search**:
  - Search by name
  - Filter by category
  - Filter by active status
  - Filter by trending status
  - Sort by usage, date, name

- **Style Cards/Rows**:
  - Preview image thumbnail
  - Style name and description
  - Category badge
  - Usage count
  - Credits required
  - Status badges (trending, new, active)
  - Quick actions (edit, duplicate, delete)

### Create/Edit Style Page
**Route**: `/admin/styles/create` or `/admin/styles/{id}/edit`

**Form Sections**:
1. **Basic Information**
   - Style name (required)
   - Description (required)
   - Category selection
   - Tags (searchable, multi-select)

2. **AI Configuration**
   - Prompt template (large textarea)
   - Negative prompt (optional)
   - Preview prompt generation

3. **Pricing & Visibility**
   - Credits required
   - Active status toggle
   - Trending status toggle
   - New style badge toggle
   - Display order

4. **Preview Image**
   - Image upload with preview
   - Drag & drop support
   - Image cropping/resizing tools

**Features**:
- Real-time prompt preview
- Style duplication option
- Save as draft functionality
- Preview generation test

### Style Detail Page
**Route**: `/admin/styles/{id}`

**Sections**:
1. **Style Overview**
   - Large preview image
   - Full prompt template
   - Usage statistics
   - Performance metrics

2. **Usage Analytics**
   - Usage trend chart
   - Top users of this style
   - Peak usage times
   - Geographic usage data

3. **Sample Creations**
   - Grid of top creations using this style
   - Most liked creations
   - Recent creations

---

## Creations Management

### All Creations Page
**Route**: `/admin/creations`

**Components Needed**:
- **View Options**: Grid view, List view, Detailed view
- **Advanced Filters**:
  - Filter by user
  - Filter by style
  - Filter by public/private status
  - Filter by featured status
  - Filter by date range
  - Filter by likes count range
  - Filter by reported status

- **Creation Grid/List**:
  - Thumbnail images
  - User info
  - Style used
  - Likes and views count
  - Public/private status
  - Featured status badge
  - Reports count (if any)
  - Quick actions

**Bulk Actions**:
- Feature/unfeature selected
- Make public/private
- Delete selected
- Export metadata

### Creation Detail Page
**Route**: `/admin/creations/{id}`

**Sections**:
1. **Creation Display**
   - Large image viewer
   - Original vs generated comparison
   - Full prompt used
   - Generation parameters

2. **Creation Info**
   - User details
   - Style used
   - Credits spent
   - Processing time
   - Creation date

3. **Engagement Metrics**
   - Total likes and views
   - Engagement rate
   - Share count
   - Comments (if applicable)

4. **Moderation Panel**
   - Feature/unfeature toggle
   - Public/private toggle
   - Delete creation button
   - View reports (if any)

---

## Categories Management

### Categories Page
**Route**: `/admin/categories`

**Components Needed**:
- **Categories List**:
  - Drag & drop reordering
  - Category name and slug
  - Styles count per category
  - Active status toggle
  - Edit/delete actions

- **Create/Edit Category Modal**:
  - Category name
  - URL slug (auto-generated)
  - Description
  - Display order
  - Active status

**Features**:
- Inline editing
- Bulk operations
- Category usage statistics

---

## Content Moderation

### Reported Content Page
**Route**: `/admin/moderation/reports`

**Components Needed**:
- **Reports Queue**:
  - Filter by report status
  - Filter by report reason
  - Sort by date, priority
  - Bulk actions

- **Report Cards**:
  - Reported content thumbnail
  - Reporter information
  - Report reason and description
  - Report date
  - Current status
  - Quick action buttons

### Report Detail Page
**Route**: `/admin/moderation/reports/{id}`

**Sections**:
1. **Report Information**
   - Reporter details
   - Report reason and description
   - Report date and status

2. **Reported Content**
   - Full content display
   - Content metadata
   - Creator information

3. **Moderation Actions**
   - Approve content (dismiss report)
   - Remove content
   - Warn user
   - Suspend user
   - Add to review notes

4. **Similar Reports**
   - Other reports on same content
   - Reports from same user
   - Pattern analysis

---

## Analytics & Reports

### Analytics Overview
**Route**: `/admin/analytics`

**Dashboard Sections**:
1. **User Analytics**
   - User growth trends
   - User engagement metrics
   - Geographic distribution
   - Device/platform usage

2. **Content Analytics**
   - Creation trends
   - Popular styles
   - Content engagement
   - Feature usage

3. **Revenue Analytics**
   - Credits purchased vs spent
   - Revenue trends
   - User lifetime value
   - Conversion rates

### Detailed Reports
**Routes**: Various analytics sub-pages

**Report Types**:
- User acquisition reports
- Content performance reports
- Revenue and monetization reports
- System performance reports
- Admin activity reports

**Features**:
- Date range selection
- Export to PDF/CSV
- Scheduled report generation
- Custom report builder

---

## System Settings

### Settings Page
**Route**: `/admin/settings`

**Settings Categories**:

1. **Credit Settings**
   - Signup bonus amount
   - Ad watch reward
   - Maximum ads per day
   - Referral bonus
   - Default creation cost

2. **Feature Toggles**
   - Battles feature enabled
   - Maintenance mode
   - New user registration
   - Public creation sharing

3. **Content Settings**
   - Maximum file upload size
   - Allowed image formats
   - Content moderation rules
   - Auto-moderation thresholds

4. **Notification Settings**
   - Email notification templates
   - Push notification settings
   - Admin alert thresholds

**Features**:
- Real-time setting updates
- Setting validation
- Change history tracking
- Rollback functionality

---

## Admin Management

### Admin Users Page
**Route**: `/admin/admins`

**Components Needed**:
- **Admin List Table**:
  - Admin name and email
  - Role badge
  - Permissions summary
  - Last login
  - Active status
  - Actions

- **Create Admin Modal**:
  - Select existing user
  - Assign role
  - Set custom permissions
  - Activation status

### Admin Activity Logs
**Route**: `/admin/activity-logs`

**Components**:
- **Activity Timeline**:
  - Admin name and action
  - Resource affected
  - Action details
  - IP address and timestamp
  - Filter by admin, action type, date

**Log Types**:
- User management actions
- Content moderation actions
- System setting changes
- Credit transactions
- Style management actions

---

## Technical Requirements

### Frontend Technology Stack
- **Framework**: React 18+ with TypeScript
- **Styling**: Tailwind CSS or Material-UI
- **State Management**: Redux Toolkit or Zustand
- **Routing**: React Router v6
- **HTTP Client**: Axios with interceptors
- **Charts**: Chart.js or Recharts
- **Tables**: TanStack Table (React Table v8)
- **Forms**: React Hook Form with Zod validation
- **Date Handling**: date-fns or dayjs
- **File Upload**: React Dropzone

### Key Features to Implement

1. **Authentication & Security**
   - JWT token management with refresh
   - Role-based route protection
   - Session timeout handling
   - CSRF protection

2. **Data Management**
   - Optimistic updates
   - Caching with React Query
   - Real-time updates (WebSocket/SSE)
   - Offline support (basic)

3. **User Experience**
   - Loading states and skeletons
   - Error boundaries
   - Toast notifications
   - Confirmation dialogs
   - Keyboard shortcuts
   - Responsive design

4. **Performance**
   - Code splitting by routes
   - Image lazy loading
   - Virtual scrolling for large lists
   - Debounced search inputs
   - Memoized components

5. **Accessibility**
   - ARIA labels and roles
   - Keyboard navigation
   - Screen reader support
   - High contrast mode
   - Focus management

### API Integration
- **Base URL**: `http://localhost:8000/api/admin`
- **Authentication**: Bearer token in headers
- **Error Handling**: Consistent error response format
- **Pagination**: Cursor or offset-based pagination
- **File Uploads**: Multipart form data support

### Development Guidelines
- **Component Structure**: Atomic design principles
- **Code Organization**: Feature-based folder structure
- **Testing**: Unit tests with Jest/RTL, E2E with Playwright
- **Documentation**: Storybook for component documentation
- **Code Quality**: ESLint, Prettier, Husky pre-commit hooks

---

## Implementation Priority

### Phase 1 (MVP)
1. Authentication and basic layout
2. Dashboard with key metrics
3. User management (list, view, create)
4. Basic credits management
5. Styles management (list, view)

### Phase 2 (Core Features)
1. Advanced user management features
2. Complete credits management
3. Creations management
4. Content moderation basics
5. Basic analytics

### Phase 3 (Advanced Features)
1. Advanced analytics and reporting
2. System settings management
3. Admin management
4. Advanced moderation tools
5. Real-time features

### Phase 4 (Enhancements)
1. Advanced search and filtering
2. Bulk operations
3. Export functionality
4. Mobile responsiveness
5. Performance optimizations

---

This document provides a comprehensive overview of all the components, features, and functionality needed for the MagicPic Admin Panel frontend. Each section can be developed incrementally, starting with the MVP features and gradually adding more advanced capabilities.