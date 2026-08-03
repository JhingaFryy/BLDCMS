"""
Module 40: seeds the TL_P7 (Traction Link / Push Pull Rod, WAP-7, 3-Phase, M4-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_traction_link_p7_template.py`

Source: page 15 of the supplied WAP-7 checksheet - "Traction Link (Push Pull Rod)", 6 schedule
activities repeated once per traction link (T/Link-1 through T/Link-4) - identical shape and
standard values to the WAG9HC Traction Link sheet.
"""
from _m4hr_template_helpers import add_final_remarks, add_unit_group_table, run_seed

TRACTION_LINKS = list(range(1, 5))


def build(add):
    activities = [
        {"key": "flange_housing_rdpt", "label": "Check Traction Rod Flange and Housing Flange Against Crack by "
         "RDPT (RDSO/SMI-259)", "field_type": "select",
         "options": "Checked, Not Checked", "required": True, "standard_value": "Checked",
         "negative_values": "Not Checked", "authority_reference": "RDSO/SMI-259"},
        {"key": "flange_lock_nuts_bolts", "label": "Ensure Provision of New Flange FS Lock Nuts and Neck Down "
         "Bolts of Traction Bar of Size-M20x65, Property Class-8.8 With 02 Interlock Washer in Each Bolt and "
         "Tightness by Specified Torque-260Nm", "field_type": "select", "options": "Ensured, Not Ensured",
         "required": True, "standard_value": "Ensured", "negative_values": "Not Ensured"},
        {"key": "elastic_ring_condition", "label": "Check the Condition of Elastic Ring and Change. "
         "(Must Change-IOH)", "field_type": "select", "options": "Checked, Not Checked", "required": True,
         "standard_value": "Checked", "negative_values": "Not Checked"},
        {"key": "retaining_plate_bolts_provision", "label": "Ensure Provision of New Inner and Outer Retaining "
         "Plate Bolts-M12x35, Property Class-8.8 With New Locking to Provide", "field_type": "select",
         "options": "Ensured, Not Ensured", "required": True, "standard_value": "Ensured",
         "negative_values": "Not Ensured"},
        {"key": "retaining_plate_bolts_tightness", "label": "Ensure Tightness of Retaining Plate Bolts-M12x35 "
         "and Tightness by Specified Torque-80Nm", "field_type": "select", "options": "Ensured, Not Ensured",
         "required": True, "standard_value": "Ensured", "negative_values": "Not Ensured"},
        {"key": "retaining_plate_elastic_ring_gap", "label": "Ensure Minimum 2.0mm Gap Between Inner Retaining "
         "Plate and Elastic Ring - if No Gap Found Then 2.0mm Shim to Provide. (RDSO/TC-142)",
         "field_type": "select", "options": "Ensured, Not Ensured", "required": True, "standard_value": "Ensured",
         "negative_values": "Not Ensured", "authority_reference": "RDSO/TC-142"},
    ]
    add_unit_group_table(add, "tl", "Traction Link", TRACTION_LINKS, activities)
    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="TL_P7", template_code="92", technology="3_PHASE",
        template_name="Checksheet for Traction Link (WAP-7)",
        description="Traction Link (Push Pull Rod) checksheet - WAP-7, 3-Phase - M4-HR section.",
        build_fn=build,
    )
