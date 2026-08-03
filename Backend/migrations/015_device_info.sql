-- Module 44: System Administration CLI - a device registry for the CLI's "devices" commands to
-- read. Populated by upserting on every successful Android login/OTP-verify (see
-- app/services/device_info_service.py); never written to or read by any authentication/
-- authorization code path. All device attribute columns are nullable - a device row can exist
-- with only device_id known if the app hasn't been updated to report the richer fields yet.

CREATE TABLE IF NOT EXISTS device_info (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(100) NOT NULL UNIQUE,
    user_id INTEGER REFERENCES users(id),
    manufacturer VARCHAR(100),
    device_model VARCHAR(100),
    os_version VARCHAR(50),
    app_version VARCHAR(50),
    battery_level INTEGER,
    network_type VARCHAR(20),
    storage_free_mb INTEGER,
    storage_total_mb INTEGER,
    disclosure_acknowledged_at TIMESTAMP,
    pending_command VARCHAR(50),
    pending_command_issued_at TIMESTAMP,
    last_seen_at TIMESTAMP NOT NULL DEFAULT now(),
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_device_info_device_id ON device_info (device_id);
CREATE INDEX IF NOT EXISTS ix_device_info_user_id ON device_info (user_id);
