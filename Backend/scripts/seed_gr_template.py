"""
Module 34: seeds the GR (Tap Changer, Conventional, M8-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_gr_template.py`

Source: PERFORMA OF CHECK POINTS OF TAP CHANGER DURING AOH/IOH (ELS/TRS/BL/M-8/02),
plus the bundled "GR LEAD ANGLE" measurement sheet (33 notches, 0-32).
"""
from _aux_template_helpers import run_seed, add_final_remarks


def build(add):
    add("gr_tap_changer_no", field_label="Tap Changer No.", field_type="text", required=True)

    # --- 1. Check Points ---
    add("gr_oil_drained", field_label="Drain GR Oil", field_type="select",
        options="Drained, Not Drained", required=True, standard_value="To be checked",
        negative_values="Not Drained")
    add("gr_contact_arm_ring_drive_wheel_dismantled", field_label="Dismantle Contact Arm, Contact Ring, "
        "Drive Wheel Without Segment", field_type="select", options="Dismantled, Not Dismantled",
        required=True, standard_value="To be dismantled", negative_values="Not Dismantled")
    add("gr_contract_segment_tightness", field_label="Check Tightness of Contract Segment by Torque Wrench",
        field_type="select", options="Tight, Not Tight", required=True, standard_value="3.5 kg/cm2",
        negative_values="Not Tight", authority_reference="SMI-113")
    add("gr_pitting_contact_segment", field_label="Check Pitting Mark on Contact Segment",
        field_type="select", options="No Pitting, Pitting", required=True,
        standard_value="No pitting", negative_values="Pitting")
    add("gr_pitting_contact_roller", field_label="Check Pitting Mark on Contact Roller",
        field_type="select", options="No Pitting, Pitting", required=True,
        standard_value="No pitting", negative_values="Pitting", authority_reference="SMI-144")
    add("gr_pitting_contact_ring", field_label="Check Pitting Mark on Contact Ring",
        field_type="select", options="No Pitting, Pitting", required=True,
        standard_value="No pitting", negative_values="Pitting")
    add("gr_insulating_ring_tightness", field_label="Ensure Tightness of Insulating Ring by Torque Wrench",
        field_type="select", options="Done, Not Done", required=True, standard_value="0.9 kg/cm2",
        negative_values="Not Done", authority_reference="OEM manual")
    add("gr_side_flange_bearing_moved", field_label="Check Side Flange Bearing for Freely Moved",
        field_type="select", options="Freely Moved, Not Freely Moved", required=True,
        standard_value="Freely moved", negative_values="Not Freely Moved")
    add("gr_double_pole_bushing_thread", field_label="Check Thread Condition of Double Pole Bushing",
        field_type="select", options="Good, Damaged", required=True,
        standard_value="Good", negative_values="Damaged")
    add("gr_16th_tap_continuity", field_label="Check Electrical Continuity of Connection of 16th Tap",
        field_type="select", options="Continuity OK, No Continuity", required=True,
        standard_value="Continuity OK", negative_values="No Continuity")
    add("gr_safety_valve_tension", field_label="Check Safety Valve Tension by Hand",
        field_type="select", options="Lifted, Not Lifted", required=True,
        standard_value="To be lift", negative_values="Not Lifted", authority_reference="MS-187")
    add("gr_selector_cleaned_inspected", field_label="Clean the Selector With Jet Pump and Nylon Brushes; "
        "Inspect Contact Place for Electrical Glow Discharge / Hair Crack",
        field_type="select", options="Cleaned, Not Cleaned", required=True,
        standard_value="Cleaned", negative_values="Not Cleaned", authority_reference="OEM manual")
    add("gr_oil_flow_indicator_functioning", field_label="Ensure Functioning of Oil Flow Indicator",
        field_type="select", options="Functioning, Not Functioning", required=True,
        standard_value="Functioning", negative_values="Not Functioning")
    add("gr_phgr_working", field_label="Check Working of PHGR", field_type="select",
        options="Working, Not Working", required=True, standard_value="Working",
        negative_values="Not Working")
    add("gr_gauge_glass_oil_level", field_label="Check Oil Level of GR Gauge Glass",
        field_type="number", required=True, unit="C", standard_value="+40 C")

    # --- 2. Must Change Items ---
    must_change = add("gr_must_change_items", field_label="Must Change Items", field_type="group",
                      required=False)
    for key, label, reference in [
        ("gr_must_change_aoh_kit", "AOH Kit (AOH)", "RDSO TC 102 / PL No. 23970844"),
        ("gr_must_change_ioh_kit", "IOH Kit (IOH)", "RDSO TC 102 / PL No. 23970819"),
        ("gr_must_change_rubber_gasket_breather", "Rubber Gasket of Breather (AOH/IOH)", "RDSO TC 102 / Non stock"),
        ("gr_must_change_silica_gel", "Silica Gel (AOH/IOH)", "RDSO TC 102 / PL No. 81034878"),
        ("gr_must_change_cork_grain_breather", "Cork Grain of Breather (AOH/IOH)", "RDSO TC 102 / Non stock"),
        ("gr_must_change_gr_oil", "GR Oil (AOH/IOH)", "RDSO TC 102 / PL No. 80090280"),
    ]:
        add(key, parent=must_change, field_label=label, field_type="select",
            options="Changed, Not Changed", required=True, authority_reference=reference)

    # --- Items Change on Condition Base ---
    condition_base = add("gr_condition_base_items", field_label="Items Change on Condition Base",
                         field_type="group", required=False, standard_value="Condition basis")
    for key, label in [
        ("gr_bevel_gear", "Bevel Gear"),
        ("gr_coupling_shaft", "Coupling Shaft"),
        ("gr_lantern_gear", "Lantern Gear"),
    ]:
        add(key, parent=condition_base, field_label=label, field_type="select",
            options="Changed, Not Changed", required=True)

    # --- Measurements ---
    add("gr_contact_arm_roller_dia", field_label="Contact Arm Roller Dia.", field_type="numeric_range",
        required=True, unit="mm", min_value=17.0, max_value=18.0, decimal_precision=2,
        standard_value="17-18mm", authority_reference="SMI-144 (IOH)")
    add("gr_contact_arm_spring_height", field_label="Height of Contact Arm Spring",
        field_type="numeric_range", required=True, unit="mm", min_value=15.3, decimal_precision=2,
        standard_value="15.3mm Min.", authority_reference="SMI-82 (IOH)")
    add("gr_lantern_gear_roller_dia", field_label="Lantern Gear Roller Dia.", field_type="numeric_range",
        required=True, unit="mm", min_value=15.5, decimal_precision=2, standard_value="15.5mm Min.",
        authority_reference="SMI-144")
    add("gr_lantern_gear_roller_pin_dia", field_label="Lantern Gear Roller Pin Dia.",
        field_type="numeric_range", required=True, unit="mm", min_value=9.8, decimal_precision=2,
        standard_value="9.8mm Min.", authority_reference="SMI-144")

    angular_play = add("gr_angular_play", field_label="Angular Play", field_type="group", required=False)
    add("gr_angular_play_full_notch", parent=angular_play, field_label="Full Notch",
        field_type="numeric_range", required=True, unit="mm", min_value=3.0, max_value=10.0,
        decimal_precision=2, standard_value="3-10mm", authority_reference="OEM manual")
    add("gr_angular_play_between_notch", parent=angular_play, field_label="Between Notch",
        field_type="numeric_range", required=True, unit="mm", min_value=2.0, max_value=4.0,
        decimal_precision=2, standard_value="2-4mm", authority_reference="OEM manual")
    add("gr_play_contact_roller_guide_housing", parent=angular_play, field_label="Play Between Contact "
        "Roller Guide & Roller Housing", field_type="numeric_range", required=True, unit="mm",
        max_value=0.5, decimal_precision=2, standard_value="0.5mm Max.", authority_reference="SMI-144")
    add("gr_play_stepping_wheel_lantern_gear_pin", parent=angular_play, field_label="Play Between Stepping "
        "Wheel & Lantern Gear Pin", field_type="numeric_range", required=True, unit="mm",
        max_value=1.5, decimal_precision=2, standard_value="1.5mm Max.")
    add("gr_wear_contact_ring", parent=angular_play, field_label="Wear of Contact Ring",
        field_type="numeric_range", required=True, unit="mm", max_value=0.5, decimal_precision=2,
        standard_value="Below 0.5mm depth", authority_reference="SMI-144")
    add("gr_wear_contact_segment", parent=angular_play, field_label="Wear of Contact Segment",
        field_type="numeric_range", required=True, unit="mm", max_value=0.5, decimal_precision=2,
        standard_value="Below 0.5mm", authority_reference="SMI-144")
    add("gr_gap_contact_pin_insulating_ring", parent=angular_play, field_label="Gap Between Contact Pin "
        "& Insulating Ring", field_type="number", required=True, unit="mm", standard_value="0.5mm Std.",
        authority_reference="MS-157")

    add("gr_bdv_after_oil_filling", field_label="After Filling Oil BDV", field_type="numeric_range",
        required=True, unit="KV", min_value=48.0, decimal_precision=1, standard_value="48 KV Min.")

    # --- GR Lead Angle: 33 notches (0-32), each with Progression/Regression Making/Braking angle ---
    lead_angle = add("gr_lead_angle", field_label="GR Lead Angle", field_type="group", required=False,
                     standard_value="+/- 4.5 deg", authority_reference="Progression & Regression per notch")
    for notch in range(33):
        notch_group = add(f"gr_lead_angle_notch_{notch}", parent=lead_angle,
                          field_label=f"Notch {notch}", field_type="group", required=False,
                          standard_value="+/- 4.5 deg")
        add(f"gr_lead_angle_notch_{notch}_progression_making", parent=notch_group,
            field_label="Progression Making Angle", field_type="numeric_range", required=True,
            unit="deg", min_value=-4.5, max_value=4.5, decimal_precision=2, standard_value="+/- 4.5 deg")
        add(f"gr_lead_angle_notch_{notch}_progression_braking", parent=notch_group,
            field_label="Progression Braking Angle", field_type="numeric_range", required=True,
            unit="deg", min_value=-4.5, max_value=4.5, decimal_precision=2, standard_value="+/- 4.5 deg")
        add(f"gr_lead_angle_notch_{notch}_regression_making", parent=notch_group,
            field_label="Regression Making Angle", field_type="numeric_range", required=True,
            unit="deg", min_value=-4.5, max_value=4.5, decimal_precision=2, standard_value="+/- 4.5 deg")
        add(f"gr_lead_angle_notch_{notch}_regression_braking", parent=notch_group,
            field_label="Regression Braking Angle", field_type="numeric_range", required=True,
            unit="deg", min_value=-4.5, max_value=4.5, decimal_precision=2, standard_value="+/- 4.5 deg")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="GR", template_code="25", technology="CONVENTIONAL",
        template_name="Checksheet for GR (Tap Changer)",
        description="GR / Tap Changer (Conventional) checksheet - M8-HR section.",
        build_fn=build,
    )
