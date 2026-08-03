"""
Module 43: seeds the Arm_Conv (Armature, Conventional locomotives, M35-TM section) checksheet
template.

Run once: `venv/bin/python scripts/seed_armature_conv_template.py`

Source: "FR/TM/AC/07 - Overhauling and Assembling Schedule - Armature" (Locomotive Care Centre
Ratlam, Western Railway), a 21-item overhaul checklist covering ultrasonic flaw detection,
cleaning, PTFE ring/balancing/commutator inspection, mica groove dimensions, commutator diameter/
resistance measurement, oven baking, varnishing, IR value, and PE/CE bearing inner race checks.

No `maintenance_type` is set (stays NULL) - see seed_rocker_brush_holder_conv_template.py's
docstring for why this keeps the Android app's TM Number/GC-Overhaul UI from triggering for
Conventional equipment.
"""
from _aux_template_helpers import add_final_remarks, run_seed


def build(add):
    add("ultrasonic_flaw_detection_check", field_label="Ensure Ultrasonic Flaw Detection Test Is Conducted and "
        "the Shaft Is Passed", field_type="select", options="Passed, Failed", required=True,
        authority_reference="SMI 150")
    add("armature_blow_clean", field_label="Blow the Armature With Compressed Air, Clean the Armature "
        "Thoroughly - Do Not Use Kerosene at the CE Side Banding, Commutator and Teflon V Ring",
        field_type="select", options="Done, Not Done", required=True)
    add("armature_visual_inspection", field_label="Examine Thoroughly for Rubbing Marks, Damaged Insulation, "
        "Over Heating, Loose Wedge, Shaft Defects Etc.", field_type="select",
        options="Good, Details of Attention Paid", required=True)
    add("ptfe_ring_condition_check", field_label="Check the Condition of PTFE Ring and Ensure Proper Adhesion "
        "of the Same", field_type="select", options="Good, Replaced", required=True)
    add("balancing_pieces_check", field_label="Ensure Balancing Pieces Are Fixed Properly by Gently Tapping "
        "With Small Hammer and Feel the Vibration - if Required Do Additional Welding at Feasible Locations",
        field_type="select", options="Good, Details of Attention Paid", required=True)
    add("oil_injection_path_threads_check", field_label="Ensure Good Condition of Oil Injection Path & Threads "
        "on Both Sides of Shaft (Specify Whether the Shaft Is Modified)", field_type="select",
        options="Done, Not Done", required=True)
    add("commutator_flash_overheating_check", field_label="Examine the Commutator for Flash Marks, Over "
        "Heating, Pitting Marks Etc. - No Such Damage Permitted", field_type="select",
        options="Good, Details of Attention Paid", required=True)
    add("commutator_lathe_turning", field_label="Turn the Commutator in Multi Purpose Armature Lathe if the "
        "Ovality During Dismantling Is More Than 0.06mm or There Is Ridge Formation", field_type="select",
        options="Done, Not Applicable", required=True)

    mica_group = add("mica_groove_measurement", field_label="Check the Depth & Width of Mica Groove, Take "
        "Undercut and Chamfer Edge (Checked Manually by Shed Made Gauge)", field_type="group", required=False,
        authority_reference="Camtech Manual/2005/TM/(H1.20 Jan 2005) Pg No:02")
    add("mica_groove_depth_min", parent=mica_group, field_label="Depth", field_type="numeric_range", required=True,
        unit="mm", min_value=1.2, max_value=2.5, decimal_precision=2)
    add("mica_groove_width", parent=mica_group, field_label="Width", field_type="number", required=True, unit="mm",
        standard_value="1.2mm")
    add("mica_groove_chamfer", parent=mica_group, field_label="Sharp Edge Chamfer", field_type="number",
        required=True, unit="mm", standard_value="0.3mm")

    add("mica_residue_removal", field_label="Remove the Mica Residues From the Sides of the Inner Walls of "
        "Commutator Segments Manually", field_type="select", options="Done, Not Done", required=True)
    add("commutator_deburring", field_label="Do the De Burring of the Commutator", field_type="select",
        options="Done, Not Done", required=True)
    add("commutator_diameter", field_label="Measure Commutator Diameter (Tool Shed Made Gauge)",
        field_type="numeric_range", required=True, unit="mm", min_value=380.0, max_value=400.0,
        decimal_precision=1, standard_value="380mm-400mm (Min. Usable Diameter)",
        authority_reference="Camtech Manual/2005/TM/(H1.20 Jan 2005) Pg No:39")
    add("bar_to_bar_resistance_check", field_label="Measure Bar to Bar Resistance of Armature and Ensure It Is "
        "Passed (Reading Sheet Attached)", field_type="select", options="Passed, Failed", required=True,
        standard_value="±3 STD Deviations", authority_reference="RDSO/ELRS/WAG5/SMI/51")
    add("armature_oven_bake", field_label="Clean the Armature by Compressed Air, Heat It in an Oven",
        field_type="select", options="Done, Not Done", required=True, standard_value="90°C for 4 Hours")
    add("red_insulation_varnish_applied", field_label="Apply Red Insulation Varnish", field_type="select",
        options="Done, Not Done", required=True)
    add("ptfe_ring_gap_fill", field_label="Fill Up the Gap Between PTFE Ring and Commutator and Gap Between "
        "PTFE Ring and Metal 'V' Ring With Epoxy/Araldite", field_type="select", options="Done, Not Done",
        required=True)
    add("armature_ir_value", field_label="After Cooling Down, Measure the IR Value of Armature",
        field_type="numeric_range", required=True, unit="MOhm", min_value=10.0, max_value=1000.0,
        decimal_precision=1, standard_value="Above 10 MΩ With 1KV Megger",
        authority_reference="Camtech Manual/2005/TM/(H1.20 Jan 2005) Pg No:26")

    inner_race_group = add("bearing_inner_races_check", field_label="Examine the Bearing Inner Races for "
        "Crack, Chipping, Pitting, Colour Change - if Any Noticed, Replace the Entire Bearing Set",
        field_type="group", required=False, standard_value="No Chipping, No Pitting, No Crack")
    add("bearing_inner_races_peb", parent=inner_race_group, field_label="PEB", field_type="select",
        options="OK, Chipping/Pitting/Crack Found", required=True, negative_values="Chipping/Pitting/Crack Found")
    add("bearing_inner_races_ceb", parent=inner_race_group, field_label="CEB", field_type="select",
        options="OK, Chipping/Pitting/Crack Found", required=True, negative_values="Chipping/Pitting/Crack Found")

    tightness_group = add("bearing_inner_races_tightness_check", field_label="Visually Examine Tightness of "
        "Both the Inner Races on the Shaft and Good Condition of Bearings Stoppers", field_type="group",
        required=False, standard_value="No Looseness")
    add("bearing_tightness_peb", parent=tightness_group, field_label="PEB", field_type="select",
        options="OK, Looseness Found", required=True, negative_values="Looseness Found")
    add("bearing_tightness_ceb", parent=tightness_group, field_label="CEB", field_type="select",
        options="OK, Looseness Found", required=True, negative_values="Looseness Found")

    add("deflector_seat_dia", field_label="Record Deflector Seat Dia (by Outside Micrometer 0-150mm)",
        field_type="numeric_range", required=True, unit="mm", min_value=140.092, max_value=140.209,
        decimal_precision=3, standard_value="140+0.117mm +0.092mm",
        authority_reference="Camtech Manual/2005/TM/(H1.20 Jan 2005) Pg No:39")
    add("deflector_bore", field_label="Record Deflector Bore (by Inside Micrometer 0-150mm)",
        field_type="numeric_range", required=True, unit="mm", min_value=140.0, max_value=140.04,
        decimal_precision=3, standard_value="Dia:140+0.04mm +0.00",
        authority_reference="Camtech Manual/2005/TM/(H1.20 Jan 2005) Pg No:39")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="Arm_Conv", template_code="140", technology="CONVENTIONAL",
        template_name="Checksheet for Armature",
        description="Overhauling and Assembling Schedule - Armature checksheet - Conventional - M35-TM "
                     "section.",
        build_fn=build,
    )
