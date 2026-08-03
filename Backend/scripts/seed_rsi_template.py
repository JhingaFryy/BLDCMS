"""
Module 37: seeds the RSI (Rectifier, Conventional, M9-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_rsi_template.py`

Source: "Check Sheet for RSI [Rectifier] (Rev. 12/11/2025)".

The AC/DC Damping Panel value-check tables (RSI-1/RSI-2, up to 18 near-identical capacitor
readings + 4 resistance readings each) are implemented as Total-value fields rather than every
individual reading - the per-unit values are factory QC data all clustered tightly around the same
nominal value (confirmed across both filled samples), and the Total is what a supervisor actually
reviews against the printed total-value line on the sheet.
"""
from _aux_template_helpers import run_seed, add_final_remarks


def build(add):
    add("rsi1_details", field_label="RSI-1 Model / Doc / Mfg", field_type="text", required=False)
    add("rsi2_details", field_label="RSI-2 Model / Doc / Mfg", field_type="text", required=False)

    fuse_group = add("rsi_power_diode_fuse_led_check", field_label="Power Diode & Power Fuse Check by LED",
        field_type="group", required=False)
    add("rsi1_power_diode_fuse", parent=fuse_group, field_label="RSI-1", field_type="select",
        options="Checked, Not Checked", required=True, negative_values="Not Checked")
    add("rsi2_power_diode_fuse", parent=fuse_group, field_label="RSI-2", field_type="select",
        options="Checked, Not Checked", required=True, negative_values="Not Checked")

    add("rsi_tt_fuse_led_check", field_label="T/T Fuse Checked by LED (RSI-1 Only)", field_type="select",
        options="Checked, Not Checked", required=True, negative_values="Not Checked")
    add("rsi_micro_switch_working", field_label="Micro Switch Working Checked (RSI-2)",
        field_type="select", options="Checked, Not Checked", required=True, negative_values="Not Checked")

    rc1_group = add("rsi1_rc_network", field_label="RSI-1 RC Network Resistance & Capacitor Value Checked",
        field_type="group", required=False)
    add("rsi1_rc_resistance", parent=rc1_group, field_label="Resistance", field_type="numeric_range",
        required=True, unit="Ohm", min_value=11.0, max_value=33.0, decimal_precision=1,
        standard_value="22 Ohm +/- 50W")
    add("rsi1_rc_capacitor", parent=rc1_group, field_label="Capacitor", field_type="number",
        required=True, unit="uF", standard_value="0.47uF/2000V")

    mcp_arno_group = add("rsi_capacitor_panel_mcp_arno", field_label="Capacitor Panel Across "
        "MCP & ARNO", field_type="group", required=False, standard_value="0.5uF/1000V +/-10%",
        authority_reference="Mod-189")
    for key, label in [("mcp1", "MCP1"), ("mcp2", "MCP2"), ("mcp3", "MCP3"), ("arno", "ARNO")]:
        add(f"rsi_capacitor_panel_{key}", parent=mcp_arno_group, field_label=label,
            field_type="number", required=False, unit="uF")

    c118_group = add("rsi_rc_network_c118", field_label="RC Network Checked Across C118",
        field_type="group", required=False, authority_reference="Mod-13")
    add("rsi_c118_resistance", parent=c118_group, field_label="Resistance", field_type="number",
        required=False, unit="Ohm", standard_value="22 Ohm +/- 10%")
    add("rsi_c118_capacitor", parent=c118_group, field_label="Capacitor", field_type="number",
        required=False, unit="uF", standard_value="0.47uF +/- 10%")

    for key, label in [("rsi1_ac_panel", "RSI-1 AC Panel"), ("rsi2_ac_panel", "RSI-2 AC Panel")]:
        panel_group = add(f"rsi_{key}", field_label=label, field_type="group", required=False,
            authority_reference="SMI-230")
        add(f"rsi_{key}_resistance", parent=panel_group, field_label="Resistance",
            field_type="numeric_range", required=True, unit="Ohm", min_value=1.35, max_value=1.65,
            decimal_precision=2, standard_value="1.5 Ohm +/- 10%")
        add(f"rsi_{key}_capacitor", parent=panel_group, field_label="Capacitor",
            field_type="numeric_range", required=True, unit="uF", min_value=45.0, max_value=55.0,
            decimal_precision=1, standard_value="50uF +/- 10%")

    add("rsi_et_panel_capacitor", field_label="E.T Panel Capacitor", field_type="number",
        required=True, unit="uF", standard_value="0.042uF", authority_reference="SMI-230")
    add("rsi_qlm_ct_value", field_label="QLM CT Value", field_type="number", required=True, unit="mH")
    add("rsi_qrsi1_ct", field_label="QRSI-1 CT", field_type="number", required=True, unit="H")
    add("rsi_qrsi2_ct", field_label="QRSI-2 CT", field_type="number", required=True, unit="H")

    for key, label in [("rc_panel_1", "RC Panel-1"), ("rc_panel_2", "RC Panel-2")]:
        panel_group = add(f"rsi_{key}", field_label=label, field_type="group", required=False)
        add(f"rsi_{key}_resistance", parent=panel_group, field_label="Resistance",
            field_type="numeric_range", required=True, unit="Ohm", min_value=4.23, max_value=5.17,
            decimal_precision=1, standard_value="4.7 Ohm +/- 10%")
        add(f"rsi_{key}_capacitor", parent=panel_group, field_label="Capacitor",
            field_type="numeric_range", required=True, unit="uF", min_value=22.59, max_value=27.61,
            decimal_precision=1, standard_value="25.1uF +/- 10%")

    rc3_group = add("rsi_rc_panel_3", field_label="RC Panel 3 (if ARNO)", field_type="group",
        required=False)
    add("rsi_rc_panel_3_resistance", parent=rc3_group, field_label="Resistance", field_type="number",
        required=False, unit="Ohm", standard_value="4.7 Ohm +/- 10%")
    add("rsi_rc_panel_3_capacitor", parent=rc3_group, field_label="Capacitor", field_type="number",
        required=False, unit="uF", standard_value="25.1uF +/- 10%")

    add("rsi_ltba_piv_testing", field_label="LTBA PIV Testing", field_type="select",
        options="OK, Not OK", required=True, negative_values="Not OK")
    a0a1_group = add("rsi_a0_a1_panel", field_label="A0-A1 Panel Capacitor", field_type="group",
        required=False)
    add("rsi_a0_a1_capacitor_1", parent=a0a1_group, field_label="Capacitor 1", field_type="text",
        required=False)
    add("rsi_a0_a1_capacitor_2", parent=a0a1_group, field_label="Capacitor 2", field_type="text",
        required=False)

    power_fuse_group = add("rsi_power_fuse", field_label="Power Fuse", field_type="group", required=False,
        authority_reference="Bussman")
    add("rsi_power_fuse_number", parent=power_fuse_group, field_label="Number", field_type="number",
        required=True)
    add("rsi_power_fuse_rating", parent=power_fuse_group, field_label="Rating", field_type="text",
        required=True)

    tt_fuse_group = add("rsi_tell_tale_fuse", field_label="Tell Tale Fuse / Micro Switch",
        field_type="group", required=False, authority_reference="Bussman")
    add("rsi_tt_fuse_number", parent=tt_fuse_group, field_label="Number", field_type="number",
        required=True)
    add("rsi_tt_fuse_rating", parent=tt_fuse_group, field_label="Rating", field_type="text",
        required=False)

    diode_group = add("rsi_diode", field_label="Diode", field_type="group", required=False,
        authority_reference="HiRect")
    add("rsi_diode_number", parent=diode_group, field_label="Number", field_type="number", required=True)
    add("rsi_diode_rating", parent=diode_group, field_label="Rating", field_type="text", required=True)

    for panel in ("rsi1", "rsi2"):
        damping_group = add(f"{panel}_ac_damping_panel", field_label=f"{panel.upper()} AC Damping Panel "
            "Value Check", field_type="group", required=False, authority_reference="SMI-230")
        add(f"{panel}_ac_damping_capacitor_total", parent=damping_group, field_label="Total Capacitor Value",
            field_type="number", required=True, unit="uF")
        add(f"{panel}_ac_damping_resistance_total", parent=damping_group, field_label="Total Resistance Value",
            field_type="number", required=True, unit="Ohm")

    for panel in ("rsi1", "rsi2"):
        dc_damping_group = add(f"{panel}_dc_damping_panel", field_label=f"{panel.upper()} DC Damping Panel "
            "Value Check", field_type="group", required=False, authority_reference="SMI-230")
        add(f"{panel}_dc_damping_capacitor_total", parent=dc_damping_group, field_label="Total Capacitor Value",
            field_type="number", required=True, unit="uF")
        add(f"{panel}_dc_damping_resistance_total", parent=dc_damping_group, field_label="Total Resistance Value",
            field_type="number", required=True, unit="kOhm")
        add(f"{panel}_dc_damping_resistance_01ohm_total", parent=dc_damping_group, field_label=
            "Total Resistance Value (0.1 Ohm, 02 Nos.)", field_type="number", required=False, unit="Ohm")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="RSI", template_code="39", technology="CONVENTIONAL",
        template_name="Checksheet for RSI",
        description="RSI (Rectifier, Conventional) checksheet - M9-HR section.",
        build_fn=build,
    )
