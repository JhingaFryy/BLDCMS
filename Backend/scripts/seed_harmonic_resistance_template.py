"""
Module 35: seeds the Harmonic Resistance (3-Phase, M8-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_harmonic_resistance_template.py`

Source: CHECK SHEET FOR 3 PHASE LOCOMOTIVES (ELS/TRS/BL/M8/15 Rev-1), section
"7. HARMONIC RESISTANCE".
"""
from _aux_template_helpers import run_seed, add_final_remarks

REF_3135 = "RDSO L.No. EL/3.1.35/16 dt. 7.2.12"


def build(add):
    add("harmonic_resistance_grid_cleaned", field_label="Remove the Protection Grid and Clean the Filter "
        "Resistor, Roof Mounted Resistor, Insulators and Ceramic Components and Check for Any Signs of "
        "Damage; Remove All Dirt and Debris; Check Tightness of Electrical Connectors",
        field_type="select", options="Done, Not Done", required=True, standard_value="Done",
        negative_values="Not Done", authority_reference=REF_3135)
    add("harmonic_resistance_earthing_shunt_condition", field_label="Check Condition of Earthing Shunt",
        field_type="select", options="Good, Damaged", required=True, standard_value="Good",
        negative_values="Damaged", authority_reference="SMI 248")
    add("harmonic_resistance_roof_mounting_cleaned", field_label="Ensure Cleaning of Roof Mounting Resistor",
        field_type="select", options="Done, Not Done", required=True, standard_value="Done",
        negative_values="Not Done")
    add("harmonic_resistance_electrical_connection", field_label="Check Electrical Connection of "
        "Resistance to Resistance", field_type="select", options="Intact, Not Intact", required=True,
        standard_value="Checked & intact", negative_values="Not Intact")

    resistance = add("harmonic_resistance_value", field_label="Check Resistance Value of Resistance "
        "Elements", field_type="group", required=False,
        standard_value="0.194 Ohm +/- 5% is standard value at 20C")
    add("harmonic_resistance_1_2", parent=resistance, field_label="Resistance 1-2", field_type="numeric_range",
        required=True, unit="Ohm", min_value=0.1843, max_value=0.2037, decimal_precision=3)
    add("harmonic_resistance_2_3", parent=resistance, field_label="Resistance 2-3", field_type="numeric_range",
        required=True, unit="Ohm", min_value=0.1843, max_value=0.2037, decimal_precision=3)
    add("harmonic_resistance_1_3", parent=resistance, field_label="Resistance 1-3", field_type="numeric_range",
        required=True, unit="Ohm", min_value=0.1843, max_value=0.2037, decimal_precision=3)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="Harmonic Resistance", template_code="32", technology="3_PHASE",
        template_name="Checksheet for Harmonic Resistance",
        description="Harmonic Resistance (3-Phase) checksheet - M8-HR section.",
        build_fn=build,
    )
