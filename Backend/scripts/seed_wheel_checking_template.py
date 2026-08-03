"""
Module 40: seeds the WC (Wheel Checking, WAG9HC, 3-Phase, M4-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_wheel_checking_template.py`

Source: page 6 of the supplied WAG-9HC checksheet - "Wheel Checking" (HQ TC-333, RDSO Drawing
No.-EL/3.2.108 dt.-13.3.26), 8 schedule activities repeated once per wheel set (W/S-1 through
W/S-6).
"""
from _m4hr_template_helpers import add_final_remarks, add_unit_group_table, run_seed

WHEEL_SETS = [1, 2, 3, 4, 5, 6]

AUTHORITY = "RDSO Drawing No.-EL/3.2.108 dt.-13.3.26"


def _defect_field(key, label, ok_word):
    return {"key": key, "label": label, "field_type": "select",
            "options": f"{ok_word}, Wheel Turning to Be Done", "required": True,
            "standard_value": ok_word, "authority_reference": AUTHORITY,
            "negative_values": "Wheel Turning to Be Done"}


def build(add):
    activities = [
        {"key": "crack_check", "label": "Examine All Wheels Visually for Any Crack", "field_type": "select",
         "options": "No Cracks, Crack Found", "required": True, "standard_value": "No cracks",
         "authority_reference": AUTHORITY, "negative_values": "Crack Found"},
        _defect_field("flats_check", "Examine All Wheels Visually for Any Flats", "No Flats"),
        _defect_field("cavities_check", "Examine All Wheels Visually for Any Cavities", "No Cavities"),
        _defect_field("metal_buildup_check", "Examine All Wheels Visually for Any Metal Build Ups", "No Metal Build Ups"),
        _defect_field("scoring_grooving_check", "Examine All Wheels Visually for Any Scoring and Grooving", "No Scoring"),
        {"key": "sprag_hole_radius", "label": "R-3 Radius on Sprag Hole Inner and Outer", "field_type": "select",
         "options": "Checked, Not Checked", "required": True, "standard_value": "Checked",
         "authority_reference": AUTHORITY, "negative_values": "Not Checked"},
        {"key": "sprag_hole_dpt_mpt", "label": "DPT/MPT of Sprag Hole Area", "field_type": "select",
         "options": "Done, Not Done", "required": True, "standard_value": "Done",
         "authority_reference": AUTHORITY, "negative_values": "Not Done"},
        {"key": "rim_area_dpt_mpt", "label": "DPT/MPT of Both Side Rim Area", "field_type": "select",
         "options": "Done, Not Done", "required": True, "standard_value": "Done",
         "authority_reference": AUTHORITY, "negative_values": "Not Done"},
    ]
    add_unit_group_table(add, "wc", "Wheel Set", WHEEL_SETS, activities)
    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="WC", template_code="61", technology="3_PHASE",
        template_name="Checksheet for Wheel Checking",
        description="Wheel Checking checksheet - WAG9HC, 3-Phase - M4-HR section.",
        build_fn=build,
    )
