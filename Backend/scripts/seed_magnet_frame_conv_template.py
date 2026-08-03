"""
Module 43: seeds the Mag_Conv (Magnet Frame, Conventional locomotives, M35-TM section)
checksheet template.

Run once: `venv/bin/python scripts/seed_magnet_frame_conv_template.py`

Source: "FR/TM/AC/05 - Overhauling of Magnet Frame" (Locomotive Care Centre Ratlam, Western
Railway), a 23-item overhaul/dimensional checklist covering yoke cleaning, winding continuity,
DPT crack checks (4 locations), pole bore dia, 'A' dimension (3 locations), yoke length, stator
bore dia, high-current injection voltage-drop and brazed-joint temperature tests (a genuine
per-joint measurement grid - 6 MP + F-FF and 6 IP + A-AA points, preserved at full granularity),
insulation values, and HV leakage test.

No `maintenance_type` is set (stays NULL) - see seed_rocker_brush_holder_conv_template.py's
docstring for why this keeps the Android app's TM Number/GC-Overhaul UI from triggering for
Conventional equipment.
"""
from _aux_template_helpers import add_final_remarks, run_seed

MP_JOINTS = [f"MP{i}" for i in range(1, 7)] + ["F-FF"]
IP_JOINTS = [f"IP{i}" for i in range(1, 7)] + ["A-AA"]


