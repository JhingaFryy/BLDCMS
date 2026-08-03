"""
Module 29.11: seeds the MVSL checksheet template.

Run once: `venv/bin/python scripts/seed_mvsl_template.py`

Field structure is confirmed word-for-word identical to MVSI in the source document (same
checking points, same standards/authorities/ranges) - only the equipment name differs, so this
script reuses seed_mvsi_template.py's build() function directly rather than duplicating it.
"""
from _aux_template_helpers import run_seed
from seed_mvsi_template import build


if __name__ == "__main__":
    run_seed(
        equipment_code="MVSL", template_code="14", technology="CONVENTIONAL",
        template_name="Checksheet for MVSL",
        description="Motor Ventilation blower (MVSL) checksheet.",
        build_fn=build,
    )
