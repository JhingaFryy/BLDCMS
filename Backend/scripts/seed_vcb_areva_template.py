"""
Module 37: seeds the VCB- Areva 22CB checksheet template for BOTH VCB- Areva Conv and
VCB- Areva 3-Ph equipment IDs - the checksheet content is identical between the two
technologies (per Module 37's explicit instruction), but per Module 37's explicit instruction each
technology gets its OWN template row against its OWN equipment_id - never merged or shared.

Run once: `venv/bin/python scripts/seed_vcb_areva_template.py`

Source: "Check Sheet for S.B. VCB 22 CB (AREVA)".
"""
from _aux_template_helpers import run_seed, add_final_remarks


def build(add):
    add("vcb_serial_no", field_label="VCB Sr. No.", field_type="text", required=True)
    add("vcb_mfg_doc", field_label="VCB Mfg / Doc", field_type="text", required=False)

    add("vcb_surge_suppressor_current", field_label="Surge Suppressor Current at 110V AC Only "
        "(Plastofab as per OEM)", field_type="numeric_range", required=False, unit="mA",
        min_value=14.0, max_value=19.5, decimal_precision=1, standard_value="14-19.5 mA")
    add("vcb_pressure_regulator_setting", field_label="Pressure Regulator Setting",
        field_type="number", required=True, unit="kg/cm2",
        standard_value="5.0-5.2 kg/cm2 (OEM) / 5.8 kg/cm2 (Shed Practice)")

    qpdj_group = add("vcb_qpdj_setting", field_label="Test QPDJ Setting and Record", field_type="group",
        required=False)
    add("vcb_qpdj_cut_in", parent=qpdj_group, field_label="Cut In", field_type="numeric_range",
        required=True, unit="kg/cm2", min_value=4.1, max_value=4.5, decimal_precision=1,
        standard_value="4.3 kg/cm2")
    add("vcb_qpdj_cut_out", parent=qpdj_group, field_label="Cut Out", field_type="numeric_range",
        required=True, unit="kg/cm2", min_value=3.4, max_value=3.8, decimal_precision=1,
        standard_value="3.6 kg/cm2")

    add("vcb_pickup_voltage", field_label="Pickup Voltage", field_type="numeric_range", required=True,
        unit="VDC", min_value=55.0, max_value=70.0, decimal_precision=1, standard_value="55-70 VDC")
    add("vcb_contact_travel", field_label="VCB Contact Travel (Closing & Opening Speed of VST)",
        field_type="numeric_range", required=True, unit="mm", min_value=9.8, max_value=13.0,
        decimal_precision=1, standard_value="9.8-11.3mm (Plastofab) / 11.4-13mm (Rotex)")

    analyzer_group = add("vcb_analyzer_timing", field_label="Closing Time, Opening Time, EV On "
        "Time, and Counter Operation (Electronic Control Unit)", field_type="group", required=False,
        authority_reference="VCB Analyzer machine")
    add("vcb_closing_time", parent=analyzer_group, field_label="Closing Time", field_type="number",
        required=False, unit="ms")
    add("vcb_opening_time", parent=analyzer_group, field_label="Opening Time", field_type="number",
        required=False, unit="ms")

    magnet_valve_res_group = add("vcb_magnet_valve_resistance", field_label="Magnet Valve "
        "Resistance at R20C", field_type="group", required=False)
    add("vcb_magnet_valve_resistance_plastofab", parent=magnet_valve_res_group,
        field_label="Plastofab", field_type="numeric_range", required=False, unit="Ohm",
        min_value=798.0, max_value=882.0, decimal_precision=0, standard_value="840 Ohm +/- 5%")
    add("vcb_magnet_valve_resistance_rotex", parent=magnet_valve_res_group, field_label="Rotex",
        field_type="numeric_range", required=False, unit="Ohm", min_value=1435.2, max_value=1684.8,
        decimal_precision=0, standard_value="1560 Ohm +/- 8%")

    magnet_valve_clearance_group = add("vcb_magnet_valve_clearance", field_label="Magnet Valve "
        "Clearance Plastofab Make", field_type="group", required=False)
    add("vcb_armature_plate_clearance", parent=magnet_valve_clearance_group, field_label=
        "Between Armature and Armature Plate", field_type="numeric_range", required=False, unit="mm",
        min_value=0.51, max_value=0.61, decimal_precision=2)
    add("vcb_floated_valve_stem_clearance", parent=magnet_valve_clearance_group, field_label=
        "Between Top Floated Valve and Stem", field_type="text", required=False,
        standard_value="Slight clearance must be available")

    hv_group = add("vcb_hv_testing", field_label="H.V Testing (One Minute at 40 KV, VCB Open)",
        field_type="group", required=False, standard_value="AQ/BSL/KYN Shed Meeting")
    add("vcb_hv_ic_to_og", parent=hv_group, field_label="Incoming Terminal to Outgoing Terminal",
        field_type="number", required=True, unit="mA")
    add("vcb_hv_ic_to_earth", parent=hv_group, field_label="Incoming Terminal to Earth Terminal",
        field_type="number", required=True, unit="mA")
    add("vcb_hv_og_to_earth", parent=hv_group, field_label="Outgoing Terminal to Earth Terminal",
        field_type="number", required=True, unit="mA")

    ir_group = add("vcb_ir_value", field_label="I.R Value", field_type="group", required=False)
    add("vcb_ir_power_circuit", parent=ir_group, field_label="Power Circuit (1KV Megger)",
        field_type="text", required=True, standard_value="> 200 M-Ohm")
    add("vcb_ir_lt_circuit", parent=ir_group, field_label="L.T Circuit (500V Megger)", field_type="text",
        required=True, standard_value="> 10 M-Ohm")

    air_leakage_group = add("vcb_air_leakage_test", field_label="Air Leakage Test (After Applying "
        "6.5kg/cm2 Air Pressure, Check Pressure Drop After 10 Minutes)", field_type="group",
        required=False, standard_value="Drop must not exceed 10% of initial pressure")
    add("vcb_air_leakage_vcb_off", parent=air_leakage_group, field_label="VCB OFF Position",
        field_type="select", options="No Leakage, Leakage", required=True, negative_values="Leakage")
    add("vcb_air_leakage_vcb_on", parent=air_leakage_group, field_label="VCB ON Position",
        field_type="select", options="No Leakage, Leakage", required=True, negative_values="Leakage")

    add("vcb_endurance_test", field_label="Endurance Test (200 Operations on Test Bench, Check "
        "for Any Abnormality)", field_type="select", options="Done, Not Done", required=True,
        negative_values="Not Done")
    add("vcb_auxiliary_switch_check", field_label="Auxiliary Switch Check and Contact Spot Cleaning",
        field_type="select", options="Done, Not Done", required=True, negative_values="Not Done")

    overhaul_group = add("vcb_overhaul", field_label="Overhaul (As Per OEM)", field_type="group",
        required=False)
    add("vcb_overhaul_magnet_valve", parent=overhaul_group, field_label="Magnet Valve Assembly",
        field_type="select", options="Done, Not Done", required=True, negative_values="Not Done")
    add("vcb_overhaul_air_filter", parent=overhaul_group, field_label="Air Filter", field_type="select",
        options="Done, Not Done", required=True, negative_values="Not Done")
    add("vcb_overhaul_pressure_switch", parent=overhaul_group, field_label="Pressure Switch",
        field_type="select", options="Done, Not Done", required=True, negative_values="Not Done")
    add("vcb_overhaul_pressure_regulator", parent=overhaul_group, field_label="Pressure Regulator",
        field_type="select", options="Done, Not Done", required=True, negative_values="Not Done")
    add("vcb_overhaul_relay_valve_assembly", parent=overhaul_group, field_label="Relay Valve Assembly",
        field_type="select", options="Available, Not Available", required=True, negative_values="Not Available")

    add("vcb_piston_assembly_provided", field_label="Piston Assembly Below to Be Provided",
        field_type="select", options="Available, Not Available", required=True, negative_values="Not Available")
    add("vcb_araldite_applied", field_label="Apply Araldite on Inner and Outer Both Sides",
        field_type="select", options="Done, Not Done", required=True, negative_values="Not Done")
    add("vcb_vst_allen_bolt_rtv", field_label="Tightening Allen Bolt of VST and Seal With RTV-685",
        field_type="select", options="Done, Not Done", required=True, negative_values="Not Done")
    add("vcb_insulator_crack_flashmark", field_label="Check the Insulator for Cracks or Any Flash Mark",
        field_type="select", options="No Crack/Flashmark, Crack/Flashmark Found", required=True,
        standard_value="No crack, no flashmark", negative_values="Crack/Flashmark Found")

    must_change_group = add("vcb_must_change_items", field_label="Must Change Items (VCB 22CB, "
        "as per SMI-236)", field_type="group", required=False)
    add("vcb_must_change_aoh_kit", parent=must_change_group, field_label="AOH Replacement Kit",
        field_type="select", options="Changed, Not Changed", required=True,
        authority_reference="PL 25-71-8150")
    add("vcb_must_change_ioh_kit", parent=must_change_group, field_label="IOH Replacement Kit",
        field_type="select", options="Changed, Not Changed", required=True,
        authority_reference="PL 25-71-8642")

    add("vcb_smi162_moly44", field_label="Lubricants MOLY44 to Be Used in Relay Valve",
        field_type="select", options="Applied, Not Applied", required=True, negative_values="Not Applied",
        authority_reference="SMI 162")
    add("vcb_smi285_rtv1080", field_label="Re-Application of RTV 1080 Selant", field_type="select",
        options="Done, Not Done", required=True, negative_values="Not Done", authority_reference="SMI 285")
    add("vcb_smi281_loctite518", field_label="Use of Loctite 518 in Place of RTV 1080 (Schneider VCB)",
        field_type="select", options="Done, Not Done", required=True, negative_values="Not Done",
        authority_reference="SMI 281")
    add("vcb_smi137_air_dryer", field_label="Maintenance of Air Dryer", field_type="text",
        required=False, authority_reference="SMI 137")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="VCB- Areva Conv", template_code="40", technology="CONVENTIONAL",
        template_name="Checksheet for VCB- Areva (Conventional)",
        description="VCB 22CB (Areva) checksheet - Conventional - M9-HR section.",
        build_fn=build,
    )
    run_seed(
        equipment_code="VCB- Areva 3-Ph", template_code="49", technology="3_PHASE",
        template_name="Checksheet for VCB- Areva (3-Phase)",
        description="VCB 22CB (Areva) checksheet - 3-Phase - M9-HR section. Content identical to "
        "the Conventional template by design (Module 37) - implemented as a separate template row "
        "against its own equipment_id, never merged.",
        build_fn=build,
    )
