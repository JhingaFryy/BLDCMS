"""
Module 29.11: seeds the ARNO Converter checksheet template.

Run once: `venv/bin/python scripts/seed_arno_template.py`

The most structurally distinct sheet in the M35-Aux family (spans 2 physical pages in the source):
- Winding resistance/inductance use W.N/V.N/U.N phase labels instead of RY/YB/BR. Resistance
  keeps the usual percentage_difference validation; inductance has no numeric target on this sheet
  ("-") so validation is intentionally left off (validate=False), same generic group field type.
- Bearing/end-cover use TOP/BOTTOM labels instead of DE/NDE (still plain numeric_range leaves -
  no new field type).
- A block of unnumbered inspection rows between S.N.9 and S.N.10 in the source, and TWO separate
  Polarization Index fields (S.N. rows are genuinely distinct in the source, hence 2 distinct
  field_keys rather than reusing one).
- Run Test After Assembly at 200 Volt has asymmetric per-phase No Load Current ranges (U/V very
  different from W), modeled as 3 individual numeric_range leaves rather than the shared
  add_run_test_no_full_temp() helper (which assumes symmetric per-phase ranges).
- A supplementary "High Current Injection Test" section that is not part of the main numbered
  checking-point list. Modeled with existing field types only (group/select/number) - no new
  template engine capability was needed for it.
"""
from _aux_template_helpers import (
    run_seed, add_pre_test_vibration, add_ir_before_dismantle, add_cleaning_backing_varnishing,
    add_surge_comparison_test, add_thread_condition, add_rotor_growler_test, add_winding_resistance,
    add_winding_inductance, add_ir_after_assembly, add_bearing_condition_spm, add_work_done_lead_lug,
    add_polarization_index, add_final_remarks, add_bearing_group, add_transparent_sleeve,
)


