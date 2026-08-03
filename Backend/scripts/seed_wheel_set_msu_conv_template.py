"""
Module 40: seeds the WS_Conv (Wheel Set/MSU Hitachi/Taochi, WAP-4, Conventional, M4-HR section)
checksheet template.

Run once: `venv/bin/python scripts/seed_wheel_set_msu_conv_template.py`

Source: pages 9-10 of the supplied WAP-4 checksheet - "Check Sheet for Wheel Set/MSU
Hitachi/Taochi of WAP-4 Loco", recorded once per Wheel Set (1-6). Unlike the WAG9HC/WAP-7 3-Phase
templates, which split this content across three separate equipment (MSU, Wheel Checking, Wheel
Measurement), the WAP-4 reference sheet combines MSU and wheel-set checks into a single table -
modelled here as one equipment/template to stay faithful to the source, per the instruction not to
invent equipment splits the reference document doesn't show.
"""
from _m4hr_template_helpers import add_final_remarks, run_seed

WHEEL_SETS = list(range(1, 7))
SIDES = ("PE", "CE")


def _pe_ce_group(add, parent, key, label, field_type, standard, **extra):
    group = add(key, parent=parent, field_label=label, field_type="group", required=False, standard_value=standard)
    for side in SIDES:
        add(f"{key}_{side.lower()}", parent=group, field_label=side, field_type=field_type, required=True,
            **extra)
    return group


def build(add):
    for ws in WHEEL_SETS:
        ws_group = add(f"wheel_set_{ws}", field_label=f"Wheel Set-{ws}", field_type="group", required=False)

        add(f"wheel_set_{ws}_axle_no", parent=ws_group, field_label="Axle No.", field_type="text", required=True,
            standard_value="Noted")
        add(f"wheel_set_{ws}_axle_ust", parent=ws_group, field_label="Axle UST (As per TC-47)", field_type="select",
            options="Done, Not Done", required=True, standard_value="Done", negative_values="Not Done")
        add(f"wheel_set_{ws}_msu_crack_check", parent=ws_group, field_label="Check MSU for Any Crack",
            field_type="select", options="Done, Crack Found", required=True, standard_value="Done",
            negative_values="Crack Found")
        add(f"wheel_set_{ws}_msu_lateral_play", parent=ws_group, field_label="MSU Lateral Play (As per SMI "
            "No.0221-2000 Rev.'0')", field_type="numeric_range", required=True, unit="mm", min_value=0.05,
            max_value=0.25, decimal_precision=2)
        add(f"wheel_set_{ws}_a_distance_gauge", parent=ws_group, field_label="Checking 'A' Distance by Go-Gauge "
            "(As per SMI No. 207-99 Rev.'0' dt 22.02.99)", field_type="numeric_range", required=True, unit="mm",
            min_value=281.980, max_value=282.052, decimal_precision=3)
        add(f"wheel_set_{ws}_enclosure_intactness", parent=ws_group, field_label="Enclosure Intactness",
            field_type="select", options="Intact, Not Intact", required=True, standard_value="Intact",
            negative_values="Not Intact")
        add(f"wheel_set_{ws}_allen_screw_tightness", parent=ws_group, field_label="Allen Screw Tightness",
            field_type="select", options="Ensured, Not Ensured", required=True, standard_value="Ensured",
            negative_values="Not Ensured")
        add(f"wheel_set_{ws}_earthing_brush", parent=ws_group, field_label="Earthing Brush", field_type="select",
            options="Provided, Not Provided", required=True, standard_value="Provided",
            negative_values="Not Provided")
        add(f"wheel_set_{ws}_greasing_msu_bearing", parent=ws_group, field_label="Greasing of MSU Bearing",
            field_type="select", options="Done, Not Done", required=True, standard_value="Done",
            negative_values="Not Done")
        add(f"wheel_set_{ws}_k_value", parent=ws_group, field_label="'K' Value (As per MP.MI 154/93 dt 1993) "
            "7 Teeth", field_type="numeric_range", required=True, unit="mm", min_value=239.6, max_value=240.983,
            decimal_precision=3, standard_value="Max.-240.983mm, Ser. Limit-239.6mm")
        add(f"wheel_set_{ws}_broad_gauge", parent=ws_group, field_label="Broad Gauge (As per MP.IB.BD 02.16.01 "
            "(Rev.01) dt.-31.12.2009)", field_type="numeric_range", required=True, unit="mm", min_value=1595.5,
            max_value=1597.5, decimal_precision=2, standard_value="1596.00-0.5mm,+1.5mm, Service Limit-1599mm")

        _pe_ce_group(add, ws_group, f"wheel_set_{ws}_wheel_dia", "Check Wheel Dia", "numeric_range",
                     "New-1097mm, Ser. Limit-1012mm", unit="mm", min_value=1012.0, max_value=1097.0,
                     decimal_precision=0)
        _pe_ce_group(add, ws_group, f"wheel_set_{ws}_root_wear", "Check Root Wear", "number", "Max. 6.0mm",
                     unit="mm")
        _pe_ce_group(add, ws_group, f"wheel_set_{ws}_flange_wear", "Check Flange Wear", "number", "Max. 3.0mm",
                     unit="mm")
        _pe_ce_group(add, ws_group, f"wheel_set_{ws}_tread_wear", "Check Tread Wear", "number", "Max. 6.5mm",
                     unit="mm")
        _pe_ce_group(add, ws_group, f"wheel_set_{ws}_wheel_tyre_thickness", "Check Wheel Tyre Thickness",
                     "numeric_range", "133.0+1.5mm/-0.0", unit="mm", min_value=133.0, max_value=134.5,
                     decimal_precision=2)

    add("wheel_dia_memo_note", field_label="Wheel Dia Memo Sent to PPSO", field_type="textarea", required=False)

    add_final_remarks(add)


if __name__ == "__main__":
    run_seed(
        equipment_code="WS_Conv", template_code="108", technology="CONVENTIONAL",
        template_name="Checksheet for Wheel Set/MSU Hitachi/Taochi (WAP-4)",
        description="Wheel Set/MSU Hitachi/Taochi checksheet - WAP-4, Conventional - M4-HR section.",
        build_fn=build,
    )
