"""
Module 40: seeds the AB-Ass_Conv (Axle Box Assembly, WAP-4, Conventional, M4-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_axle_box_assembly_conv_template.py`

Source: pages 5-6 of the supplied WAP-4 checksheet - "Check Sheet for AOH/IOH During Assembly of
Axle Box of WAP-4 Loco", recorded once per Wheel Set (1-6), each with a Pinion End (PE) and
Commutator End (CE) axle box measured/inspected independently, plus a small "Check After Assembly
of Axle Box (As Per SMI No.-216)" table recorded once per axle box (left blank on the reference
sheet whenever not applicable - modelled as optional).

Genuinely distinct sheet from the WAG9HC/WAP-7 Axle Box Mounting template (seed_axle_box_mounting_
template.py / _p7_template.py) - this is the WAP-4-specific assembly procedure with its own
checking points (servo gem grease quantity, roller pitting inspection, felt seal thrust pad) that
do not appear on the 3-Phase sheets at all.
"""
from _m4hr_template_helpers import add_final_remarks, run_seed

WHEEL_SETS = list(range(1, 7))
SIDES = ("PE", "CE")

CHECKS = [
    {"key": "servo_gem_grease", "label": "Apply Fresh Servo Gem Grease to Axle Box and Mount on Axle",
     "field_type": "select", "options": "Applied, Not Applied", "standard_value": "2.75 Kg",
     "negative_values": "Not Applied"},
    {"key": "radial_clearance", "label": "Check Radial Clearance Between Bearing and Inner Race",
     "field_type": "numeric_range", "unit": "mm", "min_value": 0.07, "max_value": 0.20, "decimal_precision": 2},
    {"key": "bearing_make_no", "label": "Bearing Make & No.", "field_type": "text", "standard_value": "NBC/FAG"},
    {"key": "bearing_condition", "label": "Condition of Bearing", "field_type": "select",
     "options": "Replaced, Good", "standard_value": "Good"},
    {"key": "roller_pitting_damage", "label": "Check Each Roller After Cleaning for Pitting Mark and Damage",
     "field_type": "select", "options": "No Pitting/No Damage, Pitting/Damage Found",
     "standard_value": "No Pitting, No Damage", "negative_values": "Pitting/Damage Found"},
    {"key": "roller_casing_rivets_condition", "label": "Check the Condition of Rivets of Roller Casing",
     "field_type": "select", "options": "Good Condition, Not Good Condition", "standard_value": "Good Condition",
     "negative_values": "Not Good Condition"},
    {"key": "spare_parts_torque", "label": "Assemble All Spare Parts as Per Normal Practice and Tightness of "
     "Bolt 12x55, 12x85", "field_type": "select", "options": "Done, Not Done", "standard_value": "By Torque = 9 Kgm",
     "negative_values": "Not Done"},
    {"key": "sealing_ring_intact", "label": "Ensure Sealing Ring Between Axle Box Housing and End Cover",
     "field_type": "select", "options": "Intact, Not Intact", "standard_value": "Intact",
     "negative_values": "Not Intact"},
    {"key": "thrust_pad_replace", "label": "Replace the Rubber Conical Thrust Pad With New for End Axle Boxes",
     "field_type": "select", "options": "Replaced, Not Replaced", "standard_value": "Replaced",
     "negative_values": "Not Replaced"},
]

POST_ASSEMBLY_CHECKS = [
    {"key": "spacing_ring_clamping_plate_clearance", "label": "Radial Clearance Between Outer Spacing Ring and "
     "Clamping Plate on Middle Axle Boxes", "field_type": "number", "unit": "mm", "standard_value": "1.0mm"},
    {"key": "end_cover_housing_clearance", "label": "Minimum Clearance Between Axle Box End Cover and Axle Box "
     "Housing", "field_type": "number", "unit": "mm", "standard_value": "1.0mm"},
    {"key": "thrust_collar_clearance", "label": "Clearance Between Outer Thrust Collar and Inner Thrust Collar",
     "field_type": "numeric_range", "unit": "mm", "min_value": 4.5, "max_value": 6.5, "decimal_precision": 1},
]


def build(add):
    for ws in WHEEL_SETS:
        ws_group = add(f"wheel_set_{ws}", field_label=f"Wheel Set-{ws}", field_type="group", required=False,
                        authority_reference="SMI No.-216")
        for check in CHECKS:
            check_group = add(f"wheel_set_{ws}_{check['key']}", parent=ws_group, field_label=check["label"],
                               field_type="group", required=False, standard_value=check.get("standard_value"))
            for side in SIDES:
                kwargs = {k: v for k, v in check.items() if k not in ("key", "label")}
                add(f"wheel_set_{ws}_{check['key']}_{side.lower()}", parent=check_group, field_label=side,
                    required=True, **kwargs)

    post_group = add("post_assembly_checks", field_label="Check After Assembly of Axle Box (As Per SMI No.-216)",
                      field_type="group", required=False, authority_reference="SMI No.-216")
    for check in POST_ASSEMBLY_CHECKS:
        kwargs = {k: v for k, v in check.items() if k not in ("key", "label")}
        add(check["key"], parent=post_group, field_label=check["label"], required=False, **kwargs)

    add("axle_box_fitted_by", field_label="Axle Box Fitted By", field_type="text", required=False)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="AB-Ass_Conv", template_code="106", technology="CONVENTIONAL",
        template_name="Checksheet for AOH/IOH During Assembly of Axle Box (WAP-4)",
        description="Axle Box Assembly checksheet - WAP-4, Conventional - M4-HR section.",
        build_fn=build,
    )
