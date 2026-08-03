"""
Module 41 (Phase 2): seeds the M-Controller (Master Controller, 3-Phase locomotives, M1-HR
section) checksheet template.

Run once: `venv/bin/python scripts/seed_master_controller_3phase_template.py`

Source: "TOH & IOH For 3-Phase Master Controller.pdf" - "Performa for TOH & IOH Maintenance
Activities for Three Phase Master Controller", a 13-item checklist plus a 5-position Potentiometer
value table (Neutral/Minimum/1-3rd/2-3rd/Maximum), each position with its own Traction (mA) and
Braking (mA) standard range - a genuine per-position measurement grid, preserved at full
granularity per the module's "preserve grouped measurements" rule (each position is a distinct
electrical operating point, not a reference lookup a technician picks one representative value
from).

The source form is one Master Controller per cab (header shows "Provided in Loco No./Sch/Cab &
date: ... CAB-2") - the Android workflow has no separate cab-selection step, so a "Cab" field is
modelled here (same pattern already used in M1-HR Conventional for BL_Conv/MP_Conv). Per the
module's "Do NOT create fields for Loco Number/Technician/Supervisor Name/Signature" rule, the
sheet's own "Removed From/Provided In Loco No. & Date" and "Overhauled & Tested By" lines are
intentionally not modelled.
"""
from _aux_template_helpers import add_final_remarks, run_seed

POSITIONS = [
    ("neutral", "Neutral", 1.75, 2.25, 1.75, 2.25),
    ("minimum", "Minimum", 3.90, 4.90, 3.40, 4.40),
    ("one_third", "1/3rd", 8.60, 9.60, 8.20, 9.20),
    ("two_third", "2/3rd", 14.60, 15.60, 14.00, 15.20),
    ("maximum", "Maximum", 19.75, 20.25, 19.75, 20.25),
]


def build(add):
    add("cab", field_label="Cab", field_type="select", options="Cab-1, Cab-2", required=False)
    add("mc_sn", field_label="Master Controller S.N.", field_type="text", required=True, standard_value="Noted")
    add("mc_make", field_label="Make", field_type="text", required=True, standard_value="Noted")
    add("mc_mfg_year", field_label="Mfg.", field_type="text", required=True, standard_value="Noted")

    checks_group = add("check_points", field_label="Maintenance Activities During Schedule", field_type="group",
                        required=False)
    add("screw_connection_tightness_check", parent=checks_group, field_label="Ensure Tightness of All Screw & "
        "Connection", field_type="select", options="OK, Loose Found", required=True,
        standard_value="Not in Loose Condition", negative_values="Loose Found")
    add("gear_cam_play_check", parent=checks_group, field_label="Check Play in Gear & Cam", field_type="select",
        options="Slight Play, No Play/Excess Play", required=True, standard_value="Should Be Slight Play")
    add("program_switch_locking_lever_check", parent=checks_group, field_label="Ensure the Operation of Program "
        "Switch & Locking Lever", field_type="select", options="Free, Not Free", required=True,
        standard_value="Should Be Free", negative_values="Not Free")
    add("program_switch_circlip_condition_check", parent=checks_group, field_label="Ensure the Proper Condition "
        "of Circlip in Program Switch", field_type="select", options="OK, Not OK", required=True,
        standard_value="Should Exist & Rotate Freely at Groove", negative_values="Not OK")
    add("gears_greasing", parent=checks_group, field_label="Apply Grease in Gears", field_type="select",
        options="Done, Not Done", required=True, standard_value="MP-3 Grease", negative_values="Not Done")
    add("throttle_movement_test", parent=checks_group, field_label="Ensure Throttle Movement Test",
        field_type="select", options="OK, Obstruction Found", required=True,
        standard_value="Throttle Must Move Smoothly in TE & BE Region Without Any Obstruction")
    add("direction_movement_test", parent=checks_group, field_label="Ensure Direction Movement Test",
        field_type="select", options="OK, Not OK", required=True,
        standard_value="Direction Handle (MPJ) Must Rotate in Forward & Reverse Direction")
    add("mechanical_interlock_test", parent=checks_group, field_label="Ensure Mechanical Inter-Lock Test Between "
        "Direction & Throttle Handle", field_type="select", options="OK, Not OK", required=True,
        standard_value="Throttle Should Not Move if Direction Switch Is in Zero Position; if Direction Selected "
                        "in Forward, Throttle Must Move in TE and BE Region")
    add("pin13_circular_connector_check", parent=checks_group, field_label="Ensure the Proper Condition of 13 "
        "Pin Circular Connector", field_type="select", options="OK, Bend/Loose", required=True,
        standard_value="Pin Should Not Be in Bend Condition & Loose", negative_values="Bend/Loose")
    add("pin09_sub_d_connector_check", parent=checks_group, field_label="Ensure the Proper Condition of 09 Pin "
        "Sub D Connector", field_type="select", options="OK, Bend/Loose", required=True,
        standard_value="Pin Should Not Be in Bend Condition & Loose", negative_values="Bend/Loose")
    add("dowel_pin_intactness_check", parent=checks_group, field_label="Ensure the Intactness of Dowel Pin",
        field_type="select", options="Intact, Not Intact", required=True, standard_value="Should Be Intact",
        negative_values="Not Intact")
    add("split_pin_dowel_pin_check", parent=checks_group, field_label="Ensure the Split Pin Inside the Dowel Pin",
        field_type="select", options="Provided, Not Provided", required=True,
        standard_value="Should Be in Provided Condition", negative_values="Not Provided")
    add("potentiometer_value_check", parent=checks_group, field_label="Examine the Potentiometer Value",
        field_type="select", options="Mentioned in the Given Table, Not OK", required=True,
        standard_value="As per OEM Manual & CLW Specification No. CLW/ES/3/0031, Alt 'H'",
        authority_reference="CLW/ES/3/0031, Alt 'H'")

    pot_group = add("potentiometer_table", field_label="Potentiometer Value Table", field_type="group",
                     required=False)
    for key, label, t_lo, t_hi, b_lo, b_hi in POSITIONS:
        pos_group = add(f"pot_{key}", parent=pot_group, field_label=label, field_type="group", required=False)
        add(f"pot_{key}_traction_ma", parent=pos_group, field_label="Traction (mA)", field_type="numeric_range",
            required=True, unit="mA", min_value=t_lo, max_value=t_hi, decimal_precision=2)
        add(f"pot_{key}_braking_ma", parent=pos_group, field_label="Braking (mA)", field_type="numeric_range",
            required=True, unit="mA", min_value=b_lo, max_value=b_hi, decimal_precision=2)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="M-Controller", template_code="129", technology="3_PHASE",
        template_name="Checksheet for Master Controller",
        description="TOH & IOH maintenance checksheet for Three Phase Master Controller - M1-HR section.",
        build_fn=build,
    )
