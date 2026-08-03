"""
Module 32.2: removes 5 header/signature TemplateField rows from the TM GC and Overhaul templates
that duplicate information the application already captures elsewhere before/after the checksheet
is filled - Loco Number, Homing Shed, Railway, Date, and Technician.

Unlike Module 32.1's Point 11/17 (which were kept as inactive future-implementation
placeholders), this is a genuine, permanent removal: none of these 5 fields are ever going to
become meaningful template entries again, since the data they'd capture is already stored as
first-class ChecksheetHeader/User metadata:
- Loco Number/Type: already known the moment the Technician selects the Locomotive, and stored on
  ChecksheetHeader via locomotive_id.
- Homing Shed/Railway: not stored anywhere at all today (no locomotive-master-data column for
  either) - deliberately left unimplemented rather than duplicated ad hoc inside a checksheet
  template, so a future locomotive-master-data module can add them once, not per-template.
- Date: the submission timestamp already exists on ChecksheetHeader.submitted_at and is already
  shown in the PDF.
- Technician: ChecksheetHeader.technician_mobile already resolves to the technician's name/
  employee ID via the existing User relationship, already shown in the PDF.

A hard DELETE (not a soft is_active=False archive) is safe and used here because zero
checksheet_value rows reference any of them (verified before running) - this is exactly the
"never used in a submitted checksheet" condition template_field_service.delete_field() already
hard-deletes for, applied the same way. None of the 5 fields are a parent of any other field
(simple top-level text/date leaves), so there is no orphaning risk either.

Only 4 of these 5 exist on the Overhaul template - it has no standalone "Date" field (its own
"D.O.C of TM" field is a different, TM-specific date and is NOT touched), and its technician-typed
field is "Staff" (overhaul_staff_name), not literally "Technician". "Supervisor"
(overhaul_supervisor_name) is intentionally left alone - the module's field list names only
Loco Number/Homing Shed/Railway/Date/Technician, not Supervisor.

Run once: `venv/bin/python scripts/remove_tm_header_redundant_fields.py`. Idempotent - safe to
re-run (skips any field_key already gone).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.database import SessionLocal
from app.models.template_field import TemplateField
from app.models.checksheet_value import ChecksheetValue

GC_TEMPLATE_ID = 25
OVERHAUL_TEMPLATE_ID = 26

GC_KEYS_TO_REMOVE = ["loco_no_type", "homing_shed", "railways", "gc_date", "technician_name"]
OVERHAUL_KEYS_TO_REMOVE = ["loco_no_type", "homing_shed", "railways", "overhaul_staff_name"]


def remove_fields(db, template_id, field_keys):
    removed = 0
    for key in field_keys:
        field = db.query(TemplateField).filter(
            TemplateField.template_id == template_id,
            TemplateField.field_key == key,
        ).first()
        if field is None:
            print(f"template {template_id}: '{key}' already absent - skipping.")
            continue

        in_use = db.query(ChecksheetValue).filter(ChecksheetValue.field_id == field.id).first() is not None
        if in_use:
            raise SystemExit(
                f"Refusing to delete template {template_id} field '{key}' (id={field.id}) - "
                "it is referenced by real checksheet_value data."
            )

        has_children = db.query(TemplateField).filter(TemplateField.parent_field_id == field.id).first() is not None
        if has_children:
            raise SystemExit(
                f"Refusing to delete template {template_id} field '{key}' (id={field.id}) - "
                "it has child fields."
            )

        print(f"Deleting template {template_id} field id={field.id} field_key={key} ({field.field_label!r})")
        db.delete(field)
        removed += 1
    return removed


def main():
    db = SessionLocal()
    try:
        gc_removed = remove_fields(db, GC_TEMPLATE_ID, GC_KEYS_TO_REMOVE)
        overhaul_removed = remove_fields(db, OVERHAUL_TEMPLATE_ID, OVERHAUL_KEYS_TO_REMOVE)
        db.commit()
        print(f"Done. GC: {gc_removed} field(s) removed. Overhaul: {overhaul_removed} field(s) removed.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
