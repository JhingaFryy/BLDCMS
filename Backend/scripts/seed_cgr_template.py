"""
Module 34: seeds the CGR (Contactor + CGR Stand, Conventional, M8-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_cgr_template.py`

Source: PERFORMA OF CHECK POINTS OF CGR DURING AOH/IOH (ELS/TRS/BL/M-8/03, page_number=1) and
PERFORMA OF CHECK POINTS OF CGR STAND OVERHAULING DURING AOH/IOH (ELS/TRS/BL/M-8/04, page_number=2)
- two physical pages of the same source PDF, both about the CGR equipment, so implemented as one
  template with two page groups (matching the TM Overhaul template's precedent of a multi-page
  template using the page_number-aware helper).

Reuses `_tm_template_helpers.run_seed` purely for its page_number support (`_aux_template_helpers`'s
`make_add` hardcodes page_number=1) - `maintenance_type=None` here, same as every other
single-template equipment; this does NOT make CGR a maintenance-type-disambiguated template.
"""
from _aux_template_helpers import add_final_remarks
from _tm_template_helpers import run_seed


def add_cgr_group(add, key, label, standard, field_type="select", options="Done, Not Done",
                  negative=None, unit=None, min_value=None, max_value=None, decimal_precision=None,
                  authority=None):
    """A checkpoint recorded once per physical CGR unit (CGR-1/2/3) - matches the source sheet's
    three parallel value columns."""
    group = add(key, field_label=label, field_type="group", required=False, standard_value=standard,
               authority_reference=authority)
    for unit_label in ("CGR-1", "CGR-2", "CGR-3"):
        suffix = unit_label.lower().replace("-", "_")
        kwargs = dict(field_type=field_type, required=True)
        if field_type == "select":
            kwargs["options"] = options
            if negative:
                kwargs["negative_values"] = negative
        else:
            if unit is not None:
                kwargs["unit"] = unit
            if min_value is not None:
                kwargs["min_value"] = min_value
            if max_value is not None:
                kwargs["max_value"] = max_value
            if decimal_precision is not None:
                kwargs["decimal_precision"] = decimal_precision
        add(f"{key}_{suffix}", parent=group, field_label=unit_label, **kwargs)
    return group


