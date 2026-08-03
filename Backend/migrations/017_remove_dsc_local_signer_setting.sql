-- Module 41.5: removes the orphaned local-signer setting left behind by the deprecated
-- IREPSSigner (DSC v1) implementation, now fully removed in favor of eMudhra emBridge. The code
-- that ever read this setting no longer exists, so the row - if any admin ever set one - is
-- inert. Does not touch dsc.trusted_ca_bundle_path or dsc.enable_revocation_check, which remain
-- in active use by the emBridge (v2) signing path.

DELETE FROM system_settings WHERE key = 'dsc.local_signer_base_url';
