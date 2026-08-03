"""
Module 43: seeds the TM-Conv (TM - Traction Motor Conventional, Conventional locomotives, M35-TM
section) checksheet template.

Run once: `venv/bin/python scripts/seed_tm_assembling_conv_template.py`

Source: "FR/TM/AC/09 - Assembling of Traction Motor" (Locomotive Care Centre Ratlam, Western
Railway), the largest and final assembly stage: 35 activities (rocker/armature/bearing assembly,
brush holder-commutator clearance, light-run temperature-rise test - a genuine per-interval,
per-direction, per-bearing grid, preserved at full granularity - shock pulse analyzer readings,
commutator ovality, pinion selection/fitment with three gear-ratio 'K' value standards), a 15-item
Must Change Items parts log, an 8-item post-overhaul checklist, and an 11-row bolt tightening
torque reference table.

Per the module's "Do NOT create fields for Loco Number/Technician/Supervisor Name/Signature"
rule, the sheet's own "TCN Name"/"Sign of TCN"/"Signature of the Technician"/"Signature of
JE/SSE TM" lines and the per-task technician-name/signature columns are intentionally not
modelled - only the underlying work-done confirmation is kept.

No `maintenance_type` is set (stays NULL) - see seed_rocker_brush_holder_conv_template.py's
docstring for why this keeps the Android app's TM Number/GC-Overhaul UI from triggering for
Conventional equipment (this module's whole point is that Conventional TM has no GC/Overhaul
split at all, unlike the existing 3-Phase "TM- 3Ph" equipment).
"""
from _aux_template_helpers import add_final_remarks, run_seed

MUST_CHANGE_ITEMS = [
    ("carbon_brush", "Carbon Brush", "25972108"),
    ("inspection_cover_gasket", "Inspection Cover Gasket", "25973046"),
    ("terminal_packing", "Packing for Terminal", "25974038"),
    ("spring_washer_6mm", "Spring Washer 6mm", "23359456"),
    ("spring_washer_8mm", "Spring Washer 08mm", "23359465"),
    ("spring_washer_12mm", "Spring Washer 12mm", "23359481"),
    ("spring_washer_16mm", "Spring Washer 16mm", "23359493"),
    ("spring_washer_20mm", "Spring Washer 20mm", "23359511"),
    ("spring_washer_24mm", "Spring Washer 24mm", "23359535"),
    ("ce_locking_washer_triangular", "CE Side Locking Washer (Triangular)", "NS"),
    ("plain_washer_16mm", "Plain Washer 16mm", "NS"),
    ("plain_washer_20mm", "Plain Washer 20mm", "NS"),
    ("bolt_m16x40", "M 16x40 Bolt", "NS"),
    ("split_pin_4x45mm", "Split Pin 4 x 45mm", "NS"),
]

CHECKLIST_ITEMS = [
    ("must_change_items_changed", "Whether All Must Change Item Changed During Overhauling"),
    ("final_testing_per_smi", "Whether Final Testing Carried Out as per SMI"),
    ("nose_stay_dpt_mpt", "Whether Nose Stay DPT Checked & MPT"),
    ("lifting_lug_dpt_mpt", "Whether All Lifting Lug DPT Checked & MPT"),
    ("pinion_end_bearing_due", "Whether Pinion End Bearing Due for Change"),
    ("ce_side_bearing_due", "Whether C Side Bearing Due for Change"),
    ("deviation_allowed", "Any Deviation Being Allowed"),
    ("abnormalities_checked", "Abnormalities if Any Checked"),
]

WORK_DONE_ITEMS = [
    ("ceb_overhaul_work", "CEB Overhaule Work"),
    ("rocker_fit_holder_adjust", "Rocker Fit and Holder Adjust"),
    ("no_load_running_trial", "No Load Running Trial"),
    ("pinion_fitting_final_inspection", "Pinion Fitting and Final Inspection"),
]

