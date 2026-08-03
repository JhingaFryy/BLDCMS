"""
Module 32: seeds the M35-TM Traction Motor "Overhaul" template - the 7-page "Assembly/Fitment of
TM type -6FRA 6068 (New/Overhauling)" reference checksheet (BL REV.05/06/2025).

Run once: `venv/bin/python scripts/seed_tm_overhaul_template.py`

Page numbers below roughly mirror the source document's own 7 physical pages, purely for a
sensible multi-page mobile form - nothing about page_number affects validation.

Distinctive modeling notes (all use only existing, generic template-engine capabilities):
- Almost every dimensional checking point (S.N. 9-20) has TWO standard values on the paper: a
  design/spec dimension range for each mating component, AND a separate, bolded "BL Interference"
  band that is the shed's own actual acceptance criterion. Modeled as a group whose children are
  the raw component readings (numeric_range from the design dimensions) plus a final
  "Interference" reading (numeric_range from the BL Interference band - the real pass/fail check).
- Where a bearing/labyrinth make (SKF/FAG/NEI) shifts the exact tolerance by a few microns
  (S.N. 16, 19), the combined (inclusive) range across all three makes is used for validation,
  with the make-specific split kept in standard_value's text for the technician's reference -
  the template engine has no per-make conditional-range concept, and inventing one for a few
  microns of difference would be a new capability the module didn't ask for.
- S.N. 29's gear K-value/backlash table lists three parallel component variants (different pinion/
  bull-gear tooth counts) - modeled as three parallel sub-groups so all three sets of standards are
  preserved exactly; whichever is physically fitted to a given motor is the one the technician fills.
- S.N. 1 of the second (electrical) table reuses the same validation_rule='absolute_difference'
  rule as the GC template's winding inductance check (0.015 mH flat threshold) - the same reusable
  rule serving both templates, exactly as intended.
- Rows with no defined numeric standard at all (e.g. S.N. 6, part of 28) are modeled as plain
  text/number fields with no range validation, rather than inventing a standard the source
  document doesn't give.
- Module 32.1: S.N. 11 and S.N. 17 (the DE/NDE inner racer BOD/AOD/Swell checkpoints - the two
  rows with no defined standard at all, not even a range) are seeded with is_active=False on the
  group and all 3 children. They stay in the template at their exact original position/field_key/
  display_order as future-implementation placeholders - excluded from Android/Dashboard form
  composition, submission requirements, validation, and PDF generation purely because those all
  already key off is_active/submitted values, with zero Template/Validation/PDF Engine changes.
  Re-running this script preserves that inactive state; reactivating them later only ever needs
  is_active flipped back to True here.
"""
from _tm_template_helpers import run_seed


def add_dimension_pair_group(add, field_key, label, standard_note, child_a_key, child_a_label, child_a_min, child_a_max,
                              child_b_key, child_b_label, child_b_min, child_b_max,
                              interference_min, interference_max, page_number):
    group = add(
        field_key, field_label=label, field_type="group", required=False,
        standard_value=standard_note, authority_reference="SMI-278", page_number=page_number,
    )
    add(f"{field_key}_{child_a_key}", parent=group, field_label=child_a_label, field_type="numeric_range",
        required=True, unit="mm", min_value=child_a_min, max_value=child_a_max, decimal_precision=3,
        standard_value=f"{child_a_min} - {child_a_max} mm", page_number=page_number)
    add(f"{field_key}_{child_b_key}", parent=group, field_label=child_b_label, field_type="numeric_range",
        required=True, unit="mm", min_value=child_b_min, max_value=child_b_max, decimal_precision=3,
        standard_value=f"{child_b_min} - {child_b_max} mm", page_number=page_number)
    add(f"{field_key}_interference", parent=group, field_label="Interference", field_type="numeric_range",
        required=True, unit="mm", min_value=interference_min, max_value=interference_max, decimal_precision=3,
        standard_value=f"BL Interference: {interference_min} - {interference_max} mm", page_number=page_number)
    return group


