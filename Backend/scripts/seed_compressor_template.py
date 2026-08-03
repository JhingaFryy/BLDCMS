"""
Module 42: seeds the CP / CP_Conv (Compressor, 3-Phase and Conventional locomotives, M35-CP
section) checksheet templates.

Run once: `venv/bin/python scripts/seed_compressor_template.py`

Source: "TOH & IOH CP.pdf" - "Overhauling and Testing Performa of ELGI Compressor Type RR20100
CG(M)" (Revised Date-01/01/2026), a dimensional overhaul-and-test performa: tank
capacity/time-taken/current tests (each with Pre-Testing and Final-Testing readings), a 16-row
LP/HP dimensional table (cylinder inner diameter, piston, ring clearances, bearing seating,
bearing/mount details), and a 6-location vibration measurement table.

Where the source prints two standards side by side ("New(mm)" - the tolerance for a freshly
overhauled part - and "Max(mm)" - the wear/service limit), both are kept in a single field's
standard_value text; the numeric_range itself uses the "New" tolerance since that is what a
correctly-overhauled reading must fall within, per the same "consolidate a reference-style dual
standard into one representative field" rule already applied to the Axle Journal/Axle & Inner Race
templates. Each LP/HP row records two distinct readings (the compressor's two heads per stage), so
both are preserved as separate fields per the module's "preserve grouped measurements" rule.

Per the module's explicit instruction, the checksheet format is IDENTICAL for Conventional and
3-Phase locomotives - a single shared `build()` function is used for both CP and CP_Conv, with only
the equipment_code/template_code/technology differing per `run_seed()` call. Per the "Do NOT
create fields for Loco Number/Technician/Supervisor Name/Signature" rule, the sheet's own "Loco",
"Name of Tech"/"Signature of Supervisor" lines are intentionally not modelled.
"""
from _aux_template_helpers import add_final_remarks, run_seed


def _add_lp_hp_row(add, parent, key, label, lp_std, hp_std, lp_range=None, hp_range=None):
    row_group = add(key, parent=parent, field_label=label, field_type="group", required=False)
    for stage, std, rng in (("lp", lp_std, lp_range), ("hp", hp_std, hp_range)):
        stage_group = add(f"{key}_{stage}", parent=row_group, field_label=stage.upper(), field_type="group",
                           required=False, standard_value=std)
        kwargs = {"field_type": "numeric_range", "unit": "mm", "decimal_precision": 3, "required": True}
        if rng is not None:
            kwargs["min_value"], kwargs["max_value"] = rng
        else:
            kwargs["field_type"] = "number"
            kwargs.pop("min_value", None)
            kwargs.pop("max_value", None)
        add(f"{key}_{stage}_reading_1", parent=stage_group, field_label="Reading 1", **kwargs)
        add(f"{key}_{stage}_reading_2", parent=stage_group, field_label="Reading 2", **kwargs)
    return row_group


