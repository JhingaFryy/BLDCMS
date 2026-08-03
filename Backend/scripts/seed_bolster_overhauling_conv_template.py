"""
Module 40: seeds the Bol-1_Conv / Bol-2_Conv (Bolster Overhauling, WAP-4, Conventional, M4-HR
section) checksheet templates.

Run once: `venv/bin/python scripts/seed_bolster_overhauling_conv_template.py`

Source: pages 2 & 4 of the supplied WAP-4 checksheet - "Check Sheet for Bolster Overhauling"
(pre-assembly), one per bolster (Bolster No. 1 / Bolster No. 2). Both bolsters share an identical
6-measurement centre-pivot table; only the bolster number differs. Genuinely different sheet from
the 3-Phase templates - WAG9HC/WAP-7 have no standalone Bolster Overhauling equipment at all
(the WAP-4/Conventional bogie design uses a separate bolster with its own centre pivot, unlike the
3-Phase Flexicoil bogies).
"""
from _m4hr_template_helpers import add_final_remarks, run_seed


def build(add):
    add("bolster_number", field_label="Bolster Number", field_type="text", required=True, standard_value="Noted")
    add("make", field_label="Make", field_type="text", required=False, standard_value="Noted")
    add("mfg_year", field_label="MFG Year", field_type="text", required=False, standard_value="Noted")
    add("points", field_label="Points", field_type="text", required=False)

    crack_group = add("crack_inspection", field_label="Crack Inspection", field_type="group", required=False)
    add("bolster_cleaned", parent=crack_group, field_label="Cleaning the Bolster in Washing Tank",
        field_type="select", options="Cleaned, Not Cleaned", required=True, standard_value="Cleaned",
        negative_values="Not Cleaned")
    add("crack_rdpt_mpt_check", parent=crack_group, field_label="Check Crackness at Bottom and Top Portion by "
        "RDPT Method or MPT", field_type="select", options="Checked, Crack Found", required=True,
        standard_value="Checked", negative_values="Crack Found")
    add("crack_length_recorded", parent=crack_group, field_label="Record the Length of Crack in Various Zones",
        field_type="select", options="Recorded, Not Applicable", required=False, standard_value="Recorded")

    add("centre_pivot_without_liner", field_label="Bolster Centre Pivot Without Liner", field_type="numeric_range",
        required=True, unit="mm", min_value=476.69, max_value=477.95, decimal_precision=2)
    add("depth_centre_pivot_without_liner", field_label="Depth of Bolster Centre Pivot Without Liner",
        field_type="number", required=True, unit="mm", standard_value="76.0mm")
    add("centre_pivot_bowl_inner_dia_with_liner", field_label="Centre Pivot Bowl Inner Dia With Liner",
        field_type="numeric_range", required=True, unit="mm", min_value=457.95, max_value=457.98,
        decimal_precision=2)
    add("centre_pivot_bowl_inner_dia_without_liner", field_label="Centre Pivot Bowl Inner Dia Without Liner",
        field_type="numeric_range", required=True, unit="mm", min_value=477.69, max_value=477.95,
        decimal_precision=2)
    add("superstructure_centre_pivot_pin_dia", field_label="Super Structure Centre Pivot Pin Dia",
        field_type="numeric_range", required=True, unit="mm", min_value=456.00, max_value=457.00,
        decimal_precision=2)
    add("height_centre_pivot_pin", field_label="Height of Centre Pivot Pin", field_type="number", required=True,
        unit="mm", standard_value="144.0mm")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="Bol-1_Conv", template_code="104", technology="CONVENTIONAL",
        template_name="Checksheet for Bolster-1 Overhauling (WAP-4)",
        description="Bolster Overhauling checksheet - WAP-4, Conventional - M4-HR section.",
        build_fn=build,
    )
    run_seed(
        equipment_code="Bol-2_Conv", template_code="105", technology="CONVENTIONAL",
        template_name="Checksheet for Bolster-2 Overhauling (WAP-4)",
        description="Bolster Overhauling checksheet - WAP-4, Conventional - M4-HR section.",
        build_fn=build,
    )
