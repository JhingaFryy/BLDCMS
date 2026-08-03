"""
Module 40: seeds the SB_CG_RG (Side Buffer, Cattle Guard & Rail Guard, WAG9HC, 3-Phase, M4-HR
section) checksheet template.

Run once: `venv/bin/python scripts/seed_side_buffer_cattle_guard_template.py`

Source: page 26 of the supplied WAG-9HC checksheet - two sub-tables: "Side Buffer" (6 activities
repeated once per side buffer, 1 through 4) and "Cattle Guard / Rail Guard" (6 activities repeated
once per cab, Cab-1/Cab-2).
"""
from _m4hr_template_helpers import add_final_remarks, add_unit_group_table, run_seed

SIDE_BUFFERS = list(range(1, 5))


def build(add):
    buffer_activities = [
        {"key": "make_serial", "label": "Buffer Make & Serial Number", "field_type": "text", "required": True,
         "standard_value": "Noted"},
        {"key": "cleanness", "label": "Cleanness of Side Buffer", "field_type": "select",
         "options": "Cleaned, Not Cleaned", "required": True, "standard_value": "Cleaned",
         "negative_values": "Not Cleaned"},
        {"key": "crankiness_dpt_mpt", "label": "Check for Any Crankiness by Dye Penetrant Test/Magnetic Particle "
         "Test (DPT/MPT)", "field_type": "select", "options": "Checked, Not Checked", "required": True,
         "standard_value": "Checked", "negative_values": "Not Checked"},
        {"key": "foundation_bolt_tightness", "label": "Check Tightness of Buffer Foundation Bolt",
         "field_type": "select", "options": "Checked, Not Checked", "required": True, "standard_value": "Checked",
         "negative_values": "Not Checked"},
        {"key": "buffer_length", "label": "Check Side Buffer Length (RDSO/TC-142)", "field_type": "numeric_range",
         "required": True, "unit": "mm", "min_value": 615.0, "max_value": 635.0, "decimal_precision": 1,
         "standard_value": "Max.- 635.0mm & Min.- 615.0mm", "authority_reference": "RDSO/TC-142"},
        {"key": "abnormality_radial_play", "label": "Check for Any Abnormality/Radial Play - if Found Then "
         "Replaced", "field_type": "select", "options": "Checked, Replaced", "required": True,
         "standard_value": "Checked"},
    ]
    add_unit_group_table(add, "side_buffer", "Side Buffer", SIDE_BUFFERS, buffer_activities)

    for cab in ("Cab-1", "Cab-2"):
        cab_key = cab.lower().replace("-", "_")
        cab_group = add(f"cattle_guard_{cab_key}", field_label=cab, field_type="group", required=False)
        add(f"cattle_guard_{cab_key}_fixing_intact", parent=cab_group, field_label="Check Proper Fixing/Intact "
            "of Cattle Guard", field_type="select", options="Checked, Not Checked", required=True,
            standard_value="Checked", negative_values="Not Checked")
        add(f"cattle_guard_{cab_key}_damage_deformation", parent=cab_group, field_label="Check for Any Visible "
            "Damage or Deformation of Cattle Guard", field_type="select", options="Checked, Not Checked",
            required=True, standard_value="Checked", negative_values="Not Checked")
        add(f"cattle_guard_{cab_key}_foundation_bolts_tightness", parent=cab_group, field_label="Check Tightness "
            "of All Foundation Bolts of Cattle Guard", field_type="select", options="Checked, Not Checked",
            required=True, standard_value="Checked", negative_values="Not Checked")
        add(f"cattle_guard_{cab_key}_nut_split_pins", parent=cab_group, field_label="Ensure of Proper Intact of "
            "Nut & Split Pins", field_type="select", options="Ensured, Not Ensured", required=True,
            standard_value="Ensured", negative_values="Not Ensured")
        add(f"cattle_guard_{cab_key}_cbc_housing_bolts", parent=cab_group, field_label="Check Tightness of "
            "Foundation Bolts of CBC Housing RR & Bottom Plate", field_type="select",
            options="Checked, Not Checked", required=True, standard_value="Checked", negative_values="Not Checked")
        add(f"cattle_guard_{cab_key}_loco_body_gap", parent=cab_group, field_label="Checked Gap Between Cattle "
            "Guard & Loco Body", field_type="select", options="Checked, Not Checked", required=True,
            standard_value="Checked", negative_values="Not Checked")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="SB_CG_RG", template_code="76", technology="3_PHASE",
        template_name="Checksheet for Side Buffer, Cattle Guard & Rail Guard",
        description="Side Buffer, Cattle Guard & Rail Guard checksheet - WAG9HC, 3-Phase - M4-HR section.",
        build_fn=build,
    )
