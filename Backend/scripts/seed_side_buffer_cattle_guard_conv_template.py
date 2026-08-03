"""
Module 40: seeds the Buff-CG_Conv (Side Buffer, Cattle Guard & Rail Guard, WAP-4, Conventional,
M4-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_side_buffer_cattle_guard_conv_template.py`

Source: page 19 of the supplied WAP-4 checksheet - "Check Sheet for Side Buffer, Cattle Guard &
Rail Guard", side buffer checks recorded once per buffer (1-4), cattle guard/rail guard checks
recorded once per cab (Cab-1/Cab-2).

Two genuine differences from the WAG9HC/WAP-7 SB_CG_RG template (seed_side_buffer_cattle_guard_
template.py / _p7_template.py): (1) this sheet's side buffer table omits the "Buffer Make & Serial
Number" row entirely (5 checks instead of 6); (2) this sheet's cattle guard table adds a "Check &
adjust the height of rail guard from rail level" measurement (115mm +3.0/-0.0) that the 3-Phase
sheets do not have (7 checks instead of 6).
"""
from _m4hr_template_helpers import add_final_remarks, add_unit_group_table, run_seed

SIDE_BUFFERS = list(range(1, 5))


def build(add):
    buffer_activities = [
        {"key": "cleanness", "label": "Cleanness of Buffer", "field_type": "select",
         "options": "Cleaned, Not Cleaned", "required": True, "standard_value": "Cleaned",
         "negative_values": "Not Cleaned"},
        {"key": "crankiness_dpt_mpt", "label": "Check for Any Crackness by DPT/MPT Test", "field_type": "select",
         "options": "Checked, Not Checked", "required": True, "standard_value": "Checked",
         "negative_values": "Not Checked"},
        {"key": "foundation_bolt_tightness", "label": "Check Tightness of Buffer Foundation Bolt",
         "field_type": "select", "options": "Checked, Not Checked", "required": True, "standard_value": "Checked",
         "negative_values": "Not Checked"},
        {"key": "buffer_length", "label": "Check Buffer Length", "field_type": "numeric_range", "required": True,
         "unit": "mm", "min_value": 615.0, "max_value": 635.0, "decimal_precision": 0,
         "standard_value": "Maximum-635mm, Minimum-615mm"},
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
        add(f"cattle_guard_{cab_key}_rail_guard_height", parent=cab_group, field_label="Check & Adjust the "
            "Height of Rail Guard From Rail Level", field_type="numeric_range", required=True, unit="mm",
            min_value=115.0, max_value=118.0, decimal_precision=1,
            standard_value="115mm +3.0, -0.0", authority_reference="EL/TRO/TRS-59 (99) dated 26.11.99")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="Buff-CG_Conv", template_code="115", technology="CONVENTIONAL",
        template_name="Checksheet for Side Buffer, Cattle Guard & Rail Guard (WAP-4)",
        description="Side Buffer, Cattle Guard & Rail Guard checksheet - WAP-4, Conventional - M4-HR section.",
        build_fn=build,
    )
