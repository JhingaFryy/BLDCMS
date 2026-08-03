"""
Module 40: seeds the TMA_P7 (Traction Motor Assembly, WAP-7, 3-Phase, M4-HR section) checksheet
template.

Run once: `venv/bin/python scripts/seed_traction_motor_assembly_p7_template.py`

Source: page 11 of the supplied WAP-7 checksheet - "Traction Motor Assembly", 6 schedule
activities repeated once per traction motor (TM No.-1 through No.-6). Two items name a specific
product on this sheet that the WAG9HC sheet leaves generic: "new servosyn gear 460RR oil" (row 4)
and "RTV (Loctite-518)" (row 5) - preserved verbatim rather than genericized, since the module
spec explicitly requires standards to be taken from each locomotive's own supplied sheet.
"""
from _m4hr_template_helpers import add_final_remarks, add_unit_group_table, run_seed

TRACTION_MOTORS = list(range(1, 7))


def build(add):
    activities = [
        {"key": "tm_number", "label": "Traction Motor Number", "field_type": "text", "required": True,
         "standard_value": "Noted"},
        {"key": "back_lash", "label": "Check the Back Lash", "field_type": "numeric_range", "required": True,
         "unit": "mm", "min_value": 0.29, "max_value": 0.49, "decimal_precision": 2,
         "standard_value": "(0.29-0.49)mm, Service Limit: 0.90mm"},
        {"key": "tm_bolt_tightness", "label": "Ensure Tightness of Traction Motor Bolt - M30x140, (Torque-1250Nm)",
         "field_type": "select", "options": "Ensured, Not Ensured", "required": True, "standard_value": "Ensured",
         "negative_values": "Not Ensured"},
        {"key": "gear_case_oil_refill", "label": "Refill 06 Liters New Servosyn Gear 460RR Oil in Each Gear Case "
         "(RDSO/TC-034, Rev.-04)", "field_type": "select", "options": "Filled, Not Filled", "required": True,
         "standard_value": "Filled", "negative_values": "Not Filled", "authority_reference": "RDSO/TC-034, Rev.-04"},
        {"key": "rtv_joints", "label": "Apply RTV (Loctite-518) at All Joints Marching Faces", "field_type": "select",
         "options": "Applied, Not Applied", "required": True, "standard_value": "Applied",
         "negative_values": "Not Applied"},
        {"key": "gear_case_coupling_torque", "label": "Couple the Gear Case With Specified Torque (Hex Head "
         "Screw-16x200mm(10.9): 300Nm, Socket Head Screw-12x160mm(8.8): 205Nm, Socket Head Cap Screw-12x80mm: "
         "80Nm, Hex Head Screw-12x30mm: 80Nm, Hex Head Screw-12x70mm: 80Nm)", "field_type": "select",
         "options": "Ensured, Not Ensured", "required": True, "standard_value": "300Nm/205Nm/80Nm/80Nm/80Nm",
         "negative_values": "Not Ensured"},
    ]
    add_unit_group_table(add, "tma", "Traction Motor", TRACTION_MOTORS, activities)
    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="TMA_P7", template_code="88", technology="3_PHASE",
        template_name="Checksheet for Traction Motor Assembly (WAP-7)",
        description="Traction Motor Assembly checksheet - WAP-7, 3-Phase - M4-HR section.",
        build_fn=build,
    )
