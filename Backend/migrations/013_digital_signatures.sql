-- Module 39: Digital Signature Integration (DSC) for Supervisor Approval.
-- One row per digitally-signed checksheet. Never stores a PIN, private key, or token secret -
-- only certificate metadata and verification results, per Module 39's explicit security
-- requirement. checksheet_id is UNIQUE: a checksheet can only ever be signed once (it becomes
-- immutable immediately after), so there is exactly 0 or 1 signature row per checksheet.

CREATE TABLE IF NOT EXISTS digital_signatures (
    id SERIAL PRIMARY KEY,
    checksheet_id INTEGER NOT NULL UNIQUE REFERENCES checksheet_header(id) ON DELETE CASCADE,

    supervisor_id INTEGER REFERENCES users(id),
    supervisor_name VARCHAR(100) NOT NULL,
    supervisor_employee_id VARCHAR(20) NOT NULL,

    certificate_subject VARCHAR(255) NOT NULL,
    certificate_issuer VARCHAR(255) NOT NULL,
    certificate_serial_number VARCHAR(100) NOT NULL,
    certificate_thumbprint VARCHAR(128) NOT NULL,
    certificate_valid_from TIMESTAMP NOT NULL,
    certificate_valid_to TIMESTAMP NOT NULL,

    signing_timestamp TIMESTAMP NOT NULL,
    signature_hash VARCHAR(128) NOT NULL,
    verification_status VARCHAR(30) NOT NULL,

    provider VARCHAR(30) NOT NULL,
    is_development_signature BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_digital_signatures_checksheet_id ON digital_signatures(checksheet_id);
