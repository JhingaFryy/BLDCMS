"""
Module 34: seeds the SL (Smoothing Reactor, Conventional, M8-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_sl_template.py`

Source: SL PERFORMA TOH/IOH, CHECK SHEET FOR WAP4 LOCO (ELS/TRS/BL/M8/12, Rev-1).
"""
from _aux_template_helpers import run_seed, add_final_remarks


def build(add):
    add("sl_serial_no", field_label="SL Sr. No.", field_type="text", required=True)
    add("sl_make_year", field_label="Make / Year", field_type="text", required=False)
    add("sl_type", field_label="Type", field_type="select", options="SL30, SL42", required=True)

    # --- 1. Check Points ---
    add("sl_removed_uncoupled_checked", field_label="SL Remove From Loco & Uncouple Both Trolley, "
        "SL Check Visually", field_type="select", options="Checked Normal, Abnormal", required=True,
        standard_value="Checked Normal", negative_values="Abnormal")
    add("sl_blown_cleaned_dry_air", field_label="Blow & Clean SL From Both Sides With Dry Air",
        field_type="select", options="Cleaned, Not Cleaned", required=True,
        standard_value="Cleaned", negative_values="Not Cleaned")
    add("sl_pressure_blocks_tightness", field_label="Check Tightness of Pressure Blocks",
        field_type="select", options="No Loose, Loose", required=True,
        standard_value="No loose", negative_values="Loose")
    add("sl_overheating_core", field_label="Check Any Overheating on Core",
        field_type="select", options="No Overheating, Overheating", required=True,
        standard_value="No overheating", negative_values="Overheating")
    add("sl_overheating_coil", field_label="Check Any Overheating on Coil",
        field_type="select", options="No Overheating, Overheating", required=True,
        standard_value="No overheating", negative_values="Overheating")
    add("sl_spacers_core_inner_coil", field_label="Check Spacers Between Insulated Core and Inner Coil Intact",
        field_type="select", options="Intact, Not Intact", required=True,
        standard_value="Intact", negative_values="Not Intact")
    add("sl_spacers_inner_outer_coil", field_label="Check Spacers Between Inner Coil and Outer Coil Intact",
        field_type="select", options="Intact, Not Intact", required=True,
        standard_value="Intact", negative_values="Not Intact")
    add("sl_core_supporting_stud_tightness", field_label="Check Tightness Core Supporting Stud",
        field_type="select", options="No Loose, Loose", required=True,
        standard_value="No loose", negative_values="Loose")
    add("sl_trolley_bolts_tightness", field_label="Check Tightness of Trolley Bolts After Fitting "
        "of SL Both Trolley", field_type="select", options="Trolley Fitted Properly, Not Properly",
        required=True, standard_value="Trolley Fitted Properly", negative_values="Not Properly")

    # --- 2. Measurements (Ref. SMI 240 Rev.1) ---
    add("sl_cleat_thickness_increase", field_label="Increase Thickness of Cleats From 18mm to 23mm",
        field_type="select", options="Already Exist, Done", required=True,
        standard_value="Already Exist / Done")
    add("sl_blind_hole_drilled", field_label="Existing Blind Hole Drilled Through 13mm Dia Holes "
        "in Both Cleats", field_type="select", options="Already Exist, Done", required=True,
        standard_value="Already Exist / Done")
    add("sl_cleats_cadmium_plated", field_label="Both Cleats Cadmium Plated",
        field_type="select", options="Already Exist, Plated", required=True,
        standard_value="Already Exist / Plated")
    add("sl_screws_replaced_cadmium_bolts", field_label="Replace Existing Screws by High Tensile "
        "Cadmium Plated M-12 Bolts and Nuts", field_type="select", options="Replaced, Not Replaced",
        required=True, standard_value="Replaced", negative_values="Not Replaced")
    add("sl_copper_bus_bar_replaced", field_label="Existing Copper Bus Bar Connecting Fixed Cleats "
        "to Winding Replaced by Brazing 50mm Wide Copper Bar", field_type="select",
        options="Already Exist, Replaced", required=True, standard_value="Already Exist / Replaced")
    add("sl_air_gap_inner_coil_core", field_label="Check Air Gap at Corners Between Inner Coil and Core",
        field_type="numeric_range", required=True, unit="mm", min_value=2.0, decimal_precision=2,
        standard_value="Min. 2mm")
    add("sl_varnish_anti_tracking", field_label="Use Two Coats of Anti-Tracking Varnish F93 on Coil",
        field_type="select", options="Varnishing Done, Not Done", required=True,
        standard_value="Varnishing done", negative_values="Not Done")
    add("sl_glass_epoxy_material_srbgf", field_label="Use of Glass Epoxy Material (SRBGF) for Insulating "
        "Boards, Support Blocks and Sleeves", field_type="select",
        options="Already Exist, Changed With SRBGF", required=True,
        standard_value="Already Exist / Cleat, Support board, blocks, Sleeve Changed with SRBGF")
    add("sl_cross_bar_stainless_steel", field_label="Change Material of Cross Bar Assembly and Stud "
        "From Mild Steel to Stainless Steel", field_type="select", options="Already Exist, Changed",
        required=True, standard_value="Already Exist / Changed")

    coil_measure = add("sl_coil_resistance_millivolt_drop", field_label="Measurement of Coil Resistance "
        "and Milli-Volt Drop (Inject 1350 Amp DC Current, Coil 1 & 2)", field_type="group", required=False,
        authority_reference="SMI 240 Rev.1")
    add("sl_r115_resistance", parent=coil_measure, field_label="R115 Resistance", field_type="numeric_range",
        required=True, unit="milli-Ohm", min_value=3.589, max_value=3.701, decimal_precision=3,
        standard_value="3.645 +/- 0.056 milli-Ohm")
    add("sl_millivolt_drop_corrected", parent=coil_measure, field_label="Milli-Volt Drop (Corrected at 115C)",
        field_type="numeric_range", required=True, unit="Volt", min_value=4.844, max_value=4.996,
        decimal_precision=3, standard_value="4.92 +/- 0.076 Volt")

    add("sl_steel_mesh_provision", field_label="Provision of One Additional Steel Mesh Over Fiber Cover",
        field_type="select", options="Provided, Not Provided", required=True,
        standard_value="Steel mesh provided", negative_values="Not Provided")

    # --- 3. Testing ---
    ir_group = add("sl_ir_value_test", field_label="Check IR Value From 2.5KV Megger",
                   field_type="group", required=False, standard_value="100 M-Ohm Min.")
    add("sl_ir_coil1_channel", parent=ir_group, field_label="Coil 1 & Channel", field_type="numeric_range",
        required=True, unit="MOhm", min_value=100.0, decimal_precision=1, standard_value="100 M-Ohm Min.")
    add("sl_ir_coil2_channel", parent=ir_group, field_label="Coil 2 & Channel", field_type="numeric_range",
        required=True, unit="MOhm", min_value=100.0, decimal_precision=1, standard_value="100 M-Ohm Min.")
    add("sl_ir_coil1_coil2", parent=ir_group, field_label="Coil 1 & 2", field_type="numeric_range",
        required=True, unit="MOhm", min_value=100.0, decimal_precision=1, standard_value="100 M-Ohm Min.")

    inductance_group = add("sl_inductance_lcr", field_label="Check Inductance by LCR Meter",
                           field_type="group", required=False, standard_value="3.35 +/- 0.3 mH")
    add("sl_inductance_coil1", parent=inductance_group, field_label="Coil 1", field_type="numeric_range",
        required=True, unit="mH", min_value=3.05, max_value=3.65, decimal_precision=2,
        standard_value="3.35 +/- 0.3 mH")
    add("sl_inductance_coil2", parent=inductance_group, field_label="Coil 2", field_type="numeric_range",
        required=True, unit="mH", min_value=3.05, max_value=3.65, decimal_precision=2,
        standard_value="3.35 +/- 0.3 mH")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="SL", template_code="23", technology="CONVENTIONAL",
        template_name="Checksheet for SL",
        description="SL (Smoothing Reactor, Conventional) checksheet - M8-HR section.",
        build_fn=build,
    )
