"""
Module 40: seeds the CPivot_Conv (Centre Pivot of Loco Body, WAP-4, Conventional, M4-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_center_pivot_conv_template.py`

Source: page 20 of the supplied WAP-4 checksheet - "Check Sheet for AOH/IOH Center Pivot of Loco
Body WAP-4 Loco", recorded once per cab (Cab-1/Cab-2). No equivalent equipment exists for
WAG9HC/WAP-7 - the loco-body centre pivot inspection is specific to the WAP-4/Conventional bogie
design.
"""
from _m4hr_template_helpers import add_final_remarks, run_seed


def build(add):
    for cab in ("Cab-1", "Cab-2"):
        cab_key = cab.lower().replace("-", "_")
        cab_group = add(f"cpivot_{cab_key}", field_label=cab, field_type="group", required=False)

        add(f"cpivot_{cab_key}_crack_check", parent=cab_group, field_label="Centre Pivot to Be Check of Any Crack "
            "by MPT/DTP", field_type="select", options="Checked, Crack Found", required=True,
            standard_value="Checked", negative_values="Crack Found")
        add(f"cpivot_{cab_key}_base_plate_crack_check", parent=cab_group, field_label="Centre Pivot Bottom Base "
            "Plate for Any Crack", field_type="select", options="Checked, Crack Found", required=True,
            standard_value="Checked", negative_values="Crack Found")
        add(f"cpivot_{cab_key}_crack_welding_done", parent=cab_group, field_label="If Crack Welding Done "
            "(As per RDSO/2007/MC/46)", field_type="select", options="Checked, Not Applicable", required=False,
            standard_value="Checked")
        add(f"cpivot_{cab_key}_pin_outer_diameter", parent=cab_group, field_label="Measure Pin Outer Diameter",
            field_type="numeric_range", required=True, unit="mm", min_value=454.5, max_value=456.5,
            decimal_precision=1)
        add(f"cpivot_{cab_key}_dust_guard_provided", parent=cab_group, field_label="Provide Centre Pivot Dust "
            "Guard", field_type="select", options="Provided, Not Provided", required=True,
            standard_value="Provided", negative_values="Not Provided")
        add(f"cpivot_{cab_key}_j_clamps_pins_condition", parent=cab_group, field_label="Check Condition of "
            "J-Clamps and Pins", field_type="select", options="Checked, Not Checked", required=True,
            standard_value="Checked", negative_values="Not Checked")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="CPivot_Conv", template_code="116", technology="CONVENTIONAL",
        template_name="Checksheet for AOH/IOH Centre Pivot of Loco Body (WAP-4)",
        description="Centre Pivot of Loco Body checksheet - WAP-4, Conventional - M4-HR section.",
        build_fn=build,
    )
