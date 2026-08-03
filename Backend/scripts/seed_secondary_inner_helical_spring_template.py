"""
Module 40: seeds the SIHS (Secondary Inner Helical Spring, WAG9HC, 3-Phase, M4-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_secondary_inner_helical_spring_template.py`

Source: page 23 of the supplied WAG-9HC checksheet - "Secondary Inner Helical Spring" (Drawing
No.-CLW/1209.01.115.028), 8 schedule activities repeated once per wheel number - only W.No.-3, 4,
9 and 10 carry a secondary spring (unlike the primary springs present at every wheel), each split
by LH/RH.
"""
from _m4hr_template_helpers import add_final_remarks, run_seed

WHEEL_NUMBERS = [3, 4, 9, 10]
DRAWING_NO = "Drawing No.-CLW/1209.01.115.028"


def build(add):
    for w in WHEEL_NUMBERS:
        w_group = add(f"sihs_w{w}", field_label=f"W. No.-{w}", field_type="group", required=False)
        for side in ("LH", "RH"):
            s_group = add(f"sihs_w{w}_{side.lower()}", parent=w_group, field_label=side, field_type="group",
                          required=False)
            add(f"sihs_w{w}_{side.lower()}_make", parent=s_group, field_label="Secondary Inner Helical Spring Make",
                field_type="text", required=True, standard_value="Noted")
            add(f"sihs_w{w}_{side.lower()}_damage_check", parent=s_group, field_label="Examine the Secondary "
                "Inner Springs for Signs of Damage/Cracks Etc.", field_type="select",
                options="No Damage/No Cracked, Damage/Cracked Found", required=True,
                standard_value="No damage/No cracked", negative_values="Damage/Cracked Found")
            add(f"sihs_w{w}_{side.lower()}_free_height", parent=s_group, field_label="Free Height",
                field_type="numeric_range", required=True, unit="mm", min_value=486.0, max_value=498.0,
                decimal_precision=1, authority_reference=DRAWING_NO)
            add(f"sihs_w{w}_{side.lower()}_working_height_band1", parent=s_group,
                field_label="Working Height - Band-1", field_type="numeric_range", required=True, unit="mm",
                min_value=405.0, max_value=408.5, decimal_precision=1)
            add(f"sihs_w{w}_{side.lower()}_working_height_band2", parent=s_group,
                field_label="Working Height - Band-2", field_type="numeric_range", required=True, unit="mm",
                min_value=401.5, max_value=405.0, decimal_precision=1)
            add(f"sihs_w{w}_{side.lower()}_working_load", parent=s_group, field_label="Spring Working Load",
                field_type="number", required=True, unit="Kg", standard_value="1499 Kg")
            add(f"sihs_w{w}_{side.lower()}_end_tip_bite", parent=s_group,
                field_label="The End Tip Should Not Bite the Effective Coil", field_type="select",
                options="No Bite, Bite", required=True, standard_value="No bite", negative_values="Bite")
            add(f"sihs_w{w}_{side.lower()}_coil_contact", parent=s_group, field_label="None of Coil Shall Be in "
                "Contact With Adjacent Coil at Working Height", field_type="select",
                options="Not Touching, Touching", required=True, standard_value="Not touching",
                negative_values="Touching")
        add(f"sihs_w{w}_same_bend_followed", parent=w_group, field_label="Spring of Same Bend Should Be Used "
            "in Same Bogie", field_type="select", options="Followed, Not Followed", required=True,
            standard_value="Followed", negative_values="Not Followed")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="SIHS", template_code="73", technology="3_PHASE",
        template_name="Checksheet for Secondary Inner Helical Spring",
        description="Secondary Inner Helical Spring checksheet - WAG9HC, 3-Phase - M4-HR section.",
        build_fn=build,
    )
