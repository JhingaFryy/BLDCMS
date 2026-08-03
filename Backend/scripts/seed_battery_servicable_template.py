"""
Module 38: seeds the Battery Servicable (Loco Battery 110V/75AH, Conventional, M9-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_battery_servicable_template.py`

Source: "Check Sheet for Loco Battery (110 Volt / 75 Ampere Hours)". "Schedule Type" and "Loco in
which fitted" from the header are not implemented (Work Type and Locomotive Number are already
captured as backend metadata); "Loco from which removed" IS implemented - it names a DIFFERENT,
previous locomotive, genuinely new information.
"""
from _aux_template_helpers import run_seed, add_final_remarks


def add_battery_group(add, parent_key, label, sub_labels, unit, min_value=None, max_value=None,
                      required=True, decimal_precision=2):
    group = add(parent_key, field_label=label, field_type="group", required=False)
    for i in range(1, 11):
        battery_group = add(f"{parent_key}_battery_{i}", parent=group, field_label=f"Battery {i}",
                            field_type="group", required=False)
        for sub_key, sub_label in sub_labels:
            add(f"{parent_key}_battery_{i}_{sub_key}", parent=battery_group, field_label=sub_label,
                field_type="numeric_range", required=required, unit=unit, min_value=min_value,
                max_value=max_value, decimal_precision=decimal_precision)
    return group


def build(add):
    add("battery_serial_no", field_label="Serial Number", field_type="text", required=True)
    add("battery_make", field_label="Make", field_type="text", required=False)
    add("battery_manufacture_date", field_label="Date of Manufacture", field_type="text", required=False)
    add("battery_commissioning_date", field_label="Date of Commissioning", field_type="text", required=False)
    add("battery_removed_from_loco", field_label="Loco From Which Removed, and Date of Removal",
        field_type="text", required=False)

    add("battery_cleaned_water_soda", field_label="Clean the Battery With Water + Soda (5% by Weight)",
        field_type="select", options="Cleaned, Not Cleaned", required=True, standard_value="Should be clean",
        negative_values="Not Cleaned")
    add("battery_corrosion_petroleum_jelly", field_label="Clean Off Corrosion and Apply Petroleum "
        "Jelly", field_type="select", options="Done, Not Done", required=True, standard_value="Should be clean",
        negative_values="Not Done")
    add("battery_cracks_leakage_check", field_label="Check the Battery for Cracks / Leakage",
        field_type="select", options="No Leakage, Leakage", required=True, standard_value="There should be no leakage",
        negative_values="Leakage")
    add("battery_electrolyte_max_mark", field_label="Maintain the Electrolyte Up to the Maximum Mark",
        field_type="numeric_range", required=True, unit="mm", min_value=35.0, max_value=50.0,
        decimal_precision=0, standard_value="35-50mm above the separator, as per respective OEM")

    add("battery_charging_specific_gravity", field_label="Charge the Battery at 5A for 10 to 12 "
        "Hours; Continue Equalising Charge Until Each Battery Reaches 11.75-12.00V; Check the "
        "Specific Gravity of Each Cell (Temperature Must Not Exceed 50C During Charging)",
        field_type="numeric_range", required=True, min_value=1240.0, max_value=1260.0, decimal_precision=0,
        standard_value="During charging, 11.75 to 12.00 volts per battery; specific gravity 1.240 to 1.260",
        authority_reference="SMI No. 112 & respective OEMs")
    add_battery_group(add, "charging_test", "Specific Gravity of Cells After 10 to 12 Hours & "
        "Battery Voltage", [("cell1", "Cell 1"), ("cell2", "Cell 2"), ("cell3", "Cell 3"),
                             ("cell4", "Cell 4"), ("cell5", "Cell 5"), ("voltage", "Battery Voltage")],
        unit=None, required=True)

    add("battery_discharge_test_note", field_label="Discharge the Battery at the Rated 15A for 5 "
        "Hours and Record the Values", field_type="text", required=False,
        standard_value="As per respective OEMs: 8.75 to 9.0 volts after 5 hours, and specific "
        "gravity minimum 1.180")
    add_battery_group(add, "discharge_test", "Battery Voltage of Cells After 5 Hours",
        [("cell1", "Cell 1"), ("cell2", "Cell 2"), ("cell3", "Cell 3"), ("cell4", "Cell 4"),
         ("cell5", "Cell 5")], unit="V", required=False)

    add("battery_final_recharge_note", field_label="Finally Recharge the Battery at 7.5A for 10 "
        "to 15 Hours and Note the Values", field_type="text", required=False,
        standard_value="(As per respective OEMs) 11.75 volts per battery / sp. gravity 1240 to 1260")
    add_battery_group(add, "final_recharge", "Battery Voltage of Cells After Final Charging & "
        "Specific Gravity", [("cell1", "Cell 1"), ("cell2", "Cell 2"), ("cell3", "Cell 3"),
                              ("cell4", "Cell 4"), ("cell5", "Cell 5"), ("specific_gravity", "Specific Gravity")],
        unit=None, required=False)

    add("battery_vent_plugs_cleaned", field_label="Cleaning of Vent Plugs", field_type="select",
        options="Done, Not Done", required=True, negative_values="Not Done")
    add("battery_electrolyte_max_mark_final", field_label="Maintain the Electrolyte Level Up to "
        "the Maximum Mark", field_type="numeric_range", required=True, unit="mm", min_value=35.0,
        max_value=50.0, decimal_precision=0, standard_value="35 to 50mm above the separator (as per respective OEMs)")
    add("battery_other_work_carried_out", field_label="Was Any Part Replaced / Was Any Other Work "
        "Carried Out Apart From the Above Maintenance?", field_type="textarea", required=False)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="Battery Servicable", template_code="54", technology="CONVENTIONAL",
        template_name="Checksheet for Battery Servicable",
        description="Loco Battery (110V/75AH) Serviceable checksheet - Conventional - M9-HR section.",
        build_fn=build,
    )
