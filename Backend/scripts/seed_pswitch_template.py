"""
Module 46: seeds the M2-HR Pressure Switch (3-Phase) checksheet template.

Source: "pressure switch 3 ph.pdf" - TRS/ELS/BL/M2HR/3 Phase/Pressure switch/Check sheet/6.
References: RDSO SMI 298 dt 06.10.2016 (Maintenance & Must Change); RDSO SMI 327 dt 11.02.2019
P-7 (setting & tolerance).

The 8-point maintenance checklist has separate expected values for TOH vs IOH schedules, and
separately for the FTIL vs KBIL panel makes fitted on this loco - both are recorded (not one
"Standard" outcome), since which value applies depends on which schedule/panel the technician is
actually working under.
"""
from _m2hr_template_helpers import add_confirm, add_date, add_numeric, add_text, run_seed_paged


def add_panel_check(add, key, label):
    group = add(key, field_label=label, field_type="group", required=False,
                authority_reference="RDSO SMI 298 dt 06.10.2016")
    add_confirm(add, f"{key}_ftil", "FTIL Panel", required=False, parent=group)
    add_confirm(add, f"{key}_kbil", "KBIL Panel", required=False, parent=group)
    return group


def add_switch_setting(add, key, label, ftil_no, kbil_no, schematic_no, cut_in, cut_out, tolerance):
    group = add(key, field_label=f"Pressure Switch Setting - {label}", field_type="group",
                required=False, authority_reference="RDSO SMI 327 dt 11.02.2019 P-7")
    add_text(add, f"{key}_ftil_no", "FTIL No.", default_value=ftil_no, required=False, parent=group)
    add_text(add, f"{key}_kbil_no", "KBIL No.", default_value=kbil_no, required=False, parent=group)
    add_text(add, f"{key}_schematic_no", "Schematic No.", default_value=schematic_no, required=False,
             parent=group)
    add_text(add, f"{key}_make", "Make", required=True, parent=group)
    add_text(add, f"{key}_mfg", "MFG.", required=True, parent=group)
    add_text(add, f"{key}_sr_no", "Sr. No. of Pressure Switch", required=True, parent=group)
    add_numeric(add, f"{key}_cut_in", "Cut in", f"{cut_in} ± {tolerance}", unit="kg/cm2",
                decimal_precision=2, parent=group)
    add_numeric(add, f"{key}_cut_out", "Cut out", f"{cut_out} ± {tolerance}", unit="kg/cm2",
                decimal_precision=2, parent=group)
    return group


def build(add, set_page):
    add_text(add, "pneumatic_panel_make", "Pneumatic Panel Make", required=False)
    add_date(add, "remove_date_sch", "Remove Date/Sch")
    add_date(add, "date_of_overhauling", "Date of Overhauling")
    add_date(add, "provided_date_sch", "Provided Date/Sch")

    add_panel_check(add, "external_visual", "Check External Condition Visually")
    add_panel_check(add, "internal_visual", "Check Internal Condition Visually")
    add_panel_check(add, "dry_air_cleaning_outer", "Clean Pressure Switch with Dry Air (Outer)")
    add_panel_check(add, "open_clean_inspect", "Open Pressure Switch, Clean and Inspect for "
                    "Proper Operation")
    add_panel_check(add, "wear_tear_check", "Check for Wear and Tear, Replace Main Spring/Knob "
                    "Setting if Necessary")
    add_panel_check(add, "connection_terminal_check", "Check Connection Terminals")
    add_panel_check(add, "air_leakage_test", "Perform Air Leakage Test")
    add_panel_check(add, "pickup_dropout_check", "Check Proper Pick-up and Drop-out Values")

    must_change = add("must_change_items", field_label="Must Change Items (as per TC-31 Rev '1')",
                      field_type="group", required=False)
    add("all_rubber_items_diaphragm", parent=must_change,
        field_label="All Rubber Items Including Diaphragm of All Pneumatic Valves (IOH)",
        field_type="select", options="Replaced, N/A", required=False, standard_value="Replaced")
    add("all_spring_items", parent=must_change,
        field_label="All Spring Items of All Pneumatic Valves (IOH)",
        field_type="select", options="Replaced, N/A", required=False, standard_value="Replaced")

    add_switch_setting(add, "pantograph1", "Pantograph-1", "P-9/1", "PANT-1-PS", "130.4/1", 5.5, 4.5, 0.2)
    add_switch_setting(add, "pantograph2", "Pantograph-2", "P-9/2", "PANT-2-PS", "130.4/2", 5.5, 4.5, 0.2)
    add_switch_setting(add, "aux_compressor_panto", "Auxiliary Compressor/Panto Reservoir (CPA)",
                       "P-26", "PAN-S-PS", "172.4", 7.0, 8.0, 0.15)
    add_switch_setting(add, "parking_brake", "Parking Brake", "P-32", "PB-PS", "269.3", 5.0, 4.0, 0.1)
    add_switch_setting(add, "feed_pipe", "Feed Pipe", "P-34", "FP-PS", "269.42", 5.6, 5.0, 0.1)
    add_switch_setting(add, "main_compressor_rgcp2", "Main Compressor (RGCP-2)", "P-35", "-", "172.2",
                       8.0, 10.0, 0.2)
    add_switch_setting(add, "main_compressor_rgcp3", "Main Compressor (RGCP-3)", "P-36", "-", "172.3",
                       8.0, 10.0, 0.2)
    add_switch_setting(add, "low_main_reservoir", "Low Main Reservoir", "P-37", "-", "269.4", 6.4, 5.6, 0.15)
    add_switch_setting(add, "venturi_afi", "Venturi Valve Pressure (AFI)", "P-44", "NA", "269.41",
                       5.0, 4.0, 0.15)
    add_switch_setting(add, "direct_brake", "Direct Brake", "P-59", "IBS-PS", "269.2", 0.65, 0.3, 0.05)
    add_switch_setting(add, "vigilance", "Vigilance", "P-60", "BC-PS", "269.5", 2.0, 1.5, 0.1)
    add_switch_setting(add, "brake_cylinder_bogie1", "Brake Cylinder Bogie-1", "P-64/1", "-", "269.6/1",
                       0.65, 0.3, 0.05)
    add_switch_setting(add, "brake_cylinder_bogie2", "Brake Cylinder Bogie-2", "P-64/2", "-", "269.6/2",
                       0.65, 0.3, 0.05)
    add_switch_setting(add, "brake_pipe", "Brake Pipe", "P-69", "NA", "269.1", 4.2, 3.0, 0.15)


if __name__ == "__main__":
    run_seed_paged(
        equipment_code="PSwitch",
        template_code="M2HR_PSWITCH_3PH",
        technology="3_PHASE",
        template_name="Check Sheet for Pressure Switch (AOH/TOH/IOH) - 3 Phase Loco",
        description="M2-HR: Pressure Switch checksheet for 3-Phase locomotives.",
        build_fn=build,
    )
