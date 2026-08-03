"""
Module 42: seeds the AC / AC_Conv (Cab AC, 3-Phase and Conventional locomotives, M35-CP section)
checksheet templates.

Run once: `venv/bin/python scripts/seed_cab_ac_template.py`

Source: "TOH & IOH CAB AC.pdf" - "AMC of Cab AC" (Ref: RDSO/2016/EL/SMI 0293 Rev.'4' dtd.
25/02/2021), covering Minor schedule activities (sections 3.1-3.11: General, Control Panel,
Condenser/Blower Motor, Compressor, Heater, Trough, OHP/HP/LP, TDR, MCBs/MPCB, Contactors,
Connector) and Major schedule activities (sections 4.1-4.8: all minor items plus overhaul-level
motor/valve/fin tests), followed by a "Items Changed on Conditional Basis" parts log.

Per the module's explicit instruction, the checksheet format is IDENTICAL for Conventional and
3-Phase locomotives - a single shared `build()` function is used for both AC and AC_Conv (and
CP/CP_Conv in the companion script), with only the equipment_code/template_code/technology
differing per `run_seed()` call. Every checking point is recorded once per cab (CAB-1/CAB-2 columns
on the source sheet), so each check is modelled as a group with a Cab-1/Cab-2 sub-field pair via
`_add_cab_pair`.

Per the module's "Do NOT create fields for Loco Number/Technician/Supervisor Name/Signature" rule,
the sheet's own "Loco No.", "Name of Tech"/signature lines are intentionally not modelled.
"""
from _aux_template_helpers import add_final_remarks, run_seed


def _add_cab_pair(add, parent, key, label, field_type="select", **kwargs):
    group = add(key, parent=parent, field_label=label, field_type="group", required=False,
                standard_value=kwargs.pop("standard_value", None),
                authority_reference=kwargs.pop("authority_reference", None))
    for cab_key, cab_label in (("cab1", "CAB-1"), ("cab2", "CAB-2")):
        add(f"{key}_{cab_key}", parent=group, field_label=cab_label, field_type=field_type, required=True,
            **kwargs)
    return group


