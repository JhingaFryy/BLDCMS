"""
Module 41 (Phase 2): seeds the HBSB (HB & SB Panel, 3-Phase locomotives, M1-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_hb_sb_panel_3phase_template.py`

Source: "HB & SB 3-Phase.pdf" - "HB-1/HB-2/SB-1/SB-2 Panel TOH & IOH Maintenance Activities", a
different shape from every other M1-HR checksheet: instead of a fixed checking-point list, each
panel is an inventory of individually-named contactors/MCBs/switches (identified by their fixed
loco wiring number, e.g. "47.2/1 - Main Compressure-1", and fixed Type & Rating, e.g.
"LC1D80/3-Phase/80 Amp") that the technician verifies one by one. The wiring number, purpose and
type/rating are fixed reference identifiers describing which physical device the row is about (not
something the technician measures), so they are baked into each field's label; only the two things
the technician actually records - Make (occasionally replaced with a different make) and
Condition/Remarks (the source sheet's own "Serviceable"/"Removed"/"New" vocabulary) - are modelled
as fields, consistent with how other equipment's fixed identity details (e.g. HRPT's "Bellow
Pipe"/"ORD Pipe") are named directly as field labels rather than re-entered as data.

HB-1 and SB-1 additionally show a panel-level Make/S.No/Mfg block (the panel manufacturer's own
identity) not shown on the HB-2/SB-2 pages, so those two fields are only added where the source
actually shows them, per the module's "implement exactly according to the supplied PDFs" rule.

Per the module's "Do NOT create fields for Loco Number/Technician/Supervisor Name/Signature" rule,
the sheet's own "Loco No." and staff attendance log lines ("1st day - DBSt Badal Kumar...") are
intentionally not modelled.
"""
from _aux_template_helpers import add_final_remarks, run_seed

CONDITION_OPTIONS = "Serviceable, Not Serviceable, Removed/Replaced"

# Each row: (key, wiring_no, purpose, type_rating, required)
HB1_CONTACTORS = [
    ("main_compressure_1", "47.2/1", "Main Compressure-1", "LC1D80/3-Phase/80 Amp", True),
    ("aux_contactor_52_4", "52.3/4", "Aux. Contactor 52/4", "01 Pole/80 Amp", True),
    ("aux_contactor_52_5", "52.3/5", "Aux. Contactor 52/5", "01 Pole/80 Amp", True),
    ("bur_load_sharing_1", "52/4", "BUR Load Sharing Contactor", "LC1D150/3-Phase/150 Amp", False),
    ("bur_load_sharing_2", "52/5", "BUR Load Sharing Contactor", "LC1D150/3-Phase/150 Amp", False),
]
HB1_MCBS = [
    ("transformer_oil_pump", "62.1/1", "Transformer Oil Pump", "03 Pole/16 Amp", True),
    ("traction_con_oil_pump", "63.1/1", "Traction Con. Oil Pump", "03 Pole: 01) 2.5-4 Amp, 02) 6-10 Amp, 03) "
     "04-6.3 Amp", True),
    ("main_compressure_mcb", "47.1/1", "Main Compressure", "03 Pole/40 Amp", True),
    ("traction_motor_blower_1", "53.1/1", "Traction Motor Blower-1", "03 Pole/63 Amp", True),
    ("scavenge_blower_tmb1_ocb2", "55.1/1", "Scvange Blower TMB-1 OCB-2", "03 Pole/10 Amp", True),
    ("oil_cooling_blower_1", "59.1/1", "Oil Cooling Blower-1", "03 Pole/63 Amp", True),
    ("mr_blower", "54.1/1", "MR Blower", "03 Pole/06 Amp", True),
    ("sc_mrb_1", "56.1/1", "SC MRB-1", "03 Pole/06 Amp", True),
    ("cab_ventilation", "69.61", "Cab Ventilation", "01 Pole/10 Amp", True),
    ("cab_heater", "69.62", "Cab Heater", "01 Pole/10 Amp", True),
    ("crew_fan", "69.71", "Crew Fan", "01 Pole/10 Amp", True),
]

