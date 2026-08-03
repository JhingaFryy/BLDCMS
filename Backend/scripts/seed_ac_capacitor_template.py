"""
Module 37: seeds the AC- Capacitor (Auxiliary Converter & Capacitor Details, 3-Phase, M9-HR
section) checksheet template.

Run once: `venv/bin/python scripts/seed_ac_capacitor_template.py`

Source: "Proforma for Auxiliary Converter & Capacitor Details" - checked as per OEM. The source
sheet groups readings under three headings exactly as transcribed here: "Auxiliary Converter 1",
"Auxiliary Converter 2-3" (2 and 3 share identical values on the sample sheet), and
"Auxiliary Converter 3" separately.
"""
from _aux_template_helpers import run_seed, add_final_remarks


def add_converter_group(add, key, label):
    group = add(key, field_label=label, field_type="group", required=False,
                authority_reference="Checked as per OEM")
    add(f"{key}_make", parent=group, field_label="Make", field_type="text", required=False)
    add(f"{key}_serial_no", parent=group, field_label="Sr. No.", field_type="text", required=True)
    add(f"{key}_mfg", parent=group, field_label="Manufacturer (Mfg)", field_type="text", required=False)
    add(f"{key}_shin_filter_capacitor", parent=group, field_label="Shin Filter Capacitor Value",
        field_type="text", required=True, help_text="Recorded as measured per phase, e.g. 88.1, 87.9, 87.9")
    add(f"{key}_snubber_ckt_capacitor", parent=group, field_label="Snubber Ckt. Capacitor Value",
        field_type="text", required=False)
    add(f"{key}_dc_link_capacitor", parent=group, field_label="DC Link Capacitor Value",
        field_type="text", required=True, help_text="e.g. 10000 uF")
    return group


def build(add):
    add("ac_loco_status", field_label="Loco Status", field_type="select",
        options="U/W (Under Work), O/W (Outside Work), Under AMC", required=False)

    add_converter_group(add, "ac_converter_1", "Auxiliary Converter - 1")
    add_converter_group(add, "ac_converter_2_3", "Auxiliary Converter - 2-3")
    add_converter_group(add, "ac_converter_3", "Auxiliary Converter - 3")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="AC- Capacitor", template_code="45", technology="3_PHASE",
        template_name="Checksheet for AC-Capacitor",
        description="Auxiliary Converter & Capacitor Details (3-Phase) checksheet - M9-HR section.",
        build_fn=build,
    )
