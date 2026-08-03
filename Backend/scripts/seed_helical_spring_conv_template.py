"""
Module 40: seeds the HS_Conv (Helical Spring, WAP-4, Conventional, M4-HR section) checksheet
template.

Run once: `venv/bin/python scripts/seed_helical_spring_conv_template.py`

Source: pages 11-12 of the supplied WAP-4 checksheet - "Check Sheet for Helical Spring", covering
both the Primary Spring and Secondary Spring performas in a single equipment/template (the
reference sheet has no separate equipment for primary vs secondary, unlike the WAG9HC/WAP-7
3-Phase templates which split PIHS/POHS/SIHS/SOHS into four independent equipment - this sheet is
followed as given rather than inventing a split it doesn't show).

Each performa has a summary block (working load, free/working height range, bite/touching/squire-
sitting checks, colour-coded pairing, spring make) plus a per-wheel actual-value table recording
free height and working height for each of the two physical springs per wheel position - preserved
at full per-spring granularity since these are genuine individual measurements, not a reference
lookup grid (per the module's "preserve grouped measurements vs consolidate" rule).

Primary springs are fitted at all 12 wheels; secondary springs are fitted only at wheels
1, 2, 3, 4, 7, 8, 9, 10 (the end axles of each 3-axle bogie) per the reference sheet's actual-value
table, which has no entries for wheels 5, 6, 11, 12.
"""
from _m4hr_template_helpers import add_final_remarks, run_seed

PRIMARY_WHEELS = list(range(1, 13))
SECONDARY_WHEELS = [1, 2, 3, 4, 7, 8, 9, 10]
SPRINGS_PER_WHEEL = (1, 2)


def _summary_block(add, parent, prefix, working_load, free_height_range, working_height_range,
                    pairing_standard, drawing_no):
    add(f"{prefix}_working_load", parent=parent, field_label="Spring Working Load", field_type="number",
        required=True, unit="Kg", standard_value=f"{working_load} Kg")
    add(f"{prefix}_free_height", parent=parent, field_label="Free Height", field_type="numeric_range",
        required=False, unit="mm", min_value=free_height_range[0], max_value=free_height_range[1],
        decimal_precision=1)
    add(f"{prefix}_working_height", parent=parent, field_label="Working Height", field_type="numeric_range",
        required=False, unit="mm", min_value=working_height_range[0], max_value=working_height_range[1],
        decimal_precision=1)
    add(f"{prefix}_end_tip_no_bite", parent=parent, field_label="The End Tip Should Not Bite the Effective Coil",
        field_type="select", options="No Bite, Bite Found", required=True, standard_value="No Bite",
        negative_values="Bite Found")
    add(f"{prefix}_no_coil_touching", parent=parent, field_label="None of Coil Shall Be in Contact With Adjacent "
        "Coil at Working Height", field_type="select", options="No Touching, Touching Found", required=True,
        standard_value="No Touching", negative_values="Touching Found")
    add(f"{prefix}_squire_sitting", parent=parent, field_label="Squire Sitting Min (3/4 As per Specification)",
        field_type="select", options="OK, Not OK", required=False, standard_value="OK",
        authority_reference="WD.010HLS-94 Rev.-1, May-95")
    add(f"{prefix}_pairing_color_coding", parent=parent, field_label=f"Pairing & Color Coding of Spring at "
        f"Compressed Height Measured at {working_load} Kg Load", field_type="select", options="Yellow, White",
        required=True, standard_value=pairing_standard, authority_reference=f"Drg. No.-{drawing_no}")
    add(f"{prefix}_spring_make", parent=parent, field_label="Spring Make", field_type="text", required=True,
        standard_value="Noted")


def _per_wheel_table(add, parent, prefix, wheels):
    for wheel in wheels:
        wheel_group = add(f"{prefix}_wheel_{wheel}", parent=parent, field_label=f"Wheel {wheel}",
                           field_type="group", required=False)
        for spring in SPRINGS_PER_WHEEL:
            spring_group = add(f"{prefix}_wheel_{wheel}_spring_{spring}", parent=wheel_group,
                                field_label=f"{wheel}/{spring}", field_type="group", required=False)
            add(f"{prefix}_wheel_{wheel}_spring_{spring}_free_height", parent=spring_group,
                field_label="Free Height", field_type="text", required=True, unit="mm")
            add(f"{prefix}_wheel_{wheel}_spring_{spring}_working_height", parent=spring_group,
                field_label="Working Height", field_type="number", required=True, unit="mm")


def build(add):
    primary_group = add("primary_spring", field_label="Primary Spring (WAP4)", field_type="group", required=False)
    _summary_block(add, primary_group, "primary_spring", 3695, (379, 391), (316, 323),
                    "(323-320)mm-Yellow, (319.5-316)mm-White", "3472 Alt-6")
    _per_wheel_table(add, primary_group, "primary_spring", PRIMARY_WHEELS)

    secondary_group = add("secondary_spring", field_label="Secondary Spring (WAP4)", field_type="group",
                           required=False)
    _summary_block(add, secondary_group, "secondary_spring", 4110, (471, 485), (394, 403),
                    "(403-399)mm-Yellow, (398.5-394)mm-White", "3473 Alt-7")
    _per_wheel_table(add, secondary_group, "secondary_spring", SECONDARY_WHEELS)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="HS_Conv", template_code="109", technology="CONVENTIONAL",
        template_name="Checksheet for Helical Spring (WAP-4)",
        description="Primary Spring & Secondary Spring checksheet - WAP-4, Conventional - M4-HR section.",
        build_fn=build,
    )
