"""
Module 40: seeds the PS (Piston Stroke, WAG9HC, 3-Phase, M4-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_piston_stroke_template.py`

Source: page 28 of the supplied WAG-9HC checksheet - two sub-tables: "Piston Stroke" (repeated
once per wheel-pair group: 1-3, 2-4, 3-5, 4-6, 7-9, 8-10, 9-11, 10-12) and "Centre Buffer Coupler,
Side Buffer and Rail Guard Height" (repeated once per cab, Cab-1/Cab-2).
"""
from _m4hr_template_helpers import add_final_remarks, add_unit_group_table, run_seed

WHEEL_PAIR_GROUPS = ["1-3", "2-4", "3-5", "4-6", "7-9", "8-10", "9-11", "10-12"]


def build(add):
    piston_activities = [
        {"key": "piston_stroke", "label": "Piston Stroke", "field_type": "numeric_range", "required": True,
         "unit": "mm", "min_value": 107.0, "max_value": 117.0, "decimal_precision": 0,
         "standard_value": "WAG-9: 107 to 117mm", "authority_reference": "RDSO/SMI-197"},
        {"key": "brake_block_wheel_gap", "label": "Gap Between Brake Block & Wheel", "field_type": "number",
         "required": True, "unit": "mm", "standard_value": "Noted"},
    ]
    add_unit_group_table(add, "piston_stroke", "Wheel Number", WHEEL_PAIR_GROUPS, piston_activities)

    for cab in ("CAB-1", "CAB-2"):
        cab_key = cab.lower().replace("-", "_")
        cab_group = add(f"height_{cab_key}", field_label=cab, field_type="group", required=False)

        buffer_group = add(f"height_{cab_key}_buffer", parent=cab_group, field_label="Buffer Height",
                            field_type="group", required=False,
                            standard_value="(1105.0-1035.0)mm (As per G-76 manual)")
        add(f"height_{cab_key}_buffer_loco_pilot", parent=buffer_group, field_label="Loco Pilot Side",
            field_type="numeric_range", required=True, unit="mm", min_value=1035.0, max_value=1105.0,
            decimal_precision=0)
        add(f"height_{cab_key}_buffer_asst_loco_pilot", parent=buffer_group, field_label="Asst. Loco Pilot Side",
            field_type="numeric_range", required=True, unit="mm", min_value=1035.0, max_value=1105.0,
            decimal_precision=0)

        add(f"height_{cab_key}_cbc", parent=cab_group, field_label="CBC Height", field_type="numeric_range",
            required=True, unit="mm", min_value=1035.0, max_value=1105.0, decimal_precision=0,
            standard_value="(1105.0-1035.0)mm (As per G-76 manual)")

        rail_guard_group = add(f"height_{cab_key}_rail_guard", parent=cab_group, field_label="Rail Guard Height",
                                field_type="group", required=False,
                                standard_value="(115.0-118.0)mm (As per EL/TRO/TRS-59 (99) dated 26.11.99)")
        add(f"height_{cab_key}_rail_guard_loco_pilot", parent=rail_guard_group, field_label="Loco Pilot Side",
            field_type="numeric_range", required=True, unit="mm", min_value=115.0, max_value=118.0,
            decimal_precision=0)
        add(f"height_{cab_key}_rail_guard_asst_loco_pilot", parent=rail_guard_group,
            field_label="Asst. Loco Pilot Side", field_type="numeric_range", required=True, unit="mm",
            min_value=115.0, max_value=118.0, decimal_precision=0)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="PS", template_code="78", technology="3_PHASE",
        template_name="Checksheet for Piston Stroke",
        description="Piston Stroke, Centre Buffer Coupler/Side Buffer/Rail Guard Height checksheet - "
                     "WAG9HC, 3-Phase - M4-HR section.",
        build_fn=build,
    )
