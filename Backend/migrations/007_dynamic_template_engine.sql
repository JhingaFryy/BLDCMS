-- Module 29.5: Dynamic Checksheet Template Engine.
-- Unlike migrations 001/005/006 (new tables, applied automatically by create_all()), this
-- migration ALTERs two existing tables, which create_all() never does - it must be applied
-- explicitly (see scripts/apply_migration_007.py, run once against the live database).

-- template_fields: new columns are all generic/reusable, never named after a specific equipment.
ALTER TABLE template_fields ADD COLUMN IF NOT EXISTS min_value DOUBLE PRECISION;
ALTER TABLE template_fields ADD COLUMN IF NOT EXISTS max_value DOUBLE PRECISION;
ALTER TABLE template_fields ADD COLUMN IF NOT EXISTS decimal_precision INTEGER;
ALTER TABLE template_fields ADD COLUMN IF NOT EXISTS standard_value TEXT;
ALTER TABLE template_fields ADD COLUMN IF NOT EXISTS authority_reference VARCHAR(255);
ALTER TABLE template_fields ADD COLUMN IF NOT EXISTS parent_field_id INTEGER REFERENCES template_fields(id);
ALTER TABLE template_fields ADD COLUMN IF NOT EXISTS page_number INTEGER NOT NULL DEFAULT 1;

CREATE INDEX IF NOT EXISTS ix_template_fields_parent_field_id ON template_fields (parent_field_id);
CREATE INDEX IF NOT EXISTS ix_template_fields_page_number ON template_fields (page_number);

-- checksheet_templates: equipment_id becomes optional so a template can instead be a section-wide
-- "common page" template (equipment_id NULL, section_id set) - see
-- checksheet_template_service.get_template_detail's compose logic.
ALTER TABLE checksheet_templates ADD COLUMN IF NOT EXISTS section_id INTEGER REFERENCES sections(id);
ALTER TABLE checksheet_templates ALTER COLUMN equipment_id DROP NOT NULL;

CREATE INDEX IF NOT EXISTS ix_checksheet_templates_section_id ON checksheet_templates (section_id);
