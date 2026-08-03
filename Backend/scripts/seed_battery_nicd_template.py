"""
Module 38: seeds the Battery 3-Ph (Battery NiCd, 3-Phase, M9-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_battery_nicd_template.py`

Source: "3-Phase Loco Ni-Cd Battery Maintenance Proforma". "Removed from Loco No." / "Provided in
Loco No." / dates / Schedule from the header are not implemented (Locomotive Number, Work Type,
and submission timestamp are already captured as backend metadata); "Removed from Loco No." alone
would normally be kept (as in the other Module 37/38 templates) but here it is IDENTICAL to
"Provided in Loco No." on the sample (both 33759 - this is the same locomotive's battery being
serviced and refitted, not swapped to a different one), so it carries no information beyond what
metadata already provides and is omitted too.

The 26-row BA (battery) table is the primary content of this checksheet (fully populated with
real varying values in the reference sample) and is implemented in full, one field per cell -
"preserve grouped measurements" per Module 38's explicit instruction.
"""
from _aux_template_helpers import run_seed, add_final_remarks


def build(add):
    add("nicd_battery_make", field_label="Battery Make", field_type="text", required=True)
    add("nicd_battery_mfg", field_label="MFG", field_type="text", required=False)
    add("nicd_lug_date", field_label="Lug Date", field_type="text", required=False)
    add("nicd_ba_set_no", field_label="BA Set No.", field_type="text", required=False)
    add("nicd_total_set_voltage", field_label="Total Set Voltage", field_type="number", required=True, unit="V")

    ba_table_group = add("nicd_ba_readings", field_label="BA Voltage Measurement & Specific Gravity",
        field_type="group", required=False)
    voltage_columns = [
        ("before_charging", "Before Charging", 3.9, 4.2),
        ("after_charging", "After Charging", 5.4, 5.8),
        ("after_discharging", "After Discharging", 2.5, 2.8),
        ("after_final_charging", "After Final Charging", 5.4, 5.8),
        ("before_providing_loco", "Before Providing in Loco", 3.9, 4.2),
    ]
    for ba_no in range(1, 27):
        ba_group = add(f"nicd_ba_{ba_no}", parent=ba_table_group, field_label=f"BA No. {ba_no}",
                       field_type="group", required=False)
        for key, label, lo, hi in voltage_columns:
            add(f"nicd_ba_{ba_no}_{key}", parent=ba_group, field_label=label, field_type="numeric_range",
                required=True, unit="V", min_value=lo, max_value=hi, decimal_precision=2)
        for cell in range(1, 4):
            add(f"nicd_ba_{ba_no}_cell{cell}", parent=ba_group, field_label=f"Specific Gravity Cell {cell}",
                field_type="numeric_range", required=True, min_value=1180.0, max_value=1220.0,
                decimal_precision=0, standard_value="1180 to 1220")

    total_voltage_group = add("nicd_total_voltage_row", field_label="Total Voltage",
        field_type="group", required=False)
    for key, label, _, _ in voltage_columns:
        add(f"nicd_total_voltage_{key}", parent=total_voltage_group, field_label=label,
            field_type="number", required=True, unit="V")

    add("nicd_dust_dirt_cleaning", field_label="Clean All Dust and Dirt Deposits / Electrolyte "
        "Leakage From Around the Batteries and Their Connectors", field_type="select",
        options="Done, Not Done", required=True, negative_values="Not Done")
    add("nicd_overhaul_battery", field_label="Overhaul the Battery as Per OEM Instructions",
        field_type="select", options="Done, Not Done", required=True, negative_values="Not Done")
    add("nicd_electrolyte_level_topup", field_label="Check the Electrolyte Level and Top Up if "
        "Required", field_type="select", options="Top-up Done, Not Required, Issue Found",
        required=True, negative_values="Issue Found")
    add("nicd_capacity_check", field_label="Check the Battery Capacity (>80% Change Electrolyte, "
        "<80% Change Battery Set)", field_type="select", options="Done, Not Done", required=True,
        negative_values="Not Done")
    add("nicd_measure_record_gravity_voltage", field_label="Measure and Record: Specific Gravity "
        "of the Electrolyte, and Voltage of Each Cell", field_type="select", options="Done, Not Done",
        required=True, standard_value="Specific Gravity: 1180 to 1220; Cell Voltage: 1.3V to 1.4V",
        negative_values="Not Done")
    add("nicd_shorting_cover_vent_plugs", field_label="Check the Shorting Cover and Vent Plugs of "
        "All Batteries; Replace if Broken", field_type="select", options="Checked, Issue Found",
        required=True, negative_values="Issue Found")
    add("nicd_shunt_tension_check", field_label="Connect the Battery Properly and Ensure That the "
        "Shunt Is Not Under Tension", field_type="select", options="OK, Under Tension", required=True,
        negative_values="Under Tension")
    add("nicd_petroleum_jelly_terminals", field_label="After Checking the Connections, Apply "
        "Petroleum Jelly on the Terminals", field_type="select", options="Done, Not Done",
        required=True, negative_values="Not Done")

    add("nicd_box_visual_inspection", field_label="Visually Inspect the Battery Box for Any "
        "External Impact and Damage; Repair if Required", field_type="select",
        options="OK, Repaired", required=True, negative_values=None)
    add("nicd_box_overhaul", field_label="Overhaul the Battery Box", field_type="select",
        options="Done, Not Done", required=True, negative_values="Not Done")
    add("nicd_box_welded_support_rdpt", field_label="Check the Integrity of the Welded Hanging "
        "Support for Any Crack/Damage by Means of RDPT; Repair if Required", field_type="select",
        options="OK, Repaired", required=False, negative_values=None)
    add("nicd_box_sliding_mechanism_grease", field_label="Open the Battery Box Cover and Take Out "
        "the Battery Tray; Apply Grease on the Sliding Mechanism and Check Free Movement; Repair "
        "if Required", field_type="select", options="Done, Not Done", required=True, negative_values="Not Done")
    add("nicd_box_acid_cleaned", field_label="Clean Battery Acid From the Battery Box and Tray",
        field_type="select", options="Cleaned, Not Cleaned", required=True, negative_values="Not Cleaned")
    add("nicd_box_tray_locking", field_label="Ensure Proper Locking of the Battery Tray in the "
        "Battery Box", field_type="select", options="OK, Not OK", required=True, negative_values="Not OK")
    add("nicd_box_door_seal_lock", field_label="Check the Door Seal and the Condition of the Door "
        "Lock; Replace if Damaged; Test the Operation and Safety of the Locking Handle and Rectify "
        "Any Defects; Apply Lubricant on the Handle Pivots", field_type="select",
        options="OK, Issue Found", required=True, negative_values="Issue Found")
    add("nicd_box_safety_guard_fit", field_label="Fit the Safety Guard Correctly and Ensure It",
        field_type="select", options="Done, Not Done", required=True, negative_values="Not Done")
    add("nicd_box_residue_removed", field_label="Remove All Oil, Grease and Other Residue From "
        "the Side Way and Screw Mechanism", field_type="select", options="Done, Not Done",
        required=True, negative_values="Not Done")
    add("nicd_box_ms_safety_rod", field_label="Fit an MS Rod for Safety (MS Safety Rod)",
        field_type="select", options="Provided, Not Provided", required=True, negative_values="Not Provided")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="Battery 3-Ph", template_code="55", technology="3_PHASE",
        template_name="Checksheet for Battery NiCd",
        description="3-Phase Loco Ni-Cd Battery Maintenance checksheet - M9-HR section.",
        build_fn=build,
    )