def build(add):
    # ================= Page 1: Header / assembly detail tables =================
    p = 1
    # Module 32.2: Loco No. & Type / Homing Shed / Railways deliberately NOT seeded here -
    # redundant with the Locomotive already selected before this template loads. See
    # scripts/remove_tm_header_redundant_fields.py for the full rationale.
    add("pu_tm_manufacturer", field_label="Name of PUs/TM Manufacturer", field_type="text", required=False, page_number=p)
    add("received_from_rehabilitation", field_label="Received from Last Rehabilitation/Repair (NKRD/CNB/PLW)",
        field_type="text", required=False, page_number=p)

    add("make_of_tm", field_label="Make of TM", field_type="text", required=False, page_number=p)
    add("doc_of_tm", field_label="D.O.C of TM", field_type="date", required=False, page_number=p)
    add("sr_no_of_tm", field_label="Sr. No. of TM", field_type="text", required=True, page_number=p)
    add("shaft_blue_matching_pct", field_label="Shaft Blue Matching % with Plug Gauge", field_type="number", required=False, unit="%", page_number=p)
    add("tm_assembly_components_11items", field_label="TM Assembly Components (11 items) (Labyrinths, DE/NDE End Frame Make)",
        field_type="textarea", required=False, page_number=p)
    add("rotor_sr_no_make", field_label="Rotor Sr. No. & Make", field_type="text", required=False, page_number=p)
    add("stator_sr_no_make", field_label="Stator Sr. No. & Make", field_type="text", required=False, page_number=p)
    add("shaft_no", field_label="Shaft No.", field_type="text", required=False, page_number=p)
    add("make_bearing_de", field_label="Make of Bearing DE", field_type="text", required=False, page_number=p)
    add("shaft_make", field_label="Shaft Make", field_type="text", required=False, page_number=p)
    add("make_bearing_nde", field_label="Make of Bearing NDE", field_type="text", required=False, page_number=p)
    add("nos_teeth_pinion", field_label="Nos. of Teeth on Pinion", field_type="number", required=False, page_number=p)
    add("pinion_make_month_year", field_label="Pinion Make/Month/Year", field_type="text", required=False, page_number=p)
    add("type_of_rotor", field_label="Type of Rotor (Sch.-1/2)", field_type="select", options="Sch.-1, Sch.-2", required=False, page_number=p)
    add("date_tm_assembly_last_overhauling", field_label="Date of TM Assembly/Last Overhauling", field_type="date", required=False, page_number=p)

    add("sr_no_de_bearing", field_label="Sr. No. of DE Bearing", field_type="text", required=False, page_number=p)
    add("sr_no_nde_bearing", field_label="Sr. No. of NDE Bearing", field_type="text", required=False, page_number=p)
    add("change_bearing_de_nde_overhauling", field_label="Change of Bearing DE/NDE During Overhauling", field_type="select",
        options="Yes, No", required=False, page_number=p)
    add("date_commissioning_de_bearing", field_label="Date of Commissioning of DE Bearing in TM", field_type="date", required=False, page_number=p)
    add("date_commissioning_nde_bearing", field_label="Date of Commissioning of NDE Bearing in TM", field_type="date", required=False, page_number=p)
    add("date_replacement_bearing_overhauling", field_label="Date of Replacement of Bearing During Overhauling", field_type="date", required=False, page_number=p)
    add("last_schedule_bearing_replaced", field_label="Last Schedule in Which TM Bearing Replaced During Overhauling", field_type="text", required=False, page_number=p)
    add("free_radial_clearance_de_before_fitment", field_label="Free Radial Clearance of (DE) Bearing NU-2236 Before Fitment",
        field_type="numeric_range", required=True, unit="um", min_value=170.0, max_value=220.0, decimal_precision=1,
        standard_value="170 - 220 um", page_number=p)
    add("free_radial_clearance_nde_before_fitment", field_label="Free Radial Clearance of (NDE) Bearing NH-320 Before Fitment",
        field_type="numeric_range", required=True, unit="um", min_value=105.0, max_value=140.0, decimal_precision=1,
        standard_value="105 - 140 um", page_number=p)

    # ================= Page 2: S.N. 1-11 =================
    p = 2
    add(
        "motor_assembled_original_dummy_pinion", field_label="Motor Assembled with Original Pinion or Dummy Pinion",
        field_type="select", options="Original, Dummy", required=True,
        standard_value="As per assembly procedure issued vide SMI:278 Amendment-2 dated 29/3/2022", page_number=p,
    )
    add(
        "pinion_shaft_taperness_ring_gauge", field_label="Check the Pinion Shaft Taperness Using Ring Gauge (Drawing SKEL-5043 Alt-0, SMI-278)",
        field_type="numeric_range", required=True, unit="mm", min_value=14.7, max_value=15.3, decimal_precision=2,
        standard_value="Distance between gauge face and pinion teeth face should be 15 +/- 0.3mm", page_number=p,
    )
    add(
        "pinion_mounting_pressure", field_label="Pinion Mounting Pressure of Pump",
        field_type="numeric_range", required=True, unit="bar", min_value=1700.0, max_value=2000.0, decimal_precision=0,
        standard_value="1700 - 2000 bar", page_number=p,
    )
    add(
        "pinion_shaft_ut_dpt_test", field_label="Pinion Shaft UT and DPT Test",
        field_type="select", options="No Cracks/Flaws, Cracks/Flaws Found", required=True,
        standard_value="No cracks/Flaws", authority_reference="Shed practice",
        negative_values="Cracks/Flaws Found", page_number=p,
    )
    add(
        "rotor_shaft_taperness_plug_gauge", field_label="Checking of Rotor Shaft Taperness Using Plug Gauge (Drawing SKEL-5032 Alt-0, SMI-278 Amendment-1)",
        field_type="numeric_range", required=True, unit="mm", min_value=0.7, max_value=1.3, decimal_precision=2,
        standard_value="Distance between plug gauge face & shaft outer face should be 1 +/- 0.3mm", page_number=p,
    )
    add(
        "advancement_pinion_fitment", field_label="Advancement of Pinion During Fitment",
        field_type="textarea", required=False,
        standard_value=(
            "Ensure actual pinion is inserted in the shaft before mounting of inner racer. "
            "Measure the bore diameter of inner racer and bearing seat diameter of shaft and "
            "ensure there shall be interference between them 50-65 micron. This can be done by "
            "selecting right match of inner racer for a given shaft."
        ),
        page_number=p,
    )
    add(
        "gap_shaft_outer_pinion_inner", field_label="Gap Between Shaft Outer Face & Pinion Inner Face",
        field_type="numeric_range", required=True, unit="mm", min_value=3.0, max_value=5.0, decimal_precision=2,
        standard_value="3.0 mm to 5.00 mm", page_number=p,
    )
    add(
        "types_of_labyrinths", field_label="Types of Labyrinths",
        field_type="boolean", required=True,
        standard_value="Modified as per MS 0478 issued on July/2019",
        negative_values="false", page_number=p,
    )
    add_dimension_pair_group(
        add, "shaft_inner_labyrinth_de", "Shaft Diameter and Inner Labyrinth Diameter (DE)",
        "Shaft Diameter 184.050-184.079mm / Inner Labyrinth ID 184.00-184.040mm",
        "shaft_od", "Shaft OD", 184.050, 184.079,
        "labyrinth_id", "Inner Labyrinth ID", 184.00, 184.040,
        0.045, 0.079, p,
    )
    add_dimension_pair_group(
        add, "shaft_inner_racer_bearing_de", "Shaft Diameter (OD) and Inner Racer Bearing (ID) of (DE)",
        "Shaft Diameter 180.043-180.068mm / Inner Racer ID 179.975-180.00mm",
        "shaft_diameter", "Shaft Diameter", 180.043, 180.068,
        "bearing_id", "Bearing (ID)", 179.975, 180.00,
        0.050, 0.065, p,
    )
    # Module 32.1: Point 11 has no clearly defined pass/fail standard in the source document (only
    # the formula Swell = interference x Diameter / Height, no stated acceptable range) - kept in
    # the template at its exact original position/field_key/display_order as an inactive
    # future-implementation placeholder (is_active=False), per the module's explicit instruction.
    # Hidden from Android/Dashboard form composition and submission requirements, ignored by
    # validation and PDF generation - all three already derive from is_active or from submitted
    # values, so this needed zero Template/Validation/PDF Engine changes. Reactivating this point
    # later is a one-column metadata change, not a structural one.
    inner_racer_de = add(
        "inner_racer_de_bod_aod", field_label="OD of Inner Racer (DE) Before/After Provision on Shaft",
        field_type="group", required=False, is_active=False,
        standard_value="Swell = interference x Diameter / Height. AOD standard = 215.000 - 215.025mm",
        page_number=p,
    )
    add("inner_racer_de_bod", parent=inner_racer_de, field_label="BOD (Before Provision)", field_type="number", required=False, is_active=False, unit="mm", page_number=p)
    add("inner_racer_de_aod", parent=inner_racer_de, field_label="AOD (After Provision)", field_type="numeric_range", required=False, is_active=False,
        unit="mm", min_value=215.000, max_value=215.025, decimal_precision=3, standard_value="215.000 - 215.025 mm", page_number=p)
    add("inner_racer_de_swell", parent=inner_racer_de, field_label="Swell (AOD - BOD)", field_type="number", required=False, is_active=False, unit="mm", page_number=p)

    # ================= Page 3: S.N. 12-19 =================
    p = 3
    add_dimension_pair_group(
        add, "de_inner_labyrinth_end_frame", "DE Inner Labyrinth (OD) and End Frame Inner Diameter of DE",
        "Inner Labyrinth OD 305.060-305.080mm / DE End Frame ID 305.025-305.050mm",
        "labyrinth_od", "Inner Labyrinth (OD)", 305.060, 305.080,
        "end_frame_id", "DE End Frame (ID)", 305.025, 305.050,
        0.035, 0.055, p,
    )
    add_dimension_pair_group(
        add, "de_outer_racer_end_frame", "OD of Outer Racer Bearing and ID of End Frame (DE)",
        "Outer Racer OD 319.960-320.000mm / DE End Frame ID 319.950-319.990mm",
        "outer_racer_od", "Outer Racer (OD)", 319.960, 320.000,
        "end_frame_id", "DE End Frame (ID)", 319.950, 319.990,
        0.010, 0.025, p,
    )
    add_dimension_pair_group(
        add, "de_shaft_outer_labyrinth_deflector", "Shaft Diameter and Outer Labyrinth/Deflector (DE)",
        "Shaft Dia 179.843-179.868mm / Outer Labyrinth (ID) 179.748-179.783mm",
        "shaft_dia", "Shaft Dia", 179.843, 179.868,
        "outer_labyrinth_id", "Outer Labyrinth (ID)", 179.748, 179.783,
        0.085, 0.120, p,
    )
    add_dimension_pair_group(
        add, "nde_inner_labyrinth_diameter", "Shaft Diameter and Inner Labyrinth Diameter (NDE)",
        "Shaft Diameter 105.037-105.059mm / Inner Labyrinth ID 105.00-105.025mm",
        "shaft_diameter", "Shaft Diameter", 105.037, 105.059,
        "labyrinth_id", "Inner Labyrinth ID", 105.00, 105.025,
        0.035, 0.059, p,
    )
    add_dimension_pair_group(
        add, "nde_inner_racer_bearing", "Shaft Diameter and Inner Racer of Bearing (ID) of (NDE)",
        "Shaft Diameter 100.023-100.045mm / Inner Racer ID 99.980-100.00mm (SKF 99.985-100.00, FAG/NEI 99.980-100.00)",
        "shaft_diameter", "Shaft Diameter", 100.023, 100.045,
        "inner_racer_id", "Inner Racer (ID)", 99.980, 100.00,
        0.035, 0.060, p,
    )
    # Module 32.1: Point 17 - same rationale and treatment as Point 11 above (its NDE-side
    # counterpart), inactive future-implementation placeholder.
    inner_racer_nde = add(
        "inner_racer_nde_bod_aod", field_label="OD of Inner Racer (NDE) Before/After Provision on Shaft",
        field_type="group", required=False, is_active=False,
        standard_value="Swell = interference x Diameter / Height",
        page_number=p,
    )
    add("inner_racer_nde_bod", parent=inner_racer_nde, field_label="BOD (Before Provision)", field_type="number", required=False, is_active=False, unit="mm", page_number=p)
    add("inner_racer_nde_aod", parent=inner_racer_nde, field_label="AOD (After Provision)", field_type="number", required=False, is_active=False, unit="mm", page_number=p)
    add("inner_racer_nde_swell", parent=inner_racer_nde, field_label="Swell (AOD - BOD)", field_type="number", required=False, is_active=False, unit="mm", page_number=p)

    add_dimension_pair_group(
        add, "nde_inner_labyrinth_end_frame", "NDE Inner Labyrinth and End Frame Inner Diameter of NDE",
        "Labyrinth OD 205.050-205.070mm / End Frame ID 205.010-205.040mm",
        "labyrinth_od", "Labyrinth (OD)", 205.050, 205.070,
        "end_frame_id", "End Frame (ID)", 205.010, 205.040,
        0.030, 0.060, p,
    )
    add_dimension_pair_group(
        add, "nde_outer_racer_end_frame", "OD of Outer Racer of (NDE) Bearing and ID of End Frame (NDE)",
        "Outer Racer OD 214.970-215.000mm (SKF 214.980-215.000, FAG/NEI 214.970-215.000) / End Frame ID 214.948-214.970mm",
        "outer_racer_od", "Outer Racer (OD)", 214.970, 215.000,
        "end_frame_id", "End Frame (ID)", 214.948, 214.970,
        0.010, 0.025, p,
    )

    # ================= Page 4: S.N. 20-28 =================
    p = 4
    clamp_plate = add(
        "shaft_clamp_plate_nde", field_label="Shaft Diameter and Clamp Plate ID of (NDE)",
        field_type="group", required=False,
        standard_value="Shaft Diameter 100.023-100.045mm / Clamp Plate ID 100.000-100.013mm. It should be ensured "
                        "that clamp plate is tight fitted on shaft.",
        page_number=p,
    )
    add("shaft_clamp_plate_nde_shaft_diameter", parent=clamp_plate, field_label="Shaft Diameter", field_type="numeric_range",
        required=True, unit="mm", min_value=100.023, max_value=100.045, decimal_precision=3,
        standard_value="100.023 - 100.045 mm", page_number=p)
    add("shaft_clamp_plate_nde_plate_id", parent=clamp_plate, field_label="Clamp Plate (ID)", field_type="numeric_range",
        required=True, unit="mm", min_value=100.000, max_value=100.013, decimal_precision=3,
        standard_value="100.000 - 100.013 mm", page_number=p)
    add("shaft_clamp_plate_nde_interference", parent=clamp_plate, field_label="Interference", field_type="numeric_range",
        required=True, unit="mm", min_value=-0.025, max_value=0.045, decimal_precision=3,
        standard_value="BL Interference: -0.025 - 0.045 mm", page_number=p)
    add("clamp_plate_tight_fitted", parent=clamp_plate, field_label="Clamp Plate Tight Fitted on Shaft",
        field_type="boolean", required=True, negative_values="false", page_number=p)

    add(
        "clearance_de_end_frame_bearing_cap", field_label="Clearance Between Outer Face of End Frame (DE) & Inner Face of Outer Bearing Cap (DE)",
        field_type="numeric_range", required=True, unit="mm", min_value=0.20, max_value=0.95, decimal_precision=2,
        standard_value="0.20 mm to 0.95 mm as per MS-0466", page_number=p,
    )
    add(
        "clearance_nde_end_frame_bearing_cap", field_label="Clearance Between Outer Face of End Frame (NDE) & Inner Face of Bearing Cap (NDE)",
        field_type="numeric_range", required=True, unit="mm", min_value=0.25, max_value=0.95, decimal_precision=2,
        standard_value="0.25 mm to 0.95 mm as per MS-0460", page_number=p,
    )

    radial_clearance = add(
        "radial_clearance_assembled_tm", field_label="Radial Clearance of Assembled Traction Motor 6FRA-6068",
        field_type="group", required=False, authority_reference="SMI-278 amendment-1 dated 08.03.2021", page_number=p,
    )
    add("radial_clearance_measured_value", parent=radial_clearance, field_label="Radial Clearance Measured Value",
        field_type="number", required=True, unit="um", standard_value="130 - 220 um", page_number=p)
    add("radial_clearance_final_effective_value", parent=radial_clearance, field_label="Final (Effective) Value of RC",
        field_type="numeric_range", required=True, unit="um", min_value=110.0, max_value=190.0, decimal_precision=1,
        standard_value="Measured value x 0.86 = 110 to 190 um", page_number=p)

    add(
        "axial_clearance_assembled_tm", field_label="Axial Clearance of Assembled Traction Motor 6FRA 6068",
        field_type="numeric_range", required=True, unit="um", min_value=200.0, max_value=400.0, decimal_precision=1,
        standard_value="200-400 um as per SMI-278 amendment-1 dated 08.03.2021", page_number=p,
    )
    add(
        "radial_clearance_nde_bearing_after_fitment", field_label="Check Radial Clearance of (NDE) Bearing After Fitment",
        field_type="numeric_range", required=True, unit="mm", min_value=0.060, max_value=0.110, decimal_precision=3,
        standard_value="0.060 to 0.110 mm", page_number=p,
    )
    add(
        "tm_procured_trade_actual_pinion", field_label="Complete Traction Motor Procured from Trade with Actual Pinion",
        field_type="boolean", required=True,
        standard_value="As per RDSO letter no. EL/3.2.182 dated 04.03.2022",
        negative_values="false", page_number=p,
    )
    add(
        "grease_outlet_hole_diameter_increased", field_label="Grease Outlet Hole Diameter of End Frame (DE) Increased from 9mm to 12mm",
        field_type="boolean", required=True,
        standard_value="As per MS-485 dated 17/3/22",
        negative_values="false", page_number=p,
    )
    resistance_ring = add(
        "radial_clearance_resistance_ring_rotor_end_ring", field_label="Radial Clearance Between Resistance Ring and Rotor End Ring",
        field_type="group", required=False,
        standard_value="Applicable during new manufacturing/Repair of Scheme-II rotor, as per MS/0438 Rev.0 dated 27.08.2015",
        page_number=p,
    )
    add("resistance_ring_three_dovetail_joints", parent=resistance_ring, field_label="Three Dovetail Joints",
        field_type="number", required=False, unit="mm", standard_value="2.5 mm", page_number=p)
    add("resistance_ring_remaining_three_dovetail_joints", parent=resistance_ring, field_label="Remaining Three Dovetail Joints",
        field_type="number", required=False, unit="mm", standard_value="3.0 mm", page_number=p)

    # ================= Page 5: S.N. 29-38 =================
    p = 5
    gear_kvalue = add(
        "gear_pinion_kvalue_backlash", field_label="Gear/Pinion Base Tangent 'K' Value and Backlash",
        field_type="group", required=False,
        standard_value="Whichever gear set variant is fitted to this motor", page_number=p,
    )
    variant_1 = add("gear_variant_15t_pinion", parent=gear_kvalue, field_label="Variant: 15T Pinion (SKDP-3436) / 77T Bull Gear (SKDP-3435)",
                     field_type="group", required=False, page_number=p)
    add("gear_variant_1_pinion_k", parent=variant_1, field_label="Pinion 'K' Value (over 3 Teeth)", field_type="numeric_range",
        required=False, unit="mm", min_value=77.783, max_value=77.802, decimal_precision=3,
        standard_value="77.783 - 77.802 mm, Condemning limit = 77.426mm", page_number=p)
    add("gear_variant_1_bull_gear_k", parent=variant_1, field_label="Bull Gear 'K' Value (over 9 Teeth)", field_type="numeric_range",
        required=False, unit="mm", min_value=261.668, max_value=261.696, decimal_precision=3,
        standard_value="261.668 - 261.696 mm, Condemning limit = 261.156mm", page_number=p)
    add("gear_variant_1_backlash", parent=variant_1, field_label="Backlash", field_type="numeric_range",
        required=False, unit="mm", min_value=0.254, max_value=0.458, decimal_precision=3,
        standard_value="0.254 mm (Min) - 0.458 mm (Max)", page_number=p)

    variant_2 = add("gear_variant_20t_pinion", parent=gear_kvalue, field_label="Variant: 20T Pinion (SKDP-3473) / 72T Bull Gear (SKDP-3474)",
                     field_type="group", required=False, page_number=p)
    add("gear_variant_2_pinion_k", parent=variant_2, field_label="Pinion 'K' Value (over 3 Teeth)", field_type="numeric_range",
        required=False, unit="mm", min_value=78.470, max_value=78.491, decimal_precision=3,
        standard_value="78.470 - 78.491 mm, Condemning limit = 78.129mm", page_number=p)
    add("gear_variant_2_bull_gear_k", parent=variant_2, field_label="Bull Gear 'K' Value (over 9 Teeth)", field_type="numeric_range",
        required=False, unit="mm", min_value=260.958, max_value=260.992, decimal_precision=3,
        standard_value="260.958 - 260.992 mm, Condemning limit = 260.451mm", page_number=p)
    add("gear_variant_2_backlash", parent=variant_2, field_label="Backlash", field_type="numeric_range",
        required=False, unit="mm", min_value=0.254, max_value=0.458, decimal_precision=3,
        standard_value="0.254 mm (Min) - 0.458 mm (Max)", page_number=p)

    variant_3 = add("gear_variant_21t_pinion", parent=gear_kvalue, field_label="Variant: 21T Pinion (SKDP-3847) / 107T Bull Gear (SKDP-3848)",
                     field_type="group", required=False, page_number=p)
    add("gear_variant_3_pinion_k", parent=variant_3, field_label="Pinion 'K' Value (over 4 Teeth)", field_type="numeric_range",
        required=False, unit="mm", min_value=77.530, max_value=77.58, decimal_precision=3,
        standard_value="77.530 - 77.58 mm, Condemning limit = 77.115mm", page_number=p)
    add("gear_variant_3_bull_gear_k", parent=variant_3, field_label="Bull Gear 'K' Value (over 15 Teeth)", field_type="numeric_range",
        required=False, unit="mm", min_value=317.09, max_value=317.17, decimal_precision=3,
        standard_value="317.09 - 317.17 mm, Condemning limit = 316.494mm", page_number=p)
    add("gear_variant_3_backlash", parent=variant_3, field_label="Backlash", field_type="numeric_range",
        required=False, unit="mm", min_value=0.290, max_value=0.490, decimal_precision=3,
        standard_value="0.290 mm (Min) - 0.490 mm (Max)", page_number=p)

    add(
        "trial_run_confirmation", field_label="If Backlash Within Range, Trial Run (2nd State) for Half an Hour",
        field_type="boolean", required=True,
        standard_value="Procedure of wheel run test of traction motor type 6FRA6068 to be followed as per CLW's letter no. CLW/TM/8021 dated 01.12.2020",
        negative_values="false", page_number=p,
    )
    add(
        "latest_drawing_associated_components", field_label="Use of Latest Drawing for Associated Components (11 items)",
        field_type="boolean", required=True,
        standard_value="As per letter no EL/3.2.172 dated 4/9/24 - enhances clearance between mating surface from min 0.25mm to 0.35mm (DE outer labyrinth & DE bearing cap)",
        negative_values="false", page_number=p,
    )

    add("compliance_smi_314", field_label="SMI-314: Use of Dial Snap Gauges with Least Count of 1 Micron for Measurement of Shaft Diameter",
        field_type="boolean", required=True, negative_values="false", page_number=p)
    add("compliance_smi_318", field_label="SMI-318: Use of Bore Gauges with Least Count of 1 Micron for Measurement of Internal Diameter of End Frame and Racer",
        field_type="boolean", required=True, negative_values="false", page_number=p)
    add("compliance_ms_478", field_label="MS-478: Adoption of TM Labyrinths as per Original Dimension Given by ABB",
        field_type="boolean", required=True, negative_values="false", page_number=p)
    add("compliance_ms_415", field_label="MS-415 Followed by Amnd. 1,2&3: To Ensure Adequate Interference Between Assembly Component",
        field_type="boolean", required=True, negative_values="false", page_number=p)
    add("compliance_smi_301", field_label="SMI-301: Use of Induction Heater for Heating of End Frames for Bearing Fitment",
        field_type="boolean", required=True, negative_values="false", page_number=p)

    add("overhaul_remarks", field_label="Remarks if Any", field_type="textarea", required=False, page_number=p)

    # ================= Page 6: Electrical tests =================
    p = 6
    winding_inductance = add(
        "overhaul_winding_inductance", field_label="Winding Inductance Luv, Lvw, Luw and Its Difference Between Phases at TM Terminal Box",
        field_type="group", required=False,
        standard_value="Difference should not be more than 0.015 millihenry at TM terminals, as per SMI-0262 dated 10.06.2010",
        validation_rule="absolute_difference", validation_threshold=0.015, page_number=p,
    )
    add("overhaul_winding_inductance_luv", parent=winding_inductance, field_label="Luv", field_type="number", required=True, unit="mH", page_number=p)
    add("overhaul_winding_inductance_lvw", parent=winding_inductance, field_label="Lvw", field_type="number", required=True, unit="mH", page_number=p)
    add("overhaul_winding_inductance_luw", parent=winding_inductance, field_label="Luw", field_type="number", required=True, unit="mH", page_number=p)

    add(
        "ir_stator_1kv_megger", field_label="Checking of Insulation Resistance of Stator with 1kV Megger",
        field_type="numeric_range", required=True, unit="MOhm", min_value=100.0, decimal_precision=1,
        standard_value="Min. 100 MOhm", page_number=p,
    )
    add(
        "ir_nde_bearing_1kv", field_label="Checking of Insulation Resistance of NDE Bearing Using 1 KV Insulation Test",
        field_type="numeric_range", required=True, unit="MOhm", min_value=50.0, decimal_precision=1,
        standard_value="Min 50 MOhm, as per SMI-0278", page_number=p,
    )

    no_load_run = add(
        "no_load_run_test_parameters", field_label="No Load Run Test Parameters of Assembled TM",
        field_type="group", required=False, page_number=p,
    )
    phase_current = add("no_load_run_phase_current", parent=no_load_run, field_label="Run TM with 3 Phase Supply (380-400V) and Measure Phase Current",
                         field_type="group", required=False, page_number=p)
    add("no_load_run_phase_current_u", parent=phase_current, field_label="U", field_type="number", required=True, unit="A", page_number=p)
    add("no_load_run_phase_current_v", parent=phase_current, field_label="V", field_type="number", required=True, unit="A", page_number=p)
    add("no_load_run_phase_current_w", parent=phase_current, field_label="W", field_type="number", required=True, unit="A", page_number=p)

    temp_rise_bearings = add("no_load_run_temp_rise_bearings", parent=no_load_run, field_label="Temperature Rise of Bearings",
                              field_type="group", required=False, standard_value="Max. 40C above ambient", page_number=p)
    add("no_load_run_temp_rise_de", parent=temp_rise_bearings, field_label="DE Side", field_type="numeric_range",
        required=True, unit="C", max_value=40.0, decimal_precision=1, standard_value="Max. 40C above ambient", page_number=p)
    add("no_load_run_temp_rise_nde", parent=temp_rise_bearings, field_label="NDE Side", field_type="numeric_range",
        required=True, unit="C", max_value=40.0, decimal_precision=1, standard_value="Max. 40C above ambient", page_number=p)

    spm_reading = add("no_load_run_spm_reading", parent=no_load_run, field_label="SPM Reading",
                       field_type="group", required=False, standard_value="Condition (Green, Red, Yellow)", page_number=p)
    add("no_load_run_spm_de", parent=spm_reading, field_label="DE Side", field_type="select",
        options="Green, Yellow, Red", required=True, standard_value="Green", negative_values="Red", page_number=p)
    add("no_load_run_spm_nde", parent=spm_reading, field_label="NDE Side", field_type="select",
        options="Green, Yellow, Red", required=True, standard_value="Green", negative_values="Red", page_number=p)

    temp_sensor_assembly = add(
        "temp_sensor_assembly_cold_condition", field_label="Checking of Temperature Sensor Assembly (Cold Condition)",
        field_type="group", required=False, page_number=p,
    )
    add("temp_sensor_assembly_ir_500v", parent=temp_sensor_assembly, field_label="IR Value with 500V Megger",
        field_type="numeric_range", required=True, unit="MOhm", min_value=50.0, decimal_precision=1,
        standard_value="> 50 Mega Ohm", page_number=p)
    add("temp_sensor_assembly_resistance_elements", parent=temp_sensor_assembly, field_label="Resistance of Elements",
        field_type="number", required=False, unit="Ohm",
        standard_value="Calculate the temperature which should not vary more than 2C", page_number=p)

    # ================= Page 7: Must Change Item in IOH Schedule =================
    p = 7
    must_change = add("must_change_item_ioh_schedule", field_label="Must Change Item in IOH Schedule", field_type="group", required=False, page_number=p)
    for key, label in [
        ("pinion", "Pinion"),
        ("bearing_de_nde", "Bearing (DE/NDE)"),
        ("o_ring_de_side_end_shield", "'O' Ring (DE Side End Shield)"),
        ("spring_washer_20mm", "Spring Washer 20 MM"),
        ("spring_washer_10mm", "Spring Washer 10MM"),
        ("spring_washer_12mm", "Spring Washer 12MM"),
        ("spring_washer_8mm", "Spring Washer 8MM"),
        ("spring_washer_6mm", "Spring Washer 6MM"),
        ("temp_sensor_gasket", "Temp. Sensor Gasket"),
        ("junction_box_gasket", "Junction Box Gasket"),
        ("sealing_ring_de_nde", "Sealing Ring (DE/NDE)"),
        ("grease_servo_plex_hs120", "Grease (Servo Plex HS120)"),
    ]:
        add(f"must_change_{key}", parent=must_change, field_label=label, field_type="select",
            options="Changed, Original", required=True, page_number=p)

    # Module 32.2: "Staff" (the technician-typed signature field) deliberately NOT seeded here -
    # same rationale as the GC template's "Technician" field. "Supervisor" is intentionally left
    # as-is - it was not named in the module's field list.
    add("overhaul_supervisor_name", field_label="Supervisor", field_type="text", required=False, page_number=p)


if __name__ == "__main__":
    run_seed(
        equipment_code="TM- 3Ph", template_code="21", technology="3_PHASE", maintenance_type="OVERHAUL",
        template_name="Checksheet for Traction Motor (Overhaul)",
        description="Assembly/Fitment of TM type 6FRA6068 (New/Overhauling) - BL REV.05/06/2025.",
        build_fn=build,
    )
