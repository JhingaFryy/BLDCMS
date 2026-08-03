"""
Module 36: seeds the M6-HR 3-Phase (WAP-7/WAG-9) checksheet template - an equipment-less,
section-wide template (no Equipment record, no SectionEquipmentMap row - template selection
depends only on section_id + locomotive technology).

Run once: `venv/bin/python scripts/seed_m6hr_3phase_template.py`

Source: "ELECTRIC LOCOMOTIVE SHED, VALSAD - Before energise loco following points to be checked"
+ "CHECK LIST FOR M6HR TESTING OF WAP-7/WAG-9 LOCO" (filename "M6-HR 3-Phase.pdf") - a wholly
independent document from the Conventional (WAG-5) checksheet, per Module 36's explicit
filename-based identification rule.
"""
from _section_template_helpers import run_seed, add_final_remarks


def add_select(add, key, label, options="Checked, Not Checked", negative="Not Checked",
              standard=None, authority=None, required=False):
    return add(
        key, field_label=label, field_type="select", options=options, required=required,
        standard_value=standard, authority_reference=authority, negative_values=negative,
    )


def add_cab_pair(add, key, label, options="Working, Not Working", negative="Not Working"):
    group = add(key, field_label=label, field_type="group", required=False)
    for cab in ("Cab-1", "Cab-2"):
        add(f"{key}_{cab.lower().replace('-', '')}", parent=group, field_label=cab,
            field_type="select", options=options, required=False, negative_values=negative)
    return group


