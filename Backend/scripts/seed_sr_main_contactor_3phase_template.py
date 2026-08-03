"""
Module 41 (Phase 2): seeds the SRMC (SR Main Contactor of Traction Converter, 3-Phase
locomotives, M1-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_sr_main_contactor_3phase_template.py`

Source: "TOH & IOH For SR Main Contactor Of Traction Converter.pdf" - a 7-item overhauling
checklist plus a 10-item electrical Testing performa, and 2 additional checks (armature free
movement, shunt condition).

Two contactor makes are covered (Secheron and Microelettrica Scientifica) with genuinely
different standards for Pick-up Voltage, Main Contact Pressure, Closing/Opening Time and Main
Contact Gap - each such field lists both makes' specs in its standard_value text (the header's
own Make field identifies which governs), the same pattern used for HRPT's multi-make fields,
rather than duplicating fields per make.

Per the module's "Do NOT create fields for Loco Number/Technician/Supervisor Name/Signature"
rule, the sheet's own "Removed From/Provided In Loco No. & Date" and "Overhauled By"/"Tested By"
lines are intentionally not modelled.
"""
from _aux_template_helpers import add_final_remarks, run_seed


def build(add):
    add("contactor_sn", field_label="Contactor S.N.", field_type="text", required=True, standard_value="Noted")
    add("contactor_make", field_label="Make", field_type="text", required=True, standard_value="Noted")
    add("contactor_type", field_label="Type", field_type="text", required=True, standard_value="Noted")
    add("contactor_mfg_year", field_label="Mfg. Year", field_type="text", required=True, standard_value="Noted")
    add("overhauling_date", field_label="Overhauling Date", field_type="date", required=True)

    overhaul_group = add("overhauling_activities", field_label="Maintenance Activities During Overhauling",
                          field_type="group", required=False)
    add("fix_contact_tips_condition", parent=overhaul_group, field_label="Ensure the Smooth Surface & No "
        "Pitting Marks on Fix Contact Tips", field_type="select", options="Smooth Surface, No Pitting/Not Smooth",
        required=True, standard_value="Smooth Surface & No Pitting")
    add("mobile_contact_tips_condition", parent=overhaul_group, field_label="Ensure the Smooth Surface & No "
        "Pitting Marks on Mobile Contact Tips", field_type="select",
        options="Smooth Surface, No Pitting/Not Smooth", required=True, standard_value="Smooth Surface & No Pitting")
    add("mobile_contact_tips_alignment", parent=overhaul_group, field_label="Ensure the Proper Alignment & Free "
        "Movement of Mobile Contact Tips", field_type="select",
        options="Proper Alignment & Free Movement, Not Proper", required=True,
        standard_value="Proper Alignment & Free Movement")
    add("arc_chute_condition", parent=overhaul_group, field_label="Ensure the Proper Condition of Arc-Chute",
        field_type="select", options="OK, Not OK", required=True, standard_value="No Crack, Should Be Clean",
        negative_values="Not OK")
    add("contact_tips_replace", parent=overhaul_group, field_label="Replace the Contact Tips of Contactor",
        field_type="select", options="Replaced, Not Replaced", required=True,
        standard_value="As per OEM Instruction", negative_values="Not Replaced")
    add("damper_washer_replace", parent=overhaul_group, field_label="Replace the Damper Washer (Made of "
        "Polyurethane Foam) With Silicon Made Damper Washer (Secheron Make Only)", field_type="select",
        options="Replaced, Serviceable/Not Replaced", required=True,
        standard_value="Must Change in IOH2 & IOH4 (for WAP5); Condition Basis for WAP7 & WAG9",
        authority_reference="RDSO Letter No. EL/9/91/1, Dated 01.03.23")
    add("nuts_bolts_tightness", parent=overhaul_group, field_label="Ensure the All Nuts & Bolts in Tight "
        "Position", field_type="select", options="Tight, Not Tight", required=True, standard_value="Should Be "
        "Tight", negative_values="Not Tight")

    testing_group = add("testing", field_label="Testing", field_type="group", required=False)
    add("pick_up_voltage", parent=testing_group, field_label="Pick Up Voltage", field_type="number", required=True,
        unit="V", standard_value="Secheron: ≤77 V; Microelettrica: ≤61 V")
    add("drop_out_voltage", parent=testing_group, field_label="Drop Out Voltage", field_type="numeric_range",
        required=True, unit="V", min_value=10.0, max_value=30.0, decimal_precision=0)
    add("main_contact_pressure", parent=testing_group, field_label="Main Contact Pressure", field_type="number",
        required=True, unit="Kgf", standard_value="Secheron: 8-12 Kgf; Microelettrica: 5±0.5 Kgf")
    add("main_contact_continuity_check", parent=testing_group, field_label="Check Continuity of Main Contact",
        field_type="select", options="OK, Not OK", required=True, standard_value="Should Be OK",
        negative_values="Not OK")
    add("aux_contact_continuity_check", parent=testing_group, field_label="Check Continuity of Auxiliary "
        "Contact", field_type="select", options="OK, Not OK", required=True, standard_value="Should Be OK",
        negative_values="Not OK")
    add("closing_time_of_contact", parent=testing_group, field_label="Closing Time of Contact", field_type="number",
        required=True, unit="ms", standard_value="Secheron: ≤95 ms; Microelettrica: ≤300 ms")
    add("opening_time_of_contact", parent=testing_group, field_label="Opening Time of Contact", field_type="number",
        required=True, unit="ms", standard_value="Secheron: ≤60 ms; Microelettrica: ≤60 ms")
    add("main_contact_gap", parent=testing_group, field_label="Main Contact Gap", field_type="number",
        required=True, unit="mm", standard_value="Secheron: 14-16.5 mm; Microelettrica: ≥25 mm")
    add("contact_bedding_check", parent=testing_group, field_label="Ensure That the Contact Bedding Should Be "
        "Proper", field_type="numeric_range", required=True, unit="%", min_value=80.0, max_value=100.0,
        decimal_precision=0, standard_value="More Than 80%")
    add("endurance_test_cycle", parent=testing_group, field_label="Endurance Test Cycle", field_type="select",
        options="Done, Not Done", required=True,
        standard_value="50 Cycle (Free From Sluggish Operation & No Mechanical Damage)",
        negative_values="Not Done")
    add("armature_free_movement_check", parent=testing_group, field_label="Ensure Armature Moves Freely",
        field_type="select", options="Free, Sluggish", required=True, standard_value="No Sluggish Movement",
        negative_values="Sluggish")
    add("shunts_condition_check", parent=testing_group, field_label="Ensure the Proper Condition of Shunts",
        field_type="select", options="OK, Not OK", required=True, standard_value="Flexible, No Discoloration",
        negative_values="Not OK")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="SRMC", template_code="130", technology="3_PHASE",
        template_name="Checksheet for SR Main Contactor of Traction Converter",
        description="TOH & IOH maintenance and testing checksheet for SR Main Contactor of Traction Converter "
                     "- 3-Phase - M1-HR section.",
        build_fn=build,
    )
