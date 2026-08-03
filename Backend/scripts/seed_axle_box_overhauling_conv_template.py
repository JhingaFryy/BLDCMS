"""
Module 40: seeds the AB_Conv (Axle Box Overhauling, WAP-4, Conventional, M4-HR section) checksheet
template.

Run once: `venv/bin/python scripts/seed_axle_box_overhauling_conv_template.py`

Source: pages 7-8 of the supplied WAP-4 checksheet - "Check Sheet for AOH/IOH Axle Box
Overhauling of WAP-4 Loco (as per NEI Drg. No. X-122)", recorded once per axle box (A/Box-1
through A/Box-12 - two axle boxes per wheel set, six wheel sets). Bore depth/diameter are recorded
only when the bearing is actually removed (the reference sheet leaves them blank with a "Bearing
not Removed" note otherwise), so both are modelled as optional; the remaining dimensional/condition
checks are always recorded.

Distinct from AB-Ass_Conv (Assembly of Axle Box, pages 5-6) - that sheet covers the PE/CE
mounting procedure (grease, bearing, rollers, torque); this one covers the axle box housing's own
overhaul dimensions and is a completely separate real-world checksheet in the source document.
"""
from _m4hr_template_helpers import add_final_remarks, add_unit_group_table, run_seed

AXLE_BOXES = list(range(1, 13))


def build(add):
    activities = [
        {"key": "bore_depth", "label": "Bore Depth", "field_type": "number", "required": False, "unit": "mm",
         "standard_value": "286+0.5mm"},
        {"key": "bore_diameter", "label": "Bore Diameter", "field_type": "number", "required": False, "unit": "mm",
         "standard_value": "270+0.052mm"},
        {"key": "face_to_face_size", "label": "Axle Box Face to Face Size With Liners", "field_type": "number",
         "required": True, "unit": "mm", "standard_value": "338+0/-0.75mm", "authority_reference": "NEI Drg. No. X-122"},
        {"key": "lateral_size", "label": "Axle Box Lateral Size With Liners", "field_type": "number",
         "required": True, "unit": "mm", "standard_value": "194+0.76/-0.00mm", "authority_reference": "NEI Drg. No. X-122"},
        {"key": "roller_bearing_check", "label": "Clean and Check the Condition of Roller Bearing if Required "
         "to Be Replaced (As per SMI No.-0216)", "field_type": "select", "required": True,
         "options": "Checked, Not Checked", "standard_value": "Checked", "negative_values": "Not Checked"},
        {"key": "distance_piece_grease_nipple", "label": "Clean and Check the Condition of Outer & Inner "
         "Distance Piece and Grease Nipple if Required to Be Replaced (As per SMI No.-0216)", "field_type": "select",
         "required": True, "options": "Clean, Replaced", "standard_value": "Clean/Replaced"},
        {"key": "spare_parts_clean", "label": "Clean and Check the Condition of All Spare Parts of Axle Box if "
         "Required to Be Replaced (As per SMI No.-0216)", "field_type": "select", "required": True,
         "options": "Clean, Not Clean", "standard_value": "Clean", "negative_values": "Not Clean"},
        {"key": "felt_seal_replace", "label": "Replace the Felt Seal of Outer Distance Piece With Grease Treated "
         "Felt Before Fitment - After Fitment It Should Be 1.5mm Above the Surface (As per SMI No.-0216)",
         "field_type": "select", "required": True, "options": "Replaced, Not Replaced",
         "standard_value": "Replaced, 1.5mm Above Surface After Fitment", "negative_values": "Not Replaced"},
    ]
    add_unit_group_table(add, "axle_box", "A/Box", AXLE_BOXES, activities)

    add("axle_box_fitted_by", field_label="Axle Box Fitted By", field_type="text", required=False)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="AB_Conv", template_code="107", technology="CONVENTIONAL",
        template_name="Checksheet for AOH/IOH Axle Box Overhauling (WAP-4)",
        description="Axle Box Overhauling checksheet - WAP-4, Conventional - M4-HR section.",
        build_fn=build,
    )
