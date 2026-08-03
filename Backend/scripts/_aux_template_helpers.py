"""
Module 29.11: shared helpers for seeding the remaining M35-Aux equipment templates.

This is NOT application code - it's reuse within the seed-scripts layer itself, to avoid
copy-pasting the same ~10 near-identical checking points (Pre Testing, IR Before Dismantle,
Cleaning/Varnishing, Surge Test, Thread Condition, Rotor Growler Test, Winding
Resistance/Inductance Comparison, IR After Assembly, Bearing Condition SPM, 3-Lug Temperature)
across every one of the 15 remaining seed scripts. Every function here just calls the same
generic `add()` callback each script's own base already uses - nothing here is a new template
engine concept, field type, or validation type; it is 100% the existing Module 29.5/29.9 metadata
columns (field_type, min_value/max_value, validation_rule/validation_threshold, negative_values).

Each function takes the template-specific bits that actually vary (a different bearing/end-cover
tolerance range, a different authority string, etc.) as parameters, defaulting to the value seen
on most of the sheets.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.database import SessionLocal  # noqa: E402
from app.models.checksheet_template import ChecksheetTemplate  # noqa: E402
from app.models.template_field import TemplateField  # noqa: E402


def get_or_create_template(db, template_code, equipment_id, technology, template_name, description):
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
        template_name=template_name,
        description=description,
        is_active=True,
    )
    db.add(template)
    db.flush()
    print(f"Created template id={template.id} for equipment_id={equipment_id} ({template_name}).")
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
            page_number=1,
            parent_field_id=parent.id if parent is not None else None,
            **kwargs,
        )
        db.add(f)
        db.flush()
        return f
    return add


# --- Shared checking points (the ~10 rows that repeat almost verbatim on every sheet) ---

def add_pre_test_vibration(add):
    return add(
        "pre_test_vibration", field_label="Pre Testing for Any Abnormal Sound/Vibration",
        field_type="select", options="Normal, Abnormal", required=True,
        standard_value="Normal", authority_reference="Shed practice",
        negative_values="Abnormal",
    )


def add_ir_before_dismantle(add, standard="Min 1 M.Ohm", min_value=1.0):
    return add(
        "ir_value_before_dismantle", field_label="IR Value Before Dismantle (with 500V Megger)",
        field_type="numeric_range", required=True, unit="MOhm", min_value=min_value, decimal_precision=2,
        standard_value=standard, authority_reference="Shed practice",
    )


def add_cleaning_backing_varnishing(add, authority="Shed practice"):
    return add(
        "cleaning_backing_varnishing", field_label="Cleaning, Backing, Anti-Tracking Varnishing",
        field_type="select", options="Done, Not done", required=True,
        standard_value="Done", authority_reference=authority,
        negative_values="Not done",
    )


def add_surge_comparison_test(add, standard="Wave form should be OK"):
    return add(
        "surge_comparison_test", field_label="Surge Comparison Test at 3 KV Peak to Peak",
        field_type="select", options="Wave form OK, Wave form Not OK", required=True,
        standard_value=standard, authority_reference="SMI-149",
        negative_values="Wave form Not OK",
    )


def add_thread_condition(add):
    return add(
        "thread_condition_end_shield_bolt", field_label="Thread Condition in Stator Body of End Shield Bolt",
        field_type="select", options="Normal, Abnormal", required=True,
        standard_value="Normal", authority_reference="Shed practice",
        negative_values="Abnormal",
    )


def add_rotor_growler_test(add):
    return add(
        "rotor_growler_test", field_label="Rotor Growler Test",
        field_type="select", options="Normal, Abnormal", required=True,
        standard_value="Normal", authority_reference="SMI-163",
        negative_values="Abnormal",
    )


def add_winding_resistance(add, phases=("RY", "YB", "BR"), standard="Difference not more than 10%"):
    group = add(
        "winding_resistance_comparison", field_label="Winding Resistance for Comparison",
        field_type="group", required=False,
        standard_value=standard, authority_reference="TC-142",
        validation_rule="percentage_difference", validation_threshold=10.0,
    )
    for phase in phases:
        add(f"winding_resistance_{phase.lower().replace('.', '')}", parent=group, field_label=phase,
            field_type="number", required=True, unit="Ohm")
    return group


def add_winding_inductance(add, phases=("RY", "YB", "BR"), standard="Difference not more than 10%", validate=True):
    kwargs = dict(
        field_type="group", required=False,
        standard_value=standard, authority_reference="TC-142",
    )
    if validate:
        kwargs["validation_rule"] = "percentage_difference"
        kwargs["validation_threshold"] = 10.0
    group = add("winding_inductance_comparison", field_label="Winding Inductance for Comparison", **kwargs)
    for phase in phases:
        add(f"winding_inductance_{phase.lower().replace('.', '')}", parent=group, field_label=phase,
            field_type="number", required=True, unit="mH")
    return group


def add_ir_after_assembly(add, standard="Min. 5 M.Ohm"):
    return add(
        "ir_value_after_assembly", field_label="IR Value After Assembly",
        field_type="numeric_range", required=True, unit="MOhm", min_value=5.0, decimal_precision=2,
        standard_value=standard, authority_reference="Shed practice",
    )


def add_bearing_condition_spm(add):
    return add(
        "bearing_condition_spm", field_label="Bearing Condition Monitoring by SPM",
        field_type="select", options="Green Zone, Not in Green Zone", required=True,
        standard_value="Green zone", authority_reference="SMI-58",
        negative_values="Not in Green Zone",
    )


def add_lug_temp_group(add):
    group = add(
        "temp_3_lugs_after_run_test", field_label="Temperature on 3 Lugs After One Hour Run Test",
        field_type="group", required=False,
        standard_value="Temp. difference not more than 5 C, if more, lug to be changed",
        authority_reference="Shed practice",
        validation_rule="percentage_difference", validation_threshold=5.0,
    )
    for phase in ["U", "V", "W"]:
        add(f"lug_temp_{phase.lower()}", parent=group, field_label=phase, field_type="number", required=True, unit="C")
    return group


def add_work_done_lead_lug(add, label="Any Work Done on Lead, Lug, Terminal Block"):
    return add(
        "work_done_lead_lug_terminal", field_label=label,
        field_type="textarea", required=False,
        standard_value="If done to be noted", authority_reference="Shed practice",
    )


def add_polarization_index(add, field_key="polarization_index", label="Polarization Index (PI) Value at 1000V",
                            standard="Not less than 1 and more than 4"):
    return add(
        field_key, field_label=label,
        field_type="text", required=True,
        standard_value=standard, authority_reference="Shed practice",
    )


def add_final_remarks(add, label="Remarks / Any Other New Material"):
    return add("final_remarks", field_label=label, field_type="textarea", required=False)


def add_run_test_no_full_temp(add, no_load=True, full_load=True, temp_rise=True, temp_children=("Body", "DE", "NDE", "Amb")):
    """Run Test After Assembly, with the sub-groups present on THIS sheet only - several
    equipment omit No Load Current or Full Load Current (e.g. compressors only run test one way)."""
    run_test = add(
        "run_test_after_assembly", field_label="Run Test After Assembly",
        field_type="group", required=False, authority_reference="Shed practice",
    )
    if no_load:
        no_load_group = add("no_load_current", parent=run_test, field_label="No Load Current",
                             field_type="group", required=False, standard_value="As per data sheet")
        for phase in ["U", "V", "W"]:
            add(f"no_load_current_{phase.lower()}", parent=no_load_group, field_label=phase,
                field_type="number", required=True, unit="A")
    if full_load:
        full_load_group = add("full_load_current", parent=run_test, field_label="Full Load Current",
                               field_type="group", required=False, standard_value="As per data sheet")
        for phase in ["U", "V", "W"]:
            add(f"full_load_current_{phase.lower()}", parent=full_load_group, field_label=phase,
                field_type="number", required=True, unit="A")
    if temp_rise:
        temp_group = add("temp_rise_on_motor", parent=run_test, field_label="Temp Rise on Motor",
                          field_type="group", required=False, standard_value="Ambient +25 C")
        for leaf_label in temp_children:
            add(f"temp_rise_{leaf_label.lower()}", parent=temp_group, field_label=leaf_label,
                field_type="number", required=True, unit="C")
    return run_test


def add_bore_shaft_impeller(add, authority="TC-142", standard=None):
    group = add(
        "impeller_bore_shaft_dia", field_label="Bore Dia. of Impeller / Shaft Dia. of Impeller Sitting",
        field_type="group", required=False, authority_reference=authority, standard_value=standard,
    )
    add("impeller_bore_dia", parent=group, field_label="Bore Dia. of Impeller", field_type="number", required=False, unit="mm")
    add("impeller_shaft_dia", parent=group, field_label="Shaft Dia. of Impeller Sitting", field_type="number", required=True, unit="mm")
    return group


def add_casing_crack_check(add, label="To Check Casing for Any Crack", field_key="casing_crack_check"):
    return add(
        field_key, field_label=label,
        field_type="select", options="No Crack, Crack Found", required=True,
        standard_value="No crack", authority_reference="Shed practice",
        negative_values="Crack Found",
    )


def add_transparent_sleeve(add, parent):
    return add(
        "must_change_transparent_sleeve", parent=parent, field_label="Transparent Sleeve on Lead Provided",
        field_type="boolean", required=True,
        standard_value="To provide", authority_reference="Shed practice",
        negative_values="false",
    )


def add_bearing_group(add, parent, field_key, label, standard, authority):
    bearing = add(
        field_key, parent=parent, field_label=label,
        field_type="group", required=False,
        standard_value=standard, authority_reference=authority,
    )
    add(f"{field_key}_status", parent=bearing, field_label="Status", field_type="select", options="New, Original", required=True)
    add(f"{field_key}_lpro_date", parent=bearing, field_label="L/Pro. Date", field_type="date", required=False)
    add(f"{field_key}_make", parent=bearing, field_label="Make", field_type="text", required=False)
    return bearing


def run_seed(equipment_code, template_code, technology, template_name, description, build_fn):
    """Common entry point every per-equipment script calls: looks up the equipment, creates/
    reuses its template, clears old fields, and runs build_fn(add) to populate new ones."""
    db = SessionLocal()
    try:
        from app.models.equipment import Equipment
        equipment = db.query(Equipment).filter(Equipment.equipment_code == equipment_code).first()
        if equipment is None:
            raise SystemExit(f"Equipment '{equipment_code}' not found - aborting.")

        template = get_or_create_template(db, template_code, equipment.id, technology, template_name, description)
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
