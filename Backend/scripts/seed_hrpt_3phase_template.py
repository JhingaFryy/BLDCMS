"""
Module 41 (Phase 2): seeds the HRPT (HR Pantograph, 3-Phase locomotives, M1-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_hrpt_3phase_template.py`

Source: "TOH & IOH For HRPT.pdf" - "Performa for TOH & IOH Maintenance Activities for HRPT",
covering pan-head/collector-head/arm-assembly inspection, must-change pneumatic components,
carbon strip measurement, ball bearing/rocker-box replacement, transverse rigidity, greasing
points, a height-stability test, a Pneumatic Control Unit section, and a Testing section (raising/
lowering time, PRV pressure, safety valve, ORD setting, leakage checks).

Four pantograph makes are covered by this single equipment/template (Schunk, FTRTIL LX3600,
FTRTIL LX3800, Mersen), each with its own numeric standard for Tilting angle, Raising/Lowering
Time, PRV pressure, Safety valve blow-off and ORD setting - since these are four genuinely
different tolerance bands (not one shared range), each such field is modelled as a "number" field
whose standard_value text lists all four makes' specs together (the header's own Make field
identifies which one governs), rather than either inventing a false unified numeric_range or
exploding into 4x near-duplicate fields per measurement.

Per the module's "Do NOT create fields for Loco Number/Technician/Supervisor Name/Signature" rule,
the sheet's own "Removed From/Provided In Loco No./Schedule & Date" lines are intentionally not
modelled.
"""
from _aux_template_helpers import add_final_remarks, run_seed

HEIGHTS_MM = [300, 1300, 2000, 3400]


