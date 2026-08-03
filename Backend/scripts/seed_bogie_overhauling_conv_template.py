"""
Module 40: seeds the BG-1_Conv / BG-2_Conv (Bogie Overhauling, WAP-4, Conventional, M4-HR section)
checksheet templates.

Run once: `venv/bin/python scripts/seed_bogie_overhauling_conv_template.py`

Source: pages 1 & 3 of the supplied WAP-4 checksheet - "Check Sheet for Bogie Overhauling"
(pre-assembly), one per bogie frame (Bogie frame No. 1 covers axle-box positions 1-6, Bogie frame
No. 2 covers positions 7-12 - WAP-4 is a Co-Co, 6-axle locomotive). Both bogie frames share an
identical structure: a crack inspection (type/location/critical zone/length) followed by two
per-position measurement tables (longitudinal pedestal spacing, bogie nose suspension).

Deliberately independent from the WAG9HC/WAP-7 "Bogie Frame Overhauling" templates
(seed_bogie_overhauling_template.py / _p7_template.py) - those record an entirely different
18-item brake-rigging/piston-housing/damper-bracket checklist with no measurement values at all,
reflecting the WAP-4/Conventional bogie's different (pedestal-liner, pin-suspended) design; this
sheet has no brake-rigging content whatsoever.
"""
from _m4hr_template_helpers import add_final_remarks, add_unit_group_table, run_seed


def build(positions):
    def _build(add):
        add("bogie_frame_number", field_label="Bogie Frame Number", field_type="text", required=True,
            standard_value="Noted")
        add("make", field_label="Make", field_type="text", required=False, standard_value="Noted")
        add("mfg_year", field_label="MFG Year", field_type="text", required=False, standard_value="Noted")
        add("points", field_label="Points", field_type="text", required=False)

        crack_group = add("crack_inspection", field_label="Crack Inspection", field_type="group", required=False)
        add("bogie_frame_cleaned", parent=crack_group, field_label="Cleaning the Bogie Frame in Washing Tank",
            field_type="select", options="Cleaned, Not Cleaned", required=True, standard_value="Cleaned",
            negative_values="Not Cleaned")
        add("crack_rdpt_mpt_check", parent=crack_group, field_label="Check Crackness at Bottom and Top Portion "
            "by RDPT Method or MPT", field_type="select", options="Checked, Crack Found", required=True,
            standard_value="Checked", negative_values="Crack Found")
        add("crack_length_recorded", parent=crack_group, field_label="Record the Length of Crack in Various "
            "Zones", field_type="select", options="Recorded, Not Applicable", required=False,
            standard_value="Recorded")
        add("crack_type", parent=crack_group, field_label="Type Crack", field_type="select", options="New, Old",
            required=False)
        add("crack_brief_description", parent=crack_group, field_label="Brief Description", field_type="textarea",
            required=False)
        add("crack_location", parent=crack_group, field_label="Location", field_type="textarea", required=False)
        add("crack_critical_zones", parent=crack_group, field_label="Critical Zones (1 to 5)", field_type="text",
            required=False)
        add("crack_length_value", parent=crack_group, field_label="Length of Crack", field_type="text",
            required=False)

        pedestal_activities = [
            {"key": "longitudinal_pedestal_spacing", "label": "Longitudinal Pedestal Spacing With Liners",
             "field_type": "numeric_range", "required": True, "unit": "mm", "min_value": 338.35,
             "max_value": 339.20, "decimal_precision": 2, "standard_value": "WAP-4 With Liner: 338.35-339.20mm"},
        ]
        add_unit_group_table(add, "pedestal_spacing", "Position", positions, pedestal_activities)

        nose_suspension_activities = [
            {"key": "bogie_nose_suspension", "label": "Bogie Nose Suspension From Liner MPMI 36/37",
             "field_type": "number", "required": True, "unit": "mm",
             "standard_value": "304 +0.00/-0.75mm (MPMI 36/37)"},
        ]
        add_unit_group_table(add, "nose_suspension", "Position", positions, nose_suspension_activities)

        add_final_remarks(add)
    return _build


if __name__ == "__main__":
    run_seed(
        equipment_code="BG-1_Conv", template_code="102", technology="CONVENTIONAL",
        template_name="Checksheet for Bogie-1 Overhauling (WAP-4)",
        description="Bogie Overhauling checksheet - WAP-4, Conventional - M4-HR section.",
        build_fn=build([1, 2, 3, 4, 5, 6]),
    )
    run_seed(
        equipment_code="BG-2_Conv", template_code="103", technology="CONVENTIONAL",
        template_name="Checksheet for Bogie-2 Overhauling (WAP-4)",
        description="Bogie Overhauling checksheet - WAP-4, Conventional - M4-HR section.",
        build_fn=build([7, 8, 9, 10, 11, 12]),
    )
