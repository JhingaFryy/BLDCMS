-- Module 29.9: Automatic Checksheet Validation Engine.
-- Adds generic, reusable metadata columns to template_fields so the validation engine
-- (app/services/validation_service.py) can be driven entirely by template data - no rule is ever
-- hardcoded to a specific equipment or field.
--
-- validation_rule: explicit opt-in identifier for a cross-field rule that can't be inferred from
-- a single field's own metadata (currently only 'percentage_difference' - Rules 3/4). Rules 1/2
-- (minimum/range) need no new column at all - they are already fully expressed by the existing
-- min_value/max_value columns on any field that has them set.
--
-- validation_threshold: generic percentage parameter for validation_rule='percentage_difference'
-- (10% for winding resistance/inductance comparison, 5% for phase/lug temperature imbalance) -
-- reusable for any future percentage-based rule too, not specific to this one.
--
-- negative_values: comma-separated list of this field's own option/boolean values that constitute
-- a FAIL (Rules 5/6) - e.g. "Not in Green Zone", "Crack Found", "Abnormal", "false". Read from
-- template metadata, never hardcoded in the validation engine or the PDF generator.
ALTER TABLE template_fields ADD COLUMN IF NOT EXISTS validation_rule VARCHAR(50);
ALTER TABLE template_fields ADD COLUMN IF NOT EXISTS validation_threshold DOUBLE PRECISION;
ALTER TABLE template_fields ADD COLUMN IF NOT EXISTS negative_values TEXT;
