"""
Module 37: seeds the B. Ch. Conventional (Battery Charger, Conventional, M9-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_battery_charger_conv_template.py`

Source: "Check Sheet for Battery Charger of Conventional Loco (Type - Simplified Charger)".
This is the CHARGER unit, distinct from the excluded Battery Lead-Acid/NiCd checksheets (Module
37 explicitly says battery checksheets are not part of this module - the charger is).
"""
from _aux_template_helpers import run_seed, add_final_remarks


def build(add):
    add("chba_serial_no", field_label="CHBA Sr. No.", field_type="text", required=True)

    ir_group = add("chba_insulation_resistance", field_label="Insulation Resistance With 500V "
        "Meggar of Transformer & Cable", field_type="group", required=False,
        standard_value="More than 10 M-Ohm", authority_reference="500V Meggar")
    ir_rows = [
        ("primary_earth", "Between Primary Winding & Earth"),
        ("secondary_earth", "Between Secondary Winding & Earth"),
        ("capacitor_earth", "Between Capacitor Winding & Earth"),
        ("primary_secondary", "Between Primary & Secondary Winding"),
        ("primary_capacitor", "Between Primary & Capacitor Winding"),
        ("secondary_condensor", "Between Secondary Winding & Condensor"),
        ("cable_earth", "All Cable Connection & Earth"),
    ]
    for key, label in ir_rows:
        add(f"chba_ir_{key}", parent=ir_group, field_label=label, field_type="numeric_range",
            required=True, unit="MOhm", min_value=10.0, decimal_precision=1,
            standard_value="More than 10 M-Ohm")

    add("chba_crimping_of_lugs", field_label="Crimping of Lugs", field_type="select",
        options="Properly Crimped, Not Crimped", required=True, standard_value="Properly Crimped",
        negative_values="Not Crimped", authority_reference="Crimping tools")

    capacitor_group = add("chba_capacitor_value", field_label="Value of Capacitor", field_type="group",
        required=False, standard_value="10uFD +/-10% or 15uFD +/-10%", authority_reference="Multi meter")
    for i in range(1, 7):
        add(f"chba_capacitor_{i}", parent=capacitor_group, field_label=f"Capacitor {i}",
            field_type="number", required=True, unit="uF")
    add("chba_capacitor_total", parent=capacitor_group, field_label="Total", field_type="number",
        required=True, unit="uF")

    snubber_group = add("chba_snubber_capacitor_value", field_label="Value of Snubber Capacitor",
        field_type="group", required=False, standard_value="0.1 mfd/1000V", authority_reference="Multi meter")
    for i in range(1, 7):
        add(f"chba_snubber_{i}", parent=snubber_group, field_label=f"Snubber {i}", field_type="number",
            required=True, unit="uF")

    diode_group = add("chba_testing_of_diode", field_label="Testing of Diode", field_type="group",
        required=False)
    add("chba_diode_tightness", parent=diode_group, field_label="Tightness of Diode", field_type="select",
        options="Tight, Not Tight", required=True, standard_value="Tight (4.5NM Torque Range)",
        negative_values="Not Tight")
    add("chba_diode_piv_leakage", parent=diode_group, field_label="PIV of Diode 500V DC",
        field_type="select", options="No Leakage, Leakage", required=True,
        standard_value="Leakage current less than 4mA", negative_values="Leakage")

    add("chba_cables_lugs_transformer_fuse_tightness", field_label="Check All the Tightness of "
        "Cables, Lugs, Transformer Panel, and Fuse", field_type="select",
        options="Checked, Not Checked", required=True, standard_value="Tightness Checked",
        negative_values="Not Checked", authority_reference="Spanner set 8-9, 10-11, 12-13")

    voltage_test_rows = [
        ("no_load", "At No Load", None),
        ("5amp_load", "At 5Amp Load With Battery", "112 +/-3 VDC"),
        ("10amp_load", "At 10Amp Load With Battery", "110 +/-3 VDC"),
        ("15amp_load", "At 15Amp Load With Battery", "105 +/-3 VDC"),
    ]
    voltage_test_group = add("chba_voltage_test", field_label="Voltage Test - Check DC Voltage of "
        "CHBA at Following Load and AC Voltage Input to Battery Charger Varying Between 360 to "
        "400V RMS", field_type="group", required=False, authority_reference="RDSO/SMI/108")
    for key, label, standard in voltage_test_rows:
        row_group = add(f"chba_voltage_{key}", parent=voltage_test_group, field_label=label,
            field_type="group", required=False, standard_value=standard)
        for sub_key, sub_label in [("ba", "BA"), ("load", "LOAD"), ("relay", "RELAY"),
                                    ("nr_winding", "NR Winding Voltage")]:
            add(f"chba_voltage_{key}_{sub_key}", parent=row_group, field_label=sub_label,
                field_type="number", required=True, unit="V")

    resistance_group = add("chba_resistance_checking", field_label="Checking of Resistance",
        field_type="group", required=False)
    add("chba_bleeder_resistance_25w", parent=resistance_group, field_label="Bleeder Resistance (25W)",
        field_type="number", required=True, unit="kOhm", standard_value="2 k-ohm / 25W")
    add("chba_bleeder_resistance_75w", parent=resistance_group, field_label="Bleeder Resistance (75W)",
        field_type="number", required=True, unit="Ohm", standard_value="600 ohm / 75W")
    add("chba_continuity_015ohm", parent=resistance_group, field_label="Continuity of 0.15 Ohm "
        "Resistance", field_type="number", required=True, unit="Ohm", standard_value="0.15 ohm")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="B. Ch. Conventional", template_code="38", technology="CONVENTIONAL",
        template_name="Checksheet for Battery Charger (Conventional)",
        description="Battery Charger, Simplified Charger type (Conventional) checksheet - M9-HR section.",
        build_fn=build,
    )
