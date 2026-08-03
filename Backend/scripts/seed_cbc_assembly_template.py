"""
Module 40: seeds the CBC ("E" Type Centre Buffer Coupler Assembly, WAG9HC, 3-Phase, M4-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_cbc_assembly_template.py`

Source: page 27 of the supplied WAG-9HC checksheet - "'E' Type Centre Buffer Coupler (CBC)
Assembly", 13 schedule activities recorded once per cab (Cab-1/Cab-2). Item 1's five MPT crack
checks (coupler body, knuckle, knuckle pin, clevis, clevis pin) are five distinct checkpoints on
the sheet, so each keeps its own field rather than being merged into one.
"""
from _m4hr_template_helpers import add_final_remarks, run_seed

MPT_PARTS = [
    ("coupler_body", "CBC Coupler Body"),
    ("knuckle", "Knuckle"),
    ("knuckle_pin", "Knuckle Pin"),
    ("clevis", "Clevis"),
    ("clevis_pin", "Clevis Pin"),
]


def build(add):
    for cab in ("Cab-1", "Cab-2"):
        cab_key = cab.lower().replace("-", "_")
        cab_group = add(f"cbc_{cab_key}", field_label=cab, field_type="group", required=False)

        mpt_group = add(f"cbc_{cab_key}_mpt_crack_check", parent=cab_group, field_label="Check for Any Crack by "
            "MPT Test of CBC Assembly Items", field_type="group", required=False)
        for key, label in MPT_PARTS:
            add(f"cbc_{cab_key}_mpt_{key}", parent=mpt_group, field_label=label, field_type="select",
                options="OK, Crack Found", required=True, standard_value="OK", negative_values="Crack Found")

        add(f"cbc_{cab_key}_knuckle_nose_wear", parent=cab_group, field_label="Checking of Knuckle Nose Wear & "
            "Stretch With Go-No Go Gauge (Gauge No-3)", field_type="select", options="Checked, Not Checked",
            required=True, standard_value="New - 25.0mm, Cond.- 9.5mm", negative_values="Not Checked")
        add(f"cbc_{cab_key}_knuckle_coupler_gap", parent=cab_group, field_label="Checking Gap Between Knuckle "
            "Nose & Coupler by Gauge No 1 & 2", field_type="select", options="Checked, Not Checked", required=True,
            standard_value="Gauge 1-135.0mm, Gauge 2-130.0mm (AOH)", negative_values="Not Checked")
        add(f"cbc_{cab_key}_knuckle_pin_diameter", parent=cab_group, field_label="Check Knuckle Pin Diameter",
            field_type="numeric_range", required=True, unit="mm", min_value=38.0, max_value=41.2,
            decimal_precision=1, standard_value="New - 41.2mm, Service Limit - 38.0mm")
        add(f"cbc_{cab_key}_clevis_pin_diameter", parent=cab_group, field_label="Check Clevis Pin Diameter",
            field_type="numeric_range", required=True, unit="mm", min_value=36.0, max_value=38.0,
            decimal_precision=1, standard_value="New - 38.0mm, Service Limit - 36.0mm")
        add(f"cbc_{cab_key}_anti_creep_test", parent=cab_group, field_label="Check Working of CBC & Anti Creep "
            "Test", field_type="select", options="OK, Not OK", required=True, standard_value="OK",
            negative_values="Not OK")
        add(f"cbc_{cab_key}_operating_handle", parent=cab_group, field_label="Check Condition & Proper Working "
            "of CBC Operating Handle", field_type="select", options="OK, Not OK", required=True,
            standard_value="OK", negative_values="Not OK")
        add(f"cbc_{cab_key}_yoke_draft_gear", parent=cab_group, field_label="Check for Any Crack and Damage in "
            "Yoke & Draft Gear", field_type="select", options="OK, Crack/Damage Found", required=True,
            standard_value="OK", negative_values="Crack/Damage Found")
        add(f"cbc_{cab_key}_shank_lateral_movement", parent=cab_group, field_label="Check Free Lateral Movement "
            "of CBC Shank", field_type="select", options="OK, Not OK", required=True, standard_value="OK",
            negative_values="Not OK")
        add(f"cbc_{cab_key}_striker_casting_liner", parent=cab_group, field_label="Check Condition of Striker "
            "Casting Liner", field_type="numeric_range", required=True, unit="mm", min_value=2.0, max_value=8.0,
            decimal_precision=1, standard_value="New - 8.0mm, Cond.- 2.0mm")
        add(f"cbc_{cab_key}_shank_wear_liner", parent=cab_group, field_label="Check Condition of Shank Wear "
            "Liner", field_type="numeric_range", required=True, unit="mm", min_value=1.0, max_value=6.0,
            decimal_precision=1, standard_value="New - 6.0mm, Cond.- 1.0mm")
        add(f"cbc_{cab_key}_locking_pin_diameter", parent=cab_group, field_label="The Diameter of "
            "Retracing/Locking Pin & Condition", field_type="number", required=True, unit="mm",
            standard_value="Diameter - 16.0mm")
        add(f"cbc_{cab_key}_hand_brake", parent=cab_group, field_label="Hand Brake", field_type="textarea",
            required=False)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="CBC", template_code="77", technology="3_PHASE",
        template_name="Checksheet for E-Type Centre Buffer Coupler Assembly",
        description="'E' Type Centre Buffer Coupler (CBC) Assembly checksheet - WAG9HC, 3-Phase - M4-HR section.",
        build_fn=build,
    )
