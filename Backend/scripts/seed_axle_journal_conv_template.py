"""
Module 40: seeds the Axle-Jrnl_Conv (Axle Journal Measurement, WAP-4, Conventional, M4-HR
section) checksheet template.

Run once: `venv/bin/python scripts/seed_axle_journal_conv_template.py`

Source: page 23 of the supplied WAP-4 checksheet - "Measurement of Axle Journal for WAP-4"
(References: MPMI-98/81 Rev. 01-2004, NEI Drg No 92-4271C & X-105, SMI-216), recorded per wheel
(1-12). Each dimensional check on the source sheet prints two standards side by side - "STD"
(new/standard-size axle) and "STEP" (a reground/undersized axle) - both are kept together as a
single descriptive standard_value string per the module's "consolidate a reference-style dual
standard into one representative field" rule (as already applied to the Axle & Inner Race
templates for WAG9HC/WAP-7), rather than splitting every measurement into two parallel fields.

Many of the Plain I/R, Lipped I/R, Thrower and Interference rows are left blank on the reference
sheet for several wheels (recorded only when that particular part was actually dismantled/
remeasured), so they are modelled as optional - consistent with the same "conditional check" rule
already used for the Axle Box Assembly/Overhauling templates on this WAP-4 sheet set.
"""
from _m4hr_template_helpers import add_final_remarks, run_seed

WHEELS = list(range(1, 13))


def build(add):
    for wheel in WHEELS:
        wheel_group = add(f"wheel_{wheel}", field_label=f"Wheel No. {wheel}", field_type="group", required=False)

        add(f"wheel_{wheel}_make", parent=wheel_group, field_label="Make", field_type="text", required=True,
            standard_value="NBC/FAG")
        add(f"wheel_{wheel}_inner_race_status", parent=wheel_group, field_label="Inner Race", field_type="select",
            options="New, Old", required=True)
        add(f"wheel_{wheel}_lipped_inner_race_status", parent=wheel_group, field_label="Lipped Inner Race",
            field_type="select", options="New, Old", required=True)
        add(f"wheel_{wheel}_thrower_status", parent=wheel_group, field_label="Thrower", field_type="select",
            options="New, Old", required=True)
        add(f"wheel_{wheel}_interference_new_inner_race", parent=wheel_group, field_label="Interference for New "
            "Inner Race", field_type="numeric_range", required=False, unit="mm", min_value=0.06, max_value=0.09,
            decimal_precision=2)

        plain_ir_group = add(f"wheel_{wheel}_plain_ir", parent=wheel_group, field_label="Plain I/R",
                              field_type="group", required=False)
        add(f"wheel_{wheel}_plain_ir_jd", parent=plain_ir_group, field_label="JD", field_type="number",
            required=False, unit="mm", standard_value="STD=150.065-150.090mm, STEP=148.06-148.09mm")
        add(f"wheel_{wheel}_plain_ir_id_bore", parent=plain_ir_group, field_label="ID/Bore", field_type="number",
            required=False, unit="mm", standard_value="STD=149.997-150.022mm, STEP=147.997-148.022mm")
        add(f"wheel_{wheel}_plain_ir_od", parent=plain_ir_group, field_label="OD", field_type="number",
            required=False, unit="mm", standard_value="179.065-179.70mm (NBC), 177.75-177.80mm (FAG)")
        add(f"wheel_{wheel}_plain_ir_after_mounting", parent=plain_ir_group, field_label="After Mounting",
            field_type="number", required=False, unit="mm")

        lipped_ir_group = add(f"wheel_{wheel}_lipped_ir", parent=wheel_group, field_label="Lipped I/R",
                               field_type="group", required=False)
        add(f"wheel_{wheel}_lipped_ir_jd", parent=lipped_ir_group, field_label="JD", field_type="number",
            required=False, unit="mm", standard_value="STD=150.065-150.090mm, STEP=148.06-148.09mm")
        add(f"wheel_{wheel}_lipped_ir_id_bore", parent=lipped_ir_group, field_label="ID/Bore", field_type="number",
            required=False, unit="mm", standard_value="STD=149.997-150.022mm, STEP=147.997-148.022mm")
        add(f"wheel_{wheel}_lipped_ir_od", parent=lipped_ir_group, field_label="OD", field_type="number",
            required=False, unit="mm", standard_value="179.065-179.70mm (NBC), 177.75-177.80mm (FAG)")
        add(f"wheel_{wheel}_lipped_ir_after_mounting", parent=lipped_ir_group, field_label="After Mounting",
            field_type="number", required=False, unit="mm")

        thrower_group = add(f"wheel_{wheel}_thrower", parent=wheel_group, field_label="Thrower",
                             field_type="group", required=False)
        add(f"wheel_{wheel}_thrower_jd", parent=thrower_group, field_label="JD", field_type="number",
            required=False, unit="mm", standard_value="STD=180+0.146 to 0.186mm, STEP=178+0.146 to 0.186mm")
        add(f"wheel_{wheel}_thrower_id", parent=thrower_group, field_label="ID", field_type="number",
            required=False, unit="mm", standard_value="STD=180mm, STEP=178mm")

        add(f"wheel_{wheel}_rc", parent=wheel_group, field_label="RC", field_type="number", required=True,
            unit="mm", standard_value="0.070-0.215mm (FAG), 0.046-0.197mm (NBC)")
        add(f"wheel_{wheel}_dth", parent=wheel_group, field_label="DTH (Distance Between Thrower & Hub)",
            field_type="number", required=True, unit="mm")
        add(f"wheel_{wheel}_dai", parent=wheel_group, field_label="DAI (Distance Between Axle End & Inner Race)",
            field_type="number", required=True, unit="mm")

    add("axle_journal_fitted_by", field_label="Name of Staff", field_type="text", required=False)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="Axle-Jrnl_Conv", template_code="119", technology="CONVENTIONAL",
        template_name="Checksheet for Measurement of Axle Journal (WAP-4)",
        description="Measurement of Axle Journal checksheet - WAP-4, Conventional - M4-HR section.",
        build_fn=build,
    )
