"""
Module 29.11: seeds the MVRF (Motor Ventilation Rectifier Fan) checksheet template.

Run once: `venv/bin/python scripts/seed_mvrf_template.py`

Explicitly seeded as Conventional technology per the module's instruction, overriding the source
document's own "3 phase AC/01 phase DC" header annotation - this is consistent with the existing
SectionEquipmentMap row for this equipment (technology="Conventional").

Brush/commutator motor family like MCPA (rows 1-9 identical), but: Carbon Brush Size has no
numeric tolerance on this sheet (plain text, "As per data sheet"), Run Test at 85 Volt has no
Amb/Body temperature leaves (only DE/NDE), and adds an impeller-crack check plus a
"Bearing detail" informational row with no defined authority.
"""
from _aux_template_helpers import (
    run_seed, add_pre_test_vibration, add_ir_before_dismantle, add_cleaning_backing_varnishing,
    add_ir_after_assembly, add_final_remarks,
)


def build(add):
    add_pre_test_vibration(add)
    add_ir_before_dismantle(add, standard="Min. 2 M.Ohm", min_value=2.0)
    add_cleaning_backing_varnishing(add, authority=None)
    add(
        "tightness_of_pole", field_label="Tightness of Pole",
        field_type="select", options="Tight, Loose", required=True,
        standard_value="Tight", authority_reference="Shed practice",
        negative_values="Loose",
    )
    add(
        "lead_lug_terminal_check", field_label="Lead, Lug, Terminal Condition",
        field_type="select", options="Normal, Abnormal", required=True,
        standard_value="Normal", authority_reference="Shed practice",
        negative_values="Abnormal",
    )
    add(
        "brush_holder_arm_check", field_label="Brush Holder & Arm Condition",
        field_type="select", options="Normal, Abnormal", required=True,
        standard_value="Normal", authority_reference="Shed practice",
        negative_values="Abnormal",
    )
    add(
        "clean_commutator", field_label="Clean Commutator",
        field_type="select", options="Done, Not done", required=True,
        standard_value="Done", authority_reference="Shed practice",
        negative_values="Not done",
    )
    add(
        "mica_cleaning", field_label="Mica Cleaning",
        field_type="select", options="Done, Not done", required=True,
        standard_value="Done", authority_reference="Shed practice",
        negative_values="Not done",
    )
    add(
        "chamfering", field_label="Chamfering",
        field_type="select", options="Done, Not done", required=True,
        standard_value="Done", authority_reference="Shed practice",
        negative_values="Not done",
    )

    carbon_brush = add(
        "carbon_brush", field_label="Carbon Brush",
        field_type="group", required=False, authority_reference="Shed practice",
    )
    add("carbon_brush_grade", parent=carbon_brush, field_label="Grade", field_type="text", required=True)
    add("carbon_brush_size", parent=carbon_brush, field_label="Size", field_type="text", required=True,
        standard_value="As per data sheet")

    add(
        "free_movement_carbon_brush", field_label="Free Movement of C/B",
        field_type="select", options="Free, Stuck", required=True,
        standard_value="Free", authority_reference="Shed practice",
        negative_values="Stuck",
    )
    add_ir_after_assembly(add)
    add(
        "carbon_brush_bedding", field_label="Carbon Brush Bedding",
        field_type="boolean", required=True,
        standard_value="Done", authority_reference="Shed practice",
        negative_values="false",
    )

    run_test = add(
        "run_test_at_85_volt", field_label="Run Test at 85 Volt",
        field_type="group", required=False, authority_reference="Shed practice",
    )
    add("run_test_sparking_commutator", parent=run_test, field_label="Sparking on Commutator",
        field_type="select", options="No Sparking, Sparking", required=True,
        standard_value="No sparking", negative_values="Sparking")
    temp_group = add("run_test_temp", parent=run_test, field_label="Temperature",
                      field_type="group", required=False, standard_value="Ambient +25 C")
    for leaf_label in ["DE", "NDE"]:
        add(f"run_test_temp_{leaf_label.lower()}", parent=temp_group, field_label=leaf_label,
            field_type="number", required=True, unit="C")

    add(
        "impeller_crackness_check", field_label="To Check Impeller for Crackness",
        field_type="select", options="No Crack, Crack Found", required=True,
        standard_value="No crack", authority_reference="Shed practice",
        negative_values="Crack Found",
    )

    add(
        "bearing_detail", field_label="Bearing Detail",
        field_type="text", required=False,
        standard_value="As per data sheet",
    )

    add("any_other_new_items", field_label="Any Other New Items", field_type="textarea", required=False)
    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="MVRF", template_code="17", technology="CONVENTIONAL",
        template_name="Checksheet for MVRF",
        description="Motor Ventilation Rectifier Fan checksheet.",
        build_fn=build,
    )
