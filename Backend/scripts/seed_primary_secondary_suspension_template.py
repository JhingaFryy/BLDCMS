"""
Module 40: seeds the P&S Susp (Primary & Secondary Suspension Lateral & Vertical Clearance,
WAG9HC, 3-Phase, M4-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_primary_secondary_suspension_template.py`

Source: page 18 of the supplied WAG-9HC checksheet - "Primary & Secondary Suspension Lateral &
Vertical Clearance" (As per RDSO/TC/0082 Rev.-3, date 18.02.26). Three sub-tables: primary
lateral clearance (per wheel number 1-12, A/B readings), primary vertical clearance (per wheel
number 1-12, single reading), and secondary lateral/vertical clearance (per axle-pair group).
"""
from _m4hr_template_helpers import add_final_remarks, run_seed

AUTHORITY = "RDSO/TC/0082 Rev.-3, dt. 18.02.26"
WHEEL_NUMBERS = list(range(1, 13))
SECONDARY_GROUPS = ["1-3", "2-4", "4-11", "10-12"]


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
        equipment_code="P&S Susp", template_code="70", technology="3_PHASE",
        template_name="Checksheet for Primary & Secondary Suspension Clearance",
        description="Primary & Secondary Suspension Lateral & Vertical Clearance checksheet - WAG9HC, "
                     "3-Phase - M4-HR section.",
        build_fn=build,
    )
