"""
Module 35: seeds the Radiator (Oil Cooling Unit, 3-Phase, M8-HR section) checksheet template.

Run once: `venv/bin/python scripts/seed_radiator_3phase_template.py`

Source: CHECK SHEET FOR 3 PHASE LOCOMOTIVES (ELS/TRS/BL/M8/15 Rev-1), section
"6. OIL COOLING UNIT RADIATOR".
"""
from _aux_template_helpers import run_seed, add_final_remarks

REF_3135 = "RDSO L.No. EL/3.1.35/16 dt. 7.2.12"


def build(add):
    flange = add("radiator_flange_joint_check", field_label="Examine Flange Joint for Sign of Cracks, "
        "Oil Leakage and Checked/Intact/Loose Missing Screws; Ensure Tightness of Radiator Protection "
        "Screen Fasteners", field_type="group", required=False, authority_reference=REF_3135)
    add("radiator_flange_joint_leakage", parent=flange, field_label="Flange Joint Leakage", field_type="select",
        options="No Leakage, Leakage", required=True, standard_value="No Leakage", negative_values="Leakage")
    add("radiator_protection_screen_fasteners", parent=flange, field_label="Protection Screen Fasteners "
        "Tightness", field_type="select", options="Done, Not Done", required=True, standard_value="Done",
        negative_values="Not Done")

    add("radiator_chamber_vacuum_cleaned", field_label="Vacuum Clean the Radiator Chamber via the Machine "
        "Room Access Cover and Then Clean the Radiator by High Pressure Hot Water Jet; Check That the "
        "Radiator Is Not Blocked", field_type="select", options="Cleaned, Not Cleaned", required=True,
        negative_values="Not Cleaned")
    add("radiator_oil_cooler_leakage_top_bottom", field_label="Check Oil Cooler Radiator for Any Oil "
        "Leakage/External Damage From Top and Bottom", field_type="select", options="No Leakage, Leakage",
        required=True, standard_value="No Leakage", negative_values="Leakage")
    add("radiator_vptp_vpsr_leakage", field_label="Check / Attend Oil Leakage From VPTP & VPSR",
        field_type="select", options="No Leakage, Leakage", required=True, standard_value="No Leakage",
        negative_values="Leakage")
    add("radiator_cleaned_top_bottom", field_label="Clean the Radiator From Top & Bottom Both Side",
        field_type="select", options="Cleaned, Not Cleaned", required=True, negative_values="Not Cleaned")
    add("radiator_cleaned_hot_water_jet_air", field_label="Clean the Radiator by Hot Water Jet / Air Blowing",
        field_type="select", options="Cleaned, Not Cleaned", required=True, negative_values="Not Cleaned",
        authority_reference="SMI 287")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="Radiator", template_code="31", technology="3_PHASE",
        template_name="Checksheet for Radiator",
        description="Oil Cooling Unit Radiator (3-Phase) checksheet - M8-HR section.",
        build_fn=build,
    )
