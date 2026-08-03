"""
Module 40: seeds the GC (Gear Case, WAG9HC, 3-Phase, M4-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_gear_case_template.py`

Source: page 14 of the supplied WAG-9HC checksheet - "Gear Case", 8 schedule activities repeated
once per gear case (Gear Case No.-1 through No.-6).
"""
from _m4hr_template_helpers import add_final_remarks, add_unit_group_table, run_seed

GEAR_CASES = list(range(1, 7))


def build(add):
    activities = [
        {"key": "oil_removed_cleaned", "label": "Remove Oil and Clean the Gear Case", "field_type": "select",
         "options": "Cleaned, Not Cleaned", "required": True, "standard_value": "Cleaned",
         "negative_values": "Not Cleaned"},
        {"key": "bolt_breakage_check", "label": "Check Holes of Gear Case for Bolt Breakage", "field_type": "select",
         "options": "Checked, Not Checked", "required": True, "standard_value": "Checked",
         "negative_values": "Not Checked"},
        {"key": "breather_cap_cleaned", "label": "Remove the Breather Cap and Clean", "field_type": "select",
         "options": "Cleaned, Not Cleaned", "required": True, "standard_value": "Cleaned",
         "negative_values": "Not Cleaned"},
        {"key": "breather_gasket_replace", "label": "Replace the Breather Gasket With New", "field_type": "select",
         "options": "Replaced, Not Replaced", "required": True, "standard_value": "Replaced",
         "negative_values": "Not Replaced"},
        {"key": "oil_cap_drain_cock", "label": "Check Oil Filling Cap and Drain Cock", "field_type": "select",
         "options": "Checked, Not Checked", "required": True, "standard_value": "Checked",
         "negative_values": "Not Checked"},
        {"key": "sight_glass_clean", "label": "Check and Clean Gear Case Oil Sight Glass", "field_type": "select",
         "options": "Checked, Not Checked", "required": True, "standard_value": "Checked",
         "negative_values": "Not Checked"},
        {"key": "magnetic_sealing_plug_rtv", "label": "Ensure Tightness of Magnetic Sealing Plug & Oil Filling "
         "Cap and Apply RTV", "field_type": "select", "options": "Ensured, Not Ensured", "required": True,
         "standard_value": "Ensured", "negative_values": "Not Ensured"},
        {"key": "gear_case_bolt_property", "label": "Property and Make of Gear Case Bolts (Hex Head Screw-16x200mm, "
         "12x30mm, 12x70mm)", "field_type": "text", "required": True, "standard_value": "Noted"},
    ]
    add_unit_group_table(add, "gc", "Gear Case", GEAR_CASES, activities)
    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="GC", template_code="66", technology="3_PHASE",
        template_name="Checksheet for Gear Case",
        description="Gear Case checksheet - WAG9HC, 3-Phase - M4-HR section.",
        build_fn=build,
    )
