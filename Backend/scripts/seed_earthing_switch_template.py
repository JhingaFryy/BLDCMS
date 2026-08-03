"""
Module 37: seeds the Earthing Switch checksheet template for BOTH E-Switch Conv and
E-Switch 3-Ph equipment IDs. Unlike the other shared PDFs in this module, the source sheet
itself marks each row's applicable Loco Type as "CONV." (Conventional only) or "CONV./3-PHASE"
(both) - E-Switch Conv gets every row, E-Switch 3-Ph gets only the rows explicitly marked
"CONV./3-PHASE". Each technology still gets its own template row against its own equipment_id,
never merged.

Run once: `venv/bin/python scripts/seed_earthing_switch_template.py`

Source: "Check Sheet for Earthing Switch of Conventional/3-Phase Loco (Rev. 14/11/2025)".
"""
from _aux_template_helpers import run_seed, add_final_remarks

# (key, label, options, negative, standard, applies_to_3phase)
ROWS = [
    ("clean_bv_box_outside", "Clean the Whole BV Box From Outside", "Done, Not Done", "Not Done",
     None, True),
    ("remove_top_cover", "Remove the Top Cover", "Done, Not Done", "Not Done", None, False),
    ("remove_old_grease_clean_chain", "Remove Old Grease and Clean the Chain and Internal Surface",
     "Done, Not Done", "Not Done", None, False),
    ("check_chain_cotter_pin_gear_bolt", "Check Chain, Cotter Pin, Chain Gear's Bolt, Fichet Key "
     "and Its Assembly for Any Damage", "OK, Damage Found", "Damage Found", None, False),
    ("remove_aux_switch_for_overhauling", "Remove the Aux. Switch and Give to M1HR for Overhauling",
     "Done, Not Done", "Not Done", None, False),
    ("new_grease_chain_fichet_key", "New Grease Provide to Chain, Fichet Key and Its Assembly",
     "Done, Not Done", "Not Done", "Servo Gem RR3", False),
    ("new_grease_jaw_moving_arm", "New Grease Provided to Between Jaw and the Connecting Part of "
     "Moving Arm; Check for Any Crack or Misalignment", "Done - No Crack, Issue Found",
     "Issue Found", None, True),
    ("remove_three_way_valve_clean", "Remove the Three-Way Valve and Clean It", "Done, Not Done",
     "Not Done", None, False),
    ("fit_valve_to_bv_box", "After Servicing the Valve Fitted to BV Box", "Done, Not Done",
     "Not Done", None, False),
    ("air_pressure_leakage_check", "After Fitting Valve, Check the Air Pressure Leakage by "
     "Applying 8.5KG/CM2 in BV Box Open Position and Close", "No Leakage, Leakage", "Leakage",
     None, False),
    ("check_fichet_key_aux_switch", "After Fitting Aux. Switch, Check the Working of Fichet Key, "
     "Aux. Switch", "OK, Not OK", "Not OK", None, False),
    ("moving_handle_key_freely", "Check the Moving Handle and Key Moving Freely", "OK, Not OK",
     "Not OK", None, True),
    ("moving_jaw_modification_ms405", "Moving Jaw Modification Done as Per MS-405", "Done, Not Done",
     "Not Done", None, True),
    ("oil_provided_oil_chamber", "Oil Provided in Oil Chamber on Top of BV Box", "Done, Not Done",
     "Not Done", None, False),
    ("rtv_water_entry_prevention", "Provide RTV to Prevent Water Entry", "Provided, Not Provided",
     "Not Provided", "RTV 685", True),
    ("bv_box_nut_bolt_screw_tightness", "Check Tightness of All BV Box's Nut-Bolt and Screw",
     "Tightened, Not Tightened", "Not Tightened", None, True),
]


def build_for_technology(applies_to_3phase: bool):
    def build(add):
        add("bv_box_serial_no", field_label="BV Box Sr. No.", field_type="text", required=True)
        add("bv_box_mfg_doc", field_label="MFG / DOC", field_type="text", required=False)

        for key, label, options, negative, standard, row_applies_to_3phase in ROWS:
            if applies_to_3phase and not row_applies_to_3phase:
                continue
            add(key, field_label=label, field_type="select", options=options, required=True,
                standard_value=standard, negative_values=negative)

        add_final_remarks(add)
    return build


if __name__ == "__main__":
    run_seed(
        equipment_code="E-Switch Conv", template_code="42", technology="CONVENTIONAL",
        template_name="Checksheet for Earthing Switch (Conventional)",
        description="Earthing Switch checksheet - Conventional - M9-HR section (all checkpoints).",
        build_fn=build_for_technology(applies_to_3phase=False),
    )
    run_seed(
        equipment_code="E-Switch 3-Ph", template_code="46", technology="3_PHASE",
        template_name="Checksheet for Earthing Switch (3-Phase)",
        description="Earthing Switch checksheet - 3-Phase - M9-HR section (only the checkpoints "
        "the source sheet marks 'CONV./3-PHASE' - see this file's module docstring).",
        build_fn=build_for_technology(applies_to_3phase=True),
    )
