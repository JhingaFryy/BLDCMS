"""
Module 40: seeds the SAss_Conv (Strap Assembly, WAP-4, Conventional, M4-HR section) checksheet
template.

Run once: `venv/bin/python scripts/seed_strap_assembly_conv_template.py`

Source: page 21 of the supplied WAP-4 checksheet - "Check Sheet for Strap Assembly of WAP-4 Loco"
- "Overhauling of Trunion & Connecting Strap", a single flat 4-item checklist (not repeated per
cab/wheelset). No equivalent equipment exists for WAG9HC/WAP-7 - the trunion/connecting-strap
strap assembly is specific to the WAP-4/Conventional bogie's traction-motor suspension.
"""
from _m4hr_template_helpers import add_final_remarks, run_seed


def build(add):
    add("modified_trunion_provision", field_label="Provision of Modified Trunion (Ref: ELRS/MS/0284 Rev.-2 dt. "
        "17.04.2007)", field_type="select", options="Provided, Not Provided", required=True,
        standard_value="Provided", negative_values="Not Provided")
    add("connecting_strap_condition", field_label="Check Condition of Connecting Strap/Replaced (EL-12.13/1 dt. "
        "29/05/2008-6) (as per L/No.-EL/3.2.13/1 Dt. 19/02/2010)", field_type="select",
        options="Done, Not Done", required=True, standard_value="Done", negative_values="Not Done")
    add("trunion_overhauling", field_label="Overhauling of Trunion", field_type="select",
        options="Done, Not Done", required=True, standard_value="Done", negative_values="Not Done")
    add("modified_guide_assembly_provision", field_label="Provision of Modified Guide Assembly (Ref: "
        "ELRS/MS/0283 Rev-0 dt. 06.06.2000)", field_type="select", options="Provided, Not Provided",
        required=True, standard_value="Provided", negative_values="Not Provided")

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="SAss_Conv", template_code="117", technology="CONVENTIONAL",
        template_name="Checksheet for Strap Assembly (WAP-4)",
        description="Overhauling of Trunion & Connecting Strap checksheet - WAP-4, Conventional - M4-HR section.",
        build_fn=build,
    )
