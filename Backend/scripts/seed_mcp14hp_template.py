"""
Module 29.11: seeds the MCP14HP (Motor Compressor 14 HP) checksheet template.

Run once: `venv/bin/python scripts/seed_mcp14hp_template.py`

Conventional-technology compressor motor. Bearing 6310, Run Test has only No Load Current +
Temp Rise (no Full Load Current row, no 3-lug check). Rows 16-18 are replaced with a cooling-fan
check and two Bore/Shaft-of-cooling-fan-and-coupler groups (Small/Big children) instead of the
blower family's bore/shaft-of-impeller pattern.
"""
from _aux_template_helpers import (
    run_seed, add_pre_test_vibration, add_ir_before_dismantle, add_cleaning_backing_varnishing,
    add_surge_comparison_test, add_thread_condition, add_rotor_growler_test, add_winding_resistance,
    add_winding_inductance, add_ir_after_assembly, add_run_test_no_full_temp, add_bearing_condition_spm,
    add_work_done_lead_lug, add_polarization_index, add_final_remarks, add_bearing_group,
    add_transparent_sleeve,
)


def build(add):
    add_pre_test_vibration(add)
    add_ir_before_dismantle(add)
    add_cleaning_backing_varnishing(add, authority=None)
    add_surge_comparison_test(add)
    add_thread_condition(add)

    bearing = add(
        "bearing_seat_dia_rotor_shaft", field_label="Bearing Seat Dia. of Rotor Shaft (for 6310)",
        field_type="group", required=False, authority_reference="SMI-16",
    )
    add("bearing_seat_dia_de", parent=bearing, field_label="DE", field_type="numeric_range", required=True, unit="mm",
        min_value=50.002, max_value=50.016, decimal_precision=3, standard_value="50.002 - 50.016 mm")
    add("bearing_seat_dia_nde", parent=bearing, field_label="NDE", field_type="numeric_range", required=True, unit="mm",
        min_value=50.002, max_value=50.016, decimal_precision=3, standard_value="50.002 - 50.016 mm")

    end_cover = add(
        "end_cover_bore_dia", field_label="End Cover Bore Dia.",
        field_type="group", required=False, authority_reference="SMI-16",
    )
    add("end_cover_bore_dia_de", parent=end_cover, field_label="DE", field_type="numeric_range", required=True, unit="mm",
        min_value=109.994, max_value=110.016, decimal_precision=3, standard_value="109.994 - 110.016 mm")
    add("end_cover_bore_dia_nde", parent=end_cover, field_label="NDE", field_type="numeric_range", required=True, unit="mm",
        min_value=109.994, max_value=110.016, decimal_precision=3, standard_value="109.994 - 110.016 mm")

    add_rotor_growler_test(add)
    add_winding_resistance(add)
    add_winding_inductance(add)
    add_ir_after_assembly(add)
    add_run_test_no_full_temp(add, full_load=False)
    add_bearing_condition_spm(add)
    add_work_done_lead_lug(add)

    add(
        "cooling_fan_check", field_label="To Check Cooling Fan",
        field_type="select", options="Good Condition, Damaged", required=True,
        standard_value="Good condition", authority_reference="Shed practice",
        negative_values="Damaged",
    )
    bore_fan = add(
        "bore_dia_cooling_fan_coupler", field_label="Bore Dia. of Cooling Fan and Coupler",
        field_type="group", required=False,
    )
    add("bore_dia_small", parent=bore_fan, field_label="Small", field_type="numeric_range", required=False, unit="mm",
        min_value=47.984, max_value=47.995, decimal_precision=3, standard_value="47.984 - 47.995 mm")
    add("bore_dia_big", parent=bore_fan, field_label="Big", field_type="numeric_range", required=False, unit="mm",
        min_value=47.984, max_value=47.995, decimal_precision=3, standard_value="47.984 - 47.995 mm")

    shaft_fan = add(
        "shaft_dia_cooling_fan_coupler", field_label="Shaft Dia. of Cooling Fan and Coupler",
        field_type="group", required=False,
    )
    add("shaft_dia_small", parent=shaft_fan, field_label="Small", field_type="numeric_range", required=False, unit="mm",
        min_value=48.002, max_value=48.018, decimal_precision=3, standard_value="48.002 - 48.018 mm")
    add("shaft_dia_big", parent=shaft_fan, field_label="Big", field_type="numeric_range", required=False, unit="mm",
        min_value=48.002, max_value=48.018, decimal_precision=3, standard_value="48.002 - 48.018 mm")

    must_change = add("must_change_item", field_label="Must Change Item", field_type="group", required=False)
    add_bearing_group(add, must_change, "must_change_bearing_6310", "Bearing 6310 (PL No. 85.01.1850)",
                       "IOH item (4½ years)", "As per RDSO TC-29")
    add_transparent_sleeve(add, must_change)

    add_polarization_index(add)
    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="MCP14HP", template_code="12", technology="CONVENTIONAL",
        template_name="Checksheet for MCP14HP",
        description="Motor Compressor 14 HP checksheet.",
        build_fn=build,
    )
