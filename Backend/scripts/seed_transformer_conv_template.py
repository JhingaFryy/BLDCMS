"""
Module 34: seeds the Transformer (Conventional, M8-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_transformer_conv_template.py`

Source: PERFORMA OF CHECK POINTS OF TRANSFORMER DURING TOH/IOH (ELS/TRS/BL/M-8/08).
"""
from _aux_template_helpers import run_seed, add_final_remarks


def add_select(add, key, label, standard, options, negative, authority=None):
    positive = options[0]
    return add(
        key, field_label=label,
        field_type="select", options=", ".join(options), required=True,
        standard_value=standard or positive, authority_reference=authority,
        negative_values=negative,
    )


def build(add):
    add_select(add, "clean_transformer_bushing", "Clean the Transformer Bushing",
               "Cleaned", ["Cleaned", "Not Cleaned"], "Not Cleaned")
    add_select(add, "check_transformer_tank", "Check the Transformer Tank",
               "Good", ["Good", "Damaged"], "Damaged")
    add_select(add, "bushing_insulator", "Bushing Insulator",
               "Good", ["Good", "Damaged"], "Damaged")
    add_select(add, "bushing_stems", "Bushing Stems",
               "Good", ["Good", "Damaged"], "Damaged")
    add_select(add, "cover_bolts", "Cover Bolts",
               "Good", ["Good", "Damaged"], "Damaged")

    oil_leak = add("oil_leakage_check", field_label="Check Oil Leakage From",
                    field_type="group", required=False, standard_value="No leakage")
    add("oil_leakage_welded_joints", parent=oil_leak, field_label="Welded Joints",
        field_type="select", options="No Leakage, Leakage", required=True,
        standard_value="No leakage", negative_values="Leakage")
    add("oil_leakage_gasket_joints", parent=oil_leak, field_label="Gasket Joints",
        field_type="select", options="No Leakage, Leakage", required=True,
        standard_value="No leakage", negative_values="Leakage")
    add("oil_leakage_bushings", parent=oil_leak, field_label="Bushings",
        field_type="select", options="No Leakage, Leakage", required=True,
        standard_value="No leakage", negative_values="Leakage")

    add_select(add, "overheating_bushing_stems_palm_clamp", "Check Any Over Heating Bushing Stems, Palm Clamp",
               "Normal", ["Normal", "Abnormal"], "Abnormal")
    add_select(add, "oil_leakage_conservator_3way_cock", "Check Oil Leakage From Conservator 3 Way Cock",
               "No Leakage", ["No Leakage", "Leakage"], "Leakage")
    add_select(add, "oil_leakage_main_drain_plug", "Check Oil Leakage From Transformer Main Drain Plug",
               "No Leakage", ["No Leakage", "Leakage"], "Leakage")
    add_select(add, "oil_leakage_sampling_cock", "Check Oil Leakage From Transformer Sampling Cock",
               "No Leakage", ["No Leakage", "Leakage"], "Leakage")
    add_select(add, "tightness_bushing_a3_a4_a5_a6", "Check Tightness of Bushing a3, a4, a5, a6",
               "No Loose", ["No Loose", "Loose"], "Loose")
    add_select(add, "tightness_main_bushing_cable_head", "Check Tightness of Main Bushing or Cable Head Termination",
               "No Loose", ["No Loose", "Loose"], "Loose")
    add_select(add, "dga_oil_sample_collected", "Collect Oil Sample From Sampling Cock for DGA Checking",
               "Normal", ["Normal", "Abnormal"], "Abnormal", authority="SMI-138")

    add("oil_level_after_work", field_label="Check Oil Level After Completing Work",
        field_type="text", required=True,
        standard_value="15 C Min. (oil level line as per ambient temperature)",
        authority_reference="Shed practice")
    add("bdv_after_oil_filtration", field_label="Check BDV After Oil Filtration",
        field_type="numeric_range", required=True, unit="KV", min_value=55.0, decimal_precision=1,
        standard_value="55 KV Min.")

    # --- Check Point of CHT ---
    add_select(add, "cht_clean_gray_modules", "Clean Gray Modules With Dry Cloth",
               "Cleaned", ["Cleaned", "Not Cleaned"], "Not Cleaned", authority="SMI-317")
    add_select(add, "cht_earthing_roof_top_termination", "Check Proper Earthing of Roof Top Termination",
               "Intact", ["Intact", "Not Intact"], "Not Intact", authority="SMI-317")
    add_select(add, "cht_earthing_vertical_receptacle", "Check Proper Earthing of Vertical Receptacle Point",
               "Intact", ["Intact", "Not Intact"], "Not Intact", authority="SMI-317")
    add_select(add, "cht_silicon_grease_replaced", "Wipeout Old Silicon Grease of Vertical Receptacle and "
               "Bushing Converter and Apply New Grease",
               "Replaced", ["Replaced", "Not Replaced"], "Not Replaced", authority="SMI-317")
    add("cht_earthing_cable_route", field_label="Check the Route of Earthing Cable (Should Be Through TFILM)",
        field_type="text", required=True, standard_value="Through CT",
        authority_reference="RDSO MS 30")

    # --- Must Change Items ---
    add("must_change_washer_sampling_plug", field_label="Washer of Sampling Plug (TOH/IOH)",
        field_type="select", options="Changed, Not Changed", required=True,
        standard_value="Must change", authority_reference="Experience basis")
    add("must_change_silica_gel", field_label="Silica Gel (TOH/IOH)",
        field_type="select", options="Changed, Not Changed", required=True,
        standard_value="Must change", authority_reference="RDSO TC29 / PL No. 81034878")
    add("must_change_rubber_sealing_washer", field_label="Rubber Sealing Washer With Gasket of Bushing "
        "a3, a4, a5, a6 (IOH)",
        field_type="select", options="Changed, Not Changed", required=True,
        standard_value="Must change", authority_reference="RDSO TC29 / PL No. 25971402")

    # --- Replacement of Items on Condition Basis ---
    gasket = add("gasket_replacement_condition_basis", field_label="Gasket Replacement (Condition Basis)",
                 field_type="group", required=False, standard_value="Condition basis")
    for key, label in [
        ("gasket_a0_a1_bushing", "a0, a1 Bushing"),
        ("gasket_conservator_gauge_glass", "Conservator Gauge Glass"),
        ("gasket_conservator_3way_cock", "Conservator Three Way Cock"),
        ("gasket_mph_drain_cock", "MPH Drain Cock"),
        ("gasket_main_drain_cock", "Main Drain Cock"),
    ]:
        add(key, parent=gasket, field_label=label,
            field_type="select", options="Changed, Not Changed", required=True)

    # --- Measurement: IR value of all bushings with 2.5KV megger ---
    ir_group = add("ir_measurement_bushings", field_label="Measurement of IR Value of All Bushing "
                   "(2.5KV Megger)", field_type="group", required=False, standard_value="100 M-Ohm Min.")
    for key, label in [
        ("ir_a0_earth", "A0 - Earth"),
        ("ir_a3_earth", "a3 - Earth"),
        ("ir_a5_earth", "a5 - Earth"),
        ("ir_a0_lv_earth", "a0 - Earth"),
        ("ir_a0_a0lv", "A0 - a0"),
        ("ir_a3_a5", "a3 - a5"),
    ]:
        add(key, parent=ir_group, field_label=label, field_type="numeric_range", required=True,
            unit="MOhm", min_value=100.0, decimal_precision=1, standard_value="100 M-Ohm Min.")

    # --- Radiator ---
    add_select(add, "radiator_cleaned_water_jet", "Clean Radiator With Water Jet",
               "Cleaned", ["Cleaned", "Not Cleaned"], "Not Cleaned")
    add_select(add, "radiator_pressure_test", "Test Radiator at 3.5 kg/cm2 Pressure for 4 Hrs Through PHGR",
               "No Leakage", ["No Leakage", "Leakage"], "Leakage", authority="No oil leakage")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="Transformer Conv", template_code="22", technology="CONVENTIONAL",
        template_name="Checksheet for Transformer",
        description="Transformer (Conventional) checksheet - M8-HR section.",
        build_fn=build,
    )