def build(add):
    add("pt_sn", field_label="PT S.N.", field_type="text", required=True, standard_value="Noted")
    add("pt_make", field_label="Make", field_type="select",
        options="Schunk, FTRTIL LX3600, FTRTIL LX3800, Mersen", required=True)
    add("pt_type", field_label="Type", field_type="text", required=True, standard_value="Noted")
    add("pt_mfg_year", field_label="Mfg. Year", field_type="text", required=True, standard_value="Noted")

    checks = add("maintenance_checks", field_label="Maintenance Activities During Schedule", field_type="group",
                 required=False)
    add("collector_head_condition_check", parent=checks, field_label="Examine the Collector Head/Pan Head",
        field_type="select", options="OK, Defective/Damage", required=True,
        standard_value="Should Not Be Defective/Damage Then Replace", negative_values="Defective/Damage")
    add("suspension_plunger_rocker_box_check", parent=checks, field_label="Examine the Manually Suspension "
        "Mounted/Plunger/Spring Box Mounted/Rocker Box Assembly", field_type="select", options="Free, Not Free",
        required=True, standard_value="Should Be Free", negative_values="Not Free")
    add("aero_foil_horn_check", parent=checks, field_label="Examine the Aero Foil & Horn of Collector Head/Pan "
        "Head for Crack, Damage, Distortion or Breakage", field_type="select", options="Free, Not Free",
        required=True, standard_value="Should Be Free", negative_values="Not Free")
    add("shunt_strains_visual_inspection", parent=checks, field_label="Visual Inspection of Damages/Cutting of "
        "Shunt Strains", field_type="select", options="OK, Replaced/Adjusted", required=True,
        standard_value="Replace Shunt in Case More Than 5% of Wire Strains Were Broken, if Not Then Adjust With "
                        "Swaying Shaft")
    add("collector_head_horizontal_level_check", parent=checks, field_label="Examine the Horizontal Level of "
        "Collector Head/Pan Head With the Help of Spirit Level", field_type="select",
        options="Horizontal, Adjusted", required=True,
        standard_value="Should Be in Horizontal Position, if Not Then Adjust With Swaying Shaft")
    add("pn_tubes_replace", parent=checks, field_label="Replace All Pn. Tubes", field_type="select",
        options="Replaced, Not Replaced", required=True,
        standard_value="Must Change Item in TOH & IOH (Schunk, FTRTIL & Mersen)", negative_values="Not Replaced")
    add_membrane_group = add("add_membrane_kit_replace", parent=checks, field_label="Replace ADD Membrane/Kit "
        "(Bellow Pipe, ORD Pipe, ADD I/P Pipe, ADD O/P Pipe)", field_type="group", required=False,
        standard_value="Must Change Item in TOH & IOH (Schunk, FTRTIL & Mersen)")
    for key, label in (("bellow_pipe", "Bellow Pipe"), ("ord_pipe", "ORD Pipe"), ("add_ip_pipe", "ADD I/P Pipe"),
                       ("add_op_pipe", "ADD O/P Pipe")):
        add(f"add_membrane_{key}", parent=add_membrane_group, field_label=label, field_type="select",
            options="Replaced, Not Replaced", required=True, negative_values="Not Replaced")
    add("teflon_tube_insulating_hose_leakage_check", parent=checks, field_label="Check the Teflon Tube/Insulating "
        "Hose - if Leakage Then Replace", field_type="select", options="No Leakage, Replaced", required=True,
        standard_value="There Should Be No Leakage. Must Change Item in TOH & IOH (Schunk & Mersen)")
    add("air_bellow_drive_check", parent=checks, field_label="Examine the Air Bellow Drive - if Defective/Damage "
        "Then Replace", field_type="select", options="OK, Replaced", required=True,
        standard_value="Should Not Be Defective/Damage/Distortion")
    add("lower_rod_coupling_rod_check", parent=checks, field_label="Inspection of Lower Rod/Coupling Rod "
        "Assembly - if Found Defective/Damage/Bend Then Replace", field_type="select", options="OK, Replaced",
        required=True, standard_value="Should Not Be Defective/Damage/Distortion/Bend")
    add("upper_rod_parallel_guide_bar_check", parent=checks, field_label="Inspection of Upper Rod/Parallel Guide "
        "Bar/Steady Tube Assembly - if Found Defective/Damage/Bend Then Replace", field_type="select",
        options="OK, Replaced", required=True, standard_value="Should Not Be Defective/Damage/Distortion/Bend")
    add("base_frame_assembly_check", parent=checks, field_label="Inspection of Base Frame Assembly - if Found "
        "Defects/Damage/Bend Then Replace", field_type="select", options="OK, Replaced", required=True,
        standard_value="Should Not Be Defective/Damage/Distortion/Bend")
    add("lower_arm_assembly_check", parent=checks, field_label="Inspection of Lower Arm Assembly - if Found "
        "Defects/Damage/Bend Then Replace", field_type="select", options="OK, Replaced", required=True,
        standard_value="Should Not Be Defective/Damage/Distortion/Bend")
    add("upper_arm_assembly_check", parent=checks, field_label="Inspection of Upper Arm Assembly - if Found "
        "Defects/Damage/Bend Then Replace", field_type="select", options="OK, Replaced", required=True,
        standard_value="Should Not Be Defective/Damage/Distortion/Bend")
    add("base_frame_groove_mark_check", parent=checks, field_label="Inspection of Base Frame Assembly - if Found "
        "Defects/Damage/Bend/Groove Mark Then Replace", field_type="select", options="OK, Replaced", required=True,
        standard_value="Should Not Be Defective/Damage/Distortion/Bend")
    add("pan_head_tilting_check", parent=checks, field_label="Examine the Tilting of Pan Head", field_type="number",
        required=True, unit="degree",
        standard_value="Schunk: 6°-8°; FTRTIL LX3600: 5°-10°; FTRTIL LX3800: 5°-10°; Mersen: 6°-8°")
    add("collecting_head_assembly_check", parent=checks, field_label="Inspection of Collecting Head Assembly "
        "(Strips Support, Aero Foil Etc.) - if Found Defective/Damage/Bend/Groove Mark Then Replace",
        field_type="select", options="OK, Replaced", required=True,
        standard_value="Should Not Be Defective/Damage/Distortion/Bend")
    add("carbon_strip_thickness", parent=checks, field_label="Measure the Thickness of Carbon Strip. If Condemn "
        "Size Then Replace With New One in Pair", field_type="number", required=True, unit="mm",
        standard_value="New Size-39±1mm, Condemn Size-25+1mm With Support Frame (Mersen); New Size-21mm With "
                        "Support Frame, Condemn Size-37mm (Pantrac/Wabtec)")
    add("carbon_strip_crack_groove_check", parent=checks, field_label="Examine Crack, Groove Marks, Breakage on "
        "Carbon Strip", field_type="select", options="No Crack, Crack Found", required=True,
        standard_value="Crack, Groove Marks, Breakage Should Not Be on Carbon Strip", negative_values="Crack Found")
    add("transverse_rigidity", parent=checks, field_label="Transverse Rigidity (Lateral Deflexion at Max. "
        "Working Height & Lateral Force of 300 N)", field_type="numeric_range", required=True, unit="mm",
        min_value=0.0, max_value=30.0, decimal_precision=0,
        standard_value="On Applying the Weight of 30 Kg, Lateral Max 30mm (Schunk, FTRTIL & Mersen)")
    add("screws_nuts_fasteners_tightness", parent=checks, field_label="Ensure the Tightness of All "
        "Screws/Nuts/Fasteners Connection", field_type="select", options="Tight, Loose Found", required=True,
        standard_value="Should Not Be in Loose Condition", negative_values="Loose Found")
    add("cable_thread_fitting_replace", parent=checks, field_label="Replace the Cable With Thread Fitting",
        field_type="select", options="Replaced, Not Replaced", required=True,
        standard_value="Must Change Item in IOH (Schunk)", negative_values="Not Replaced")

    bearing_replace_group = add("ball_bearing_rocker_box_replace", parent=checks, field_label="Replace Ball "
        "Bearings & Rocker Box (Must Change Item in IOH - Schunk)", field_type="group", required=False)
    for key, label in (("base_bearing_floating", "Base Bearing Floating"), ("base_bearing_fix", "Base Bearing Fix"),
                       ("upper_bearing_floating", "Upper Bearing (Floating)"),
                       ("upper_bearing_fix", "Upper Bearing (Fix)"), ("coupling_rod", "Coupling Rod"),
                       ("rocker_box", "Rocker Box"), ("ord_valve", "ORD Valve (3/2 Push Pull Operated Valve)")):
        label_text = f"Replace Ball Bearings ({label})" if key not in ("rocker_box", "ord_valve") else f"Replace {label}"
        add(f"replace_{key}", parent=bearing_replace_group, field_label=label_text, field_type="select",
            options="Replaced, Not Replaced", required=True, negative_values="Not Replaced")

    greasing_group = add("greasing_points", field_label="Greasing (SKF Alphalub/LGEP2) - Must Be Done in TOH & "
        "IOH (FTRTIL & Mersen)", field_type="group", required=False)
    for key, label in (("knee_joint_lower_upper_arm", "Knee Joint of Lower Arm Assembly & Upper Arm Assembly"),
                       ("bearing_housing_lower_arm", "Bearing Housing Assembly of Lower Arm Assembly"),
                       ("bearing_eye_lr_lower_arm", "Bearing Eye Left & Right of Lower Arm Assembly"),
                       ("damper_assembly", "Damper Assembly"), ("spring_box_mounted", "Spring Box Mounted"),
                       ("cam_chain", "Cam Chain")):
        add(f"greasing_{key}", parent=greasing_group, field_label=label, field_type="select",
            options="Done, Not Done", required=True, negative_values="Not Done")

    height_group = add("height_stability_test", field_label="After Applying the Weight of 07 Kg, at Different "
        "Height - Pantograph Should Be Stable on All Heights", field_type="group", required=False)
    for h in HEIGHTS_MM:
        add(f"height_stability_{h}mm", parent=height_group, field_label=f"{h} mm", field_type="select",
            options="Stable, Not Stable", required=True, standard_value="Stable", negative_values="Not Stable")

    pcu_group = add("pneumatic_control_unit", field_label="Pneumatic Control Unit Details", field_type="group",
                     required=False)
    add("air_filter_insert_replace", parent=pcu_group, field_label="Replace Air Filter Insert in Air Filter",
        field_type="select", options="Replaced, Not Replaced", required=True,
        standard_value="Must Change Item in TOH & IOH (FTRTIL)", negative_values="Not Replaced")
    add("air_filter_replace", parent=pcu_group, field_label="Replace Air Filter", field_type="select",
        options="Replaced, Not Replaced", required=True, standard_value="Must Change Item in TOH & IOH (Schunk)",
        negative_values="Not Replaced")
    add("air_pressure_hose_d10_8_replace", parent=pcu_group, field_label="Replace Air Pressure Hose d10/8 for "
        "Schunk", field_type="select", options="Replaced, Not Replaced", required=True,
        standard_value="Must Change Item in TOH & IOH (Schunk)", negative_values="Not Replaced")
    add("air_pressure_hose_d6_4_replace", parent=pcu_group, field_label="Replace Air Pressure Hose d6/4 for "
        "Schunk", field_type="select", options="Replaced, Not Replaced", required=True,
        standard_value="Must Change Item in TOH & IOH (Schunk & Mersen)", negative_values="Not Replaced")
    add("throttle_valve_raising_replace", parent=pcu_group, field_label="Throttle Valve (Raising) for Schunk",
        field_type="select", options="Replaced, Not Replaced", required=True,
        standard_value="Must Change Item in TOH & IOH (Schunk & Mersen)", negative_values="Not Replaced")
    add("throttle_valve_lowering_replace", parent=pcu_group, field_label="Throttle Valve (Lowering) for Schunk",
        field_type="select", options="Replaced, Not Replaced", required=True,
        standard_value="Must Change Item in TOH & IOH (Schunk)", negative_values="Not Replaced")
    add("add_valve_spare_kit_replace", parent=pcu_group, field_label="Spare Kit for ADD Valve", field_type="select",
        options="Replaced, Not Replaced", required=True, standard_value="Must Change Item in TOH & IOH (Schunk)",
        negative_values="Not Replaced")
    add("prv_leakage_check", parent=pcu_group, field_label="Examine the PRV, if Leakage Occurs Then Replace the "
        "Kit", field_type="select", options="No Leakage, Replaced", required=True,
        standard_value="No Air Leakage. Must Change Item in IOH (FTRTIL)")
    add("hydraulic_dampers_leakage_check", parent=pcu_group, field_label="Visual Inspection of Hydraulic Dampers "
        "(Spring Box Mounted) for Any Leakages, Exchange if Necessary", field_type="select",
        options="OK, Exchanged", required=True,
        standard_value="Should Not Be in Loose Condition. Must Change Item in IOH (Schunk, FTRTIL & Mersen)")
    add("suspension_unit_replace", parent=pcu_group, field_label="Replace the Suspension Unit (Spring Box "
        "Mounted)", field_type="select", options="Replaced, Not Replaced", required=True,
        standard_value="Must Change Item in IOH (Schunk, FTRTIL & Mersen)", negative_values="Not Replaced")

    testing_group = add("testing", field_label="Testing of Pantograph", field_type="group", required=False)
    add("raising_time", parent=testing_group, field_label="Raising Time", field_type="number", required=True,
        unit="sec", standard_value="Schunk: ≤10 Sec; FTRTIL LX3600: 6-15 Sec; FTRTIL LX3800: Max 15 Sec; Mersen: "
                                    "6-15 Sec")
    add("lowering_time", parent=testing_group, field_label="Lowering Time", field_type="number", required=True,
        unit="sec", standard_value="Schunk: ≤10 Sec; FTRTIL LX3600: ≤15 Sec; FTRTIL LX3800: Max 20 Sec; Mersen: "
                                    "06-20 Sec")
    add("prv_pressure", parent=testing_group, field_label="PRV Pressure", field_type="number", required=True,
        unit="kg/cm2", standard_value="Schunk: 3.8-4.2; FTRTIL LX3600: 4.8-5.2; FTRTIL LX3800: 3.8-4.2; Mersen: "
                                       "5.4-5.8")
    add("safety_valve_blow_off", parent=testing_group, field_label="Safety Valve Blow Off At", field_type="number",
        required=True, unit="kg/cm2",
        standard_value="Schunk: 4.3-4.8; FTRTIL LX3600: 5.3-5.7; FTRTIL LX3800: 4.3-4.7; Mersen: 4.8-5.2")
    add("add_working_check", parent=testing_group, field_label="ADD Working", field_type="select",
        options="Working, Not Working", required=True, standard_value="Should Be in Working",
        negative_values="Not Working")
    add("ord_working_check", parent=testing_group, field_label="ORD Working", field_type="select",
        options="Working, Not Working", required=True, standard_value="Should Be in Working",
        negative_values="Not Working")
    add("ord_setting_at", parent=testing_group, field_label="ORD Setting At", field_type="number", required=True,
        unit="mm", standard_value="Schunk: 3680mm; FTRTIL LX3600: 3750mm; FTRTIL LX3800: 3750mm; Mersen: 3680mm")
    add("pcu_leakage_check", parent=testing_group, field_label="Any Leakage in PCU", field_type="select",
        options="No Leakage, Leakage Found", required=True, standard_value="Leakage Not Permissible",
        negative_values="Leakage Found")
    add("pantograph_leakage_check", parent=testing_group, field_label="Any Leakage in Pantograph",
        field_type="select", options="No Leakage, Leakage Found", required=True,
        standard_value="Leakage Not Permissible", negative_values="Leakage Found")
    add("final_stability_check", parent=testing_group, field_label="After Applying the Weight of 07 Kg, "
        "Pantograph Should Be Stable", field_type="select", options="Stable, Not Stable", required=True,
        standard_value="Pantograph Should Be Stable", negative_values="Not Stable")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="HRPT", template_code="126", technology="3_PHASE",
        template_name="Checksheet for HR Pantograph",
        description="TOH & IOH maintenance and testing checksheet for HRPT - 3-Phase - M1-HR section.",
        build_fn=build,
    )
