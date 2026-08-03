"""
Module 40: seeds the BT-1_P7 and BT-2_P7 (Bogie Trammeling-1 and -2, during IOH, WAP-7, 3-Phase,
M4-HR section) checksheet templates.

Run once: `venv/bin/python scripts/seed_bogie_trammeling_p7_template.py`

Source: page 3 of the supplied WAP-7 checksheet - "Bogie Trammeling", two identical A-F
reference-dimension tables (one per bogie frame). Same reference figures as the WAG9HC bogie
frame (this bogie frame drawing is shared across WAG9HC/WAP-7 locos per the sheet's own
"BOGIE FRAME WAP7 LOCOS" diagram label), still implemented as its own independent template per
equipment_id since BT-1_P7/BT-2_P7 are separate equipment records from BT-1/BT-2.
"""
from _m4hr_template_helpers import add_final_remarks, run_seed

DIMENSIONS = [
    ("a", "A", 4325.0),
    ("b", "B", 2490.0),
    ("c", "C", 2240.0),
    ("d", "D", 6042.0),
    ("e", "E", 2480.0),
    ("f", "F", 1850.0),
]


def build(add):
    for key, label, value in DIMENSIONS:
        add(f"trammeling_{key}", field_label=f"Dimension {label}", field_type="number", required=True,
            unit="mm", standard_value=f"{value:g}mm", authority_reference="CLW/1209/GD-232/CD-213/GR14.1")
    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="BT-1_P7", template_code="82", technology="3_PHASE",
        template_name="Checksheet for Bogie Trammeling-1 (WAP-7)",
        description="Bogie Trammeling (During IOH) - Bogie Frame No.-1 checksheet - WAP-7, 3-Phase - M4-HR section.",
        build_fn=build,
    )
    run_seed(
        equipment_code="BT-2_P7", template_code="83", technology="3_PHASE",
        template_name="Checksheet for Bogie Trammeling-2 (WAP-7)",
        description="Bogie Trammeling (During IOH) - Bogie Frame No.-2 checksheet - WAP-7, 3-Phase - M4-HR section.",
        build_fn=build,
    )
