-- BL-DCMS bootstrap seed data.
--
-- Contains ONLY what a brand-new deployment needs to be usable on first boot:
--   1. Default system settings (generic operational defaults, not site-specific).
--   2. One bootstrap Administrator account, so a new shed can log in for the first time and
--      then create its own Sections, Equipment, Locomotives, Users, and Checksheet Templates
--      through the Dashboard UI (or via the seed scripts under Backend/scripts/ - see
--      Database/03_optional_checksheet_template_library.md).
--
-- No Sections, Equipment, Locomotives, Checksheet Templates, Checksheets, Activity Logs, OTP
-- Logs, Digital Signatures, or Notifications are included - this is deliberately a blank slate,
-- not a copy of any shed's production data.
--
-- Run this AFTER 01_schema.sql has been applied to a fresh database.

BEGIN;

INSERT INTO system_settings (key, category, value) VALUES
    ('company_name', 'General', 'YOUR_ORGANIZATION_NAME'),
    ('default_workflow', 'Workflow', 'DRAFT,SUBMITTED,UNDER_REVIEW,APPROVED'),
    ('allow_draft_edit', 'Workflow', 'true'),
    ('email_notifications', 'Notifications', 'false'),
    ('pdf_logo', 'PDF', ''),
    ('password_expiry_days', 'Security', '90'),
    ('session_timeout', 'Security', '30'),
    ('dsc.pkcs11_lib_path', 'Digital Signature', ''),
    ('dsc.pkcs11_token_label', 'Digital Signature', ''),
    ('dsc.pkcs11_cert_label', 'Digital Signature', ''),
    ('dsc.trusted_ca_bundle_path', 'Digital Signature', ''),
    ('dsc.enable_revocation_check', 'Digital Signature', 'false')
ON CONFLICT (key) DO NOTHING;

-- Bootstrap Administrator.
--   employee_id: ELSBL_ADMIN   (CHANGE_ME - pick your own login ID before going live)
--   password:    ChangeMe@123  (bcrypt hash below - see README.md "First Login")
--
-- This password is PUBLIC (it is printed in this file and in README.md) precisely so a brand
-- new deployment can log in at all. It grants full Administrator access. Change it immediately
-- after first login - Dashboard > Users > (this account) > Reset Password - before creating any
-- other user or entering any real data.
INSERT INTO users (employee_id, name, mobile, email, password_hash, role, is_active, section_id)
VALUES (
    'ELSBL_ADMIN',
    'System Administrator',
    '0000000000',
    NULL,
    '$2b$12$zf01USrcQNlW/WO5Qpkk6uDoyJyE1WCufzuyPmF4VuhF1t6tspn1a',
    'Admin',
    true,
    NULL
)
ON CONFLICT (employee_id) DO NOTHING;

COMMIT;