def build(add):
    add("equipment_sr_no", field_label="Equipment S.R. No.", field_type="text", required=True,
        standard_value="Noted")
    add("mcp_sr_no_make", field_label="MCP S.R. No./Make", field_type="text", required=True,
        standard_value="Noted")
    add("overhauling_date", field_label="Overhauling Date", field_type="date", required=True)
    add("tank_capacity", field_label="Tank Capacity", field_type="text", required=False,
        standard_value="065 Ltrs")

    testing_group = add("testing", field_label="Testing", field_type="group", required=False)
    time_taken_group = add("time_taken", parent=testing_group, field_label="Time Taken", field_type="group",
                            required=False)
    time_10_5_group = add("time_0_to_10_5kg", parent=time_taken_group, field_label="0 to 10.5 kg/cm2",
                           field_type="group", required=False, standard_value="Max 5.5 Min (330 Sec)")
    add("time_0_to_10_5kg_pre_testing", parent=time_10_5_group, field_label="Pre-Testing", field_type="numeric_range",
        required=True, unit="sec", min_value=0.0, max_value=330.0, decimal_precision=1)
    add("time_0_to_10_5kg_final_testing", parent=time_10_5_group, field_label="Final Testing", field_type="numeric_range",
        required=True, unit="sec", min_value=0.0, max_value=330.0, decimal_precision=1)
    time_9_5_group = add("time_0_to_9_5kg", parent=time_taken_group, field_label="0 to 9.5 kg/cm2",
                          field_type="group", required=False, standard_value="Max 55 Sec")
    add("time_0_to_9_5kg_pre_testing", parent=time_9_5_group, field_label="Pre-Testing", field_type="numeric_range",
        required=True, unit="sec", min_value=0.0, max_value=55.0, decimal_precision=1)
    add("time_0_to_9_5kg_final_testing", parent=time_9_5_group, field_label="Final Testing", field_type="numeric_range",
        required=True, unit="sec", min_value=0.0, max_value=55.0, decimal_precision=1)

    current_group = add("current", parent=testing_group, field_label="Current", field_type="group",
                         required=False, standard_value="Max 29 Amp")
    for phase_group_key, phase_group_label in (("pre_testing", "Pre-Testing"), ("final_testing", "Final Testing")):
        phase_group = add(f"current_{phase_group_key}", parent=current_group, field_label=phase_group_label,
                           field_type="group", required=False)
        for phase in ("u", "v", "y"):
            add(f"current_{phase_group_key}_{phase}", parent=phase_group, field_label=phase.upper(),
                field_type="numeric_range", required=True, unit="Amp", min_value=0.0, max_value=29.0,
                decimal_precision=1)

    dims_group = add("dimensional_checks", field_label="Dimensional Checks", field_type="group", required=False)
    _add_lp_hp_row(add, dims_group, "cylinder_inner_diameter", "Cylinder Inner Diameter",
                   lp_std="New: 127.05-127.06mm, Max: 127.4mm", hp_std="New: 100.005-100.015mm, Max: 100.12mm",
                   lp_range=(127.05, 127.4), hp_range=(100.005, 100.12))
    _add_lp_hp_row(add, dims_group, "piston", "Piston",
                   lp_std="New: 126.796-126.822mm", hp_std="New: 99.94-99.96mm",
                   lp_range=(126.796, 126.822), hp_range=(99.94, 99.96))
    _add_lp_hp_row(add, dims_group, "difference_1_2", "Difference of 1 & 2",
                   lp_std="New: 0.23-0.26mm, Max: 0.4mm", hp_std="New: 0.045-0.075mm, Max: 0.12mm",
                   lp_range=(0.23, 0.4), hp_range=(0.045, 0.12))
    _add_lp_hp_row(add, dims_group, "butt_ring_joint_clearance", "Butt (Ring Joint) Clearance",
                   lp_std="New: 0.10-0.35mm, Max: 0.45mm", hp_std="New: 0.08-0.25mm, Max: 0.5mm",
                   lp_range=(0.10, 0.45), hp_range=(0.08, 0.5))
    _add_lp_hp_row(add, dims_group, "piston_ring_side_play", "Permissible Piston Rings Side Play in Groove",
                   lp_std="New: 0.03-0.11mm, Max: 0.2mm", hp_std="New: 0.03-0.07mm, Max: 0.5mm",
                   lp_range=(0.03, 0.2), hp_range=(0.03, 0.5))
    _add_lp_hp_row(add, dims_group, "piston_crown_disc_valve_clearance", "Clearance Between Piston Crown and "
                   "Disc Valve (TDC)", lp_std="New: 0.6mm, Max: 0.8mm", hp_std="New: 0.6mm, Max: 0.8mm",
                   lp_range=(0.6, 0.8), hp_range=(0.6, 0.8))

    bearing_seating_group = add("bearing_seating_dia", parent=dims_group, field_label="Bearing Seating Dia",
                                 field_type="group", required=False, standard_value="DE Side: 50.002mm, "
                                                                                     "NDE Side: 50.002-50.013mm")
    add("bearing_seating_de_side", parent=bearing_seating_group, field_label="DE Side", field_type="text",
        required=True)
    add("bearing_seating_nde_side", parent=bearing_seating_group, field_label="NDE Side", field_type="text",
        required=True)

    add("intercooler_safety_valve_overhaul", parent=dims_group, field_label="Inter Cooler Safety Valve "
        "Overhauling", field_type="select", options="Done, Not Done", required=True,
        standard_value="Blowing 6 kg/cm2")
    add("bearing_6310_make", parent=dims_group, field_label="6310 Bearing Make", field_type="text", required=False,
        standard_value="Noted")
    add("bearing_condition", parent=dims_group, field_label="Bearing New/Serviceable", field_type="select",
        options="New, Serviceable", required=True)
    add("motor_compressor_bracket_torque", parent=dims_group, field_label="Tightness of Motor and Compressor "
        "Side Bracket With Torque Wrench", field_type="select", options="OK, Not OK", required=True,
        standard_value="Motor Side 138Nm, Comp Side 136Nm")
    add("must_change_item_ioh_toh_kit", parent=dims_group, field_label="Must Change Item IOH/TOH Kit",
        field_type="select", options="Done, Not Done", required=True)

    soft_mount_group = add("soft_mount", parent=dims_group, field_label="Soft Mount", field_type="group",
                            required=False)
    add("soft_mount_mfg_date", parent=soft_mount_group, field_label="Mfg. Dt.", field_type="text", required=False)
    add("soft_mount_condition", parent=soft_mount_group, field_label="Condition", field_type="select",
        options="New, Old", required=True)
    hard_mount_group = add("hard_mount", parent=dims_group, field_label="Hard Mount", field_type="group",
                            required=False)
    add("hard_mount_mfg_date", parent=hard_mount_group, field_label="Mfg. Dt.", field_type="text", required=False)
    add("hard_mount_condition", parent=hard_mount_group, field_label="Condition", field_type="select",
        options="New, Old", required=True)

    add("any_other_material", parent=dims_group, field_label="Any Other Material", field_type="textarea",
        required=False)

    vibration_group = add("vibration_measurement", field_label="Vibration Measurement of Compressor on Test "
        "Bench (Permissible Limit in Micron)", field_type="group", required=False)
    for key, label, limit in (
        ("cp_mount", "CP Mount", 1540), ("motor_end_outside", "Motor End Out Side", 1400),
        ("motor_end_inside", "Motor End Inside", 1015), ("crank_case", "Crank Case", 1540),
        ("motor_body_v", "Motor Body (V)", 1130), ("motor_body_h", "Motor Body (H)", 1235),
    ):
        add(f"vibration_{key}", parent=vibration_group, field_label=label, field_type="numeric_range",
            required=True, unit="micron", min_value=0.0, max_value=float(limit), decimal_precision=0,
            standard_value=f"{limit} Micron (Max)")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="CP", template_code="137", technology="3_PHASE",
        template_name="Checksheet for Compressor",
        description="Overhauling and Testing Performa of ELGI Compressor - 3-Phase - M35-CP section.",
        build_fn=build,
    )
    run_seed(
        equipment_code="CP_Conv", template_code="138", technology="CONVENTIONAL",
        template_name="Checksheet for Compressor",
        description="Overhauling and Testing Performa of ELGI Compressor - Conventional - M35-CP section.",
        build_fn=build,
    )
