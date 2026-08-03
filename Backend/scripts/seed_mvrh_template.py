"""
Seeds the MVRH (Motor for Radiator) checksheet template from its physical reference checksheet,
reusing the exact same generic template engine, metadata conventions, and validation engine
already built and verified for TMB/OCB - nothing new is introduced here, this is data only.

Run once: `venv/bin/python scripts/seed_mvrh_template.py`

Equipment "MVRH" (id=16) and its Section M35-Aux <-> MVRH <-> Conventional SectionEquipmentMap
row already exist - only the ChecksheetTemplate + TemplateField rows are new. technology=
'CONVENTIONAL' matches Locomotive.technology's own format - this template must NOT resolve for
3-Phase locomotives, only Conventional ones.

MVRH's document has only 21 checking points (not 22): it combines TMB's two separate crack-check
rows into a single "MPT of Impeller" row (matching OCB's consolidation pattern, though OCB calls
it "RDPT of Impeller"), and its Must Change Item has only 2 sub-items (Bearing 6313, transparent
sleeve - no Impeller Flakt/Arco on this document). Its Rotor Balancing standard reads "...& 40
micron on plate" (not "on casing" as on TMB/MVMT) and shows only 4 generic reading boxes with no
"On Drum" note. Bearing/end-cover dimension standards (65.002-65.015mm / 139.993-140.018mm) match
MVMT's document, both being larger than TMB/OCB's.

Idempotent: safe to re-run.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.database import SessionLocal
from app.models.checksheet_template import ChecksheetTemplate
from app.models.equipment import Equipment
from app.models.template_field import TemplateField

EQUIPMENT_CODE = "MVRH"
TEMPLATE_CODE = "3"


def main():
    db = SessionLocal()
    try:
        equipment = db.query(Equipment).filter(Equipment.equipment_code == EQUIPMENT_CODE).first()
        if equipment is None:
            raise SystemExit(f"Equipment '{EQUIPMENT_CODE}' not found - aborting.")

        template = get_or_create_template(db, equipment.id)
        clear_existing_fields(db, template.id)
        build_fields(db, template.id)
        db.commit()
        print(f"MVRH template (id={template.id}) synchronized with reference checksheet.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_or_create_template(db, equipment_id):
    existing = db.query(ChecksheetTemplate).filter(ChecksheetTemplate.template_code == TEMPLATE_CODE).first()
    if existing:
        print(f"Template code '{TEMPLATE_CODE}' already exists (id={existing.id}), reusing it.")
        return existing

    template = ChecksheetTemplate(
        template_code=TEMPLATE_CODE,
        version=1,
        equipment_id=equipment_id,
        section_id=None,
        technology="CONVENTIONAL",
        template_name="Checksheet for MVRH",
        description="Motor for Radiator checksheet.",
        is_active=True,
    )
    db.add(template)
    db.flush()
    print(f"Created template id={template.id} for equipment_id={equipment_id}.")
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
    print(f"Removed {removed} pre-existing MVRH template field(s).")


def build_fields(db, template_id):
    order = [0]

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
        negative_values="Abnormal",
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
        negative_values="Not done",
    )

    # S.N. 4
    add(
        "surge_comparison_test", field_label="Surge Comparison Test at 3 KV Peak to Peak",
        field_type="select", options="Wave form OK, Wave form Not OK", required=True,
        standard_value="Wave form OK", authority_reference="SMI-149",
        negative_values="Wave form Not OK",
    )

    # S.N. 5
    add(
        "thread_condition_end_shield_bolt", field_label="Thread Condition in Stator Body of End Shield Bolt",
        field_type="select", options="Normal, Abnormal", required=True,
        standard_value="Normal", authority_reference="Shed practice",
        negative_values="Abnormal",
    )

    # S.N. 6 - MVRH's own bearing dimension standard (65.002-65.015mm)
    bearing_seat = add(
        "bearing_dia_rotor_shaft", field_label="Bearing Dia. of Rotor Shaft (for 6313)",
        field_type="group", required=False, authority_reference="SMI-16",
    )
    add(
        "bearing_dia_de", parent=bearing_seat, field_label="DE",
        field_type="numeric_range", required=True, unit="mm",
        min_value=65.002, max_value=65.015, decimal_precision=3,
        standard_value="65.002 - 65.015 mm",
    )
    add(
        "bearing_dia_nde", parent=bearing_seat, field_label="NDE",
        field_type="numeric_range", required=True, unit="mm",
        min_value=65.002, max_value=65.015, decimal_precision=3,
        standard_value="65.002 - 65.015 mm",
    )

    # S.N. 7
    end_cover = add(
        "end_cover_bore_dia", field_label="End Cover Bore Dia.",
        field_type="group", required=False, authority_reference="SMI-16",
    )
    add(
        "end_cover_bore_dia_de", parent=end_cover, field_label="DE",
        field_type="numeric_range", required=True, unit="mm",
        min_value=139.993, max_value=140.018, decimal_precision=3,
        standard_value="139.993 - 140.018 mm",
    )
    add(
        "end_cover_bore_dia_nde", parent=end_cover, field_label="NDE",
        field_type="numeric_range", required=True, unit="mm",
        min_value=139.993, max_value=140.018, decimal_precision=3,
        standard_value="139.993 - 140.018 mm",
    )

    # S.N. 8
    add(
        "rotor_growler_test", field_label="Rotor Growler Test",
        field_type="select", options="Normal, Abnormal", required=True,
        standard_value="Normal", authority_reference="SMI-163",
        negative_values="Abnormal",
    )

    # S.N. 9 - Rule 3 (Percentage Difference), 10% threshold
    winding_resistance = add(
        "winding_resistance_comparison", field_label="Winding Resistance for Comparison",
        field_type="group", required=False,
        standard_value="Difference not more than 10%", authority_reference="TC-142",
        validation_rule="percentage_difference", validation_threshold=10.0,
    )
    for phase in ["RY", "YB", "BR"]:
        add(
            f"winding_resistance_{phase.lower()}", parent=winding_resistance, field_label=phase,
            field_type="number", required=True, unit="Ohm",
        )

    # S.N. 10 - Rule 3 (Percentage Difference), 10% threshold
    winding_inductance = add(
        "winding_inductance_comparison", field_label="Winding Inductance for Comparison",
        field_type="group", required=False,
        standard_value="Difference not more than 10%", authority_reference="TC-142",
        validation_rule="percentage_difference", validation_threshold=10.0,
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
        negative_values="Not in Green Zone",
    )

    # S.N. 14 - Rule 4 (Phase Imbalance), 5% threshold
    lug_temp = add(
        "temp_3_lugs_after_run_test", field_label="Temperature on 3 Lugs After One Hour Run Test",
        field_type="group", required=False,
        standard_value="Temp. difference not more than 5 C, if more, lug to be changed",
        authority_reference="Shed practice",
        validation_rule="percentage_difference", validation_threshold=5.0,
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

    # S.N. 16 - no numeric standard in the source document
    impeller_fit = add(
        "impeller_bore_shaft_dia", field_label="Bore Dia. of Impeller / Shaft Dia. of Impeller Sitting",
        field_type="group", required=False, authority_reference="TC-142",
    )
    add("impeller_bore_dia", parent=impeller_fit, field_label="Bore Dia. of Impeller", field_type="number", required=False, unit="mm")
    add("impeller_shaft_dia", parent=impeller_fit, field_label="Shaft Dia. of Impeller Sitting", field_type="number", required=True, unit="mm")

    # S.N. 17 - MVRH's document combines the two crack-check rows into a single "MPT of Impeller"
    # checkpoint (matching OCB's consolidation, unlike TMB/MVMT which keep them separate).
    add(
        "mpt_impeller", field_label="MPT of Impeller",
        field_type="select", options="No Crack, Crack Found", required=True,
        standard_value="No crack", authority_reference="Shed practice",
        negative_values="Crack Found",
    )

    # S.N. 18 - only 4 generic reading boxes on this document, no "On Drum" note (unlike
    # TMB/MVMT), and the standard reads "on plate" rather than "on casing".
    rotor_balancing = add(
        "rotor_balancing_portable_balancer", field_label="Rotor Balancing with Impeller by Portable Balancer",
        field_type="group", required=False,
        standard_value="Max. 15 micron on motor & 40 micron on plate", authority_reference="SMI-199",
    )
    for i in range(1, 5):
        add(
            f"rotor_balancing_reading_{i}", parent=rotor_balancing, field_label=f"Reading {i}",
            field_type="number", required=False, unit="micron",
        )

    # S.N. 19 - Must Change Item: only 2 sub-items on this document (Bearing 6313, transparent
    # sleeve) - no Impeller Flakt/Arco, matching OCB's 2-item pattern rather than TMB/MVMT's 4.
    must_change = add(
        "must_change_item", field_label="Must Change Item",
        field_type="group", required=False,
    )
    bearing_6313 = add(
        "must_change_bearing_6313", parent=must_change, field_label="Bearing 6313 (PL No. 85.01.1885)",
        field_type="group", required=False,
        standard_value="IOH item but change in 3 yrs.",
        authority_reference="As per RDSO TC-29",
    )
    add("bearing_6313_status", parent=bearing_6313, field_label="Status", field_type="select", options="New, Original", required=True)
    add("bearing_6313_lpro_date", parent=bearing_6313, field_label="L/Pro. Date", field_type="date", required=False)
    add("bearing_6313_make", parent=bearing_6313, field_label="Make", field_type="text", required=False)

    add(
        "must_change_transparent_sleeve", parent=must_change, field_label="Transparent Sleeve on Lead Provided",
        field_type="boolean", required=True,
        standard_value="To provide.", authority_reference="Shed practice",
        negative_values="false",
    )

    # S.N. 20
    add(
        "polarization_index", field_label="Polarization Index (PI) Value at 1000V",
        field_type="text", required=True,
        standard_value="Not less than 1 and more than 4", authority_reference="Shed practice",
    )

    # S.N. 21 (MVRH's document has 21 checkpoints total, not 22)
    add(
        "final_remarks", field_label="Remarks / Any Other New Material",
        field_type="textarea", required=False,
    )

    print(f"Inserted {order[0]} field(s) for the MVRH template.")


if __name__ == "__main__":
    main()
