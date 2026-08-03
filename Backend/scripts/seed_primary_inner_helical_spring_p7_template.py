"""
Module 40: seeds the PIHS_P7 (Primary Inner Helical Spring, WAP-7, 3-Phase, M4-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_primary_inner_helical_spring_p7_template.py`

Source: page 17 of the supplied WAP-7 checksheet - "Primary Inner Helical Spring (Middle Axle)"
(CLW Drawing No.-1209-01-115-009 & RDSO Drawing No.-SKVL-268). Structurally different from
WAG9HC's Primary Inner Helical Spring: on WAP-7, a primary INNER spring only exists at the middle
axle positions (W.No.-3, 4, 9, 10) - there is no primary inner spring at the end-axle positions at
all (only a primary OUTER spring exists there - see seed_primary_outer_helical_spring_p7_template.py).
8 schedule activities per wheel number, split by LH/RH.
"""
from _m4hr_template_helpers import add_final_remarks, run_seed

MIDDLE_AXLE_WHEELS = [3, 4, 9, 10]
DRAWING_NO = "CLW Drawing No.-1209-01-115-009 & RDSO Drawing No.-SKVL-268"


def build(add):
    for w in MIDDLE_AXLE_WHEELS:
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
                field_type="numeric_range", required=True, unit="mm", min_value=247.40, max_value=257.40,
                decimal_precision=2, authority_reference=DRAWING_NO)
            add(f"pihs_w{w}_{side.lower()}_working_height_band1", parent=s_group,
                field_label="Working Height - Band-1", field_type="numeric_range", required=True, unit="mm",
                min_value=188.0, max_value=190.0, decimal_precision=1)
            add(f"pihs_w{w}_{side.lower()}_working_height_band2", parent=s_group,
                field_label="Working Height - Band-2", field_type="numeric_range", required=True, unit="mm",
                min_value=186.0, max_value=188.0, decimal_precision=1)
            add(f"pihs_w{w}_{side.lower()}_working_load", parent=s_group, field_label="Spring Working Load",
                field_type="number", required=True, unit="Kg", standard_value="948 Kg")
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
        equipment_code="PIHS_P7", template_code="94", technology="3_PHASE",
        template_name="Checksheet for Primary Inner Helical Spring (WAP-7)",
        description="Primary Inner Helical Spring (Middle Axle) checksheet - WAP-7, 3-Phase - M4-HR section.",
        build_fn=build,
    )