def build(add):
    header_group = add("machine_details", field_label="Machine Details", field_type="group", required=False)
    add("machine_no", parent=header_group, field_label="Machine No", field_type="text", required=True,
        standard_value="Noted")
    add("make_year", parent=header_group, field_label="Make & Year", field_type="text", required=True,
        standard_value="Noted")
    add("armature_no", parent=header_group, field_label="Armature No", field_type="text", required=True,
        standard_value="Noted")
    add("shaft_no", parent=header_group, field_label="Shaft No", field_type="text", required=True,
        standard_value="Noted")
    add("shaft_modified_unmodified", parent=header_group, field_label="Shaft Modified/Unmodified",
        field_type="select", options="Modified, Unmodified", required=True)
    add("pinion_no_make_year", parent=header_group, field_label="Pinion No, Make & Year of Mfd.",
        field_type="text", required=True, standard_value="Noted")
    add("position", parent=header_group, field_label="Position", field_type="text", required=False,
        standard_value="Noted")
    add("date_provided_in_service", parent=header_group, field_label="Date Provided in Service", field_type="date",
        required=False)
    add("special_repair_toh_ioh", parent=header_group, field_label="Special Repair/TOH/IOH", field_type="text",
        required=True, standard_value="Noted")
    add("bearing_pe_make_country", parent=header_group, field_label="Bearings Make & Country - PE",
        field_type="text", required=True, standard_value="Noted")
    add("bearing_ce_make_country", parent=header_group, field_label="Bearings Make & Country - CE",
        field_type="text", required=True, standard_value="Noted")
    add("pe_old_bearing_history", parent=header_group, field_label="PE Old Bearing History", field_type="textarea",
        required=False)
    add("ce_old_bearing_history", parent=header_group, field_label="CE Old Bearing History", field_type="textarea",
        required=False)

    add("yoke_cleaning", field_label="Clean the Yoke Thoroughly, First by Compressed Air Then by Kerosene Jet "
        "and Again by Compressed Air", field_type="select", options="Done, Not Done", required=True,
        standard_value="Ensure Thorough Cleaning")

    continuity_group = add("winding_continuity_check", field_label="Check the Continuity of Windings",
        field_type="group", required=False, standard_value="Should Have Continuity")
    add("continuity_main_field_winding", parent=continuity_group, field_label="A. Main Field Winding",
        field_type="select", options="OK, No Continuity", required=True, negative_values="No Continuity")
    add("continuity_commutating_pole_winding", parent=continuity_group, field_label="B. Commutating Pole "
        "Winding", field_type="select", options="OK, No Continuity", required=True,
        negative_values="No Continuity")
    add("continuity_a_cable", parent=continuity_group, field_label="C. 'A' Cable", field_type="select",
        options="OK, No Continuity", required=True, negative_values="No Continuity")

    add("poles_windings_inspection", field_label="Inspect the Poles and Windings for Rubbing Marks, Insulation "
        "Damage, Overheating, Potting Crack Etc.", field_type="select", options="Good, Details of Attention Paid",
        required=True)
    add("lead_wire_terminal_lugs_check", field_label="Check the Lead Wire Terminal Lugs for Any Damage, "
        "Deformation, Crack, Etc.", field_type="select", options="Good, Details of Attention Paid", required=True)

    dpt_group = add("dpt_crack_check", field_label="Conduct DPT on Locations After Proper Cleaning of the "
        "Parts", field_type="group", required=False, standard_value="OK/Crack")
    for key, label in (("gear_case_lugs", "A. Gear Case Mounting Lugs Top and Bottom"),
                       ("tm_nose_stay", "B. TM Nose Stay Top and Bottom"), ("safety_lugs", "C. Safety Lugs"),
                       ("lifting_hooks", "D. Lifting Hooks")):
        add(f"dpt_{key}", parent=dpt_group, field_label=label, field_type="select", options="OK, Crack Found",
            required=True, negative_values="Crack Found")

    add("top_nose_welding_check", field_label="Ensure Adequate Welding of Top Nose on Magnet Frame as per CLW "
        "Drawing", field_type="select", options="Adequate, Not Adequate", required=True,
        authority_reference="CLW Drawing No. 10P-702-107 Alt 'Q'")
    add("pole_fixing_bolts_tightness_check", field_label="Ensure Proper Tightness of the Entire Pole Fixing "
        "Bolts", field_type="select", options="OK, Not OK", required=True)
    add("magnet_frame_baking", field_label="Baking the Magnet Frame for 5 Hours at 100°C", field_type="select",
        options="Done, Not Done", required=True)

    pole_bore_group = add("pole_bore_dia_check", field_label="Check the Pole Bore Dia. With 'Go and No Go "
        "Gauge'", field_type="group", required=False,
        authority_reference="Camtech Manual/2005/TM/(H1.20 Jan 2005) Pg No: 37")
    add("main_pole_bore_dia", parent=pole_bore_group, field_label="Main Pole (at Center)", field_type="numeric_range",
        required=True, unit="mm", min_value=512.5, max_value=512.9, decimal_precision=1)
    add("commutating_pole_bore_dia", parent=pole_bore_group, field_label="Commutating Pole (at Center)",
        field_type="numeric_range", required=True, unit="mm", min_value=519.8, max_value=520.2,
        decimal_precision=1)

    add("gear_case_lugs_bush_check", field_label="Ensure Good Condition of Bush on Gear Case Lugs and Replace "
        "if Necessary", field_type="select", options="Good, Replaced", required=True,
        authority_reference="RDSO/ELRS/MS/WAG5/237")

    a_dimension_group = add("a_dimension_measurement", field_label="Measure 'A' Dimension at Three Locations "
        "and Record (by Vernier)", field_type="group", required=False, standard_value="A:282+0.052mm +0.000mm",
        authority_reference="RDSO/ELRS/SMI/WAG5/207")
    for i in (1, 2, 3):
        add(f"a_dimension_location_{i}", parent=a_dimension_group, field_label=f"Location {i}",
            field_type="numeric_range", required=True, unit="mm", min_value=282.0, max_value=282.052,
            decimal_precision=3)

    add("yoke_length", field_label="Measure Yoke Length", field_type="numeric_range", required=True, unit="mm",
        min_value=1018.0, max_value=1018.5, decimal_precision=1, authority_reference="CLW Drawing No. 10P-702-107 "
        "Alt 'Q'")
    add("inspection_cover_clamping_check", field_label="Ensure Proper Clamping Arrangements and Airtight "
        "Fitment of Inspection Cover", field_type="select", options="Done, Not Done", required=True)
    add("terminal_fixing_insulators_check", field_label="Check the Condition and Tightness of the Terminal "
        "Fixing Insulators", field_type="select", options="Done, Not Done", required=True)
    add("threaded_bores_thread_clean", field_label="Clean the Threads of All Threaded Bores With Original "
        "Size Tap", field_type="select", options="Done, Not Done", required=True)

    stator_bore_group = add("stator_bore_dia", field_label="Stator Bore Dia", field_type="group", required=False)
    add("stator_bore_dia_pe", parent=stator_bore_group, field_label="PE", field_type="numeric_range", required=True,
        unit="mm", min_value=696.0, max_value=696.226, decimal_precision=3, standard_value="696+0.138mm+0.088mm")
    add("stator_bore_dia_ce", parent=stator_bore_group, field_label="CE", field_type="numeric_range", required=True,
        unit="mm", min_value=710.0, max_value=710.226, decimal_precision=3, standard_value="710+0.138+0.088mm")

    add("end_shield_rocker_ring_seating_check", field_label="Check the End Shield & Rocker Ring Seating Area "
        "and Remove Burr if Any", field_type="select", options="Done, Not Done", required=True)

    voltage_drop_group = add("high_current_voltage_drop", field_label="Connect the Yoke to High Current "
        "Injection Kit and Inject 500Amps - Measure the Voltage Drop Across MP and IP (by High Current Test "
        "Bench)", field_type="group", required=False, authority_reference="RDSO/ELRS/SMI/271")
    add("voltage_drop_mp", parent=voltage_drop_group, field_label="a) MP", field_type="numeric_range", required=True,
        unit="V", min_value=4.28, max_value=4.68, decimal_precision=2, standard_value="4.48±0.2V")
    add("voltage_drop_ip", parent=voltage_drop_group, field_label="b) IP", field_type="numeric_range", required=True,
        unit="V", min_value=3.80, max_value=4.20, decimal_precision=2, standard_value="4.00±0.2V")

    brazed_joint_group = add("brazed_joint_temperature_test", field_label="Inject 700 Amps for 30 Minutes and "
        "Measure the Temperature at the Brazed Joints (by High Current Test Bench)", field_type="group",
        required=False)
    mp_joints_group = add("mp_joints_temperature", parent=brazed_joint_group, field_label="a) MP Joints",
        field_type="group", required=False, standard_value="MP Below 100°C")
    for joint in MP_JOINTS:
        add(f"mp_joint_{joint.lower().replace('-', '_')}_temp", parent=mp_joints_group, field_label=joint,
            field_type="numeric_range", required=True, unit="°C", min_value=0.0, max_value=100.0,
            decimal_precision=1)
    ip_joints_group = add("ip_joints_temperature", parent=brazed_joint_group, field_label="b) IP Joints",
        field_type="group", required=False, standard_value="IP Below 100°C")
    for joint in IP_JOINTS:
        add(f"ip_joint_{joint.lower().replace('-', '_')}_temp", parent=ip_joints_group, field_label=joint,
            field_type="numeric_range", required=True, unit="°C", min_value=0.0, max_value=100.0,
            decimal_precision=1)

    add("insulation_varnish_applied", field_label="Apply Insulation Varnish and Let It Dry in Air for 2 Hrs",
        field_type="select", options="Done, Not Done", required=True)

    final_insulation_group = add("final_insulation_value_check", field_label="Allow the Yoke to Cool to Room "
        "Temperature and Check the Insulation Value", field_type="group", required=False,
        standard_value="Not Less Than 10MΩ", authority_reference="Camtech Manual/2005/TM/(H1.20 Jan 2005) Pg "
        "No:37")
    add("final_insulation_main_field_winding", parent=final_insulation_group, field_label="a) Main Field "
        "Winding", field_type="numeric_range", required=True, unit="MOhm", min_value=10.0, max_value=1000.0,
        decimal_precision=1)
    add("final_insulation_commutating_pole_winding", parent=final_insulation_group, field_label="b) "
        "Commutating Pole Winding", field_type="numeric_range", required=True, unit="MOhm", min_value=10.0,
        max_value=1000.0, decimal_precision=1)
    add("final_insulation_a_cable", parent=final_insulation_group, field_label="c) 'A' Cable",
        field_type="numeric_range", required=True, unit="MOhm", min_value=10.0, max_value=1000.0,
        decimal_precision=1)

    hv_test_group = add("hv_test", field_label="Conduct HV Test at 2.5KV for 1 Min (by HV Test Machine)",
        field_type="group", required=False, standard_value="Should Withstand Max. Leakage Current Permitted - "
        "20mA", authority_reference="Camtech Manual/2005/TM/(H1.20 Jan 2005) Pg No:37")
    add("hv_test_f_ff", parent=hv_test_group, field_label="A. F-FF", field_type="numeric_range", required=True,
        unit="mA", min_value=0.0, max_value=20.0, decimal_precision=1)
    add("hv_test_a_aa", parent=hv_test_group, field_label="B. A-AA", field_type="numeric_range", required=True,
        unit="mA", min_value=0.0, max_value=20.0, decimal_precision=1)

    add("rocker_ring_needle_bearings_regrease", field_label="Overhaul and Re-Grease the Rocker Ring Needle "
        "Bearings", field_type="select", options="Done, Not Done", required=True)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="Mag_Conv", template_code="142", technology="CONVENTIONAL",
        template_name="Checksheet for Magnet Frame",
        description="Overhauling of Magnet Frame checksheet - Conventional - M35-TM section.",
        build_fn=build,
    )
