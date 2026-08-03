"""
Module 46: seeds the M2-HR Auxiliary Converter (BUR, 3-Phase) checksheet template.

Source: "Auxiliary converter.pdf" - TRS/ELS/BL/M2HR/3 Phase/Auxiliary Converter/Check sheet/2,
as per SMI-332 & TC 142 Rev 1.
"""
from _m2hr_template_helpers import add_confirm, add_text, run_seed_paged


def build(add, set_page):
    add("schedule", field_label="Schedule (TOH/IOH/POH)", field_type="text", required=False)
    add_text(add, "make", "Make", required=True)
    add_text(add, "equip_sr_no", "Equip. Sr. No.", required=False)
    add_text(add, "received_software_version", "Received Software Version", required=False)
    add_text(add, "updated_software_version", "Updated Software Version", required=False)
    add_text(add, "cubical_1", "Cubical 1", required=False)
    add_text(add, "cubical_2", "Cubical 2", required=False)

    add_confirm(add, "visual_inspect_insulators",
                "Visually Inspect the Insulators in the Auxiliary Converters (BUR) 1, 2 & 3 for "
                "Damage; Replace Any Damaged Insulator")
    add_confirm(add, "visual_inspect_mounting_hardware",
                "Visual Inspection of All Mounting Hardware for Mechanical and Electrical "
                "Components for Slackness (Torque Marking Changes)")
    add_confirm(add, "visual_check_electronic_cards",
                "Visually Check Each Electronic Card for Defects (Loose Components, IC "
                "Tightness, Leakage/Deform of Capacitors, Dust Accumulation)",
                authority_reference="Handle electronic cards with ESD protection")
    add_confirm(add, "visual_check_voltage_indicator", "Visual Checking of Voltage Indicator")
    add_confirm(add, "clean_inside_cabinets_vacuum",
                "Clean Inside the Auxiliary Converter Cabinets Using a Vacuum Cleaner; Remove "
                "Dust, Dirt and Debris", done_word="Dust Free")
    add_confirm(add, "cleaning_heat_sink_duct_aux",
                "Cleaning of Heat Sink, Duct and Overall Aux Converter by Blower/Vacuum Cleaner",
                done_word="Clean")
    add_confirm(add, "remove_dust_insulation_heat_convection",
                "Remove Dust and Dirt from Insulation and Heat Convection Surface",
                done_word="Dust Free")
    add("blower_fans_check", field_label="Check the Working of Blower Fans of Auxiliary "
        "Converters, if Provided; Attend/Replace as per Need", field_type="select",
        options="Checked OK, Replaced, Not Applicable", required=False,
        standard_value="Not Applicable")
    add_confirm(add, "inspect_cubicle_mechanical_electrical",
                "Inspect the Cubicle for Mechanical and Electrical Integrity - Fixings, "
                "Tightness, Wiring, Insulation Not Damaged/Burnt/Eroded")
    add_confirm(add, "electronics_cards_physical_integrity",
                "All Electronics Cards for Corresponding Aux. Converter to Be Checked for "
                "Physical Integrity; Replace if Faulty")
    add_confirm(add, "tightness_dust_cables_busbar_cts_pts",
                "Checking Tightness, Dust Accumulation & Overall Status of Cables, Busbar, "
                "CTs, PTs, MOV, Sensor and Connector of Different PCBs", done_word="Tight")
    add_confirm(add, "security_bolted_terminals_rectifier_inverter",
                "Check the Security of Bolted Terminals and Mechanical Mounting of Large "
                "Modules/Components of Aux. Rectifier and Aux. Inverter Module")
    add_confirm(add, "aux_converter_base_mounting_tightness",
                "Check the Auxiliary Converter Base Mounting Tightness", done_word="Tight")
    add_confirm(add, "gasket_dc_link_capacitor_bank",
                "Check the Condition of Gasket of DC Link Capacitor Bank, if Used; Replace if "
                "Damaged (In Other Than ATIL) (IOH/POH)")
    add_confirm(add, "gasket_rectifier_inverter_battery_charger",
                "Check the Condition of Gaskets of Rectifier, Inverter and Battery Charger "
                "Module; Replace if Damaged (TOH/IOH)")
    add_confirm(add, "dc_link_capacitance_value",
                "Check the Value of DC Link Capacitance Bank (In Other Than ATIL), Battery "
                "Charger Capacitance and Snubber Capacitance & Record; Ensure Within Permissible "
                "Range")
    add_confirm(add, "tightness_3phase_couplers",
                "Check the Tightness & Proper Fitment of 3 Phase Couplers (Internal) of Aux. "
                "Converter")
    add_confirm(add, "mov_check_replace", "All MOV to Be Checked and Replaced, if Found Defective")
    add_confirm(add, "vlu_discharge_resistor_overheating",
                "Check the VLU & Discharge Resistor for Evidence of Overheating")
    add("focs_db_loss_meter", field_label="Check the FOCs of Auxiliary Converter with DB Loss Meter",
        field_type="select", options="Checked OK, Not Applicable", required=False,
        standard_value="Checked OK")
    add_confirm(add, "cubicle_doors_covers_lock",
                "Check the Condition of Aux. Converter Doors/Covers and Door Lock Operation")
    add_confirm(add, "tightness_of_cards", "Tightness of Cards", done_word="Tight")
    add_confirm(add, "tightness_components_modules",
                "Check the Tightness of Components in Modules (Inverter Module, Rectifier "
                "Module, PCB Bus Station, AC Filter Assembly, EFD Assembly, Output Voltage "
                "Sensing Assembly, Output Current Sensing Assembly, DC Link Voltage Sensing "
                "Assembly)")
    add_confirm(add, "earthing_connections_check", "Checking the Earthing Connections")
    add_confirm(add, "earth_cables_check",
                "Check All Earth Cables of Auxiliary Converter, All Modules and Electronic "
                "Cubicles")
    add_confirm(add, "tightness_control_power_cables_couplers",
                "Check the Tightness of All Control & Power Cables and All Couplers",
                done_word="Tight")
    add_confirm(add, "mvb_connections_cables_check", "All MVB Connections and Cables to Be Checked")
    add_confirm(add, "cable_ties_ofc_condition",
                "Ensure All Cable Ties Are Tight and Intact OFC Cables Are in Good Condition")
    add_confirm(add, "abnormality_damage_address",
                "While Doing Maintenance, if Any Abnormality/Damage of Components and Cable "
                "Are Found, It Should Be Addressed")

    must_change = add("must_change_items", field_label="Must Change Items", field_type="group",
                      required=False)
    add("gasket_dc_link_capacitor", parent=must_change,
        field_label="Gasket of DC Link Capacitor Bank (IOH/POH)", field_type="select",
        options="Replaced, N/A", required=False, standard_value="Replaced")
    add("gasket_rectifier_inverter_battery_charger_module", parent=must_change,
        field_label="Gasket of Rectifier, Inverter and Battery Charger Modules, if Provided (POH)",
        field_type="select", options="Replaced, N/A", required=False, standard_value="Replaced")
    add("internal_cooling_churning_fan", parent=must_change,
        field_label="Internal Cooling/Churning Fan (IOH/POH)", field_type="select",
        options="Replaced, N/A", required=False, standard_value="Replaced")
    add("seals_aux_converter_cabinets", parent=must_change,
        field_label="Seals on the Aux. Converter Cabinets & Equipment Modules (IOH/POH)",
        field_type="select", options="Replaced, N/A", required=False, standard_value="Replaced")

    add("remarks", field_label="Remarks", field_type="textarea", required=False)


if __name__ == "__main__":
    run_seed_paged(
        equipment_code="BUR",
        template_code="M2HR_BUR",
        technology="3_PHASE",
        template_name="Check Sheet for Maintenance of Auxiliary Converter",
        description="M2-HR: Auxiliary Converter (BUR) checksheet for 3-Phase locomotives.",
        build_fn=build,
    )
