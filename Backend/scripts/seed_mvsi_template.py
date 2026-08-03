"""
Module 29.11: seeds the MVSI (Motor Ventilation Silicon Rectifier / traction motor blower variant)
checksheet template.

Run once: `venv/bin/python scripts/seed_mvsi_template.py`

Conventional-technology blower motor. Bearing 6306, full 3-part Run Test. Adds a "standard link
patti" checkpoint and an impeller-crack check plus bore/shaft-of-impeller group not present on the
TMB/OCB family. Field structure is confirmed identical to MVSL (see seed_mvsl_template.py, which
reuses this module's build() directly).
"""
from _aux_template_helpers import (
    run_seed, add_pre_test_vibration, add_ir_before_dismantle, add_cleaning_backing_varnishing,
    add_surge_comparison_test, add_thread_condition, add_rotor_growler_test, add_winding_resistance,
    add_winding_inductance, add_ir_after_assembly, add_run_test_no_full_temp, add_bearing_condition_spm,
    add_lug_temp_group, add_work_done_lead_lug, add_bore_shaft_impeller, add_polarization_index,
    add_final_remarks, add_bearing_group, add_transparent_sleeve,
)


def build(add):
    add_pre_test_vibration(add)
    add_ir_before_dismantle(add)
    add_cleaning_backing_varnishing(add, authority=None)
    add_surge_comparison_test(add)
    add_thread_condition(add)

    bearing = add(
        "bearing_seat_dia_rotor_shaft", field_label="Bearing Seat Dia. of Rotor Shaft (for 6306)",
        field_type="group", required=False, authority_reference="SMI-16",
    )
    add("bearing_seat_dia_de", parent=bearing, field_label="DE", field_type="numeric_range", required=True, unit="mm",
        min_value=30.002, max_value=30.013, decimal_precision=3, standard_value="30.002 - 30.013 mm")
    add("bearing_seat_dia_nde", parent=bearing, field_label="NDE", field_type="numeric_range", required=True, unit="mm",
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
    add_run_test_no_full_temp(add)
    add_bearing_condition_spm(add)
    add_lug_temp_group(add)
    add_work_done_lead_lug(add, label="Any Work Done on Lead, Lug, Terminal Block, Nomex Paper to Provide")

    add(
        "standard_link_patti_jbox", field_label="Standard Link Patti to Provide in J/box of SHI Make",
        field_type="boolean", required=True,
        standard_value="To provide", authority_reference="Shed practice.",
        negative_values="false",
    )
    add(
        "impeller_check", field_label="To Check Impeller",
        field_type="select", options="No Crack, Crack Found", required=True,
        standard_value="No crack", authority_reference="Shed practice",
        negative_values="Crack Found",
    )
    add_bore_shaft_impeller(add)

    must_change = add("must_change_item", field_label="Must Change Item", field_type="group", required=False)
    add_bearing_group(add, must_change, "must_change_bearing_6306", "Bearing 6306 (PL No. 85.01.2038)",
                       "AOH item; IOH item as per TC", "As per RDSO TC-29")
    add_transparent_sleeve(add, must_change)

    add_polarization_index(add)
    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="MVSI", template_code="13", technology="CONVENTIONAL",
        template_name="Checksheet for MVSI",
        description="Motor Ventilation blower (MVSI) checksheet.",
        build_fn=build,
    )
