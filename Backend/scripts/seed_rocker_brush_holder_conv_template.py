"""
Module 43: seeds the RB_Conv (Rocker & Brush Holder, Conventional locomotives, M35-TM section)
checksheet template.

Run once: `venv/bin/python scripts/seed_rocker_brush_holder_conv_template.py`

Source: "FR/TM/AC/06 - Overhauling and Assembling of Rocker & Brush Holder" (Locomotive Care
Centre Ratlam, Western Railway), a 15-item overhaul checklist covering brush holder/insulator
condition, insulation resistance, spring tension (6 brush holders x 3 readings each - a genuine
per-position measurement grid, preserved at full granularity), bolt torque, and arc horn gap
(6 positions).

No `maintenance_type` is set on this template (stays NULL) - per Module 43's architecture,
Conventional TM equipment resolves to exactly one active template per equipment, so the
Android app's TM Number/GC-Overhaul selection UI (gated on >1 candidate template) never
triggers, matching the required "Locomotive → Equipment → Checksheet" Conventional workflow
without any Android or backend code changes.
"""
from _aux_template_helpers import add_final_remarks, run_seed

BRUSH_HOLDERS = [f"BH{i}" for i in range(1, 7)]
ARC_HORNS = list(range(1, 7))


def build(add):
    add("brush_holder_shaking_check", field_label="Provide Brush Holder on Each Insulator and Check for Any "
        "Shaking of Insulator", field_type="select", options="Good, Replaced", required=True)
    add("rocker_ring_petrol_clean", field_label="Clean the Rocker Ring With Petrol, Ensure Proper Glaze of "
        "Insulators - if Required Replace Teflon Sleeve", field_type="select", options="Done, Not Done",
        required=True)

    insulation_group = add("insulation_value_check", field_label="Check the Insulation Value of Brush Holders",
        field_type="group", required=False, standard_value="10 Mega Ohms Min With 1000V Insulation Tester")
    add("insulation_value_positive_circuit", parent=insulation_group, field_label="Positive Circuit of Brush "
        "Holders", field_type="numeric_range", required=True, unit="MOhm", min_value=10.0, max_value=1000.0,
        decimal_precision=1)
    add("insulation_value_negative_circuit", parent=insulation_group, field_label="Negative Circuit of Brush "
        "Holders", field_type="numeric_range", required=True, unit="MOhm", min_value=10.0, max_value=1000.0,
        decimal_precision=1)

    brush_holder_condition_group = add("brush_holder_condition_check", field_label="Check the Condition of "
        "Brush Holders for Flash, Bend, Worn/Tight Pockets and Replace/Attend Wherever Required",
        field_type="group", required=False)
    add("brush_holder_condition", parent=brush_holder_condition_group, field_label="Condition", field_type="select",
        options="Good, Details of Attention", required=True)
    add("brush_holder_pocket_width", parent=brush_holder_condition_group, field_label="Pocket Width Wise "
        "Dimension", field_type="numeric_range", required=True, unit="mm", min_value=0.0, max_value=20.3,
        decimal_precision=1, standard_value="Not More Than 20.3mm")

    add("brush_holder_type", field_label="Specify Brush Holder Type", field_type="select",
        options="Modified, Unmodified", required=True)
    add("bh_springs_spacers_condition_check", field_label="Check the Condition of BH Springs, Spacers, Split "
        "Pins and Related Components and Replace if Required", field_type="select",
        options="Good, Details of Attention", required=True)

    spring_tension_group = add("spring_tension_measurement", field_label="Measure, Adjust and Record the "
        "Spring Tension Standard Values (On Brush Holder Test Bench)", field_type="group", required=False,
        standard_value="At 64mm Brush Height: 3.44 Kg±10%; At 25mm Brush Height: 2.82 Kg±10%")
    for bh in BRUSH_HOLDERS:
        bh_group = add(f"spring_tension_{bh.lower()}", parent=spring_tension_group, field_label=bh,
                        field_type="group", required=False)
        for reading in (1, 2, 3):
            add(f"spring_tension_{bh.lower()}_reading_{reading}", parent=bh_group,
                field_label=f"Reading {reading}", field_type="numeric_range", required=True, unit="Kg",
                min_value=2.5, max_value=3.8, decimal_precision=2)

    add("insulator_bh_bolts_torque_check", field_label="Ensure Proper Tightness of Insulator/BH Fixing Bolts "
        "(By Torque Wrench)", field_type="select", options="Done, Not Done", required=True,
        standard_value="Torque Value for M20 Bolts-24.2Kg-m/175.038 Ft-Lbs, for M24 Bolts-42Kg-m/303.786 Ft-Lbs")
    add("brush_holder_insulator_type", field_label="Specify Whether Brush Holder Insulator Is Modified or "
        "Unmodified", field_type="select", options="Modified, Unmodified", required=True)
    add("interconnection_leads_tightness_check", field_label="Check the Condition of Interconnection Leads and "
        "Ensure Tightness of Connection Bolts", field_type="select", options="Done, Not Done", required=True)
    add("support_insulator_threads_check", field_label="Check the Threads of +ve & -ve Support Insulators and "
        "Replace if Worn/Damaged", field_type="select", options="Done, Not Done", required=True)
    add("rocker_ring_threads_mna_bore_check", field_label="Check the Condition of Rocker Ring Fixing Threads, "
        "MNA Setting Bore and Attend", field_type="select", options="Done, Not Done", required=True)
    add("mating_area_finish_check", field_label="Ensure Smooth Finish of Mating Area With Magnet Frame/End "
        "Shield", field_type="select", options="Done, Not Done", required=True)

    arc_horn_group = add("arc_horn_check", field_label="Check the Condition of Arc Horns, Replace if Damaged "
        "and Ensure Standard Gap (by Shed Made Go No Go Gauge)", field_type="group", required=False,
        standard_value="11.5 to 13.5mm")
    for pos in ARC_HORNS:
        add(f"arc_horn_gap_{pos}", parent=arc_horn_group, field_label=f"Position {pos}",
            field_type="numeric_range", required=True, unit="mm", min_value=11.5, max_value=13.5,
            decimal_precision=1)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="RB_Conv", template_code="139", technology="CONVENTIONAL",
        template_name="Checksheet for Rocker & Brush Holder",
        description="Overhauling and Assembling of Rocker & Brush Holder checksheet - Conventional - M35-TM "
                     "section.",
        build_fn=build,
    )