HB2_CONTACTORS = [
    ("main_compressure_2", "47.2/2", "Main Compressure-2", "LC1D80/3-Phase/80 Amp", True),
    ("cab_ac", "47.3/2 (52.7)", "Cab AC", "LC1D80/3-Phase/80 Amp", True),
    ("sc_tmb_1", "52.4/1", "SC. TMB-1", "LC1D80/3-Phase/80 Amp", True),
    ("sc_tmb_2", "52.4/2", "SC. TMB-2", "LC1D80/3-Phase/80 Amp", True),
    ("aux_contactor_oil_pump_1", "52.5/1", "Aux. Contactor for Oil Pump-1 (OCB)", "LC1F150/3-Phase/150 Amp", True),
    ("aux_contactor_oil_pump_2", "52.5/2", "Aux. Contactor for Oil Pump-2", "LC1F150/3-Phase/150 Amp", True),
    ("aux_contactor_52_5_1a", "52.6/1", "Aux. Contactor 52.5/1", "01-Phase/80 Amp (Schaltbau)", True),
    ("aux_contactor_52_5_1b", "52.6/2", "Aux. Contactor 52.5/1", "01-Phase/80 Amp (Schaltbau)", True),
]
HB2_MCBS = [
    ("transformer_oil_pump", "62.1/2", "Transformer Oil Pump", "03 Pole/16 Amp", True),
    ("traction_con_oil_pump", "63.1/2", "Traction Con. Oil Pump", "03 Pole/6-10 Amp", True),
    ("main_compressure_mcb", "47.1/2", "Main Compressure", "03 Pole/40 Amp", True),
    ("traction_motor_blower_1", "53.1/2", "Traction Motor Blower-1", "03 Pole/63 Amp", True),
    ("scavenge_blower_tmb1_ocb2", "55.1/2", "Scvange Blower TMB-1 OCB-2", "03 Pole/10 Amp", True),
    ("oil_cooling_blower_1", "59.1/2", "Oil Cooling Blower-1", "03 Pole/63 Amp", True),
    ("mr_blower_1", "54.1/2", "MR Blower-1", "01 Phase/06 Amp (ABB)", True),
    ("sc_mrb_1", "56.1/2", "SC MRB-1", "01 Phase/06 Amp (ABB)", True),
    ("mcb_for_cab_ac", "64.1", "MCB for Cab AC", "03 Pole/10 Amp", True),
    ("cab_selection_switch_ac", "-", "Cab Selection Switch for Cab AC Unit", "-", False),
]

SB1_CONTACTORS = [
    ("control_electronics_off", "126.5", "Control Electronics Off", "CAD32/3-Phase/10 Amp", False),
    ("vcb_control", "136.4", "VCB Control", "LC1D09/3-Phase/25 Amp", False),
    ("power_supply_cab1", "126.7/1", "Power Supply Cab-1", "LC1D128/3-Phase/25 Amp", False),
    ("time_delay_relay_vcb", "136.3", "Time Delay Relay VCB", "LC1D128/3-Phase/25 Amp", False),
    ("vcu_reset_relay", "VCU Reset Relay", "VCU Reset Cont.", "CAD32", False),
    ("vcu_reset_timer", "-", "VCU Reset Timer", "Timer", False),
    ("contactor_head_light", "338/1", "Contactor for Head Light", "01 Phase/80 Amp", True),
    ("control_circuit_on", "126", "Control Circuit On", "01 Phase/140 Amp", True),
    ("central_electronics_in", "218", "Central Electronics In", "01 Phase/140 Amp", True),
]
SB1_MCBS = [
    ("driver_cab1", "127.3/1", "Driver Cab-1", "01 Pole/10 Amp", True),
    ("panto_vcb", "127.12", "Panto-VCB", "01 Pole/10 Amp", True),
    ("power_supply_24_48v_1", "127.91/1", "Power Supply 24/48V-1", "01 Pole/10 Amp", True),
    ("lightning_front", "310.1", "Lightning Front", "01 Pole/10 Amp", True),
    ("electronics_traction_con_1", "127.1/1", "Electronics Traction Con.-1", "01 Pole/10 Amp", True),
    ("power_supply_gate_units", "127.11/1", "Power Supply Gate Units", "01 Pole/20 Amp", True),
    ("monitoring", "127.2/1", "Monitoring", "01 Pole/10 Amp", True),
    ("electronics_aux_con_1", "127.22/1", "Electronics Auxillairy Con.-1", "01 Pole/10 Amp", True),
    ("central_electronics_1", "127.9/1", "Central Electronics-1", "01 Pole/10 Amp", True),
    ("central_electronics_2", "127.9/2", "Central Electronics-2", "01 Pole/10 Amp", True),
    ("speed_sensor", "127.25/1", "Speed Sensor", "01 Pole/10 Amp", False),
    ("rtis", "RTIS", "RTIS", "02 Pole/02-03 Amp", True),
]
SB1_SWITCHES = [
    ("failure_operation", "152", "Failure Operation", "Rotating Switch", False),
    ("bogie_cut_out", "154", "Bogie Cut Out", "Rotating Switch", False),
    ("configuration_shunting", "160", "Configuration (Shunting)", "Rotating Switch", False),
    ("vigilance_device_cut_out", "237.1", "Vigilance Device Cut Out", "Rotating Switch", False),
    ("key_switch_simulation", "179", "Key Switch for Simulation", "-", False),
    ("configuration", "161", "Configuration", "Push Button", False),
    ("vcu_reset", "-", "VCU Reset", "Push Button", False),
]

