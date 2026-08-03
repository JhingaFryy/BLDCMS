"""
Module 29.11: seeds the TFP Pump (Transformer Oil Filtration Pump) checksheet template.

Run once: `venv/bin/python scripts/seed_tfppump_template.py`

Distinctive: pump-style equipment, not a blower - DE/NDE bearings use different part numbers
(4306/6306) sharing the same tolerance; Run Test only has Full Load Current + Temp Rise (no No
Load Current, and no 3-lug temperature check at all - this class of equipment skips it entirely);
several new checkpoints (impeller condition, RTV on end cover, oil leakage) replace the
blower-family's casing-crack/MPT/must-change-item-with-sleeve-only pattern.

The Must Change Item row's Standard/Authority column alignment is genuinely ambiguous in the
source document (4 lines of text across only 3 lettered sub-items) - mapped here on a best-effort,
sequential basis; flagged in the module report.
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
    add_cleaning_backing_varnishing(add, authority=None)
    add_surge_comparison_test(add)
    add_thread_condition(add)

    bearing = add(
        "bearing_seat_dia_rotor_shaft", field_label="Bearing Seat Dia. of Rotor Shaft (DE 4306 / NDE 6306)",
        field_type="group", required=False, authority_reference="SMI-16",
    )
    add("bearing_seat_dia_de", parent=bearing, field_label="DE (Bearing 4306)", field_type="numeric_range", required=True, unit="mm",
        min_value=30.002, max_value=30.013, decimal_precision=3, standard_value="30.002 - 30.013 mm")
    add("bearing_seat_dia_nde", parent=bearing, field_label="NDE (Bearing 6306)", field_type="numeric_range", required=True, unit="mm",
        min_value=30.002, max_value=30.013, decimal_precision=3, standard_value="30.002 - 30.013 mm")

    end_cover = add(
        "end_cover_bore_dia", field_label="End Cover Bore Dia.",
        field_type="group", required=False, authority_reference="SMI-16",
    )
    add("end_cover_bore_dia_de", parent=end_cover, field_label="DE", field_type="numeric_range", required=True, unit="mm",
        min_value=71.994, max_value=72.013, decimal_precision=3, standard_value="71.994 - 72.013 mm")
    add("end_cover_bore_dia_nde", parent=end_cover, field_label="NDE", field_type="numeric_range", required=True, unit="mm",
        min_value=71.994, max_value=72.013, decimal_precision=3, standard_value="71.994 - 72.013 mm")

    add_rotor_growler_test(add)
    add_winding_resistance(add)
    add_winding_inductance(add)
    add_ir_after_assembly(add)
    # Pump-family: only Full Load Current + Temp Rise, no No Load Current, no separate 3-lug check.
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
        "must_change_bearing_4306_6306", parent=must_change, field_label="Bearing 4306, 6306",
        field_type="select", options="Provided, Not Provided", required=True,
        standard_value="TOH/TOH item", authority_reference="Shed practice",
    )
    add(
        "must_change_rubber_o_ring", parent=must_change, field_label='To Replace Set of Rubber "O" Ring',
        field_type="select", options="Provided, Not Provided", required=True,
        standard_value="TOH, IOH item", authority_reference="As per RDSO TC-29",
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
        equipment_code="TFP Pump", template_code="9", technology="3_PHASE",
        template_name="Checksheet for TFP Pump",
        description="Transformer Oil Filtration Pump checksheet.",
        build_fn=build,
    )
