"""
Module 41 (Phase 2): seeds the SRPCC (SR Pre-Charging Contactor, 3-Phase locomotives, M1-HR
section) checksheet template.

Run once: `venv/bin/python scripts/seed_sr_precharging_contactor_3phase_template.py`

Source: "SR Contactor (Pre-Charging).pdf" - "Overhauling Chart-M1HR: Discharging/Pre Charging
Contactor", a 13-item overhaul/test checklist (arc-chute/arcing-horn, air gap, coil resistance,
pick-up/drop-out voltage, Q factor, setting nut tightness). Item 13 ("Paralleling of auxi I/L and
auxi contactors as per M.S.-0419 rev0 date-20-12-12") is shown struck through and left blank on
both reference samples, indicating the standard it cites has been superseded - kept as an optional
field rather than dropped or given a fabricated standard.
"""
from _aux_template_helpers import add_final_remarks, run_seed


def build(add):
    add("contactor_sn", field_label="S.N.", field_type="text", required=False, standard_value="Noted")
    add("contactor_make", field_label="Make of Contactor", field_type="text", required=True,
        standard_value="Noted")
    add("contactor_type", field_label="Type of Contactor", field_type="text", required=True,
        standard_value="Noted")
    add("overhauling_date", field_label="Date of Overhauling", field_type="date", required=True)

    add("contactor_defect_visual_check", field_label="Visual Check the Condition of Contactor for Any Defects",
        field_type="select", options="No Defect, Defect Found", required=True, standard_value="No Defect",
        negative_values="Defect Found")
    add("core_assembly_coil_clean", field_label="Clean Core Assembly of Coil With Clean Cloth", field_type="select",
        options="Cleaned, Not Cleaned", required=True, standard_value="Cleaned", negative_values="Not Cleaned")
    add("arc_chute_condition_check", field_label="Check the Condition of Arc-Chute", field_type="select",
        options="OK, Not OK", required=True,
        standard_value="No Flash Marks, No Play in Bottom Arc-Horn", negative_values="Not OK")
    add("arcing_horn_polishing", field_label="Arcing Horn Polishing to Be Done", field_type="select",
        options="Done, Not Done", required=True, standard_value="Done", negative_values="Not Done")
    add("main_contacts_air_gap", field_label="Air Gap of Main Contacts (OEM Manual)", field_type="numeric_range",
        required=True, unit="mm", min_value=20.5, max_value=23.5, decimal_precision=1)
    add("coil_resistance_20c", field_label="Coil Resistance at Room Temp. 20°C (OEM Manual)",
        field_type="number", required=True, unit="Ohm", standard_value="462.0 Ω ± 8% or 371.0 Ω ± 8%")
    add("fixed_mobile_contacts_alignment_check", field_label="Check Alignment of Fixed & Mobile Contacts",
        field_type="select", options="Perfect, Not Perfect", required=True, standard_value="Perfect",
        negative_values="Not Perfect")
    add("pick_up_voltage_closing", field_label="Pick Up Voltage (Closing) (OEM Manual)", field_type="numeric_range",
        required=True, unit="V", min_value=0.0, max_value=77.0, decimal_precision=1, standard_value="<77.0 V")
    add("drop_out_voltage_opening", field_label="Drop Out Voltage (Opening) (OEM Manual)",
        field_type="numeric_range", required=True, unit="V", min_value=11.0, max_value=100.0,
        decimal_precision=1, standard_value=">11.0 V")
    add("main_aux_contacts_continuity_check", field_label="Check Continuity & Discontinuity of Main Contacts & "
        "Aux. I/L. NO/NC", field_type="select", options="Perfect, Not Perfect", required=True,
        standard_value="Perfect", negative_values="Not Perfect")
    add("coil_q_factor_check", field_label="Check the 'Q' Factor of Coil", field_type="number", required=True,
        standard_value="Record Value")
    add("setting_nut_tightness_check", field_label="Check the Tightness of Setting Nut. Ensure Red Marking of "
        "Setting Nut", field_type="select", options="Done, Not Done", required=True, standard_value="To Be Done",
        negative_values="Not Done")
    add("auxi_il_contactors_paralleling", field_label="Paralleling of Auxi I/L and Auxi Contactors (M.S.-0419 "
        "Rev0, Dated 20-12-12)", field_type="select", options="Done, Not Applicable", required=False)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="SRPCC", template_code="131", technology="3_PHASE",
        template_name="Checksheet for SR Pre-Charging Contactor",
        description="Overhauling checksheet for Discharging/Pre Charging Contactor - 3-Phase - M1-HR section.",
        build_fn=build,
    )
