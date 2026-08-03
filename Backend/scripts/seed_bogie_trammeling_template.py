"""
Module 40: seeds the BT-1 and BT-2 (Bogie Trammeling-1 and -2, during IOH, WAG9HC, 3-Phase,
M4-HR section) checksheet templates.

Run once: `venv/bin/python scripts/seed_bogie_trammeling_template.py`

Source: page 4 of the supplied WAG-9HC checksheet - "Bogie Trammeling (During IOH)", two
identical A-F reference-dimension tables (one per bogie frame) plus a bogie-frame diagram whose
legend gives the same A-F reference values (Ref. DSG: CLW/1209/GD-232/CD-213/GR14.1). The sheet
states only a single reference figure per dimension, no explicit +/- tolerance band, so these are
implemented as plain numeric fields carrying that reference as standard_value rather than
fabricating a min/max window the source does not state.
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
        equipment_code="BT-1", template_code="58", technology="3_PHASE",
        template_name="Checksheet for Bogie Trammeling-1",
        description="Bogie Trammeling (During IOH) - Bogie Frame No.-1 checksheet - WAG9HC, 3-Phase - M4-HR section.",
        build_fn=build,
    )
    run_seed(
        equipment_code="BT-2", template_code="59", technology="3_PHASE",
        template_name="Checksheet for Bogie Trammeling-2",
        description="Bogie Trammeling (During IOH) - Bogie Frame No.-2 checksheet - WAG9HC, 3-Phase - M4-HR section.",
        build_fn=build,
    )
