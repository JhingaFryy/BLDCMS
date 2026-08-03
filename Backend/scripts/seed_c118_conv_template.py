"""
Module 41: seeds the C118_Conv (C118 contactor, WAP-4/Conventional locomotives, M1-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_c118_conv_template.py`

Source: "TOH & IOH For C118.pdf" - "Check Sheet for C118 (ELS/BL)", a 17-item electrical test
performa (coil resistance, pick-up/drop-out voltage, contact pressures/gap, contact wipe/bedding,
copper shunt/arc chute condition, blow-out-coil overheating check, inter-turn/surge test, contactor
opening time lag, aux switch crack check, Q factor, coil locking effectiveness) plus a "Must
Change Item of C118" parts log (Fixed & mobile contact / Auxiliary I/L box / Microswitch, each with
its own PL No.).

Per the module's "Do NOT create fields for Loco Number/Technician/Supervisor Name/Signature" rule,
the sheet's own "Fitted on Loco" and "O/H done by" lines are intentionally not modelled - the
former duplicates the checksheet's auto-captured Locomotive Number, the latter duplicates the
auto-captured Technician identity.
"""
from _aux_template_helpers import add_final_remarks, run_seed

MUST_CHANGE_ITEMS = [
    ("fixed_mobile_contact", "Fixed & Mobile Contact", "23992566"),
    ("auxiliary_il_box", "Auxiliary I/L Box", "23709327"),
    ("microswitch", "Microswitch", "23649823"),
]


def build(add):
    add("overhauling_date", field_label="Date of Overhauling", field_type="date", required=True)
    add("contactor_make", field_label="Make of Contactor", field_type="text", required=True,
        standard_value="Noted")
    add("coil_make", field_label="Coil Make", field_type="text", required=True, standard_value="Noted")
    add("coil_sr_no", field_label="Sr. No. of Coil", field_type="text", required=True, standard_value="Noted")
    add("schedule", field_label="Schedule", field_type="text", required=True, standard_value="Noted")

    add("coil_resistance_20c", field_label="Coil Resistance at 20°C (88 to 102 Ohms)",
        field_type="numeric_range", required=True, unit="Ohm", min_value=88.0, max_value=102.0,
        decimal_precision=0, standard_value="95±8% Ohms")
    add("pick_up_voltage", field_label="Pick Up Voltage", field_type="numeric_range", required=True, unit="V",
        min_value=55.0, max_value=65.0, decimal_precision=1, standard_value="60±5 V.DC")
    add("drop_out_voltage", field_label="Drop Out Voltage", field_type="numeric_range", required=True, unit="V",
        min_value=10.0, max_value=20.0, decimal_precision=1, standard_value="15±5 V.DC")
    add("main_contact_pressure", field_label="Main Contact Pressure", field_type="number", required=True,
        unit="Kg", standard_value="5 Kgs. Min.")
    add("auxiliary_contact_pressure", field_label="Auxiliary Contact Pressure", field_type="numeric_range",
        required=True, unit="gm", min_value=60.0, max_value=100.0, decimal_precision=0,
        standard_value="60-100% gms")
    add("main_contact_gap", field_label="Main Contact Gap", field_type="numeric_range", required=True, unit="mm",
        min_value=16.0, max_value=18.0, decimal_precision=1, standard_value="17±1 mm")
    add("main_contact_wipe_crushing", field_label="Wipe of Main Contact (Crushing)", field_type="number",
        required=True, unit="mm", standard_value="4.5 mm Min.")
    add("main_contact_bedding_check", field_label="Check the Bedding of Main Contact", field_type="number",
        required=True, unit="%", standard_value="85% (Min)")
    add("auxiliary_contact_pitting_check", field_label="Check the Auxiliary Contact for Pitting",
        field_type="select", options="No Pitting Marks, Pitting Found", required=True,
        standard_value="No Pitting Marks", negative_values="Pitting Found")
    add("copper_shunts_condition", field_label="Check the Condition of Copper Shunts (Replace if Stiff or Badly "
        "Frayed & More Than 10% Strands Are Out)", field_type="select", options="Good Condition, Replaced",
        required=True, standard_value="Good Condition")
    add("arc_chute_condition", field_label="Check the Condition of Arc Chute", field_type="select",
        options="Good Condition, Not Good", required=True, standard_value="Good Condition",
        negative_values="Not Good")
    add("blow_out_coil_overheating_check", field_label="Check for Over Heating Marks on Blow Out Coil",
        field_type="select", options="No Over Heating Marks, Over Heating Marks Found", required=True,
        standard_value="No Over Heating Marks", negative_values="Over Heating Marks Found")
    add("coil_interturn_surge_test", field_label="Check the Coil for Inter Turn Short and Surge Test",
        field_type="select", options="OK, Not OK", required=True,
        standard_value="No Inter Turn Shorting & Surge OK", authority_reference="SMI-157",
        negative_values="Not OK")
    add("contactor_opening_time_lag", field_label="Check the Time Lag Obtained During Opening of the Contactor",
        field_type="number", required=True, unit="sec", standard_value="5 Seconds")
    add("aux_switch_operating_strip_crack_check", field_label="Check the Aux Switch Operating Strip for "
        "Crackness by Dismantling It", field_type="select", options="No Crack/MPT OK, Crack Found",
        required=True, standard_value="No Crack, MPT - OK", negative_values="Crack Found")
    add("coil_q_factor_check", field_label="Check Q Factor of Coil", field_type="number", required=True)
    add("coil_locking_effectiveness_check", field_label="Check Effectiveness of Coil Locking",
        field_type="select", options="OK, Not OK", required=True, standard_value="OK", negative_values="Not OK")

    must_change_group = add("must_change_item", field_label="Must Change Item of C118", field_type="group",
                             required=False)
    for key, label, pl_no in MUST_CHANGE_ITEMS:
        item_group = add(f"must_change_{key}", parent=must_change_group, field_label=label, field_type="group",
                          required=False, standard_value=f"PL No. {pl_no}")
        add(f"must_change_{key}_status", parent=item_group, field_label="Change/Not Change", field_type="select",
            options="Changed, Not Changed", required=False)
        add(f"must_change_{key}_make", parent=item_group, field_label="Make", field_type="text", required=False)
        add(f"must_change_{key}_mfg_year", parent=item_group, field_label="Mfg/Year", field_type="text",
            required=False)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="C118_Conv", template_code="123", technology="CONVENTIONAL",
        template_name="Checksheet for C118",
        description="Check sheet for C118 contactor (ELS/BL) - Conventional - M1-HR section.",
        build_fn=build,
    )
