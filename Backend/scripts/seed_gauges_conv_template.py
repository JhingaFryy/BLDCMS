"""
Module 46: seeds the M2-HR Gauges (Conventional) checksheet template.

Source: "gauge conv..pdf" - TRS/ELS/BL/M2HR/Conv./Pressure Gauge/Check sheet/X.
References: RDSO/2017/EL/SPEC/0126 (Rev.0); SMI No. RDSO/2015/EL/SMI/0284.

Structurally different from the 3-phase sheet: a single 7-point checklist applies once (not
per-gauge), followed by an 11-row gauge table (BP-1/2, MR/FP-1/2, RS (Pento), AR/PR-1/2, AFI-1/2,
Br.Cy.-1/2) capturing Make, Sr.No, standard check range and observed remark.
"""
from _m2hr_template_helpers import add_confirm, add_text, add_date, run_seed_paged

GAUGES = [
    ("bp1", "BP Gauge-1", "00-05"),
    ("bp2", "BP Gauge-2", "00-05"),
    ("mr_fp1", "MR/FP Gauge-1", "MR-00-10 / FP-00-06"),
    ("mr_fp2", "MR/FP Gauge-2", "MR-00-10 / FP-00-06"),
    ("rs", "RS Gauge (Pento Gauge)", "00-10"),
    ("ar_pr1", "AR/PR Gauge-1", "AR: 00-10 / PR: 00-08"),
    ("ar_pr2", "AR/PR Gauge-2", "AR: 00-10 / PR: 00-08"),
    ("afi1", "AFI Gauge-1", "At 05 per 100 wagons"),
    ("afi2", "AFI Gauge-2", "At 05 per 100 wagons"),
    ("br_cy1", "Br. Cy. Gauge-1", "00-04"),
    ("br_cy2", "Br. Cy. Gauge-2", "00-04"),
]


def build(add, set_page):
    add_date(add, "remove_date_sch", "Remove Date/Sch")
    add_date(add, "date_of_overhauling", "Date of Overhauling")
    add_date(add, "provided_date_sch", "Provided Date/Sch")

    add_confirm(add, "visual_inspect", "Visual Inspection of Gauge for Any Abnormality "
                "(Needle Bent/Broken, Glass Crack/Broken)", done_word="Normal", negative_word="Abnormal")
    add_confirm(add, "clean_cotton_cloth", "Clean the Gauge with Cotton Cloth", done_word="Cleaned")
    add_confirm(add, "open_top_bottom_cover", "Open Top and Bottom Cover", done_word="Done")
    add_confirm(add, "clean_internal_parts", "Clean Internal Parts with Cotton Cloth", done_word="Cleaned")
    add_confirm(add, "hairspring_supply_uniformity", "Ensure Uniformity of Hair Spring Supply",
                done_word="Done")
    add_confirm(add, "nuts_tightness_check", "Check Tightness of Nuts", done_word="Done")
    add_confirm(add, "gauge_range_check_tolerance",
                "Check the Gauge Against a Standard Gauge in the Specific Range "
                "(Tolerance ± 0.1 kg/cm2)", done_word="Done",
                authority_reference="RDSO/2017/EL/SPEC/0126 (Rev.0)")

    for key, label, std_range in GAUGES:
        group = add(f"gauge_{key}", field_label=label, field_type="group", required=False)
        add_text(add, f"gauge_{key}_make", "Make", required=True, parent=group)
        add_text(add, f"gauge_{key}_sr_no", "Sr. No.", required=True, parent=group)
        add_text(add, f"gauge_{key}_check_range", "Check Range (in kg/cm2)", required=False,
                 default_value=std_range, parent=group)
        add_text(add, f"gauge_{key}_remark", "Remark (in kg/cm2)", required=True, parent=group)


if __name__ == "__main__":
    run_seed_paged(
        equipment_code="Gauges_Conv",
        template_code="M2HR_GAUGES_CONV",
        technology="CONVENTIONAL",
        template_name="Check Sheet for Gauges (AOH/TOH/IOH) - Conv. Loco",
        description="M2-HR: Gauges checksheet for Conventional locomotives.",
        build_fn=build,
    )
