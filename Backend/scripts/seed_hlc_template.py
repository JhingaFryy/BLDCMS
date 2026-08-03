"""
Module 37: seeds the HLC (Hotel Load Convertor, 3-Phase, M9-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_hlc_template.py`

Source: "Checksheet for Hotel Load Convertor" (REF: RDSO/2016/EL/SMI/0297 Rev.'1'). The source
sheet's Action/Remarks column applies to "HLCs" collectively (one column, not split per HLC-1/
HLC-2 unit), so each checkpoint is implemented as a single field, matching the sheet's own
structure.
"""
from _aux_template_helpers import run_seed, add_final_remarks


def build(add):
    add("hlc_make", field_label="HLC Make", field_type="text", required=True)
    hlc1_group = add("hlc1_details", field_label="HLC-1 Details", field_type="group", required=False)
    add("hlc1_serial_no", parent=hlc1_group, field_label="Sr. No.", field_type="text", required=True)
    add("hlc1_mfg_doc", parent=hlc1_group, field_label="MFG/DOC", field_type="text", required=False)
    hlc2_group = add("hlc2_details", field_label="HLC-2 Details", field_type="group", required=False)
    add("hlc2_serial_no", parent=hlc2_group, field_label="Sr. No.", field_type="text", required=True)
    add("hlc2_mfg_doc", parent=hlc2_group, field_label="MFG/DOC", field_type="text", required=False)

    add("hlc_fault_log_download", field_label="Fault Log Schedules; Data Download Before Schedules",
        field_type="select", options="Done, Not Done", required=True, negative_values="Not Done")
    add("hlc_door_gaskets_check", field_label="Check Door Gaskets for Damages; if Found Damaged, "
        "Change the Same", field_type="select", options="OK, Damaged - Replaced", required=True,
        negative_values="Damaged - Replaced")
    add("hlc_hcl_covers_gaskets_ioh", field_label="Replace All the Gaskets of HCL Covers (IOH Only)",
        field_type="select", options="Replaced, N/A (IOH only), Not Replaced", required=True,
        negative_values="Not Replaced")
    add("hlc_body_side_filter_gasket", field_label="Replacement of Gasket of Body Side Filter",
        field_type="select", options="Replaced, Not Replaced", required=True, negative_values="Not Replaced")
    add("hlc_dust_ingress_check", field_label="Check the Dust Ingress Into the HLC Panel and "
        "Output Contactor Panel; Use a Vacuum Cleaner to Clean", field_type="select",
        options="Done, Not Done", required=True, negative_values="Not Done")
    add("hlc_igbt_air_entry_check", field_label="Check the HLC Main Air Entry for IGBT Modules & "
        "Magnetic Components and Clean Thoroughly", field_type="select", options="Done, Not Done",
        required=True, negative_values="Not Done")
    add("hlc_cable_tie_wraps_check", field_label="Check the Cable Tie Wraps of the Power Cables; "
        "Check for Sign of Overheating", field_type="select", options="OK, Issue Found", required=True,
        negative_values="Issue Found")

    add("hlc_dc_link_capacitance", field_label="Measure the Overall Capacitance of Each DC Link",
        field_type="numeric_range", required=True, unit="uF", min_value=11.4, max_value=12.6,
        decimal_precision=2, standard_value="SIEMENS & AAL - 12uF +/- 5% (MEDHA - 10.8uF +/- 5%, "
        "BHEL - 10.4uF +/- 5%)")

    add("hlc_input_output_control_tightness", field_label="Check Tightness of Connections at "
        "Input, Output and Control Cables", field_type="select", options="OK, Loose", required=True,
        negative_values="Loose")
    add("hlc_power_connection_color_overheating", field_label="Check the Power Connection for "
        "Color Changes/Overheating and Change the Cables and Sockets, if Required", field_type="select",
        options="OK, Issue Found", required=True, negative_values="Issue Found")
    add("hlc_power_cable_connections_tightness", field_label="Check Tightness of Connections of "
        "Power Cables", field_type="select", options="OK, Loose", required=True, negative_values="Loose")
    add("hlc_precharging_contactors_check", field_label="Check the Pre-Charging Contactors for "
        "Any Signs of Physical Damage, Overheating or Discoloration; Check for Loose Connections",
        field_type="select", options="OK, Issue Found", required=True, negative_values="Issue Found")
    add("hlc_main_contactors_check", field_label="Check the Contacts of the Main Contactors for "
        "Any Signs of Physical Damage, Overheating or Discoloration; Check for Loose Connections",
        field_type="select", options="OK, Issue Found", required=True, negative_values="Issue Found")
    add("hlc_heat_sinks_cleaned", field_label="Clean the Heat Sinks of HLCs", field_type="select",
        options="Cleaned, Not Cleaned", required=True, negative_values="Not Cleaned")
    add("hlc_fdp_memory_erased", field_label="After Schedule of Inspection, Erase FDP Memory",
        field_type="select", options="Done, Not Done", required=True, negative_values="Not Done")

    voltage_group = add("hlc_working_parameters", field_label="Check Parameters of HLC in Working "
        "Conditions", field_type="group", required=False,
        standard_value="Output Voltage: 750V +5%/-2%; Line to Earth Voltage Peak < 800V")
    add("hlc_voltage_vph_wrt_vpb", parent=voltage_group, field_label="Vph WRT Vpb", field_type="numeric_range",
        required=True, unit="V", min_value=735.0, max_value=787.5, decimal_precision=0)
    add("hlc_voltage_vph_wrt_wpb", parent=voltage_group, field_label="Vph WRT Wpb", field_type="numeric_range",
        required=True, unit="V", min_value=735.0, max_value=787.5, decimal_precision=0)
    add("hlc_voltage_other_phase", parent=voltage_group, field_label="Any Other Phase", field_type="numeric_range",
        required=True, unit="V", max_value=800.0, decimal_precision=0)

    add("hlc_earth_fault_checking", field_label="Input and Output Earth Fault Checking",
        field_type="select", options="OK, Fault Found", required=True, negative_values="Fault Found")
    add("hlc_backup_battery_text_display", field_label="Replace the Back-Up Battery of Text "
        "Display Unit of HLC, if Available", field_type="select",
        options="Replaced, N/A (IOH only/Not Available), Not Replaced", required=True,
        negative_values="Not Replaced")

    add("hlc_cable_entry_sealing", field_label="Check the Sealing of the Cable Entry Into the "
        "Panel (to Stop the Dust Entry)", field_type="select", options="OK, Issue Found", required=True,
        negative_values="Issue Found")
    add("hlc_earth_connections_check", field_label="Check the Earth Connections of the HLC and "
        "Output Contactor Panels", field_type="select", options="OK, Issue Found", required=True,
        negative_values="Issue Found")
    add("hlc_mounting_bolts_tightness", field_label="Check the Tightness of Mounting/Fixation "
        "Bolts With the Loco Body", field_type="select", options="Tight, Loose", required=True,
        negative_values="Loose")
    add("hlc_connectors_tightness", field_label="Check the Tightness/Intactness of Connectors of "
        "the Panel", field_type="select", options="OK, Issue Found", required=True, negative_values="Issue Found")
    add("hlc_door_locks_check", field_label="Check the Door Locks of the Panel", field_type="select",
        options="OK, Issue Found", required=True, negative_values="Issue Found")
    add("hlc_output_contactors_opower_cable", field_label="Check the Output Contactors and O/P "
        "Power Cable Connection for Any Overheating, Physical Damage or Discoloration; Check for "
        "Loose Connections", field_type="select", options="OK, Issue Found", required=True,
        negative_values="Issue Found")
    add("hlc_display_keypad_working", field_label="Check the Working of Display Unit of HLCs & "
        "Functioning of Keypad Keys", field_type="select", options="Working, Not Working",
        required=True, negative_values="Not Working")
    add("hlc_gate_drive_unit_check", field_label="Check Gate Drive Unit of HCL for Its Healthiness "
        "and Cleaning; Measure DB Loose of Fiber Optic Cables", field_type="select",
        options="OK, Issue Found", required=True, negative_values="Issue Found")
    add("hlc_sine_filter_capacitor_value", field_label="Visually Check the Sine Filter Capacitor "
        "and Measure Its Value; Ensure Proper Tightening Torque of Fasteners", field_type="number",
        required=True, unit="uF")
    add("hlc_rc_filter_discharge_resistors", field_label="Visually Inspect the RC Filter and "
        "Discharge Resistors for Signs of Overheating", field_type="select", options="OK, Issue Found",
        required=True, negative_values="Issue Found")
    add("hlc_precharge_resistor_check", field_label="Visually Inspect Pre-Charge Resistor; "
        "Replace if Found Damaged or Overheated", field_type="select",
        options="OK, Damaged - Replaced", required=True, negative_values="Damaged - Replaced")
    add("hlc_blower_transformer_check", field_label="Visual Checking of Blower Transformer, if "
        "Available", field_type="select", options="OK, Issue Found", required=False,
        negative_values="Issue Found")
    add("hlc_load_arrangement_test", field_label="Check Both HLCs on Load Arrangement for "
        "Ensuring Proper Working on Line; Run HLC on Load for 5-10 Minutes; Check All Indications "
        "at Control Box Are Proper or Not", field_type="select", options="OK, Issue Found",
        required=True, negative_values="Issue Found")
    add("hlc_hog_on_command_indication", field_label="Ensure Proper Working of HOG ON Command "
        "Indication Lamp Provided in D-Panel", field_type="select", options="Working, Not Working",
        required=True, negative_values="Not Working", authority_reference="RDSO MS-488")
    add("hlc_fault_reset_command_check", field_label="Check Working of Fault Reset Command With "
        "the Help of Control Box", field_type="select", options="Working, Not Working", required=True,
        negative_values="Not Working")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="HLC", template_code="52", technology="3_PHASE",
        template_name="Checksheet for HLC",
        description="Hotel Load Convertor (3-Phase) checksheet - M9-HR section.",
        build_fn=build,
    )
