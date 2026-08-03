"""
Module 41: seeds the BL_Conv (BL Box, WAP-4/Conventional locomotives, M1-HR section) checksheet
template.

Run once: `venv/bin/python scripts/seed_bl_box_conv_template.py`

Source: "TOH & IOH For Conv. BL Box.pdf" - "Performa of Check Points of BL Box O/H", a 12-item
overhaul checklist, a 3-item testing performa, and an experience-based "Must Change Item" log (the
sheet's own filled example replaced the 2 limit switches BLDJ/BLRDJ/BLPRR/BLPRF/BLPRD/BLVMT with a
Siemens make in 2024/2025).

The source form is one BL Box per cab (its header shows "LOCO NO- 22704 CAB-1") - the Android
workflow has no separate cab-selection step, so a "Cab" field is modelled here (matching the same
pattern already used for per-cab equipment in M4-HR, e.g. CBC-1/CBC-2) so the technician records
which physical BL Box this checksheet instance covers. Per the module's "Do NOT create fields for
Loco Number/Technician/Supervisor Name/Signature" rule, the sheet's own "LOCO NO" and "Sign. of
Tech"/"Signature of Supervisor" lines are intentionally not modelled - those duplicate metadata the
application already auto-captures and prints in the PDF.
"""
from _aux_template_helpers import add_final_remarks, run_seed


def build(add):
    add("cab", field_label="Cab", field_type="select", options="Cab-1, Cab-2", required=False)
    add("bl_sr_no", field_label="BL Sr. No.", field_type="text", required=True, standard_value="Noted")
    add("date_of_providing", field_label="Date of Providing/In Position Attending", field_type="date",
        required=False)
    add("overhauling_date", field_label="O/H Date", field_type="date", required=True)

    checks_group = add("check_points", field_label="Check Points", field_type="group", required=False)
    add("program_switch_dismantle_clean", parent=checks_group, field_label="Dismantle All Knobs, Springs and "
        "Main Programme Switch & Clean With Petrol and Dry Air Jet", field_type="select",
        options="Cleaned, Not Cleaned", required=True, standard_value="Cleaned", negative_values="Not Cleaned")
    add("knobs_crack_damage_check", parent=checks_group, field_label="Check Knobs for Any Crack or Damage",
        field_type="select", options="No Crack, Crack Found", required=True, standard_value="No Crack",
        negative_values="Crack Found")
    add("knob_spring_shaft_play_check", parent=checks_group, field_label="Check Knob & Spring Holding Shaft for "
        "Play - if Play Notice Roll Pin or Knob to Be Change", field_type="select",
        options="No Play, Play Found", required=True, standard_value="No Play", negative_values="Play Found")
    add("program_switch_dismantle_assemble", parent=checks_group, field_label="Programme Switch Dismantle Clean "
        "and Assemble", field_type="select", options="Done, Not Done", required=True, standard_value="Done",
        negative_values="Not Done")
    add("knobs_profile_check", parent=checks_group, field_label="Check the Profile of All Knobs",
        field_type="select", options="OK, Worn Out", required=True, standard_value="OK",
        negative_values="Worn Out")
    add("limit_switches_change", parent=checks_group, field_label="Change the Must-Change Limit Switches "
        "(BLDJ, BLRDJ, BLPRR, BLPRF, BLPRD, BLVMT)", field_type="textarea", required=True,
        standard_value="New/Serviceable")
    add("limit_switches_paralleling", parent=checks_group, field_label="Paralleling of Limit Switches BLDJ, "
        "BLRDJ, BLPRF, BLPRR, BLVMT (NO Interlock), BLPRD (NC Interlock)", field_type="select",
        options="Done, Not Done", required=True, standard_value="Done", negative_values="Not Done")
    add("bl_box_key_slot_slackness", parent=checks_group, field_label="Check Slackness of BL Box Key in Slot - "
        "if Notice Change the Key", field_type="select", options="No Slackness, Slackness Found", required=True,
        standard_value="No Slackness", negative_values="Slackness Found")
    add("cable_damage_lug_check", parent=checks_group, field_label="Check Cable for Any Damage or Lug Uncouple",
        field_type="select", options="Good, Damage Found", required=True, standard_value="Good",
        negative_values="Damage Found")
    add("lever_roller_free_movement", parent=checks_group, field_label="Check Roller of Lever for Free "
        "Movement", field_type="select", options="Free, Not Free", required=True, standard_value="Free",
        negative_values="Not Free")
    add("split_pins_condition", parent=checks_group, field_label="All Split Pin to Be Split Out Condition",
        field_type="select", options="Split Out, Not Split Out", required=True, standard_value="Split Out",
        negative_values="Not Split Out")
    add("interlocking_spring_tension_check", parent=checks_group, field_label="Check Spring Tension of Inter "
        "Locking Mechanism & Ensure Proper Interlocking - Replace the Defective Spring", field_type="select",
        options="Good, Not Good", required=True, standard_value="Good", negative_values="Not Good")
    add("inner_locking_devices_lubrication", parent=checks_group, field_label="Lubricate All the Points of "
        "Articulation of Inner Locking Devices", field_type="select", options="Done, Not Done", required=True,
        standard_value="With Servo Press 150 Oil", negative_values="Not Done")

    testing_group = add("testing", field_label="Testing", field_type="group", required=False)
    add("bl_box_key_locking_unlocking", parent=testing_group, field_label="Check Locking and Unlocking of BL "
        "Box Key", field_type="select", options="OK, Not OK", required=True, standard_value="OK",
        negative_values="Not OK")
    add("limit_switches_continuity", parent=testing_group, field_label="Check Continuity of Limit Switches by "
        "Operating the Knobs", field_type="select", options="OK, Not OK", required=True, standard_value="OK",
        negative_values="Not OK")
    add("limit_switches_crushing", parent=testing_group, field_label="Check the Crushing of Limit Switches",
        field_type="select", options="OK, Not OK", required=True, standard_value="OK", negative_values="Not OK")

    must_change_group = add("must_change_item", field_label="Must Change Item of BL (Experience Based)",
                             field_type="group", required=False,
                             standard_value="2 Nos. Limit Switches BLDJ, BLRDJ, BLPRR, BLPRF, BLPRD, BLVMT")
    add("must_change_status", parent=must_change_group, field_label="Change/Not Change", field_type="select",
        options="Changed, Not Changed", required=False)
    add("must_change_make", parent=must_change_group, field_label="Make", field_type="text", required=False)
    add("must_change_mfg_year", parent=must_change_group, field_label="Mfg/Year", field_type="text",
        required=False)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="BL_Conv", template_code="122", technology="CONVENTIONAL",
        template_name="Checksheet for BL Box",
        description="BL Box O/H checksheet - Conventional - M1-HR section.",
        build_fn=build,
    )
