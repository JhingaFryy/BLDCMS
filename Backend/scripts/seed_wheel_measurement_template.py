"""
Module 40: seeds the WM (Wheel Measurement, WAG9HC, 3-Phase, M4-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_wheel_measurement_template.py`

Source: pages 7-8 of the supplied WAG-9HC checksheet - "Wheel Measurement", 10 schedule activities
repeated once per wheel set (W/Set-1 through W/Set-6); most activities are further split into PE
(Pinion End) and CE (Commutator End) sub-readings. "Check Inside Face Wheel Distance" shows three
stacked readings per wheel set on the source sheet (taken at three points around the wheel to
catch uneven wear/ovality, per standard wheelset measurement practice) - implemented as three
sub-fields rather than one, matching what the sheet actually records.
"""
from _m4hr_template_helpers import add_final_remarks, run_seed

WHEEL_SETS = [1, 2, 3, 4, 5, 6]


def build(add):
    for ws in WHEEL_SETS:
        ws_group = add(f"wm_wset_{ws}", field_label=f"Wheel Set-{ws}", field_type="group", required=False)

        add(f"wm_wset_{ws}_axle_number", parent=ws_group, field_label="Axle Number", field_type="text", required=True)

        hub_group = add(f"wm_wset_{ws}_hub_number", parent=ws_group, field_label="Hub Number",
                         field_type="group", required=False)
        add(f"wm_wset_{ws}_hub_pe", parent=hub_group, field_label="PE", field_type="text", required=True)
        add(f"wm_wset_{ws}_hub_ce", parent=hub_group, field_label="CE", field_type="text", required=True)

        thickness_group = add(f"wm_wset_{ws}_wheel_thickness", parent=ws_group, field_label="Check Wheel Thickness",
                               field_type="group", required=False, standard_value="(134.5-131.5)mm",
                               authority_reference="Drawing No.-1209.01.111.003")
        add(f"wm_wset_{ws}_thickness_pe", parent=thickness_group, field_label="PE", field_type="numeric_range",
            required=True, unit="mm", min_value=131.5, max_value=134.5, decimal_precision=2)
        add(f"wm_wset_{ws}_thickness_ce", parent=thickness_group, field_label="CE", field_type="numeric_range",
            required=True, unit="mm", min_value=131.5, max_value=134.5, decimal_precision=2)

        diameter_group = add(f"wm_wset_{ws}_wheel_diameter", parent=ws_group, field_label="Check Wheel Diameter",
                              field_type="group", required=False,
                              standard_value="New: 1092.0+0.5mm, Condemning Limit: 1016.0mm",
                              authority_reference="Drawing No.-1209.01.111.003")
        add(f"wm_wset_{ws}_diameter_pe", parent=diameter_group, field_label="PE", field_type="numeric_range",
            required=True, unit="mm", min_value=1016.0, max_value=1092.5, decimal_precision=2)
        add(f"wm_wset_{ws}_diameter_ce", parent=diameter_group, field_label="CE", field_type="numeric_range",
            required=True, unit="mm", min_value=1016.0, max_value=1092.5, decimal_precision=2)

        root_wear_group = add(f"wm_wset_{ws}_root_wear", parent=ws_group, field_label="Check Root Wear",
                               field_type="group", required=False, standard_value="6.0mm",
                               authority_reference="MPIB.BD.02.16.01 Rev.-01")
        add(f"wm_wset_{ws}_root_wear_pe", parent=root_wear_group, field_label="PE", field_type="numeric_range",
            required=True, unit="mm", min_value=0.0, max_value=6.0, decimal_precision=1)
        add(f"wm_wset_{ws}_root_wear_ce", parent=root_wear_group, field_label="CE", field_type="numeric_range",
            required=True, unit="mm", min_value=0.0, max_value=6.0, decimal_precision=1)

        flange_wear_group = add(f"wm_wset_{ws}_flange_wear", parent=ws_group, field_label="Check Flange Wear",
                                 field_type="group", required=False, standard_value="3.0mm",
                                 authority_reference="MPIB.BD.02.16.01 Rev.-01")
        add(f"wm_wset_{ws}_flange_wear_pe", parent=flange_wear_group, field_label="PE", field_type="numeric_range",
            required=True, unit="mm", min_value=0.0, max_value=3.0, decimal_precision=1)
        add(f"wm_wset_{ws}_flange_wear_ce", parent=flange_wear_group, field_label="CE", field_type="numeric_range",
            required=True, unit="mm", min_value=0.0, max_value=3.0, decimal_precision=1)

        trade_wear_group = add(f"wm_wset_{ws}_trade_wear", parent=ws_group, field_label="Check Trade Wear",
                                field_type="group", required=False, standard_value="6.5mm",
                                authority_reference="MPIB.BD.02.16.01 Rev.-01")
        add(f"wm_wset_{ws}_trade_wear_pe", parent=trade_wear_group, field_label="PE", field_type="numeric_range",
            required=True, unit="mm", min_value=0.0, max_value=6.5, decimal_precision=1)
        add(f"wm_wset_{ws}_trade_wear_ce", parent=trade_wear_group, field_label="CE", field_type="numeric_range",
            required=True, unit="mm", min_value=0.0, max_value=6.5, decimal_precision=1)

        add(f"wm_wset_{ws}_msu_lateral_play", parent=ws_group, field_label="Check Lateral Play of MSU",
            field_type="numeric_range", required=True, unit="mm", min_value=0.0, max_value=1.0,
            decimal_precision=2, authority_reference="RDSO/TC-142")

        inside_face_group = add(f"wm_wset_{ws}_inside_face_distance", parent=ws_group,
                                 field_label="Check Inside Face Wheel Distance", field_type="group", required=False,
                                 standard_value="(1595.5-1597.5)mm, Service Limit: 1599.0mm",
                                 authority_reference="MPMI.BD.02.16.01, Rev.-1 dtd.-31.12.09")
        for reading in (1, 2, 3):
            add(f"wm_wset_{ws}_inside_face_reading_{reading}", parent=inside_face_group,
                field_label=f"Reading {reading}", field_type="numeric_range", required=True, unit="mm",
                min_value=1595.5, max_value=1599.0, decimal_precision=2)

        add(f"wm_wset_{ws}_k_value", parent=ws_group, field_label='Check "K" Value', field_type="numeric_range",
            required=True, unit="mm", min_value=317.09, max_value=317.17, decimal_precision=2,
            standard_value="Gear Ratio 21:107T, 15 Teeth, SKDL-3848")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="WM", template_code="62", technology="3_PHASE",
        template_name="Checksheet for Wheel Measurement",
        description="Wheel Measurement checksheet - WAG9HC, 3-Phase - M4-HR section.",
        build_fn=build,
    )
