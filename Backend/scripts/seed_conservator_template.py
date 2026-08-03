"""
Module 35: seeds the Conservator (Conservator Tank 1 & 2, 3-Phase, M8-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_conservator_template.py`

Source: CHECK SHEET FOR 3 PHASE LOCOMOTIVES (ELS/TRS/BL/M8/15 Rev-1), section
"9. CONSERVATOR 1 & 2". The "1 & 2" in the title means these checks apply to both conservator
tanks generically - unlike CGR (Module 34), this table has a single Reference/Standard/Actual
column set (no separate CGR-1/CGR-2/CGR-3-style per-unit columns), so it is implemented as plain
fields, not a per-unit group.
"""
from _aux_template_helpers import run_seed, add_final_remarks

REF_3135 = "RDSO L.No. EL/3.1.35/16 dt. 7.2.12"


def build(add):
    add("conservator_foundation_welding_stand_bolts", field_label="Check Conservator Foundation Welding "
        "and Conservator Stand Bolts for Tightness & Ensure Provision of Double Nut", field_type="select",
        options="Intact, Not Intact", required=True, standard_value="Intact", negative_values="Not Intact",
        authority_reference=REF_3135)
    add("conservator_oil_level_gauge_check", field_label="Check the Oil Level on the Gauge Situated on "
        "the Conservator (Top Up if Required); Check for Any Sign of Leakage", field_type="select",
        options="No Leakage, Leakage", required=True, negative_values="Leakage")
    add("conservator_prismatic_gauge_cleaned", field_label="Prismatic Level Gauge - Clean the Gauge With "
        "Dry Cloth to Check for Leaks", field_type="select", options="Cleaned, Not Cleaned", required=True,
        negative_values="Not Cleaned")

    coupling = add("conservator_stuchi_coupling_tightness", field_label="Ensure Tightness of Stuchi "
        "Coupling, Base Plate and Conservator Tank Foundation Bolt During Overhauling (As Per OEM "
        "Guidelines & Present Practices Followed by Shed)", field_type="group", required=False,
        standard_value="Tighten, no leakage")
    add("conservator_coupling_tightness", parent=coupling, field_label="Tightness", field_type="select",
        options="Tightened, Loose", required=True, negative_values="Loose")
    add("conservator_coupling_leakage", parent=coupling, field_label="Leakage Check", field_type="select",
        options="No Leakage, Leakage", required=True, negative_values="Leakage")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="Conservator", template_code="34", technology="3_PHASE",
        template_name="Checksheet for Conservator",
        description="Conservator Tank 1 & 2 (3-Phase) checksheet - M8-HR section.",
        build_fn=build,
    )
