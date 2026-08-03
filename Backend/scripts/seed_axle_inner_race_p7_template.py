"""
Module 40: seeds the Axle & IR_P7 (Axle & Inner Race, WAP-7, 3-Phase, M4-HR section) checksheet
template.

Run once: `venv/bin/python scripts/seed_axle_inner_race_p7_template.py`

Source: pages 7-8 of the supplied WAP-7 checksheet - "Axle & Inner Race" (RDSO/SMI-246), identical
shape and standard values to the WAG9HC Axle & Inner Race sheet - implemented as its own
independent template since Axle & IR_P7 is a separate equipment record.
"""
from _m4hr_template_helpers import add_final_remarks, run_seed

AXLES = [1, 2, 3, 4, 5, 6]


def _de_nde_select(add, parent, key, label, options, standard, negative=None, authority=None):
    group = add(key, parent=parent, field_label=label, field_type="group", required=False,
                standard_value=standard, authority_reference=authority)
    for side in ("DE", "NDE"):
        add(f"{key}_{side.lower()}", parent=group, field_label=side, field_type="select",
            options=options, required=True, negative_values=negative)
    return group


def build(add):
    for axle in AXLES:
        axle_group = add(f"axle_ir_{axle}", field_label=f"Axle No.-{axle}", field_type="group", required=False)

        _de_nde_select(add, axle_group, "ultrasonic_test", "Ultrasonic Test of Axle",
                        "Checked, Not Checked", "Checked", "Not Checked", "RDSO/TC-147")
        _de_nde_select(add, axle_group, "inner_race_make", "Inner Race (Make: NBC/FAG/SKF)",
                        "NBC, FAG, SKF", "Noted")
        _de_nde_select(add, axle_group, "abutment_condition", "Check the Condition of Inner Race and Abutment Ring",
                        "Checked, Not Checked", "Checked", "Not Checked")
        _de_nde_select(add, axle_group, "abutment_replace_defects",
                        "Replace the Inner Race & Abutment Ring if Any Defects", "New, Old", "New/Old")

        seat_dia_group = add("abutment_ring_seat_dia", parent=axle_group, field_label="Abutment Ring Seat Diameter",
                              field_type="group", required=False,
                              standard_value="STD: (170.146-169.814)mm, STEP: (170.106-169.957)mm")
        for side in ("DE", "NDE"):
            add(f"abutment_ring_seat_dia_{side.lower()}", parent=seat_dia_group, field_label=side,
                field_type="numeric_range", required=True, unit="mm", min_value=169.814, max_value=170.146,
                decimal_precision=3)

        _de_nde_select(add, axle_group, "abutment_ring_inner_dia", "Abutment Ring Inner Diameter",
                        "Checked, Not Removed", "Checked")
        _de_nde_select(add, axle_group, "waviness_check",
                        "Waviness of Surface by Blue Marking by Metal Ruler (Length Should Be 2/3rd of "
                        "Journal Length) Journal Length=180mm", "Checked, Not Removed", "Checked")

        add("axle_journal_diameter", parent=axle_group, field_label="Axle Journal Diameter",
            field_type="numeric_range", required=True, unit="mm", min_value=150.043, max_value=150.068,
            decimal_precision=3, standard_value="STD: (150.068-150.043)mm, STEP: (148.068-148.043)mm")
        add("inner_race_bore_diameter", parent=axle_group, field_label="Inner Race Bore Diameter",
            field_type="numeric_range", required=True, unit="mm", min_value=149.975, max_value=150.00,
            decimal_precision=3, standard_value="STD: (150.00-149.975)mm, STEP: (148.00-147.975)mm")
        add("inner_race_interference", parent=axle_group, field_label="Inner Race Interference",
            field_type="numeric_range", required=True, unit="mm", min_value=0.043, max_value=0.093,
            decimal_precision=3)
        add("loose_lip_bore_diameter", parent=axle_group, field_label="Loose Lip Bore Diameter",
            field_type="numeric_range", required=True, unit="mm", min_value=150.035, max_value=150.075,
            decimal_precision=3,
            standard_value="SKF-150.075-150.035mm, NEI-150.125-150.085mm, FAG-150.100-150.060mm")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="Axle & IR_P7", template_code="86", technology="3_PHASE",
        template_name="Checksheet for Axle & Inner Race (WAP-7)",
        description="Axle & Inner Race checksheet - WAP-7, 3-Phase - M4-HR section.",
        build_fn=build,
    )
