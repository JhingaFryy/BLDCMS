"""
Module 40: seeds the TM-Ass_Conv (TM Assembly on Wheel Set, WAP-4, Conventional, M4-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_tm_assembly_wheelset_conv_template.py`

Source: page 15 of the supplied WAP-4 checksheet - "Check Sheet TM Assembly on Wheel Set of
WAP-4", recorded once per traction motor (TM-1 through TM-6): TM number/staff who fitted it, axle
cap bolt torque, back lash after TM assembly (Hitachi spec), and a B/G (bearing/gearcase) serial
number noted at the foot of the sheet.
"""
from _m4hr_template_helpers import add_final_remarks, run_seed

TM_UNITS = list(range(1, 7))


def build(add):
    for tm in TM_UNITS:
        tm_group = add(f"tm_{tm}", field_label=f"TM-{tm}", field_type="group", required=False)
        add(f"tm_{tm}_number", parent=tm_group, field_label="TM Number", field_type="text", required=True,
            standard_value="Noted")
        add(f"tm_{tm}_staff_name", parent=tm_group, field_label="Staff Name", field_type="text", required=False)
        add(f"tm_{tm}_axle_cap_bolt_torque", parent=tm_group, field_label="Check Tightness of Axle Cap Bolt by "
            "Torque Wrench M36 (SMI 205) (36x200-TAO/TAOCHI TM) (36x110-HITACHI TM)", field_type="numeric_range",
            required=True, unit="kg", min_value=121.0, max_value=145.0, decimal_precision=0,
            authority_reference="SMI-205")
        add(f"tm_{tm}_back_lash", parent=tm_group, field_label="Check the Back Lash After Traction Motor Assembly "
            "With Wheel Set (SMI-160) With Feeler Gauge or Dial Gauge of 0.01mm (Followed With Feeler Gauge)",
            field_type="numeric_range", required=True, unit="mm", min_value=0.3, max_value=1.2,
            decimal_precision=2, standard_value="Hitachi: 0.3 to 1.2mm", authority_reference="SMI-160")
        add(f"tm_{tm}_bg_no", parent=tm_group, field_label="B/G No.", field_type="text", required=False,
            standard_value="Noted")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="TM-Ass_Conv", template_code="111", technology="CONVENTIONAL",
        template_name="Checksheet for TM Assembly on Wheel Set (WAP-4)",
        description="TM Assembly on Wheel Set checksheet - WAP-4, Conventional - M4-HR section.",
        build_fn=build,
    )
