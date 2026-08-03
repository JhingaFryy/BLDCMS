"""
Module 40: seeds the PIHS (Primary Inner Helical Spring, WAG9HC, 3-Phase, M4-HR section) checksheet
template.

Run once: `venv/bin/python scripts/seed_primary_inner_helical_spring_template.py`

Source: pages 19-20 of the supplied WAG-9HC checksheet - "Primary Inner Helical Spring (BF-1)" /
"(BF-2)" (Drawing No.-CLW/1209.01.215.027), 8 schedule activities repeated once per wheel number
(Wheel No.-1 through No.-12 - No.-1 to 6 on Bogie Frame-1, No.-7 to 12 on Bogie Frame-2) and once
more per spring side (LH/RH). "Spring of same bend should be used in same bogie" is a general
practice confirmation on the sheet, not a per-side measurement, so it is kept at the wheel level
rather than duplicated under LH and RH.
"""
from _m4hr_template_helpers import add_final_remarks, run_seed

WHEEL_NUMBERS = list(range(1, 13))
DRAWING_NO = "Drawing No.-CLW/1209.01.215.027"


def build(add):
    for w in WHEEL_NUMBERS:
        w_group = add(f"pihs_w{w}", field_label=f"Wheel No.-{w}", field_type="group", required=False)
        for side in ("LH", "RH"):
            s_group = add(f"pihs_w{w}_{side.lower()}", parent=w_group, field_label=side, field_type="group",
                          required=False)
            add(f"pihs_w{w}_{side.lower()}_make", parent=s_group, field_label="Primary Inner Helical Spring Make",
                field_type="text", required=True, standard_value="Noted")
            add(f"pihs_w{w}_{side.lower()}_damage_check", parent=s_group, field_label="Examine the Primary Inner "
                "Springs for Signs of Damage/Cracks Etc.", field_type="select",
                options="No Damage/No Cracked, Damage/Cracked Found", required=True,
                standard_value="No damage/No cracked", negative_values="Damage/Cracked Found")
            add(f"pihs_w{w}_{side.lower()}_free_height", parent=s_group, field_label="Free Height",
                field_type="numeric_range", required=True, unit="mm", min_value=237.8, max_value=245.2,
                decimal_precision=1, authority_reference=DRAWING_NO)
            add(f"pihs_w{w}_{side.lower()}_working_height_band1", parent=s_group,
                field_label="Working Height - Band-1", field_type="numeric_range", required=True, unit="mm",
                min_value=188.0, max_value=190.0, decimal_precision=1)
            add(f"pihs_w{w}_{side.lower()}_working_height_band2", parent=s_group,
                field_label="Working Height - Band-2", field_type="numeric_range", required=True, unit="mm",
                min_value=186.0, max_value=188.0, decimal_precision=1)
            add(f"pihs_w{w}_{side.lower()}_working_load", parent=s_group, field_label="Spring Working Load",
                field_type="number", required=True, unit="Kg", standard_value="500 Kg")
            add(f"pihs_w{w}_{side.lower()}_end_tip_bite", parent=s_group,
                field_label="The End Tip Should Not Bite the Effective Coil", field_type="select",
                options="No Bite, Bite", required=True, standard_value="No bite", negative_values="Bite")
            add(f"pihs_w{w}_{side.lower()}_coil_contact", parent=s_group, field_label="None of Coil Shall Be in "
                "Contact With Adjacent Coil at Working Height", field_type="select",
                options="Not Touching, Touching", required=True, standard_value="Not touching",
                negative_values="Touching")
        add(f"pihs_w{w}_same_bend_followed", parent=w_group, field_label="Spring of Same Bend Should Be Used "
            "in Same Bogie", field_type="select", options="Followed, Not Followed", required=True,
            standard_value="Followed", negative_values="Not Followed")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="PIHS", template_code="71", technology="3_PHASE",
        template_name="Checksheet for Primary Inner Helical Spring",
        description="Primary Inner Helical Spring checksheet - WAG9HC, 3-Phase - M4-HR section.",
        build_fn=build,
    )
