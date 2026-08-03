"""
Module 36: seeds the M6-HR Conventional (WAG-5) checksheet template - an equipment-less,
section-wide template (no Equipment record, no SectionEquipmentMap row - template selection
depends only on section_id + locomotive technology).

Run once: `venv/bin/python scripts/seed_m6hr_conventional_template.py`

Source: "M6 HR AOH/IOH SCHEDULE ACTIVITIES WAG-4/7" (filename "M6-HR Conventional.pdf").

Per Module 36's explicit instruction, "Super Check Observation & Booking Attending" (index item
11) physically appears mid-document in the source scan (sandwiched between two halves of Fire
Prevention Measures) but is implemented here as the LAST section of the template - it is the
final add() call in build(), after every other section including Safety Items and Remarks.
Index items 1 (History Booking & Section Observations), 13 (List of Works Through Out Sourcing)
and 17 (Milli-Volt Drop Test) were listed in the source document's own index but their content
pages were not included in the supplied scan, so they are not implemented (nothing to
authoritatively transcribe); index item 15 ("Remarks if Any") IS implemented, as the generic
optional Remarks field.
"""
from _section_template_helpers import run_seed, add_final_remarks


def add_select(add, key, label, options, negative=None, standard=None, authority=None, required=True):
    return add(
        key, field_label=label, field_type="select", options=", ".join(options), required=required,
        standard_value=standard, authority_reference=authority, negative_values=negative,
    )


def add_confirm(add, key, label, authority=None):
    """The generic "checked/confirmed" pattern used by the many single-outcome guideline-style
    checkpoints in this document (Special Check Points, Fire Prevention Measures, Equipping,
    Visual Checking) where the sample sheet's own remark is just a confirmation word."""
    return add_select(add, key, label, ["Confirmed", "Not Confirmed"], negative="Not Confirmed",
                      authority=authority)


