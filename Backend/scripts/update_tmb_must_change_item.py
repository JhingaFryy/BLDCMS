"""
TMB's "Must Change Item" no longer lists Impeller Flakt/Arco as separate line items - it now
keeps Bearing (unchanged) and a single "Impeller" line with a free-text box for its make.

Real checksheet data (checksheet ids 4 and 8) already references the old "Impeller Flakt" group
(and its 3 children) and the "Arco" field, so a hard DELETE would raise a ForeignKeyViolation on
checksheet_value.field_id. Those fields are archived instead (is_active=False, is_deleted=True,
deleted_at=now) - the same pattern template_field_service.delete_field already uses for a field
blocked by real historical data. Archived fields are excluded from new checksheets
(checksheet_template_service._compose_fields filters on is_active) but the two historical
submissions keep reading them fine (checksheet_service._serialize_detail and pdf_service both
build their field list from header.values directly, unfiltered by is_active).

A new "Impeller (Make)" text field is added in their place for every checksheet filled from now on.

Run once: `venv/bin/python scripts/update_tmb_must_change_item.py`. Idempotent - safe to re-run.
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.database import SessionLocal
from app.models.template_field import TemplateField

TMB_TEMPLATE_ID = 5
ARCHIVE_KEYS = [
    "must_change_impeller_flakt",
    "impeller_flakt_imp_no",
    "impeller_flakt_mfd_date",
    "impeller_flakt_make",
    "must_change_arco",
]
NEW_FIELD_KEY = "must_change_impeller_make"
# Same display_order slot the old "Impeller Flakt" group occupied - between Bearing 6313's
# children (54-57) and Transparent Sleeve (63).
NEW_FIELD_DISPLAY_ORDER = 58


def main():
    db = SessionLocal()
    try:
        must_change = db.query(TemplateField).filter(
            TemplateField.template_id == TMB_TEMPLATE_ID,
            TemplateField.field_key == "must_change_item",
        ).first()
        if must_change is None:
            raise SystemExit("TMB template's Must Change Item group not found - aborting.")

        archived = 0
        for key in ARCHIVE_KEYS:
            field = db.query(TemplateField).filter(
                TemplateField.template_id == TMB_TEMPLATE_ID,
                TemplateField.field_key == key,
            ).first()
            if field is None or field.is_deleted:
                continue
            field.is_active = False
            field.is_deleted = True
            field.deleted_at = datetime.now(timezone.utc)
            archived += 1

        existing_new_field = db.query(TemplateField).filter(
            TemplateField.template_id == TMB_TEMPLATE_ID,
            TemplateField.field_key == NEW_FIELD_KEY,
        ).first()
        if existing_new_field is None:
            db.add(TemplateField(
                template_id=TMB_TEMPLATE_ID,
                field_key=NEW_FIELD_KEY,
                field_label="Impeller (Make)",
                field_type="text",
                display_order=NEW_FIELD_DISPLAY_ORDER,
                required=False,
                page_number=1,
                parent_field_id=must_change.id,
            ))
            print("Added new 'Impeller (Make)' field.")
        else:
            print("'Impeller (Make)' field already exists - skipping.")

        db.commit()
        print(f"Archived {archived} field(s) (Impeller Flakt group + Arco).")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
