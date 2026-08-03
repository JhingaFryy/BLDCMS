"""
Module 46: seeds the M2-HR Pressure Switch (Conventional) checksheet template.

Source: "pressure switch conv..pdf" - TRS/ELS/BL/M2HR/Conv./Pressure Switch/Check sheet/IX.
Page 1 is a 9-point maintenance checklist; page 2 is the per-switch setting table (8 switches:
RGCP, RGEB, RGAF, QPH, P-1, P-2, SWC, SA-9) with cut-in/cut-out standard + tolerance + actual.
"""
from _m2hr_template_helpers import add_confirm, add_date, add_numeric, add_text, run_seed_paged


def add_switch_setting(add, key, label, std_ref, cut_in, cut_out, tolerance):
    group = add(key, field_label=f"Pressure Switch Setting - {label}", field_type="group",
                required=False, authority_reference=std_ref)
    add_text(add, f"{key}_make", "Make/Type", required=True, parent=group)
    add_text(add, f"{key}_sr_no", "Sr. No. of Pressure Switch", required=True, parent=group)
    add_numeric(add, f"{key}_cut_in", "Cut in", f"{cut_in} ± {tolerance}", unit="kg/cm2",
                decimal_precision=2, parent=group)
    add_numeric(add, f"{key}_cut_out", "Cut out",
                f"{cut_out} ± {tolerance}" if cut_out is not None else None,
                unit="kg/cm2", decimal_precision=2, required=cut_out is not None, parent=group)
    return group


def build(add, set_page):
    add_text(add, "equipment_no", "Equipment No", required=False)
    add_text(add, "pneumatic_panel_make", "Pneumatic Panel Make", required=False)
    add_text(add, "mfg_year", "MFG Year", required=False)
    add_date(add, "remove_date_sch", "Remove Date/Sch")
    add_date(add, "date_of_overhauling", "Date of Overhauling")
    add_date(add, "provided_date_sch", "Provided Date/Sch")

    add_confirm(add, "external_internal_check", "Check the External and Internal Condition")
    add_confirm(add, "clean_dry_air", "Clean the Pressure Switch Using Dry Air", done_word="Clean",
                negative_word="Not Clean")
    add_confirm(add, "open_clean_inspect", "Open the Pressure Switch, Clean It, and Inspect for "
                "Proper Operation")
    add_confirm(add, "replace_micro_switch", "Replace the Micro Switch Based on Its Condition, "
                "if Necessary")
    add_confirm(add, "wear_tear_check", "Check Parts for Any Signs of Wear and Tear, Replace "
                "the Main Spring and Knob Settings if Necessary")
    add_confirm(add, "connection_terminals_check", "Inspect the Connection Terminals")
    add_confirm(add, "air_leakage_test", "Perform an Air Leakage Test")
    add_confirm(add, "pickup_dropout_check", "Verify Proper Pick-up and Drop-out Values According "
                "to Specifications and Records")
    add_confirm(add, "bench_overhaul_settings", "Verify Overhauling and Settings on the Test Bench")

    std_ref = "RDSO letter EL/3.2.19(G) / RDSO SMI 197-2001 / CLW MM WAP4 Vol 4 / CLW SPEC CLW/ES/S-24"
    add_switch_setting(add, "rgcp", "RGCP", "RDSO letter No. EL/3.2.19(G) dtd 18.10.2012", 8.0, 9.5, 0.1)
    add_switch_setting(add, "rgeb", "RGEB", "RDSO SMI 197-2001 (Rev-1) dtd 22.06.2001 Para 5(viii)", 4.2, 2.5, 0.1)
    add_switch_setting(add, "rgaf", "RGAF", "CLW MM WAP 4 Vol -4, Section-III 2000 - Para 2.7", 4.0, 3.5, 0.1)
    add_switch_setting(add, "qph", "QPH", "CLW SPEC CLW/ES/S-24/Alt.J", 0.6, 0.3, 0.1)
    add_switch_setting(add, "p1", "P-1", "RDSO TC 93 DT 30/08/06", 4.8, 4.6, 0.1)
    add_switch_setting(add, "p2", "P-2", "RDSO TC 93 DT 30/08/06", 4.6, 4.4, 0.1)
    add_switch_setting(add, "swc", "SWC", "D1: CLW SPEC CLW/ES/S-24/Alt.J", 1.0, 0.3, 0.1)
    add_switch_setting(add, "sa9", "SA-9", None, 1.5, None, 0.1)


if __name__ == "__main__":
    run_seed_paged(
        equipment_code="PS_Conv",
        template_code="M2HR_PS_CONV",
        technology="CONVENTIONAL",
        template_name="Check Sheet for Pressure Switch (AOH/TOH/IOH) - Conv. Loco",
        description="M2-HR: Pressure Switch checksheet for Conventional locomotives.",
        build_fn=build,
    )
