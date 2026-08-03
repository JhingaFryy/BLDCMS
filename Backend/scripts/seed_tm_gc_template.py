"""
Module 32: seeds the M35-TM Traction Motor "GC" (General Cleaning) template - the 2-page
"TOH PROFORMA FOR 3-PHASE TM (TYPE 6FRA6068)" reference checksheet.

Module 32.1: confirmed this is the correct GC/Overhaul mapping - per the module's own
identification rule ("the checksheet whose heading contains TOH is the GC checksheet"), this
document's heading literally is "TOH PROFORMA...", so it is GC; the other supplied document
("Assembly/Fitment of TM type 6FRA6068 (New/Overhauling)") is Overhaul. "GC"/"Overhaul" are
internal identification labels only - the PDF's own heading text is left exactly as printed.

Run once: `venv/bin/python scripts/seed_tm_gc_template.py`

Header block (Make of TM/Sr. No./TM Position/etc.) is modeled as page-1 informational fields, same
as every other equipment template's own header info (M35-TM has no section-wide common page the
way M35-Aux does, so each TM template carries its own header block).

Module 32.2: Loco No. & Type/Homing Shed/Railways/Date (header) and Technician (signature) are
deliberately absent - all five duplicate data the app already captures automatically elsewhere
(the selected Locomotive, and the submission timestamp/technician identity resolved from
ChecksheetHeader). See scripts/remove_tm_header_redundant_fields.py for the full rationale.

Distinctive validation pattern: S.N. 6's "Difference value of phase UV,VW,UW<0.015" is a flat
millihenry cutoff, not a percentage of the readings - modeled with the new
validation_rule='absolute_difference' rule (see app/services/validation_service.py), reusing the
existing validation_threshold column with a different interpretation than percentage_difference.
S.N. 7's "<5%" difference IS a true percentage, so that one reuses percentage_difference unchanged.
"""
from _tm_template_helpers import run_seed


