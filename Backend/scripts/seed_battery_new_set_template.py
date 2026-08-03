"""
Module 38: seeds the Battery- NewSet (Battery Lead-Acid New Set, Conventional, M9-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_battery_new_set_template.py`

Source: "BATTERY SET" new-set commissioning form. "Battery set fitted in Loco No." / "Date of
fitment" / "Date" from the footer are not implemented (Locomotive Number and submission timestamp
are already captured as backend metadata).

The "READING ON TEST BENCH" table (up to 26 open-ended rows: Date, Charging/Discharging, Time,
Sp.Gr., Amp, Volt) has no fixed row count or labels of its own on the source sheet - it is a
free-form bench-test log, not a fixed checklist, so it is implemented as a single optional
textarea rather than up to 156 individual fields (matching Module 36's "Super Check Observation"
precedent for the same kind of blank ruled log table). The four battery-by-battery specific
gravity/voltage tables (10 batteries each) ARE fixed, structured measurements at four distinct
commissioning stages, so those are implemented in full - preserving grouped measurements per
Module 38's explicit instruction.
"""
from _aux_template_helpers import run_seed, add_final_remarks


def add_battery_reading_table(add, parent_key, label, include_cells=True, hour_labels=None):
    group = add(parent_key, field_label=label, field_type="group", required=False)
    for i in range(1, 11):
        battery_group = add(f"{parent_key}_battery_{i}", parent=group, field_label=f"Battery {i}",
                            field_type="group", required=False)
        if include_cells:
            for cell in range(1, 6):
                add(f"{parent_key}_battery_{i}_cell{cell}", parent=battery_group,
                    field_label=f"Cell-{cell}", field_type="number", required=False, unit="Sp.Gr.")
            add(f"{parent_key}_battery_{i}_battery_volt", parent=battery_group, field_label="Battery Volt",
                field_type="number", required=False, unit="V")
            add(f"{parent_key}_battery_{i}_total_battery_volt", parent=battery_group,
                field_label="Total Battery Volt", field_type="number", required=False, unit="V")
        else:
            for key, hour_label in hour_labels:
                add(f"{parent_key}_battery_{i}_{key}", parent=battery_group, field_label=hour_label,
                    field_type="number", required=False, unit="V")
            add(f"{parent_key}_battery_{i}_specific_gravity", parent=battery_group,
                field_label="Specific Gravity After 5th Hour", field_type="number", required=False)
    return group


def build(add):
    add("battery_set_make", field_label="Make", field_type="text", required=True)
    add("battery_set_starting_date", field_label="Date of Starting", field_type="text", required=False)
    add("battery_set_electrolyte_specific_gravity", field_label="Electrolyte Specific Gravity",
        field_type="text", required=False)
    add("battery_set_starting_time", field_label="Time of Starting", field_type="text", required=False)
    add("battery_set_number", field_label="Battery Number", field_type="text", required=False)

    serial_group = add("battery_serial_numbers", field_label="Battery Serial Numbers",
        field_type="group", required=False)
    for i in range(1, 11):
        add(f"battery_serial_{i}", parent=serial_group, field_label=f"Battery {i:02d} Serial No.",
            field_type="text", required=True)

    add("battery_test_bench_reading_log", field_label="Reading on Test Bench (Date, "
        "Charging/Discharging, Time, Sp. Gr., Amp, Volt)", field_type="textarea", required=False)

    add_battery_reading_table(add, "before_initial_charging", "Readings Taken Before Initial Charging")
    add("initial_charging_start", field_label="Date & Time of Starting Initial Charging (at 5.0A "
        "for 75 Hours)", field_type="text", required=False)
    add("initial_charging_end", field_label="Date & Time of Readings Taken at the End, on "
        "Completion of Initial Charging", field_type="text", required=False)
    add_battery_reading_table(add, "after_initial_charging", "Readings Taken After Initial Charging")

    add("discharge_reading_start", field_label="Discharge Reading - Time to Start", field_type="text",
        required=False)
    add_battery_reading_table(add, "after_discharging", "Readings Taken After Discharging at 15 "
        "Amp for 5 Hours", include_cells=False, hour_labels=[
            ("hour1", "After 1st Hour"), ("hour2", "After 2nd Hour"), ("hour3", "After 3rd Hour"),
            ("hour4", "After 4th Hour"), ("hour5", "After 5th Hour"),
        ])

    add("final_charge_start", field_label="Date & Time of Starting Final Charge (at 5A for 15 Hours)",
        field_type="text", required=False)
    add("final_charge_end", field_label="Readings Taken After Charging - Date & Time of Completion",
        field_type="text", required=False)
    add_battery_reading_table(add, "after_final_charging", "Readings Taken After Final Charging")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="Battery- NewSet", template_code="53", technology="CONVENTIONAL",
        template_name="Checksheet for Battery Lead-Acid New Set",
        description="Battery Set (Lead-Acid, New Set) commissioning checksheet - Conventional - M9-HR section.",
        build_fn=build,
    )
