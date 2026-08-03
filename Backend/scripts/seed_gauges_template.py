"""
Module 46: seeds the M2-HR Gauges (3-Phase) checksheet template.

Source: "gauge 3 ph.pdf" - TRS/ELS/BL/M2HR/3 Phase/Pressure Gauge/Check sheet/7.
References: RDSO SMI 298 Rev 0 dt 06.10.2016; RB Instruction Bulletin No. MP.IB-BK-04.19.00.

The sheet lists 11 gauge positions (BP-1, BP-2, MR/FP-1, MR/FP-2, RS, AFI-1, AFI-2, Br.Cy.-1,
Br.Cy.-2, PB-1, PB-2) with the identical 12-point checklist run once per gauge; RS/PB-1/PB-2 are
frequently not fitted (shown as "-" in the sample), so those three are optional groups.
"""
from _m2hr_template_helpers import add_confirm, add_numeric, add_text, add_date, run_seed_paged

CHECK_RANGES = {
    "bp1": "0-5", "bp2": "0-5", "mr_fp1": "0-10/0-6", "mr_fp2": "0-10/0-6", "rs": "0-10",
    "afi1": "0-10", "afi2": "0-10", "br_cy1": "0-4", "br_cy2": "0-4", "pb1": "0-10", "pb2": "0-10",
}


def add_gauge_group(add, key, label, required=True):
    group = add(key, field_label=f"Gauge - {label}", field_type="group", required=False,
                authority_reference="RDSO SMI 298 Rev 0 dt 06.10.2016")
    add_text(add, f"{key}_make", "Make (Name of Gauge)", required=required, parent=group)
    add_text(add, f"{key}_sr_no", "Sr. No.", required=required, parent=group)
    add_confirm(add, f"{key}_visual_inspect",
                "Inspection of Gauge for Any Abnormality (Needle Bent/Broken, Glass Crack/Broken, "
                "Loose Joint/Fastening, Leakage, Other Damage)", required=required, parent=group)
    add_confirm(add, f"{key}_clean_gear_pinion",
                "Clean Grease/Dust/Oil from Gear and Pinion Assembly", done_word="Cleaned",
                required=required, parent=group)
    add_confirm(add, f"{key}_gear_pinion_free_dirt",
                "Gear and Pinion Assembly Should Be Completely Free of Dirt", done_word="Cleaned",
                required=required, parent=group)
    add_confirm(add, f"{key}_no_play_gear_pinion",
                "No Play (Unwanted Looseness or Gap) Between Gear and Pinion",
                done_word="No Looseness", negative_word="Looseness", required=required, parent=group)
    add_confirm(add, f"{key}_led_check", "Check the LED", done_word="LED OK", negative_word="LED Not OK",
                required=required, parent=group)
    add_confirm(add, f"{key}_pcb_card_check",
                "Check PCB Cards for Any Abnormality and Replace if Necessary",
                required=required, parent=group)
    add_confirm(add, f"{key}_connection_tightness", "Check Tightness of Connection",
                done_word="Tightened", negative_word="Loose", required=required, parent=group)
    add_confirm(add, f"{key}_performance_check", "Performance Check", required=required, parent=group)
    add_confirm(add, f"{key}_range_check_tolerance",
                "Check the Gauge Against a Standard Gauge in the Specific Range "
                "(Tolerance ± 0.1 kg/cm2)", required=required, parent=group)
    add_text(add, f"{key}_check_range", "Check Range (in kg/cm2)", required=False,
             default_value=CHECK_RANGES.get(key), parent=group)
    add_text(add, f"{key}_actual_range", "Actual Range (in kg/cm2)", required=required, parent=group)
    add_text(add, f"{key}_remarks", "Remarks", required=False, parent=group)
    return group


def build(add, set_page):
    add_date(add, "remove_date_sch", "Remove Date/Sch")
    add_date(add, "date_of_overhauling", "Date of Overhauling")
    add_date(add, "provided_date_sch", "Provided Date/Sch")

    add_gauge_group(add, "bp1", "BP-1")
    add_gauge_group(add, "bp2", "BP-2")
    add_gauge_group(add, "mr_fp1", "MR/FP-1")
    add_gauge_group(add, "mr_fp2", "MR/FP-2")
    add_gauge_group(add, "rs", "RS", required=False)
    add_gauge_group(add, "afi1", "AFI-1")
    add_gauge_group(add, "afi2", "AFI-2")
    add_gauge_group(add, "br_cy1", "Br.Cy.-1")
    add_gauge_group(add, "br_cy2", "Br.Cy.-2")
    add_gauge_group(add, "pb1", "PB-1", required=False)
    add_gauge_group(add, "pb2", "PB-2", required=False)

    add("gauge_washer_replace", field_label="Items to Be Replaced: Gauge Washer",
        field_type="select", options="Replaced, Not Replaced", required=False,
        standard_value="Replaced", negative_values="Not Replaced")


if __name__ == "__main__":
    run_seed_paged(
        equipment_code="Gauges",
        template_code="M2HR_GAUGES_3PH",
        technology="3_PHASE",
        template_name="Check Sheet for Gauges (AOH/TOH/IOH) - 3 Phase Loco",
        description="M2-HR: Gauges checksheet for 3-Phase locomotives.",
        build_fn=build,
    )
