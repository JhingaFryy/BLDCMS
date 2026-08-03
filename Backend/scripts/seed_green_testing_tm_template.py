"""
Module 40: seeds the GTTM (Green Testing of Traction Motor, WAG9HC, 3-Phase, M4-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_green_testing_tm_template.py`

Source: page 29 of the supplied WAG-9HC checksheet - "Green Testing of Traction Motor", one row
per traction motor run (SN 1-6), each recording a Before and an After (1 hour later) temperature
reading across ambient, axle box (PE/CE, each with an outer "C" and bearing "B" point), MSU
(PE/CE), TM (PE/CE) and gear case - matching the sheet's own before/after run-test structure
rather than flattening it to a single reading.
"""
from _m4hr_template_helpers import add_final_remarks, run_seed

TM_RUNS = list(range(1, 7))


def _temperature_reading(add, parent, run, stage):
    prefix = f"gttm_run_{run}_{stage}"
    stage_group = add(prefix, parent=parent, field_label=stage.capitalize(),
                       field_type="group", required=False)
    add(f"{prefix}_time", parent=stage_group, field_label="Time", field_type="text", required=True)
    add(f"{prefix}_amb_temp", parent=stage_group, field_label="Ambient Temperature", field_type="number",
        required=True, unit="C")
    axle_box_group = add(f"{prefix}_axle_box", parent=stage_group, field_label="Axle Box",
                          field_type="group", required=False)
    for side in ("PE", "CE"):
        for point in ("C", "B"):
            add(f"{prefix}_axle_box_{side.lower()}_{point.lower()}", parent=axle_box_group,
                field_label=f"{side} {point}", field_type="number", required=True, unit="C")
    msu_group = add(f"{prefix}_msu", parent=stage_group, field_label="MSU", field_type="group", required=False)
    add(f"{prefix}_msu_pe", parent=msu_group, field_label="PE", field_type="number", required=True, unit="C")
    add(f"{prefix}_msu_ce", parent=msu_group, field_label="CE", field_type="number", required=True, unit="C")
    tm_group = add(f"{prefix}_tm", parent=stage_group, field_label="TM", field_type="group", required=False)
    add(f"{prefix}_tm_pe", parent=tm_group, field_label="PE", field_type="number", required=True, unit="C")
    add(f"{prefix}_tm_ce", parent=tm_group, field_label="CE", field_type="number", required=True, unit="C")
    add(f"{prefix}_gear_case", parent=stage_group, field_label="Gear Case", field_type="number", required=True,
        unit="C")
    return stage_group


def build(add):
    for run in TM_RUNS:
        run_group = add(f"gttm_run_{run}", field_label=f"TM Run {run}", field_type="group", required=False)
        add(f"gttm_run_{run}_date", parent=run_group, field_label="Date", field_type="text", required=True)
        add(f"gttm_run_{run}_tm_number", parent=run_group, field_label="TM Number", field_type="text", required=True)
        _temperature_reading(add, run_group, run, "before")
        _temperature_reading(add, run_group, run, "after")
        add(f"gttm_run_{run}_signature", parent=run_group, field_label="Signature", field_type="text",
            required=False)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="GTTM", template_code="79", technology="3_PHASE",
        template_name="Checksheet for Green Testing of Traction Motor",
        description="Green Testing of Traction Motor checksheet - WAG9HC, 3-Phase - M4-HR section.",
        build_fn=build,
    )
