-- Documentation of the activity_logs table SQLAlchemy already creates automatically via
-- Base.metadata.create_all() (app/database/database.py's initialize_db(), which only creates
-- tables that don't already exist). Provided for consistency with migrations 001-005; not
-- required to be run manually for this table to exist.

CREATE TABLE IF NOT EXISTS activity_logs (
    id SERIAL PRIMARY KEY,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INTEGER,
    user_id INTEGER REFERENCES users(id),
    section_id INTEGER REFERENCES sections(id),
    description TEXT,
    old_value JSON,
    new_value JSON,
    activity_metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_activity_logs_action ON activity_logs (action);
CREATE INDEX IF NOT EXISTS ix_activity_logs_entity_type ON activity_logs (entity_type);
CREATE INDEX IF NOT EXISTS ix_activity_logs_entity_id ON activity_logs (entity_id);
CREATE INDEX IF NOT EXISTS ix_activity_logs_user_id ON activity_logs (user_id);
CREATE INDEX IF NOT EXISTS ix_activity_logs_section_id ON activity_logs (section_id);
CREATE INDEX IF NOT EXISTS ix_activity_logs_created_at ON activity_logs (created_at);
