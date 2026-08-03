"""
Module 41 (Phase 2): seeds the 8182C (8.1 & 8.2 Contactor, 3-Phase locomotives, M1-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_8182_contactor_3phase_template.py`

Source: "TOH & IOH For 8.1 & 8.2 Contactor.pdf" - "Performa for TOH & IOH Maintenance Activities
Schedule", a 7-item overhauling checklist (servo motor/main cylinder overhaul, contact tip
replacement, arc-chute cleaning) plus a 13-item Testing performa (main contact gap, EP valve coil
resistance, pick-up/drop-out voltage and timing, air leakage, auxiliary I/L continuity, locking).

This single equipment code covers both the 8.1 and 8.2 contactors of the same family - the
Android workflow has no separate position-selection step, so a "Position" field (8.1/8.2) is
modelled here (same pattern already used for per-cab equipment elsewhere in M1-HR). Three makes
(AAL, Secheron, Continental) are covered with different EP valve coil resistance standards, kept
together in one field's standard_value text since only one applies per physical unit.

Per the module's "Do NOT create fields for Loco Number/Technician/Supervisor Name/Signature"
rule, the sheet's own "Removed From/Provided In Loco No. & Date" and "Overhauled By"/"Tested By"
lines are intentionally not modelled.
"""
from _aux_template_helpers import add_final_remarks, run_seed


