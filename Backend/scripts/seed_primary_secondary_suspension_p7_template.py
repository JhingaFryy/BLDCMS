"""
Module 40: seeds the P&S Susp_P7 (Primary & Secondary Suspension Lateral & Vertical Clearance,
WAP-7, 3-Phase, M4-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_primary_secondary_suspension_p7_template.py`

Source: page 16 of the supplied WAP-7 checksheet - "Primary & Secondary Suspension Lateral &
Vertical Clearance" (As per RDSO/TC/0082 Rev.-3, date 18.02.26) - same clearance ranges as the
WAG9HC sheet, but the secondary lateral/vertical clearance is grouped by wheel positions
1-3/2-4/9-11/10-12 on this sheet (vs WAG9HC's 1-3/2-4/4-11/10-12) - each sheet's own printed
grouping is used rather than assuming they match.
"""
from _m4hr_template_helpers import add_final_remarks, run_seed

AUTHORITY = "RDSO/TC/0082 Rev.-3, dt. 18.02.26"
WHEEL_NUMBERS = list(range(1, 13))
SECONDARY_GROUPS = ["1-3", "2-4", "9-11", "10-12"]


def build(add):
    lateral_section = add("primary_lateral_clearance", field_label="Primary Lateral Clearance (15-22)",
                           field_type="group", required=False, standard_value="(15-22)mm",
                           authority_reference=AUTHORITY)
    for w in WHEEL_NUMBERS:
        w_group = add(f"primary_lateral_w{w}", parent=lateral_section, field_label=f"Wheel No. {w}",
                       field_type="group", required=False)
        add(f"primary_lateral_w{w}_a", parent=w_group, field_label="A", field_type="numeric_range",
            required=True, unit="mm", min_value=15.0, max_value=22.0, decimal_precision=2)
        add(f"primary_lateral_w{w}_b", parent=w_group, field_label="B", field_type="numeric_range",
            required=True, unit="mm", min_value=15.0, max_value=22.0, decimal_precision=2)

    vertical_section = add("primary_vertical_clearance", field_label="Primary Vertical Clearance (27-45)",
                            field_type="group", required=False, standard_value="(27-45)mm",
                            authority_reference=AUTHORITY)
    for w in WHEEL_NUMBERS:
        add(f"primary_vertical_w{w}", parent=vertical_section, field_label=f"Wheel No. {w}",
            field_type="numeric_range", required=True, unit="mm", min_value=27.0, max_value=45.0,
            decimal_precision=2)

    secondary_section = add("secondary_clearance", field_label="Secondary Lateral and Vertical Clearance",
                             field_type="group", required=False, authority_reference=AUTHORITY)
    for grp in SECONDARY_GROUPS:
        key_suffix = grp.replace("-", "_")
        grp_group = add(f"secondary_clearance_{key_suffix}", parent=secondary_section,
                         field_label=f"W. No. {grp}", field_type="group", required=False)
        add(f"secondary_lateral_{key_suffix}", parent=grp_group, field_label="Secondary Lateral Clearance (45-55)",
            field_type="numeric_range", required=True, unit="mm", min_value=45.0, max_value=55.0,
            decimal_precision=2)
        add(f"secondary_vertical_{key_suffix}", parent=grp_group, field_label="Secondary Vertical Clearance (32-60)",
            field_type="numeric_range", required=True, unit="mm", min_value=32.0, max_value=60.0,
            decimal_precision=2)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="P&S Susp_P7", template_code="93", technology="3_PHASE",
        template_name="Checksheet for Primary & Secondary Suspension Clearance (WAP-7)",
        description="Primary & Secondary Suspension Lateral & Vertical Clearance checksheet - WAP-7, "
                     "3-Phase - M4-HR section.",
        build_fn=build,
    )
