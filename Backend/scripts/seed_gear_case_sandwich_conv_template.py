"""
Module 40: seeds the GC_Conv (Gear Case & Sandwich Mounting, WAP-4, Conventional, M4-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_gear_case_sandwich_conv_template.py`

Source: pages 13-14 of the supplied WAP-4 checksheet - "Check Sheet for Gear Case & Sandwich
Mounting", recorded once per unit (1-6 - one per axle, six axles).

Genuinely distinct sheet from the WAG9HC/WAP-7 "Gear Case" template (seed_gear_case_template.py /
_p7_template.py) - those cover oil/breather/sight-glass/bolt-property checks on the axle-hung gear
case of the 3-Phase Flexicoil bogie's fully-suspended traction motor. This WAP-4 sheet instead
covers the nose-suspended traction motor's sandwich mounting (rubber-metal bonded nose pad, free
height/total height of the sandwich elements, nose pad spring-testing-machine compression
readings, gap to the TM's bottom lug) - a different subsystem entirely, reflecting the
Conventional bogie's different (nose-suspended, as opposed to fully-suspended) TM mounting.
"""
from _m4hr_template_helpers import add_final_remarks, add_unit_group_table, run_seed

UNITS = list(range(1, 7))


def _nose_pad_testing_builder(add, parent, unit_label):
    group = add(f"gear_case_{unit_label}_nose_pad_testing", parent=parent, field_label="Nose Pad Number and "
                "Testing on Spring Testing Machine", field_type="group", required=False)
    add(f"gear_case_{unit_label}_nose_pad_number", parent=group, field_label="Nose Pad Number", field_type="text",
        required=True, standard_value="Noted")
    add(f"gear_case_{unit_label}_nose_pad_make_year", parent=group, field_label="Make & Year", field_type="text",
        required=True, standard_value="Noted")
    add(f"gear_case_{unit_label}_nose_pad_2000kg", parent=group, field_label="On 2000Kg Compress Hts.",
        field_type="number", required=False, unit="mm")
    add(f"gear_case_{unit_label}_nose_pad_4000kg", parent=group, field_label="On 4000Kg Compress Hts.",
        field_type="number", required=False, unit="mm")
    add(f"gear_case_{unit_label}_nose_pad_6000kg", parent=group, field_label="On 6000Kg Compress Hts.",
        field_type="number", required=False, unit="mm")


def build(add):
    activities = [
        {"key": "cleaned", "label": "Gear Case Cleaned", "field_type": "select", "options": "Cleaned, Not Cleaned",
         "required": True, "standard_value": "Cleaned", "negative_values": "Not Cleaned"},
        {"key": "crack_damage_check", "label": "Check for Any Crack and Damage", "field_type": "select",
         "options": "No Crack, Crack Found", "required": True, "standard_value": "No Crack",
         "negative_values": "Crack Found"},
        {"key": "boss_thread_condition", "label": "Check Threads Condition of Boss", "field_type": "select",
         "options": "OK, Not OK", "required": True, "standard_value": "OK", "negative_values": "Not OK"},
        {"key": "channel_condition", "label": "Check Condition of Channel for Damage Replace if Required",
         "field_type": "select", "options": "OK, Not OK", "required": True, "standard_value": "OK",
         "negative_values": "Not OK"},
        {"key": "felt_replace", "label": "Felt Should Be Replace With Grease Impregnated Felt & Rivet Properly",
         "field_type": "select", "options": "Done, Not Done", "required": True, "standard_value": "Done",
         "negative_values": "Not Done"},
        {"key": "hovels_assembly_gap", "label": "Check No Gap Before the Assembly of Two Hovels",
         "field_type": "select", "options": "No Gap, Gap Found", "required": True, "standard_value": "No Gap",
         "negative_values": "Gap Found"},
        {"key": "gear_case_cap_intact", "label": "Check Gear Case Cap", "field_type": "select",
         "options": "Intact, Not Intact", "required": True, "standard_value": "Intact",
         "negative_values": "Not Intact"},
        {"key": "ccf_filled", "label": "Fill Up Gear Case With CCF", "field_type": "select",
         "options": "Filled, Not Filled", "required": True, "standard_value": "Shell Cardium Compound",
         "negative_values": "Not Filled"},
        {"key": "rubber_pad_metal_plate_bonding", "label": "Check the Rubber Pad & Metal Plate Bonding for "
         "Intactness", "field_type": "select", "options": "Intact, Not Intact", "required": True,
         "standard_value": "Intact", "negative_values": "Not Intact"},
        {"key": "free_height_elements", "label": "Check Free Height of Elements", "field_type": "numeric_range",
         "required": True, "unit": "mm", "min_value": 183.0, "max_value": 187.0, "decimal_precision": 0,
         "standard_value": "185±2mm, Service Limit-180mm"},
        {"key": "total_height", "label": "Check Total Height", "field_type": "numeric_range", "required": True,
         "unit": "mm", "min_value": 315.0, "max_value": 318.0, "decimal_precision": 0,
         "standard_value": "315 to 318mm, Service Limit-309mm"},
        {"key": "end_plate_thickness", "label": "Thickness Top & Bottom End Plate, 6mm Manganese Steel Liner",
         "field_type": "numeric_range", "required": True, "unit": "mm", "min_value": 64.5, "max_value": 65.0,
         "decimal_precision": 1, "standard_value": "65 to 64.5mm (Each)"},
        {"key": "nose_pad_offset", "label": "OFF Set of Nose Pad", "field_type": "number", "required": True,
         "unit": "mm", "standard_value": "5.0mm"},
        {"key": "nose_pad_parallelism", "label": "Parallelism of Nose Pad", "field_type": "number",
         "required": True, "unit": "mm", "standard_value": "3.0mm"},
        {"builder": _nose_pad_testing_builder},
        {"key": "nose_pad_tm_lug_gap", "label": "Gap Between Nose Pad and Bottom Lug of TM", "field_type": "number",
         "required": True, "unit": "mm", "standard_value": "Should Not Exceed 6.0mm"},
    ]
    add_unit_group_table(add, "gear_case", "Unit", UNITS, activities)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="GC_Conv", template_code="110", technology="CONVENTIONAL",
        template_name="Checksheet for Gear Case & Sandwich Mounting (WAP-4)",
        description="Gear Case & Sandwich Mounting checksheet - WAP-4, Conventional - M4-HR section.",
        build_fn=build,
    )
