"""
Module 35: seeds the PVT (Primary Voltage Transformer, 3-Phase, M8-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_pvt_template.py`

Source: CHECK SHEET FOR 3 PHASE LOCOMOTIVES (ELS/TRS/BL/M8/15 Rev-1), section
"4. PRIMARY VOLTAGE TRANSFORMER 25 KV/200 V".
"""
from _aux_template_helpers import run_seed, add_final_remarks

REF_3135 = "RDSO L.No. EL/3.1.35/16 dt. 7.2.12"


def build(add):
    add("pvt_porcelain_insulators_cleaned", field_label="Thoroughly Clean the Porcelain Insulators; "
        "Replace if Cracked/Chipped/Burning; Apply Specified Grease and Polish With Soft Lint Free Cloth",
        field_type="select", options="No Abnormality, Abnormality Found", required=True,
        standard_value="Checked, no abnormality", negative_values="Abnormality Found",
        authority_reference=REF_3135)
    add("pvt_roofline_conductor_defects", field_label="Examine the Roofline Conductor for Defects / Looseness",
        field_type="select", options="Tightened, Loose", required=True, standard_value="Tighten",
        negative_values="Loose")
    add("pvt_connections_tightness_after_cap_opening", field_label="Check the Connections for Tightness "
        "After Opening the Cap", field_type="select", options="Tightened, Loose", required=True,
        standard_value="Tighten", negative_values="Loose")
    add("pvt_earthing_shunt_condition", field_label="Check Condition of Earthing Shunt", field_type="select",
        options="Good, Damaged", required=True, standard_value="Good", negative_values="Damaged",
        authority_reference="RDSO SMI 248")
    add("pvt_pt_terminal_wires_fuse_bypass", field_label="Open Terminal for PT & Check Wires for Any "
        "Damage, Tighten the Connections & Check for Fuse Bypass", field_type="select",
        options="Already Bypassed, Bypassed Now, Not Bypassed", required=True,
        standard_value="Already bypass / Bypassed", negative_values="Not Bypassed",
        authority_reference="RDSO MS 277")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="PVT", template_code="29", technology="3_PHASE",
        template_name="Checksheet for PVT",
        description="Primary Voltage Transformer 25KV/200V (3-Phase) checksheet - M8-HR section.",
        build_fn=build,
    )
