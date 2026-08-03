"""
Module 37: seeds the FB Cubicle (3-Phase, M9-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_fb_cubicle_template.py`

Source: "Check Sheet for FB Cubicle" (RDSO Letter No. 2006/Elect(TRS)441/8 Pt, dt. 14.08.2023).
"""
from _aux_template_helpers import run_seed, add_final_remarks


def build(add):
    add("fb_cubicle_make", field_label="FB Cubicle Make", field_type="text", required=True)
    add("fb_cubicle_serial_no", field_label="FB Cubicle Sr. No.", field_type="text", required=True)
    add("fb_cubicle_mfg", field_label="FB Cubicle Mfg", field_type="text", required=False)
    add("fb_capacitor_make", field_label="Capacitor Make", field_type="text", required=False)

    capacitor_bank_group = add("fb_capacitor_bank_values", field_label="Capacitor Bank Values",
        field_type="group", required=False, standard_value="380-420 uF total bank",
        authority_reference="RDSO Letter No. 2006/Elect(TRS)441/8 Pt")
    for i in range(1, 7):
        add(f"fb_capacitor_{i}", parent=capacitor_bank_group, field_label=f"Capacitor {i}",
            field_type="number", required=True, unit="uF")
    add("fb_capacitor_bank_total", field_label="Total Capacitor Bank Value", field_type="numeric_range",
        required=True, unit="uF", min_value=380.0, max_value=420.0, decimal_precision=1,
        standard_value="380-420 uF")

    add("fb_dust_cleaning", field_label="Use Soft Brush or Vacuum Cleaner to Remove All Dust "
        "Particles; Clean the Surface", field_type="select", options="Cleaned, Not Cleaned",
        required=True, negative_values="Not Cleaned")
    add("fb_physical_damage_leakage_check", field_label="Inspect Capacitor for Physical Damage, "
        "Leakage and Insulation Defects", field_type="select", options="OK, Issue Found", required=True,
        negative_values="Issue Found")
    add("fb_loose_fixing_connection_check", field_label="Check Loose Fixing and Connection, "
        "Tighten if Required; Inspect for Damage, Replace if Required", field_type="select",
        options="Tightened, Not Tightened", required=True, negative_values="Not Tightened",
        standard_value="Torque range: 10Nm")
    add("fb_capacitance_permissible_limit_each", field_label="Inspect Capacitor for Signs of "
        "Damage; Check That the Capacitance Is Within Permissible Limit", field_type="select",
        options="Within Limit, Out of Limit", required=True, negative_values="Out of Limit",
        standard_value="Each capacitor permissible limit: 66.6 uF +/- 5%")
    add("fb_capacitor_terminal_inspection", field_label="Inspect the Terminal of Capacitor and "
        "Fix Them if They Are Loose or Hanging", field_type="select",
        options="Checked & Tightened, Issue Found", required=True, negative_values="Issue Found")
    add("fb_capacitor_bank_cleaning_mounting", field_label="Clean the Capacitor Bank and Tighten "
        "the Capacitor Mounting Nut Properly", field_type="select", options="Done, Not Done",
        required=True, negative_values="Not Done")
    add("fb_capacitance_permissible_limit_bank", field_label="Check the Capacitor Bank That the "
        "Capacitance Is Within Permissible Limit", field_type="select",
        options="Within Limit, Out of Limit", required=True, negative_values="Out of Limit",
        standard_value="Capacitor bank permissible limit: 380-420 uF")

    resistance_group = add("fb_resistance_value", field_label="Resistance Value (02 Nos., Each "
        "Standard Value 2.2 kOhm 250W)", field_type="group", required=False)
    add("fb_resistance_1", parent=resistance_group, field_label="Resistance 1", field_type="number",
        required=True, unit="kOhm")
    add("fb_resistance_2", parent=resistance_group, field_label="Resistance 2", field_type="number",
        required=True, unit="kOhm")

    discharging_resistance_group = add("fb_discharging_resistance", field_label="Discharging "
        "Resistance (02 Nos., Each Standard Value 14 Ohm)", field_type="group", required=False)
    add("fb_discharging_resistance_1", parent=discharging_resistance_group, field_label="Resistance 1",
        field_type="number", required=True, unit="Ohm")
    add("fb_discharging_resistance_2", parent=discharging_resistance_group, field_label="Resistance 2",
        field_type="number", required=True, unit="Ohm")

    crc_panel_group = add("fb_crc_panel", field_label="CRC Panel", field_type="group", required=False)
    add("fb_crc_resistance", parent=crc_panel_group, field_label="Resistance (04 Nos.)",
        field_type="number", required=True, unit="Ohm", standard_value="22 Ohm, 80W each")
    add("fb_crc_capacitor", parent=crc_panel_group, field_label="Capacitor (03 Nos.)",
        field_type="number", required=True, unit="uF", standard_value="0.22 uF, 2000V each")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="FB Cubicle", template_code="48", technology="3_PHASE",
        template_name="Checksheet for FB Cubicle",
        description="FB Cubicle (3-Phase) checksheet - M9-HR section.",
        build_fn=build,
    )
