"""
Module 40: seeds the AGS (Axle Guide Sphere Bloc, WAG9HC, 3-Phase, M4-HR section) checksheet
template.

Run once: `venv/bin/python scripts/seed_axle_guide_sphere_bloc_template.py`

Source: page 16 of the supplied WAG-9HC checksheet - "Axle Guide Sphere Bloc", 6 schedule
activities repeated once per axle guide (Axle Guide-1 through Axle Guide-12).
"""
from _m4hr_template_helpers import add_final_remarks, add_unit_group_table, run_seed

AXLE_GUIDES = list(range(1, 13))
DRAWING_NO = "Drawing No.-1209-01-218-003"


def build(add):
    activities = [
        {"key": "spheri_bloc_removed", "label": "Remove the Axle Guide Spheri Blocs", "field_type": "select",
         "options": "Removed, Not Removed", "required": True, "standard_value": "Removed",
         "negative_values": "Not Removed"},
        {"key": "bore_diameter", "label": "Check the Bore Diameter of Axle Guide", "field_type": "number",
         "required": True, "unit": "mm", "standard_value": "110.0mm", "authority_reference": DRAWING_NO},
        {"key": "spheri_bloc_condition", "label": "Condition of Sphere Bloc (Must Change-IOH)",
         "field_type": "select", "options": "New, Old", "required": True, "standard_value": "New/Old"},
        {"key": "spheri_bloc_make_year", "label": "Make & Year of Sphere Bloc", "field_type": "text",
         "required": True, "standard_value": "Noted"},
        {"key": "fs_nut_replace", "label": "Replace FS Nut M24 With New", "field_type": "select",
         "options": "New, Old", "required": True, "standard_value": "New/Old"},
        {"key": "bolt_torque_applied", "label": "Applied Torque of 665Nm to Bolt Size 24x300",
         "field_type": "select", "options": "Applied, Not Applied", "required": True,
         "standard_value": "Applied", "negative_values": "Not Applied"},
    ]
    add_unit_group_table(add, "ags", "Axle Guide", AXLE_GUIDES, activities)
    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="AGS", template_code="68", technology="3_PHASE",
        template_name="Checksheet for Axle Guide Sphere Bloc",
        description="Axle Guide Sphere Bloc checksheet - WAG9HC, 3-Phase - M4-HR section.",
        build_fn=build,
    )
