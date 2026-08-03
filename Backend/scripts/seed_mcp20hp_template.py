"""
Module 29.11: seeds the MCP20HP (Main Compressor for Three Phase) checksheet template.

Run once: `venv/bin/python scripts/seed_mcp20hp_template.py`

Distinctive vs TMB: Run Test After Assembly has only No Load Current + Temp Rise (no Full Load
Current); rows 16-17 replace impeller/casing checks with cooling-fan-coupler bore/shaft checks
(no defined numeric standard in the source document, so left as plain unranged number fields);
Must Change Item has only 2 sub-items (Bearing 6312, transparent sleeve). Row 3 (Cleaning) has no
authority listed on this specific sheet.
"""
from _aux_template_helpers import (
    run_seed, add_pre_test_vibration, add_ir_before_dismantle, add_cleaning_backing_varnishing,
    add_surge_comparison_test, add_thread_condition, add_rotor_growler_test, add_winding_resistance,
    add_winding_inductance, add_ir_after_assembly, add_run_test_no_full_temp, add_bearing_condition_spm,
    add_lug_temp_group, add_work_done_lead_lug, add_polarization_index, add_final_remarks,
    add_bearing_group, add_transparent_sleeve,
)


def build(add):
    add_pre_test_vibration(add)
    add_ir_before_dismantle(add)
    add_cleaning_backing_varnishing(add, authority=None)
    add_surge_comparison_test(add)
    add_thread_condition(add)

    bearing = add(
        "bearing_dia_rotor_shaft", field_label="Bearing Dia. of Rotor Shaft (for 6312)",
        field_type="group", required=False, authority_reference="SMI-16",
    )
    add("bearing_dia_de", parent=bearing, field_label="DE", field_type="numeric_range", required=True, unit="mm",
        min_value=60.002, max_value=60.015, decimal_precision=3, standard_value="60.002 - 60.015 mm")
    add("bearing_dia_nde", parent=bearing, field_label="NDE", field_type="numeric_range", required=True, unit="mm",
        min_value=60.002, max_value=60.015, decimal_precision=3, standard_value="60.002 - 60.015 mm")

    end_cover = add(
        "end_cover_bore_dia", field_label="End Cover Bore Dia.",
        field_type="group", required=False, authority_reference="SMI-16",
    )
    add("end_cover_bore_dia_de", parent=end_cover, field_label="DE", field_type="numeric_range", required=True, unit="mm",
        min_value=129.993, max_value=130.018, decimal_precision=3, standard_value="129.993 - 130.018 mm")
    add("end_cover_bore_dia_nde", parent=end_cover, field_label="NDE", field_type="numeric_range", required=True, unit="mm",
        min_value=129.993, max_value=130.018, decimal_precision=3, standard_value="129.993 - 130.018 mm")

    add_rotor_growler_test(add)
    add_winding_resistance(add)
    add_winding_inductance(add)
    add_ir_after_assembly(add)
    # No Full Load Current on this sheet - just No Load Current + Temp Rise.
    add_run_test_no_full_temp(add, full_load=False)
    add_bearing_condition_spm(add)
    add_lug_temp_group(add)
    add_work_done_lead_lug(add)

    add(
        "cooling_fan_slack_crack_check", field_label="To Check Motor Cooling Fan for Slackness and Crack",
        field_type="select", options="No Slack and Crack, Slack or Crack Found", required=True,
        standard_value="No slack and crack", authority_reference="Shed practice",
        negative_values="Slack or Crack Found",
    )

    bore_coupler = add(
        "bore_dia_coupler", field_label="Bore Dia. of Coupler",
        field_type="group", required=False,
    )
    add("bore_dia_coupler_cooling_fan", parent=bore_coupler, field_label="Cooling Fan", field_type="number", required=False, unit="mm")
    add("bore_dia_coupler_coupler", parent=bore_coupler, field_label="Coupler", field_type="number", required=False, unit="mm")

    shaft_coupler = add(
        "shaft_dia_coupler", field_label="Shaft Dia. for Coupler",
        field_type="group", required=False,
    )
    add("shaft_dia_coupler_cooling_fan", parent=shaft_coupler, field_label="Cooling Fan", field_type="number", required=False, unit="mm")
    add("shaft_dia_coupler_coupler", parent=shaft_coupler, field_label="Coupler", field_type="number", required=False, unit="mm")

    must_change = add("must_change_item", field_label="Must Change Item", field_type="group", required=False)
    add_bearing_group(add, must_change, "must_change_bearing_6312", "Bearing 6312 (PL No. 85.01.9732)",
                       "IOH/TOH item (3 years)", "As per RDSO TC-29")
    add_transparent_sleeve(add, must_change)

    add_polarization_index(add)
    add_final_remarks(add, label="Remarks / Any Other New Material")


if __name__ == "__main__":
    run_seed(
        equipment_code="MCP20HP", template_code="5", technology="3_PHASE",
        template_name="Checksheet for MCP20HP",
        description="Main Compressor for Three Phase checksheet.",
        build_fn=build,
    )
