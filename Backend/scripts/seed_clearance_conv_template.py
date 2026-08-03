"""
Module 40: seeds the Clearance_Conv (Longitudinal & Lateral Clearance, WAP-4, Conventional, M4-HR
section) checksheet template.

Run once: `venv/bin/python scripts/seed_clearance_conv_template.py`

Source: page 16 of the supplied WAP-4 checksheet - "Longitudinal & Lateral Clearance for WAP-4
Loco" (Ref: MPIBVL.05.06, Rev.'0' Dt.-03/08/06), recorded per axle-box position (1-12, two
positions per wheel set, six wheel sets). Longitudinal clearance uses a single standard for every
position. Lateral clearance uses two different standards depending on whether the position is an
End Axle or a Middle Axle - the reference sheet prints both standard rows for every position and
the technician fills in only the one that applies to that physical axle, so both are modelled as
optional numeric fields rather than guessing a fixed end/middle mapping per position.
"""
from _m4hr_template_helpers import add_final_remarks, add_unit_group_table, run_seed

POSITIONS = list(range(1, 13))
AUTHORITY = "MPIBVL.05.06, Rev.'0' Dt.-03/08/06"


def build(add):
    activities = [
        {"key": "longitudinal_clearance", "label": "Longitudinal Clearance (High Speed Axle Box)",
         "field_type": "numeric_range", "required": True, "unit": "mm", "min_value": 0.40, "max_value": 2.00,
         "decimal_precision": 2, "standard_value": "Min.-0.40mm, Max.-2.00mm, Service Limit-4.00mm",
         "authority_reference": AUTHORITY},
        {"key": "lateral_clearance_end_axle", "label": "Lateral Clearance - End Axle", "field_type": "numeric_range",
         "required": False, "unit": "mm", "min_value": 15.40, "max_value": 18.20, "decimal_precision": 2,
         "standard_value": "Min.-15.40mm, Max.-18.20mm, Service Limit-24.00mm", "authority_reference": AUTHORITY},
        {"key": "lateral_clearance_middle_axle", "label": "Lateral Clearance - Middle Axle Per Axle",
         "field_type": "numeric_range", "required": False, "unit": "mm", "min_value": 3.60, "max_value": 7.20,
         "decimal_precision": 2, "standard_value": "Min.-3.60mm, Max.-7.20mm, Service Limit-12.00mm",
         "authority_reference": AUTHORITY},
    ]
    add_unit_group_table(add, "clearance", "Position", POSITIONS, activities)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="Clearance_Conv", template_code="112", technology="CONVENTIONAL",
        template_name="Checksheet for Longitudinal & Lateral Clearance (WAP-4)",
        description="Longitudinal & Lateral Clearance checksheet - WAP-4, Conventional - M4-HR section.",
        build_fn=build,
    )
