"""
Module 46: seeds the M2-HR Speedometer (SPM, 3-Phase) checksheet template.

Source: "SPM.pdf" - TRS/ELS/BL/M2HR/Comm./SPM/A (shared with the Conventional variant; see
_spm_m2hr_build.py for why). Only Electrical Checking sub-items A/B/C apply to 3-Phase.
"""
from _spm_m2hr_build import build_spm
from _m2hr_template_helpers import run_seed_paged


def build(add, set_page):
    build_spm(add, set_page, conv_only=False)


if __name__ == "__main__":
    run_seed_paged(
        equipment_code="SPM",
        template_code="M2HR_SPM_3PH",
        technology="3_PHASE",
        template_name="Check Sheet for SPM (AOH/TOH/IOH)",
        description="M2-HR: Speedometer (SPM) checksheet for 3-Phase locomotives.",
        build_fn=build,
    )
