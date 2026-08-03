-- Module 32: supports multiple checksheet templates for the same equipment+technology,
-- differentiated by Maintenance Type (e.g. Traction Motor's GC vs Overhaul templates) - a
-- dimension distinct from Work Type (IOH/TOH), which continues to exist unchanged and is not
-- used for template selection.
--
-- checksheet_templates.maintenance_type stays NULL for every existing template (single template
-- per equipment+technology, resolved exactly as before); it is only set on templates that need
-- disambiguating beyond equipment+technology.
--
-- checksheet_header gains two new metadata columns, stored the same way work_type already is:
-- traction_motor_number (which of the locomotive's 6 physical traction motors this checksheet is
-- for) and maintenance_type (which template variant was used to fill it in).
ALTER TABLE checksheet_templates ADD COLUMN IF NOT EXISTS maintenance_type VARCHAR(20);

ALTER TABLE checksheet_header ADD COLUMN IF NOT EXISTS traction_motor_number VARCHAR(20);
ALTER TABLE checksheet_header ADD COLUMN IF NOT EXISTS maintenance_type VARCHAR(20);
