"""
Module 40: seeds the POHS_P7 (Primary Outer Helical Spring, WAP-7, 3-Phase, M4-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_primary_outer_helical_spring_p7_template.py`

Source: pages 17-18 of the supplied WAP-7 checksheet - "Primary Outer Helical Spring (Middle
Axle)" (CLW Drawing No.-1209-01-115-009 & RDSO Drawing No.-SKVL-268) and "Primary Outer Helical
Spring (End Axle)" (CLW Drawing No.-1209-01-115-008 & RDSO Drawing No.-SKVL-267). Unlike WAG9HC,
where one uniform spec covers all 12 wheels, WAP-7's primary outer spring genuinely has two
different specs depending on wheel position - middle axle (W.No.-3,4,9,10) vs end axle
(W.No.-1,2,5,6,7,8,11,12), each with its own drawing number, free height and spring working load
(working height bands happen to be the same for both). Both are modelled here as one equipment
covering all 12 wheels, each wheel using whichever spec its position actually calls for.
"""
from _m4hr_template_helpers import add_final_remarks, run_seed

MIDDLE_AXLE_WHEELS = {3, 4, 9, 10}
END_AXLE_WHEELS = {1, 2, 5, 6, 7, 8, 11, 12}
ALL_WHEELS = sorted(MIDDLE_AXLE_WHEELS | END_AXLE_WHEELS)

MIDDLE_AXLE_SPEC = {
    "drawing_no": "CLW Drawing No.-1209-01-115-009 & RDSO Drawing No.-SKVL-268",
    "free_height_min": 253.6, "free_height_max": 263.6,
    "working_load": "3190.6 Kg",
}
END_AXLE_SPEC = {
    "drawing_no": "CLW Drawing No.-1209-01-115-008 & RDSO Drawing No.-SKVL-267",
    "free_height_min": 233.5, "free_height_max": 243.8,
    "working_load": "4138.6 Kg",
}


def build(add):
    for w in ALL_WHEELS:
        spec = MIDDLE_AXLE_SPEC if w in MIDDLE_AXLE_WHEELS else END_AXLE_SPEC
        w_group = add(f"pohs_w{w}", field_label=f"Wheel No.-{w}", field_type="group", required=False)
        for side in ("LH", "RH"):
            s_group = add(f"pohs_w{w}_{side.lower()}", parent=w_group, field_label=side, field_type="group",
                          required=False)
            add(f"pohs_w{w}_{side.lower()}_make", parent=s_group, field_label="Primary Outer Helical Spring Make",
                field_type="text", required=True, standard_value="Noted")
            add(f"pohs_w{w}_{side.lower()}_damage_check", parent=s_group, field_label="Examine the Primary Outer "
                "Springs for Signs of Damage/Cracks Etc.", field_type="select",
                options="No Damage/No Cracked, Damage/Cracked Found", required=True,
                standard_value="No damage/No cracked", negative_values="Damage/Cracked Found")
            add(f"pohs_w{w}_{side.lower()}_free_height", parent=s_group, field_label="Free Height",
                field_type="numeric_range", required=True, unit="mm", min_value=spec["free_height_min"],
                max_value=spec["free_height_max"], decimal_precision=1, authority_reference=spec["drawing_no"])
            add(f"pohs_w{w}_{side.lower()}_working_height_band1", parent=s_group,
                field_label="Working Height - Band-1", field_type="numeric_range", required=True, unit="mm",
                min_value=192.0, max_value=194.0, decimal_precision=1)
            add(f"pohs_w{w}_{side.lower()}_working_height_band2", parent=s_group,
                field_label="Working Height - Band-2", field_type="numeric_range", required=True, unit="mm",
                min_value=190.0, max_value=192.0, decimal_precision=1)
            add(f"pohs_w{w}_{side.lower()}_working_load", parent=s_group, field_label="Spring Working Load",
                field_type="number", required=True, unit="Kg", standard_value=spec["working_load"])
            add(f"pohs_w{w}_{side.lower()}_end_tip_bite", parent=s_group,
                field_label="The End Tip Should Not Bite the Effective Coil", field_type="select",
                options="No Bite, Bite", required=True, standard_value="No bite", negative_values="Bite")
            add(f"pohs_w{w}_{side.lower()}_coil_contact", parent=s_group, field_label="None of Coil Shall Be in "
                "Contact With Adjacent Coil at Working Height", field_type="select",
                options="Not Touching, Touching", required=True, standard_value="Not touching",
                negative_values="Touching")
        add(f"pohs_w{w}_same_bend_followed", parent=w_group, field_label="Spring of Same Bend Should Be Used "
            "in Same Bogie", field_type="select", options="Followed, Not Followed", required=True,
            standard_value="Followed", negative_values="Not Followed")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="POHS_P7", template_code="95", technology="3_PHASE",
        template_name="Checksheet for Primary Outer Helical Spring (WAP-7)",
        description="Primary Outer Helical Spring (Middle Axle & End Axle) checksheet - WAP-7, 3-Phase - "
                     "M4-HR section.",
        build_fn=build,
    )
