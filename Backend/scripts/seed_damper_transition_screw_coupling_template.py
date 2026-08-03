"""
Module 40: seeds the DTSC (Damper & Transition Screw Coupling, WAG9HC, 3-Phase, M4-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_damper_transition_screw_coupling_template.py`

Source: page 25 of the supplied WAG-9HC checksheet - two sub-tables: "Damper" (axle dampers sit at
wheel positions 1,2,5,6,7,8,11,12; horizontal/vertical/yaw dampers sit only at 3,4,9,10, matching
where the bogie's bolster/yaw mounts actually are) and "Transition Screw Coupling" (MPMI No. 25
Rev.-00, RDSO/Drawing No. SKDL-2494), recorded once per cab (Cab-1/Cab-2).
"""
from _m4hr_template_helpers import add_final_remarks, run_seed

AXLE_DAMPER_POSITIONS = [1, 2, 5, 6, 7, 8, 11, 12]
BOLSTER_DAMPER_POSITIONS = [3, 4, 9, 10]


def _damper_group(add, key, label, positions, standard):
    group = add(key, field_label=label, field_type="group", required=False, standard_value=standard)
    for pos in positions:
        add(f"{key}_w{pos}", parent=group, field_label=f"W.No.-{pos}", field_type="text", required=True,
            standard_value="Noted")
    return group


def build(add):
    _damper_group(add, "axle_damper", "Axle Damper", AXLE_DAMPER_POSITIONS,
                   "Top: 16x65-192Nm, Bottom: 16x50-192Nm")
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

    for cab in ("Cab-1", "Cab-2"):
        cab_key = cab.lower().replace("-", "_")
        cab_group = add(f"tsc_{cab_key}", field_label=cab, field_type="group", required=False,
                         authority_reference="MPMI No. 25 Rev.-00, RDSO/Drawing No. SKDL-2494")
        add(f"tsc_{cab_key}_serial_number", parent=cab_group, field_label="Transition Screw Coupling Serial Number",
            field_type="text", required=True, standard_value="Noted")
        add(f"tsc_{cab_key}_make", parent=cab_group, field_label="Transition Screw Coupling Make",
            field_type="text", required=True, standard_value="Noted")
        add(f"tsc_{cab_key}_crankiness_dpt_mpt", parent=cab_group, field_label="Check for Any Crankiness by "
            "DPT/MPT Test", field_type="select", options="Checked, Not Checked", required=True,
            standard_value="Checked", negative_values="Not Checked")
        add(f"tsc_{cab_key}_thread_handle_damage", parent=cab_group, field_label="Check for Any Damage of "
            "Thread & Operating Handle", field_type="select", options="Checked, Not Checked", required=True,
            standard_value="Checked", negative_values="Not Checked")
        shackle_group = add(f"tsc_{cab_key}_shackle_gauge", parent=cab_group, field_label="Checking of Long & "
            "Short Shackle by Go-No Go Gauge", field_type="group", required=False,
            standard_value="Long Shackle: New-43.0mm, Cond.-39.5mm; Short Shackle: New-28.0mm, Cond.-25.0mm")
        add(f"tsc_{cab_key}_long_shackle", parent=shackle_group, field_label="Long Shackle", field_type="numeric_range",
            required=True, unit="mm", min_value=39.5, max_value=43.0, decimal_precision=2)
        add(f"tsc_{cab_key}_short_shackle", parent=shackle_group, field_label="Short Shackle", field_type="numeric_range",
            required=True, unit="mm", min_value=25.0, max_value=28.0, decimal_precision=2)
        add(f"tsc_{cab_key}_thread_handle_damage_2", parent=cab_group, field_label="Check for Any Damage of "
            "Threads & Operating Handle of Screw Coupling", field_type="select", options="Checked, Not Checked",
            required=True, standard_value="Checked", negative_values="Not Checked")
        add(f"tsc_{cab_key}_full_operation_check", parent=cab_group, field_label="Check the Full Operation of "
            "Screw Coupling", field_type="select", options="Checked, Not Checked", required=True,
            standard_value="Checked", negative_values="Not Checked")
        add(f"tsc_{cab_key}_lock_washer_condition", parent=cab_group, field_label="Check Condition of Lock Washer",
            field_type="select", options="Checked, Not Checked", required=True, standard_value="Checked",
            negative_values="Not Checked")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="DTSC", template_code="75", technology="3_PHASE",
        template_name="Checksheet for Damper & Transition Screw Coupling",
        description="Damper & Transition Screw Coupling checksheet - WAG9HC, 3-Phase - M4-HR section.",
        build_fn=build,
    )
