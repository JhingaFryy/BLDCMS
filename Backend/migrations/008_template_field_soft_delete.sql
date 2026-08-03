-- Adds soft-delete/archival support to template_fields, so a field that is referenced by
-- historical checksheet_value rows (FK: checksheet_value.field_id -> template_fields.id) can be
-- archived instead of hard-deleted, avoiding a ForeignKeyViolation on DELETE.
--
-- is_active already exists (Module 29.5) and is reused as the "hidden from new checksheets/editing"
-- flag; is_deleted/deleted_at are new and specifically mark "this field was deleted via the API but
-- had to be archived instead of removed" (distinct from an admin manually toggling is_active off).
--
-- Apply once against the live database: `venv/bin/python scripts/apply_migration_008.py`
ALTER TABLE template_fields ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE template_fields ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL;

CREATE INDEX IF NOT EXISTS ix_template_fields_is_deleted ON template_fields (is_deleted);
