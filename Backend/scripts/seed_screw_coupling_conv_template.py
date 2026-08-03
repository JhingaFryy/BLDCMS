"""
Module 40: seeds the SC_Conv (Screw Coupling, WAP-4, Conventional, M4-HR section) checksheet
template.

Run once: `venv/bin/python scripts/seed_screw_coupling_conv_template.py`

Source: page 18 of the supplied WAP-4 checksheet - "Check Sheet for Screw Coupling for AOH/IOH
Loco", recorded once per coupling unit (CBC-1, CBC-2, Spare - three units, same "third Spare
unit" convention as the WAP-7 DTSC_P7 template). Same shackle gauge standards as the WAG9HC/WAP-7
Damper & Transition Screw Coupling templates (Long Shackle New-43.0mm/Cond.-39.5mm, Short Shackle
New-28.0mm/Cond.-25.0mm), but this WAP-4 sheet has no damper section at all - dampers are not
part of this equipment's reference checksheet, so none is added here.
"""
from _m4hr_template_helpers import add_final_remarks, run_seed

UNITS = ("CBC-1", "CBC-2", "Spare")


def build(add):
    for unit in UNITS:
        unit_key = unit.lower().replace("-", "_")
        unit_group = add(f"sc_{unit_key}", field_label=unit, field_type="group", required=False)

        add(f"sc_{unit_key}_make_sr_no", parent=unit_group, field_label="Make & Sr. No.", field_type="text",
            required=True, standard_value="Noted")
        add(f"sc_{unit_key}_crankiness_dpt_mpt", parent=unit_group, field_label="Check for Any Crackness by "
            "DPT/MPT Test", field_type="select", options="Checked, Not Checked", required=True,
            standard_value="Checked", negative_values="Not Checked")
        add(f"sc_{unit_key}_thread_handle_damage", parent=unit_group, field_label="Check for Any Damage of "
            "Thread & Operating Handle", field_type="select", options="Checked, Not Checked", required=True,
            standard_value="Checked", negative_values="Not Checked")
        shackle_group = add(f"sc_{unit_key}_shackle_gauge", parent=unit_group, field_label="Checking of Long & "
            "Short Shackle by Go-No Go Gauge", field_type="group", required=False,
            standard_value="Long Shackle: New-43.0mm, Cond.-39.5mm; Short Shackle: New-28.0mm, Cond.-25.0mm")
        add(f"sc_{unit_key}_long_shackle", parent=shackle_group, field_label="Long Shackle", field_type="numeric_range",
            required=True, unit="mm", min_value=39.5, max_value=43.0, decimal_precision=2)
        add(f"sc_{unit_key}_short_shackle", parent=shackle_group, field_label="Short Shackle", field_type="numeric_range",
            required=True, unit="mm", min_value=25.0, max_value=28.0, decimal_precision=2)
        add(f"sc_{unit_key}_thread_handle_damage_2", parent=unit_group, field_label="Check for Any Damage of "
            "Threads & Operating Handle of Screw Coupling", field_type="select", options="Checked, Not Checked",
            required=True, standard_value="Checked", negative_values="Not Checked")
        add(f"sc_{unit_key}_full_operation_check", parent=unit_group, field_label="Check the Full Operation of "
            "Screw Coupling", field_type="select", options="Checked, Not Checked", required=True,
            standard_value="Checked", negative_values="Not Checked")
        add(f"sc_{unit_key}_lock_washer_condition", parent=unit_group, field_label="Check Condition of Lock "
            "Washer", field_type="select", options="Checked, Not Checked", required=True,
            standard_value="Checked", negative_values="Not Checked")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="SC_Conv", template_code="114", technology="CONVENTIONAL",
        template_name="Checksheet for Screw Coupling (WAP-4)",
        description="Screw Coupling checksheet for AOH/IOH loco - WAP-4, Conventional - M4-HR section.",
        build_fn=build,
    )
