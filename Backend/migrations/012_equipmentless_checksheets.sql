-- Module 36: supports sections that have no equipment at all (M6-HR) - a checksheet template
-- with equipment_id NULL and section_id set already existed as a concept (Module 29.5's M35-Aux
-- "common page" prepended ahead of an equipment template), but checksheet_header.equipment_id was
-- always NOT NULL, so a checksheet could never actually be submitted against an equipment-less
-- template on its own. M6-HR templates set equipment_id NULL and stand alone (not prepended to
-- anything) - the existing composition logic in checksheet_template_service.get_template_detail
-- already returns an equipment-less template's own fields unmodified when fetched directly, so no
-- Template Engine change is needed there, only this column's NOT NULL constraint.
ALTER TABLE checksheet_header ALTER COLUMN equipment_id DROP NOT NULL;