TORQUE_TABLE = [
    ("m36", "M-36", "-", 14500.0, 1048.79, "As per Hitachi 15250A Manual"),
    ("m30", "M-30", "-", 8300.0, 600.34, "As per Hitachi 15250A Manual"),
    ("m24", "M-24", "PEB Endshield & Main Pole Bolts", 4200.0, 303.0, "As per Hitachi 15250A Manual"),
    ("m20", "M-20", "CEB Endshield, Inter Pole, Terminal Connection Bolt, Brush Holder-Insulator Foundation & "
     "Big Inspection Cover Bolts", 2420.0, 175.04, "As per Hitachi 15250A Manual"),
    ("m18", "M-18", "Pinion Locking Plate Bolts", 2447.11, 177.0, "Grampian Fasteners Manual"),
    ("m16_ceb", "M-16", "CEB Locking Plate Bolts", 1500.0, 108.495, "As per SMI 220 Rev 1 Date 28.10.2004"),
    ("m16_outer", "M-16", "Outer Cover CEB, Outer Grease Cover PEB & Rocker Connection Bolts", 1225.0, 88.60,
     "As per Hitachi 15250A Manual"),
    ("m12", "M-12", "Small Inspection Cover Bolts", 503.0, 36.38, "As per Hitachi 15250A Manual"),
    ("m10", "M-10", "Holder Sub Assembly Bolts", 295.0, 21.33, "As per Hitachi 15250A Manual"),
    ("m8", "M-8", "Holder Sub Assembly Bolts", 146.0, 10.56, "As per Hitachi 15250A Manual"),
    ("m6", "M-6", "Holder Sub Assembly Bolts", 61.6, 4.41, "As per Hitachi 15250A Manual"),
]


