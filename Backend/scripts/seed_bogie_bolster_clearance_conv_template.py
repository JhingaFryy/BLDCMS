"""
Module 40: seeds the B&B_Conv (Bogie & Bolster Clearance, WAP-4, Conventional, M4-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_bogie_bolster_clearance_conv_template.py`

Source: page 22 of the supplied WAP-4 checksheet - "Check Sheet for Bogie & Bolster Clearance"
(Ref: TC No.-ELRS/TC/0059-2000/Rev.'0'), combining three distinct measurement blocks: (1) four
bolster/bogie clearance checks recorded per cab, each with a Driver-side (DVR) and Assistant
Driver-side (ADVR) reading; (2) piston stroke and brake-block/wheel gap recorded per wheel number
(1-12) - the reference sheet prints no explicit standard range for these two (all recorded values
are uniform, so both are modelled as unstandardised "number" fields rather than inventing a range
the source doesn't show); (3) post-buffer-lowering CBC/buffer height recorded per cab
(1030.0-1105.0mm, as literally stated on this sheet - note this is a narrower/different range than
the "(1105.0-1035.0)mm" used on the WAG9HC/WAP-7 Piston Stroke templates' buffer height fields).

Genuinely distinct sheet from the WAG9HC/WAP-7 "Piston Stroke" templates - this WAP-4 sheet has no
brake-block-and-wheel-gap standard, uses "Wheel Number" (not wheel-pair groups) for piston stroke,
and adds the DVR/ADVR bolster-clearance block that has no 3-Phase equivalent equipment at all.
"""
from _m4hr_template_helpers import add_final_remarks, add_unit_group_table, run_seed

WHEEL_NUMBERS = list(range(1, 13))
AUTHORITY = "ELRS/TC/0059-2000/Rev.'0'"


def build(add):
    clearance_checks = [
        ("lateral_clearance_bolster_bogie_pad", "Lateral Clearance Between Bolster Pad and Bogie Pad",
         31.0, 34.0),
        ("vertical_clearance_bolster_bogie", "Vertical Clearance Between Bolster and Bogie", 29.0, 35.0),
        ("combined_longitudinal_bolster_bogie", "Combined Longitudinal Between Two Traction End of Bolster and "
         "Two Upright Pedestals of Bogie", 2.5, 3.5),
        ("vertical_clearance_u_bracket_bolster", "Vertical Clearance Between Under Frame 'U' Bracket and "
         "Bolster", 10.0, 11.5),
    ]
    for cab in ("Cab-1", "Cab-2"):
        cab_key = cab.lower().replace("-", "_")
        cab_group = add(f"bb_{cab_key}", field_label=cab, field_type="group", required=False,
                         authority_reference=AUTHORITY)
        for side in ("DVR", "ADVR"):
            side_group = add(f"bb_{cab_key}_{side.lower()}", parent=cab_group, field_label=side,
                              field_type="group", required=False)
            for key, label, min_v, max_v in clearance_checks:
                add(f"bb_{cab_key}_{side.lower()}_{key}", parent=side_group, field_label=label,
                    field_type="numeric_range", required=True, unit="mm", min_value=min_v, max_value=max_v,
                    decimal_precision=1)

    piston_activities = [
        {"key": "piston_stroke", "label": "Piston Stroke", "field_type": "number", "required": True, "unit": "mm",
         "standard_value": "As per shed practice"},
        {"key": "brake_block_wheel_gap", "label": "Gap Between Brake Block & Wheel", "field_type": "number",
         "required": True, "unit": "mm", "standard_value": "Noted"},
    ]
    add_unit_group_table(add, "piston_stroke", "Wheel Number", WHEEL_NUMBERS, piston_activities)

    for cab in ("Cab-1", "Cab-2"):
        cab_key = cab.lower().replace("-", "_")
        height_group = add(f"post_lowering_height_{cab_key}", field_label=cab, field_type="group", required=False,
                            standard_value="1105.0mm to 1030.0mm")
        add(f"post_lowering_height_{cab_key}_loco_pilot", parent=height_group, field_label="Loco Pilot Side",
            field_type="numeric_range", required=True, unit="mm", min_value=1030.0, max_value=1105.0,
            decimal_precision=0)
        add(f"post_lowering_height_{cab_key}_asst_loco_pilot", parent=height_group,
            field_label="Asst. Loco Pilot Side", field_type="numeric_range", required=True, unit="mm",
            min_value=1030.0, max_value=1105.0, decimal_precision=0)
        add(f"post_lowering_height_{cab_key}_cbc_height", parent=height_group, field_label="CBC Height",
            field_type="numeric_range", required=True, unit="mm", min_value=1030.0, max_value=1105.0,
            decimal_precision=0)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="B&B_Conv", template_code="118", technology="CONVENTIONAL",
        template_name="Checksheet for Bogie & Bolster Clearance (WAP-4)",
        description="Bogie & Bolster Clearance checksheet - WAP-4, Conventional - M4-HR section.",
        build_fn=build,
    )
