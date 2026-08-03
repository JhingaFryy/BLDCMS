"""
Module 37: seeds the 25 KV Surge Arrestor checksheet template for BOTH S- Arrestor Conv and
S- Arrestor 3-Ph equipment IDs - identical content, separate template row per equipment_id (per
Module 37's explicit instruction), never merged.

Run once: `venv/bin/python scripts/seed_surge_arrestor_template.py`

Source: "Check Sheet for 25 KV Surge Arrestor, Rev.-15/11/2025" (as per TC 0136 Rev. '0').
"""
from _aux_template_helpers import run_seed, add_final_remarks


def build(add):
    et1_group = add("sa_et1_details", field_label="ET-1 Details", field_type="group", required=False)
    add("sa_et1_make", parent=et1_group, field_label="Make", field_type="text", required=False)
    add("sa_et1_serial_no", parent=et1_group, field_label="Sr. No.", field_type="text", required=True)

    et2_group = add("sa_et2_details", field_label="ET-2 Details", field_type="group", required=False)
    add("sa_et2_make", parent=et2_group, field_label="Make", field_type="text", required=False)
    add("sa_et2_serial_no", parent=et2_group, field_label="Sr. No.", field_type="text", required=True)

    add("sa_clean_check_damage", field_label="Clean the Surge Arrester; Check for Damage/Crack; "
        "Replace if Damaged", field_type="select", options="Cleaned, Not Cleaned", required=True,
        negative_values="Not Cleaned")
    add("sa_bolted_connections_tightness", field_label="Check Tightness of All Bolted Connections",
        field_type="select", options="Tightened, Not Tightened", required=True, negative_values="Not Tightened")
    add("sa_grounded_pad_provision", field_label="Check That Each Surge Arrester Is Provided a "
        "Grounded Pad", field_type="select", options="Provided, Not Provided", required=True,
        negative_values="Not Provided")
    add("sa_protective_coating_check", field_label="Clean/Remove Old Protective Coating; Check "
        "Crack/Chipping; Replace as Needed; Recoat Insulator", field_type="select",
        options="Done, Not Done", required=True, negative_values="Not Done")

    ir_group = add("sa_ir_value_replacement", field_label="Replace Surge Arrester With IR Value "
        "Less Than 1 G-Ohm", field_type="group", required=False, standard_value="IR value > 1 G-Ohm")
    add("sa_ir_et1", parent=ir_group, field_label="ET-1", field_type="numeric_range", required=True,
        unit="GOhm", min_value=1.0, decimal_precision=0, standard_value="> 1 G-Ohm")
    add("sa_ir_et2", parent=ir_group, field_label="ET-2", field_type="numeric_range", required=True,
        unit="GOhm", min_value=1.0, decimal_precision=0, standard_value="> 1 G-Ohm")

    add("sa_ir_value_5kv_megger", field_label="IR Value Checked With 5KV Megger", field_type="select",
        options="Checked, Not Checked", required=True, negative_values="Not Checked")
    add("sa_hv_testing_leakage", field_label="HV Testing at 40 KV for 10 Seconds; Check Current "
        "Leakage", field_type="text", required=False)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="S- Arrestor Conv", template_code="43", technology="CONVENTIONAL",
        template_name="Checksheet for Surge Arrestor (Conventional)",
        description="25 KV Surge Arrestor checksheet - Conventional - M9-HR section.",
        build_fn=build,
    )
    run_seed(
        equipment_code="S- Arrestor 3-Ph", template_code="47", technology="3_PHASE",
        template_name="Checksheet for Surge Arrestor (3-Phase)",
        description="25 KV Surge Arrestor checksheet - 3-Phase - M9-HR section. Content identical "
        "to the Conventional template by design (Module 37) - implemented as a separate template "
        "row against its own equipment_id, never merged.",
        build_fn=build,
    )
