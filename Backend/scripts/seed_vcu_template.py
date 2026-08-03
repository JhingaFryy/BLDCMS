"""
Module 46: seeds the M2-HR Vehicle Control Unit (VCU, 3-Phase) checksheet template.

Source: "VCU check sheet.pdf" - TRS/ELS/BL/M2HR/3 Phase/VCU/Check sheet/3, as per SMI-332 & TC 142
Rev.1. Page 2's fault-log/software table is shared across SR, BUR & VCU in the source document,
but only its VCU-scoped rows are included here (SR and BUR have their own templates/checksheets).
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

    add_confirm(add, "cleaning_dust_vacuum",
                "Cleaning Dust from All Electronics, Electrical Equipment, Sensor Using Vacuum "
                "Cleaner", done_word="Dust Free")
    add_confirm(add, "visual_inspect_box_enclosure",
                "Visually Inspect the Entire Box, Enclosure Walls, Covers & Welds for Any Damage "
                "or Cracks")
    add_confirm(add, "visual_inspect_cable_connections",
                "Visually Inspect All Internal Cable Connections of the Sub D for Damage")
    add_confirm(add, "visual_inspect_screws_mounting",
                "Visually Inspect the Screws Securing the VCU to the Supporting")
    add_confirm(add, "visual_check_physical_damage_insulation",
                "Visually Check Physical Damage and Insulation Defects")
    add_confirm(add, "cleaning_heat_sink_duct", "Cleaning of Heat Sink, Duct and Overall VCU by "
                "Blower/Vacuum Cleaner", done_word="Cleaned")
    add_confirm(add, "loose_fixing_check", "Check for Loose Fixing of Any Connection")
    add_confirm(add, "pcb_cards_couplers_tightness",
                "Check the Tightness of All PCB Cards and Couplers/Connections")
    add_confirm(add, "cooling_fan_condition", "Ensure Condition of Instrument Cooling Fan")
    add_confirm(add, "pcb_handling_cleaning_rdso",
                "Handling and Cleaning of PCB as per RDSO Guideline",
                authority_reference="ELRS/TC/0091 dated 13.02.06")
    add_confirm(add, "subd_coupler_tightness", "Sub-D Coupler Tightness Check of Each Card")
    add_confirm(add, "earthing_shunt_tightness", "Earthing Shunt Tightness Check")
    add_confirm(add, "hinges_brackets_condition",
                "Check the Condition of Hinges/Brackets for the Hinged Assembly")
    add_confirm(add, "mvb_connections_cables_check", "All MVB Connections and Cables Need to Be Checked")
    add_confirm(add, "fiber_optic_cable_tightness", "Check the Tightness of Fiber Optic Cables")

    add("download_fault_log_data", field_label="Download Fault Log Data Through Laptop/Pen Drive "
        "and Check for Any Abnormal Messages; Record Loco-Wise Fault Data", field_type="textarea",
        required=True)
    add_confirm(add, "mvb_admin_card_fault_history", "MVB Administrator Card - Check the Fault "
                "History Data (Upload)")
    add_confirm(add, "app_processor_card_sw_version", "Application Processor Card - Check the "
                "Software Version from VCU Tool")
    add("reload_software_vcbu_station_computer", field_label="Reload the Software to the Vehicle "
        "Control Unit Bus Station Computer (POH)", field_type="select", options="Reloaded, Not Reloaded",
        required=False, standard_value="Reloaded")
    add("reload_vcu_application_software", field_label="Reload VCU Application Software on "
        "Condition Basis (TOH/IOH/POH)", field_type="select", options="Reloaded, Not Reloaded",
        required=False, standard_value="Reloaded")

    add("remarks", field_label="Remarks", field_type="textarea", required=False)


if __name__ == "__main__":
    run_seed_paged(
        equipment_code="VCU",
        template_code="M2HR_VCU",
        technology="3_PHASE",
        template_name="Check Sheet for Maintenance of VCU",
        description="M2-HR: Vehicle Control Unit (VCU) checksheet for 3-Phase locomotives.",
        build_fn=build,
    )
