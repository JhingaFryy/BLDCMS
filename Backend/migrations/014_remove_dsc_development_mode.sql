-- Removes the Digital Signature Development/Test Mode entirely - the app now signs exclusively
-- with the supervisor's real Class-III DSC on a PKCS#11 USB crypto token. No production
-- checksheet was ever signed with a development signature (is_development_signature was only
-- ever TRUE for test data), so dropping the column is safe.

ALTER TABLE digital_signatures DROP COLUMN IF EXISTS is_development_signature;

DELETE FROM system_settings WHERE key = 'dsc.development_mode';
