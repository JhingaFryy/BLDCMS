"""
Module 35: seeds the Aux. Transformer (Auxiliary Transformer, 3-Phase, M8-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_aux_transformer_template.py`

Source: CHECK SHEET FOR 3 PHASE LOCOMOTIVES (ELS/TRS/BL/M8/15 Rev-1), section
"8. AUXILIARY TRANSFORMER 1000/415 Volt".
"""
from _aux_template_helpers import run_seed, add_final_remarks

REF_3135 = "RDSO L.No. EL/3.1.35/16 dt. 7.2.12"


def build(add):
    add("aux_transformer_dirt_dust_cleaned", field_label="Clean All Dirt and Dust Deposit by Means of "
        "Blowing Out, Brushing With a Non-Metallic Brush or by Rubbing With a Cloth", field_type="select",
        options="Done, Not Done", required=True, standard_value="Done", negative_values="Not Done",
        authority_reference=REF_3135)
    add("aux_transformer_connections_secure", field_label="Check That All Connections Are Secure and "
        "There Is No Physical Damage", field_type="select", options="Intact, Not Intact", required=True,
        standard_value="Checked & intact", negative_values="Not Intact")
    add("aux_transformer_foundation_bolt_tightness", field_label="All Foundation Bolt to Check for "
        "Proper Tightness", field_type="select", options="Tight, Loose", required=True,
        standard_value="Checked", negative_values="Loose")
    add("aux_transformer_earthing_shunt_check", field_label="Earthing Shunt to Check", field_type="select",
        options="OK, Not OK", required=True, standard_value="Checked", negative_values="Not OK",
        authority_reference="RDSO SMI 248")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="Aux. Transformer", template_code="33", technology="3_PHASE",
        template_name="Checksheet for Aux. Transformer",
        description="Auxiliary Transformer 1000/415 Volt (3-Phase) checksheet - M8-HR section.",
        build_fn=build,
    )
