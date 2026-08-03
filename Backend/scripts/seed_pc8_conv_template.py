"""
Module 46: seeds the M2-HR PC-8 Relays (Conventional) checksheet template.

Source: "PC-8 relay.pdf" - TRS/ELS/BL/M2HR/Conv./PC-8 Relay/Check sheet/I. The sheet's sample has
four named relay positions (QSIT, QEMS, QFL, QVCD); QVCD reads "NA" throughout in the sample,
consistent with it being fitted only on certain loco variants, so it is optional/not required.
"""
from _m2hr_template_helpers import add_confirm, add_date, add_numeric, add_text, run_seed_paged


def add_relay_group(add, key, label, required=True):
    group = add(key, field_label=f"PC-8 Relay - {label}", field_type="group", required=False)
    add_text(add, f"{key}_relay_no", "Relay No.", required=required, parent=group)
    add_text(add, f"{key}_make_mfg", "Make/MFG", required=required, parent=group)
    add_numeric(add, f"{key}_coil_resistance", "Coil Resistance",
                "ABB 997-1103Ω, Woama 950-1050Ω, R 20Ω (OEM)", unit="Ohm", decimal_precision=0,
                required=required, authority_reference="OEM", parent=group)
    add_numeric(add, f"{key}_ambient_temp", "Ambient/Room Temp.", None, unit="C",
                decimal_precision=0, required=required, parent=group)
    add_numeric(add, f"{key}_contact_gap", "Contact Gap", "1.8-2.2 mm", min_value=1.8, max_value=2.2,
                unit="mm", authority_reference="OEM", required=required, parent=group)
    add_numeric(add, f"{key}_contact_pressure", "Contact Pressure", ">15 gm", min_value=15.0, unit="gm",
                authority_reference="OEM", required=required, parent=group)
    add_numeric(add, f"{key}_plunger_travel", "Plunger Travel", "3 ± 0.3 mm", min_value=2.7, max_value=3.3,
                unit="mm", authority_reference="OEM", required=required, parent=group)
    add_confirm(add, f"{key}_male_pins_check", "Check the Male Pins of the Relay Base",
                done_word="Good", required=required, parent=group)
    add_confirm(add, f"{key}_cover_condition", "Condition of the Cover (Replace Compulsorily if Poor)",
                done_word="Good", authority_reference="SMI 173 dtd 02/02/95", required=required,
                parent=group)
    add_numeric(add, f"{key}_economy_resistance", "Economy Resistance (ABB)", "1KΩ ± 10%",
                unit="Ohm", authority_reference="OEM", required=False, parent=group)
    add_confirm(add, f"{key}_economy_resistance_soldering",
                "Economy Resistance Joint Soldering Condition (ABB)", done_word="Good",
                authority_reference="SMI 172 dtd 24/02/95", required=False, parent=group)
    add_confirm(add, f"{key}_contact_holder_clamping",
                "Ensure Proper Clamping on the Contact Holder and All Springs",
                done_word="Ensured", authority_reference="TC 142-Rev.1 dtd 18/09/23", required=required,
                parent=group)
    add_numeric(add, f"{key}_pickup", "Pick Up", "50V DC ± 5% (47.5 to 52.5)", min_value=47.5,
                max_value=52.5, unit="V", required=required, authority_reference="OEM (AAL)", parent=group)
    add_numeric(add, f"{key}_dropout", "Drop Out", "10-35V DC", min_value=10.0, max_value=35.0,
                unit="V", required=required, parent=group)

    mv_group = add(f"{key}_mv_drop", parent=group, field_label="Average Millivolt Drop Across I/L "
                   "After 3 Cycles", field_type="group", required=False)
    for il_key, il_label in [
        ("34_mv2", "I/L 3-4 (MV2)"), ("56_mv3", "I/L 5-6 (MV3)"), ("78_mv4", "I/L 7-8 (MV4)"),
        ("910_mv5", "I/L 9-10 (MV5)"), ("1112_mv6", "I/L 11-12 (MV6)"), ("1314_mv7", "I/L 13-14 (MV7)"),
        ("1516_mv8", "I/L 15-16 (MV8)"),
    ]:
        add_numeric(add, f"{key}_mv_{il_key}", il_label, "<90mV", max_value=90.0, unit="mV",
                    required=False, parent=mv_group)

    add_numeric(add, f"{key}_nc_il_count", "Number of NC I/L and Its Working", None, decimal_precision=0,
                authority_reference="TC 142-Rev.1 dtd 18/09/23", required=required, parent=group)
    add_numeric(add, f"{key}_no_il_count", "Number of NO I/L and Its Working", None, decimal_precision=0,
                authority_reference="TC 142-Rev.1 dtd 18/09/23", required=required, parent=group)
    add_text(add, f"{key}_data_index_no", "Data Index No.", required=required, parent=group)
    add_confirm(add, f"{key}_relay_cover_sealed", "The Relay Cover Should Be in Sealed Condition",
                done_word="Sealed", authority_reference="SMI 173-02/02/95; MS19-10/09/75",
                required=required, parent=group)
    return group


def build(add, set_page):
    add_date(add, "remove_date_sch", "Remove Date/Sch")
    add_date(add, "date_of_overhauling", "Date of Overhauling")
    add_date(add, "fitted_date", "Fitted on Loco Date")

    add_relay_group(add, "qsit", "QSIT")
    add_relay_group(add, "qems", "QEMS")
    add_relay_group(add, "qfl", "QFL")
    add_relay_group(add, "qvcd", "QVCD", required=False)

    must_change = add("must_change_item", field_label="Must Change Item", field_type="group",
                      required=False)
    add("gasket_relay_cover", parent=must_change, field_label="Gasket for Relay Cover (PL No. 23257428)",
        field_type="select", options="Changed, Not Changed", required=True, standard_value="Changed",
        negative_values="Not Changed")
    add("contact_tips_replacement", parent=must_change, field_label="Replacement of Contact Tips "
        "in Every IOH Schedule (PL No. 25648020)", field_type="select", options="Replaced, N/A",
        required=False, standard_value="Replaced")

    reliability = add("reliability_action_plan", field_label="Reliability Action Plan",
                      field_type="group", required=False)
    add_confirm(add, "interlock_paralleling", "Interlock Paralleling", done_word="Ensuring condition",
                authority_reference=None, parent=reliability)
    add("relay_life_replace", parent=reliability, field_label="If the Relay Has Completed Its "
        "Prescribed (Codal Life 18 Yrs) Service Life, Replace It", field_type="select",
        options="Replace, Same", required=False, standard_value="Replace")

    add("modifications", field_label="Modifications, if any", field_type="textarea", required=False)
    add("remarks", field_label="Remarks", field_type="textarea", required=False)


if __name__ == "__main__":
    run_seed_paged(
        equipment_code="PC-8_Conv",
        template_code="M2HR_PC8_CONV",
        technology="CONVENTIONAL",
        template_name="PC-8 Relays (AOH/TOH/IOH)",
        description="M2-HR: PC-8 Relays checksheet for Conventional locomotives.",
        build_fn=build,
    )
