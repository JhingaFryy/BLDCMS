"""
Module 29.11: seeds the MCPA (Motor Compressor Auxiliary / brush-type DC compressor motor)
checksheet template.

Run once: `venv/bin/python scripts/seed_mcpa_template.py`

Completely different equipment family from the bearing/winding motors above - this is a
brush/commutator compressor. No winding resistance/inductance comparison, no bearing dimension
checks (only an informational "Bearing detail" text row), no growler test. Field structure is
reused as-is (rows 1-9) by MVRF (see seed_mvrf_template.py).
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
    add("carbon_brush_size", parent=carbon_brush, field_label="Size", field_type="numeric_range", required=True,
        unit="mm", min_value=25.0, max_value=38.0, decimal_precision=1,
        standard_value="New=38mm, Condemning=25mm")

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
        "run_test_after_assembly", field_label="Run Test",
        field_type="group", required=False, authority_reference="Shed practice",
    )
    add("run_test_no_load_current", parent=run_test, field_label="No Load Current",
        field_type="numeric_range", required=True, unit="A", max_value=3.5, decimal_precision=2,
        standard_value="Max. 3.5 Amp")
    add("run_test_sparking_commutator", parent=run_test, field_label="Sparking on Commutator",
        field_type="select", options="No Sparking, Sparking", required=True,
        standard_value="No sparking", negative_values="Sparking")
    temp_group = add("run_test_temp", parent=run_test, field_label="Temperature",
                      field_type="group", required=False, standard_value="Ambient +25 C")
    for leaf_label in ["DE", "NDE", "Amb"]:
        add(f"run_test_temp_{leaf_label.lower()}", parent=temp_group, field_label=leaf_label,
            field_type="number", required=True, unit="C")

    add(
        "bearing_detail", field_label="Bearing Detail",
        field_type="text", required=False,
        standard_value="DE-6306, NDE-6304",
    )

    must_change = add("must_change_item", field_label="Must Change Item", field_type="group", required=False)
    add(
        "must_change_oil_seal", parent=must_change, field_label="Oil Seal (PL No. 23.51.9095)",
        field_type="select", options="Replaced, Not Replaced", required=True,
        standard_value="AOH item", authority_reference="As per TC-29",
        negative_values="Not Replaced",
    )

    add("any_other_new_items", field_label="Any Other New Items", field_type="textarea", required=False)
    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="MCPA", template_code="16", technology="CONVENTIONAL",
        template_name="Checksheet for MCPA",
        description="Motor Compressor Auxiliary (brush-type DC compressor motor) checksheet.",
        build_fn=build,
    )