SB2_CONTACTORS = [
    ("aux_con_pantograph", "130.1", "Aux. Con. Pantograph", "3-Phase/LC1D09", True),
    ("relay_temp_control_electronics", "211", "Relay Temp. Control Electronics", "03 Phase/CAD32", True),
    ("safety_relay_control_electronics_on", "126.6", "Safety Relay Control Electronics On",
     "03 Phase/CAD32/LADC22", True),
    ("power_supply_cab2", "126.7/2", "Power Supply Cab-2", "03 Phase/LC1D128/LADC22", True),
    ("aux_compressure", "48.2", "Aux. Compressure", "01 Phase/80 Amp", True),
    ("head_light", "338/2", "Head Light", "01 Phase/80 Amp", True),
]
SB2_MCBS = [
    ("aux_compressure_mcb", "48.1", "Aux. Compressure", "01 Pole/16A", True),
    ("driver_cab2", "127.3/2", "Driver Cab-2", "01 Pole/10A", True),
    ("lighting_machine_room", "310.4", "Lighting Machine Room", "01 Pole/16A", True),
    ("power_supply_gate_unit_sr2", "127.11/2", "Power Supply Gate Unit (SR-2)", "01 Pole/20A", True),
    ("commissioning_1", "127.81", "Commissioning-1", "01 Pole/10A", True),
    ("vigillance_control", "127.15", "Vigillance Control", "01 Pole/10A", True),
    ("pneumatic_panel", "127.7", "Pneumatic Panel", "01 Pole/10A", True),
    ("commissioning_2", "127.82", "Commissioning-2", "01 Pole/10A", True),
    ("power_supply_24_48_2", "127.91/2", "Power Supply 24/48-2", "01 Pole/10A", True),
    ("marker_light", "310.7/1", "Marker Light", "01 Pole/10A", True),
    ("lighting_front_2", "310.12", "Lighting Front-2", "01 Pole/10A", True),
    ("electronics_sr_2", "127.1/2", "Electronics SR-2", "01 Pole/10A", True),
    ("monitoring_2", "127.2/2", "Monitoring-2", "01 Pole/10A", True),
    ("aux_conv_electronics_2", "127.22/2", "Aux. Conv. Electronics-2", "01 Pole/10A", True),
    ("aux_conv_electronics_3", "127.22/3", "Aux. Conv. Electronics-3", "01 Pole/10A", True),
    ("central_electronics_2a", "127.9/3", "Central Electronics-2", "01 Pole/10A", True),
    ("central_electronics_2b", "127.9/4", "Central Electronics-2", "01 Pole/10A", True),
    ("memotel_speedometer", "127.92", "Memotel Speedometer", "01 Pole/10A", True),
    ("electronics_aux_contactor", "127.24", "Electronics Aux. Contactor", "01 Pole/10A", True),
    ("power_supply_air_dryer", "128.1/2", "Power Supply Air Dryer", "02 Pole/03A", True),
]


def _add_device_rows(add, parent, prefix, rows):
    for key, wiring_no, purpose, type_rating, required in rows:
        label = f"{wiring_no} - {purpose} ({type_rating})"
        device_group = add(f"{prefix}_{key}", parent=parent, field_label=label, field_type="group",
                            required=False)
        add(f"{prefix}_{key}_make", parent=device_group, field_label="Make", field_type="text", required=required,
            standard_value="Noted")
        add(f"{prefix}_{key}_mfg", parent=device_group, field_label="Mfg.", field_type="text", required=False,
            standard_value="Noted")
        add(f"{prefix}_{key}_condition", parent=device_group, field_label="Condition/Remarks", field_type="select",
            options=CONDITION_OPTIONS, required=required, standard_value="Serviceable")


