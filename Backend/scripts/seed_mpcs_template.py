"""
Module 46: seeds the M2-HR MPCS (Micro Processor based Control System, Conventional) checksheet
template.

Source: "MPCS check sheet.pdf" - TRS/ELS/BL/M2HR/Conv./MPCS/Check sheet/VIII, as per TC 142 Rev 1
& SMI 288 Rev 0. Despite its equipment_code carrying no "_Conv" suffix, the equipment's
section_equipment_map.technology column reads "Conventional" - confirmed directly from the
database rather than inferred from naming, per Module 46 instructions.
"""
from _m2hr_template_helpers import add_confirm, add_numeric, add_text, run_seed_paged


def build(add, set_page):
    add_text(add, "make", "Make", required=True)
    add_text(add, "equipment_sr_no", "Equipment Sr. No.", required=False)

    add("download_fault_data_record", field_label="Download Fault Data and Record Major "
        "Loggings; Check and Record Fault Logging History from Downloaded Data and Analyze",
        field_type="textarea", required=True,
        standard_value="There should be no fault messages; issue booking to PPIO if any fault is noticed")
    add_confirm(add, "driver_logbook_verification",
                "Verification of Driver Logbook: Verify Driver's Booking and Attend Bookings "
                "Related to MPCS Functionality", done_word="Normal", negative_word="Abnormal")
    add_confirm(add, "remote_monitoring_data_verification",
                "Verification of Remote Monitoring Data from Website for MPCS Ver.3 for Proper "
                "Working of Remote Monitoring Module", done_word="Recording", negative_word="Not Recording")

    main_unit = add("main_unit", field_label="A. Main Unit", field_type="group", required=True)
    add_confirm(add, "a1_visual_abnormality", "Visually Check if Any Abnormality", parent=main_unit)
    add_confirm(add, "a2_cabinet_clean", "Main Unit Cabinet to Be Cleaned by Vacuum Cleaner",
                done_word="Clean", parent=main_unit)
    add_confirm(add, "a3_bayonet_connectors_clean",
                "Clean the Bayonet Connectors Using Appropriate Connector Cleaner", done_word="Clean",
                parent=main_unit)
    add_confirm(add, "a4_dust_free_gasket",
                "Check and Ensure Dust-Free Environment in the Main Unit; Replace Gasket in IOH "
                "as per TC-142 Rev 1", done_word="Dust free", parent=main_unit)
    add_confirm(add, "a5_facia_thumbscrew_tightness",
                "Check the Proper Tightness of All Facia Fixing Thumbscrew of the Cards",
                done_word="Intact", parent=main_unit)
    add_confirm(add, "a6_bayonet_connector_tightness",
                "Check the Proper Tightness/Locking of Bayonet Connectors at Main Unit",
                done_word="Intact", parent=main_unit)
    add_confirm(add, "a7_mounting_bolts_tightness",
                "Check the Proper Tightness of Mounting Bolts of the Main Unit", done_word="Intact",
                parent=main_unit)

    display_unit = add("display_unit", field_label="B. Display Unit", field_type="group", required=True)
    add_confirm(add, "b1_physical_condition",
                "Check the Physical Condition of the Unit for Any Breakage and Condition of "
                "Indication Panel and Keypad", done_word="Intact", parent=display_unit)
    add_confirm(add, "b2_mounting_bolts_tight", "Check the Proper Tightness of Mounting Bolts of "
                "Display Unit", done_word="Tight", parent=display_unit)
    add_confirm(add, "b3_bayonet_connector_tight",
                "Check the Proper Tightness/Locking of Bayonet Connectors at Display Unit",
                done_word="Tight", parent=display_unit)
    add_confirm(add, "b4_display_operation_check",
                "Check Display Units in Both Cabs and Its Operation Through Menu Driven Keys",
                parent=display_unit)

    scu = add("signal_conditioning_unit", field_label="C. Signal Conditioning Unit (SCU)",
             field_type="group", required=True)
    add_confirm(add, "c1_mounting_bolts_tight", "Check the Proper Tightness of Mounting Bolts of "
                "SCU Box", done_word="Tight", parent=scu)
    add_confirm(add, "c2_connection_tightness", "Check Connection Tightness", done_word="Tight",
                parent=scu)
    add_confirm(add, "c3_bayonet_connector_tight", "Check the Proper Tightness/Locking of Bayonet "
                "Connectors of SCU", done_word="Tight", parent=scu)

    iscu = add("intelligent_signal_unit", field_label="D. Intelligent Signal Unit (ISCU)",
              field_type="group", required=True)
    add_confirm(add, "d1_mounting_bolts_tight", "Check the Proper Tightness of Mounting Bolts of "
                "ISCU", done_word="Tight", parent=iscu)
    add_confirm(add, "d2_connection_tightness", "Check All Connection Tightness", done_word="Tight",
                parent=iscu)
    add_confirm(add, "d3_bayonet_connector_tight", "Check the Proper Tightness/Locking of Bayonet "
                "Connectors at ISCU", done_word="Tight", parent=iscu)

    ct_group = add("ct_group", field_label="E. CT (1,2,3,4,5,6)", field_type="group", required=True)
    add_confirm(add, "e1_heating_mark_damage_check", "Visual Checking for Any Heating Mark/Damage",
                parent=ct_group)
    add_confirm(add, "e2_mounting_bolts_tight", "Check the Proper Tightness of Mounting Bolts of "
                "CTs", done_word="Tight", parent=ct_group)
    add_confirm(add, "e3_bayonet_connector_tight", "Check the Proper Tightness/Locking of Bayonet "
                "Connectors of CTs", done_word="Tight", parent=ct_group)

    antenna = add("antenna", field_label="F. Antenna", field_type="group", required=True)
    add_confirm(add, "f1_crack_damage_check",
                "Visual Checking of Antenna for Any Crack/Damage of Safety Cover", parent=antenna)
    add_confirm(add, "f2_mounting_bolts_tight", "Check the Proper Tightness of Mounting Bolts",
                done_word="Tight", parent=antenna)

    general = add("general", field_label="G. General", field_type="group", required=True)
    add_confirm(add, "g1_control_cable_termination_tight",
                "Check the Proper Tightness of Control Cable Termination on BD Panel",
                done_word="Tight", parent=general)
    add_confirm(add, "g2_equipment_earthing_intact", "Check That Equipment Earthing Is Intact",
                done_word="Intact", parent=general)
    add_confirm(add, "g3_rubber_gaskets_grommets",
                "All Rubber Gaskets and Grommets to Be Replaced as per SMI-288 Rev 0/TC142 Rev 1 "
                "(During IOH)", done_word="Intact", required=False, parent=general)
    add_confirm(add, "g4_rtc_battery_condition",
                "Check the Condition of the Real Time Clock (RTC) Battery and Replace It if "
                "Required Before Completion of Codal Life as per OEM", parent=general)
    add_confirm(add, "g5_lock_condition_check",
                "Check the Condition of Lock in Front Door of Main Control Panel and Replace if "
                "Required", parent=general)

    g6 = add("pulse_wheel_dia_setting", field_label="G6. Setting of Number of Pulse/Revolution and "
             "Wheel Diameter with MPCS Version-3 for Correct Indication of Speed",
             field_type="group", required=True, authority_reference="TC-119 Rev.1")
    add("g6_spm_make", parent=g6, field_label="SPM Make", field_type="select",
        options="Medha, AAL, Laxven, MR", required=True)
    add_numeric(add, "g6_rpm_set", "RPM Set", "Medha 60, AAL 200, Laxven 30, MR 60",
                decimal_precision=0, required=True, parent=g6)

    add_confirm(add, "g7_time_match_mpcs_gps",
                "Time Matches MPCS Digital Clock with Control Office Clock During Every "
                "Inspection", done_word="Matched as per GPS", authority_reference="TC 142 Rev 1",
                parent=general)

    add("modifications", field_label="Modifications, if any", field_type="textarea", required=False)
    add("remarks", field_label="Remarks", field_type="textarea", required=False)


if __name__ == "__main__":
    run_seed_paged(
        equipment_code="MPCS",
        template_code="M2HR_MPCS_CONV",
        technology="CONVENTIONAL",
        template_name="Check Sheet for MPCS Maintenance",
        description="M2-HR: MPCS (Micro Processor based Control System) checksheet for "
                     "Conventional locomotives.",
        build_fn=build,
    )
