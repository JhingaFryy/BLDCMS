"""
Module 41: seeds the PT_Conv (Pantograph, WAP-4/Conventional locomotives, M1-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_pantograph_conv_template.py`

Source: "TOH & IOH Conv. PT.pdf" - "Performa for TOH & IOH Maintenance Activities for
Conventional PT", covering Upper Articulation Assembly & Main Spring, Bow Assembly, Bearing
(cage & ball), Lubricant, LAB Test items, important modifications, copper shunt, mechanism
assembly (eyelet rod), nuts & bolts tightness, Transverse Rigidity/Swivel Angle/Static
Balancing/Raising & Lowering Time/Max Height testing, and a "Must Change Item of Pantograph"
parts log.

Two pantograph models are fitted across the fleet (AM-12 and IR03H) with genuinely different
standards for Transverse Rigidity (AM-12: max 36±5mm with 50kg at 1.5m; IR03H: max 30mm with 30kg
at 2.0m) and Swivel Angle (AM-12: 7°±1°; IR03H: 7.5°±1°), and different Pantograph Kit PL numbers
for TOH/IOH - both are modelled as separate optional fields (technician fills only the one that
matches the fitted pantograph), the same "reference sheet prints both standards, tech fills the
applicable one" pattern already used for WAP-4 templates (e.g. Lateral Clearance End/Middle Axle).
Static balancing, raising/lowering time and max height are explicitly marked "(for both)" on the
source sheet and use a single shared standard.

Per the module's "Do NOT create fields for Loco Number/Technician/Supervisor Name/Signature" rule,
the sheet's own "Removed From/Provided In Loco No. & Date", "O/H By & Date" and
"Staff/Supervisor Name/Signature" lines are intentionally not modelled.
"""
from _aux_template_helpers import add_final_remarks, run_seed


