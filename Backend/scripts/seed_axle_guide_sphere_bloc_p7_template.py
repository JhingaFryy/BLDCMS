"""
Module 40: seeds the AGS_P7 (Axle Guide Sphere Bloc, WAP-7, 3-Phase, M4-HR section) checksheet
template.

Run once: `venv/bin/python scripts/seed_axle_guide_sphere_bloc_p7_template.py`

Source: page 14 of the supplied WAP-7 checksheet - "Axle Guide Sphere Bloc", 5 schedule
activities repeated once per axle guide (Axle Guide-1 through Axle Guide-12). Deliberately
independent from the WAG9HC Axle Guide Sphere Bloc template - this sheet has only 5 checking
points, NOT 6: WAG9HC's item 6 ("Applied torque of 665Nm to bolt size 24x300") is absent here
entirely, and item 5's own wording/standard differs ("Replace FS Nuts with new" / Replaced, vs
WAG9HC's "Replace FS Nut M24 with new" / New-Old). Do not merge with the WAG9HC template.
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
        {"key": "spheri_bloc_make_year", "label": "Make & Year of Sphere Bloc (Imported Sphere Bloc to Be "
         "Provided as Per RDSO/TC-142)", "field_type": "text", "required": True, "standard_value": "Noted",
         "authority_reference": "RDSO/TC-142"},
        {"key": "fs_nuts_replace", "label": "Replace FS Nuts With New", "field_type": "select",
         "options": "Replaced, Not Replaced", "required": True, "standard_value": "Replaced",
         "negative_values": "Not Replaced"},
    ]
    add_unit_group_table(add, "ags", "Axle Guide", AXLE_GUIDES, activities)
    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="AGS_P7", template_code="91", technology="3_PHASE",
        template_name="Checksheet for Axle Guide Sphere Bloc (WAP-7)",
        description="Axle Guide Sphere Bloc checksheet - WAP-7, 3-Phase - M4-HR section.",
        build_fn=build,
    )