def build(add):
    add_pre_test_vibration(add)
    add_ir_before_dismantle(add)
    add_cleaning_backing_varnishing(add)
    add_surge_comparison_test(add, standard="Wave form -OK")
    add_thread_condition(add)

    bearing = add(
        "bearing_seat_dia_rotor_shaft", field_label="Bearing Seat Dia. of Rotor Shaft (for 6316)",
        field_type="group", required=False, authority_reference="SMI-16",
    )
    add("bearing_seat_dia_top", parent=bearing, field_label="TOP", field_type="numeric_range", required=True, unit="mm",
        min_value=80.002, max_value=80.015, decimal_precision=3, standard_value="80.002 - 80.015 mm")
    add("bearing_seat_dia_bottom", parent=bearing, field_label="BOTTOM", field_type="numeric_range", required=True, unit="mm",
        min_value=80.002, max_value=80.015, decimal_precision=3, standard_value="80.002 - 80.015 mm")

    end_cover = add(
        "end_cover_bore_dia", field_label="End Cover Bore Dia.",
        field_type="group", required=False, authority_reference="SMI-16",
    )
    add("end_cover_bore_dia_top", parent=end_cover, field_label="TOP", field_type="numeric_range", required=True, unit="mm",
        min_value=169.993, max_value=170.018, decimal_precision=3, standard_value="169.993 - 170.018 mm")
    add("end_cover_bore_dia_bottom", parent=end_cover, field_label="BOTTOM", field_type="numeric_range", required=True, unit="mm",
        min_value=169.993, max_value=170.018, decimal_precision=3, standard_value="169.993 - 170.018 mm")

    add_winding_resistance(
        add, phases=("W.N", "V.N", "U.N"),
        standard="Difference not more than 10% (WN - 0.020, VN,UN - 0.0118 Ohm)",
    )
    add_winding_inductance(add, phases=("W.N", "V.N", "U.N"), standard="-", validate=False)

    # Unnumbered inspection rows between S.N.9 and S.N.10 in the source document.
    add(
        "rotor_bar_end_ring_brazing", field_label="Condition of Rotor Bar/End Ring Brazing",
        field_type="select", options="No Crack, Crack Found", required=True,
        standard_value="No crack", authority_reference="Shed practice",
        negative_values="Crack Found",
    )
    add(
        "araldite_work", field_label="Araldite Work",
        field_type="select", options="Normal, Abnormal", required=True,
        standard_value="Normal", authority_reference="Shed practice",
        negative_values="Abnormal",
    )
    add(
        "baking_of_rotors", field_label="Baking of Rotors",
        field_type="boolean", required=True,
        standard_value="Done", authority_reference="Shed practice",
        negative_values="false",
    )
    add(
        "graphite_grease_copper_stud", field_label="Graphite Grease on Copper Stud",
        field_type="boolean", required=True,
        standard_value="To apply", authority_reference="Shed practice",
        negative_values="false",
    )
    terminal_stud = add(
        "terminal_stud_clearance_nomex", field_label="Terminal Stud Clearance and Nomex Paper",
        field_type="group", required=False, authority_reference="Shed practice",
    )
    add("terminal_stud_clearance", parent=terminal_stud, field_label="Clearance", field_type="numeric_range",
        required=True, unit="mm", min_value=5.0, decimal_precision=1, standard_value="Min. 5mm")
    add("terminal_stud_nomex_paper", parent=terminal_stud, field_label="Nomex Paper Provided",
        field_type="boolean", required=True, standard_value="To provide", negative_values="false")
    add(
        "terminal_box_modify_3hole_cleat", field_label="Terminal Box Modify for 3-Hole Cleat",
        field_type="boolean", required=True,
        standard_value="To provide", authority_reference="Shed practice",
        negative_values="false",
    )
    add(
        "double_copper_patti_jbox", field_label="Double Copper Patti in J/Box",
        field_type="boolean", required=True,
        standard_value="To provide", authority_reference="Shed practice",
        negative_values="false",
    )
    add(
        "mpt_cooling_fan", field_label="MPT Test of Cooling Fan",
        field_type="select", options="No Crack, Crack Found", required=True,
        standard_value="No crack", authority_reference="Shed practice",
        negative_values="Crack Found",
    )

    add_rotor_growler_test(add)
    add_ir_after_assembly(add)
    add_polarization_index(
        add, field_key="polarization_index_before_run_test", label="P I Value After Assembly",
        standard="Between 1-4",
    )

    run_test = add(
        "run_test_after_assembly_200v", field_label="Run Test After Assembly at 200 Volt",
        field_type="group", required=False, authority_reference="Shed practice",
    )
    no_load_group = add("no_load_current", parent=run_test, field_label="No Load Current",
                         field_type="group", required=False, standard_value="As per data sheet")
    add("no_load_current_u", parent=no_load_group, field_label="U", field_type="numeric_range", required=True,
        unit="A", min_value=35.0, max_value=50.0, decimal_precision=1, standard_value="35 - 50 A")
    add("no_load_current_v", parent=no_load_group, field_label="V", field_type="numeric_range", required=True,
        unit="A", min_value=35.0, max_value=50.0, decimal_precision=1, standard_value="35 - 50 A")
    add("no_load_current_w", parent=no_load_group, field_label="W", field_type="numeric_range", required=True,
        unit="A", min_value=1.0, max_value=10.0, decimal_precision=1, standard_value="1 - 10 A")
    temp_group = add("temp_rise_on_motor", parent=run_test, field_label="Temp Rise on Motor",
                      field_type="group", required=False, standard_value="Ambient +25 C")
    for leaf_label in ["Body", "DE", "NDE", "Amb"]:
        add(f"temp_rise_{leaf_label.lower()}", parent=temp_group, field_label=leaf_label,
            field_type="number", required=True, unit="C")

    add_bearing_condition_spm(add)
    add_work_done_lead_lug(add)

    must_change = add("must_change_item", field_label="Must Change Item", field_type="group", required=False)
    add_bearing_group(add, must_change, "must_change_bearing_6316", "Bearing 6316 (PL No. 85.01.1915)",
                       "IOH item (4½ years)", "As per RDSO TC-29")
    add_transparent_sleeve(add, must_change)

    add_polarization_index(
        add, field_key="polarization_index_1000v", label="To Measure Polarization Index (PI) Value at 1000V",
        standard="Not less than 1 and more than 4",
    )

    # Supplementary section, not part of the main numbered checking-point list. Modeled with
    # existing group/select/number field types only - no new engine capability required.
    hci_test = add(
        "high_current_injection_test", field_label="High Current Injection Test of ARNO Lug/Stud",
        field_type="group", required=False,
    )
    add("hci_junction_box_type", parent=hci_test, field_label="Junction Box Type",
        field_type="select", options="Lug Type, Stud Type", required=True)
    add("hci_ambient_temperature", parent=hci_test, field_label="Ambient Temperature",
        field_type="number", required=True, unit="C")
    for item_no in (1, 2, 3):
        item_group = add(f"hci_item_{item_no}", parent=hci_test, field_label=f"Item {item_no}",
                          field_type="group", required=False)
        add(f"hci_item_{item_no}_temp_10min", parent=item_group, field_label="Temp (10 Min)",
            field_type="number", required=True, unit="C")
        add(f"hci_item_{item_no}_temp_diff", parent=item_group, field_label="Temp Diff",
            field_type="number", required=True, unit="C")
        add(f"hci_item_{item_no}_winding_temp", parent=item_group, field_label="Winding Temp",
            field_type="number", required=True, unit="C")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="ARNO", template_code="18", technology="CONVENTIONAL",
        template_name="Checksheet for ARNO Converter",
        description="ARNO Converter checksheet.",
        build_fn=build,
    )
