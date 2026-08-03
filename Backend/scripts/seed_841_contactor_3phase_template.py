"""
Module 41 (Phase 2): seeds the 841C (8.41 Contactor, 3-Phase locomotives, M1-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_841_contactor_3phase_template.py`

Source: "TOH & IOH For 8.41 Contactor.pdf" - "Performa for TOH & IOH Maintenance Activities for
8.41 Contactor", a single continuous 16-item checklist (visual/cleaning checks, air gap, coil
resistance, crushing, pick-up/drop-out voltage, auxiliary I/L continuity/millivolt drop,
pick-up/drop-out timing, arc-chute locking) - same family as the 8182C sheet, but this equipment
is a single physical contactor position (no 8.1/8.2-style dual position), so no "Position" field
is needed.

Four makes are covered (PPS, Secheron, Continental, AAL) with differing standards for air gap and
coil resistance specifically - both makes' specs are kept together in the relevant field's
standard_value text (the header's own Make field identifies which governs), the same pattern used
for HRPT/SRMC/8182C. Per the module's "Do NOT create fields for Loco Number/Technician/Supervisor
Name/Signature" rule, the sheet's own "Removed From/Provided In Loco No. & Date" and "Overhauling
& Testing By"/"Sign of Staff"/"Sign of Supervisor" lines are intentionally not modelled.
"""
from _aux_template_helpers import add_final_remarks, run_seed


def build(add):
    add("contactor_sn", field_label="S.N.", field_type="text", required=True, standard_value="Noted")
    add("contactor_make", field_label="Make", field_type="text", required=True, standard_value="Noted")
    add("contactor_type", field_label="Type", field_type="text", required=True, standard_value="Noted")
    add("contactor_mfg_year", field_label="Mfg.", field_type="text", required=True, standard_value="Noted")
    add("overhauling_date", field_label="Overhauling & Tested Date", field_type="date", required=True)

    checks_group = add("check_points", field_label="Maintenance Activities During Schedule", field_type="group",
                        required=False)
    add("contactor_damage_breakage_check", parent=checks_group, field_label="Visual Check the Condition of the "
        "Contactor for Any Damage/Breakage", field_type="select", options="No Damage/Breakage, Damage/Breakage "
        "Found", required=True, standard_value="No Damage/Breakage", negative_values="Damage/Breakage Found")
    add("arc_chute_condition_check", parent=checks_group, field_label="Check the Condition of Arc-Chute",
        field_type="select", options="OK, Not OK", required=True, standard_value="No Play in Bottom",
        negative_values="Not OK")
    add("arc_chute_cleaning_blowing", parent=checks_group, field_label="Cleaning & Blowing of Arc-Chute",
        field_type="select", options="Cleaned, Not Cleaned", required=True, standard_value="Should Be Cleaned",
        negative_values="Not Cleaned")
    add("fix_mobile_contact_alignment_check", parent=checks_group, field_label="Check the Alignment of Fix & "
        "Mobile Contact", field_type="select", options="Perfect, Not Perfect", required=True,
        standard_value="Should Be Perfect", negative_values="Not Perfect")
    add("main_contacts_air_gap", parent=checks_group, field_label="Air Gap of Main Contacts", field_type="numeric_range",
        required=True, unit="mm", min_value=20.0, max_value=24.0, decimal_precision=1,
        standard_value="As per OEM Manual: 20.5-23.5mm (PPS); 20-24mm (Secheron & Continental)")
    add("coil_resistance_r20", parent=checks_group, field_label="Coil Resistance at R20", field_type="number",
        required=True, unit="Ohm", standard_value="As per OEM Manual: 377±8% = 346-407 Ohm (PPS); 462±8% = "
                                                    "425-499 Ohm (Secheron & Continental)")
    add("main_contactor_crushing", parent=checks_group, field_label="Ensure Crushing of Main Contactor in Closed "
        "Position", field_type="numeric_range", required=True, unit="mm", min_value=5.9, max_value=6.1,
        decimal_precision=2, standard_value="6±0.1mm")
    add("core_assembly_coil_clean", parent=checks_group, field_label="Clean Core Assembly of Coil With Clean "
        "Cloth", field_type="select", options="Cleaned, Not Cleaned", required=True, standard_value="Should Be "
        "Cleaned", negative_values="Not Cleaned")
    add("pick_up_voltage", parent=checks_group, field_label="Ensure the Pick Up Voltage", field_type="numeric_range",
        required=True, unit="V", min_value=0.0, max_value=77.0, decimal_precision=0,
        standard_value="Equal to or Less Than 77 V")
    add("drop_out_voltage", parent=checks_group, field_label="Ensure the Drop Out Voltage", field_type="numeric_range",
        required=True, unit="V", min_value=11.0, max_value=100.0, decimal_precision=0,
        standard_value="As per OEM Manual: Equal to or Greater Than 11 V")

    aux_il_group = add("aux_il_continuity", parent=checks_group, field_label="Examination of Continuity & "
        "Discontinuity of Auxiliary I/L NO/NC", field_type="group", required=False,
        standard_value="Should Be Perfect")
    for key, label in (("no1", "NO 1"), ("no2", "NO 2"), ("nc1", "NC 1"), ("nc2", "NC 2")):
        add(f"aux_il_{key}", parent=aux_il_group, field_label=label, field_type="number", required=True, unit="mV")

    add("aux_il_millivolt_drop", parent=checks_group, field_label="MilliVolt Drop of Auxiliary I/L",
        field_type="number", required=True, unit="mV", standard_value="As per OEM Manual (PPS/Secheron/"
                                                                        "Continental/AAL)")
    add("pickup_closing_time", parent=checks_group, field_label="Ensure the Pick Up (Closing) Time of the "
        "Contactor", field_type="number", required=True, unit="msec",
        standard_value="80-100 msec (PPS/Secheron/Continental/AAL)")
    add("dropout_opening_time", parent=checks_group, field_label="Ensure the Drop Out (Opening) Time of the "
        "Contactor", field_type="number", required=True, unit="msec",
        standard_value="70-75 msec (PPS/Secheron/Continental/AAL)")
    add("arc_chute_locking_condition_check", parent=checks_group, field_label="Ensure the Condition of Locking "
        "of Arc-Chute", field_type="select", options="Properly Locked, Not Properly Locked", required=True,
        standard_value="Should Be Locked Properly", negative_values="Not Properly Locked")
    add("contactor_operation_after_arc_chute_fitment", parent=checks_group, field_label="Examine the Operation "
        "of Contactor After Fitment of Arc-Chute", field_type="select", options="Proper, Not Proper", required=True,
        standard_value="Should Be Proper", negative_values="Not Proper")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="841C", template_code="133", technology="3_PHASE",
        template_name="Checksheet for 8.41 Contactor",
        description="TOH & IOH maintenance and testing checksheet for 8.41 Contactor - 3-Phase - M1-HR section.",
        build_fn=build,
    )
