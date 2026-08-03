"""
Module 41: seeds the MP_Conv (Master Controller (MP), WAP-4/Conventional locomotives, M1-HR
section) checksheet template.

Run once: `venv/bin/python scripts/seed_master_controller_mp_conv_template.py`

Source: "TOH & IOH For Conv. Master Controller (MP).pdf" - "Performa of Check Points of Master
Controller (MP)", a 14-item overhaul checklist, a 7-item testing performa (I/L roller-cam gap,
LED continuity, conk-pin shorting, Q52 branch I/L progression/regression, main drum
forward/reverse interlocks and smoothness), and an experience-based "Must Change Item of MP" log
(05 Nos. auxiliary cam switched interlock, new SCSC make).

The source form is one Master Controller per cab (both supplied pages show the identical
performa, once for CAB-1 and once for CAB-2) - the Android workflow has no separate
cab-selection step, so a "Cab" field is modelled here (same pattern as BL_Conv) so the technician
records which physical MP this checksheet instance covers. Per the module's "Do NOT create fields
for Loco Number/Technician/Supervisor Name/Signature" rule, the sheet's own "Loco No." and "Sign.
of Tech"/"Signature of Supervisor" lines are intentionally not modelled.
"""
from _aux_template_helpers import add_final_remarks, run_seed


