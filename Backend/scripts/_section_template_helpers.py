"""
Module 36: shared helpers for seeding equipment-less, section-wide checksheet templates (M6-HR -
"No Equipment records are required. No Equipment Mapping is required."). Deliberately a separate
module from `_aux_template_helpers.py` rather than an extension of it, because `run_seed` there
looks the template's owner up by `equipment_code` (`Equipment.equipment_code == equipment_code`),
which has no meaning here - a M6-HR template's identity is `section_id + technology` only,
equipment_id is always NULL.

`clear_existing_fields`/`make_add` are identical in behavior to `_aux_template_helpers.py`'s
versions (copied rather than imported, to keep the two seed-helper modules independent, matching
the existing precedent of `_tm_template_helpers.py` being its own copy rather than importing from
`_aux_template_helpers.py`).
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.database import SessionLocal  # noqa: E402
from app.models.checksheet_template import ChecksheetTemplate  # noqa: E402
from app.models.template_field import TemplateField  # noqa: E402
from app.models.section import Section  # noqa: E402


def get_or_create_template(db, template_code, section_id, technology, template_name, description):
    existing = db.query(ChecksheetTemplate).filter(ChecksheetTemplate.template_code == template_code).first()
    if existing:
        print(f"Template code '{template_code}' already exists (id={existing.id}), reusing it.")
        return existing

    template = ChecksheetTemplate(
        template_code=template_code,
        version=1,
        equipment_id=None,
        section_id=section_id,
        technology=technology,
        template_name=template_name,
        description=description,
        is_active=True,
    )
    db.add(template)
    db.flush()
    print(f"Created template id={template.id} for section_id={section_id}, technology={technology} ({template_name}).")
    return template


def clear_existing_fields(db, template_id):
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


def run_seed(section_name, template_code, technology, template_name, description, build_fn):
    """Looks up the section (never created here - "No Equipment records are required" extends to
    never creating/touching Section rows either; M6-HR must already exist), creates/reuses its
    equipment-less template, clears old fields, and runs build_fn(add) to populate new ones."""
    db = SessionLocal()
    try:
        section = db.query(Section).filter(Section.name == section_name).first()
        if section is None:
            raise SystemExit(f"Section '{section_name}' not found - aborting.")

        template = get_or_create_template(db, template_code, section.id, technology, template_name, description)
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


def add_final_remarks(add, label="Remarks / Any Other Observation"):
    return add("final_remarks", field_label=label, field_type="textarea", required=False)