def build(add):
    add("pt_sn", field_label="PT S.N.", field_type="text", required=True, standard_value="Noted")
    add("pt_make", field_label="Make", field_type="select", options="AM-12, IR03H", required=True)
    add("pt_type", field_label="Type", field_type="text", required=True, standard_value="Noted")
    add("pt_mfg_year", field_label="Mfg. Year", field_type="text", required=True, standard_value="Noted")

    upper_art_group = add("upper_articulation_assembly", field_label="Upper Articulation Assembly & Main Spring",
                           field_type="group", required=False, authority_reference="CAMTECH/E/11-12/Panto AM-12/1.0")
    add("steady_tube_link_bend_crack_check", parent=upper_art_group, field_label="To Check Steady Tube and "
        "Steady Link Assly. For Bend & Crack", field_type="select", options="OK, Defective/Damage/Distortion/Bend",
        required=True, standard_value="Should Not Be Defective/Damage/Distortion/Bend", negative_values="Defective/Damage/Distortion/Bend")
    add("main_raising_spring_crack_check", parent=upper_art_group, field_label="To Check Main Raising Spring "
        "for Crack or Breakage", field_type="select", options="OK, Defective/Damage", required=True,
        standard_value="Should Not Be Defective/Damage", negative_values="Defective/Damage")
    add("top_mounting_part_ab_check", parent=upper_art_group, field_label="To Check Top Mounting Part A&B",
        field_type="select", options="OK, Defective/Damage", required=True,
        standard_value="Should Not Be Defective/Damage", negative_values="Defective/Damage")
    add("cylinder_support_crack_check", parent=upper_art_group, field_label="To Check Cylinder Support for "
        "Crack", field_type="select", options="OK, Defective/Damage", required=True,
        standard_value="Should Not Be Defective/Damage", negative_values="Defective/Damage")
    add("longitudinal_tube_bend_damage_check", parent=upper_art_group, field_label="To Check Longitudinal Tube "
        "Bend or Damage", field_type="select", options="OK, Defective/Damage/Bend", required=True,
        standard_value="Should Not Be Defective/Damage/Bend", negative_values="Defective/Damage/Bend")

    bow_group = add("bow_assembly", field_label="Bow Assembly", field_type="group", required=False)
    add("bow_groove_wear_edges_crack_bend_check", parent=bow_group, field_label="To Check for Groove, Worn, "
        "Sharp Edges, Cracks and Bend Etc.", field_type="select", options="Good Condition, Not Good",
        required=True, standard_value="Should Be in Good Condition", negative_values="Not Good")
    add("carbon_strip_fixing_bolt_torque_check", parent=bow_group, field_label="To Check Whether the Metalized "
        "Carbon Strip Fixing Bolt Are Loose", field_type="select", options="Checked, Loose Found", required=True,
        standard_value="2.5 Nm Torque by Torque Wrench", negative_values="Loose Found")
    add("carbon_strip_thickness", parent=bow_group, field_label="To Measure the Thickness of Metalized Carbon "
        "Strip", field_type="numeric_range", required=True, unit="mm", min_value=12.0, max_value=24.0,
        decimal_precision=1, standard_value="New Size-24mm, Condemn Size-12mm With Support Frame "
        "(Condemn Size-3.5mm Without Support Frame)")
    add("end_wearing_strip_groove_wear_damage_check", parent=bow_group, field_label="To Check End Wearing Strip "
        "for Groove, Wear and Damage", field_type="select", options="Good Condition, Not Good", required=True,
        standard_value="Should Be in Good Condition", negative_values="Not Good")
    add("welded_joints_steady_link_crack_check", parent=bow_group, field_label="Verify Welded Joints (Steady "
        "Link) for Cracks - if Require Reweld", field_type="select", options="No Crack, Crack Found",
        required=True, standard_value="No Crack", negative_values="Crack Found")

    bearing_group = add("bearing_cage_ball_check", field_label="Bearing - Check for Any Damage in Cage & Ball "
        "(for Both)", field_type="group", required=False)
    add("top_mounting_part_bearing_2204", parent=bearing_group, field_label="Top Mounting Part A/B (2204) - "
        "2 Nos (Only in IR03H)", field_type="select", options="Done, Not Done", required=False,
        standard_value="O/H (Must Change Item to Be Change)", negative_values="Not Done")
    add("push_rod_bearing_2204", parent=bearing_group, field_label="Push Rod (2204) - 2 Nos", field_type="select",
        options="OK, Defective/Damage", required=True, standard_value="Should Not Be Defective/Damage",
        negative_values="Defective/Damage")
    add("yoke_assembly_bearing_6302", parent=bearing_group, field_label="Yoke Assembly (6302)",
        field_type="select", options="OK, Defective/Damage", required=True,
        standard_value="Should Not Be Defective/Damage", negative_values="Defective/Damage")
    add("side_pedestal_bearing_lr", parent=bearing_group, field_label="Side Pedestal L/R (1305/0325) - 2 Nos",
        field_type="select", options="OK, Defective/Damage", required=True,
        standard_value="Should Not Be Defective/Damage", negative_values="Defective/Damage")
    add("middle_articulation_bearing_6205", parent=bearing_group, field_label="Middle Articulation (6205) - "
        "2 Nos", field_type="select", options="OK, Defective/Distortion", required=True,
        standard_value="Should Not Be Defective/Distortion", negative_values="Defective/Distortion")

    lubricant_group = add("lubricant", field_label="Lubricant (RDSO/SMI/198)", field_type="group", required=False)
    add("lubricant_ball_bearing_plunger_articulation", parent=lubricant_group, field_label="Lubricant to Be Used "
        "in Ball Bearing, Plunger Box, Articulation Pin Joint", field_type="select", options="Done, Not Done",
        required=True, standard_value="MP3 Greasing", negative_values="Not Done")
    add("lubricant_throttle_valve", parent=lubricant_group, field_label="Lubricant to Be Used in Throttle "
        "Valve", field_type="select", options="Done, Not Done", required=True, standard_value="Vaseline",
        negative_values="Not Done")

    lab_test_group = add("lab_test", field_label="LAB Test of Following Items (HQ TC-97)", field_type="group",
                          required=False)
    add("main_raising_spring_screw_assembly_crack_check", parent=lab_test_group, field_label="Main Raising "
        "Spring Screw Assembly", field_type="select", options="No Crack, Crack Found", required=True,
        standard_value="No Crack (Zyglow)", negative_values="Crack Found")
    add("eyelet_rod_eye_bolt_crack_check", parent=lab_test_group, field_label="Eye Bolt of Eyelet Rod",
        field_type="select", options="No Crack, Crack Found", required=True, standard_value="No Crack (Zyglow)",
        negative_values="Crack Found")
    add("anti_balancing_tube_pin_crack_check", parent=lab_test_group, field_label="Pin for Anti-Balancing Tube",
        field_type="select", options="No Crack, Crack Found", required=True, standard_value="No Crack (Zyglow)",
        negative_values="Crack Found")
    add("middle_articulation_crack_check", parent=lab_test_group, field_label="Middle Articulation",
        field_type="select", options="No Crack, Crack Found", required=True, standard_value="No Crack (RDPT)",
        negative_values="Crack Found")
    add("push_rod_bracket_crack_check", parent=lab_test_group, field_label="Push Rod Bracket (Local Practice as "
        "Failure Prone)", field_type="select", options="No Crack, Crack Found", required=True,
        standard_value="No Crack (RDPT)", negative_values="Crack Found")

    modification_group = add("important_modification_check", field_label="To Check Important Modification",
                              field_type="group", required=False)
    add("longitudinal_tube_rubber_bush_check", parent=modification_group, field_label="Rubber Bush at the Top "
        "Open End of Longitudinal Tube", field_type="select", options="Good, Not Good", required=True,
        standard_value="Good", negative_values="Not Good")
    add("rubber_stopper_ms_bracket_check", parent=modification_group, field_label="Rubber Stopper and MS "
        "Bracket on Lower Articulation to Restrict 2 Meter Height (HQ TC-97)", field_type="select",
        options="Intact, Not Intact", required=True, standard_value="Intact", negative_values="Not Intact")

    add("copper_shunt_condition_check", field_label="Check Copper Shunt", field_type="select",
        options="Good Condition, Not Good", required=True, standard_value="Good Condition",
        negative_values="Not Good")

    mechanism_group = add("mechanism_assembly_check", field_label="Check Points for Mechanism Assly. (Eyelet "
        "Rod)", field_type="group", required=False)
    add("insulator_petticoat_check", parent=mechanism_group, field_label="Petticoat of Insulator",
        field_type="select", options="Healthy, Not Healthy", required=True, standard_value="Healthy",
        negative_values="Not Healthy")
    add("slotted_bar_check", parent=mechanism_group, field_label="Slotted Bar", field_type="select",
        options="Good, Not Good", required=True, standard_value="Good", negative_values="Not Good")
    add("eye_bolt_check", parent=mechanism_group, field_label="Eye Bolt", field_type="select",
        options="Good, Not Good", required=True, standard_value="Good", negative_values="Not Good")
    add("chain_clamp_anti_balancing_tube_check", parent=mechanism_group, field_label="Chain & Clamp With "
        "Anti-Balancing Tube", field_type="select", options="Intact, Not Intact", required=True,
        standard_value="Intact", negative_values="Not Intact")
    add("additional_spring_catcher_check", parent=mechanism_group, field_label="Additional Spring Catcher "
        "(RDSO MS-389)", field_type="select", options="Provided/Intact, Not Provided/Not Intact", required=True,
        standard_value="Provided/Intact", negative_values="Not Provided/Not Intact")
    add("spring_catcher_top_bottom_check", parent=mechanism_group, field_label="Spring Catcher Top & Bottom",
        field_type="select", options="Intact, Not Intact", required=True, standard_value="Intact",
        negative_values="Not Intact")

    add("nuts_bolts_tightness", field_label="Ensure the All Nuts & Bolts in Tight Position", field_type="select",
        options="Tight, Not Tight", required=True, standard_value="Should Be Tight", negative_values="Not Tight")

    testing_group = add("testing", field_label="Testing", field_type="group", required=False)
    tr_group = add("transverse_rigidity", parent=testing_group, field_label="Transverse Rigidity (as per "
        "Camtech Manual)", field_type="group", required=False)
    add("transverse_rigidity_am12", parent=tr_group, field_label="For AM 12 - Transverse Rigidity With 50 Kg "
        "Weight AT 1.5 M & Displacement to Be Measure (HQ TC-97)", field_type="numeric_range", required=False,
        unit="mm", min_value=31.0, max_value=41.0, decimal_precision=0, standard_value="Max 36±5mm on Each Side")
    add("transverse_rigidity_ir03h", parent=tr_group, field_label="For IR03H - Transverse Rigidity With 30 Kg "
        "Weight AT 2.0 M & Displacement to Be Measure (SMI-292)", field_type="numeric_range", required=False,
        unit="mm", min_value=0.0, max_value=30.0, decimal_precision=0, standard_value="Max 30mm on Each Side")
    add("swivel_angle_am12", parent=testing_group, field_label="Swivel Angle - AM 12 (RDSO/SMI 192)",
        field_type="numeric_range", required=False, unit="degree", min_value=6.0, max_value=8.0,
        decimal_precision=1, standard_value="7°±1°")
    add("swivel_angle_ir03h", parent=testing_group, field_label="Swivel Angle - IR03H (RDSO/SMI 192)",
        field_type="numeric_range", required=False, unit="degree", min_value=6.5, max_value=8.5,
        decimal_precision=1, standard_value="7.5°±1°")
    add("static_balancing", parent=testing_group, field_label="Static Balancing With Weight of 7 Kg at the "
        "Height of 500mm, 1000mm, 1500mm, 1750mm (RDSO SMI 64)", field_type="numeric_range", required=True,
        unit="Kg", min_value=15.0, max_value=25.0, decimal_precision=0, standard_value="Minimum 15 Kg")
    add("raising_time", parent=testing_group, field_label="Raising Time (RDSO SMI 75)", field_type="numeric_range",
        required=True, unit="sec", min_value=6.0, max_value=10.0, decimal_precision=0,
        standard_value="6-10 Sec (for Both)")
    add("lowering_time", parent=testing_group, field_label="Lowering Time (RDSO SMI 75)", field_type="number",
        required=True, unit="sec", standard_value="10 Sec (Max) (for Both)")
    add("max_height_pantograph", parent=testing_group, field_label="Max. Height of Pantograph (RDSO MS 150)",
        field_type="number", required=True, unit="mm", standard_value="2000mm Max")

    must_change_group = add("must_change_item", field_label="Must Change Item of Pantograph (Ref. RDSO TC 94)",
                             field_type="group", required=False)
    add("plunger_deflection_10kg", parent=must_change_group, field_label="Plunger Deflection While Putting 10 "
        "Kg Weight (HQ TC-296 and Audit Report EL/TAR/0006/2016)", field_type="number", required=True, unit="mm",
        standard_value="25mm (Max)")
    am12_kit_group = add("pantograph_kit_am12", parent=must_change_group, field_label="For AM 12", field_type="group",
                          required=False)
    add("toh_kit_am12", parent=am12_kit_group, field_label="TOH Kit of Pantograph (35 Nos)", field_type="select",
        options="Provided, Not Provided/N.A.", required=False, standard_value="PL No. 25888250")
    add("ioh_kit_am12", parent=am12_kit_group, field_label="IOH Kit of Pantograph (126 Nos)", field_type="select",
        options="Provided, Not Provided/N.A.", required=False, standard_value="PL No. 25888262")
    ir03h_kit_group = add("pantograph_kit_ir03h", parent=must_change_group, field_label="For IR03H",
                           field_type="group", required=False)
    add("toh_kit_ir03h", parent=ir03h_kit_group, field_label="TOH Kit of Pantograph (41 Nos)", field_type="select",
        options="Provided, Not Provided/N.A.", required=False, standard_value="PL No. 29810061")
    add("ioh_kit_ir03h", parent=ir03h_kit_group, field_label="IOH Kit of Pantograph (126 Nos)", field_type="select",
        options="Provided, Not Provided/N.A.", required=False, standard_value="PL No. 29880075")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="PT_Conv", template_code="125", technology="CONVENTIONAL",
        template_name="Checksheet for Pantograph",
        description="TOH & IOH maintenance and testing checksheet for Pantograph - Conventional - M1-HR section.",
        build_fn=build,
    )