def build(add):
    add("rocker_ring_ce_end_shield_assembly", field_label="Assemble the Rocker Ring and CE End Shield on the "
        "Magnet Frame and Ensure Free Rotation of Rocker Ring (After Filling the Specified Quantity of "
        "Recommended Grease)", field_type="select", options="Done, Not Done", required=True,
        standard_value="860gm", authority_reference="Camtech Maintenance Manual of Hitachi TM Page No.39")
    add("armature_insertion_ptfe_commutator_clean", field_label="Clean the PTFE Ring and Commutator With "
        "Petrol and Insert the Armature Into the Magnet Frame With Due Care to Avoid Rubbing and Hitting of "
        "Each Other, Ensure Free Rotation of Armature", field_type="select", options="Done, Not Done",
        required=True)
    add("pe_end_shield_fix", field_label="Fix the PE End Shield After Filling Up Grease and Again Ensure Free "
        "Rotation of Armature", field_type="select", options="Done, Not Done", required=True,
        standard_value="925gm", authority_reference="Camtech Maintenance Manual of Hitachi TM Page No.39")
    add("motor_horizontal_rocker_freeness_check", field_label="Bring the Motor to Horizontal Position on the "
        "Stand, Check the Freeness of Rocker Ring", field_type="select", options="Done, Not Done", required=True)
    add("commutator_nj324_free_clearance", field_label="Commutator and (NJ-324) Free Clearance (Before "
        "Fitting) if Bearing Is Changed", field_type="numeric_range", required=True, unit="mm", min_value=0.155,
        max_value=0.195, decimal_precision=3, authority_reference="Camtech Maintenance Manual of Hitachi TM "
        "Page No.40")
    add("ce_bearing_radial_clearance_after_fitting", field_label="Measure the Radial Clearance (After Fitting) "
        "of CE Bearing (NJ324)", field_type="numeric_range", required=True, unit="mm", min_value=0.066,
        max_value=0.147, decimal_precision=3, authority_reference="Camtech Maintenance Manual of Hitachi TM "
        "Page No.40")
    add("pe_outer_bearing_cover_provided", field_label="Provide the PE Side Outer Bearing Cover",
        field_type="select", options="Done, Not Done", required=True)

    ab_diff_group = add("rib_bearing_stopper_step_difference", field_label="Measure Height of Loose Rib From "
        "Shaft Face vs Shaft Step ('A'), and Outer/Inner Step of CE Side Outer Bearing Stopper ('B') - Ensure "
        "'A'-'B' Is Within Range (Machine Max 0.5mm or Replace Stopper if Needed)", field_type="group",
        required=False, standard_value="'A' - 'B' = 1.0 - 1.5mm")
    add("dimension_a", parent=ab_diff_group, field_label="Dimension 'A'", field_type="number", required=True,
        unit="mm")
    add("dimension_b", parent=ab_diff_group, field_label="Dimension 'B'", field_type="number", required=True,
        unit="mm")

    end_shield_group = add("end_shield_diameter", field_label="End Shield Diameter", field_type="group",
                            required=False)
    add("end_shield_diameter_ce", parent=end_shield_group, field_label="CE", field_type="numeric_range",
        required=True, unit="mm", min_value=710.0, max_value=710.226, decimal_precision=3,
        standard_value="710+0.138+0.088mm")
    add("end_shield_diameter_pe", parent=end_shield_group, field_label="PE", field_type="numeric_range",
        required=True, unit="mm", min_value=696.0, max_value=696.226, decimal_precision=3,
        standard_value="696+0.138+0.088mm")

    deflector_seat_group = add("deflector_seating_dia", field_label="Seating Dia of Deflector (by Outside "
        "Micrometer)", field_type="group", required=False,
        authority_reference="RDSO/2012/ELRS/MS/0414 Amendment No. 01 Dt. 29.01.2013")
    add("deflector_seat_peb_shaft_dia", parent=deflector_seat_group, field_label="PEB-Def Shaft Dia",
        field_type="numeric_range", required=True, unit="mm", min_value=140.092, max_value=140.117,
        decimal_precision=3)
    add("deflector_seat_pe_def_id", parent=deflector_seat_group, field_label="PE-Def I/D", field_type="numeric_range",
        required=True, unit="mm", min_value=140.00, max_value=140.04, decimal_precision=3)
    add("deflector_seat_interference", parent=deflector_seat_group, field_label="Interference", field_type="numeric_range",
        required=True, unit="mm", min_value=0.052, max_value=0.117, decimal_precision=3)

    add("inner_race_bonding_test", field_label="Inner Race Bonding Test With Shaft to Be Done by CMS, Lab",
        field_type="select", options="OK, Not OK", required=True)
    add("ce_shaft_face_ink_impression_check", field_label="Apply Ink on the CE Side Shaft Face, Provide Outer "
        "Bearing Stopper, Tighten With 15.0 Kg-m Torque, Remove Locking Bolts and Stopper - Ensure No Ink "
        "Impression on Inner Surface", field_type="select", options="No Impression, Impression Found",
        required=True, standard_value="There Should Not Be Ink Impression on the Inner Surface of Outer "
        "Bearing Stopper", negative_values="Impression Found")
    add("ce_locking_plate_bolts_washer_replace", field_label="Replace the CE Locking Plate Bolts & Triangular "
        "Locking Washer During Every TOH/IOH and Tighten via Torque Wrench", field_type="select",
        options="Done, Not Done", required=True, standard_value="Torque Value: 15kg-m/108.495 Ft-Lbs",
        authority_reference="RDSO/ELRS/SMI 220 Rev 1 Dt.28.10.2004")
    add("pe_outer_bearing_stopper_induction_heat", field_label="Fix the Outer Bearing Stopper (PE Side) by "
        "Heating in an Induction Heater", field_type="numeric_range", required=True, unit="°C", min_value=110.0,
        max_value=120.0, decimal_precision=0, authority_reference="Camtech Maintenance Manual "
        "E/2005/TM(H)/1.0 Page No. 35")
    add("brush_holder_commutator_clearance", field_label="Adjust Brush Holder - Commutator Clearance (by "
        "Feeler Gauge)", field_type="numeric_range", required=True, unit="mm", min_value=2.0, max_value=4.0,
        decimal_precision=1, standard_value="3.00±1mm", authority_reference="Camtech Maintenance Manual "
        "E/2005/TM(H)/1.0 Page No. 02")

    carbon_brush_group = add("carbon_brush_provision", field_label="Provide New Carbon Brushes, Connect the "
        "Pig Tails IP Links and Record the Make & Date", field_type="group", required=False)
    add("carbon_brush_make", parent=carbon_brush_group, field_label="Brush Make", field_type="text", required=True,
        standard_value="Noted")
    add("carbon_brush_mfg_date", parent=carbon_brush_group, field_label="MFG Date", field_type="date",
        required=True)
    add("carbon_brush_grade", parent=carbon_brush_group, field_label="Brush Grade", field_type="text",
        required=True, standard_value="Noted")

    light_run_group = add("light_run_test", field_label="Conduct Light Run Test 895RPM Max in Both the "
        "Directions for Min. One-Hour in Each Direction - Observe for Abnormal Temperature Rise Especially at "
        "Bearing Housings", field_type="group", required=False, authority_reference="Camtech Maintenance "
        "Manual E/2005/TM(H)/1.0 Page No. 36 & 41")
    add("light_run_ambient_temp", parent=light_run_group, field_label="Ambient Temp.", field_type="number",
        required=True, unit="°C")
    for direction in ("clockwise", "anti_clockwise"):
        direction_label = "Clock Wise" if direction == "clockwise" else "Anti Clock Wise"
        direction_group = add(f"light_run_{direction}", parent=light_run_group, field_label=direction_label,
                               field_type="group", required=False, standard_value="Temp Rise 35-40°C (Above "
                               "Ambient)")
        for interval_key, interval_label in (
            ("0_15min_200rpm", "0-15 Min (200RPM)"), ("15_30min_400rpm", "15-30 Min (400RPM)"),
            ("30_45min_600rpm", "30-45 Min (600RPM)"), ("45_60min_895rpm", "45-60 Min (895RPM)"),
        ):
            interval_group = add(f"light_run_{direction}_{interval_key}", parent=direction_group,
                                  field_label=interval_label, field_type="group", required=False)
            add(f"light_run_{direction}_{interval_key}_peb", parent=interval_group, field_label="PEB",
                field_type="numeric_range", required=True, unit="°C", min_value=35.0, max_value=40.0,
                decimal_precision=1)
            add(f"light_run_{direction}_{interval_key}_ceb", parent=interval_group, field_label="CEB",
                field_type="numeric_range", required=True, unit="°C", min_value=35.0, max_value=40.0,
                decimal_precision=1)

    shock_pulse_group = add("shock_pulse_analyzer_check", field_label="Check the Sound, Confirm It Is Normal "
        "& Test the Bearings by Shock Pulse Analyzer", field_type="group", required=False,
        authority_reference="HTM Manual Page No 41")
    for side in ("pe", "ce"):
        side_group = add(f"shock_pulse_{side}", parent=shock_pulse_group, field_label=side.upper(),
                          field_type="group", required=False)
        for metric_key, metric_label in (("code", "Code"), ("lub", "Lub"), ("cond", "Cond."), ("lr", "LR"),
                                          ("hr", "HR")):
            add(f"shock_pulse_{side}_{metric_key}", parent=side_group, field_label=metric_label,
                field_type="text", required=True)

    ovality_group = add("commutator_ovality_final_assembly", field_label="Check Ovality of Commutator in Final "
        "Assembled TM (on Brush Holder Spring)", field_type="group", required=False, standard_value="0.04mm "
        "(Max)", authority_reference="Camtech Maintenance Manual E/2005/TM(H)/1.0 Page No. 41")
    for axis in ("r", "c", "v"):
        add(f"commutator_ovality_{axis}", parent=ovality_group, field_label=axis.upper(), field_type="numeric_range",
            required=True, unit="mm", min_value=0.0, max_value=0.04, decimal_precision=3)

    add("armature_lateral_play", field_label="Record the Lateral Play of Armature", field_type="numeric_range",
        required=True, unit="mm", min_value=0.0, max_value=0.5, decimal_precision=2, standard_value="0.5mm")
    add("stiffener_condition", field_label="Condition of Stiffener", field_type="select",
        options="OK, Welding, New Welded", required=True, authority_reference="RDSO/2008/EL/MS/0636 Dt. "
        "17.07.2008")

    gap_group = add("gap_measurements", field_label="Gap Between", field_type="group", required=False)
    add("gap_mp_armature", parent=gap_group, field_label="MP & Armature", field_type="numeric_range", required=True,
        unit="mm", min_value=6.35, max_value=20.0, decimal_precision=2, standard_value="6.35mm (Min)")
    add("gap_ip_armature", parent=gap_group, field_label="IP and Armature", field_type="numeric_range", required=True,
        unit="mm", min_value=10.0, max_value=30.0, decimal_precision=2, standard_value="10mm (Min)")

    add("brush_seater_bedding_check", field_label="Conduct Light Run Test in Both the Directions and Apply "
        "Brush Seater and Ensure 100% Bedding of Carbon Brush", field_type="select", options="Done, Not Done",
        required=True, standard_value="100% Bedding of Carbon Brush")
    add("tm_blow_dry_compressed_air", field_label="Blow the Traction Motor Thoroughly With Dry Compressed Air",
        field_type="select", options="Done, Not Done", required=True)
    add("commutator_ovality_record", field_label="Record the Ovality of Commutator", field_type="numeric_range",
        required=True, unit="mm", min_value=0.0, max_value=0.04, decimal_precision=3, standard_value="0.04mm "
        "(Max)")
    add("inspection_cover_seating_check", field_label="Close the Inspection Cover - Check for Its Proper "
        "Seating and There Should Not Be Any Gap in All Sides", field_type="select", options="Done, Not Done",
        required=True)

    pinion_selection_group = add("pinion_selection", field_label="Select Pinion of Required Ratio, Which Is "
        "Passed in the Crack Check, Check the Matching With Shaft and Record (Pinion Matching Sheet Attached)",
        field_type="group", required=False, standard_value="Gear Ratio 18:64 (WAG5H); Gear Ratio 16:65 (WAG7); "
        "Gear Ratio 23:58 (WAP4)")
    add("pinion_gear_ratio_used", parent=pinion_selection_group, field_label="Gear Ratio Used", field_type="text",
        required=True, standard_value="Noted")
    add("pinion_contact_area", parent=pinion_selection_group, field_label="Contact Area", field_type="numeric_range",
        required=True, unit="%", min_value=90.0, max_value=100.0, decimal_precision=0, standard_value="More "
        "Than 90%")

    pinion_details_group = add("pinion_details", field_label="Record Pinion Details", field_type="group",
                                required=False)
    add("pinion_make", parent=pinion_details_group, field_label="1. Make", field_type="text", required=True,
        standard_value="Noted")
    add("pinion_serial_no", parent=pinion_details_group, field_label="2. Serial No.", field_type="text",
        required=True, standard_value="Noted")
    add("pinion_mfg", parent=pinion_details_group, field_label="3. MFG.", field_type="text", required=True,
        standard_value="Noted")

    add("k_value_measurement", field_label="Measure 'K' Value and Record", field_type="number", required=True,
        unit="mm", standard_value="3 Teeth for 18 Teeth Pinion: 93.293-94.741mm; 3 Teeth for 16 Teeth Pinion: "
        "95.881-96.019mm; 4 Teeth for 23 Teeth Pinion: 131.461-131.600mm",
        authority_reference="Camtech Maintenance Manual E/2005/TM(H)/1.0 Page No. 40")
    add("pinion_p_value_check", field_label="Check the P Value of Pinion Teeth", field_type="numeric_range",
        required=True, unit="mm", min_value=0.0, max_value=0.4, decimal_precision=2, standard_value="0.4mm "
        "(Max)")

    pinion_fitment_group = add("pinion_stopper_fitment", field_label="Prepare the Correct Size Stopper, Heat "
        "the Pinion in Induction Heater and Fix It on the Shaft Ensuring Correct Advancement by the Stopper",
        field_type="group", required=False, standard_value="140deg+Ambient Temp., Adv.: 2.0mm",
        authority_reference="Camtech Maintenance Manual of Hitachi TM Page No.40")
    add("pinion_fitment_initial", parent=pinion_fitment_group, field_label="Initial", field_type="number",
        required=True, unit="mm")
    add("pinion_fitment_after", parent=pinion_fitment_group, field_label="After Fitment", field_type="number",
        required=True, unit="mm")

    add("pinion_locking_after_cooldown", field_label="Lock the Pinion After Allowing It to Cool Down for Some "
        "Time", field_type="select", options="Done, Not Done", required=True)
    add("terminal_clamper_machined_check", field_label="Provide Terminals of Suitable Size to Match the "
        "Nominated Loco - Specify Terminal & Clamper Is Machined or Unmachined", field_type="select",
        options="Machined, Unmachined", required=True)
    add("terminal_cover_air_inlet_paint", field_label="Provide Terminal Cover and Clean Air Inlet Cover - "
        "Paint the Motor", field_type="select", options="Done, Not Done", required=True)
    add("final_ir_value", field_label="Take Final IR Value of the Motor", field_type="numeric_range", required=True,
        unit="MOhm", min_value=10.0, max_value=1000.0, decimal_precision=1, standard_value="Min. 10M-Ohms "
        "With 1000V Megger", authority_reference="Camtech Maintenance Manual E/2005/TM(H)/1.0 Page No. 36")

    must_change_group = add("must_change_items", field_label="Must Change Items", field_type="group",
                             required=False)
    for key, label, pl_no in MUST_CHANGE_ITEMS:
        add(f"must_change_{key}", parent=must_change_group, field_label=f"{label} (PL No. {pl_no})",
            field_type="select", options="Changed, Not Changed", required=True, negative_values="Not Changed")
    new_components_group = add("new_components_used", parent=must_change_group, field_label="Details of New "
        "Components Used", field_type="group", required=False)
    for i in range(1, 5):
        add(f"new_component_{i}", parent=new_components_group, field_label=f"Component {i}", field_type="text",
            required=False)

    checklist_group = add("post_overhaul_checklist", field_label="Check List", field_type="group", required=False)
    for key, label in CHECKLIST_ITEMS:
        item_group = add(f"checklist_{key}", parent=checklist_group, field_label=label, field_type="group",
                          required=False)
        add(f"checklist_{key}_answer", parent=item_group, field_label="Yes/No", field_type="select",
            options="Yes, No", required=True)
        add(f"checklist_{key}_remark", parent=item_group, field_label="Remark", field_type="text", required=False)

    work_done_group = add("work_done_confirmation", field_label="Work Done", field_type="group", required=False)
    for key, label in WORK_DONE_ITEMS:
        add(f"work_done_{key}", parent=work_done_group, field_label=label, field_type="select",
            options="Done, Not Done", required=True)

    add("previous_history_yoke_armature", field_label="Brief Previous History of Yoke and Armature",
        field_type="textarea", required=False)

    torque_group = add("tightening_torque", field_label="Tightening Torque of Each Bolt & Nut - Check Each "
        "Bolt & Nut for Looseness as Required", field_type="group", required=False)
    for key, size, description, torque_kgfcm, torque_ftlb, remark in TORQUE_TABLE:
        label = f"{size}" + (f" - {description}" if description != "-" else "")
        add(f"torque_{key}", parent=torque_group, field_label=label, field_type="select",
            options="Ensured, Not Ensured", required=True,
            standard_value=f"{torque_kgfcm} Kgf.Cm ({torque_ftlb} Ft-Lb) - {remark}",
            negative_values="Not Ensured")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="TM-Conv", template_code="143", technology="CONVENTIONAL",
        template_name="Checksheet for Assembling of Traction Motor",
        description="Assembling of Traction Motor checksheet - Conventional - M35-TM section.",
        build_fn=build,
    )
