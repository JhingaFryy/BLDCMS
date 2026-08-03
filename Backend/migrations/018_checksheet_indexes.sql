-- Module 43: Production Validation - checksheet_header and checksheet_value had no indexes
-- beyond their primary key, despite being the two most heavily filtered/joined tables in the
-- app (supervisor pending/approved/rejected lists filter by section_id+status, technicians are
-- scoped by technician_mobile, daily-count queries range-filter by submitted_at, and every
-- checksheet detail view loads all checksheet_value rows for a given checksheet_id). Masked in
-- testing by low data volume; would degrade badly at real production scale. Purely additive -
-- no query logic changes, no behavior change, only faster lookups.

CREATE INDEX IF NOT EXISTS ix_checksheet_header_section_id ON checksheet_header (section_id);
CREATE INDEX IF NOT EXISTS ix_checksheet_header_status ON checksheet_header (status);
CREATE INDEX IF NOT EXISTS ix_checksheet_header_technician_mobile ON checksheet_header (technician_mobile);
CREATE INDEX IF NOT EXISTS ix_checksheet_header_submitted_at ON checksheet_header (submitted_at);
CREATE INDEX IF NOT EXISTS ix_checksheet_header_equipment_id ON checksheet_header (equipment_id);
CREATE INDEX IF NOT EXISTS ix_checksheet_header_locomotive_id ON checksheet_header (locomotive_id);

CREATE INDEX IF NOT EXISTS ix_checksheet_value_checksheet_id ON checksheet_value (checksheet_id);
CREATE INDEX IF NOT EXISTS ix_checksheet_value_field_id ON checksheet_value (field_id);

CREATE INDEX IF NOT EXISTS ix_digital_signatures_signing_timestamp ON digital_signatures (signing_timestamp);