def build(add):
    # --- Special Check Points ---
    add_select(add, "special_dbr_qlm_cable_continuity", "DBR CKT. Standardization to Check, QLM "
        "Cable Continuity to Check", ["Checked", "Not Checked"], negative="Not Checked")
    add_confirm(add, "special_roof_shunt", "Roof Shunt to Be Check")
    add_confirm(add, "special_dbr_rps_rope", "DBR & RPS Rope to Check")
    add_confirm(add, "special_tk_panel_phase_separation", "TK Panel Phase Separation and Colour "
        "Code to Be Check")
    add_select(add, "special_xmer_rsi_terminal_lug_overheating", "X'mer to RSI Terminal Lug to "
        "Check for Any Over Heating, Decolourise Noticed", ["No Overheating", "Overheating Found"],
        negative="Overheating Found")
    add_confirm(add, "special_roof_flexible_shunt_vcb", "On Roof Flexible Shunt of VCB, "
        "Lightening Arrestor, Main Bushing to Check")
    add_select(add, "special_lt_cables_rubbing_touching", "Rubbing / Touching of LT Cables at "
        "Various Location", ["Rubber Packing Provided", "Not Provided"], negative="Not Provided")
    add_select(add, "special_sb_panel_overheating_cleaning", "Check SB Panel for Over Heating, "
        "Rubbing, Touching and Cleaning; Power Cable SB Separator to Check",
        ["Cleaned & Checked", "Not Done"], negative="Not Done")
    add_select(add, "special_xmer_oil_leakage", "X'mer Insulating Oil Leakage to Check",
        ["No Leakage", "Leakage"], negative="Leakage")
    add_confirm(add, "special_ht5_jali_clamping_vibration", "HT5 Jali Clamping, Vibration, "
        "Support to Check")
    add_select(add, "special_ht5_area_cab_corridor_cleaning", "Cleaning to Check in HT5 Area, "
        "Cab & Corridoor", ["Cleaned", "Not Cleaned"], negative="Not Cleaned")

    # --- Stripping of the Items ---
    stripping_items = [
        ("stripping_roof_bar_shunts", "Removal of Roof Bar, Roof Shunts"),
        ("stripping_roof_dj_bv_box", "Removal of All Roof, DJ, BV Box"),
        ("stripping_side_body_filter", "Removal of Side Body Filter"),
        ("stripping_sl_connection_jali_cover", "Removal of SL 1,2 Connection & Jali Cover"),
        ("stripping_rps_dbr_atfex_transformer", "Removal of RPS, DBR, ATFEX, Transformer Connection"),
    ]
    for key, label in stripping_items:
        add_select(add, key, label, ["Removed", "Not Removed"], negative="Not Removed")
    add_select(add, "stripping_transformer_oil_radiator", "Transformer Oil Draining & Removal of Radiator",
        ["Drained & Removed", "Not Done"], negative="Not Done")
    add_select(add, "stripping_roof_gaskets", "Removal of All Roof Gaskets",
        ["Removed", "Not Removed"], negative="Not Removed")
    add_select(add, "stripping_foot_plate_ioh", "Removal of Foot Plate (Only in IOH Sch.)",
        ["Removed", "N/A (IOH only)", "Not Removed"], negative="Not Removed")

    # --- Dust Blowing ---
    dust_locations = [
        ("dust_sb_cab1_pc1_mp1_mcp_pv_mvmt1", "SB CAB-1, SB PC-1, Below MP1, Near MCP/PV & MVMT1"),
        ("dust_ht1_2", "HT1-2"),
        ("dust_ht5_smgr_transformer_connection", "HT5, Below SMGR, Transformer Connection"),
        ("dust_rsi1_2_chba_mvmt2_tk_panel", "RSI1-2, CHBA & MVMT2 Bottom, TK Panel"),
        ("dust_sb_cab2_pc2_mp2", "SB CAB-2, SB PC-2, Below MP2"),
        ("dust_car_body_filter", "Car Body Filter"),
    ]
    for key, label in dust_locations:
        add_select(add, key, label, ["Done", "Not Done"], negative="Not Done")

    # --- Modification ---
    modification_items = [
        ("mod_millivolt_sb_fitting", "Millivolt SB Fitting to Check"),
        ("mod_dbr_control_ckt", "DBR Control Ckt. Modification to Check"),
        ("mod_ctf3_c145_branch", "CTF3 I/L on C145 Branch (Mod. No. 330)"),
        ("mod_ls_c145", "LS C-145 Modification to Be Done"),
        ("mod_cab_heater_ccra", "Cab Heater Modification (CCRA)"),
        ("mod_multiple_coupler_connection", "Multiple Coupler Connection to Check"),
        ("mod_h01_h31_cable", "H-01 Cable Separation & H31 Cable to Check"),
        ("mod_vcb_air_pipe", "VCB Air Pipe to Replace in Steel Braided"),
        ("mod_lsol_ls_group_cabling", "LSOL, LS Group Cabling to Check"),
        ("mod_ccpt_16amp", "CCPT 16 AMP to Be Convert From 10 AMP"),
        ("mod_r118_c118_safety_plate", "R118/C118 Safety Plate to Check"),
        ("mod_ccvcd_provide", "CCVCD to Be Provide"),
        ("mod_mpcs_hmcs_qd_bl_zpt", "In MPCS Loco HMCS1,2, QD1,2, BL1,2 & ZPT1,2 Mod. to Be "
            "Check (Mod. No. 386, 384)"),
        ("mod_tk_panel_standardization", "TK Panel Standardization to Check"),
        ("mod_xmer_rsi_cable_transposition", "Transposition of X'mer to RSI1,2 Cable to Check",
            "SMI-237"),
    ]
    for item in modification_items:
        key, label = item[0], item[1]
        authority = item[2] if len(item) > 2 else None
        add(key, field_label=label, field_type="text", required=False, authority_reference=authority)

    # --- Schedule Repair Works by M6 HR ---
    add_select(add, "repair_main_door_gasket_slot", "Main Door - Gasket to Be Replaced & Slot to "
        "Be Check", ["Checked", "Not Checked"], negative="Not Checked")
    add_confirm(add, "repair_window_ht_compartment_locks", "Window, HT Compartment Locks to Check")
    add_select(add, "repair_cp123_tray_cleaning", "CP1-2-3, Tray Cleaning to Done",
        ["Cleaned", "Not Cleaned"], negative="Not Cleaned")
    add_confirm(add, "repair_mvmt_stand_fbolt_threaded_block", "MVMT1-2 Stand F/Bolt, Threaded "
        "Block & Duct to Check")
    add_select(add, "repair_carbody_filter_mastic_gasketing", "Car Body Filter Mastic Compound "
        "Cleaning & Gasketing to Be Done", ["Done", "Not Done"], negative="Not Done")
    add_select(add, "repair_roof_gasketing", "Roof Gasketing to Be Done", ["Done", "Not Done"],
        negative="Not Done")
    add_select(add, "repair_cable_checking_below_footplate_ioh", "Cable Checking Below Footplate "
        "(Only in IOH Sch.)", ["Checked", "N/A (IOH only)", "Not Checked"], negative="Not Checked")
    add_select(add, "repair_mastic_compound_roof_dj_bv_box", "Cleaning of Mastic Compound & "
        "Repairing of Roof Near DJ, BV Box & Gasketing to Be Done", ["Done", "Not Done"],
        negative="Not Done")
    add_confirm(add, "repair_jali_clamps_corridor_panel_locks", "All Jali, Supporting Clamps, All "
        "Corridoor and Panel Door Locks, Hinges to Check")
    add_select(add, "repair_tm_cable_condition_lug_size", "TM Cable Condition & Lug Size to Check",
        ["Checked & Noted", "Not Checked"], negative="Not Checked")

    # --- Must Change Items ---
    must_change_group = add("m6hr_must_change_items", field_label="Must Change Items",
                            field_type="group", required=False)
    must_change_rows = [
        ("mc_main_door_gasket", "Main Door Gasket", "PL 23.98.1921 / 20 M/LOCO / IOH-AOH"),
        ("mc_roof_gasket", "Roof Gasket", "PL 25.97.0707 / 05 Roll/LOCO / IOH-AOH"),
        ("mc_carbody_filter", "Carbody Filter", "PL 23.98.1581 / 48 MT/LOCO / IOH-AOH"),
        ("mc_dj_base_gasket", "DJ Base Gasket", "PL 23.25.7416 / 01/LOCO / IOH-AOH"),
        ("mc_bv_box_gasket", "BV Box Gasket", "PL 25.97.1360 / 01 NO/LOCO / IOH-AOH"),
        ("mc_radiator_gasket", "Radiator Gasket", "PL 23.98.2160 / 01 SET/LOCO / AOH-IOH"),
        ("mc_rdj_pipe", "RDJ Pipe", "PL NS ITEMS / 01 NO/LOCO / IOH-AOH"),
        ("mc_mph_radiator_flange_gasket", "MPH to Radiator Flange Joint Gasket", "PL NS ITEMS / 04 SET / AOH-IOH"),
        ("mc_rdj_copper_washer", "RDJ Copper Washer", "PL NS ITEMS / 02 NO / AOH-IOH"),
        ("mc_rubber_sheet_foot_plate", "Rubber Sheet of Foot Plate", "PL 75.32.2894 / 25 KG / IOH"),
        ("mc_hl_reflector", "H/L Reflector", "PL 23.98.1180 / 04 NO / AOH-IOH"),
        ("mc_rubber_block_roof_fitting", "Rubber Block for Roof Fitting", "PL NS / 50 NOS / AOH-IOH"),
    ]
    for key, label, ref in must_change_rows:
        add(key, parent=must_change_group, field_label=label, field_type="select",
            options="Changed, Serviceable (Not Replaced), N/A (Not this schedule)", required=True,
            authority_reference=ref)

    # --- Loco Checking by Different Section ---
    loco_checking_rows = [
        ("loco_check_ep_contactor_interlock_archchute", "Remaining EP Contactor With Interlock "
            "Box & Archchute", "Section M-1,8"),
        ("loco_check_rs_elements", "All RS Elements", "Section M-1,8"),
        ("loco_check_sl_hood_sj_bl_padel", "SL & Its Hood, SJ, BL1&2, Padel Switches", "Section M-1,8"),
        ("loco_check_ltba_battery_box", "LTBA, Battery Box", "Section M-2,9"),
        ("loco_check_rsi1_2", "RSI1-2", "Section M-2,9"),
        ("loco_check_ac_et_capacitor_qop_qoa", "AC ET Panel, Capacitor Panel, QOP/QOA Resistance", "Section M-2,9"),
        ("loco_check_vs_diodes", "All VS Diodes", "Section M-2,9"),
        ("loco_check_main_transformer", "Main Transformer", "Section M-1,8"),
        ("loco_check_body_patch_sand_box_ba_clamp", "Patch Work of Body & Sand Box, BA1,2 "
            "Support Clamp", "Section M/SHOP"),
        ("loco_check_rotating_switches_hvmt_hvrh_hmcs", "Remaining Rotating Switch HVMT-1,2, "
            "HVRH, HMCS1,2, HCP, HBA, HUBA, HQPDJ", "Section M-1,8"),
    ]
    for key, label, section_ref in loco_checking_rows:
        add_select(add, key, label, ["Checked by Related Section", "Not Checked"],
            negative="Not Checked", authority=section_ref)

    # --- Equipping ---
    equipping_fitted_rows = [
        ("equip_roof_gaskets", "Fitment of All Roof Gaskets"),
        ("equip_dj_bv_box_rps_radiator", "Fitment of DJ, BV Box, RPS, Radiator"),
        ("equip_sl_hood_connection", "Fitment of SL1,2, Hood & Connection"),
        ("equip_dbr_atfex_transformer_connection", "Fitment of DBR, ATFEX, Transformer Connection"),
        ("equip_side_body_filter", "Fitment of Side Body Filter"),
        ("equip_foot_plate", "Fitment of Foot Plate"),
        ("equip_roof_1245", "Fitment of Roof No. 1,2,4,5"),
        ("equip_ht5_roof", "Fitment of HT5 Roof"),
    ]
    for key, label in equipping_fitted_rows:
        add_select(add, key, label, ["Fitted", "Not Fitted"], negative="Not Fitted")
    add_select(add, "equip_roof_bar_insulator_shunt_paint", "Fitment of All Roof Bar, Roof "
        "Insulator Cleaning, Roof Shunt, ET, Anti-Tracking Paint Applied on Roof & Insulator",
        ["Cleaned & Fitted", "Not Done"], negative="Not Done")
    add_select(add, "equip_xmer_oil_filtration", "X'mer Oil Filtration", ["Done", "Not Done"],
        negative="Not Done")
    add_select(add, "equip_tm_cable_checking", "TM Cable Checking", ["Checked", "Not Checked"],
        negative="Not Checked")
    add_select(add, "equip_cleaning_sb_ba_compartment", "Cleaning, SB Checking, Back Cover "
        "Fitting of BA1,2 Compartment", ["Cleaned & Fitted", "Not Done"], negative="Not Done")

    # --- Visual Checking ---
    add_select(add, "visual_sb_checking", "SB Checking - SB CAB1-2, SB BD, SB PC1-2, SB "
        "Pneumatic, Fuse Board", ["Done", "Not Done"], negative="Not Done")
    add_select(add, "visual_ht5_cleaning_checking_transformer", "HT5 Cleaning, Checking & "
        "Transformer Connection - Transformer, ET Panel, Capacitor Panel, SB (MPH), LSGRR/P, GR "
        "Transformer Area & Oil Cleaning, SB Checking", ["Done", "Not Done"], negative="Not Done")
    add_select(add, "visual_ht1_2_checking", "HT1-2 Checking - Bus Bar, Foundation, Power & "
        "Control Cable of EPC, Insulator & Separator Checking, SJ Connection, and Foundation Bolt "
        "Tightness & Back Cover Fitting", ["Checked & Fitted", "Not Done"], negative="Not Done")
    add_select(add, "visual_roof_checking", "Roof Checking - Roof Bar, Roof Shunt, ET Connection "
        "Tightness & Insulator Cleaning", ["Done", "Not Done"], negative="Not Done")

    # --- Fire Prevention Measures ---
    fire_prevention_items = [
        ("fire_thin_walled_cables", "Use of Thin Walled Cables as Per RDSO's Specifications Only "
            "if Require Changing"),
        ("fire_avoid_sharp_bends", "Avoid Sharp Bends While Laying Out or Replacing the Power, "
            "Auxiliary and Control Cables"),
        ("fire_avoid_joining_cables", "Avoid the Joining of Cables Even for Emergency Operations "
            "for Short Duration; the Cable Lay Out Should Be in One Piece With End to End Having "
            "Proper Lugs"),
        ("fire_tm_connection_cable_ferrule", "The Ferrule of Traction Motor Connection Cables "
            "Should Be Checked During Every Disconnection of Traction Motor; Replacement of "
            "Ferrules Should Be Strictly Per the Size of Cables"),
        ("fire_tm_cable_not_under_tension", "Proper Care Should Be Given So That Traction Motor "
            "Cable Is Not Under Tension; Proper Supporting Cleats With Chain Arrangement With the "
            "Body Must Be Ensured"),
        ("fire_tfp_terminal_cables_rsi", "Check the Cables From TFP Terminal a3,a4,a5,a6 to RSI "
            "1&2 for Intact and Proper Condition (Change if Overheating Mark or Insulation "
            "Getting Brittle)"),
        ("fire_cable_cleats_srbgf", "The Cable Cleats Not to Be Opened or Loosened During Routine "
            "Maintenance Should Be Opened for Cleaning and Replaced With SRBGF, With Additional "
            "Neoprene Rubber Sheet Provision During AOH/IOH"),
        ("fire_sl_cable_connections_ic", "All the Cable Connections of SL Should Be Thoroughly "
            "Checked During IC Inspection and During AOH of Locomotive by Sheds"),
        ("fire_control_circuit_fuse_rating", "All the Fuse in the Control Circuit Should Be of "
            "Appropriate and Specified Rating Only"),
        ("fire_fuse_base_connections", "During AOH/IOH of Locomotive the Condition of Fuse Base "
            "and Their Connections Should Be Checked"),
        ("fire_transformer_earthing_a0", "Transformer Earthing Connection (A0) With the "
            "Locomotive Body Must Be Ensured Whenever Transformer Is Lifted and Fitted Back"),
        ("fire_lsol_circuit_functional", "LSOL Circuit Should Be Maintained in Proper Functional "
            "Order in All the WAG-5 Locomotives"),
        ("fire_tk_panel_phase_separation", "The Separation of Phases in TK Panel With a "
            "Provision of Glass Fibre Separators"),
        ("fire_side_body_filter_pressurized_cleaning", "Cleaning of Side Body Filter With "
            "Pressurized Blowing Must Be Done During Every Inspection of Locomotives"),
        ("fire_side_body_filter_condition_maintained", "The Condition of Side Body Filters "
            "Should Be Maintained and Replacement Should Be Planned as and When Required"),
        ("fire_cable_entry_points_blocked", "All Locomotive Opening at the Cable Entry Points or "
            "Otherwise Must Be Blocked by Suitable Rubber Materials"),
        ("fire_roof_gaskets_changed_ioh", "All Roof Gaskets Must Be Changed During IOH of the "
            "Locomotives"),
        ("fire_central_hood_rubber_gasket", "The Rubber Gasket for Central Hood Should Be Checked "
            "Thoroughly With Respect to Its Condition as Well as Proper Placement During Removal "
            "of Central Hood Along With DJ/VCB"),
        ("fire_water_leakage_testing", "Do Water Leakage Testing After AOH/IOH"),
        ("fire_apertures_blocked_gasket_sealing", "All Apertures and Opening From Doors, Sky "
            "Light Glasses Should Be Blocked by Proper Fitment of Rubber Gasket and Sealing "
            "Compound"),
        ("fire_footplates_secured", "Proper Securing of Footplates in Corridors and HT "
            "Compartment Area Must Be Ensured With All Fasteners Intact"),
        ("fire_mph_mvsl_mvrh_mvsi_rotation", "The Rotation of MPH, MVSL, MVRH & MVSI Should Be "
            "Carefully Checked and Ensured Whenever the Auxiliary Machines Are Changed or "
            "Disconnected"),
        ("fire_mph_oil_leakage", "Even a Slight Oil Leakage From MPH Should Not Be Permitted for "
            "Long in Service"),
        ("fire_oil_accumulation_ba_panel", "Accumulation of Oil Should Be Watched Under BA Panel "
            "and Suitable Remedial Measure Must Be Taken"),
        ("fire_muck_removal_cable_ducts", "The Removal of Muck and Foreign Materials From the "
            "Cable Carrying Ducts, Junction Box in the Under Frame Should Be Ensured During AOH, "
            "IOH and During Lifting of Locomotive"),
        ("fire_roof_bars_pantograph_shunts", "Checking of Roof Bars, Its Fixation Arrangement of "
            "Pantograph Shunts Should Be Checked During Every Inspection and Replacement Should "
            "Be Done, if Required, Immediately"),
        ("fire_panto_roof_insulators_cleaning", "Cleaning of Panto Foot Insulators, Roof Line "
            "Insulators, Insulators of DJ/VCB, Lightening Arrestor, Bushing Portion on the Roof "
            "Should Be Kept in Cleaned Condition During Every Inspection"),
    ]
    for key, label in fire_prevention_items:
        add_confirm(add, key, label)

    # --- Final Testing: Electrical Testing ---
    add("final_testing_battery_voltage", field_label="Battery Voltage", field_type="numeric_range",
        required=False, unit="V", min_value=100.0, max_value=110.0, decimal_precision=1,
        standard_value="100 to 110 V")
    add("final_testing_battery_voltage_cpa_on", field_label="Battery Voltage While CPA 'ON'",
        field_type="number", required=False, unit="V")
    add("final_testing_chba_voltage_hba_off", field_label="CHBA Voltage While HBA 'OFF'",
        field_type="number", required=False, unit="V")
    add("final_testing_charging_current_hba_on", field_label="Charging Current While HBA 'ON'",
        field_type="number", required=False, unit="Amp")

    def add_cab_pair(key, label, options="Working, Not Working", negative="Not Working"):
        group = add(key, field_label=label, field_type="group", required=False)
        for cab in ("CAB-1", "CAB-2"):
            add(f"{key}_{cab.lower().replace('-', '')}", parent=group, field_label=cab,
                field_type="select", options=options, required=False, negative_values=negative)
        return group

    add_cab_pair("final_testing_hl_working", "Working of H/L")
    add_cab_pair("final_testing_fl_working", "Working of F/L")
    add_cab_pair("final_testing_ml_working", "Working of M/L")
    add_cab_pair("final_testing_cab_light_working", "Working of Cab Light")
    add_cab_pair("final_testing_signalling_lamps_working", "Working of Signalling Lamps")
    add_cab_pair("final_testing_bl_light_working", "Working of BL Light")
    add_cab_pair("final_testing_cab_fan_working", "Working of Cab Fan")
    add_cab_pair("final_testing_cab_heater_working", "Working of Cab Heater")
    add_cab_pair("final_testing_notch_repeaters_working", "Working of Notch Repeaters")
    add_cab_pair("final_testing_mp_eec_working", "Working of MP/EEC")

    meters_group = add("final_testing_various_meters_working", field_label="Working of Various Meters",
                       field_type="group", required=False)
    add("final_testing_meters_a4_u5_u6_ua1", parent=meters_group, field_label="A4, U5, U6, UA-1",
        field_type="select", options="Working, Not Working", required=False, negative_values="Not Working")
    add("final_testing_meters_a3_u1_u2_ua2", parent=meters_group, field_label="A3, U1, U2, UA-2",
        field_type="select", options="Working, Not Working", required=False, negative_values="Not Working")

    add_cab_pair("final_testing_various_pressure_working", "Working of Various Pressure")
    add("final_testing_em_contactor", field_label="Working and Condition of EM Contactor",
        field_type="select", options="Working, Not Working", required=False, negative_values="Not Working")

    line_contactor_group = add("final_testing_line_contactor_sequence", field_label="Working and "
        "Sequence of Line Contactor Through", field_type="group", required=False)
    for label in ("HVSI-1", "HVSI-2", "HMCS-1", "HMCS-2"):
        add(f"final_testing_line_contactor_{label.lower().replace('-', '_')}", parent=line_contactor_group,
            field_label=label, field_type="select", options="Working, Not Working", required=False,
            negative_values="Not Working")

    add("final_testing_shunting_contactors", field_label="Working of Shunting Contactors",
        field_type="select", options="Working, Not Working", required=False, negative_values="Not Working")

    aux_motors_group = add("final_testing_aux_motors_working_direction", field_label="Working and "
        "Direction of All Auxiliary Motors", field_type="group", required=False)
    for label in ("MPH", "MVSI 1&2", "MVSL 1&2", "MVRH", "MVMT 1&2", "MCP 1,2&3"):
        key = "final_testing_aux_" + label.lower().replace(" ", "_").replace("&", "and").replace(",", "_")
        add(key, parent=aux_motors_group, field_label=label, field_type="select",
            options="Working, Not Working", required=False, negative_values="Not Working")

    add("final_testing_tm_individual_working_direction", field_label="Individual Working and "
        "Direction of All TM", field_type="select", options="Working, Not Working", required=False,
        negative_values="Not Working")

    rgcp_group = add("final_testing_rgcp_setting", field_label="RGCP Setting", field_type="group",
                     required=False, unit="kg/cm2")
    add("final_testing_rgcp_cut_in", parent=rgcp_group, field_label="Cut In", field_type="number",
        required=False, unit="kg/cm2")
    add("final_testing_rgcp_cut_out", parent=rgcp_group, field_label="Cut Out", field_type="number",
        required=False, unit="kg/cm2")

    regression_group = add("final_testing_regression_q20", field_label="Regression by Q20",
                           field_type="group", required=False)
    add("final_testing_regression_lt", parent=regression_group, field_label="LT", field_type="select",
        options="Checked, Not Checked", required=False, negative_values="Not Checked")
    add("final_testing_regression_ht", parent=regression_group, field_label="HT", field_type="select",
        options="Checked, Not Checked", required=False, negative_values="Not Checked")

    target_relay_group = add("final_testing_target_relay_working", field_label="Working of Target Relay",
                             field_type="group", required=False)
    for label in ("QOP-1", "HQOP-1", "QOP-2", "HQOP-2", "QOA", "HQOA"):
        add(f"final_testing_target_relay_{label.lower().replace('-', '_')}", parent=target_relay_group,
            field_label=label, field_type="select", options="Working, Not Working", required=False,
            negative_values="Not Working")

    air_flow_relay_group = add("final_testing_air_flow_relay_working", field_label="Working of "
        "Air Flow Relay", field_type="group", required=False)
    for label in ("QPH", "QVSI 1&2", "QVSL 1&2", "QVRH", "QVMT 1&2"):
        key = "final_testing_air_flow_" + label.lower().replace(" ", "_").replace("&", "and")
        add(key, parent=air_flow_relay_group, field_label=label, field_type="select",
            options="Working, Not Working", required=False, negative_values="Not Working")

    for key, label in [
        ("final_testing_q46_relay", "Working of Q-46 Relay"),
        ("final_testing_q48_qd", "Working of Q-48 Through QD1&2"),
        ("final_testing_bpqd_hpar_hq51", "Working of BPQD/HPAR/HQ51"),
        ("final_testing_bp1dj_bp2dj", "Working of BP1DJ & BP2DJ"),
    ]:
        add(key, field_label=label, field_type="select", options="Working, Not Working",
            required=False, negative_values="Not Working")

    add("final_testing_relays_sealing", field_label="Sealing of All Relays", field_type="select",
        options="Sealed, Not Sealed", required=False, negative_values="Not Sealed")
    add("final_testing_ctfs_working_condition", field_label="Working & Condition of CTFs",
        field_type="select", options="Working, Not Working", required=False, negative_values="Not Working")
    add("final_testing_reversers_working_condition", field_label="Working & Condition of Reversers",
        field_type="select", options="Working, Not Working", required=False, negative_values="Not Working")
    add("final_testing_negative_bond_checking", field_label="Checking of Negative Bond",
        field_type="text", required=False)
    add("final_testing_dbr_working", field_label="Working of DBR", field_type="select",
        options="Working, Not Working", required=False, negative_values="Not Working")

    smgr_group = add("final_testing_smgr_working", field_label="Working of SMGR", field_type="group",
                     required=False)
    add("final_testing_smgr_pressure_normal", parent=smgr_group, field_label="Pressure in Normal Position",
        field_type="number", required=False, unit="kg/cm2")
    add("final_testing_smgr_pressure_drop_notches", parent=smgr_group, field_label="Pressure Drop by Notches",
        field_type="number", required=False, unit="kg/cm2")
    add("final_testing_smgr_progression_time", parent=smgr_group, field_label="Progression Time",
        field_type="number", required=False, unit="sec")
    add("final_testing_smgr_regression_time", parent=smgr_group, field_label="Regression Time",
        field_type="number", required=False, unit="sec")
    add("final_testing_smgr_transformer_oil_level", parent=smgr_group, field_label="Transformer Oil Level",
        field_type="text", required=False)
    add("final_testing_smgr_gr_oil_level", parent=smgr_group, field_label="GR Oil Level",
        field_type="text", required=False)
    add("final_testing_smgr_phgr_working", parent=smgr_group, field_label="Working of PHGR",
        field_type="select", options="Working, Not Working", required=False, negative_values="Not Working")

    add_cab_pair("final_testing_brake_power_checking", "Checking of Brake Power",
        options="Checked, Not Checked", negative="Not Checked")
    add("final_testing_fire_extinguisher", field_label="Fire Extinguisher", field_type="select",
        options="Intact, Not Intact", required=False, standard_value="04 Nos intact with more than 60 days expiry",
        negative_values="Not Intact")
    add("final_testing_vcd_working", field_label="Working of VCD", field_type="select",
        options="Working, Not Working", required=False, negative_values="Not Working")
    add("final_testing_acp_working", field_label="Working of ACP", field_type="select",
        options="Working, Not Working", required=False, negative_values="Not Working")
    add("final_testing_zqwc_working_10_notches", field_label="ZQWC Working Till 10 Notches",
        field_type="select", options="Working, Not Working", required=False, negative_values="Not Working")

    bpems_group = add("final_testing_bpems_working", field_label="BPEMS Working", field_type="group",
                      required=False)
    add("final_testing_bpems_lt", parent=bpems_group, field_label="LT", field_type="select",
        options="Working, Not Working", required=False, negative_values="Not Working")
    add("final_testing_bpems_ht", parent=bpems_group, field_label="HT", field_type="select",
        options="Working, Not Working", required=False, negative_values="Not Working")

    add("final_testing_hravt_switch_working", field_label="HRAVT Switch Working", field_type="select",
        options="Working, Not Working", required=False, negative_values="Not Working")
    add_cab_pair("final_testing_cab_ac_working", "CAB AC Working")

    # --- Annexure-1 for TI-322 (MV Drop across 7 named contactors, reference 0-50 mV) ---
    annexure_group = add("final_testing_annexure1_ti322_mv_drop", field_label="Annexure-1 for "
        "TI-322 - MV Drop (B/W 0 to 50 mV)", field_type="group", required=False,
        standard_value="0-50 mV")
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
        key = "annexure_mv_drop_" + contactor.lower().replace(".", "_").replace("/", "_")
        add(key, parent=annexure_group, field_label=f"Contactor {contactor} ({location})",
            field_type="number", required=False, unit="mV",
            help_text=f"B/W Cable No. {cable_no}, Interlock 1-2, Condition: {condition}")

    # --- Safety Items: Provision of Safety Items ---
    safety_items = [
        ("safety_wooden_wedges", "Wooden Wedges", 4),
        ("safety_universal_coupling", "Universal Coupling", 1),
        ("safety_bp_hose", "BP Hose", 1),
        ("safety_fp_hose", "FP Hose", 1),
        ("safety_bp_fp_palm_coupling", "BP-FP Palm Coupling", "1+1"),
        ("safety_screw_coupling", "Screw Coupling", 1),
        ("safety_fire_extinguisher_qty", "Fire Extinguisher", 4),
        ("safety_log_book", "Log Book", 1),
        ("safety_spare_coupling", "Spare Coupling", 1),
        ("safety_u_clamp", "U' Clamp", 1),
    ]
    for key, label, qty in safety_items:
        add(key, field_label=label, field_type="number", required=False,
            standard_value=f"Qty: {qty}")
    spare_fuses_group = add("safety_spare_fuses", field_label="Spare Fuses", field_type="group",
                            required=False)
    add("safety_spare_fuses_35a", parent=spare_fuses_group, field_label="35 A", field_type="number",
        required=False, standard_value="Qty: 35 A")
    add("safety_spare_fuses_16a", parent=spare_fuses_group, field_label="16 A", field_type="number",
        required=False, standard_value="Qty: 16 A")
    add("safety_spare_fuses_6a", parent=spare_fuses_group, field_label="6 A", field_type="number",
        required=False, standard_value="Qty: 6 A")
    add("safety_coupling_hanging_clamps", field_label="Coupling Hanging Clamps", field_type="select",
        options="Both Sides, Not Both Sides", required=False, standard_value="Both Sides",
        negative_values="Not Both Sides")

    # --- Remarks (index item 15: "Remarks if Any") ---
    add_final_remarks(add)

    # --- Super Check Observation & Booking Attending (MUST be last - see module docstring) ---
    add("super_check_observation_booking_attending", field_label="Super Check Observation & "
        "Booking Attending", field_type="textarea", required=False,
        help_text="Record of Sr.No. / Booking / Remarks entries from the super-check inspection, if any.")


if __name__ == "__main__":
    run_seed(
        section_name="M6-HR", template_code="36", technology="CONVENTIONAL",
        template_name="Checksheet for M6-HR (Conventional)",
        description="M6-HR AOH/IOH Schedule Activities (WAG-4/7, Conventional) - equipment-less section-wide checksheet.",
        build_fn=build,
    )
