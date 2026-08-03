"""
Module 46: seeds the M2-HR Fire Detection Unit (FDU, 3-Phase) checksheet template.

Source: "FDU.pdf" - TRS/ELS/BL/M2HR/3 Phase/FDU/Check sheet/4 (OEM Manual & CLW Specification).

The sheet's Sr.No.5 (setting limits) and Sr.No.6 (normal/blockage/rupture mV table) are per-make
reference tables covering 8 OEM makes (Trolex, Hind/Hirect, Elixir, Auspice/AAPL, Saitronix,
Laxven, ARC, Arisys); the technician records which make is fitted and a single actual reading, not
one row per make - so these are modelled as one "select the fitted make" field plus the observed
value(s), with the full reference table preserved in `authority_reference`. Sr.No.7's ten interlock
pairs are modelled as one repeated group per pair (standard/actual for both Normal and
Rupture&Blockage conditions).
"""
from _m2hr_template_helpers import add_confirm, add_date, add_numeric, add_text, run_seed_paged

FDU_MAKES = "TROLEX, HIND (HIRECT), ELIXIR, AUSPICE (AAPL), SAITRONIX, LAXVEN, ARC, ARISYS"
FDU_RANGE_REFERENCE = "OEM Manual: per-make setting range (see FDU.pdf Sr.No.5 table)."
FDU_MV_TABLE_REFERENCE = "OEM Manual: per-make Normal/Blockage/Rupture mV table (see FDU.pdf Sr.No.6 table)."
INTERLOCKS_NORMAL = [("10-11", "Close"), ("10-23", "Open")]
INTERLOCKS_RUPTURE_BLOCKAGE = [
    ("04-17", "Close"), ("06-19", "Close"), ("07-20", "Close"), ("09-22", "Close"),
    ("04-05", "Open"), ("07-08", "Open"), ("18-19", "Open"), ("21-22", "Open"),
]


def add_interlock(add, key, label, standard, condition_label):
    return add(f"interlock_{key}_{condition_label}", field_label=f"Interlock {label} ({condition_label})",
               field_type="select", options="Close, Open", required=True, standard_value=standard)


def build(add, set_page):
    add_text(add, "sr_no", "Sr. No.", required=True)
    add_text(add, "make", "Make", required=True)
    add_text(add, "mgf", "MGF (Month/Year)", required=False)
    add_date(add, "remove_date_sch", "Remove Date/Sch")
    add_date(add, "date_of_overhauling", "Date of Overhauling")
    add_date(add, "provided_date_sch", "Provided Date/Sch")

    add_confirm(add, "visual_check_internal_external", "Visually Check the Internal & External "
                "Condition of FDU and Its Cards, Pin & etc.", done_word="No abnormality",
                negative_word="Abnormality")
    add_confirm(add, "clean_fdu", "Clean the FDU", done_word="Cleaned")
    add_confirm(add, "check_cards_sensors", "Thoroughly Check the Cards Connection, Sensors, "
                "Flashing and Abnormality", done_word="No abnormality", negative_word="Abnormality")
    add_confirm(add, "connect_power_supply", "Connect Power Supply 16 to 24V DC", done_word="Connected")

    set_range = add("set_fdu_range", field_label="Set the FDU as Per Limits as Per Make",
                    field_type="group", required=True, authority_reference=FDU_RANGE_REFERENCE)
    add("set_fdu_range_make", parent=set_range, field_label="Make", field_type="select",
        options=FDU_MAKES, required=True)
    add_text(add, "set_fdu_range_value", "Set Value", required=True, unit="mV", parent=set_range)

    mv_group = add("measure_millivolt", field_label="Measure the Millivolt in Normal, Blockage & "
                   "Rupture Condition", field_type="group", required=True,
                   authority_reference=FDU_MV_TABLE_REFERENCE)
    add_numeric(add, "measure_millivolt_blockage", "Blockage Condition Reading", None, unit="V",
                required=True, parent=mv_group)
    add_numeric(add, "measure_millivolt_rupture", "Rupture Condition Reading", None, unit="V",
                required=True, parent=mv_group)
    add_confirm(add, "measure_millivolt_smoke_check", "Smoke Check", parent=mv_group)

    interlock_group = add("interlock_status", field_label="Check & Note Down Interlock Status",
                          field_type="group", required=True, authority_reference="OEM Manual & CLW Specification")
    for pair, std in INTERLOCKS_NORMAL:
        add_interlock(add, pair.replace("-", "_"), pair, std, "normal_condition")
        add_interlock(add, pair.replace("-", "_"), pair, "Open" if std == "Close" else "Close",
                      "rupture_blockage_condition")
    for pair, std in INTERLOCKS_RUPTURE_BLOCKAGE:
        add_interlock(add, pair.replace("-", "_"), pair, std, "normal_condition")
        add_interlock(add, pair.replace("-", "_"), pair, "Open" if std == "Close" else "Close",
                      "rupture_blockage_condition")

    time_delay = add("time_delay_setting", field_label="Set the Time Delay for Fault Messages",
                     field_type="group", required=True)
    add_text(add, "time_delay_test", "Time Delay Setting (for Test)", required=True,
             standard_value="0.5 min", parent=time_delay)
    add_text(add, "time_delay_locos", "Time Delay Setting (for Locos)", required=True,
             standard_value="2 min", parent=time_delay)

    add_confirm(add, "smoke_test", "Give Smoke to the Suction Pipe - Both Smoke Detector "
                "Sensors Red LED Should Glow", done_word="LED Glow", negative_word="LED Not Glow")
    add_confirm(add, "led_reset", "LED Status to Be Reset by Pushing Reset Button", done_word="LED Off",
                negative_word="LED On")
    add_confirm(add, "remove_test_jig", "Remove the Test Jig from FDU and All Tightness to Be "
                "Ensured Before Declaring Ready for Work on Loco", done_word="Ensured")

    add("modifications", field_label="Modifications, if any", field_type="textarea", required=False)
    add("remarks", field_label="Remarks", field_type="textarea", required=False)


if __name__ == "__main__":
    run_seed_paged(
        equipment_code="FDU",
        template_code="M2HR_FDU",
        technology="3_PHASE",
        template_name="Fire Detection Unit (AOH/TOH/IOH)",
        description="M2-HR: Fire Detection Unit checksheet for 3-Phase locomotives.",
        build_fn=build,
    )
