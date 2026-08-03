"""
Module 46: shared helpers for seeding the M2-HR equipment templates (Air Flow Relay, Earth Fault
Relay, OCR/MCR, Pressure Switch, Gauges, FDU, SPM, PC-8 Relay, VCU, Auxiliary Converter, Traction
Converter, MPCS, Meters).

Reuses `get_or_create_template` / `clear_existing_fields` / `run_seed` from `_aux_template_helpers.py`
unchanged. The only new piece is a `make_add` that threads a `page_number` (M2-HR source sheets are
frequently 2-3 physical pages), plus small conveniences for the row shapes that repeat across these
particular sheets (a Standard-word confirmation, a per-item group with std/actual numeric pair).
"""
from _aux_template_helpers import (  # noqa: F401
    clear_existing_fields,
    get_or_create_template,
    run_seed,
)
from app.models.template_field import TemplateField


def make_add(db, template_id, order_state, page_state):
    def add(field_key, parent=None, page=None, **kwargs):
        order_state[0] += 1
        f = TemplateField(
            template_id=template_id,
            field_key=field_key,
            display_order=order_state[0],
            page_number=page if page is not None else page_state[0],
            parent_field_id=parent.id if parent is not None else None,
            **kwargs,
        )
        db.add(f)
        db.flush()
        return f
    return add


def run_seed_paged(equipment_code, template_code, technology, template_name, description, build_fn):
    """Same contract as `_aux_template_helpers.run_seed`, but `build_fn` receives `(add, set_page)`
    instead of just `add`, where `set_page(n)` moves the page counter used by subsequent add() calls
    that don't pass their own `page=`."""
    from app.database.database import SessionLocal
    db = SessionLocal()
    try:
        from app.models.equipment import Equipment
        equipment = db.query(Equipment).filter(Equipment.equipment_code == equipment_code).first()
        if equipment is None:
            raise SystemExit(f"Equipment '{equipment_code}' not found - aborting.")

        template = get_or_create_template(db, template_code, equipment.id, technology, template_name, description)
        clear_existing_fields(db, template.id)

        order_state = [0]
        page_state = [1]
        add = make_add(db, template.id, order_state, page_state)

        def set_page(n):
            page_state[0] = n

        build_fn(add, set_page)

        db.commit()
        print(f"{template_name} template (id={template.id}) synchronized with reference checksheet. "
              f"{order_state[0]} field(s) inserted.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def add_confirm(add, key, label, done_word="Checked", negative_word=None, required=True,
                 standard_value=None, authority_reference=None, unit=None, parent=None, page=None):
    """The single most common M2-HR row shape: a "Standard" column word (Checked/Cleaned/Done/
    Intact/Tight/Ensured/Replaced) confirmed by the technician as either that word or its negation."""
    negative_word = negative_word or f"Not {done_word}"
    return add(
        key, parent=parent, page=page, field_label=label, field_type="select",
        options=f"{done_word}, {negative_word}", required=required,
        standard_value=standard_value or done_word, unit=unit,
        authority_reference=authority_reference, negative_values=negative_word,
    )


def add_numeric(add, key, label, standard_value, min_value=None, max_value=None, unit=None,
                 decimal_precision=2, required=True, authority_reference=None, parent=None, page=None):
    return add(
        key, parent=parent, page=page, field_label=label, field_type="numeric_range", required=required,
        min_value=min_value, max_value=max_value, unit=unit, decimal_precision=decimal_precision,
        standard_value=standard_value, authority_reference=authority_reference,
    )


def add_text(add, key, label, required=False, standard_value=None, unit=None,
              authority_reference=None, default_value=None, parent=None, page=None):
    return add(
        key, parent=parent, page=page, field_label=label, field_type="text", required=required,
        standard_value=standard_value, unit=unit, authority_reference=authority_reference,
        default_value=default_value,
    )


def add_date(add, key, label, required=True, parent=None, page=None):
    return add(key, parent=parent, page=page, field_label=label, field_type="date", required=required)