def build(add):
    add("overhauling_date", field_label="Date", field_type="date", required=True)

    hb1_group = add("hb1_panel", field_label="HB-1 Panel TOH & IOH Maintenance Activities", field_type="group",
                     required=False)
    add("hb1_panel_make", parent=hb1_group, field_label="Make", field_type="text", required=False,
        standard_value="Noted")
    add("hb1_panel_sn", parent=hb1_group, field_label="HB-1 Contactor Details S.No.", field_type="text",
        required=False, standard_value="Noted")
    add("hb1_panel_mfg", parent=hb1_group, field_label="Mfg.", field_type="text", required=False,
        standard_value="Noted")
    hb1_contactors_group = add("hb1_contactors", parent=hb1_group, field_label="HB-1 Contactor Details",
                                field_type="group", required=False)
    _add_device_rows(add, hb1_contactors_group, "hb1c", HB1_CONTACTORS)
    hb1_mcb_group = add("hb1_mcbs", parent=hb1_group, field_label="HB-1 MCB Details", field_type="group",
                         required=False)
    _add_device_rows(add, hb1_mcb_group, "hb1m", HB1_MCBS)

    hb2_group = add("hb2_panel", field_label="HB-2 Panel TOH & IOH Maintenance Activities", field_type="group",
                     required=False)
    hb2_contactors_group = add("hb2_contactors", parent=hb2_group, field_label="HB-2 Contactor Details",
                                field_type="group", required=False)
    _add_device_rows(add, hb2_contactors_group, "hb2c", HB2_CONTACTORS)
    hb2_mcb_group = add("hb2_mcbs", parent=hb2_group, field_label="HB-2 MCB Details", field_type="group",
                         required=False)
    _add_device_rows(add, hb2_mcb_group, "hb2m", HB2_MCBS)

    sb1_group = add("sb1_panel", field_label="SB-1 Panel TOH & IOH Maintenance Activities", field_type="group",
                     required=False)
    add("sb1_panel_make", parent=sb1_group, field_label="Make", field_type="text", required=False,
        standard_value="Noted")
    add("sb1_panel_sn", parent=sb1_group, field_label="SB-1 Contactor Details S.No.", field_type="text",
        required=False, standard_value="Noted")
    add("sb1_panel_mfg", parent=sb1_group, field_label="Mfg.", field_type="text", required=False,
        standard_value="Noted")
    sb1_contactors_group = add("sb1_contactors", parent=sb1_group, field_label="SB-1 Contactor Details",
                                field_type="group", required=False)
    _add_device_rows(add, sb1_contactors_group, "sb1c", SB1_CONTACTORS)
    sb1_mcb_group = add("sb1_mcbs", parent=sb1_group, field_label="SB-1 MCB Details", field_type="group",
                         required=False)
    _add_device_rows(add, sb1_mcb_group, "sb1m", SB1_MCBS)
    sb1_switch_group = add("sb1_switches", parent=sb1_group, field_label="SB-1 Switch Details", field_type="group",
                            required=False)
    _add_device_rows(add, sb1_switch_group, "sb1s", SB1_SWITCHES)

    sb2_group = add("sb2_panel", field_label="SB-2 Panel TOH & IOH Maintenance Activities", field_type="group",
                     required=False)
    sb2_contactors_group = add("sb2_contactors", parent=sb2_group, field_label="SB-2 Contactor Details",
                                field_type="group", required=False)
    _add_device_rows(add, sb2_contactors_group, "sb2c", SB2_CONTACTORS)
    sb2_mcb_group = add("sb2_mcbs", parent=sb2_group, field_label="SB-2 MCB Details", field_type="group",
                         required=False)
    _add_device_rows(add, sb2_mcb_group, "sb2m", SB2_MCBS)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="HBSB", template_code="134", technology="3_PHASE",
        template_name="Checksheet for HB & SB Panel",
        description="HB-1/HB-2/SB-1/SB-2 Panel TOH & IOH maintenance activities checksheet - 3-Phase - M1-HR "
                     "section.",
        build_fn=build,
    )
