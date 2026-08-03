"""
Module 40: seeds the DTSC_P7 (Damper & Transition Screw Coupling, WAP-7, 3-Phase, M4-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_damper_transition_screw_coupling_p7_template.py`

Source: page 20 of the supplied WAP-7 checksheet - "Damper" (Koni make imported dampers to be
provided - RDSO/TC-142 and Escort make) and "Transition Screw Coupling" (MPMI No. 25 Rev.-00,
RDSO/Drawing No. SKDL-2494). The damper table is identical in shape and torque specs to WAG9HC's.
The transition screw coupling table differs: this sheet records a third unit, "Spare", in
addition to Cab-1/Cab-2 (WAG9HC's sheet only has Cab-1/Cab-2) - implemented as a third repeated
group rather than omitted.
"""
from _m4hr_template_helpers import add_final_remarks, run_seed

AXLE_DAMPER_POSITIONS = [1, 2, 5, 6, 7, 8, 11, 12]
BOLSTER_DAMPER_POSITIONS = [3, 4, 9, 10]
COUPLING_UNITS = ["Cab-1", "Cab-2", "Spare"]


def _damper_group(add, key, label, positions, standard):
    group = add(key, field_label=label, field_type="group", required=False, standard_value=standard)
    for pos in positions:
        add(f"{key}_w{pos}", parent=group, field_label=f"W.No.-{pos}", field_type="text", required=True,
            standard_value="Noted")
    return group


def build(add):
    _damper_group(add, "axle_damper", "Axle Damper", AXLE_DAMPER_POSITIONS,
                   "Top: 16x65-192Nm, Bottom: 16x50-192Nm (Koni make imported dampers - RDSO/TC-142, or Escort make)")
    _damper_group(add, "horizontal_damper", "Horizontal Damper", BOLSTER_DAMPER_POSITIONS,
                   "Top: 16x80-192Nm, Bottom: 16x65-192Nm")
    _damper_group(add, "vertical_damper", "Vertical Damper", BOLSTER_DAMPER_POSITIONS,
                   "Top: 16x65-192Nm, Bottom: 16x70-192Nm")
    _damper_group(add, "yaw_damper", "Yaw Damper", BOLSTER_DAMPER_POSITIONS,
                   "Top: 20x80-385Nm, Bottom: 20x60-385Nm")
    add("fs_nut_m16_replace", field_label="Replace FS Nut M16 in Axle, Horizontal, Vertical Damper",
        field_type="select", options="Replaced, Not Replaced", required=True, standard_value="Replaced",
        negative_values="Not Replaced")
    add("fs_nut_m20_replace", field_label="Replace FS Nut M20 in Yaw Damper", field_type="select",
        options="Replaced, Not Replaced", required=True, standard_value="Replaced", negative_values="Not Replaced")

    for unit in COUPLING_UNITS:
        unit_key = unit.lower().replace("-", "_")
        unit_group = add(f"tsc_{unit_key}", field_label=unit, field_type="group", required=False,
                         authority_reference="MPMI No. 25 Rev.-00, RDSO/Drawing No. SKDL-2494")
        add(f"tsc_{unit_key}_serial_number", parent=unit_group, field_label="Transition Screw Coupling Serial Number",
            field_type="text", required=True, standard_value="Noted")
        add(f"tsc_{unit_key}_make", parent=unit_group, field_label="Transition Screw Coupling Make",
            field_type="text", required=True, standard_value="Noted")
        add(f"tsc_{unit_key}_crankiness_dpt_mpt", parent=unit_group, field_label="Check for Any Crankiness by "
            "DPT/MPT Test", field_type="select", options="Checked, Not Checked", required=True,
            standard_value="Checked", negative_values="Not Checked")
        add(f"tsc_{unit_key}_thread_handle_damage", parent=unit_group, field_label="Check for Any Damage of "
            "Thread & Operating Handle", field_type="select", options="Checked, Not Checked", required=True,
            standard_value="Checked", negative_values="Not Checked")
        shackle_group = add(f"tsc_{unit_key}_shackle_gauge", parent=unit_group, field_label="Checking of Long & "
            "Short Shackle by Go-No Go Gauge", field_type="group", required=False,
            standard_value="Long Shackle: New-43.0mm, Cond.-39.5mm; Short Shackle: New-28.0mm, Cond.-25.0mm")
        add(f"tsc_{unit_key}_long_shackle", parent=shackle_group, field_label="Long Shackle", field_type="numeric_range",
            required=True, unit="mm", min_value=39.5, max_value=43.0, decimal_precision=2)
        add(f"tsc_{unit_key}_short_shackle", parent=shackle_group, field_label="Short Shackle", field_type="numeric_range",
            required=True, unit="mm", min_value=25.0, max_value=28.0, decimal_precision=2)
        add(f"tsc_{unit_key}_thread_handle_damage_2", parent=unit_group, field_label="Check for Any Damage of "
            "Threads & Operating Handle of Screw Coupling", field_type="select", options="Checked, Not Checked",
            required=True, standard_value="Checked", negative_values="Not Checked")
        add(f"tsc_{unit_key}_full_operation_check", parent=unit_group, field_label="Check the Full Operation of "
            "Screw Coupling", field_type="select", options="Checked, Not Checked", required=True,
            standard_value="Checked", negative_values="Not Checked")
        add(f"tsc_{unit_key}_lock_washer_condition", parent=unit_group, field_label="Check Condition of Lock Washer",
            field_type="select", options="Checked, Not Checked", required=True, standard_value="Checked",
            negative_values="Not Checked")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="DTSC_P7", template_code="97", technology="3_PHASE",
        template_name="Checksheet for Damper & Transition Screw Coupling (WAP-7)",
        description="Damper & Transition Screw Coupling checksheet - WAP-7, 3-Phase - M4-HR section.",
        build_fn=build,
    )
