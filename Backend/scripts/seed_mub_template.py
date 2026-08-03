"""
Module 35: seeds the MUB (MUB Resistor, 3-Phase, M8-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_mub_template.py`

Source: CHECK SHEET FOR 3 PHASE LOCOMOTIVES (ELS/TRS/BL/M8/15 Rev-1), section "10. MUB RESISTOR"
(spans pages 3-4 of the source PDF - the row wraps mid-sentence: "...Measure the impedance of the
fault detection and MUB resistors. Replace the MUB resistor [page break] assembly if damaged or
defective or not within specification in IOH.").
"""
from _aux_template_helpers import run_seed, add_final_remarks


def build(add):
    add("mub_visual_inspection", field_label="Visually Inspect the MUB Resistor for Evidence of "
        "Overheating, Bending of Resistor Tapes, Discoloration of the Resistors or Its Case, or Burn "
        "Marks; Measure the Impedance of the Fault Detection and MUB Resistors", field_type="select",
        options="No Overheating - Good Condition, Overheating/Damaged", required=True,
        standard_value="No over heating", negative_values="Overheating/Damaged",
        authority_reference="RDSO L.No. EL/3.1.35/16 dt. 7.2.12")
    add("mub_assembly_replaced_ioh", field_label="Replace the MUB Resistor Assembly if Damaged or "
        "Defective or Not Within Specification (IOH)", field_type="select",
        options="Replaced, N/A (IOH only), Not Replaced", required=True, negative_values="Not Replaced")
    add("mub_resistance_value", field_label="Check the Value of MUB Resistance", field_type="numeric_range",
        required=True, unit="Ohm", min_value=2.5745, max_value=2.8455, decimal_precision=2,
        standard_value="2.71 Ohm +/- 5%")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="MUB", template_code="35", technology="3_PHASE",
        template_name="Checksheet for MUB",
        description="MUB Resistor (3-Phase) checksheet - M8-HR section.",
        build_fn=build,
    )
