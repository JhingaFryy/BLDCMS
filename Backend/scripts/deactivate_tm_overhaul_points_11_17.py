"""
Module 32.1: marks Point 11 ("OD of Inner Racer (DE) Before/After Provision on Shaft" - BOD/AOD/
Swell) and Point 17 ("OD of Inner Racer (NDE) Before/After Provision on Shaft" - BOD/AOD/Swell) of
the TM Overhaul template inactive, per the module's explicit instruction: these two checking
points have no clearly defined pass/fail standard in the source document (only a formula,
Swell = interference x Diameter / Height, with no stated acceptable range) and are deferred as
future-implementation placeholders rather than fully specified now.

This is a surgical UPDATE (is_active=False on the group + its 3 children, for both points) - NOT
a delete-and-rebuild via scripts/_tm_template_helpers.py's run_seed(), which would needlessly
recreate every field's primary key. Points stay in the template with their exact original
field_key/display_order/parent_field_id, satisfying "do not renumber, do not remove" - they are
simply excluded from _compose_fields() (Android/Dashboard form composition),
_validate_required_values_for_template() (submission requirements), and the checking-point rows
pdf_service builds from header.values - all three already filter/derive from is_active or from
header.values (which will now never contain a row for these fields), with zero Template
Engine/Validation Engine/PDF Engine code changes.

Run once: `venv/bin/python scripts/deactivate_tm_overhaul_points_11_17.py`. Idempotent - safe to
re-run (skips fields already inactive).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.database import SessionLocal
from app.models.template_field import TemplateField

OVERHAUL_TEMPLATE_ID = 26

POINT_11_KEYS = ["inner_racer_de_bod_aod", "inner_racer_de_bod", "inner_racer_de_aod", "inner_racer_de_swell"]
POINT_17_KEYS = ["inner_racer_nde_bod_aod", "inner_racer_nde_bod", "inner_racer_nde_aod", "inner_racer_nde_swell"]


def main():
    db = SessionLocal()
    try:
        target_keys = POINT_11_KEYS + POINT_17_KEYS
        fields = db.query(TemplateField).filter(
            TemplateField.template_id == OVERHAUL_TEMPLATE_ID,
            TemplateField.field_key.in_(target_keys),
        ).all()

        found_keys = {f.field_key for f in fields}
        missing = set(target_keys) - found_keys
        if missing:
            raise SystemExit(f"Expected fields not found - aborting without changing anything: {sorted(missing)}")

        changed = 0
        for f in fields:
            if f.is_active:
                f.is_active = False
                changed += 1
                print(f"Deactivated id={f.id} field_key={f.field_key} display_order={f.display_order}")
            else:
                print(f"Already inactive: id={f.id} field_key={f.field_key}")

        db.commit()
        print(f"Done. {changed} field(s) newly deactivated, {len(fields)} total matched.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