def build(add):
    add("contactor_position", field_label="Position", field_type="select", options="8.1, 8.2", required=False)
    add("contactor_sn", field_label="S.N.", field_type="text", required=True, standard_value="Noted")
    add("contactor_make", field_label="Make", field_type="text", required=True, standard_value="Noted")
    add("contactor_type", field_label="Type", field_type="text", required=True, standard_value="Noted")
    add("contactor_mfg_year", field_label="Mfg.", field_type="text", required=True, standard_value="Noted")
    add("overhauling_date", field_label="Overhauling Date", field_type="date", required=True)

    overhaul_group = add("overhauling_activities", field_label="Maintenance Activities During Overhauling "
        "Schedule", field_type="group", required=False)
    add("contactor_cleaning_blowing", parent=overhaul_group, field_label="Cleaning & Blowing of Contactor",
        field_type="select", options="Cleaned, Not Cleaned", required=True, standard_value="Should Be Cleaned",
        negative_values="Not Cleaned")
    add("all_components_crack_damage_check", parent=overhaul_group, field_label="Examine the All Components "
        "for Crack & Damage", field_type="select", options="No Damage/No Crack, Damage/Crack Found", required=True,
        standard_value="No Damage/No Crack", negative_values="Damage/Crack Found")
    add("servo_motor_main_cylinder_overhaul", parent=overhaul_group, field_label="Overhauling of Servo Motor & "
        "Main Cylinder of Contactor - Replace the Rubber Parts of Servo Motor & Main Cylinder",
        field_type="select", options="Done, Not Done", required=True,
        standard_value="Must Change Items in TOH", authority_reference="RDSO Letter No. EL/3.1.28(DM2), Dated "
                                                                        "13.01.2023",
        negative_values="Not Done")
    add("cross_bar_over_cylinder_crack_damage_check", parent=overhaul_group, field_label="Examine the Cross Bar "
        "& Over Cylinder for Any Crack or Damage", field_type="select", options="No Damage/No Crack, Damage/Crack "
        "Found", required=True, standard_value="No Damage/No Crack", negative_values="Damage/Crack Found")
    add("contact_tips_replace", parent=overhaul_group, field_label="Replace the Contact Tips (Mobile & Fix)",
        field_type="select", options="Replaced, Not Replaced", required=True,
        standard_value="Must Change Items in IOH2 & IOH4 for WAG9", negative_values="Not Replaced")
    add("servo_motor_piston_overhaul_lubricate", parent=overhaul_group, field_label="Overhaul & Lubricate Servo "
        "Motor & Piston Assembly With Specified Grease", field_type="select", options="Done, Not Done",
        required=True, standard_value="As per OEM Manual: Shell Alvania, R-2, Ratinex, LX (AAL/Secheron/"
                                       "Continental)", negative_values="Not Done")
    add("arc_chute_cleaning_blowing", parent=overhaul_group, field_label="Cleaning & Blowing of Arc-Chute",
        field_type="select", options="Cleaned, Not Cleaned", required=True, standard_value="Should Be Cleaned",
        negative_values="Not Cleaned")

    testing_group = add("testing", field_label="Tested By/Tested On", field_type="group", required=False)
    add("main_contact_gap", parent=testing_group, field_label="Ensure the Gap of Main Contact", field_type="numeric_range",
        required=True, unit="mm", min_value=14.0, max_value=16.5, decimal_precision=1,
        standard_value="14-16.5 mm (for AAL, Secheron, Continental)")
    add("main_aux_contact_continuity_check", parent=testing_group, field_label="Examine the Continuity & "
        "Discontinuity of Main Auxiliary Contact During Operation", field_type="select",
        options="Perfect, Not Perfect", required=True, standard_value="Should Be Perfect",
        negative_values="Not Perfect")
    add("ep_valve_coil_resistance", parent=testing_group, field_label="Check the Coil Resistance of EP Valve",
        field_type="number", required=True, unit="Ohm",
        standard_value="As per OEM Manual: AAL: 617±5% Ohm; Secheron: 1280±8% = (1177-1382 Ohm); Continental: "
                        "Range Not Mentioned")
    add("max_pickup_voltage", parent=testing_group, field_label="Ensure the Maximum Pick Up Voltage at Pressure "
        "of (4-10) kg/cm2", field_type="numeric_range", required=True, unit="V", min_value=0.0, max_value=77.0,
        decimal_precision=0, standard_value="≤77 V (for AAL/Secheron/Continental)")
    add("min_dropout_voltage", parent=testing_group, field_label="Ensure the Minimum Drop Out Voltage at "
        "Pressure of (4-10) kg/cm2", field_type="numeric_range", required=True, unit="V", min_value=11.0,
        max_value=100.0, decimal_precision=0, standard_value="≥11 V (for AAL/Secheron/Continental)")
    add("pickup_closing_time", parent=testing_group, field_label="Ensure the Pick Up (Closing) Time of the "
        "Contactor", field_type="number", required=True, unit="msec", standard_value="As per OEM Manual")
    add("dropout_opening_time", parent=testing_group, field_label="Ensure the Drop Out (Opening) Time of the "
        "Contactor", field_type="number", required=True, unit="msec", standard_value="As per OEM Manual")
    add("air_leakage_check_100_ops", parent=testing_group, field_label="Check the Air Leakage for 100 Operations "
        "on Test Bench", field_type="select", options="No Leakage, Leakage Found", required=True,
        standard_value="No Leakage", negative_values="Leakage Found")
    add("coil_energized_leakage_check", parent=testing_group, field_label="Coil in Energized Condition",
        field_type="select", options="No Leakage, Leakage Found", required=True, standard_value="No Leakage",
        negative_values="Leakage Found")
    add("coil_deenergized_leakage_check", parent=testing_group, field_label="Coil in De-Energized Condition",
        field_type="select", options="No Leakage, Leakage Found", required=True, standard_value="No Leakage",
        negative_values="Leakage Found")
    add("aux_il_no_nc_continuity_check", parent=testing_group, field_label="Examination of Continuity & "
        "Discontinuity of Auxiliary I/L NO/NC", field_type="select", options="Perfect, Not Perfect", required=True,
        standard_value="Should Be Perfect", negative_values="Not Perfect")
    add("contactor_locking_condition_check", parent=testing_group, field_label="Ensure the Condition of Locking "
        "of Contactor", field_type="select", options="Properly Locked, Not Properly Locked", required=True,
        standard_value="Should Be Locked Properly", negative_values="Not Properly Locked")
    add("contactor_operation_after_arc_chute_fitment", parent=testing_group, field_label="Examine the Operation "
        "of Contactor After Fitment of Arc-Chute", field_type="select", options="Proper, Not Proper", required=True,
        standard_value="Should Be Proper", negative_values="Not Proper")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="8182C", template_code="132", technology="3_PHASE",
        template_name="Checksheet for 8.1 & 8.2 Contactor",
        description="TOH & IOH maintenance and testing checksheet for 8.1 & 8.2 Contactor - 3-Phase - M1-HR "
                     "section.",
        build_fn=build,
    )
