-- Migration: create user_sessions table for server-managed session infrastructure
-- Do NOT execute automatically.

CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    jti VARCHAR(36) NOT NULL UNIQUE,
    refresh_token_hash VARCHAR(255),
    device_type VARCHAR(20) NOT NULL DEFAULT 'WEB',
    device_name VARCHAR(100),
    device_id VARCHAR(100),
    app_version VARCHAR(50),
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    revoked_reason VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS ix_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS ix_user_sessions_jti ON user_sessions(jti);
CREATE INDEX IF NOT EXISTS ix_user_sessions_device_id ON user_sessions(device_id);
CREATE INDEX IF NOT EXISTS ix_user_sessions_revoked ON user_sessions(revoked);
