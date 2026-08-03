"""
Module 46: seeds the M2-HR Meters (10 Meters, Conventional) checksheet template.

Source: "10 METERS (AOH TOH IOH).docx.pdf" - TRS/ELS/BL/M2HR/Conv./Meters/Check sheet/XII. Page 1
is an 11-point generic meter maintenance checklist; page 2 is the per-meter calibration table for
the three fitted meters (TE-BE meter, KV meter, UBA meter), each calibrated at several fixed
setpoints.
"""
from _m2hr_template_helpers import add_confirm, add_numeric, add_text, run_seed_paged


def build(add, set_page):
    add_confirm(add, "glass_cover_crack_check", "Check for Any Crack on the Glass Cover")
    add_confirm(add, "hairspring_condition_check", "Check the Condition of the Hairspring")
    add_confirm(add, "pivots_condition_check", "Check the Condition of the Pivots")
    add_confirm(add, "jewel_bearing_condition_check", "Check the Condition of the Jewel Bearing")
    add_confirm(add, "jewel_bearing_clean", "Clean the Jewel Bearing", done_word="Cleaned")
    add_confirm(add, "wire_wound_resistors_overheating_check",
                "Check the Condition of All Wire-Wound Resistors to Ensure They Are Not "
                "Overheating")
    add_confirm(add, "dial_scale_legibility_check",
                "Check Legibility/Wear and Tear of the Dial Scale; Replace if Necessary")
    add_confirm(add, "led_condition_check",
                "Check the Condition of the LED; Replace if Necessary")
    add_confirm(add, "falling_resistors_condition_check",
                "Check the Condition of the Falling Resistors; Replace if Necessary")
    add_confirm(add, "sealant_moisture_ingress",
                "Apply Sealant on the Inner Edge of the Glass to Prevent Moisture Ingress")
    add_confirm(add, "test_bench_comparison_calibration",
                "Compare and Calibrate with the Test Bench")

    te_be = add("te_be_meter", field_label="TE-BE Meter", field_type="group", required=True)
    add_text(add, "te_be_make", "Make", required=True, parent=te_be)
    add_text(add, "te_be_sr_no", "Sr. No.", required=True, parent=te_be)
    for key, label, std in [
        ("25pct", "At 2.5 VDC - 25%", "2.5 VDC - 25%"),
        ("50pct", "At 5 VDC - 50%", "5 VDC - 50%"),
        ("100pct", "At 10 VDC - 100%", "10 VDC - 100%"),
    ]:
        add_numeric(add, f"te_be_{key}_observed", label, std, unit="VDC", parent=te_be)
        add_text(add, f"te_be_{key}_oh_calibration", f"{label} - OH/Calibration", required=False, parent=te_be)

    kv = add("kv_meter", field_label="KV Meter", field_type="group", required=True)
    add_text(add, "kv_make", "Make", required=True, parent=kv)
    add_text(add, "kv_sr_no", "Sr. No.", required=True, parent=kv)
    for key, label in [
        ("5kv", "At 1.65 VDC - 5 KV"), ("10kv", "At 3.3 VDC - 10 KV"), ("15kv", "At 5 VDC - 15 KV"),
        ("20kv", "At 6.65 VDC - 20 KV"), ("25kv", "At 8.3 VDC - 25 KV"), ("30kv", "At 10 VDC - 30 KV"),
    ]:
        add_numeric(add, f"kv_{key}_observed", label, label.split("At ")[1], unit="VDC", parent=kv)
        add_text(add, f"kv_{key}_oh_calibration", f"{label} - OH/Calibration", required=False, parent=kv)

    uba = add("uba_meter", field_label="UBA Meter", field_type="group", required=True)
    add_text(add, "uba_make", "Make", required=True, parent=uba)
    add_text(add, "uba_sr_no", "Sr. No.", required=True, parent=uba)
    for key, label, std in [
        ("30v", "At 30V", "30 V ± 1.5%"), ("60v", "At 60V", "60 V ± 1.5%"),
        ("90v", "At 90V", "90 V ± 1.5%"), ("120v", "At 120V", "120 V ± 1.5%"),
    ]:
        add_numeric(add, f"uba_{key}_observed", label, std, unit="V", parent=uba)
        add_text(add, f"uba_{key}_oh_calibration", f"{label} - OH/Calibration", required=False, parent=uba)

    add("remarks", field_label="Remarks", field_type="textarea", required=False)


if __name__ == "__main__":
    run_seed_paged(
        equipment_code="Meters_Conv",
        template_code="M2HR_METERS_CONV",
        technology="CONVENTIONAL",
        template_name="Check Sheet for Meters (AOH/TOH/IOH)",
        description="M2-HR: Meters (TE-BE, KV, UBA) checksheet for Conventional locomotives.",
        build_fn=build,
    )
