"""
Module 37: seeds the RTIS (Avantel Make, PH-2 Devices) checksheet template for BOTH RTIS- Conv
and RTIS- 3Ph equipment IDs - identical content, separate template row per equipment_id (per
Module 37's explicit instruction), never merged.

Run once: `venv/bin/python scripts/seed_rtis_template.py`

Source: "Maintenance Checks for Avantel Make RTIS PH-2 Devices".
"""
from _aux_template_helpers import run_seed, add_final_remarks


def build(add):
    add("rtis_irn_serial_no", field_label="IRN Sr. No.", field_type="text", required=True)
    add("rtis_psm_serial_no", field_label="PSM Sr. No.", field_type="text", required=True)
    add("rtis_rmt_serial_no", field_label="RMT Sr. No.", field_type="text", required=True)

    add("rtis_mcb_switched_on", field_label="Ensure the RTIS MCB Installed in the Machine Room "
        "Is Switched On", field_type="select", options="OK, Not OK", required=True, negative_values="Not OK")
    add("rtis_power_on_leds", field_label="Verify That the POWER ON LEDs (DC IN / DC OUT) on the "
        "PSM Are Illuminated", field_type="select", options="OK, Not OK", required=True, negative_values="Not OK")
    add("rtis_irn_power_on_led", field_label="Confirm the IRN Power ON LED on the IRN Is Lit",
        field_type="select", options="OK, Not OK", required=True, negative_values="Not OK")
    add("rtis_cables_connectors_tightness", field_label="Inspect All Cables and Connectors for "
        "Proper Tightness and Secure Connections", field_type="select", options="OK, Not OK",
        required=True, negative_values="Not OK")
    add("rtis_mounting_brackets_welding", field_label="Check the Welding of Mounting Brackets, "
        "Conduits and Wiring on the Rooftop for Integrity and Soundness", field_type="select",
        options="OK, Not OK", required=True, negative_values="Not OK")
    add("rtis_screws_tightened", field_label="Ensure All Screws on the IRN, RMT and PSM Units "
        "Are Properly Tightened", field_type="select", options="OK, Not OK", required=True,
        negative_values="Not OK")
    add("rtis_cable_connections_fitment", field_label="Verify All Cable Connections for Proper "
        "Fitment and Security", field_type="select", options="OK, Not OK", required=True, negative_values="Not OK")

    health_group = add("rtis_module_health_status", field_label="Verify the Health Status of MSS, "
        "SIM-1, SIM-2, Primary GPS, Secondary GPS Modules Thru RTIS Mobile App as well as Device's "
        "Screen", field_type="group", required=False)
    for key, label in [("mss", "MSS"), ("sim1", "SIM-1"), ("sim2", "SIM-2"),
                        ("primary_gps", "Primary GPS"), ("secondary_gps", "Secondary GPS")]:
        add(f"rtis_health_{key}", parent=health_group, field_label=label, field_type="select",
            options="Connected, Not Connected", required=True, negative_values="Not Connected")

    add("rtis_touch_screen_operating", field_label="Confirm That the Touch Screen Is Operating Normal",
        field_type="select", options="OK, Not OK", required=True, negative_values="Not OK")
    add("rtis_irn_tampering_check", field_label="Check for Any Signs of Tampering or Damage on "
        "the IRN Units", field_type="select", options="OK, Not OK", required=True, negative_values="Not OK")
    add("rtis_rmt_tampering_check", field_label="Check for Any Signs of Tampering or Damage on "
        "the RMT Units", field_type="select", options="OK, Not OK", required=True, negative_values="Not OK")
    add("rtis_psm_tampering_check", field_label="Check for Any Signs of Tampering or Damage on "
        "the PSM Units", field_type="select", options="OK, Not OK", required=True, negative_values="Not OK")
    add("rtis_rf_cables_check", field_label="Inspect RF Cables for Any Tampering or Physical Damage",
        field_type="select", options="OK, Not OK", required=True, negative_values="Not OK")
    add("rtis_ethernet_cables_check", field_label="Inspect Ethernet Cables for Any Tampering or "
        "Physical Damage", field_type="select", options="OK, Not OK", required=True, negative_values="Not OK")
    add("rtis_power_cables_check", field_label="Inspect Power Cables for Any Tampering or Physical "
        "Damage", field_type="select", options="OK, Not OK", required=True, negative_values="Not OK")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="RTIS- Conv", template_code="44", technology="CONVENTIONAL",
        template_name="Checksheet for RTIS (Conventional)",
        description="RTIS PH-2 Devices (Avantel Make) checksheet - Conventional - M9-HR section.",
        build_fn=build,
    )
    run_seed(
        equipment_code="RTIS- 3Ph", template_code="51", technology="3_PHASE",
        template_name="Checksheet for RTIS (3-Phase)",
        description="RTIS PH-2 Devices (Avantel Make) checksheet - 3-Phase - M9-HR section. "
        "Content identical to the Conventional template by design (Module 37) - implemented as a "
        "separate template row against its own equipment_id, never merged.",
        build_fn=build,
    )