def build(add):
    minor_group = add("minor_schedule", field_label="Maintenance Activities During Minor Schedules "
                       "(RDSO/2016/EL/SMI 0293 Rev.'4' dtd. 25/02/2021)", field_type="group", required=False)

    general_group = add("general", parent=minor_group, field_label="3.1 General", field_type="group",
                         required=False)
    _add_cab_pair(add, general_group, "logbook_defects_check", "Check the Loco Logbook and Attend the Defects "
                  "Recorded", options="OK, Defects Found", standard_value="Checked, Defects Attended")
    _add_cab_pair(add, general_group, "ac_unit_all_modes_check", "Run the AC Unit in (Off, Auto, Manual Cooling) "
                  "All Modes - Attend to Any Abnormalities Observed", options="No Abnormality, Abnormality Found")
    _add_cab_pair(add, general_group, "control_panel_dust_clean", "Clean Dust From Control Panel by Compressed "
                  "Air or Vacuum Cleaner and Tighten the Cable Terminals", options="Done, Not Done",
                  standard_value="Cleaned & Tightened")
    _add_cab_pair(add, general_group, "return_air_filters_clean", "Remove Return Air Filters by Opening the "
                  "Grill - Clean These Filters With Water/Vacuum Cleaner or Compressed Air",
                  options="Done, Not Done", standard_value="Cleaned")
    _add_cab_pair(add, general_group, "damaged_jointed_cable_check", "Check for Damaged/Jointed Cable",
                  options="No Damage/Joint, Damage/Joint Found")
    _add_cab_pair(add, general_group, "top_cover_locking_gasket_check", "Ensure Top Cover of AC Unit Proper "
                  "Locking and Gasket - Replace Gasket if Damaged", options="OK, Replaced")

    current_group = add("equipment_current_draw", parent=general_group, field_label="Run the AC Unit for Half "
        "an Hour and Record the Current Drawn by Various Equipments With the Help of Clamp Tester",
        field_type="group", required=False)
    _add_cab_pair(add, current_group, "ac_unit_cooling_mode_current", "AC Unit in Cooling Mode Current",
                  field_type="numeric_range", unit="Amp", min_value=4.5, max_value=6.0, decimal_precision=1)
    _add_cab_pair(add, current_group, "ac_unit_heating_mode_current", "AC Unit in Heating Mode Current",
                  field_type="numeric_range", unit="Amp", min_value=2.0, max_value=3.0, decimal_precision=1)
    _add_cab_pair(add, current_group, "compressor_motor_current", "Compressor Motor Current",
                  field_type="numeric_range", unit="Amp", min_value=2.0, max_value=4.0, decimal_precision=1)
    _add_cab_pair(add, current_group, "condenser_motor_current", "Condenser Motor Current",
                  field_type="numeric_range", unit="Amp", min_value=0.6, max_value=0.8, decimal_precision=1)
    _add_cab_pair(add, current_group, "blower_motor_current", "Blower Motor Current",
                  field_type="numeric_range", unit="Amp", min_value=0.4, max_value=0.6, decimal_precision=1)

    _add_cab_pair(add, general_group, "compressor_start_time_delay_check", "Switch 'ON' the AC Unit (Blower "
        "Motor ON, Condenser Motor ON, Compressor ON) and Rotary Switch Set the Manual Cooling Mode Then Check "
        "the Time Delay Relay for Its Operation", options="OK, Not OK",
        standard_value="Compressor Must Start Within 180±15 Sec")

    thermostat_group = add("thermostat_check", parent=general_group, field_label="Run the AC Unit in Auto Mode "
        "and Check the Cut-In and Cut-Out of Thermostat", field_type="group", required=False)
    _add_cab_pair(add, thermostat_group, "thermostat_cutin_cutout_check", "Cut-In/Cut-Out of Thermostat",
                  options="OK, Not OK")
    _add_cab_pair(add, thermostat_group, "sensor_probe_clean", "Clean the Cooling Sensor Probe and Heater "
                  "Sensor Probe (if Thermostat Not Working Properly)", options="Done, Not Applicable")
    _add_cab_pair(add, thermostat_group, "thermostat_connector_tightened", "Ensure Thermostat Connector Is "
                  "Properly Tightened", options="Done, Not Applicable")

    _add_cab_pair(add, general_group, "condensate_water_leakage_check", "Ensure That There Is No Leakage of "
        "Condensate Water From Trough to Driver Cab - Rectify Any Leakage", options="No Leakage, Leakage Found")

    control_panel_group = add("control_panel", parent=minor_group, field_label="3.2 Control Panel",
                               field_type="group", required=False)
    _add_cab_pair(add, control_panel_group, "control_panel_connectors_intactness_check", "Check Intactness of "
        "Control Panel Connectors", options="Intact, Not Intact")
    _add_cab_pair(add, control_panel_group, "rotary_switch_working_check", "Check Working of Rotary Switch by "
        "Rotating Forward and Backward - Replace if Found Loose, Damaged and Jammed", options="OK, Replaced")
    _add_cab_pair(add, control_panel_group, "led_manual_mode_check", "Check LED Indications - Manual Cooling "
        "Mode Position (Main-ON, BLR-ON, COMP-ON, COOL-ON)", options="OK, Not OK")
    _add_cab_pair(add, control_panel_group, "led_auto_mode_check", "Check LED Indications - Auto Mode Position "
        "(Summer: Main-ON, BLR-ON, COMP-ON, COOL-ON; Winter: Main-ON, BLR-ON, HTR-ON)", options="OK, Not OK")
    _add_cab_pair(add, control_panel_group, "step_down_transformer_clean", "Check and Clean Step-Down "
        "Transformer (Control Transformer and Its Connections)", options="Done, Not Done")

    condenser_blower_group = add("condenser_blower_motor", parent=minor_group, field_label="3.3 Condenser Motor "
        "and Blower Motor", field_type="group", required=False)
    _add_cab_pair(add, condenser_blower_group, "condenser_blower_body_clean", "Clean the Body of Condenser "
        "Motor and Blower Motor by Compressed Air", options="Done, Not Done")
    _add_cab_pair(add, condenser_blower_group, "condenser_motor_crack_check", "Check Condenser Motor Visually "
        "for Crack on Blade or Body", options="No Crack, Crack Found")
    _add_cab_pair(add, condenser_blower_group, "condenser_blower_mounting_fasteners_check", "Check and Ensure "
        "Mounting Fasteners Are Properly Tightened", options="OK, Not OK")
    _add_cab_pair(add, condenser_blower_group, "condenser_blower_terminal_box_check", "Check Connection at "
        "Terminal Boxes of Motor for Proper Tightness & Cables Are Terminated With Lugs", options="OK, Not OK")
    _add_cab_pair(add, condenser_blower_group, "condenser_blower_insulation_resistance", "Check Insulation "
        "Resistance of Motors by 500 V DC Megger From the Control Panel", field_type="numeric_range", unit="MOhm",
        min_value=2.0, max_value=1000.0, decimal_precision=1, standard_value="Attend Motors if Less Than 2MΩ")
    _add_cab_pair(add, condenser_blower_group, "condenser_blower_abnormal_sound_check", "Check Motors for Any "
        "Abnormal Sound While Running", options="No Abnormal Sound, Abnormal Sound Found")

    compressor_group = add("compressor_section", parent=minor_group, field_label="3.4 Compressor",
                            field_type="group", required=False)
    _add_cab_pair(add, compressor_group, "compressor_mounting_fasteners_check", "Check and Ensure Mounting "
        "Fasteners Are Properly Tightened", options="OK, Not OK")
    _add_cab_pair(add, compressor_group, "compressor_terminal_box_check", "Check Electrical Terminal Box Is "
        "Properly Tightened and Cables Are Terminated With Lugs", options="OK, Not OK")
    abnormal_sound_group = add("abnormal_sound_checks", parent=compressor_group, field_label="In Case of "
        "Abnormal Sound", field_type="group", required=False)
    _add_cab_pair(add, abnormal_sound_group, "electric_connection_sequence_check", "Check the Sequence of "
        "Electric Connection", options="Checked, Not Checked")
    _add_cab_pair(add, abnormal_sound_group, "compressor_winding_resistance_balance", "Ensure That the Winding "
        "Resistances of Compressor Motor Between UV, VW and WU Phases Are Balanced", options="OK, Not OK",
        standard_value="Balanced ±3%")

    heater_group = add("heater_section", parent=minor_group, field_label="3.5 Heater", field_type="group",
                        required=False)
    _add_cab_pair(add, heater_group, "heater_mounting_check", "Ensure Proper Mounting of Heater Without "
        "Touching Side Bodies", options="OK, Not OK")
    _add_cab_pair(add, heater_group, "heater_wire_clamping_check", "Ensure Proper Clamping of Electric Wires "
        "to Heater", options="OK, Not OK")
    _add_cab_pair(add, heater_group, "heating_element_dust_removal", "Remove Dust Accumulation on Heating "
        "Element Gently by Soft Brush/Dry Air", options="Done, Not Done")
    _add_cab_pair(add, heater_group, "thermostat_probe_clean_replace", "Clean Thermostat Temperature Probe "
        "(OHP) - Replace if Cracked or Broken", options="Cleaned, Replaced")
    _add_cab_pair(add, heater_group, "winter_season_current_check", "Check at the Beginning of Winter Season "
        "by Checking Current Drawn at Control Panel by Clamp Tester", field_type="numeric_range", unit="Amp",
        min_value=2.0, max_value=3.0, decimal_precision=1)

    trough_group = add("trough_section", parent=minor_group, field_label="3.6 Trough", field_type="group",
                        required=False)
    _add_cab_pair(add, trough_group, "condensate_drain_check", "Make Sure Condensate/Rain Water Drains "
        "Properly - No Blockage in Drain Pipes", options="No Blockage, Blockage Found")
    _add_cab_pair(add, trough_group, "trough_water_leakage_check", "Ensure That There Is No Leakage of Water "
        "to Cab", options="No Leakage, Leakage Found")

    ohp_group = add("ohp_hp_lp_section", parent=minor_group, field_label="3.7 OHP (Over Heat Protection), HP "
        "(High Pressure), LP (Low Pressure)", field_type="group", required=False)
    _add_cab_pair(add, ohp_group, "ohp_mounting_fasteners_check", "Check the Mounting Fasteners Are Properly "
        "Tightened", options="OK, Not OK")
    _add_cab_pair(add, ohp_group, "ohp_control_wires_clamp_check", "Ensure That Control Wires to HP/LP/OHP "
        "Cut-Out Are Properly Clamped", options="OK, Not OK")

    tdr_group = add("tdr_section", parent=minor_group, field_label="3.8 Time Delay Relay (TDR)",
                     field_type="group", required=False)
    _add_cab_pair(add, tdr_group, "tdr_assembly_clean", "Clean the Complete Assembly by Compressed Dry Air Jet",
                  options="Done, Not Done")
    _add_cab_pair(add, tdr_group, "tdr_physical_damage_check", "Check the Condition of the TDR for Physical "
        "Damage", options="No Damage, Damage Found")
    _add_cab_pair(add, tdr_group, "tdr_terminal_mounting_tighten", "Tighten Terminal & Mounting Screws",
                  options="Done, Not Done")
    _add_cab_pair(add, tdr_group, "tdr_thimbles_lugs_replace", "Replace Damage Thimbles/Lugs",
                  options="Replaced, Not Applicable")

    mcb_group = add("mcb_mpcb_section", parent=minor_group, field_label="3.9 MCBs (Miniature Circuit Breaker) "
        "& MPCB (Motor Protection Circuit Breaker)", field_type="group", required=False)
    _add_cab_pair(add, mcb_group, "mcb_mpcb_clean", "Clean the MCBs and MPCB With Dry Compressed Air",
                  options="Done, Not Done")
    _add_cab_pair(add, mcb_group, "mcb_mpcb_physical_damage_check", "Check the Condition of MCBs and MPCB for "
        "Physical Damage", options="No Damage, Damage Found")
    _add_cab_pair(add, mcb_group, "mcb_end_locks_check", "Ensure That End Locks Are Provided",
                  options="Provided, Not Provided")
    _add_cab_pair(add, mcb_group, "mcb_cable_rail_screws_tighten", "Tighten Electric Cable Connections and "
        "Rail Screws", options="Done, Not Done")

    contactors_group = add("contactors_section", parent=minor_group, field_label="3.10 Contactors",
                            field_type="group", required=False)
    _add_cab_pair(add, contactors_group, "contactors_clean", "Clean the Contactors With Dry Compressed Air",
                  options="Done, Not Done")
    _add_cab_pair(add, contactors_group, "contactors_continuity_check", "Check Continuity Between the Incoming "
        "and Outgoing Terminals", options="OK, Not OK")
    _add_cab_pair(add, contactors_group, "contactors_connection_tightness", "Ensure Tightness of Connection",
                  options="OK, Not OK")

    connector_group = add("connector_section", parent=minor_group, field_label="3.11 Connector",
                           field_type="group", required=False)
    _add_cab_pair(add, connector_group, "connector_flash_marks_check", "Open the Connectors and Check for "
        "Flash Marks/Damage to Pins", options="No Damage, Damage Found")
    _add_cab_pair(add, connector_group, "connector_tightness_check", "Ensure That They Are Tightened Properly",
                  options="OK, Not OK")
    _add_cab_pair(add, connector_group, "connector_moisture_removal", "Remove Moisture by Blowing Air Through "
        "Hot Air Gun", options="Done, Not Done")

    major_group = add("major_schedule", field_label="Maintenance Activities During Major Schedules",
                       field_type="group", required=False)
    _add_cab_pair(add, major_group, "all_ic_schedule_items", "All Items of IC Schedule", options="Done, Not Done")

    major_general_group = add("major_general", parent=major_group, field_label="4.2 General", field_type="group",
                               required=False)
    _add_cab_pair(add, major_general_group, "major_return_air_filters_clean", "Remove Return Air Filters by "
        "Opening the Grill - Clean These Filters With Water/Vacuum Cleaner or Compressed Air",
        options="Done, Not Done")
    _add_cab_pair(add, major_general_group, "major_top_cover_locking_gasket_check", "Ensure Proper Locking of "
        "Top Cover of AC Unit and Provision of Gasket - Replace Gasket if Damaged", options="OK, Replaced")

    major_motor_group = add("major_condenser_blower_motor", parent=major_group, field_label="4.4 Condenser "
        "Motor and Blower Motor", field_type="group", required=False)
    no_load_run_group = add("no_load_run_check", parent=major_motor_group, field_label="Run Motor on No Load "
        "for 15 Minutes and Check the Following", field_type="group", required=False)
    _add_cab_pair(add, no_load_run_group, "bearing_noise_check", "Bearing Noise", options="Normal, Abnormal")
    _add_cab_pair(add, no_load_run_group, "bearing_temp_rise_check", "Bearing Temperature Rise Above Ambient",
                  field_type="numeric_range", unit="°C", min_value=0.0, max_value=10.0, decimal_precision=1,
                  standard_value="Should Not Be More Than 10°C")
    _add_cab_pair(add, no_load_run_group, "spm_reading_check", "SPM (Shock Pulse Meter) Reading",
                  field_type="numeric_range", unit="dBN", min_value=0.0, max_value=20.0, decimal_precision=0,
                  standard_value="20dBN Max (Green Zone) - Replace Bearings if Defective")

    overhaul_motor_group = add("overhaul_blower_condenser_motor", parent=major_motor_group, field_label="Overhauling "
        "of Blower and Condenser Fan Motor", field_type="group", required=False)
    _add_cab_pair(add, overhaul_motor_group, "ir_before_after_overhaul", "Insulation Resistance (IR) Between "
        "Motor Terminals and Frame Before and After Overhauling", field_type="numeric_range", unit="MOhm",
        min_value=40.0, max_value=1000.0, decimal_precision=0, standard_value="Should Not Be Less Than 40MΩ "
        "at 500V Megger")
    _add_cab_pair(add, overhaul_motor_group, "terminal_block_damage_check", "Check Terminal Block and "
        "Connecting Lead for Any Physical Damage or Any Flash Mark", options="No Damage, Damage Found")
    _add_cab_pair(add, overhaul_motor_group, "hv_dielectric_test", "Perform HV (Di-Electric) Test on Stator by "
        "Applying 1.5 kV AC for One Minute - Leakage Current", field_type="numeric_range", unit="mA",
        min_value=0.0, max_value=1.0, decimal_precision=2, standard_value="Should Not Exceed 1.0mA")
    _add_cab_pair(add, overhaul_motor_group, "sct_surge_comparison_test", "SCT (Surge Comparison Test) of "
        "Stator at 1 kV", options="OK, Not OK")
    _add_cab_pair(add, overhaul_motor_group, "starting_current_no_load", "Starting Current of Motors on No "
        "Load", field_type="numeric_range", unit="A", min_value=0.0, max_value=14.0, decimal_precision=1,
        standard_value="Should Not Exceed 14A")
    _add_cab_pair(add, overhaul_motor_group, "no_load_current_check", "No Load Current of Motors",
                  field_type="numeric_range", unit="A", min_value=0.0, max_value=1.4, decimal_precision=2,
                  standard_value="Should Not Exceed 1.4A")
    _add_cab_pair(add, overhaul_motor_group, "motor_winding_resistance_balance", "Winding Resistance of Motors "
        "Between UV, VW and WU Phases", options="OK, Not OK", standard_value="Ensure Balanced ±10%")
    _add_cab_pair(add, overhaul_motor_group, "post_spray_ir_check", "Spray Water Over Running Motor by Jet "
        "Having 10mm Dia From All Side - After Spray Check IR Value (10 Min)", field_type="numeric_range",
        unit="MOhm", min_value=10.0, max_value=1000.0, decimal_precision=0,
        standard_value="Should Not Be Less Than 10MΩ")

    refrigerant_group = add("refrigerant_pipeline", parent=major_group, field_label="4.5 Refrigerant Pipe "
        "Line/Thermostatic Expansion Valve", field_type="group", required=False)
    _add_cab_pair(add, refrigerant_group, "pipeline_clamping_support_check", "Check Visually for Proper "
        "Clamping/Support", options="OK, Not OK")
    _add_cab_pair(add, refrigerant_group, "expansion_valve_crack_bend_check", "Ensure That Thermostatic "
        "Expansion Valve of Distributors to Evaporator Coil Does Not Have Any Crack, Bend or Kinks (Sensor Bulb "
        "Clamped on Suction Pipe at 2 O'Clock Position)", options="OK, Not OK")

    fins_group = add("evaporator_condenser_fins", parent=major_group, field_label="4.6 Evaporator/Condenser "
        "Fins", field_type="group", required=False)
    _add_cab_pair(add, fins_group, "fins_mounting_fasteners_check", "Check That the Mounting Fasteners Are "
        "Properly Tightened", options="OK, Not OK")
    _add_cab_pair(add, fins_group, "fins_damage_check", "Ensure That There Is No Damage to Fins",
                  options="No Damage, Damage Found")
    _add_cab_pair(add, fins_group, "fins_clean", "Clean the Evaporator and Condenser Fins With Pressurized "
        "Water and Blow Dry With Moisture Free Air at 10-15 Psi", options="Done, Not Done")

    cutout_group = add("ohp_hp_lp_cutouts", parent=major_group, field_label="4.7 OHP/HP/LP Cut-Outs",
                        field_type="group", required=False)
    _add_cab_pair(add, cutout_group, "lp_tripping_check", "Disconnect Blower Motor Through MPCB to Cause "
        "Compressor Tripping on Low Pressure (LP)", field_type="numeric_range", unit="psi", min_value=25.0,
        max_value=35.0, decimal_precision=1, standard_value="30±5 psi")
    _add_cab_pair(add, cutout_group, "hp_tripping_check", "Disconnect Condenser Fan Motor Through MPCB to "
        "Cause Compressor Tripping in High Pressure (HP)", field_type="numeric_range", unit="psi",
        min_value=435.0, max_value=465.0, decimal_precision=1, standard_value="450±15 psi")
    _add_cab_pair(add, cutout_group, "heater_tripping_check", "Check the Tripping of Heater by Switching Off "
        "the Blower - Probe of Digital Thermometer Near the OHP Sensor", field_type="numeric_range", unit="°C",
        min_value=60.0, max_value=70.0, decimal_precision=1, standard_value="Heater Should Trip at 65°C")

    major_tdr_group = add("major_tdr", parent=major_group, field_label="4.8 Time Delay Relay (TDR)",
                           field_type="group", required=False)
    _add_cab_pair(add, major_tdr_group, "tdr_time_setting_check", "Check the Time Setting on Test Bench",
                  field_type="numeric_range", unit="sec", min_value=165.0, max_value=195.0, decimal_precision=0,
                  standard_value="180±15 Sec")

    conditional_group = add("conditional_items_changed", field_label="Items Changed on Conditional Basis With "
        "Reasons", field_type="group", required=False)
    for i in range(1, 4):
        item_group = add(f"conditional_item_{i}", parent=conditional_group, field_label=f"Item {i}",
                          field_type="group", required=False)
        add(f"conditional_item_{i}_description", parent=item_group, field_label="Description", field_type="text",
            required=False)
        add(f"conditional_item_{i}_part_no", parent=item_group, field_label="Part No.", field_type="text",
            required=False)
        add(f"conditional_item_{i}_quantity", parent=item_group, field_label="Quantity", field_type="text",
            required=False)
        add(f"conditional_item_{i}_remarks", parent=item_group, field_label="Remarks/Reason", field_type="text",
            required=False)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="AC", template_code="135", technology="3_PHASE",
        template_name="Checksheet for Cab AC",
        description="AMC of Cab AC - TOH & IOH maintenance checksheet - 3-Phase - M35-CP section.",
        build_fn=build,
    )
    run_seed(
        equipment_code="AC_Conv", template_code="136", technology="CONVENTIONAL",
        template_name="Checksheet for Cab AC",
        description="AMC of Cab AC - TOH & IOH maintenance checksheet - Conventional - M35-CP section.",
        build_fn=build,
    )
