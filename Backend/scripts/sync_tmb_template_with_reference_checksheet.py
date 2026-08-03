"""
Synchronizes the TMB (Traction Motor Blower) template (checksheet_templates.id == TMB_TEMPLATE_ID)
with the physically filled reference checksheet supplied for this equipment, so every checking
point S.N. 1-22 on that document is represented, correctly typed, and in document order.

Run once: `venv/bin/python scripts/sync_tmb_template_with_reference_checksheet.py`

Why a full rebuild rather than incremental patching: at the time this was written, the live
database had zero checksheet_header/checksheet_value rows (verified before running), so there was
no historical-data risk in replacing the TMB template's existing fields outright - they were
seeded from an earlier illustrative example (not the real document) and had several mismatches
(wrong authority text, wrong grouped-leaf labels, several rows missing entirely). If this script
is ever re-run against a database that DOES have real checksheet_value rows referencing these
fields, deleting a referenced field will raise a FK violation and the run will stop - it is not
designed to silently archive around real data (see template_field_service.delete_field for that
logic, used by the interactive delete-field API instead).

Every column used here (field_type, min_value/max_value, standard_value, authority_reference,
parent_field_id, page_number, options, unit) is the existing generic Module 29.5 template schema -
nothing TMB-specific was added to the engine. In particular this seed demonstrates that a GROUP's
leaf children can themselves be NUMERIC_RANGE fields (independently range-validated) with zero
additional code: TemplateField places no type constraint between a parent and its children, the
backend's compose logic serializes min/max for every field regardless of nesting, and Android's
GroupComponent dispatches each leaf through the same FieldRendererRegistry used for top-level
fields.

Idempotent: safe to re-run - deletes and recreates the TMB template's own fields every time (the
section-wide M35-Aux common page, which already correctly covers Aux Serial No/Make/Mfg
Date/Rewinding Date/Overhaul Date/VPI Date from the document's header block, is untouched).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.database import SessionLocal
from app.models.checksheet_template import ChecksheetTemplate
from app.models.template_field import TemplateField

TMB_TEMPLATE_ID = 5


def main():
    db = SessionLocal()
    try:
        template = db.query(ChecksheetTemplate).filter(ChecksheetTemplate.id == TMB_TEMPLATE_ID).first()
        if template is None or template.equipment_id != 6:
            raise SystemExit(f"Expected template id={TMB_TEMPLATE_ID} to be the TMB equipment template - aborting.")

        clear_existing_fields(db, TMB_TEMPLATE_ID)
        build_fields(db, TMB_TEMPLATE_ID)
        db.commit()
        print("TMB template synchronized with reference checksheet.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


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
    print(f"Removed {removed} pre-existing TMB template field(s).")


def build_fields(db, template_id):
    order = [0]  # single incrementing counter shared across the whole page, mutable via closure

    def add(field_key, parent=None, **kwargs):
        order[0] += 1
        f = TemplateField(
            template_id=template_id,
            field_key=field_key,
            display_order=order[0],
            page_number=1,
            parent_field_id=parent.id if parent is not None else None,
            **kwargs,
        )
        db.add(f)
        db.flush()
        return f

    # S.N. 1
    add(
        "pre_test_vibration", field_label="Pre Testing for Any Abnormal Sound/Vibration",
        field_type="select", options="Normal, Abnormal", required=True,
        standard_value="Normal", authority_reference="Shed practice",
    )

    # S.N. 2
    add(
        "ir_value_before_dismantle", field_label="IR Value Before Dismantle (with 500V Megger)",
        field_type="numeric_range", required=True, unit="MOhm", min_value=1.0, decimal_precision=2,
        standard_value="Min 1 M.Ohm", authority_reference="Shed practice",
    )

    # S.N. 3
    add(
        "cleaning_backing_varnishing", field_label="Cleaning, Backing, Anti-Tracking Varnishing",
        field_type="select", options="Done, Not done", required=True,
        standard_value="Done", authority_reference="Shed practice",
    )

    # S.N. 4
    add(
        "surge_comparison_test", field_label="Surge Comparison Test at 3 KV Peak to Peak",
        field_type="select", options="Wave form OK, Wave form Not OK", required=True,
        standard_value="Wave form - OK", authority_reference="SMI-149",
    )

    # S.N. 5
    add(
        "thread_condition_end_shield_bolt", field_label="Thread Condition in Stator Body of End Shield Bolt",
        field_type="select", options="Normal, Abnormal", required=True,
        standard_value="Normal", authority_reference="Shed practice",
    )

    # S.N. 6 - group whose leaves are themselves range-validated (DE/NDE)
    bearing_seat = add(
        "bearing_seat_dia_rotor_shaft", field_label="Bearing Seat Dia. of Rotor Shaft (for 6313)",
        field_type="group", required=False, authority_reference="SMI-16",
    )
    add(
        "bearing_seat_dia_de", parent=bearing_seat, field_label="DE",
        field_type="numeric_range", required=True, unit="mm",
        min_value=60.002, max_value=60.015, decimal_precision=3,
        standard_value="60.002 - 60.015 mm",
    )
    add(
        "bearing_seat_dia_nde", parent=bearing_seat, field_label="NDE",
        field_type="numeric_range", required=True, unit="mm",
        min_value=60.002, max_value=60.015, decimal_precision=3,
        standard_value="60.002 - 60.015 mm",
    )

    # S.N. 7
    end_cover = add(
        "end_cover_bore_dia", field_label="End Cover Bore Dia.",
        field_type="group", required=False, authority_reference="SMI-16",
    )
    add(
        "end_cover_bore_dia_de", parent=end_cover, field_label="DE",
        field_type="numeric_range", required=True, unit="mm",
        min_value=129.993, max_value=130.013, decimal_precision=3,
        standard_value="129.993 - 130.013 mm",
    )
    add(
        "end_cover_bore_dia_nde", parent=end_cover, field_label="NDE",
        field_type="numeric_range", required=True, unit="mm",
        min_value=129.993, max_value=130.013, decimal_precision=3,
        standard_value="129.993 - 130.013 mm",
    )

    # S.N. 8
    add(
        "rotor_growler_test", field_label="Rotor Growler Test",
        field_type="select", options="Normal, Abnormal", required=True,
        standard_value="Normal", authority_reference="SMI-163",
    )

    # S.N. 9 - grouped comparison, no fixed numeric bound (relative % difference) -> plain number leaves
    winding_resistance = add(
        "winding_resistance_comparison", field_label="Winding Resistance for Comparison",
        field_type="group", required=False,
        standard_value="Difference not more than 10%", authority_reference="TC-142",
    )
    for phase in ["RY", "YB", "BR"]:
        add(
            f"winding_resistance_{phase.lower()}", parent=winding_resistance, field_label=phase,
            field_type="number", required=True, unit="Ohm",
        )

    # S.N. 10
    winding_inductance = add(
        "winding_inductance_comparison", field_label="Winding Inductance for Comparison",
        field_type="group", required=False,
        standard_value="Difference not more than 10%", authority_reference="TC-142",
    )
    for phase in ["RY", "YB", "BR"]:
        add(
            f"winding_inductance_{phase.lower()}", parent=winding_inductance, field_label=phase,
            field_type="number", required=True, unit="mH",
        )

    # S.N. 11
    add(
        "ir_value_after_assembly", field_label="IR Value After Assembly",
        field_type="numeric_range", required=True, unit="MOhm", min_value=5.0, decimal_precision=2,
        standard_value="Min. 5 M.Ohm", authority_reference="Shed practice",
    )

    # S.N. 12 - Run Test After Assembly: three nested sub-groups
    run_test = add(
        "run_test_after_assembly", field_label="Run Test After Assembly",
        field_type="group", required=False, authority_reference="Shed practice",
    )
    no_load = add(
        "no_load_current", parent=run_test, field_label="No Load Current",
        field_type="group", required=False, standard_value="As per data sheet",
    )
    full_load = add(
        "full_load_current", parent=run_test, field_label="Full Load Current",
        field_type="group", required=False, standard_value="As per data sheet",
    )
    for group in (no_load, full_load):
        for phase in ["U", "V", "W"]:
            add(
                f"{group.field_key}_{phase.lower()}", parent=group, field_label=phase,
                field_type="number", required=True, unit="A",
            )
    temp_rise = add(
        "temp_rise_on_motor", parent=run_test, field_label="Temp Rise on Motor",
        field_type="group", required=False, standard_value="Ambient +25 C",
    )
    for leaf_key, leaf_label in [("body", "Body"), ("de", "DE"), ("nde", "NDE"), ("amb", "Amb")]:
        add(
            f"temp_rise_{leaf_key}", parent=temp_rise, field_label=leaf_label,
            field_type="number", required=True, unit="C",
        )

    # S.N. 13
    add(
        "bearing_condition_spm", field_label="Bearing Condition Monitoring by SPM",
        field_type="select", options="Green Zone, Not in Green Zone", required=True,
        standard_value="Green zone", authority_reference="SMI-58",
    )

    # S.N. 14 - a second, independent U/V/W group (not nested under Run Test) - proves the same
    # grouped-field component is reusable for unrelated checkpoints, not hardcoded to S.N. 12.
    lug_temp = add(
        "temp_3_lugs_after_run_test", field_label="Temperature on 3 Lugs After One Hour Run Test",
        field_type="group", required=False,
        standard_value="Temp. difference not more than 5 C, if more, lug to be changed",
        authority_reference="Shed practice",
    )
    for phase in ["U", "V", "W"]:
        add(
            f"lug_temp_{phase.lower()}", parent=lug_temp, field_label=phase,
            field_type="number", required=True, unit="C",
        )

    # S.N. 15
    add(
        "work_done_lead_lug_terminal", field_label="Any Work Done on Lead, Lug, Terminal Block",
        field_type="textarea", required=False,
        standard_value="If done to be noted", authority_reference="Shed practice",
    )

    # S.N. 16
    impeller_fit = add(
        "impeller_bore_shaft_dia", field_label="Bore Dia. of Impeller / Shaft Dia. of Impeller Sitting",
        field_type="group", required=False, authority_reference="TC-142",
    )
    add(f"impeller_bore_dia", parent=impeller_fit, field_label="Bore Dia. of Impeller", field_type="number", required=True, unit="mm")
    add(f"impeller_shaft_dia", parent=impeller_fit, field_label="Shaft Dia. of Impeller Sitting", field_type="number", required=True, unit="mm")

    # S.N. 17
    add(
        "casing_crack_check", field_label="To Check Casing for Any Crack",
        field_type="select", options="No Crack, Crack Found", required=True,
        standard_value="No crack", authority_reference="Shed practice",
    )

    # S.N. 18
    add(
        "mpt_impeller", field_label="MPT of Impeller",
        field_type="select", options="No Crack, Crack Found", required=True,
        standard_value="No crack", authority_reference="Shed practice",
    )

    # S.N. 19 - grouped, each leaf independently range-validated (max-only bound)
    rotor_balancing = add(
        "rotor_balancing_portable_balancer", field_label="Rotor Balancing with Impeller by Portable Balancer",
        field_type="group", required=False, authority_reference="SMI-199",
    )
    add(
        "rotor_balancing_on_motor", parent=rotor_balancing, field_label="On Motor",
        field_type="numeric_range", required=True, unit="micron", max_value=15.0,
        standard_value="Max. 15 micron on motor",
    )
    add(
        "rotor_balancing_on_casing", parent=rotor_balancing, field_label="On Casing",
        field_type="numeric_range", required=True, unit="micron", max_value=40.0,
        standard_value="Max. 40 micron on casing",
    )

    # S.N. 20 - Must Change Item: nested groups per part, demonstrating arbitrary grouping depth
    must_change = add(
        "must_change_item", field_label="Must Change Item",
        field_type="group", required=False,
    )
    bearing_6313 = add(
        "must_change_bearing_6313", parent=must_change, field_label="Bearing 6313 (PL No. 85.01.1885)",
        field_type="group", required=False,
        standard_value="IOH item but change in 4 yrs, 10 years old to change",
        authority_reference="As per RDSO TC-29",
    )
    add(f"bearing_6313_status", parent=bearing_6313, field_label="Status", field_type="select", options="New, Original", required=True)
    add(f"bearing_6313_lpro_date", parent=bearing_6313, field_label="L/Pro. Date", field_type="date", required=False)
    add(f"bearing_6313_make", parent=bearing_6313, field_label="Make", field_type="text", required=False)

    # 2026-07: Impeller Flakt/Arco (two separate make-specific line items) replaced with a single
    # generic "Impeller (Make)" text box - see scripts/update_tmb_must_change_item.py, which
    # applies this same change directly against the live database without disturbing the two real
    # historical checksheets that still reference the old fields (archived, not deleted).
    add(
        "must_change_impeller_make", parent=must_change, field_label="Impeller (Make)",
        field_type="text", required=False,
    )

    add(
        "must_change_transparent_sleeve", parent=must_change, field_label="Transparent Sleeve on Lead Provided",
        field_type="boolean", required=True,
        standard_value="To provide", authority_reference="Shed practice",
    )

    # S.N. 21
    add(
        "polarization_index", field_label="Polarization Index (PI) Value at 1000V",
        field_type="numeric_range", required=True, min_value=1.0, max_value=4.0, decimal_precision=2,
        standard_value="Not less than 1 and not more than 4", authority_reference="Shed practice",
    )

    # S.N. 22
    add(
        "final_remarks", field_label="Remarks / Any Other Material",
        field_type="textarea", required=False,
    )

    print(f"Inserted {order[0]} field(s) for the TMB template.")


if __name__ == "__main__":
    main()
