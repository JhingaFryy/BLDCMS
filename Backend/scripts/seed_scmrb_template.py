"""
Module 29.11: seeds the Sc. MRB (Scavenge Motor for MRB / "Machine room scavenge blower (SCMRB)")
checksheet template.

Run once: `venv/bin/python scripts/seed_scmrb_template.py`

Distinctive vs TMB: only "To check casing for any crack" - no separate MPT of Impeller row on
this sheet. Bearing 6205, smaller dimensions than the blower-family sheets.
"""
from _aux_template_helpers import (
    run_seed, add_pre_test_vibration, add_ir_before_dismantle, add_cleaning_backing_varnishing,
    add_surge_comparison_test, add_thread_condition, add_rotor_growler_test, add_winding_resistance,
    add_winding_inductance, add_ir_after_assembly, add_run_test_no_full_temp, add_bearing_condition_spm,
    add_lug_temp_group, add_work_done_lead_lug, add_bore_shaft_impeller, add_casing_crack_check,
    add_polarization_index, add_final_remarks, add_bearing_group, add_transparent_sleeve,
)


def build(add):
    add_pre_test_vibration(add)
    add_ir_before_dismantle(add)
    add_cleaning_backing_varnishing(add)
    add_surge_comparison_test(add, standard="Wave form -OK")
    add_thread_condition(add)

    bearing = add(
        "bearing_seat_dia_rotor_shaft", field_label="Bearing Seat Dia. of Rotor Shaft (for 6205)",
        field_type="group", required=False, authority_reference="SMI-16",
    )
    add("bearing_seat_dia_de", parent=bearing, field_label="DE", field_type="numeric_range", required=True, unit="mm",
        min_value=25.002, max_value=25.011, decimal_precision=3, standard_value="25.002 - 25.011 mm")
    add("bearing_seat_dia_nde", parent=bearing, field_label="NDE", field_type="numeric_range", required=True, unit="mm",
        min_value=25.002, max_value=25.011, decimal_precision=3, standard_value="25.002 - 25.011 mm")

    end_cover = add(
        "end_cover_bore_dia", field_label="End Cover Bore Dia.",
        field_type="group", required=False, authority_reference="SMI-16",
    )
    add("end_cover_bore_dia_de", parent=end_cover, field_label="DE", field_type="numeric_range", required=True, unit="mm",
        min_value=51.994, max_value=52.013, decimal_precision=3, standard_value="51.994 - 52.013 mm")
    add("end_cover_bore_dia_nde", parent=end_cover, field_label="NDE", field_type="numeric_range", required=True, unit="mm",
        min_value=51.994, max_value=52.013, decimal_precision=3, standard_value="51.994 - 52.013 mm")

    add_rotor_growler_test(add)
    add_winding_resistance(add)
    add_winding_inductance(add)
    add_ir_after_assembly(add)
    add_run_test_no_full_temp(add)
    add_bearing_condition_spm(add)
    add_lug_temp_group(add)
    add_work_done_lead_lug(add)
    add_bore_shaft_impeller(add)
    add_casing_crack_check(add)

    must_change = add("must_change_item", field_label="Must Change Item", field_type="group", required=False)
    add_bearing_group(add, must_change, "must_change_bearing_6205", "Bearing 6205 (PL No. 85011022)",
                       "AOH/IOH item as per TC.", "As per RDSO TC-29")
    add_transparent_sleeve(add, must_change)

    add_polarization_index(add)
    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="Sc. MRB", template_code="8", technology="3_PHASE",
        template_name="Checksheet for Sc. MRB",
        description="Scavenge Motor for MRB (Machine Room Scavenge Blower) checksheet.",
        build_fn=build,
    )
