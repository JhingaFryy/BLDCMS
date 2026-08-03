"""
Module 41 (Phase 2): seeds the CHB (Cab Heater cum Blower, 3-Phase locomotives, M1-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_cab_heater_blower_3phase_template.py`

Source: "TOH & IOH Maintenance for Cab heater cum blower.pdf" - "Performa for TOH & IOH
Maintenance Activities for Cab Heater & Cab Heater cum Blower", a 14-item checklist covering the
Heater, Blower and Temperature Switch sub-components (each separately identified by Make/S.N./Mfg
Year), fuse/insulation checks, must-change bearing/flexible-duct items, and a terminal-connection
segregation modification (RDSO MS 408).

The source form is one Cab Heater cum Blower assembly per cab - the Android workflow has no
separate cab-selection step, so a "Cab" field is modelled here (same pattern already used for
BL_Conv/MP_Conv in M1-HR Conventional). Per the module's "Do NOT create fields for Loco
Number/Technician/Supervisor Name/Signature" rule, the sheet's own "Removed From/Provided In Loco
No. & Date" and "O/H & Tested By" lines are intentionally not modelled.
"""
from _aux_template_helpers import add_final_remarks, run_seed


def build(add):
    add("cab", field_label="Cab", field_type="select", options="Cab-1, Cab-2", required=False)
    add("overhauling_date", field_label="Date of Overhauling & Testing", field_type="date", required=True)

    heater_group = add("heater_details", field_label="Equip. Name: Heater", field_type="group", required=False)
    add("heater_make", parent=heater_group, field_label="Make", field_type="text", required=True,
        standard_value="Noted")
    add("heater_sn", parent=heater_group, field_label="S.N.", field_type="text", required=True,
        standard_value="Noted")
    add("heater_mfg_year", parent=heater_group, field_label="Mfg.", field_type="text", required=True,
        standard_value="Noted")

    blower_group = add("blower_details", field_label="Equip. Name: Blower", field_type="group", required=False)
    add("blower_make", parent=blower_group, field_label="Make", field_type="text", required=True,
        standard_value="Noted")
    add("blower_sn", parent=blower_group, field_label="S.N.", field_type="text", required=True,
        standard_value="Noted")
    add("blower_mfg_year", parent=blower_group, field_label="Mfg.", field_type="text", required=True,
        standard_value="Noted")

    temp_switch_group = add("temperature_switch_details", field_label="Equip. Name: Temperature Switch",
                             field_type="group", required=False)
    add("temp_switch_make", parent=temp_switch_group, field_label="Make", field_type="text", required=True,
        standard_value="Noted")
    add("temp_switch_sn", parent=temp_switch_group, field_label="S.N.", field_type="text", required=True,
        standard_value="Noted")
    add("temp_switch_mfg_year", parent=temp_switch_group, field_label="Mfg.", field_type="text", required=False,
        standard_value="Noted")

    checks_group = add("check_points", field_label="Maintenance Activities During Schedule", field_type="group",
                        required=False)
    add("heater_cover_frame_damage_check", parent=checks_group, field_label="Check the Heater Cover and Frame "
        "for Any Damage", field_type="select", options="No Damage, Damage Found", required=True,
        standard_value="No Damage", negative_values="Damage Found")
    add("heater_element_condition_check", parent=checks_group, field_label="Check the Condition of Heater "
        "Element", field_type="select", options="Good, Replaced", required=True, standard_value="Good/Replaced")
    add("heater_flexible_duct_clean", parent=checks_group, field_label="Clean the Cab Heater Flexible Duct "
        "(Rubber Hose/Bellow)", field_type="select", options="Cleaned, Not Cleaned", required=True,
        standard_value="Should Be Cleaned", negative_values="Not Cleaned")
    add("heater_blower_area_clean", parent=checks_group, field_label="Clean the Area Surrounding Cab Heater & "
        "Bellow Driver Desk in Locomotives", field_type="select", options="Cleaned, Not Cleaned", required=True,
        standard_value="Should Be Cleaned", negative_values="Not Cleaned")
    add("fuse_check", parent=checks_group, field_label="Check the Fuse (06A) in Heater Circuit & Blower Fuse "
        "(02A)", field_type="select", options="Healthy, Not Healthy", required=True, standard_value="Healthy",
        negative_values="Not Healthy")
    add("heater_heating_effect_380v_check", parent=checks_group, field_label="Check the Proper Heating of "
        "Heater Element After Giving 380 V Supply for Heater (Equip: Heater Cum Blower - Only Heater)",
        field_type="select", options="Heating Effect, No Heating Effect", required=True,
        standard_value="Heating Effect", negative_values="No Heating Effect")
    add("blower_heating_effect_415v_check", parent=checks_group, field_label="Check the Proper Heating of "
        "Heater Element After Giving 415 V Supply for Blower (Equip: Heater Cum Blower)", field_type="select",
        options="Heating Effect, No Heating Effect", required=True, standard_value="Heating Effect",
        negative_values="No Heating Effect")
    add("thermostat_working_check", parent=checks_group, field_label="Check the Working of Thermostat",
        field_type="select", options="Working, Not Working", required=True, negative_values="Not Working")
    add("insulation_resistance_check", parent=checks_group, field_label="Check the Insulation Resistance With "
        "500 V Megger", field_type="numeric_range", required=True, unit="MOhm", min_value=5.0, max_value=1000.0,
        decimal_precision=1, standard_value="5 Mega Ohms (Min)")
    add("grommets_replace", parent=checks_group, field_label="Check the Grommets (Applicable Only for Heater)",
        field_type="select", options="Replaced, Not Replaced", required=True, standard_value="Must Be Replaced",
        negative_values="Not Replaced")
    add("blower_motor_bearing_replace", parent=checks_group, field_label="Replace the Bearing of Cab Heater "
        "Blower Motor", field_type="select", options="Replaced, Not Replaced", required=True,
        standard_value="Must Change Item in IOH", authority_reference="RDSO Letter No. EL/3.1.28(DML), Dated "
                                                                       "13.01.2023", negative_values="Not Replaced")
    add("flexible_duct_replace", parent=checks_group, field_label="Replace the Cab Heater Flexible Duct (Rubber "
        "Hose/Bellow)", field_type="select", options="Replaced, Not Replaced", required=True,
        standard_value="Must Change Item in TOH & IOH", authority_reference="RDSO Letter No. EL/3.1.28(DML), "
                                                                             "Dated 13.01.2023",
        negative_values="Not Replaced")
    add("blower_110v_supply_check", parent=checks_group, field_label="Check the Proper Working of Heater Giving "
        "110 V Supply for Blower", field_type="select", options="Working, Not Working", required=True,
        standard_value="Should Be in Working", negative_values="Not Working")
    add("terminal_connection_segregation", parent=checks_group, field_label="Replace Terminal Connection of "
        "Heater Cum Blower Assembly (Segregation of Heater & Blower Terminals) - Applicable for All Class of "
        "Locomotives", field_type="select", options="Implemented, Not Implemented", required=True,
        standard_value="Must Be Implemented", authority_reference="RDSO MS 408, Dated 30.05.2012",
        negative_values="Not Implemented")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="CHB", template_code="127", technology="3_PHASE",
        template_name="Checksheet for Cab Heater cum Blower",
        description="TOH & IOH maintenance checksheet for Cab Heater cum Blower - 3-Phase - M1-HR section.",
        build_fn=build,
    )
