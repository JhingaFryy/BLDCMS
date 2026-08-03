"""
Module 43: seeds the Bear_Conv (Bearing Brackets, Conventional locomotives, M35-TM section)
checksheet template.

Run once: `venv/bin/python scripts/seed_bearing_brackets_conv_template.py`

Source: "FR/TM/AC/08 - Overhauling and Assembling Schedule - Bearing Brackets" (Locomotive Care
Centre Ratlam, Western Railway), an 11-item overhaul/dimensional checklist (item 1 has 5
sub-parts A-E, each a distinct dimensional measurement set) covering PEB/CEB bearing stopper,
end shield, deflector clearances/interference, outer race condition, and radial clearance before/
after assembly - all referencing RDSO/2012/ELRS/MS/0414 Amendment No. 01.

No `maintenance_type` is set (stays NULL) - see seed_rocker_brush_holder_conv_template.py's
docstring for why this keeps the Android app's TM Number/GC-Overhaul UI from triggering for
Conventional equipment.
"""
from _aux_template_helpers import add_final_remarks, run_seed

RDSO_REF = "RDSO/2012/ELRS/MS/0414 Amendment No. 01 Dt. 29.01.2013"


def build(add):
    add("armature_no", field_label="Armature No.", field_type="text", required=True, standard_value="Noted")
    add("armature_make", field_label="Make", field_type="text", required=True, standard_value="Noted")
    add("armature_mfg", field_label="MFG", field_type="text", required=True, standard_value="Noted")

    bearing_group = add("bearing_details", field_label="Bearing Details", field_type="group", required=False)
    for side in ("PE", "CE"):
        side_group = add(f"bearing_{side.lower()}", parent=bearing_group, field_label=side, field_type="group",
                          required=False)
        add(f"bearing_{side.lower()}_serial_no", parent=side_group, field_label="Bearing Serial No",
            field_type="text", required=True, standard_value="Noted")
        add(f"bearing_{side.lower()}_make", parent=side_group, field_label="Bearing Make", field_type="text",
            required=True, standard_value="Noted")
        add(f"bearing_{side.lower()}_country_mfg", parent=side_group, field_label="Country MFG",
            field_type="text", required=True, standard_value="Noted")
        add(f"bearing_{side.lower()}_date_of_fitting", parent=side_group, field_label="Date of Fitting",
            field_type="date", required=True)

    add("pe_old_bearing_history", field_label="PE Old Bearing History", field_type="textarea", required=False)
    add("ce_old_bearing_history", field_label="CE Old Bearing History", field_type="textarea", required=False)

    degrease_group = add("degrease_clean", field_label="Degrease the Bearing Brackets, Grease Covers and "
        "Deflector With Kerosene and Clean Thoroughly by Compressed Air and Then by Petrol", field_type="group",
        required=False)
    add("degrease_clean_done", parent=degrease_group, field_label="Done", field_type="select",
        options="Done, Not Done", required=True)

    peb_stopper_group = add("peb_bearing_stopper_shaft_dia", field_label="Measure PEB Bearing Stopper and "
        "Shaft Dia. and Interference", field_type="group", required=False, authority_reference=RDSO_REF)
    add("peb_stopper_id", parent=peb_stopper_group, field_label="ID of BRG Stopper", field_type="numeric_range",
        required=True, unit="mm", min_value=151.00, max_value=151.015, decimal_precision=3)
    add("peb_stopper_shaft_outer_dia", parent=peb_stopper_group, field_label="Outer Dia of Shaft",
        field_type="numeric_range", required=True, unit="mm", min_value=151.027, max_value=151.052,
        decimal_precision=3)
    add("peb_stopper_interference", parent=peb_stopper_group, field_label="Interference", field_type="numeric_range",
        required=True, unit="mm", min_value=0.012, max_value=0.052, decimal_precision=3)

    peb_end_shield_group = add("peb_end_shield_bracket_dia", field_label="Measure PEB End Shield and "
        "Bracket/Cover Dia. and Clearance", field_type="group", required=False, authority_reference=RDSO_REF)
    add("peb_bracket_id", parent=peb_end_shield_group, field_label="PEB-Bracket/ID", field_type="numeric_range",
        required=True, unit="mm", min_value=319.954, max_value=319.990, decimal_precision=3)
    add("peb_outer_cover", parent=peb_end_shield_group, field_label="PEB-Outer Cover", field_type="numeric_range",
        required=True, unit="mm", min_value=319.900, max_value=319.920, decimal_precision=3)
    add("peb_end_shield_clearance", parent=peb_end_shield_group, field_label="Clearance", field_type="numeric_range",
        required=True, unit="mm", min_value=-0.090, max_value=0.034, decimal_precision=3)

    ceb_end_shield_group = add("ceb_end_shield_bracket_dia", field_label="Measure CEB End Shield and "
        "Bracket/Cover Dia. and Interference", field_type="group", required=False, authority_reference=RDSO_REF)
    add("ceb_bracket_id", parent=ceb_end_shield_group, field_label="CEB-Bracket/ID", field_type="numeric_range",
        required=True, unit="mm", min_value=259.959, max_value=259.993, decimal_precision=3)
    add("ceb_outer_cover", parent=ceb_end_shield_group, field_label="CEB-Outer Cover", field_type="numeric_range",
        required=True, unit="mm", min_value=259.900, max_value=259.920, decimal_precision=3)
    add("ceb_end_shield_clearance", parent=ceb_end_shield_group, field_label="Clearance", field_type="numeric_range",
        required=True, unit="mm", min_value=-0.093, max_value=0.039, decimal_precision=3)

    deflector_group = add("deflector_shaft_dia_interference", field_label="Deflector and Shaft Dia. and "
        "Interference", field_type="group", required=False, authority_reference=RDSO_REF)
    add("deflector_shaft_dia", parent=deflector_group, field_label="Deflector - Shaft Dia", field_type="numeric_range",
        required=True, unit="mm", min_value=140.092, max_value=140.117, decimal_precision=3)
    add("deflector_id", parent=deflector_group, field_label="Deflector - ID", field_type="numeric_range",
        required=True, unit="mm", min_value=140.000, max_value=140.04, decimal_precision=3)
    add("deflector_interference", parent=deflector_group, field_label="Interference", field_type="numeric_range",
        required=True, unit="mm", min_value=0.052, max_value=0.117, decimal_precision=3)

    outer_race_group = add("bearing_outer_races_check", field_label="Examine the Bearing Outer Races for "
        "Crack, Roller Damage, Loose Rivet, Punch-Marks or Any Other Abnormalities in PEB and CEB",
        field_type="group", required=False, standard_value="Normal")
    add("outer_races_peb", parent=outer_race_group, field_label="PEB", field_type="select",
        options="Normal, Abnormal", required=True, negative_values="Abnormal")
    add("outer_races_ceb", parent=outer_race_group, field_label="CEB", field_type="select",
        options="Normal, Abnormal", required=True, negative_values="Abnormal")

    rollers_group = add("rollers_freeness_check", field_label="Ensure Freeness and Smooth Rotation of Rollers",
        field_type="group", required=False, standard_value="Normal")
    add("rollers_freeness_peb", parent=rollers_group, field_label="PEB", field_type="select",
        options="Normal, Abnormal", required=True, negative_values="Abnormal")
    add("rollers_freeness_ceb", parent=rollers_group, field_label="CEB", field_type="select",
        options="Normal, Abnormal", required=True, negative_values="Abnormal")

    inner_covers_group = add("inner_bearing_covers_check", field_label="Visually Examine for Good Condition "
        "of Both the Inner Bearing Covers", field_type="group", required=False, standard_value="Normal")
    add("inner_covers_peb", parent=inner_covers_group, field_label="PEB", field_type="select",
        options="Normal, Abnormal", required=True, negative_values="Abnormal")
    add("inner_covers_ceb", parent=inner_covers_group, field_label="CEB", field_type="select",
        options="Normal, Abnormal", required=True, negative_values="Abnormal")

    mating_surface_group = add("mating_surface_fit_check", field_label="Check Up for Good Finish of Mating "
        "Surface and Ensure Tight Fit of Both the End Shields on the Magnet Frame", field_type="group",
        required=False, standard_value="Normal")
    add("mating_surface_peb", parent=mating_surface_group, field_label="PEB", field_type="select",
        options="Normal, Abnormal", required=True, negative_values="Abnormal")
    add("mating_surface_ceb", parent=mating_surface_group, field_label="CEB", field_type="select",
        options="Normal, Abnormal", required=True, negative_values="Abnormal")

    add("bearing_brackets_varnish", field_label="Varnish the Inside of Both the Bearing Brackets",
        field_type="select", options="Done, Not Done", required=True)
    add("pe_air_meshes_check", field_label="Attend/Replace the PE Side Air Meshes if Required",
        field_type="select", options="Good, Replaced", required=True)
    add("bearing_residual_life_check", field_label="Ensure Residual Life for PE & CE Bearings",
        field_type="select", options="OK, Not OK", required=True, standard_value="WAG5: 10 Years")

    outer_race_fit_group = add("outer_race_housing_fit_check", field_label="Visually Examine for Tight Fit of "
        "Outer Race in the Bearing Housing", field_type="group", required=False, standard_value="Normal")
    add("outer_race_fit_check", parent=outer_race_fit_group, field_label="Fit Check", field_type="select",
        options="Normal, Abnormal", required=True, negative_values="Abnormal")

    peb_housing_group = add("peb_end_shield_outer_race_dia", field_label="Measure PEB End Shield Inner Dia. "
        "and Outer Race Outer Dia. and Interference", field_type="group", required=False,
        authority_reference=RDSO_REF)
    add("peb_housing_dia", parent=peb_housing_group, field_label="PEB-Housing", field_type="numeric_range",
        required=True, unit="mm", min_value=319.944, max_value=319.962, decimal_precision=3)
    add("peb_od", parent=peb_housing_group, field_label="PEB-OD", field_type="numeric_range", required=True,
        unit="mm", min_value=319.972, max_value=320.000, decimal_precision=3)
    add("peb_housing_interference", parent=peb_housing_group, field_label="Interference", field_type="numeric_range",
        required=True, unit="mm", min_value=0.010, max_value=0.056, decimal_precision=3)

    ceb_housing_group = add("ceb_end_shield_outer_race_dia", field_label="Measure CEB End Shield Inner Dia. "
        "and Outer Race Outer Dia. and Interference", field_type="group", required=False,
        authority_reference=RDSO_REF)
    add("ceb_housing_dia", parent=ceb_housing_group, field_label="CEB-Housing", field_type="numeric_range",
        required=True, unit="mm", min_value=259.949, max_value=259.965, decimal_precision=3)
    add("ceb_od", parent=ceb_housing_group, field_label="CEB-OD", field_type="numeric_range", required=True,
        unit="mm", min_value=259.975, max_value=260.000, decimal_precision=3)
    add("ceb_housing_interference", parent=ceb_housing_group, field_label="Interference", field_type="numeric_range",
        required=True, unit="mm", min_value=0.010, max_value=0.051, decimal_precision=3)

    peb_fitment_group = add("peb_shaft_inner_race_id_before_fitment", field_label="Measure Shaft Dia. and PEB "
        "Inner Race ID Before Fitment and Interference", field_type="group", required=False)
    add("peb_shaft_outer_dia_fitment", parent=peb_fitment_group, field_label="Shaft Outer Dia", field_type="numeric_range",
        required=True, unit="mm", min_value=150.043, max_value=150.068, decimal_precision=3)
    add("peb_inner_race_id_fitment", parent=peb_fitment_group, field_label="Inner Racer ID", field_type="numeric_range",
        required=True, unit="mm", min_value=149.982, max_value=150.000, decimal_precision=3)
    add("peb_fitment_interference", parent=peb_fitment_group, field_label="Interference", field_type="numeric_range",
        required=True, unit="mm", min_value=0.043, max_value=0.086, decimal_precision=3)

    ceb_fitment_group = add("ceb_shaft_inner_race_id_before_fitment", field_label="Measure Shaft Dia. and CEB "
        "Inner Race ID Before Fitment and Interference", field_type="group", required=False)
    add("ceb_shaft_dia_fitment", parent=ceb_fitment_group, field_label="Shaft Dia", field_type="numeric_range",
        required=True, unit="mm", min_value=120.037, max_value=120.059, decimal_precision=3)
    add("ceb_inner_race_id_fitment", parent=ceb_fitment_group, field_label="Inner Racer ID", field_type="numeric_range",
        required=True, unit="mm", min_value=119.985, max_value=120.000, decimal_precision=3)
    add("ceb_fitment_interference", parent=ceb_fitment_group, field_label="Interference", field_type="numeric_range",
        required=True, unit="mm", min_value=0.037, max_value=0.074, decimal_precision=3)

    radial_before_group = add("radial_clearance_before_assembly", field_label="Check the Radial Clearance of "
        "Both the Bearings Before Assembling", field_type="group", required=False,
        authority_reference="Camtech Maintenance Manual Page No. 40")
    add("radial_clearance_before_peb", parent=radial_before_group, field_label="PEB", field_type="numeric_range",
        required=True, unit="mm", min_value=0.165, max_value=0.210, decimal_precision=3)
    add("radial_clearance_before_ceb", parent=radial_before_group, field_label="CEB", field_type="numeric_range",
        required=True, unit="mm", min_value=0.155, max_value=0.195, decimal_precision=3)

    radial_after_group = add("radial_clearance_after_assembly", field_label="Check the Radial Clearance of "
        "Both the Bearings After Assembling", field_type="group", required=False,
        authority_reference="Camtech Maintenance Manual Page No. 40")
    add("radial_clearance_after_peb", parent=radial_after_group, field_label="PEB", field_type="numeric_range",
        required=True, unit="mm", min_value=0.104, max_value=0.177, decimal_precision=3)
    add("radial_clearance_after_ceb", parent=radial_after_group, field_label="CEB", field_type="numeric_range",
        required=True, unit="mm", min_value=0.066, max_value=0.147, decimal_precision=3)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="Bear_Conv", template_code="141", technology="CONVENTIONAL",
        template_name="Checksheet for Bearing Brackets",
        description="Overhauling and Assembling Schedule - Bearing Brackets checksheet - Conventional - "
                     "M35-TM section.",
        build_fn=build,
    )
