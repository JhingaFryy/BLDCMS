"""
Module 29.11: seeds the SR Pump (Oil Pump for Traction Converter) checksheet template.

Run once: `venv/bin/python scripts/seed_srpump_template.py`

Same pump-family structure as TFP Pump (Full Load Current + Temp Rise only, no 3-lug check,
impeller condition/RTV/oil leakage checkpoints), but the bearing/end-cover Standard cells are
blank on this specific sheet - no tolerance range is given, so DE/NDE are plain (unranged) number
fields rather than numeric_range. Same Must Change Item column-alignment ambiguity as TFP Pump/
MPH, resolved the same sequential best-effort way.
"""
from _aux_template_helpers import (
    run_seed, add_pre_test_vibration, add_ir_before_dismantle, add_cleaning_backing_varnishing,
    add_surge_comparison_test, add_thread_condition, add_rotor_growler_test, add_winding_resistance,
    add_winding_inductance, add_ir_after_assembly, add_run_test_no_full_temp, add_bearing_condition_spm,
    add_work_done_lead_lug, add_bore_shaft_impeller, add_polarization_index, add_final_remarks,
)


def build(add):
    add_pre_test_vibration(add)
    add_ir_before_dismantle(add)
    add_cleaning_backing_varnishing(add)
    add_surge_comparison_test(add)
    add_thread_condition(add)

    bearing = add(
        "bearing_seat_dia_rotor_shaft", field_label="Bearing Sheet Dia. of Rotor Shaft",
        field_type="group", required=False, authority_reference="SMI-16",
    )
    add("bearing_seat_dia_de", parent=bearing, field_label="DE", field_type="number", required=False, unit="mm")
    add("bearing_seat_dia_nde", parent=bearing, field_label="NDE", field_type="number", required=False, unit="mm")

    end_cover = add(
        "end_cover_bore_dia", field_label="End Cover Bore Dia.",
        field_type="group", required=False, authority_reference="SMI-16",
    )
    add("end_cover_bore_dia_de", parent=end_cover, field_label="DE", field_type="number", required=False, unit="mm")
    add("end_cover_bore_dia_nde", parent=end_cover, field_label="NDE", field_type="number", required=False, unit="mm")

    add_rotor_growler_test(add)
    add_winding_resistance(add)
    add_winding_inductance(add)
    add_ir_after_assembly(add)
    add_run_test_no_full_temp(add, no_load=False)
    add_bearing_condition_spm(add)
    add_work_done_lead_lug(add, label="Any Work Done on Lead, Lug, Terminal Block, Nomex Paper to Provide")

    add(
        "impeller_condition_check", field_label="To Check Condition of Impeller for Any Crack or Rubbing Mark",
        field_type="select", options="Good Condition, Not Good Condition", required=True,
        standard_value="Good condition", authority_reference="Shed practice.",
        negative_values="Not Good Condition",
    )
    add_bore_shaft_impeller(add)
    add(
        "rtv_end_cover", field_label="RTV to Apply on End Cover",
        field_type="boolean", required=True,
        standard_value="To provide", authority_reference="Shed practice",
        negative_values="false",
    )
    add(
        "oil_leakage_check", field_label="Oil Leakage to Check by Applying 1.5 kg/cm2 Air Pressure",
        field_type="select", options="No Leakage, Leakage Found", required=True,
        standard_value="No leakage", authority_reference="Shed practice.",
        negative_values="Leakage Found",
    )

    must_change = add("must_change_item", field_label="Must Change Item", field_type="group", required=False)
    add(
        "must_change_bearing", parent=must_change, field_label="Bearing",
        field_type="select", options="Provided, Not Provided", required=True,
        standard_value="AOH item", authority_reference="Shed practice",
    )
    add(
        "must_change_rubber_o_ring", parent=must_change, field_label='To Replace Set of Rubber "O" Ring',
        field_type="select", options="Provided, Not Provided", required=True,
        standard_value="IOH item as per TC", authority_reference="As per RDSO TC-29",
    )
    add(
        "must_change_transparent_sleeve", parent=must_change, field_label="Transparent Sleeve on Lead Provided",
        field_type="boolean", required=True,
        standard_value="To provide.", authority_reference="As per RDSO TC-31 / Shed practice.",
        negative_values="false",
    )

    add_polarization_index(add)
    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="SR Pump", template_code="10", technology="3_PHASE",
        template_name="Checksheet for SR Pump",
        description="Oil Pump for Traction Converter checksheet.",
        build_fn=build,
    )
