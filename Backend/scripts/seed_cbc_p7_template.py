"""
Module 40: seeds the CBC_P7 ("H" Type Centre Buffer Coupler Assembly, WAP-7, 3-Phase, M4-HR
section) checksheet template.

Run once: `venv/bin/python scripts/seed_cbc_p7_template.py`

Source: page 22 of the supplied WAP-7 checksheet - "'H' Type Centre Buffer Coupler (CBC)
Assembly", recorded once per coupler (CBC-1/CBC-2). Deliberately independent from the WAG9HC
"E" Type CBC Assembly template (seed_cbc_assembly_template.py) - WAP-7 uses a completely
different coupler type (H-Type vs E-Type) with its own, much more detailed 20-item inspection
procedure (gauge-based knuckle/coupler-head checks, supporting device checks, hand brake
checks) that has no equivalent on the WAG9HC sheet at all. Do not merge with the E-Type template.
"""
from _m4hr_template_helpers import add_final_remarks, run_seed

MPT_PARTS = [
    ("coupler_body", "CBC Coupler Body"),
    ("knuckle", "Knuckle"),
    ("knuckle_pin", "Knuckle Pin"),
    ("clevis", "Clevis"),
    ("clevis_pin", "Clevis Pin"),
]


def build(add):
    for cbc in ("CBC-1", "CBC-2"):
        cbc_key = cbc.lower().replace("-", "_")
        cbc_group = add(f"cbc_p7_{cbc_key}", field_label=cbc, field_type="group", required=False)

        add(f"cbc_p7_{cbc_key}_number", parent=cbc_group, field_label="CBC Number (Make & Year)",
            field_type="text", required=True, standard_value="Noted")

        mpt_group = add(f"cbc_p7_{cbc_key}_mpt_crack_check", parent=cbc_group, field_label="Check for Any Crack "
            "by MPT Test of CBC Assembly Items", field_type="group", required=False)
        for key, label in MPT_PARTS:
            add(f"cbc_p7_{cbc_key}_mpt_{key}", parent=mpt_group, field_label=label, field_type="select",
                options="OK, Crack Found", required=True, standard_value="OK", negative_values="Crack Found")

        coupler_head_group = add(f"cbc_p7_{cbc_key}_coupler_head", parent=cbc_group, field_label="Coupler Head",
                                  field_type="group", required=False)
        add(f"cbc_p7_{cbc_key}_telltail_check", parent=coupler_head_group, field_label="Check Tell-Tail of the "
            "Coupler Head After Coupling", field_type="select", options="OK, Not OK", required=True,
            standard_value="OK", negative_values="Not OK")
        add(f"cbc_p7_{cbc_key}_cotter_pin_check", parent=coupler_head_group, field_label="Check Cotter Pin-6.3 "
            "Is Installed", field_type="select", options="OK, Not OK", required=True, standard_value="OK",
            negative_values="Not OK")
        add(f"cbc_p7_{cbc_key}_visual_wear_plate_check", parent=coupler_head_group, field_label="Visual Checks "
            "for External Damage, Condition of Wear Plate on Shank", field_type="select", options="OK, Not OK",
            required=True, standard_value="OK", negative_values="Not OK")
        add(f"cbc_p7_{cbc_key}_condemning_limit_gauge_check", parent=coupler_head_group, field_label="Check Gap "
            "Between Coupler Head and Knuckle With Condemning Limit Gauge (Part Drawing No.-228965W14) - if Wear "
            "Out Unacceptable Replace Knuckle Etc. as Advised in the Maintenance Manual", field_type="select",
            options="OK, Not OK", required=True, standard_value="OK", negative_values="Not OK")
        add(f"cbc_p7_{cbc_key}_inspector_contour_gauge_check", parent=coupler_head_group, field_label="Check by "
            "Inspector Contour Gauge (Knuckle Profile Gauge, GO Gauge)", field_type="select", options="OK, Not OK",
            required=True, standard_value="OK", negative_values="Not OK")
        add(f"cbc_p7_{cbc_key}_knuckle_wear_stretch_gauge_check", parent=coupler_head_group, field_label="Check "
            "Wear & Stretch of Knuckle by Using Knuckle Nose Wear & Stretch Limit Gauge", field_type="select",
            options="OK, Not OK", required=True, standard_value="OK", negative_values="Not OK")
        add(f"cbc_p7_{cbc_key}_coupler_head_distortion_check", parent=coupler_head_group, field_label="Check "
            "Distortion of the Coupler Head by Using Aligning Wing Limit Gauge", field_type="select",
            options="OK, Not OK", required=True, standard_value="OK", negative_values="Not OK")
        add(f"cbc_p7_{cbc_key}_vertical_height_nogo_check", parent=coupler_head_group, field_label="Checking Wear "
            "& Distortion of Coupler Head Using Vertical Height Aligning Wing Pocket & Guard Arm Gauge (No-Go "
            "Gauge)", field_type="select", options="OK, Not OK", required=True, standard_value="OK",
            negative_values="Not OK")
        add(f"cbc_p7_{cbc_key}_vertical_height_go_check", parent=coupler_head_group, field_label="Checking "
            "Vertical Height Alignment & Guard Arm of Coupler in New Condition Using Vertical Height Aligning "
            "Wing Pocket & Guard Arm Gauge (Go Gauge)", field_type="select", options="OK, Not OK", required=True,
            standard_value="OK", negative_values="Not OK")
        add(f"cbc_p7_{cbc_key}_anti_creep_test", parent=coupler_head_group, field_label="Check Working of CBC & "
            "Anti Creep Test", field_type="select", options="OK, Not OK", required=True, standard_value="OK",
            negative_values="Not OK")
        add(f"cbc_p7_{cbc_key}_operating_handle", parent=coupler_head_group, field_label="Check Condition & "
            "Proper Working of CBC Operating Handle", field_type="select", options="OK, Not OK", required=True,
            standard_value="OK", negative_values="Not OK")
        add(f"cbc_p7_{cbc_key}_yoke_draft_gear", parent=coupler_head_group, field_label="Check for Any Crack and "
            "Damage in Yoke & Draft Gear", field_type="select", options="OK, Crack/Damage Found", required=True,
            standard_value="OK", negative_values="Crack/Damage Found")

        supporting_device_group = add(f"cbc_p7_{cbc_key}_supporting_device", parent=cbc_group,
                                       field_label="Supporting Device", field_type="group", required=False)
        add(f"cbc_p7_{cbc_key}_external_damage_visual", parent=supporting_device_group, field_label="Visual Check "
            "for External Damage", field_type="select", options="OK, Not OK", required=True, standard_value="OK",
            negative_values="Not OK")
        add(f"cbc_p7_{cbc_key}_nyloc_nut_height_check", parent=supporting_device_group, field_label="Tighten the "
            "M16 Nyloc Nut & Check Height 165.0±1mm Both Sides Near the Bolts", field_type="select",
            options="OK, Not OK", required=True, standard_value="OK", negative_values="Not OK")
        add(f"cbc_p7_{cbc_key}_shank_lateral_movement", parent=supporting_device_group, field_label="Check Free "
            "Lateral Movement of CBC Shank", field_type="select", options="OK, Not OK", required=True,
            standard_value="OK", negative_values="Not OK")
        add(f"cbc_p7_{cbc_key}_hand_brake_make", parent=supporting_device_group, field_label="Hand Brake Make "
            "(Modified/Un-Modified)", field_type="select", options="Modified, Un-Modified", required=True,
            standard_value="Modified/Un-modified")
        add(f"cbc_p7_{cbc_key}_hand_brake_removed_overhauled", parent=supporting_device_group, field_label="Hand "
            "Brake to Be Remove for Overhauling", field_type="select", options="Remove and Overhauled, Not Done",
            required=True, standard_value="Remove and overhauled", negative_values="Not Done")
        add(f"cbc_p7_{cbc_key}_hand_brake_application_release", parent=supporting_device_group, field_label="Ensure "
            "Proper Application and Release of Hand Brake in Loco", field_type="select",
            options="Ensured, Not Ensured", required=True, standard_value="Ensured", negative_values="Not Ensured")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="CBC_P7", template_code="99", technology="3_PHASE",
        template_name='Checksheet for "H" Type Centre Buffer Coupler Assembly (WAP-7)',
        description="'H' Type Centre Buffer Coupler (CBC) Assembly checksheet - WAP-7, 3-Phase - M4-HR section.",
        build_fn=build,
    )
