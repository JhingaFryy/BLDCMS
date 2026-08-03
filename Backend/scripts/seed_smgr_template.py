"""
Module 34: seeds the SMGR (Conventional, M8-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_smgr_template.py`

Source: PERFORMA OF CHECK POINTS OF SMGR DURING TOH/IOH (ELS/TRS/BL/M-8/01), plus the
"CAM SWITCHES PRESSURE SMGR" sheet bundled with it.
"""
from _aux_template_helpers import run_seed, add_final_remarks


def build(add):
    add("smgr_serial_no", field_label="SMGR No.", field_type="text", required=True)
    add("smgr_removed_from_loco_no", field_label="Removed From Loco No. (Previous Fitment)",
        field_type="text", required=False)

    # --- 1. Check the Following Points ---
    add("smgr_dismantled_cleaned_petrol", field_label="Dismantle SMGR & Cleaned Parts With Petrol",
        field_type="select", options="Cleaned, Not Cleaned", required=True,
        standard_value="Cleaned", negative_values="Not Cleaned")
    add("smgr_greasing_main_control_cylinder", field_label="During Assembly Greasing to Be Done "
        "Main Cylinder, Control Cylinder", field_type="text", required=True, standard_value="Bharat MP-2")
    add("smgr_gearing_lubrication_oil", field_label="Lubricate Gearing Arrangement With Oil",
        field_type="text", required=True, standard_value="BBC 909")
    add("smgr_control_lever_guide_pin_lubrication", field_label="Lubricate Control Lever Guide Pin With Oil",
        field_type="text", required=True, standard_value="Transformer oil")
    add("smgr_bevel_gear_teeth_damage", field_label="Check Any Damage Bevel Gear Teeth",
        field_type="select", options="No Damage, Damage", required=True,
        standard_value="No damage", negative_values="Damage")
    add("smgr_bevel_gear_play", field_label="Check Any Play in Bevel Gear",
        field_type="select", options="No Play, Play", required=True,
        standard_value="No play", negative_values="Play")
    add("smgr_fly_wheel_play", field_label="Check Any Play in Fly Wheel",
        field_type="select", options="No Play, Play", required=True,
        standard_value="No play", negative_values="Play")
    add("smgr_pipe_line_compress_condition", field_label="Check Pipe Line for Any Compress Condition",
        field_type="select", options="No Compress, Compress", required=True,
        standard_value="No compress", negative_values="Compress")
    add("smgr_rdpt_crankshaft_journal_pin", field_label="Check RDPT of Crank Shaft & Journal Pin",
        field_type="select", options="No Crack, Crack", required=True,
        standard_value="No crack", negative_values="Crack",
        authority_reference="HQ TC No. 93 dt. 29/09/2000 (IOH)")

    mom = add("smgr_mom", field_label="MOM", field_type="group", required=False)
    add("smgr_mom_cleaned_washed", parent=mom, field_label="Clean & Wash MOM",
        field_type="select", options="Cleaned, Not Cleaned", required=True,
        standard_value="Cleaned", negative_values="Not Cleaned")
    add("smgr_mom_universal_coupling_play", parent=mom, field_label="Check Any Play in Universal Coupling",
        field_type="select", options="No Play, Play", required=True,
        standard_value="No play", negative_values="Play")
    add("smgr_mom_shaft_key_loose", parent=mom, field_label="Check MOM Shaft Key Was for Any Loose",
        field_type="select", options="No Loose, Loose", required=True,
        standard_value="No loose", negative_values="Loose")
    add("smgr_mom_mounting_bolts", parent=mom, field_label="Check MOM Mounting 3 Nos. Bolts for Any "
        "Threads Worn Out", field_type="select", options="Good, Worn Out", required=True,
        standard_value="Good", negative_values="Worn Out")

    zsms = add("smgr_zsms_panel", field_label="ZSMS Panel", field_type="group", required=False)
    add("smgr_zsms_pipe_condition", parent=zsms, field_label="Condition of ZSMS Pipe",
        field_type="select", options="Good, Damaged", required=True,
        standard_value="Good", negative_values="Damaged")
    add("smgr_zsmc_pipe_condition", parent=zsms, field_label="Condition of ZSMC Pipe",
        field_type="select", options="Good, Damaged", required=True,
        standard_value="Good", negative_values="Damaged")
    add("smgr_prv_air_leakage", parent=zsms, field_label="Check Air Leakage From PRV or Any Coupling",
        field_type="select", options="No Leakage, Leakage", required=True,
        standard_value="No leakage", negative_values="Leakage")
    add("smgr_prv_pressure_drop", parent=zsms, field_label="Check Pressure Drop of PRV",
        field_type="numeric_range", required=True, unit="kg/cm2", max_value=0.5, decimal_precision=2,
        standard_value="0.5 kg/cm2 Max")
    add("smgr_ev_phgr_pickup", parent=zsms, field_label="Check Pick Up of EV PHGR at 110 DC",
        field_type="select", options="Pick Up, No Pick Up", required=True,
        standard_value="Pick up", negative_values="No Pick Up")

    # --- 2. Must Change Items ---
    must_change = add("smgr_must_change_items", field_label="Must Change Items", field_type="group",
                      required=False)
    for key, label, reference in [
        ("smgr_must_change_aoh_kit_1", "AOH Kit (TOH)", "RDSO TC 102 / PL No. 23970844"),
        ("smgr_must_change_aoh_kit_2", "AOH Kit (TOH)", "RDSO TC 102 / PL No. 25568255"),
        ("smgr_must_change_u_section_ring", "U Section Ring (TOH/IOH)", "RDSO TC 102 / PL No. 23569761"),
        ("smgr_must_change_ioh_kit_1", "IOH Kit (IOH)", "RDSO TC 102 / PL No. 23970819"),
        ("smgr_must_change_ioh_kit_2", "IOH Kit (IOH)", "RDSO TC 102 / PL No. 23560680"),
        ("smgr_must_change_prv_kit", "PRV Kit (TOH/IOH)", "RDSO TC 102 / PL No. 25569697"),
        ("smgr_must_change_mom_roll_pin", "MOM Roll Pin (IOH)", "RDSO TC 102 / Non stock"),
    ]:
        add(key, parent=must_change, field_label=label, field_type="select",
            options="Changed, Not Changed", required=True, authority_reference=reference)

    # --- 3. Replacement of Items on Condition Basis ---
    condition_basis = add("smgr_condition_basis_items", field_label="Replacement of Items on Condition Basis",
                          field_type="group", required=False, standard_value="Condition basis")
    for key, label in [
        ("smgr_valve_spring", "Valve Spring (MG 6/6A & MG 4/5A) (6 Nos.)"),
        ("smgr_guide_pin", "Guide Pin"),
        ("smgr_guide_pin_spring", "Guide Pin Spring"),
        ("smgr_notching_spring", "Notching Spring"),
        ("smgr_fly_wheel_key", "Fly Wheel Key"),
        ("smgr_bevel_gear_key", "Bevel Gear Key"),
        ("smgr_intermediate_gear_complete", "Intermediate Gear Complete"),
        ("smgr_notching_lever_bearing", "Notching Lever Bearing (2 Nos.)"),
        ("smgr_main_pipe_line", "Main Pipe Line"),
        ("smgr_bearing_liner", "Bearing Liner (8 Nos.)"),
        ("smgr_solenoid_push_rod", "Solenoid Push Rod"),
    ]:
        add(key, parent=condition_basis, field_label=label, field_type="select",
            options="Changed, Not Changed", required=True)

    # --- Measurements & Testing ---
    coil_resistance = add("smgr_coil_resistance", field_label="Resistance of Coil", field_type="group",
                          required=False, authority_reference="OEM manual")
    add("smgr_coil_resistance_ve1", parent=coil_resistance, field_label="VE1", field_type="numeric_range",
        required=True, unit="Ohm", min_value=768.6, max_value=939.4, decimal_precision=1,
        standard_value="854 Ohm +/- 10%")
    add("smgr_coil_resistance_ve2", parent=coil_resistance, field_label="VE2", field_type="numeric_range",
        required=True, unit="Ohm", min_value=313.2, max_value=382.8, decimal_precision=1,
        standard_value="348 Ohm +/- 10%")

    pickup_voltage = add("smgr_pickup_voltage", field_label="Pickup Voltage (at 3.5 kg/cm2)",
                        field_type="group", required=False, authority_reference="OEM manual")
    add("smgr_pickup_voltage_ve1", parent=pickup_voltage, field_label="VE1", field_type="numeric_range",
        required=True, unit="V", min_value=53.0, decimal_precision=1, standard_value="53 V Min.")
    add("smgr_pickup_voltage_ve2", parent=pickup_voltage, field_label="VE2", field_type="numeric_range",
        required=True, unit="V", min_value=53.0, decimal_precision=1, standard_value="53 V Min.")

    dropout_voltage = add("smgr_dropout_voltage", field_label="Dropout Voltage (at 3.5 kg/cm2)",
                          field_type="group", required=False, authority_reference="OEM manual")
    add("smgr_dropout_voltage_ve1", parent=dropout_voltage, field_label="VE1", field_type="numeric_range",
        required=True, unit="V", min_value=11.0, decimal_precision=1, standard_value="11 V Min.")
    add("smgr_dropout_voltage_ve2", parent=dropout_voltage, field_label="VE2", field_type="numeric_range",
        required=True, unit="V", min_value=11.0, decimal_precision=1, standard_value="11 V Min.")

    add("smgr_gap_guide_pin_intermediate_gear", field_label="Gap Between Control Lever Guide Pin & "
        "Guide Segment of Intermediate Gear", field_type="numeric_range", required=True, unit="mm",
        min_value=0.4, max_value=0.7, decimal_precision=2, standard_value="0.4 to 0.7mm",
        authority_reference="OEM manual")
    add("smgr_clearance_bolt_head_3way_valve", field_label="Clearance Between Head of Bolt & Sleeve "
        "of 3 Way Valve", field_type="numeric_range", required=True, unit="mm",
        min_value=0.4, max_value=0.7, decimal_precision=2, standard_value="0.4 to 0.7mm",
        authority_reference="OEM manual")
    add("smgr_clearance_solenoid_valve_push_rod", field_label="Clearance Between Solenoid Push Rod & "
        "Valve Push Rod", field_type="number", required=True, unit="mm",
        standard_value="0.5mm Std.", authority_reference="OEM manual")

    lead_angle = add("smgr_lead_angle_without_push_rod", field_label="Lead Angle Without Push Rod",
                     field_type="group", required=False, authority_reference="SMI-48")
    add("smgr_lead_angle_progression", parent=lead_angle, field_label="Progression", field_type="numeric_range",
        required=True, unit="deg", min_value=71.0, max_value=79.0, decimal_precision=1,
        standard_value="75 +/- 4 deg")
    add("smgr_lead_angle_regression", parent=lead_angle, field_label="Regression", field_type="numeric_range",
        required=True, unit="deg", min_value=71.0, max_value=79.0, decimal_precision=1,
        standard_value="75 +/- 4 deg")

    add("smgr_progression_time", field_label="Progression Time", field_type="numeric_range", required=True,
        unit="sec", min_value=9.0, max_value=13.0, decimal_precision=1, standard_value="9-13 sec",
        authority_reference="OEM manual")
    add("smgr_regression_time", field_label="Regression Time", field_type="numeric_range", required=True,
        unit="sec", min_value=9.0, max_value=13.0, decimal_precision=1, standard_value="9-13 sec",
        authority_reference="OEM manual")

    panel_testing = add("smgr_panel_mp_testing", field_label="Testing SMGR Through Panel & MP at "
        "3.5 kg/cm2 (3 Days MP Testing)", field_type="group", required=False)
    add("smgr_panel_air_leakage", parent=panel_testing, field_label="Air Leakage", field_type="select",
        options="No Leakage, Leakage", required=True, standard_value="No leakage", negative_values="Leakage")
    add("smgr_panel_sticking_up", parent=panel_testing, field_label="Sticking Up", field_type="select",
        options="No Sticking, Sticking", required=True, standard_value="No sticking", negative_values="Sticking")
    add("smgr_panel_fly_wheel_wobbling", parent=panel_testing, field_label="Wobbling of Fly Wheel",
        field_type="select", options="No Wobbling, Wobbling", required=True,
        standard_value="No wobbling", negative_values="Wobbling")

    # --- Cam Switches Pressure SMGR ---
    cam_pressure = add("smgr_cam_switches_pressure", field_label="Cam Switches Pressure",
                       field_type="group", required=False, standard_value="160-260 gm")
    pin_pairs = [
        "1-2", "3-4", "5-6", "7-8", "9-10", "11-12", "13-14", "15-16", "41-42", "43-44",
        "45-46", "47-48", "49-50", "51-52", "53-54", "55-56", "57-58", "59-60", "61-62",
        "63-64", "65-66", "67-68", "69-70", "71-72", "73-74", "75-76", "77-78", "79-80",
        "81-82", "83-84", "85-86", "87-88", "89-90", "91-92",
    ]
    for pair in pin_pairs:
        key = "smgr_cam_pressure_" + pair.replace("-", "_")
        add(key, parent=cam_pressure, field_label=f"Pins {pair}", field_type="numeric_range",
            required=False, unit="gm", min_value=160.0, max_value=260.0, decimal_precision=0,
            standard_value="160-260 gm")

    aux_cam = add("smgr_auxiliary_cam_switch", field_label="Auxiliary Cam Switch", field_type="group",
                  required=False)
    add("smgr_aux_cam_roller_worn_out", parent=aux_cam, field_label="Check Cam Switch Roller Worn Out",
        field_type="select", options="No Worn Out, Worn Out", required=True,
        standard_value="No worn out", negative_values="Worn Out")
    add("smgr_aux_cam_crack", parent=aux_cam, field_label="Check Any Crack in Cam Switch",
        field_type="select", options="No Crack, Crack", required=True,
        standard_value="No crack", negative_values="Crack")
    add("smgr_aux_cam_jam_roller", parent=aux_cam, field_label="Check Any Jam in Roller",
        field_type="select", options="No Jam, Jam", required=True,
        standard_value="No jam", negative_values="Jam")

    add("smgr_cam_sequence_check", field_label="Check Cam Sequences 1 by 1, 35 Aux. Switch Drum",
        field_type="select", options="Checked, Not Checked", required=True,
        standard_value="Checked", negative_values="Not Checked")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="SMGR", template_code="24", technology="CONVENTIONAL",
        template_name="Checksheet for SMGR",
        description="SMGR (Conventional) checksheet - M8-HR section.",
        build_fn=build,
    )
