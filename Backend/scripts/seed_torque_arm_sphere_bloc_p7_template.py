"""
Module 40: seeds the TAS_P7 (Torque Arm Sphere Bloc, WAP-7, 3-Phase, M4-HR section) checksheet
template.

Run once: `venv/bin/python scripts/seed_torque_arm_sphere_bloc_p7_template.py`

Source: page 13 of the supplied WAP-7 checksheet - "Torque Arm Sphere Bloc", 6 schedule
activities repeated once per torque arm (T/Arm-1 through T/Arm-6) - identical shape and standard
values to the WAG9HC Torque Arm Sphere Bloc sheet.
"""
from _m4hr_template_helpers import add_final_remarks, add_unit_group_table, run_seed

TORQUE_ARMS = list(range(1, 7))
DRAWING_NO = "Drawing No.-1209-01-218-003"


def build(add):
    activities = [
        {"key": "spheri_bloc_removed", "label": "Remove the Torque Arm Spheri Blocs", "field_type": "select",
         "options": "Removed, Not Removed", "required": True, "standard_value": "Removed",
         "negative_values": "Not Removed"},
        {"key": "bore_diameter", "label": "Check the Bore Diameter of Torque Arm", "field_type": "number",
         "required": True, "unit": "mm", "standard_value": "110.0mm", "authority_reference": DRAWING_NO},
        {"key": "spheri_bloc_condition", "label": "Condition of Sphere Bloc (Must Change-TOH/IOH)",
         "field_type": "select", "options": "New, Old", "required": True, "standard_value": "New/Old"},
        {"key": "spheri_bloc_make_year", "label": "Make & Year of Sphere Bloc (Imported Spheri Bloc to Be "
         "Provided as Per RDSO/TC-142)", "field_type": "text", "required": True, "standard_value": "Noted",
         "authority_reference": "RDSO/TC-142"},
        {"key": "support_plate_bolt_tightness", "label": "Check the Tightness of Torque Arm Support Plate Bolt. "
         "Top Size: 24x110, Bottom Size: 24x100, Torque: 665Nm, Property: 8.8", "field_type": "select",
         "options": "Ensured, Not Ensured", "required": True, "standard_value": "Ensured",
         "negative_values": "Not Ensured"},
        {"key": "steel_lock_nut_replace", "label": "Replace the Steel Lock Nut (New to Provide)",
         "field_type": "select", "options": "Replaced, Not Replaced", "required": True,
         "standard_value": "Replaced", "negative_values": "Not Replaced"},
    ]
    add_unit_group_table(add, "tas", "Torque Arm", TORQUE_ARMS, activities)
    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="TAS_P7", template_code="90", technology="3_PHASE",
        template_name="Checksheet for Torque Arm Sphere Bloc (WAP-7)",
        description="Torque Arm Sphere Bloc checksheet - WAP-7, 3-Phase - M4-HR section.",
        build_fn=build,
    )
