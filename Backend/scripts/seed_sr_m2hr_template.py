"""
Module 46: seeds the M2-HR Traction Converter (SR, 3-Phase) checksheet template.

Source: "Traction converter.pdf" - TRS/ELS/BL/M2HR/3 Phase/Traction Converter/Check sheet/1,
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

    add_confirm(add, "visual_inspect_control_power_cards",
                "Visually Inspect Control Cards and Power Supply Cards in Electronic Cubicles "
                "and Ensure Tightness")
    add_confirm(add, "voltage_indicator_current_transducer",
                "Check the Voltage Indicator and Current Transducer (Visually); Replace if Required")
    add_confirm(add, "stuchi_coupling_inspect",
                "Inspect Stuchi Coupling at Power Module of the Traction Converter (BHEL)")
    add_confirm(add, "cleaning_wiping_dust_modules",
                "Cleaning/Wiping Off the Dust Shall Be Carried Out on All Modules of Traction "
                "Converter", done_word="Dust Free")
    add_confirm(add, "clean_heat_sink_vacuum", "Clean the Heat Sink by Vacuum Cleaner",
                done_word="Clean")
    add_confirm(add, "dc_link_voltage_current_sensors_tightness",
                "Inspect and Ensure Tightness of DC Link Voltage Sensors and Current Sensors",
                done_word="Tight")
    add_confirm(add, "internal_cooling_churning_fans", "Checking the Internal Cooling/Churning Fans")
    add_confirm(add, "pressure_temp_sensor_air_coolant",
                "Checking of Pressure Sensor and Temperature Sensor of Air and Coolant")
    add_confirm(add, "gate_drive_fiber_optics_inspect",
                "Gate Drive Unit Fiber Optics - Inspect (ATIL: Visual Checking of OFC Connection "
                "and Its Condition on DCU Cards and from DCU to Module; BHEL: Visual Checking of "
                "Internal OFC Connection and Its Condition); Replace if Required")

    must_change = add("must_change_items", field_label="Must Change Items", field_type="group",
                      required=False)
    add("coolant_flexible_pipeline_module", parent=must_change,
        field_label="Traction Converter Coolant Flexible Pipeline at Module Side (WAG9/9H) "
        "(IOH2/IOH4)", field_type="select", options="Replaced, N/A", required=False,
        standard_value="Replaced")
    add("stucchi_coupling_rubber_parts", parent=must_change,
        field_label="Stucchi Coupling Rubber Parts at Module Side (WAG9/9H) (IOH2/IOH4)",
        field_type="select", options="Replaced, N/A", required=False, standard_value="Replaced")
    add("internal_churning_fan", parent=must_change,
        field_label="Internal Churning Fan (WAG9/9H) (IOH2/IOH4)", field_type="select",
        options="Replaced, N/A", required=False, standard_value="Replaced")
    add("pressure_temp_sensor_replace", parent=must_change,
        field_label="SR Pressure Sensor & Temperature Sensor (WAG9/9H) (IOH2/IOH4)",
        field_type="select", options="Replaced, N/A", required=False, standard_value="Replaced")

    add("remarks", field_label="Remarks", field_type="textarea", required=False)


if __name__ == "__main__":
    run_seed_paged(
        equipment_code="SR",
        template_code="M2HR_SR",
        technology="3_PHASE",
        template_name="Check Sheet for Maintenance of Traction Converter",
        description="M2-HR: Traction Converter (SR) checksheet for 3-Phase locomotives.",
        build_fn=build,
    )
