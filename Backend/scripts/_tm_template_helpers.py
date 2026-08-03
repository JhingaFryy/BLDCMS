"""
Module 32: shared helpers for seeding the M35-TM Traction Motor templates (GC and Overhaul).

Deliberately a SEPARATE module from scripts/_aux_template_helpers.py (the M35-Aux blower/motor
helper library) rather than an extension of it - M35-TM's checking points share no structural
overlap with M35-Aux's (no "Pre Testing"/"Winding Resistance"/"Must Change Item" pattern reuse is
possible here), and this keeps the M35-Aux seed scripts completely untouched.

The only genuine extension over _aux_template_helpers.py's pattern is `maintenance_type`
(Module 32): Traction Motor is the first equipment with more than one active template for the
same equipment_id+technology (GC vs Overhaul), so `get_or_create_template`/`run_seed` accept it as
an explicit parameter. Every other piece of infrastructure here (clear_existing_fields, make_add,
the leaf-first deletion loop) is identical in behavior to the M35-Aux version.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.database import SessionLocal  # noqa: E402
from app.models.checksheet_template import ChecksheetTemplate  # noqa: E402
from app.models.template_field import TemplateField  # noqa: E402


def get_or_create_template(db, template_code, equipment_id, technology, maintenance_type, template_name, description):
    existing = db.query(ChecksheetTemplate).filter(ChecksheetTemplate.template_code == template_code).first()
    if existing:
        print(f"Template code '{template_code}' already exists (id={existing.id}), reusing it.")
        return existing

    template = ChecksheetTemplate(
        template_code=template_code,
        version=1,
        equipment_id=equipment_id,
        section_id=None,
        technology=technology,
        maintenance_type=maintenance_type,
        template_name=template_name,
        description=description,
        is_active=True,
    )
    db.add(template)
    db.flush()
    print(f"Created template id={template.id} for equipment_id={equipment_id}, maintenance_type={maintenance_type} ({template_name}).")
    return template


def clear_existing_fields(db, template_id):
    """Deletes every field on the template, leaf-first (a field referenced by another field's
    parent_field_id can't be deleted before its children, or Postgres raises a FK violation).
    Each pass must be flushed before the next query, or the query keeps re-reading the same
    not-yet-deleted rows and the loop never terminates."""
    removed = 0
    while True:
        fields = db.query(TemplateField).filter(TemplateField.template_id == template_id).all()
        if not fields:
            break
        parent_ids_in_use = {f.parent_field_id for f in fields if f.parent_field_id is not None}
        leaves = [f for f in fields if f.id not in parent_ids_in_use]
        for f in leaves:
            db.delete(f)
        db.flush()
        removed += len(leaves)
    print(f"Removed {removed} pre-existing field(s) for template {template_id}.")


def make_add(db, template_id, order_state):
    def add(field_key, parent=None, **kwargs):
        order_state[0] += 1
        f = TemplateField(
            template_id=template_id,
            field_key=field_key,
            display_order=order_state[0],
            page_number=kwargs.pop("page_number", 1),
            parent_field_id=parent.id if parent is not None else None,
            **kwargs,
        )
        db.add(f)
        db.flush()
        return f
    return add


def run_seed(equipment_code, template_code, technology, maintenance_type, template_name, description, build_fn):
    """Common entry point both TM seed scripts call: looks up the equipment, creates/reuses its
    template (keyed by template_code, disambiguated by maintenance_type), clears old fields, and
    runs build_fn(add) to populate new ones."""
    db = SessionLocal()
    try:
        from app.models.equipment import Equipment
        equipment = db.query(Equipment).filter(Equipment.equipment_code == equipment_code).first()
        if equipment is None:
            raise SystemExit(f"Equipment '{equipment_code}' not found - aborting.")

        template = get_or_create_template(
            db, template_code, equipment.id, technology, maintenance_type, template_name, description
        )
        clear_existing_fields(db, template.id)

        order_state = [0]
        add = make_add(db, template.id, order_state)
        build_fn(add)

        db.commit()
        print(f"{template_name} template (id={template.id}) synchronized with reference checksheet. "
              f"{order_state[0]} field(s) inserted.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
