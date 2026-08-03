"""
Module 46: seeds the M2-HR Air Flow Relay (Conventional) checksheet template.

Source: "air flow relay.pdf" (Check sheet for airflow relay). Loco number, technician name/
signature and supervisor name/signature are intentionally excluded - handled elsewhere in BL-DCMS.

Run: `venv/bin/python scripts/seed_afr_conv_template.py`
"""
from _m2hr_template_helpers import add_date, add_numeric, add_text, run_seed_paged


def add_pickup_dropout(add, key, label, pickup_std, dropout_std, authority):
    group = add(key, field_label=label, field_type="group", required=False, authority_reference=authority)
    add_numeric(add, f"{key}_pickup", "Pick Up", pickup_std, unit="mm WC", decimal_precision=1, parent=group)
    add_numeric(add, f"{key}_dropout", "Drop Out", dropout_std, unit="mm WC", decimal_precision=1, parent=group)
    return group


def build(add, set_page):
    add_text(add, "sr_no_of_relay", "Sr. No. of Relay", required=True)
    add_text(add, "make", "Make", required=True)
    add_date(add, "remove_date_sch", "Remove Date/Sch")
    add_date(add, "date_of_overhauling", "Date of Overhauling")

    ir_group = add("ir_value_check", field_label="Check IR Value with 500V Megger", field_type="group",
                   required=False, authority_reference="Shed practice")
    add_numeric(add, "ir_terminal_to_body", "Terminal to Body", "10MΩ (Min)", min_value=10.0,
                unit="MOhm", parent=ir_group)
    add_numeric(add, "ir_between_terminals", "Between Both Terminals", "10MΩ (Min)", min_value=10.0,
                unit="MOhm", parent=ir_group)

    add("continuity_aux_contact", field_label="Check Continuity Between Aux Contact (Normal & Operation)",
        field_type="select", options="Continuity OK, Continuity Not OK", required=True,
        standard_value="Continuity OK", negative_values="Continuity Not OK")

    add_pickup_dropout(add, "qvmt1", "QVMT1", "50 mm WC", "40/30 mm WC", "WR/BZ/154/2019")
    add_pickup_dropout(add, "qvmt2", "QVMT2", "50 mm WC", "40/30 mm WC", "WR/BL/68/2021")
    add_pickup_dropout(add, "qvrh", "QVRH", "25 mm WC", "15/10 mm WC", "SR/PER/388/2024")
    add_pickup_dropout(add, "qvsl1", "QVSL1", "30 mm WC", "20/15 mm WC", "NR/CB/131/2023")
    add_pickup_dropout(add, "qvsl2", "QVSL2", "30 mm WC", "20/15 mm WC", "WR/BRCY/56/2018")
    add_pickup_dropout(add, "qvsi1", "QVSI1", "-30 mm WC", "-20/15 mm WC", "CR/BSL/335/2016")
    add_pickup_dropout(add, "qvsi2", "QVSI2", "-30 mm WC", "-20/15 mm WC", "WR/BL/16/2019")

    must_change = add("must_change_items", field_label="Must Change Items", field_type="group", required=False)
    add("diaphragm_replace_aoh_ioh", parent=must_change,
        field_label="Replace Diaphragm in AOH/IOH", field_type="select",
        options="Replaced, Not Replaced", required=True, standard_value="Replaced",
        negative_values="Not Replaced")
    add("micro_switch_ioh", parent=must_change,
        field_label="Micro Switch in IOH", field_type="select",
        options="Replaced, Not Replaced", required=False, standard_value="Replaced",
        negative_values="Not Replaced")


if __name__ == "__main__":
    run_seed_paged(
        equipment_code="AFR_Conv",
        template_code="M2HR_AFR_CONV",
        technology="CONVENTIONAL",
        template_name="Check Sheet for Air Flow Relay (AOH/TOH/IOH)",
        description="M2-HR: Air Flow Relay checksheet for Conventional locomotives.",
        build_fn=build,
    )