def build(add):
    # === Before Energise Loco - Points to Be Checked ===
    pre_energise_items = [
        ("pre_energise_sr_oil_level", "SR-1 & 2 Oil Level to Be Checked"),
        ("pre_energise_xmer_oil_level", "X'mer Oil Level to Be Checked"),
        ("pre_energise_aux_terminal_connection", "All Auxiliary's Terminal Connection to Be Checked"),
        ("pre_energise_vcb_gapless_cable_earthing", "VCB Gapless Cable Connection & Earthing "
            "Shunt to Be Checked"),
        ("pre_energise_vcb_bushing_pt_xmer_insulator", "VCB Gapless Main Bushing Connection & PT "
            "X'mer Insulator Foundation Fitness & Insulator Cleaning to Be Checked"),
        ("pre_energise_harmonic_filter_foundation_cable", "Harmonic Filter Foundation Fitness & "
            "It's Cable Connection to Be Checked"),
        ("pre_energise_tm_cable_sensor_coupler", "All TM's Cable Connection & Sensor Coupler "
            "Fitness to Be Checked"),
    ]
    for key, label in pre_energise_items:
        add_select(add, key, label, options="Checked, Not Checked", negative="Not Checked")
    add_select(add, "pre_energise_bv_box_ungrounded", "Ensure BV-Box in Un Ground Position",
        options="Ensured, Not Ensured", negative="Not Ensured")

    # === Check List for M6HR Testing of WAP-7/WAG-9 Loco ===
    add_select(add, "test_tube_light_machine_room_cabs", "Working of Tube Light of Machine Room "
        "& Cabs (All Tube Lights Are Working)", options="Working, Not Working", negative="Not Working")

    marker_light_group = add("test_marker_light_working", field_label="Working of Marker Light "
        "(All Marker Lights Are Working)", field_type="group", required=False)
    add("test_marker_light_red", parent=marker_light_group, field_label="RED", field_type="select",
        options="Working, Not Working", required=False, negative_values="Not Working")
    add("test_marker_light_white", parent=marker_light_group, field_label="White", field_type="select",
        options="Working, Not Working", required=False, negative_values="Not Working")

    add_select(add, "test_auto_flasher", "Auto Flasher (Only by RS)", options="Working, Not Working",
        negative="Not Working")
    add_select(add, "test_flasher_light_bpfl", "Working of Flasher Light by BPFL (All Flasher "
        "Lights Are Working)", options="Working, Not Working", negative="Not Working")
    add_select(add, "test_spot_light", "Working of Spot Light (All Spot Lights Are Working)",
        options="Working, Not Working", negative="Not Working")

    head_light_group = add("test_head_light_working", field_label="Working of Head Light (Both "
        "Head Lights Are Working)", field_type="group", required=False)
    add("test_head_light_front", parent=head_light_group, field_label="Front", field_type="select",
        options="Working, Not Working", required=False, negative_values="Not Working")
    add("test_head_light_rear", parent=head_light_group, field_label="Rear", field_type="select",
        options="Working, Not Working", required=False, negative_values="Not Working")

    led_group = add("test_led_indications_fbv_cel", field_label="Checking of LED Indications in "
        "FBV Card in CEL-1 & 2 ('T Slot' LED 39.3 Yellow Must Be Flickering)", field_type="group",
        required=False)
    add("test_led_cel1", parent=led_group, field_label="CEL-1", field_type="text", required=False)
    add("test_led_cel2", parent=led_group, field_label="CEL-2", field_type="text", required=False)

    battery_voltage_group = add("test_battery_voltage_pclh", field_label="Battery Voltage "
        "(Voltmeter) Multi Meter (in PCLH)", field_type="group", required=False)
    add("test_battery_voltage_positive_earth", parent=battery_voltage_group, field_label="+ve Earth",
        field_type="number", required=False, unit="V")
    add("test_battery_voltage_negative_earth", parent=battery_voltage_group, field_label="-ve Earth",
        field_type="number", required=False, unit="V")
    add("test_battery_voltage_total", parent=battery_voltage_group, field_label="Total",
        field_type="number", required=False, unit="V")

    cooling_fan_group = add("test_cooling_fan_working", field_label="Working of Cooling Fan",
        field_type="group", required=False,
        help_text="Recorded per unit: SR-1, SR-2, BUR-1, BUR-2, BUR-3, CEL-1, CEL-2")
    for unit in ("sr1", "sr2", "bur1", "bur2", "bur3", "cel1", "cel2"):
        add(f"test_cooling_fan_{unit}", parent=cooling_fan_group, field_label=unit.upper().replace("SR", "SR-").replace("BUR", "BUR-").replace("CEL", "CEL-"),
            field_type="select", options="Working, Not Working", required=False, negative_values="Not Working")

    silica_gel_group = add("test_silica_gel_tfp_breather", field_label="Condition of Silica Gel "
        "of TFP Breather", field_type="group", required=False)
    add("test_silica_gel_tr1", parent=silica_gel_group, field_label="TR-1", field_type="select",
        options="OK, Not OK", required=False, negative_values="Not OK")
    add("test_silica_gel_tr2", parent=silica_gel_group, field_label="TR-2", field_type="select",
        options="OK, Not OK", required=False, negative_values="Not OK")

    add_cab_pair(add, "test_indication_lamp_working", "Working of All Indication Lamp")
    add_cab_pair(add, "test_monitor_dds_working", "Working of Monitor (DDS)")

    earth_fault_group = add("test_earth_fault_dc_voltage_control_ckt", field_label="Test "
        "Function Earth Fault DC Voltage (Control Ckt.)", field_type="group", required=False)
    for suffix, label in (("positive", "Positive PCLH + Earth"), ("negative", "Negative PCLH + Earth")):
        sub = add(f"test_earth_fault_{suffix}", parent=earth_fault_group, field_label=label,
                  field_type="group", required=False)
        add(f"test_earth_fault_{suffix}_cab1", parent=sub, field_label="CAB-1", field_type="select",
            options="Working, Not Working", required=False, negative_values="Not Working")
        add(f"test_earth_fault_{suffix}_cab2", parent=sub, field_label="CAB-2", field_type="select",
            options="Working, Not Working", required=False, negative_values="Not Working")

    add_cab_pair(add, "test_function_simulation_mode", "Function Test in Simulation Mode")

    vigilance_group = add("test_vigilance_work", field_label="Work of Vigilance", field_type="group",
        required=False, help_text="Push Button (BPVG), Ack. Button (BPVR), Rest Button")
    for suffix, label in (("push_button", "Push Button (BPVG)"), ("ack_button", "Ack. Button (BPVR)"),
                          ("rest_button", "Rest Button")):
        sub = add(f"test_vigilance_{suffix}", parent=vigilance_group, field_label=label,
                  field_type="group", required=False)
        add(f"test_vigilance_{suffix}_cab1", parent=sub, field_label="CAB-1", field_type="select",
            options="Working, Not Working", required=False, negative_values="Not Working")
        add(f"test_vigilance_{suffix}_cab2", parent=sub, field_label="CAB-2", field_type="select",
            options="Working, Not Working", required=False, negative_values="Not Working")

    air_leakage_group = add("test_air_leakage_contactor_pipe_line", field_label="Air Leakage "
        "Checking of Contactor & Pipe Line", field_type="group", required=False)
    add("test_air_leakage_inside_fb_panel", parent=air_leakage_group, field_label="Inside FB Panel",
        field_type="select", options="No Leakage, Leakage", required=False, negative_values="Leakage")
    add("test_air_leakage_sr12", parent=air_leakage_group, field_label="Check SR-1,2 Air Leakage",
        field_type="select", options="No Leakage, Leakage", required=False, negative_values="Leakage")

    add_cab_pair(add, "test_fdu_smoke_working", "Working of FDU by Smoke to Be Checked (Buzzer "
        "Sound in Both Cab From Any One Cab)")
    add_cab_pair(add, "test_te_be_meter_working", "Working of TE/BE Meter")
    add_cab_pair(add, "test_regression_a9_rs", "Regression Through A9 & RS", options="Working, Not Working")

    oil_level_group = add("test_oil_level_min_max", field_label="Oil Level Should Between Min & Max",
        field_type="group", required=False)
    for unit in ("SR-1", "SR-2", "TR-1", "TR-2"):
        add(f"test_oil_level_{unit.lower().replace('-', '')}", parent=oil_level_group, field_label=unit,
            field_type="select", options="OK, Not OK", required=False, negative_values="Not OK")

    add("test_vcb_timer_1sec", field_label="VCB Timer 1 sec", field_type="text", required=False,
        standard_value="1 sec")
    add_cab_pair(add, "test_bpcs_working", "Working of BPCS")

    rotating_switch_group = add("test_rotating_switches_sb1_panel", field_label="Working of All "
        "Rotating Switches to Be Checked in SB-1 Panel", field_type="group", required=False)
    for suffix, label in (
        ("failure_mode_152", "Failure Mode Operation 152 - \"0\""),
        ("bogie_cutout_154", "Bogie Cut Out 154 - Normal"),
        ("configuration_160", "Configuration 160 - \"1\""),
        ("vigilance_cutoff_2371", "Vigilance Device Cut Off 237.1 - \"1\""),
    ):
        sub = add(f"test_rotating_{suffix}", parent=rotating_switch_group, field_label=label,
                  field_type="group", required=False)
        add(f"test_rotating_{suffix}_cab1", parent=sub, field_label="CAB-1", field_type="select",
            options="Working, Not Working", required=False, negative_values="Not Working")
        add(f"test_rotating_{suffix}_cab2", parent=sub, field_label="CAB-2", field_type="select",
            options="Working, Not Working", required=False, negative_values="Not Working")

    tm_temp_group = add("test_tm_temperature_driver_display", field_label="Temperature Value of "
        "TM as Seen in Driver Display", field_type="group", required=False)
    for i in range(1, 7):
        add(f"test_tm_temp_tm{i}", parent=tm_temp_group, field_label=f"TM{i}", field_type="number",
            required=False, unit="C")

    add("test_fdu_calibration", field_label="FDU Calibration", field_type="select",
        options="OK, Not OK", required=False, negative_values="Not OK")

    # --- Annexure-1 for TI-322 (MV Drop, 7 named contactors) ---
    annexure_group = add("test_annexure1_ti322_mv_drop", field_label="Annexure-1 for TI-322 - "
        "MV Drop (B/W 0 to 50 mV)", field_type="group", required=False, standard_value="0-50 mV")
    annexure_rows = [
        ("218", "SB-1", "2095-2096", "MCE\"ON\""),
        ("126", "SB-1", "2094-2095", "MCE\"ON\""),
        ("126.7/1", "SB-1", "2101A-2111A", "From CAB-1 MCE\"ON\""),
        ("126.7/2", "SB-2", "2101B-2111B", "From CAB-2 MCE\"ON\""),
        ("130.1", "SB-1", "2064-2302", "Panto Raised"),
        ("136.4", "SB-1", "2314-2312", "DJ Closed"),
        ("48.2", "SB-2", "3027-2068", "CPA ON"),
    ]
    for contactor, location, cable_no, condition in annexure_rows:
        key = "test_annexure_mv_drop_" + contactor.lower().replace(".", "_").replace("/", "_")
        add(key, parent=annexure_group, field_label=f"Contactor {contactor} ({location})",
            field_type="number", required=False, unit="mV",
            help_text=f"B/W Cable No. {cable_no}, Interlock 1-2, Condition: {condition}")

    battery_charging_group = add("test_battery_charging_voltage_pclh", field_label="Battery "
        "Charging Voltage (Voltmeter) Multi Meter (in PCLH)", field_type="group", required=False)
    add("test_battery_charging_1", parent=battery_charging_group, field_label="Reading 1",
        field_type="number", required=False, unit="V")
    add("test_battery_charging_2", parent=battery_charging_group, field_label="Reading 2",
        field_type="number", required=False, unit="V")

    add_cab_pair(add, "test_emergency_push_button", "Working of Emergency Push Button (Observe: "
        "Pantograph Down, Emergency Brake Applied, Flasher Working and Check Message on DDS)")

    mcb100_group = add("test_battery_charging_mcb100", field_label="Battery Charging Working "
        "Through MCB-100 in UBA Meter", field_type="group", required=False)
    for suffix in ("1_2", "1_3", "2_3"):
        add(f"test_battery_charging_mcb100_{suffix}", parent=mcb100_group,
            field_label=suffix.replace("_", "-"), field_type="number", required=False, unit="V")

    add_cab_pair(add, "test_speedo_meter_working", "Working of Speedo Meter")
    add_cab_pair(add, "test_sander_working", "Working of Sander")

    vcb_tripping_group = add("test_vcb_tripping_sr_pump_mcb", field_label="VCB Tripping Through "
        "SR Pump MCB", field_type="group", required=False)
    add("test_vcb_tripping_6311", parent=vcb_tripping_group, field_label="63.1/1", field_type="select",
        options="OK, Not OK", required=False, negative_values="Not OK")
    add("test_vcb_tripping_6312", parent=vcb_tripping_group, field_label="63.1/2", field_type="select",
        options="OK, Not OK", required=False, negative_values="Not OK")

    bogie_movement_group = add("test_bogie_movement_isolation_sw", field_label="Movement of "
        "Bogie (Through Isolation SW)", field_type="group", required=False)
    add("test_bogie_movement_1", parent=bogie_movement_group, field_label="Bogie-1", field_type="select",
        options="OK, Not OK", required=False, negative_values="Not OK")
    add("test_bogie_movement_2", parent=bogie_movement_group, field_label="Bogie-2", field_type="select",
        options="OK, Not OK", required=False, negative_values="Not OK")

    add("test_ocr_tripping_working", field_label="Working of OCR Tripping", field_type="select",
        options="OK, Not OK", required=False, negative_values="Not OK")

    rgcp_range_group = add("test_rgcp_range", field_label="RGCP Range", field_type="group",
                           required=False)
    add("test_rgcp_range_cut_in", parent=rgcp_range_group, field_label="Cut In", field_type="number",
        required=False, unit="kg/cm2", standard_value="8.00 kg/cm2")
    add("test_rgcp_range_cut_out", parent=rgcp_range_group, field_label="Cut Out", field_type="number",
        required=False, unit="kg/cm2", standard_value="10.00 kg/cm2")

    earth_fault2_group = add("test_earth_fault_dc_voltage_2", field_label="Test Function Earth "
        "Fault DC Voltage", field_type="group", required=False)
    for suffix, label in (
        ("harmonic_filter", "A) Harmonic Filter (Earth + Link 89.6)"),
        ("aux_ckt", "B) Aux Ckt 89.2 (Earth + 1117 in HB-2)"),
        ("415_110", "C) 415/110 (Earth + 1218 in HB-1)"),
    ):
        sub = add(f"test_earth_fault2_{suffix}", parent=earth_fault2_group, field_label=label,
                  field_type="group", required=False)
        add(f"test_earth_fault2_{suffix}_cab1", parent=sub, field_label="CAB-1", field_type="select",
            options="Working, Not Working", required=False, negative_values="Not Working")
        add(f"test_earth_fault2_{suffix}_cab2", parent=sub, field_label="CAB-2", field_type="select",
            options="Working, Not Working", required=False, negative_values="Not Working")

    # --- Calibrated Anemometer (SMI-RDSO/0255) by M3 Aux ---
    anemometer_group = add("test_calibrated_anemometer", field_label="Calibrated Anemometer "
        "(SMI-RDSO/0255) by M3 Aux", field_type="group", required=False,
        authority_reference="SMI-RDSO/0255")
    anemometer_rows = [
        ("above_sr_top", "Above SR Electronics Top Side", 3.0, 2),
        ("heat_sink_top_right_back", "Control Electronics Heat Sink Top Right Back Side", 2.0, 2),
        ("heat_sink_top_left", "Control Electronics Heat Sink Top Left Side", 2.0, 2),
        ("above_bur1", "Above Top Side BUR-1", 3.5, 1),
        ("above_bur2", "Above Top Side BUR-2", 3.5, 1),
        ("above_bur3", "Above Top Side BUR-3", 3.5, 1),
        ("below_scmrb", "Below Under Frame of Opening of SCMRB", 12.0, 2),
    ]
    for key, label, min_val, count in anemometer_rows:
        sub = add(f"test_anemometer_{key}", parent=anemometer_group, field_label=label,
                  field_type="group", required=False, standard_value=f"Min. {min_val}")
        unit_labels = ["SR-1", "SR-2"] if count == 2 else ["Reading"]
        for u in unit_labels:
            add(f"test_anemometer_{key}_{u.lower().replace('-', '')}", parent=sub, field_label=u,
                field_type="numeric_range", required=False, unit="m/s", min_value=min_val,
                decimal_precision=1)
    ocb_radiator_group = add("test_anemometer_ocb_radiator", field_label="OCB in Under Frame of "
        "Radiator", field_type="group", required=False, standard_value="Min. 8.0")
    for ocb in ("OCB-1", "OCB-2"):
        for i in range(1, 4):
            add(f"test_anemometer_ocb_{ocb.lower().replace('-', '')}_{i}", parent=ocb_radiator_group,
                field_label=f"{ocb} Reading {i}", field_type="numeric_range", required=False,
                unit="m/s", min_value=8.0, decimal_precision=1)
    tm_jali_group = add("test_anemometer_tm_end_shield_jali", field_label="In Under Frame at TM "
        "End Shield Jali", field_type="group", required=False, standard_value="Min. 12")
    for i in range(1, 7):
        add(f"test_anemometer_tm{i}", parent=tm_jali_group, field_label=f"TM{i}",
            field_type="numeric_range", required=False, unit="m/s", min_value=12.0, decimal_precision=1)
    sctmb_group = add("test_anemometer_sctmb", field_label="Below Under Frame at Opening of SCTMB",
        field_type="group", required=False, standard_value="Min. 13")
    add("test_anemometer_sctmb1", parent=sctmb_group, field_label="SCTMB-1", field_type="numeric_range",
        required=False, unit="m/s", min_value=13.0, decimal_precision=1)
    add("test_anemometer_sctmb2", parent=sctmb_group, field_label="SCTMB-2", field_type="numeric_range",
        required=False, unit="m/s", min_value=13.0, decimal_precision=1)

    # --- Performance of Oil Pumps Pressure ---
    oil_pumps_group = add("test_oil_pumps_performance", field_label="Measure the Performance of "
        "the Oil Pumps of TFP & SR Through the MIC View and Recorder (Prescribed 45% to 65%)",
        field_type="group", required=False,
        help_text="SR = Earth + S slot (06) right; TR = Earth + T slot (04) right")
    for unit in ("SR1", "SR2", "TFP1", "TFP2"):
        add(f"test_oil_pumps_{unit.lower()}", parent=oil_pumps_group, field_label=unit,
            field_type="number", required=False)

    burs_group = add("test_burs_performance_isolated", field_label="Performance of BURs When One "
        "BUR Is Isolated (When Any BUR Goes Out, Rest of the Two BURs Should Take the Load of All "
        "Auxiliaries at Ventilation Level 3 of the Loco)", field_type="group", required=False)
    for bur in ("BUR1", "BUR2", "BUR3"):
        add(f"test_burs_{bur.lower()}", parent=burs_group, field_label=bur, field_type="select",
            options="OK, Not OK", required=False, negative_values="Not OK")

    add("test_brake_test_loco", field_label="Brake Test on Loco (Loco Should Not Move On / Loco "
        "Should Move On)", field_type="select", options="OK, Not OK", required=False,
        negative_values="Not OK")
    add("test_fire_extinguisher_count", field_label="No. of Fire Extinguisher", field_type="number",
        required=False)
    add("test_cleanliness_loco_cab", field_label="Ensure the Cleanliness: Inside the Loco and Cab",
        field_type="select", options="Done, Not Done", required=False, negative_values="Not Done")
    add("test_light_glasses_cleaned", field_label="All H/Light, F/Light, M/Light Glasses Are "
        "Properly Cleaned", field_type="select", options="Done, Not Done", required=False,
        negative_values="Not Done")
    add("test_painting_sticker_cab", field_label="Painting / Sticker Instruction in Cab",
        field_type="select", options="OK, Not OK", required=False, negative_values="Not OK")
    add("test_dead_loco_movement_sch_date", field_label="Dead Loco Movement, Sch. Date",
        field_type="select", options="OK, Not OK", required=False, negative_values="Not OK")
    add("test_pantograph_selector_switch", field_label="Check Working of Pantograph Selector Switch",
        field_type="select", options="Working, Not Working", required=False, negative_values="Not Working")

    # --- Numbered supplementary sections ---
    tm_igbt_group = add("test_tm_working_igbt_loco", field_label="Working of Each Traction Motor "
        "in IGBT Loco", field_type="group", required=False)
    for i in range(1, 7):
        add(f"test_tm_igbt_tm{i}", parent=tm_igbt_group, field_label=f"TM{i}", field_type="select",
            options="Working, Not Working", required=False, negative_values="Not Working")

    tm_color_group = add("test_tm_colour_code", field_label="Traction Motor Colour Code",
        field_type="group", required=False)
    for i in range(1, 7):
        add(f"test_tm_colour_tm{i}", parent=tm_color_group, field_label=f"TM{i}", field_type="text",
            required=False)

    tm_earthing_group = add("test_tm_earthing_shunt", field_label="Traction Motor Earthing Shunt",
        field_type="group", required=False)
    for i in range(1, 7):
        add(f"test_tm_earthing_tm{i}", parent=tm_earthing_group, field_label=f"TM{i}",
            field_type="select", options="OK, Not OK", required=False, negative_values="Not OK")

    hlc_group = add("test_hotel_load_converter_working", field_label="Working of Hotel Load Converter",
        field_type="group", required=False)
    add("test_hlc1", parent=hlc_group, field_label="HLC1", field_type="text", required=False)
    add("test_hlc2", parent=hlc_group, field_label="HLC2", field_type="text", required=False)

    battery_sealing_group = add("test_battery_box_sealing", field_label="Battery Box Sealing to "
        "Be Check", field_type="group", required=False)
    add("test_battery_box1_sealing", parent=battery_sealing_group, field_label="BA Box 1",
        field_type="text", required=False)
    add("test_battery_box2_sealing", parent=battery_sealing_group, field_label="BA Box 2",
        field_type="text", required=False)

    add_cab_pair(add, "test_vcu_reset_working", "VCU Reset Working")

    return_earth_group = add("test_return_earth_current", field_label="Return Earth Current for "
        "WAP7/WAG9", field_type="group", required=False)
    for label in ("Axle Box 1", "Axle Box 2-6", "Axle Box 3-7", "Axle Box 3-12"):
        key = "test_return_earth_" + label.lower().replace(" ", "_").replace("-", "_")
        add(key, parent=return_earth_group, field_label=label, field_type="number", required=False,
            unit="Amp")

    fire_ext_group = add("test_fire_extinguisher_sr_no", field_label="Fire Extinguisher Sr. No.",
        field_type="group", required=False)
    add("test_fire_ext_cab1", parent=fire_ext_group, field_label="CAB1", field_type="text", required=False)
    add("test_fire_ext_cab2", parent=fire_ext_group, field_label="CAB2", field_type="text", required=False)

    add("test_harmonic_filter_current", field_label="Harmonic Filter Current", field_type="number",
        required=False, unit="Amp")

    # --- Modification (blank free-form table in the source - see Conventional's Modification
    # section for the equivalent WITH printed item descriptions; this 3-Phase document's
    # Modification table has none, only ruled blank rows, so it is captured as free text) ---
    add("test_modification_notes", field_label="Modification Notes", field_type="textarea",
        required=False)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        section_name="M6-HR", template_code="37", technology="3_PHASE",
        template_name="Checksheet for M6-HR (3-Phase)",
        description="M6-HR Testing checklist for WAP-7/WAG-9 (3-Phase) - equipment-less section-wide checksheet.",
        build_fn=build,
    )
