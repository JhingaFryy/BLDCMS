"""
Module 46: seeds the M2-HR Earth Fault Relay (3-Phase) checksheet template.

Source: "earth fault relay.pdf" - TRS/ELS/BL/M2HR/3 Phase/Earth Fault Relay/Checksheet/10,
CLW Specification No. CLW/ES/3/0090 Alt.C dated 14.04.1997. The sheet has four named relay
positions (415/110V, Auxiliary Converter, Harmonic Filter, Control Circuit); each is modelled as
its own group since schematic number and loco location are fixed per relay position (pre-filled
as default values, not required).
"""
from _m2hr_template_helpers import add_confirm, add_date, add_numeric, add_text, run_seed_paged


def add_relay_group(add, key, label, schematic_no, location, pickup_std, dropout_required=True):
    group = add(key, field_label=f"Earth Fault Relay - {label}", field_type="group", required=False,
                authority_reference="CLW/ES/3/0090 Alt.C dtd 14.04.1997")
    add_text(add, f"{key}_schematic_no", "Schematic No.", default_value=schematic_no, parent=group)
    add_text(add, f"{key}_location_on_loco", "Location on Loco", default_value=location, parent=group)
    add_text(add, f"{key}_make", "Make", required=True, parent=group)
    add_text(add, f"{key}_sr_no", "Sr. No. of Relay", required=True, parent=group)
    add("m2hr_efr_" + key + "_mfd", parent=group, field_label="MFD (Month/Year)", field_type="date", required=False)
    add_confirm(add, f"{key}_visual_check", "Visual Checking for Any Abnormality", parent=group)
    add_confirm(add, f"{key}_terminal_check", "Check the Condition of Terminals", parent=group)
    add_numeric(add, f"{key}_pickup_ma", "Pick Up", pickup_std, unit="mA", decimal_precision=0, parent=group)
    add_numeric(add, f"{key}_dropout_ma", "Drop Out", None, unit="mA", decimal_precision=0,
                required=dropout_required, parent=group)
    return group


def build(add, set_page):
    add_date(add, "remove_date_sch", "Remove Date/Sch")
    add_date(add, "date_of_overhauling", "Date of Overhauling")
    add_date(add, "provided_date_sch", "Provided Date/Sch")

    add_relay_group(add, "relay_415_110v", "415/110V", "89.5", "HB1", "150")
    add_relay_group(add, "relay_aux_converter", "Auxiliary Converter", "89.2", "HB2", "150")
    add_relay_group(add, "relay_harmonic_filter", "Harmonic Filter", "89.6", "FB", None, dropout_required=False)
    add_relay_group(add, "relay_control_circuit", "Control Circuit", "89.7", "SB1", "150")


if __name__ == "__main__":
    run_seed_paged(
        equipment_code="EFR",
        template_code="M2HR_EFR",
        technology="3_PHASE",
        template_name="Check Sheet for Earth Fault Relay (AOH/TOH/IOH) - 3 Phase Loco",
        description="M2-HR: Earth Fault Relay checksheet for 3-Phase locomotives.",
        build_fn=build,
    )
