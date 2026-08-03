"""
Module 35: seeds the SR-Coolant/Oil (Traction Converter, 3-Phase, M8-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_sr_coolant_oil_template.py`

Source: CHECK SHEET FOR 3 PHASE LOCOMOTIVES (ELS/TRS/BL/M8/15 Rev-1), section
"5. TRACTION CONVERTER (SR)".
"""
from _aux_template_helpers import run_seed, add_final_remarks


def build(add):
    add("sr_coolant_sample_checking", field_label="Coolant Sample Checking - pH, Ethylene Glycol %, "
        "Reverse Alkaline", field_type="select", options="Tested, Not Tested", required=True,
        standard_value="Ethylene glycol 30%, pH value 7.7-8.5, Reverse Alkaline test",
        negative_values="Not Tested", authority_reference="SMI 325")

    level = add("sr_coolant_level_check", field_label="Check the Oil/Coolant Level Indicator Situated on "
        "the Conservator (Expansion Tank); Top Up if Below Minimum Mark; Check for Any Signs of Leakage",
        field_type="group", required=False)
    add("sr_coolant_level", parent=level, field_label="Level", field_type="select",
        options="Between Min & Max, Below Minimum, Above Maximum", required=True,
        standard_value="Between min & max", negative_values="Below Minimum, Above Maximum")
    add("sr_coolant_leakage", parent=level, field_label="Leakage Check", field_type="select",
        options="No Leakage, Leakage", required=True, standard_value="No leakage",
        negative_values="Leakage")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="SR-Coolant/Oil", template_code="30", technology="3_PHASE",
        template_name="Checksheet for SR-Coolant/Oil",
        description="Traction Converter (SR) Coolant/Oil (3-Phase) checksheet - M8-HR section.",
        build_fn=build,
    )
