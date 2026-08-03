"""
Module 35: seeds the Transformer 3-Phase (M8-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_transformer_3phase_template.py`

Source: CHECK SHEET FOR 3 PHASE LOCOMOTIVES, M8-HR ACTIVITIES IN TOH/IOH SCHEDULE
(ELS/TRS/BL/M8/15 Rev-1) - sections "1. MAIN TRANSFORMER" and "2. MAIN BUSHING HV CABLE WITH
PLUG" (equipment_code "Transformer 3-phase" is named "Transformer & Main Bushing" in the DB,
confirming both sections belong to this one equipment), plus the "List of Must Change Items of
3 Phase drive Loco in TOH/IOH" table (both listed items are transformer-specific - silica gel and
transformer-terminal/conservator-tank gaskets), implemented as dedicated fields per Module 35's
explicit instruction not to merge them into remarks.

The "STATUS OF RDSO SMI/MS/TC" section on the same source page is reference/documentation only
and is deliberately NOT implemented here (per Module 35's explicit instruction).

Several checkpoints only apply during IOH ("N.A. as TOH" on the sample sheet, which was filled
for a TOH schedule) - modeled with an explicit "N/A (IOH only)" select option rather than making
the field conditionally required, since one static template must serve both schedules.
"""
from _aux_template_helpers import run_seed, add_final_remarks


def add_select(add, key, label, options, negative=None, standard=None, authority=None, required=True):
    return add(
        key, field_label=label, field_type="select", options=", ".join(options), required=required,
        standard_value=standard, authority_reference=authority,
        negative_values=negative,
    )


IOH_ONLY_OPTIONS = ["Replaced", "N/A (IOH only)", "Not Replaced"]
REF_3135 = "RDSO L.No. EL/3.1.35/16 dt. 7.2.12"


def build(add):
    add("transformer_serial_no", field_label="Main Transformer Serial No.", field_type="text", required=True)
    add("transformer_make_year", field_label="Make / Year", field_type="text", required=False)

    oil_test = add("transformer_oil_sample_test", field_label="Test Oil Sample for BDV, DGA, Acidity and "
        "Other Lab Tests (Conduct Centrifuging of the Oil)", field_type="group", required=False,
        authority_reference=REF_3135)
    add("transformer_oil_bdv", parent=oil_test, field_label="BDV After Filtration", field_type="numeric_range",
        required=True, unit="KV", min_value=60.0, decimal_precision=1, standard_value=">60 KV (After filtration)")
    add("transformer_oil_dga", parent=oil_test, field_label="DGA Result (as per RDSO SMI 138 Rev.1)",
        field_type="select", options="Normal, Abnormal", required=True, standard_value="DGA Normal",
        negative_values="Abnormal")

    add_select(add, "transformer_connections_earthing_bushing_insulators", "Visually Inspect Electrical "
        "Connections, Earthing Cable, Bushing and Insulators for Cracks/Chips/Impact Damage "
        "(Clean Connectors, Replace Damaged/Chipped/Cracked Insulators)",
        ["Good Condition", "Damaged"], negative="Damaged", authority=REF_3135)
    add_select(add, "transformer_cork_sheet_replaced_ioh", "Replace All Rubberised Cork Sheet in IOH",
        IOH_ONLY_OPTIONS, negative="Not Replaced", authority=REF_3135)
    add_select(add, "transformer_tfp_bushing_rubber_seals_replaced_ioh", "Replace All TFP Bushings "
        "Rubber Seals in IOH", IOH_ONLY_OPTIONS, negative="Not Replaced", authority=REF_3135)
    add_select(add, "transformer_foundation_bolts_bushing_nuts_tightness", "Check Transformer Foundation "
        "Bolts and Bushing Nuts Tightness With Proper Torque", ["Intact", "Not Intact"],
        negative="Not Intact", authority=REF_3135)
    add_select(add, "transformer_silica_gel_replaced_breather", "Replace the Silica Gel in Breather Assembly",
        ["Replaced", "Not Replaced"], negative="Not Replaced", authority=REF_3135)
    add_select(add, "transformer_oil_maintenance_in_service", "Maintenance of Transformer Oil in Service",
        ["Followed", "Not Followed"], negative="Not Followed", authority="RDSO/ELRS/SMI/158 dtd. 19.01.95")
    add_select(add, "transformer_bushing_gaskets_replaced_ioh", "Replacement of Bushing Gaskets During IOH",
        IOH_ONLY_OPTIONS, negative="Not Replaced", authority="ELRS/TC/0076 dt. 17.09.2002")
    add_select(add, "transformer_tfp_protection_cover_check", "Check the Main TFP and Its Protection Cover "
        "for Damage/Crack & Oil Leakage", ["Intact", "Damaged"], negative="Damaged",
        standard="Checked & Found intact", authority="RDSO TC 76 Rev.2")
    add_select(add, "transformer_tfp_bushing_oil_leakage", "Check the Oil Leakage From TFP Bushings, "
        "Attend if Any Leakage", ["No Leakage", "Leakage"], negative="Leakage")
    add_select(add, "transformer_earthing_shunt_check", "Check Earthing Shunt of Transformer (3 Nos.)",
        ["Intact", "Not Intact"], negative="Not Intact", authority="SMI 248")
    add_select(add, "transformer_foundation_bolt_intactness", "Check All 16 Nos. Foundation Bolt of "
        "Transformer for Intactness", ["Intact", "Not Intact"], negative="Not Intact")
    add_select(add, "transformer_foundation_crack_dpt", "Transformer Foundation Crack to Check by DPT",
        ["No Crack", "Crack Found"], negative="Crack Found")

    add_select(add, "transformer_hv_cable_plug_inspection", "Visually Inspect the HV Cable at the Main "
        "Transformer Connection for Damage or Oil Contamination (Replace if Damaged/Contaminated)",
        ["Good Condition", "Replaced", "Damaged"], negative="Damaged", standard="Checked/Replaced",
        authority=REF_3135)

    must_change = add("transformer_must_change_items", field_label="Must Change Items",
                      field_type="group", required=False)
    add("must_change_transformer_silica_gel", parent=must_change, field_label="Transformer Silica Gel",
        field_type="select", options="Replaced, Not Replaced", required=True,
        standard_value="04 Kg (TOH/IOH)")
    add("must_change_transformer_conservator_gaskets", parent=must_change, field_label="Set of Nilrile "
        "Bonded Cork Gaskets & Rubber Gaskets of Transformer Terminals & Conservator Tank",
        field_type="select", options="Replaced, N/A (IOH only), Not Replaced", required=True,
        standard_value="1 SET (IOH)")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="Transformer 3-phase", template_code="27", technology="3_PHASE",
        template_name="Checksheet for Transformer (3-Phase)",
        description="Main Transformer + Main Bushing HV Cable With Plug (3-Phase) checksheet - M8-HR section.",
        build_fn=build,
    )
