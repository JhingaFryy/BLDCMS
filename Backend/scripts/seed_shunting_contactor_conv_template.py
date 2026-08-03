"""
Module 41: seeds the ShC_Conv (Shunting Contactor, WAP-4/Conventional locomotives, M1-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_shunting_contactor_conv_template.py`

Source: "TOH & IOH For Conv. Shunting Contactor.pdf" - same "Performa for TOH & IOH Maintenance
Activities" family as the EP Contactor sheet, sharing its 9-item overhauling checklist verbatim
plus two Shunting-Contactor-specific additions ("Ensure the all Nuts & Bolts in Tight Position",
"Ensure the Proper Condition of Shunts").

The Testing performa differs genuinely from EP Contactor's: Main Contact Gap (23-27mm vs EP's
24±1mm) and Main Contact Pressure (6.4-8.2 kg/cm2 - a pressure spec, vs EP's 13-14 Kg force spec)
use different standards, and contact bedding is specified as a percentage ("more than 80%") rather
than EP's "Proper seating". The source scan for this sheet's testing table is partially illegible
(rotated/overlapping handwriting); only the checking points that are clearly legible are included
here - Auxiliary Contact Pressure, RDPT of flexible shunt/mobile contact lever assembly and Delay
Time ON/OFF (all present on the EP Contactor sheet) are not modelled for Shunting Contactor because
no legible standard value could be confirmed for them on this sheet, rather than guessing.
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
        "Movement of Mobile Contact Tips", field_type="select", options="Proper Alignment & Free Movement, Not "
        "Proper", required=True, standard_value="Proper Alignment & Free Movement")
    add("arc_chute_condition", parent=overhaul_group, field_label="Ensure the Proper Condition of Arc-Chute",
        field_type="select", options="OK, Not OK", required=True, standard_value="No Crack, Should Be Clean",
        negative_values="Not OK")
    add("insulating_part_mounting", parent=overhaul_group, field_label="Ensure the Cleaning & Condition of "
        "Mounting of Insulating Part", field_type="select", options="OK, Not OK", required=True,
        standard_value="Clean, Firmly Mounted", negative_values="Not OK")
    add("coil_blow_out", parent=overhaul_group, field_label="Blow Out Coil", field_type="select",
        options="Done, Not Done", required=True, standard_value="Done", negative_values="Not Done")
    add("servomotor_piston_cup_replace", parent=overhaul_group, field_label="Replace the Piston Cup of "
        "Servomotor", field_type="select", options="Changed, Not Changed", required=True,
        standard_value="Must Change in TOH & IOH", negative_values="Not Changed")
    add("servomotor_rubber_gasket_replace", parent=overhaul_group, field_label="Replace the Rubber Gasket of "
        "Servomotor", field_type="select", options="Changed, Not Changed", required=True,
        standard_value="Must Change in TOH & IOH", negative_values="Not Changed")
    add("piston_cup_servomotor_lubrication", parent=overhaul_group, field_label="Proper Lubrication of Piston "
        "Cup, Servomotor Assembly", field_type="text", required=True, standard_value="MP3")
    add("nuts_bolts_tightness", parent=overhaul_group, field_label="Ensure the All Nuts & Bolts in Tight "
        "Position", field_type="select", options="Tight, Not Tight", required=True, standard_value="Should Be "
        "Tight", negative_values="Not Tight")
    add("shunts_condition", parent=overhaul_group, field_label="Ensure the Proper Condition of Shunts",
        field_type="select", options="OK, Not OK", required=True,
        standard_value="Flexible, No Discoloration", negative_values="Not OK")

    testing_group = add("testing", field_label="Testing", field_type="group", required=False)
    add("coil_resistance_20c", parent=testing_group, field_label="Coil Resistance at 20°C (R20)",
        field_type="numeric_range", required=True, unit="Ohm", min_value=1242.0, max_value=1458.0,
        decimal_precision=0, standard_value="1350±8% (1242-1458) Ohm")
    add("pick_up_voltage", parent=testing_group, field_label="Pick Up Voltage", field_type="numeric_range",
        required=True, unit="V", min_value=60.0, max_value=70.0, decimal_precision=1)
    add("drop_out_voltage", parent=testing_group, field_label="Drop Out Voltage", field_type="numeric_range",
        required=True, unit="V", min_value=15.0, max_value=25.0, decimal_precision=1)
    add("surge_comparison_test", parent=testing_group, field_label="Surge Comparison Test of Coil",
        field_type="select", options="OK, Not OK", required=True, standard_value="As per SMI 157",
        authority_reference="SMI-157", negative_values="Not OK")
    add("inter_turn_short_test", parent=testing_group, field_label="Inter Turn Short Test of Coil",
        field_type="select", options="OK, Not OK", required=True, standard_value="As per SMI 59",
        authority_reference="SMI-59", negative_values="Not OK")
    add("quality_factor_test", parent=testing_group, field_label="Quality Factor Test of Coil",
        field_type="numeric_range", required=True, min_value=1.0, max_value=3.0, decimal_precision=0)
    add("main_contact_gap", parent=testing_group, field_label="Main Contact Gap", field_type="numeric_range",
        required=True, unit="mm", min_value=23.0, max_value=27.0, decimal_precision=1)
    add("main_contact_pressure", parent=testing_group, field_label="Main Contact Pressure",
        field_type="numeric_range", required=True, unit="kg/cm2", min_value=6.4, max_value=8.2,
        decimal_precision=1)
    add("contact_bedding_check", parent=testing_group, field_label="Ensure That the Contact Bedding Should Be "
        "Proper", field_type="select", options="OK, Not OK", required=True,
        standard_value="Should Be More Than 80%", negative_values="Not OK")
    add("ep_valve_smooth_operation", parent=testing_group, field_label="Ensure the Smooth Operation of EP Valve",
        field_type="select", options="Smooth/No Sticking, Sticking Found", required=True,
        standard_value="Smooth/No Sticking", negative_values="Sticking Found")
    add("servo_piston_movement", parent=testing_group, field_label="Ensure the Movement of Servo Piston",
        field_type="select", options="Free & Smooth, Not Free", required=True, standard_value="Free & Smooth",
        negative_values="Not Free")
    add("air_passage_check", parent=testing_group, field_label="Ensure the Smooth Air Passage (EP Valve "
        "Gasket, Servomotor Inlet Supply, EP Valve Nut)", field_type="select",
        options="No Blockage/Leakage, Blockage/Leakage Found", required=True,
        standard_value="No Blockage or Leakage", negative_values="Blockage/Leakage Found")
    add("endurance_test_cycle", parent=testing_group, field_label="Endurance Test Cycle", field_type="select",
        options="Done, Not Done", required=True,
        standard_value="110 Cycle (Free From Sluggish Operation & No Mechanical Damage)",
        negative_values="Not Done")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="ShC_Conv", template_code="121", technology="CONVENTIONAL",
        template_name="Checksheet for Shunting Contactor",
        description="TOH & IOH maintenance and testing checksheet for Shunting Contactor - Conventional - "
                     "M1-HR section.",
        build_fn=build,
    )