def build(add):
    # --- Header block (informational entry, not S.N. checking points) ---
    # Module 32.2: Loco No. & Type / Homing Shed / Railways / Date deliberately NOT seeded here -
    # all four are redundant with data the app already captures elsewhere (Locomotive is selected
    # before this template ever loads, and the submission timestamp already exists on
    # ChecksheetHeader.submitted_at) - see scripts/remove_tm_header_redundant_fields.py for the
    # full rationale. The remaining TM-specific technical fields below are unaffected.
    add("make_of_tm", field_label="Make of TM", field_type="text", required=False)
    add("mfd_of_tm", field_label="M.F.D. of TM", field_type="text", required=False)
    add("sr_no_of_tm", field_label="Sr. No. of TM", field_type="text", required=True)
    add("tm_position", field_label="TM Position", field_type="text", required=False)
    add("stator_sr_no_make", field_label="Stator Sr. No. & Make", field_type="text", required=False)
    add("pinion_make_month_year", field_label="Pinion Make/Month/Year", field_type="text", required=False)
    add("rotor_no", field_label="Rotor No", field_type="text", required=False)
    add("nos_teeth_pinion", field_label="Nos. of Teeth on Pinion", field_type="number", required=False)
    add("bearing_make_de", field_label="Bearing Make/Sl. No./Mfd. Of DE", field_type="text", required=False)
    add("bearing_make_nde", field_label="Bearing Make/Sl. No./Mfd. Of NDE", field_type="text", required=False)

    # --- S.N. 1-17 checking points ---
    add(
        "tm_blowing_cleaning", field_label="TM Blowing & Cleaning",
        field_type="boolean", required=True,
        standard_value="Done", authority_reference="Shed practice",
        negative_values="false",
    )
    add(
        "temp_sensor_sticker_blue", field_label="Check Temp. Sensor Sticker Blue",
        field_type="boolean", required=True,
        standard_value="Confirmed", authority_reference="Shed practice",
        negative_values="false",
    )
    add(
        "ir_value", field_label="IR Value",
        field_type="number", required=True, unit="MOhm",
    )
    add(
        "rdpt_holder_plate", field_label="RDPT of Holder Plate",
        field_type="select", options="OK, Not OK", required=True,
        standard_value="OK", authority_reference="Shed practice",
        negative_values="Not OK",
    )

    temp_sensor_resistance = add(
        "temp_sensor_resistance", field_label="Measure the Resistance of Temp Sensor",
        field_type="group", required=False,
    )
    add("temp_sensor_resistance_ab", parent=temp_sensor_resistance, field_label="AB", field_type="number", required=True, unit="Ohm")
    add("temp_sensor_resistance_cd", parent=temp_sensor_resistance, field_label="CD", field_type="number", required=True, unit="Ohm")

    winding_inductance = add(
        "winding_inductance", field_label="Winding Inductance",
        field_type="group", required=False,
        standard_value="Difference value of phase UV,VW,UW < 0.015",
        validation_rule="absolute_difference", validation_threshold=0.015,
    )
    add("winding_inductance_uv", parent=winding_inductance, field_label="UV", field_type="number", required=True, unit="mH")
    add("winding_inductance_vw", parent=winding_inductance, field_label="VW", field_type="number", required=True, unit="mH")
    add("winding_inductance_uw", parent=winding_inductance, field_label="UW", field_type="number", required=True, unit="mH")

    internal_resistance = add(
        "internal_resistance_winding", field_label="Internal Resistance of Winding",
        field_type="group", required=False,
        standard_value="Difference value of phase UV,VW,UW < 5%",
        validation_rule="percentage_difference", validation_threshold=5.0,
    )
    add("internal_resistance_uv", parent=internal_resistance, field_label="UV", field_type="number", required=True, unit="Ohm")
    add("internal_resistance_vw", parent=internal_resistance, field_label="VW", field_type="number", required=True, unit="Ohm")
    add("internal_resistance_uw", parent=internal_resistance, field_label="UW", field_type="number", required=True, unit="Ohm")

    add(
        "tightness_terminal_connection", field_label="Check Tightness of Terminal Connection",
        field_type="boolean", required=True,
        standard_value="Tight", authority_reference="Shed practice",
        negative_values="false",
    )
    add(
        "tightness_bellow_plate", field_label="Check Tightness of Bellow Plate",
        field_type="boolean", required=True,
        standard_value="Tight", authority_reference="Shed practice",
        negative_values="false",
    )
    add(
        "pgr_cleaning", field_label="PGR Cleaning",
        field_type="boolean", required=True,
        standard_value="Done", authority_reference="Shed practice",
        negative_values="false",
    )
    add(
        "pinion_mpt", field_label="Pinion MPT",
        field_type="select", options="No Crack, Crack Found", required=True,
        standard_value="No crack", authority_reference="Shed practice",
        negative_values="Crack Found",
    )
    add(
        "pinion_cleaning_k_value", field_label="Pinion Cleaning & Check 'K' Value",
        field_type="text", required=True,
    )
    add(
        "grease_sample_laboratory", field_label="Grease Sample of TM to Laboratory",
        field_type="boolean", required=True,
        standard_value="Sent", authority_reference="Shed practice",
        negative_values="false",
    )
    add(
        "tightness_pgr_nde_locking_plate", field_label="Check Tightness of PGR & NDE Side Locking Plate",
        field_type="boolean", required=True,
        standard_value="Tight", authority_reference="Shed practice",
        negative_values="false",
    )
    add(
        "check_tm_visually", field_label="Check TM Visually",
        field_type="select", options="OK, Not OK", required=True,
        standard_value="OK", authority_reference="Shed practice",
        negative_values="Not OK",
    )

    play = add("radial_axial_play", field_label="Radial Play / Axial Play", field_type="group", required=False)
    add("radial_play", parent=play, field_label="Radial Play", field_type="number", required=True, unit="mm")
    add("axial_play", parent=play, field_label="Axial Play", field_type="number", required=True, unit="mm")

    grease_history = add(
        "grease_sample_old_history", field_label="Grease Sample Old History",
        field_type="group", required=False,
    )
    add("grease_sample_old_history_a", parent=grease_history, field_label="a.", field_type="text", required=False)
    add("grease_sample_old_history_b", parent=grease_history, field_label="b.", field_type="text", required=False)
    add("grease_sample_old_history_c", parent=grease_history, field_label="c.", field_type="text", required=False)
    add("grease_sample_old_history_d", parent=grease_history, field_label="d.", field_type="text", required=False)

    add(
        "post_final_test_grease_cleaning", field_label="After Final Testing of Loco, TM Extra Grease Cleaning at PGR and Sensor",
        field_type="boolean", required=True,
        standard_value="Done", authority_reference="Shed practice",
        negative_values="false",
    )

    # --- Must Change Items 3-Phase TM Type 6FRA6068 ---
    must_change = add("must_change_item", field_label="Must Change Items 3-Phase TM Type 6FRA6068", field_type="group", required=False)
    add(
        "must_change_o_ring", parent=must_change, field_label='"O" Ring Changing',
        field_type="boolean", required=True, negative_values="false",
    )
    add(
        "must_change_temp_gasket", parent=must_change, field_label="Temp. Gasket",
        field_type="boolean", required=True, negative_values="false",
    )
    add(
        "must_change_jbox_gasket", parent=must_change, field_label="J/Box Gasket",
        field_type="boolean", required=True, negative_values="false",
    )
    add(
        "must_change_grease", parent=must_change, field_label="Grease",
        field_type="boolean", required=True, negative_values="false",
    )

    # Module 32.2: "Technician" signature field deliberately NOT seeded here - the technician's
    # name/employee ID are already resolved automatically from ChecksheetHeader.technician_mobile
    # and shown in the PDF; there is no need for the technician to type their own name.


if __name__ == "__main__":
    run_seed(
        equipment_code="TM- 3Ph", template_code="20", technology="3_PHASE", maintenance_type="GC",
        template_name="Checksheet for Traction Motor (GC)",
        description="TOH Proforma for 3-Phase TM (Type 6FRA6068) - General Cleaning.",
        build_fn=build,
    )
