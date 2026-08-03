"""
Module 37: seeds the VCB- Autometer (AAL/BTIL) checksheet template for BOTH VCB- Autometer Conv
and VCB- Autometer 3-Ph equipment IDs - identical content, separate template row per equipment_id
(per Module 37's explicit instruction), never merged.

Run once: `venv/bin/python scripts/seed_vcb_autometer_template.py`

Source: "Check Sheet for S.B. VCB AAL/BTIL (Type VCBA 25.10 Tr)".
"""
from _aux_template_helpers import run_seed, add_final_remarks


def build(add):
    add("vcb_serial_no", field_label="VCB Sr. No.", field_type="text", required=True)
    add("vcb_mfg_doc", field_label="VCB Mfg / Doc", field_type="text", required=False)

    ir_group = add("vcb_ir_value", field_label="IR Value", field_type="group", required=False)
    for row_key, row_label in [("a", "I/C and O/G of Main Circuit"), ("b", "Main Connection to W.R.T Earth"),
                                ("c", "O/G to W.R.T Earth"), ("d", "Control Wiring to W.R.T Earth")]:
        add(f"vcb_ir_{row_key}_power", parent=ir_group, field_label=f"{row_label} - Power Ckt.",
            field_type="text", required=True, standard_value="> 200 M-Ohm (1KV Megger)")
        add(f"vcb_ir_{row_key}_lt", parent=ir_group, field_label=f"{row_label} - L.T Ckt.",
            field_type="text", required=True, standard_value="> 10 M-Ohm (500V Megger)")

    add("vcb_insulator_crack_flashmark", field_label="Check the Insulator for Cracks or Flash Mark",
        field_type="select", options="Checked & Clean, Crack/Flashmark Found", required=True,
        standard_value="Check and clean, no crack", negative_values="Crack/Flashmark Found")

    aux_switch_group = add("vcb_auxiliary_switch", field_label="Auxiliary Switch", field_type="group",
        required=False)
    add("vcb_aux_switch_screw_check", parent=aux_switch_group, field_label="Check the Screw for "
        "Broken or Damaged", field_type="select", options="Done, Not Done", required=True,
        negative_values="Not Done")
    add("vcb_aux_switch_contacts_continuity", parent=aux_switch_group, field_label="Check "
        "Continuity of Moving Contacts", field_type="select", options="Done, Not Done", required=True,
        negative_values="Not Done")
    add("vcb_aux_switch_cable_check", parent=aux_switch_group, field_label="Check That the Cable "
        "Is Not Broken or Loose", field_type="select", options="Done, Not Done", required=True,
        negative_values="Not Done")
    add("vcb_aux_switch_support_plate", parent=aux_switch_group, field_label="Ensure Auxiliary "
        "Switch and Support Plate Are in Place", field_type="select", options="Done, Not Done",
        required=True, negative_values="Not Done")
    add("vcb_aux_switch_wiring_sequence", parent=aux_switch_group, field_label="Check the Wiring "
        "Sequence of Each Auxiliary Contact", field_type="select", options="Done, Not Done",
        required=True, negative_values="Not Done")

    add("vcb_leakage_test", field_label="Leakage Test (< 10% at 6.5 kg/cm2 in 10 Minutes)",
        field_type="select", options="No Leakage, Leakage", required=True, negative_values="Leakage")
    add("vcb_pneumatic_circuit_sealing", field_label="Check Sealing of Connections, Flexible Pipe "
        "and Regulator", field_type="select", options="Done, Not Done", required=True,
        negative_values="Not Done")
    add("vcb_pressure_regulator_setting", field_label="Pressure Regulator Setting",
        field_type="numeric_range", required=True, unit="kg/cm2", min_value=4.9, max_value=5.1,
        decimal_precision=1, standard_value="5.0 kg/cm2 +/- 0.1")

    holding_coil_group = add("vcb_holding_coil_resistance", field_label="Check Resistance of "
        "Holding Coil", field_type="group", required=False)
    add("vcb_holding_coil_aal", parent=holding_coil_group, field_label="AAL Hold", field_type="numeric_range",
        required=True, unit="Ohm", min_value=1390.0, max_value=1630.0, decimal_precision=0,
        standard_value="1390-1630 Ohm")
    add("vcb_holding_coil_bt_hold", parent=holding_coil_group, field_label="BT Hold", field_type="numeric_range",
        required=False, unit="Ohm", min_value=690.0, max_value=810.0, decimal_precision=0,
        standard_value="690-810 Ohm")
    add("vcb_holding_coil_bt_ev", parent=holding_coil_group, field_label="BT EV Coil", field_type="numeric_range",
        required=False, unit="Ohm", min_value=274.0, max_value=321.0, decimal_precision=0,
        standard_value="274-321 Ohm")

    pressure_switch_group = add("vcb_pressure_switch_setting", field_label="Pressure Switch Setting",
        field_type="group", required=False)
    add("vcb_pressure_switch_cut_in", parent=pressure_switch_group, field_label="Cut In",
        field_type="numeric_range", required=True, unit="kg/cm2", min_value=3.5, max_value=3.7,
        decimal_precision=1, standard_value="3.6 kg/cm2")
    add("vcb_pressure_switch_cut_out", parent=pressure_switch_group, field_label="Cut Out",
        field_type="numeric_range", required=True, unit="kg/cm2", min_value=3.2, max_value=3.4,
        decimal_precision=1, standard_value="3.3 kg/cm2")

    add("vcb_minimum_operating_voltage", field_label="Minimum Operating Voltage", field_type="numeric_range",
        required=True, unit="V", max_value=77.0, decimal_precision=1, standard_value="<= 77.0V")
    add("vcb_speed_travel_record", field_label="Take Speed Travel Record", field_type="numeric_range",
        required=True, unit="mm", min_value=18.5, max_value=20.5, decimal_precision=1,
        standard_value="18.5-20.5mm")

    hv_group = add("vcb_high_voltage_test", field_label="High Voltage Test", field_type="group",
        required=False, standard_value="40 kV AC for 10 sec With Stand")
    add("vcb_hv_fix_contact_earth", parent=hv_group, field_label="Fix Contact (HT) to Earth & "
        "Moving Contact", field_type="number", required=True, unit="mA")
    add("vcb_hv_earth_to_contacts_ola", parent=hv_group, field_label="Earth to Contacts (HT) - "
        "OLA to Earth", field_type="number", required=True, unit="mA")
    add("vcb_hv_ic_to_ola", parent=hv_group, field_label="I/C to OLA", field_type="number",
        required=True, unit="mA")

    add("vcb_analyzer_timing_check", field_label="Check Closing Time, Opening Time, EV On Time & "
        "Counter Operation (Electronic Control Unit)", field_type="text", required=False,
        authority_reference="VCB Analyzer machine")

    must_change_group = add("vcb_must_change_items", field_label="Must Change Items (as per "
        "RDSO SMI-236 Rev.1)", field_type="group", required=False)
    add("vcb_must_change_aoh_kit_aal", parent=must_change_group, field_label="AOH Replacement Kit AAL",
        field_type="select", options="Changed, Not Changed", required=True,
        authority_reference="PL 29-71-8260")
    add("vcb_must_change_ioh_kit_aal", parent=must_change_group, field_label="IOH Replacement Kit AAL",
        field_type="select", options="Changed, Not Changed", required=True,
        authority_reference="PL 31-43-7072")
    add("vcb_must_change_aoh_kit_btil", parent=must_change_group, field_label="AOH Replacement Kit BTIL",
        field_type="select", options="Changed, Not Changed", required=False,
        authority_reference="PL 25-71-8381")
    add("vcb_must_change_ioh_kit_btil", parent=must_change_group, field_label="IOH Replacement Kit BTIL",
        field_type="select", options="Changed, Not Changed", required=False,
        authority_reference="PL 25-71-8885")

    add("vcb_smi137_air_dryer", field_label="Maintenance of Air Dryer", field_type="text",
        required=False, authority_reference="RDSO SMI-137")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="VCB- Autometer Conv", template_code="41", technology="CONVENTIONAL",
        template_name="Checksheet for VCB- Autometer (Conventional)",
        description="VCB AAL/BTIL (Type VCBA 25.10 Tr) checksheet - Conventional - M9-HR section.",
        build_fn=build,
    )
    run_seed(
        equipment_code="VCB- Autometer 3-Ph", template_code="50", technology="3_PHASE",
        template_name="Checksheet for VCB- Autometer (3-Phase)",
        description="VCB AAL/BTIL (Type VCBA 25.10 Tr) checksheet - 3-Phase - M9-HR section. "
        "Content identical to the Conventional template by design (Module 37) - implemented as a "
        "separate template row against its own equipment_id, never merged.",
        build_fn=build,
    )
