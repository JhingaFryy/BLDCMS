"""
Module 35: seeds the HV Bushing (3-Phase, M8-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_hv_bushing_template.py`

Source: CHECK SHEET FOR 3 PHASE LOCOMOTIVES (ELS/TRS/BL/M8/15 Rev-1), section
"3. HIGH VOLTAGE BUSHING".
"""
from _aux_template_helpers import run_seed, add_final_remarks

REF_3135 = "RDSO L.No. EL/3.1.35/16 dt. 7.2.12"


def build(add):
    add("hv_bushing_cleaned_coating", field_label="Thoroughly Clean and Remove Any Previous Protective "
        "Coating; Examine for Cracks/Chipping and Replace as Necessary", field_type="select",
        options="Checked & Cleaned, Damaged/Replaced", required=True, standard_value="Checked & Cleaned",
        negative_values="Damaged/Replaced", authority_reference=REF_3135)
    add("hv_bushing_creepage_carbonization", field_label="Examine for Creepage/Carbonization; Recoat "
        "With the Specified Coating", field_type="select", options="Checked, Not Checked", required=True,
        standard_value="Checked", negative_values="Not Checked")
    add("hv_bushing_tan_delta_test_ioh", field_label="Tan Delta Test in Case of Mica Filled HV Bushing (IOH)",
        field_type="select", options="Done, N/A (IOH only), Not Done", required=True,
        negative_values="Not Done")
    add("hv_bushing_earthing_shunt_condition", field_label="Check Condition of Earthing Shunt",
        field_type="select", options="Good, Damaged", required=True, standard_value="Good",
        negative_values="Damaged", authority_reference="SMI 248")
    add("hv_bushing_foundation_bolt_rtv", field_label="Check All Foundation Bolt for Proper Tightness "
        "& RTV to Be Applied", field_type="select", options="RTV Applied, Not Applied", required=True,
        standard_value="RTV Applied", negative_values="Not Applied")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="HV Bushing", template_code="28", technology="3_PHASE",
        template_name="Checksheet for HV Bushing",
        description="High Voltage Bushing (3-Phase) checksheet - M8-HR section.",
        build_fn=build,
    )