def build(add):
    # === Page 1: CGR (Contactor) ===
    add_cgr_group(add, "cgr_dismantled_completely", "Dismantle CGR Completely Without Insulating Beam "
        "With Yoke Plate", "Dismantled", options="Dismantled, Not Dismantled", negative="Not Dismantled")
    add_cgr_group(add, "cgr_cleaned_washed_petrol", "Clean & Wash CGR Parts With Petrol", "Cleaned",
        options="Cleaned, Not Cleaned", negative="Not Cleaned")
    add_cgr_group(add, "cgr_contact_block_bearing", "Check Condition Contact Block Bearing", "Good",
        options="Good, Damaged", negative="Damaged")
    add_cgr_group(add, "cgr_insulating_bush_contact_lever", "Check Condition of Insulating Bush of "
        "Contact Lever", "Good", options="Good, Damaged", negative="Damaged")
    add_cgr_group(add, "cgr_contact_lever_play", "Check Condition of Contact Lever for Any Play", "No play",
        options="No Play, Play", negative="Play")
    add_cgr_group(add, "cgr_connection_shunt", "Check Condition of Connection Shunt (06 Nos.)", "Good",
        options="Good, Damaged", negative="Damaged", authority="OEM manual")
    add_cgr_group(add, "cgr_assembled_in_fixture", "Assembled the CGR in Fixture", "fixture",
        options="Fixture, Not in Fixture", negative="Not in Fixture", authority="OEM manual")
    add_cgr_group(add, "cgr_marked_top_bottom", "Mark the CGR Top & Bottom After Assembly", "Marking",
        options="Marked, Not Marked", negative="Not Marked")
    add_cgr_group(add, "cgr_contact_piece_replaced", "Replace Contact Piece (06 Nos.)", "Must change",
        options="Replaced, Not Replaced", negative="Not Replaced")
    add_cgr_group(add, "cgr_contact_piece_allen_bolt_replaced", "Replace Contact Piece Allen Bolt (06 Nos.)",
        "Must change", options="Replaced, Not Replaced", negative="Not Replaced")
    add_cgr_group(add, "cgr_contact_pivots_lubricated", "Contact Pivots Lubricated Through Nipples "
        "High Temp. Grease", "Must be lubricated", options="Lubricated, Not Lubricated",
        negative="Not Lubricated", authority="OEM manual & SMI-117")
    add_cgr_group(add, "cgr_arcing_chamber_cleaned", "Clean Arcing Chamber & Ensure Modified Catch Assly.",
        "Must be ensured", options="Ensured, Not Ensured", negative="Not Ensured")

    add_cgr_group(add, "cgr_gap_between_contacts", "Gap Between Contacts", "29-33mm",
        field_type="numeric_range", unit="mm", min_value=29.0, max_value=33.0, decimal_precision=2)
    add_cgr_group(add, "cgr_contact_centre_distance", "Contact Centre Distance Between Top & Bottom Pivot",
        "129.8-150mm", field_type="numeric_range", unit="mm", min_value=129.8, max_value=150.0,
        decimal_precision=2)
    add_cgr_group(add, "cgr_play_open_contact_arcing_horn", "Play Between Open Contact Piece & Arcing Horn",
        "0.5-2.0mm", field_type="numeric_range", unit="mm", min_value=0.5, max_value=2.0,
        decimal_precision=2, authority="OEM manual")
    add_cgr_group(add, "cgr_contact_thickness_new", "Contact Thickness (New)", "48mm",
        field_type="number", unit="mm")

    add_cgr_group(add, "cgr_contact_pressure_single_spring", "Contact Pressure - Single Spring",
        "7.8 +/- 20%", field_type="numeric_range", unit="kg", min_value=6.24, max_value=9.36,
        decimal_precision=2, authority="SMI-150")
    add_cgr_group(add, "cgr_contact_pressure_double_spring", "Contact Pressure - Double Spring",
        "13.4 +/- 20%", field_type="numeric_range", unit="kg", min_value=10.72, max_value=16.08,
        decimal_precision=2, authority="SMI-150")

    add_cgr_group(add, "cgr_contact_torque_tightened", "Tightened CGR Contact by Torque Wrench",
        "2.5 kg-m", field_type="number", unit="kg-m", authority="OEM manual")
    add_cgr_group(add, "cgr_foundation_bolt_torque_tightened", "Tightened CGR Foundation Bolt by "
        "Torque Wrench", "5.0 kg-m", field_type="number", unit="kg-m")
    add_cgr_group(add, "cgr_notch_sequence_checked", "Check CGR Closing & Opening Sequence From "
        "'0' to '32' Notch ('0'/Even Notch: O-C-C, Odd Notch: C-O-O, Half Notch: C-C-O)",
        "checked", options="Checked, Not Checked", negative="Not Checked")

    # === Page 2: CGR Stand ===
    add("cgr_stand_top_copper_bolt_thread", field_label="Check Top Side Copper Bolt for Thread Worn Out",
        field_type="select", options="Good, Worn Out", required=True, standard_value="Good",
        negative_values="Worn Out", page_number=2)
    add("cgr_stand_bottom_copper_bolt_thread", field_label="Check Bottom Side Copper Bolt for Thread "
        "Worn Out", field_type="select", options="Good, Worn Out", required=True, standard_value="Good",
        negative_values="Worn Out", page_number=2)
    add("cgr_stand_top_copper_connecting_bar", field_label="Check Condition of Top Copper Connecting Bar "
        "for Any Thread Damage", field_type="select", options="Good, Damaged", required=True,
        standard_value="Good", negative_values="Damaged", page_number=2)
    add("cgr_stand_bevel_gear_teeth_damage", field_label="Check Condition of Bevel Gear Teeth for Any Damage",
        field_type="select", options="Good, Damaged", required=True, standard_value="Good",
        negative_values="Damaged", page_number=2)

    cam_dia = add("cgr_stand_cam_dia", field_label="Check & Measure Cam Dia for CGR", field_type="group",
                  required=False, standard_value="109-114mm", authority_reference="OEM manual",
                  page_number=2)
    for cam_label in ("Cam 1", "Cam 2", "Cam 3"):
        key = "cgr_stand_cam_dia_" + cam_label.lower().replace(" ", "_")
        add(key, parent=cam_dia, field_label=cam_label, field_type="numeric_range", required=True,
            unit="mm", min_value=109.0, max_value=114.0, decimal_precision=1, page_number=2)

    add("cgr_stand_insulated_plate_crack_damage", field_label="Check Condition of Top & Bottom Insulated "
        "Plate for Any Crack or Damage", field_type="select", options="Good, Damaged", required=True,
        standard_value="Good", negative_values="Damaged", page_number=2)
    add("cgr_stand_camshaft_bearing_freely_moved", field_label="Check Condition of Cam Shaft Bearing "
        "Freely Moved or Not", field_type="select", options="Freely Moved, Not Freely Moved",
        required=True, standard_value="Freely move", negative_values="Not Freely Moved", page_number=2)
    add("cgr_stand_megger_top_bottom_insulated_plate", field_label="Check Megger Value of Top & Bottom "
        "Insulated Plate", field_type="numeric_range", required=True, unit="MOhm", min_value=50.0,
        decimal_precision=1, standard_value="50 M-Ohm mm", page_number=2)
    add("cgr_stand_megger_leg", field_label="Check Megger Value of CGR Stand Leg", field_type="numeric_range",
        required=True, unit="MOhm", min_value=50.0, decimal_precision=1, standard_value="50 M-Ohm mm",
        page_number=2)
    add("cgr_stand_copper_bolt_torque_tightness", field_label="Check Tightness of Copper Bolt by "
        "Torque Wrench", field_type="number", required=True, unit="kg-m", standard_value="3 kg-m",
        page_number=2)
    add("cgr_stand_rpgr_resistance", field_label="Check Resistance Value of RPGR", field_type="numeric_range",
        required=True, unit="KOhm", min_value=90.0, max_value=110.0, decimal_precision=1,
        standard_value="100 KOhm +/- 10%", page_number=2)

    dowel_pin = add("cgr_stand_dowel_pin_camshaft", field_label="Change Dowell Pin of Cam Shaft",
                    field_type="group", required=False, standard_value="Condition basis", page_number=2)
    add("cgr_stand_dowel_pin_5x45", parent=dowel_pin, field_label="5 x 45 mm", field_type="select",
        options="Changed, Not Changed", required=True, page_number=2)
    add("cgr_stand_dowel_pin_8x45", parent=dowel_pin, field_label="8 x 45 mm", field_type="select",
        options="Changed, Not Changed", required=True, page_number=2)

    add("cgr_stand_nut_bolt_set_changed", field_label="Change Set of CGR Nut & Bolt", field_type="select",
        options="Changed, Not Changed", required=True, standard_value="Must change",
        negative_values="Not Changed", authority_reference="HQ TC 213 (IOH)", page_number=2)

    electrical_conn = add("cgr_stand_electrical_connections_tightness", field_label="Ensure Tightness of "
        "All Electrical Connections", field_type="group", required=False,
        authority_reference="SMI-62 & 90", page_number=2)
    for key, label in [
        ("cgr_stand_conn_i", "CGR1 & III to GR Condenser Bushing (04 Nos. Bolts)"),
        ("cgr_stand_conn_ii", "CGR-II to RGR"),
        ("cgr_stand_conn_iii", "CGR-III to RGR"),
        ("cgr_stand_conn_iv", "CGR-1 to Transformer A34 Bushing"),
    ]:
        add(key, parent=electrical_conn, field_label=label, field_type="select",
            options="Ensured, Not Ensured", required=True, standard_value="Must be ensured",
            negative_values="Not Ensured", page_number=2)

    add("cgr_stand_contact_angle_measurement", field_label="Measurement of Contact Angle",
        field_type="text", required=True, standard_value="Angle in zone of angle disk", page_number=2)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="CGR", template_code="26", technology="CONVENTIONAL", maintenance_type=None,
        template_name="Checksheet for CGR",
        description="CGR (Contactor + CGR Stand, Conventional) checksheet - M8-HR section.",
        build_fn=build,
    )