def build(add):
    add("cab", field_label="Cab", field_type="select", options="Cab-1, Cab-2", required=False)
    add("mp_sr_no", field_label="MP Sr. No.", field_type="text", required=True, standard_value="Noted")
    add("date_of_providing", field_label="Date of Providing", field_type="date", required=False)
    add("overhauling_date", field_label="Date of O/H", field_type="date", required=True)

    checks_group = add("check_points", field_label="Check Points", field_type="group", required=False)
    add("levers_springs_il_dismantle_clean", parent=checks_group, field_label="Dismantle All Levers, Springs "
        "and I/L & Clean With Petrol or Kerosene", field_type="select", options="Cleaned, Not Cleaned",
        required=True, standard_value="Cleaned", negative_values="Not Cleaned")
    add("lever_crack_damage_check", parent=checks_group, field_label="Check Lever for Crack or Damage",
        field_type="select", options="No Crack, Crack Found", required=True, standard_value="No Crack",
        negative_values="Crack Found")
    add("lever_spring_shaft_play_check", parent=checks_group, field_label="Check Lever & Spring Holding Shaft "
        "for Play - if Play Notice Roll Pin to Be Change", field_type="select", options="No Play, Play Found",
        required=True, standard_value="No Play", negative_values="Play Found")
    add("il_condition_check", parent=checks_group, field_label="Check I/L Condition (for Pit Mark on Tips & "
        "Roller Damage)", field_type="select", options="Good, Not Good", required=True, standard_value="Good",
        negative_values="Not Good")
    add("cam_switch_contact_pressure", parent=checks_group, field_label="Check Contact Pressure of Cam Switch",
        field_type="numeric_range", required=True, unit="gm", min_value=180.0, max_value=220.0,
        decimal_precision=0)
    add("mci_cam_slackness_check", parent=checks_group, field_label="Check Slackness of MCI Cam - if Notice "
        "Tapered Split Pin to Be Change", field_type="select", options="No Slackness, Slackness Found",
        required=True, standard_value="No Slackness", negative_values="Slackness Found")
    add("main_handle_mps_handle_slackness_check", parent=checks_group, field_label="Check Slackness of Main "
        "Handle & MPS Handle - if Notice Tapered Split Pin to Be Change", field_type="select",
        options="No Slackness, Slackness Found", required=True, standard_value="No Slackness",
        negative_values="Slackness Found")
    add("cable_damage_lug_check", parent=checks_group, field_label="Check Cable for Any Damage or Lug Uncouple",
        field_type="select", options="Good, Damage Found", required=True, standard_value="Good",
        negative_values="Damage Found")
    add("lever_roller_free_movement", parent=checks_group, field_label="Check Roller of Lever for Free "
        "Movement", field_type="select", options="Free, Not Free", required=True, standard_value="Free",
        negative_values="Not Free")
    add("tapered_pins_condition", parent=checks_group, field_label="All Tapered Pin to Be Split Out Condition",
        field_type="select", options="Split Out, Not Split Out", required=True, standard_value="Split Out",
        negative_values="Not Split Out")
    add("interlocking_spring_tension_check", parent=checks_group, field_label="Check Spring Tension of Inter "
        "Locking Mechanism & Ensure Proper Interlocking - Replace the Defective Spring", field_type="select",
        options="Good, Not Good", required=True, standard_value="Good", negative_values="Not Good")
    add("rollers_mci_cam_greasing", parent=checks_group, field_label="Provide Grease on the Rollers & MCI Cam",
        field_type="select", options="Provided, Not Provided", required=True, standard_value="Provided",
        negative_values="Not Provided")
    add("inner_locking_devices_lubrication", parent=checks_group, field_label="Lubricate All the Points of "
        "Articulation of Inner Locking Devices", field_type="select", options="Done, Not Done", required=True,
        standard_value="With Servo Press 150 Oil", negative_values="Not Done")
    add("latherised_paper_condition_check", parent=checks_group, field_label="To Check Latherised Paper "
        "Condition Inside the Cover", field_type="select", options="Good, Not Good", required=True,
        standard_value="Good", negative_values="Not Good")

    testing_group = add("testing", field_label="Testing", field_type="group", required=False)
    add("il_roller_cam_gap_check", parent=testing_group, field_label="Check Gap Between I/L Roller & Cam in "
        "Close Position", field_type="select", options="Minimum, Not Minimum", required=True,
        standard_value="Minimum", negative_values="Not Minimum")
    add("led_il_conk_pin_continuity", parent=testing_group, field_label="Continuity to Be Check by LED From "
        "I/L to Conk Pin", field_type="select", options="OK, Not OK", required=True, standard_value="OK",
        negative_values="Not OK")
    add("conk_pin_body_shorting_check", parent=testing_group, field_label="All Conk Pin Continuity to Be Check "
        "With Body for Any Shorting", field_type="select", options="No Shorting, Shorting Found", required=True,
        standard_value="No Shorting", negative_values="Shorting Found")
    add("q52_branch_il_progression_regression", parent=testing_group, field_label="Q52 Branch I/L (2nd No I/L) "
        "Advanced Close With Respect to 1st & 2nd I/L During Progression & Regression Respectively",
        field_type="select", options="Advance Close, Not Advance Close", required=True,
        standard_value="Advance Close", negative_values="Not Advance Close")
    add("main_drum_forward_reverse_interlock", parent=testing_group, field_label="Main Drum (Driving Wheel) "
        "Will Not Move Until MPJ Key Is Put on Forward or Reverse", field_type="select",
        options="Not Move, Moves", required=True, standard_value="Not Move", negative_values="Moves")
    add("mpj_operation_smoothness_check", parent=testing_group, field_label="MPJ Operation Forward Zero, No "
        "Shorting Reverse Must Be Smooth", field_type="select", options="Smooth Working, Not Smooth",
        required=True, standard_value="Smooth Working", negative_values="Not Smooth")
    add("main_drum_plus_minus_stop_check", parent=testing_group, field_label="Main Drum (Driving Wheel) Should "
        "Not Stopped at the Position of '+' or '-'", field_type="select", options="Not Stopped, Stopped",
        required=True, standard_value="Not Stopped", negative_values="Stopped")

    must_change_group = add("must_change_item", field_label="Must Change Item of MP (Experience Based)",
                             field_type="group", required=False,
                             standard_value="05 Nos. Auxiliary Cam Switched Interlock Location Q52, Q46, "
                                            "Progression, Regression, EEC")
    add("must_change_status", parent=must_change_group, field_label="Change/Not Change", field_type="select",
        options="New, Not Changed", required=False)
    add("must_change_make", parent=must_change_group, field_label="Make", field_type="text", required=False)
    add("must_change_mfg_year", parent=must_change_group, field_label="Mfg/Year", field_type="text",
        required=False)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="MP_Conv", template_code="124", technology="CONVENTIONAL",
        template_name="Checksheet for Master Controller (MP)",
        description="Master Controller (MP) O/H checksheet - Conventional - M1-HR section.",
        build_fn=build,
    )
