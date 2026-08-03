"""
Module 41 (Phase 2): seeds the EMC (EM Contactor, 3-Phase locomotives, M1-HR section) checksheet
template.

Run once: `venv/bin/python scripts/seed_em_contactor_3phase_template.py`

Source: "3-Phase 80Amp - EM Contactor.pdf" - "Overhauling Chart-M1HR: 3 Phase 80 Amp EM
Contactor", an 11-item overhaul/test checklist. Coil resistance has two OEM sub-standards
depending on contactor variant (LC1D80FD vs LC1D80FW) - both kept together in one field's
standard_value text since only one variant applies per physical contactor.

Per the module's "Do NOT create fields for Loco Number/Technician/Supervisor Name/Signature"
rule, the sheet's own "Overhauling Done By"/"Signature of Staff"/"Signature of Supervisor" lines
are intentionally not modelled.
"""
from _aux_template_helpers import add_final_remarks, run_seed


def build(add):
    add("contactor_make", field_label="Make of Contact", field_type="text", required=True,
        standard_value="Noted")
    add("contactor_type", field_label="Type of Contactor", field_type="text", required=True,
        standard_value="Noted")
    add("contactor_sn", field_label="S.N.", field_type="text", required=False, standard_value="Noted")
    add("overhauling_date", field_label="Date of Overhauling", field_type="date", required=True)

    add("contactor_damage_defect_check", field_label="Visually Check the Contactor for Any Damage/Defects",
        field_type="select", options="No Damages/No Defects, Damage/Defects Found", required=True,
        standard_value="No Damages/No Defects", negative_values="Damage/Defects Found")
    add("cover_contacts_arc_chutes_clean", field_label="Remove the Cover and Clean the Contacts & Arc-Chutes",
        field_type="select", options="Done, Not Done", required=True, standard_value="Done",
        negative_values="Not Done")
    add("core_clean_dust_wipe", field_label="Remove the Core, Clean and Wipe Out the Dust", field_type="select",
        options="Done, Not Done", required=True, standard_value="Done", negative_values="Not Done")
    add("main_contacts_looseness_breakage_check", field_label="Check the Main Contacts for Looseness/Breakages "
        "& Ensure Tightness", field_type="select", options="No Loose/No Breakage, Loose/Breakage Found",
        required=True, standard_value="No Loose/No Breakage", negative_values="Loose/Breakage Found")
    add("aux_switch_fitment_check", field_label="Check the Proper Fitment of Aux. Switch After Overhauling",
        field_type="select", options="Properly Locked, Not Properly Locked", required=True,
        standard_value="It Should Be Properly Locked", negative_values="Not Properly Locked")
    add("contactor_opening_check", field_label="Check the Opening of Contactor", field_type="select",
        options="Perfect, Not Perfect", required=True, standard_value="Perfect", negative_values="Not Perfect")
    add("coil_resistance_20c", field_label="Coil Resistance at 20°C (OEM)", field_type="numeric_range",
        required=True, unit="Ohm", min_value=492.0, max_value=648.0, decimal_precision=0,
        standard_value="For LC1D80FD: 600±8 Ohm; For LC1D80FW: 500±8 Ohm")
    add("min_pickup_voltage", field_label="Minimum Pickup Voltage (OEM)", field_type="numeric_range",
        required=True, unit="V", min_value=0.0, max_value=77.0, decimal_precision=0,
        standard_value="≤77 Volts")
    add("dropout_voltage", field_label="Check the Dropout Voltage (OEM)", field_type="numeric_range",
        required=True, unit="V", min_value=0.0, max_value=15.0, decimal_precision=0,
        standard_value="<15 Volts")
    add("main_contacts_continuity_check", field_label="Check the Continuity and Discontinuity of Main Contacts",
        field_type="select", options="Perfect, Not Perfect", required=True, standard_value="Perfect",
        negative_values="Not Perfect")
    add("aux_contacts_continuity_check", field_label="Check the Continuity and Discontinuity of Aux Contacts",
        field_type="select", options="Perfect, Not Perfect", required=True, standard_value="Perfect",
        negative_values="Not Perfect")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="EMC", template_code="128", technology="3_PHASE",
        template_name="Checksheet for EM Contactor",
        description="Overhauling checksheet for 3 Phase 80 Amp EM Contactor - M1-HR section.",
        build_fn=build,
    )
