-- Documentation of the notifications table SQLAlchemy already creates automatically via
-- Base.metadata.create_all() (app/database/database.py's initialize_db(), which only creates
-- tables that don't already exist). Provided for consistency with migrations 001-004; not required
-- to be run manually for this table to exist.

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'SYSTEM',
    checksheet_id INTEGER REFERENCES checksheet_header(id),
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_notifications_user_id ON notifications (user_id);
CREATE INDEX IF NOT EXISTS ix_notifications_id ON notifications (id);
