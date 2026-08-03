"""
Module 40: seeds the MSU_P7 (Motor Suspension Unit, WAP-7, 3-Phase, M4-HR section) checksheet
template.

Run once: `venv/bin/python scripts/seed_msu_p7_template.py`

Source: page 4 of the supplied WAP-7 checksheet - "Motor Suspension Unit", 5 schedule activities
repeated once per wheel set (W/S-1 through W/S-6). Identical activities/standards to the WAG9HC
MSU sheet - implemented as its own independent template since MSU_P7 is a separate equipment
record from MSU.
"""
from _m4hr_template_helpers import add_final_remarks, add_unit_group_table, run_seed

WHEEL_SETS = [1, 2, 3, 4, 5, 6]


def build(add):
    activities = [
        {"key": "gear_case_oil_sample", "label": "Check the Gear Case Oil Sample of MSU DE Side "
            "for Metal Content (RDSO/SMI-324)", "field_type": "select", "options": "Checked, Not Checked",
            "required": True, "standard_value": "Checked", "negative_values": "Not Checked"},
        {"key": "grease_sample_nde", "label": "Check the Grease Sample of MSU NDE Side for Metal Content.",
            "field_type": "select", "options": "Checked, Not Checked", "required": True,
            "standard_value": "Checked", "negative_values": "Not Checked"},
        {"key": "labyrinth_ring_intactness", "label": "Check the Intactness of MSU Labyrinth Ring "
            "(Socket Screw-DE Side-12x25 & NDE Side-12x35)", "field_type": "select",
            "options": "Checked, Not Checked", "required": True, "standard_value": "Checked",
            "negative_values": "Not Checked"},
        {"key": "greasing_nde", "label": "Greasing to Be Done in Motor Suspension Unit (MSU) at "
            "NDE Side (Servoplex SHC-120 Grease) (RDSO/SMI-246)", "field_type": "number",
            "required": True, "unit": "gm", "standard_value": "100 gm", "authority_reference": "RDSO/SMI-246"},
        {"key": "o_ring_check_replace", "label": "Check and Replace 'O' Ring of MSU (IOH - Must Change)",
            "field_type": "select", "options": "Checked, Replaced", "required": True,
            "standard_value": "Checked/Replace"},
    ]
    add_unit_group_table(add, "msu", "Wheel Set", WHEEL_SETS, activities)
    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="MSU_P7", template_code="84", technology="3_PHASE",
        template_name="Checksheet for Motor Suspension Unit (WAP-7)",
        description="Motor Suspension Unit checksheet - WAP-7, 3-Phase - M4-HR section.",
        build_fn=build,
    )
