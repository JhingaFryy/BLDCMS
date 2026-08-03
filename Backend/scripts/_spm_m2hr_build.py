"""
Module 46: shared field builder for the M2-HR Speedometer (SPM) checksheet, used by both
seed_spm_template.py (3-Phase) and seed_spm_conv_template.py (Conventional) since only a single
source document ("SPM.pdf" - TRS/ELS/BL/M2HR/Comm./SPM/A) was supplied for both technologies.

Item 7 (Electrical Checking) on the source sheet marks sub-items A/B/C as "(3 Phase/Conv.)" and
D/E/F as "(Conv.)" only - so the Conventional build includes all six, the 3-Phase build includes
only A/B/C. Everything else on the sheet applies to both technologies identically.
"""
from _m2hr_template_helpers import add_confirm, add_date, add_numeric, add_text


def build_spm(add, set_page, conv_only=False):
    add_text(add, "eqp_recorder_sr_no", "Eqp. Sr. No. - Recorder", required=False)
    add_text(add, "eqp_indicator_sr_no", "Eqp. Sr. No. - Indicator", required=False)
    add_text(add, "eqp_pg_sr_no", "Eqp. Sr. No. - PG", required=False)
    add_text(add, "eqp_scu_sr_no", "Eqp. Sr. No. - SCU", required=False)
    add_text(add, "eqp_ct_sr_no", "Eqp. Sr. No. - CT", required=False)
    add_text(add, "eqp_pt_sr_no", "Eqp. Sr. No. - PT", required=False)
    add_text(add, "make", "Make", required=True)
    add_date(add, "remove_date_sch", "Remove Date/Sch")
    add_date(add, "date_of_overhauling", "Date of Overhauling")
    add_date(add, "provided_date_sch", "Provided Date/Sch")

    add("memory_card_data_download", field_label="Download Memory Card Data and Analyze It; "
        "Note and Fix Any Faults Found", field_type="textarea", required=True)

    visual_group = add("visual_check", field_label="Visual Check", field_type="group", required=True)
    add_confirm(add, "visual_pointer_at_zero", "Pointer at '0'", done_word="Yes", negative_word="No",
                parent=visual_group)
    add_confirm(add, "visual_dial_display_no_crack",
                "9/50 Pin 'D' Connector, Dial/Display/Memory Freeze Glass - No Crack/Damage",
                done_word="No damage", negative_word="Damage", parent=visual_group)
    add_confirm(add, "visual_door_hinges_stuck", "Door Hinges Not Stuck", done_word="Not stuck",
                negative_word="Stuck", parent=visual_group)

    add_confirm(add, "clean_2kg_air", "Clean Using 2 Kg/cm2 Dry Air", done_word="Cleaned")
    add_confirm(add, "pcb_overheating_flashing_check",
                "Check All PCB Boards for Any Overheating/Flashing", done_word="No overheating",
                negative_word="Overheating found")
    add_confirm(add, "aoh_ioh_kit_parts_replace", "Replace Parts as per AOH/IOH Kit",
                done_word="Replaced")

    data_group = add("data_downloading_recording", field_label="Check Data Downloading/Recording",
                     field_type="group", required=True, authority_reference="SMI 289-5.10.1.9/5.10.1.10")
    add_confirm(add, "data_external", "External Data", done_word="Done", parent=data_group)
    add_confirm(add, "data_internal", "Internal Data", done_word="Done", parent=data_group)
    add_confirm(add, "data_error_log", "Error Log", done_word="Done", parent=data_group)

    elec_group = add("electrical_check", field_label="Electrical Checking", field_type="group",
                     required=True)
    add_confirm(add, "elec_dial_illumination", "Dial Illumination (3 Phase/Conv.)",
                done_word="Illuminated", parent=elec_group)
    add_confirm(add, "elec_keypad_illumination", "Key-Pad Working Illumination (3 Phase/Conv.)",
                done_word="Working", parent=elec_group)
    add_confirm(add, "elec_config_illumination", "Configuration Illumination (3 Phase/Conv.)",
                done_word="OK", parent=elec_group)
    if conv_only:
        add_confirm(add, "elec_costing_illumination", "Costing Illumination (Conv.)",
                    done_word="Working", parent=elec_group)
        add_confirm(add, "elec_braking_illumination", "Braking Illumination (Conv.)",
                    done_word="Working", parent=elec_group)
        add_confirm(add, "elec_energy_meter_illumination", "Energy Meter Working Illumination (Conv.)",
                    done_word="Working as per energy chart", parent=elec_group)

    add_confirm(add, "functional_test_rpm_calibration",
                "Functional Test - Testing at 20 KMPH Interval and Calibration w.r.t. RPM "
                "(Refer Speed v/s RPM Chart)", done_word="Done",
                authority_reference="SMI 289-5.10.2.4; error <= 1.5% RDSO spec ELRS/SPM/0002 (Rev.2)")
    add_numeric(add, "wheel_dia_setting", "Wheel Dia. Setting", None, unit="mm", decimal_precision=0,
                required=True, authority_reference="As per wheel dia.")

    pg_group = add("pg_check", field_label="Check of PG", field_type="group", required=True,
                   authority_reference="SMI 289-5.10.1.2/3")
    add_confirm(add, "pg_cable_condition", "Cable Condition", done_word="Tight", parent=pg_group)
    add_confirm(add, "pg_speed_sensors", "Speed Sensors", parent=pg_group)
    add_confirm(add, "pg_bearing_condition", "Bearing Condition, Shaft's Free Movement, Proper "
                "Functioning of Bearing", parent=pg_group)
    add_confirm(add, "pg_coded_disc", "Coded Disc", parent=pg_group)
    add_confirm(add, "pg_driving_fork_inspection", "Inspection of Driving Fork for Any Damage",
                done_word="No damage", negative_word="Damage found", parent=pg_group)

    add_confirm(add, "cables_intact", "All Cables Should Be Intact", done_word="Intact")
    add_confirm(add, "overheating_ptc_ctc_junction",
                "Check for Any Damage and Overheating for PTC/CTC/SSCU/Junction Boxes",
                done_word="No damage/overheating", negative_word="Damage/overheating found",
                authority_reference="SMI 289-5.10.1.1")
    add_confirm(add, "cutoff_speed_functional_15kmph",
                "Ensure Functionality of Cut Off Speed at 15 Km/h Circuit as per MS 492",
                done_word="Ensured")

    rdso_group = add("rdso_smi_implementation", field_label="RDSO SMI Implementation",
                     field_type="group", required=False)
    add_confirm(add, "smi232_pg_reliability", "SMI 232 - Improve Reliability of PG (Do Not Hold "
                "PG Cable While Moving It From One Place to Another)", done_word="Done",
                parent=rdso_group)
    add_confirm(add, "smi289_general_checking_1",
                "General Checking as per SMI 289-5.10.1.6 (Fitment/Tightness of Screws/Bolts/"
                "Connectors)", done_word="Done", parent=rdso_group)
    add_confirm(add, "smi289_general_checking_2",
                "General Checking as per SMI 289-5.10.1.8 (Confirm Accuracy of Previously Set "
                "Parameters)", done_word="Done", parent=rdso_group)
    add_confirm(add, "gps_time_setting", "Time Setting as per GPS", done_word="Done",
                authority_reference="SMI 302", parent=rdso_group)

    must_change = add("must_change_items", field_label="Must Change Items", field_type="group",
                      required=False)
    for key, label in [
        ("aoh_kit_aal_telpro", "AOH Replacement Kit - AAL's TELPRO ELM"),
        ("ioh_kit_aal_telpro", "IOH Replacement Kit - AAL's TELPRO ELM"),
        ("aoh_kit_medha_mrt", "AOH Replacement Kit - Medha's MRT 922M"),
        ("ioh_kit_medha_mrt", "IOH Replacement Kit - Medha's MRT 922M"),
        ("aoh_kit_laxven", "AOH Replacement Kit - Laxven's Lax E2/E3"),
        ("ioh_kit_laxven", "IOH Replacement Kit - Laxven's Lax E2/E3"),
        ("pulse_generator_kit", "AOH/IOH Kit for Pulse Generator"),
    ]:
        add(key, parent=must_change, field_label=label, field_type="select",
            options="Replaced, Not Replaced", required=False, standard_value="Replaced",
            negative_values="Not Replaced")

    add("remarks", field_label="Remarks", field_type="textarea", required=False)
