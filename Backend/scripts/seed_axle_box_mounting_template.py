"""
Module 40: seeds the Axle BM (Axle Box Mounting, WAG9HC, 3-Phase, M4-HR section) checksheet
template.

Run once: `venv/bin/python scripts/seed_axle_box_mounting_template.py`

Source: pages 11-12 of the supplied WAG-9HC checksheet - "Axle Box Mounting" (RDSO/SMI-246), 13
schedule activities repeated once per axle box (A/B-1 through A/B-12).
"""
from _m4hr_template_helpers import add_final_remarks, add_unit_group_table, run_seed

AXLE_BOXES = list(range(1, 13))
AUTHORITY = "RDSO/SMI-246"


def build(add):
    activities = [
        {"key": "grease_removed_cleaned", "label": "Clean the Roller Bearing, Axle Box and Remove the Old Grease",
         "field_type": "select", "options": "Cleaned, Not Cleaned", "required": True, "standard_value": "Cleaned",
         "negative_values": "Not Cleaned", "authority_reference": AUTHORITY},
        {"key": "bearing_condition_check", "label": "Check the Condition of Roller Bearings and Replace",
         "field_type": "select", "options": "Checked, Replaced", "required": True, "standard_value": "Checked",
         "authority_reference": AUTHORITY},
        {"key": "bearing_make", "label": "Check Make of the Roller Bearings", "field_type": "select",
         "options": "NBC, FAG, SKF", "required": True, "standard_value": "NBC/FAG/SKF",
         "authority_reference": AUTHORITY},
        {"key": "rear_cover_o_ring", "label": 'Replace "O" Ring of Rear Cover', "field_type": "select",
         "options": "Replaced, Not Replaced", "required": True, "standard_value": "Replaced",
         "negative_values": "Not Replaced", "authority_reference": AUTHORITY},
        {"key": "housing_bore_diameter", "label": "Axle Box Housing Bore Diameter", "field_type": "numeric_range",
         "required": True, "unit": "mm", "min_value": 250.000, "max_value": 250.046, "decimal_precision": 3,
         "authority_reference": AUTHORITY},
        {"key": "radial_clearance", "label": "Radial Clearance of Bearing", "field_type": "numeric_range",
         "required": True, "unit": "mm", "min_value": 0.165, "max_value": 0.215, "decimal_precision": 3,
         "authority_reference": AUTHORITY},
        {"key": "rear_cover_bolts_tightness", "label": "Ensure Tightness of Rear Cover Bolts (M16x45) by "
         "Specified Torque and Locking of Bolts to Be Done (Torque-100Nm)", "field_type": "select",
         "options": "Ensured, Not Ensured", "required": True, "standard_value": "Ensured",
         "negative_values": "Not Ensured", "authority_reference": AUTHORITY},
        {"key": "grease_fill", "label": "Fill the Axle Box Roller Bearing With New Grease. (Gadus Grease as Per "
         "Make: NBC-650gm, FAG-430gm, SKF-470gm)", "field_type": "select", "options": "Filled, Not Filled",
         "required": True, "standard_value": "Filled", "negative_values": "Not Filled",
         "authority_reference": AUTHORITY},
        {"key": "front_cover_o_ring", "label": 'Replace "O" Ring of Front Cover', "field_type": "select",
         "options": "Replaced, Not Replaced", "required": True, "standard_value": "Replaced",
         "negative_values": "Not Replaced", "authority_reference": AUTHORITY},
        {"key": "end_plate_screw_tightness", "label": "Ensure Tightness of the End Plate (Clamping Plate) Socket "
         "Head Caps Screw (M20x50) With Specified Torque-330Nm", "field_type": "select",
         "options": "Ensured, Not Ensured", "required": True, "standard_value": "Ensured",
         "negative_values": "Not Ensured", "authority_reference": AUTHORITY},
        {"key": "front_cover_gasket", "label": "Replace Front Cover Gasket", "field_type": "select",
         "options": "Replaced, Not Replaced", "required": True, "standard_value": "Replaced",
         "negative_values": "Not Replaced", "authority_reference": AUTHORITY},
        {"key": "front_cover_bolts_tightness", "label": "Ensure Tightness of Front Cover Bolts (M16x45) by "
         "Specified Torque-100Nm", "field_type": "select", "options": "Ensured, Not Ensured", "required": True,
         "standard_value": "Ensured", "negative_values": "Not Ensured", "authority_reference": AUTHORITY},
        {"key": "axial_clearance", "label": "Axial Clearance", "field_type": "numeric_range", "required": True,
         "unit": "mm", "min_value": 0.400, "max_value": 0.700, "decimal_precision": 3,
         "standard_value": "SKF & NEI: (0.400-0.700)mm, FAG: (0.200-0.400)mm", "authority_reference": AUTHORITY},
    ]
    add_unit_group_table(add, "axle_bm", "Axle Box", AXLE_BOXES, activities)
    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="Axle BM", template_code="64", technology="3_PHASE",
        template_name="Checksheet for Axle Box Mounting",
        description="Axle Box Mounting checksheet - WAG9HC, 3-Phase - M4-HR section.",
        build_fn=build,
    )
