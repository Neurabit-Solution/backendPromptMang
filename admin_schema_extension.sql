-- ============================================================
-- ADMIN TABLES EXTENSION
-- ============================================================

-- 1. Admins Table
CREATE TABLE IF NOT EXISTS admins (
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

CREATE INDEX IF NOT EXISTS idx_admins_user_id ON admins(user_id);
CREATE INDEX IF NOT EXISTS idx_admins_role ON admins(role);

-- 2. Admin Activity Logs
CREATE TABLE IF NOT EXISTS admin_activity_logs (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER NOT NULL REFERENCES admins(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,  -- 'user.created', 'credits.added', etc.
    resource_type VARCHAR(50) NOT NULL,
    resource_id INTEGER,
    details JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_admin_logs_admin_id ON admin_activity_logs(admin_id);

-- 3. System Settings
CREATE TABLE IF NOT EXISTS system_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSON NOT NULL,
    description VARCHAR(500),
    updated_by INTEGER REFERENCES admins(id) ON DELETE SET NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Content Reports
CREATE TABLE IF NOT EXISTS content_reports (
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

-- Sample settings
INSERT INTO system_settings (key, value, description) VALUES
('credits.signup_bonus', '2500', 'Initial credits given on signup'),
('credits.ad_watch_reward', '50', 'Credits earned per ad watch')
ON CONFLICT (key) DO NOTHING;
