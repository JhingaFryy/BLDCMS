"""
Module 29.11: seeds the MRB (Machine Room Blower) checksheet template.

Run once: `venv/bin/python scripts/seed_mrb_template.py`

Distinctive: this motor is fitted with either of two bearing part numbers (6208, or 6308 for a
CGL-make motor) which happen to share identical dimensional tolerances on this document - modeled
as 4 leaf readings (6208 DE/NDE, 6308(CGL) DE/NDE) rather than assuming only one variant is ever
fitted. Otherwise matches TMB's full structure (casing crack + MPT separate, full 3-part Run Test,
2-item Must Change), plus the same standalone Earthing Shunt checkpoint TMB/OCB also carry.
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
        "bearing_seat_dia_rotor_shaft", field_label="Bearing Seat Dia. of Rotor Shaft (6208 / CGL Motor 6308)",
        field_type="group", required=False, authority_reference="SMI-16",
    )
    for key, label in [("6208_de", "6208 DE"), ("6208_nde", "6208 NDE"), ("6308_cgl_de", "6308 (CGL) DE"), ("6308_cgl_nde", "6308 (CGL) NDE")]:
        add(f"bearing_seat_dia_{key}", parent=bearing, field_label=label, field_type="numeric_range", required=False, unit="mm",
            min_value=40.002, max_value=40.013, decimal_precision=3, standard_value="40.002 - 40.013 mm")

    end_cover = add(
        "end_cover_bore_dia", field_label="End Cover Bore Dia. (6208 / CGL Motor 6308)",
        field_type="group", required=False, authority_reference="SMI-16",
    )
    add("end_cover_bore_dia_6208_de", parent=end_cover, field_label="6208 DE", field_type="numeric_range", required=False, unit="mm",
        min_value=79.994, max_value=80.016, decimal_precision=3, standard_value="79.994 - 80.016 mm")
    add("end_cover_bore_dia_6208_nde", parent=end_cover, field_label="6208 NDE", field_type="numeric_range", required=False, unit="mm",
        min_value=79.994, max_value=80.016, decimal_precision=3, standard_value="79.994 - 80.016 mm")
    add("end_cover_bore_dia_6308_cgl_de", parent=end_cover, field_label="6308 (CGL) DE", field_type="numeric_range", required=False, unit="mm",
        min_value=89.994, max_value=90.016, decimal_precision=3, standard_value="89.994 - 90.016 mm")
    add("end_cover_bore_dia_6308_cgl_nde", parent=end_cover, field_label="6308 (CGL) NDE", field_type="numeric_range", required=False, unit="mm",
        min_value=89.994, max_value=90.016, decimal_precision=3, standard_value="89.994 - 90.016 mm")

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
    add(
        "mpt_impeller", field_label="MPT of Impeller",
        field_type="select", options="No Crack, Crack Found", required=True,
        standard_value="No crack", authority_reference="Shed practice",
        negative_values="Crack Found",
    )

    must_change = add("must_change_item", field_label="Must Change Item", field_type="group", required=False)
    add_bearing_group(add, must_change, "must_change_bearing_6208_6308", "Bearing 6208 (PL No. 85981035) / 6308 (CGL Make)",
                       "AOH/IOH item as per TC.", "As per RDSO TC-29")
    add_transparent_sleeve(add, must_change)

    add_polarization_index(add)
    add(
        "earthing_shunt_motor_casing", field_label="Earthing Shunt Between Motor and Casing to be Ensured",
        field_type="boolean", required=True, negative_values="false",
    )
    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="MRB", template_code="7", technology="3_PHASE",
        template_name="Checksheet for MRB",
        description="Machine Room Blower checksheet.",
        build_fn=build,
    )
