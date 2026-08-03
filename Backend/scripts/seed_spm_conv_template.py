"""
Module 46: seeds the M2-HR Speedometer (SPM, Conventional) checksheet template.

Source: "SPM.pdf" - TRS/ELS/BL/M2HR/Comm./SPM/A (shared with the 3-Phase variant; see
_spm_m2hr_build.py for why). Electrical Checking sub-items A-F all apply to Conventional.
"""
from _spm_m2hr_build import build_spm
from _m2hr_template_helpers import run_seed_paged


def build(add, set_page):
    build_spm(add, set_page, conv_only=True)


if __name__ == "__main__":
    run_seed_paged(
        equipment_code="SPM_Conv",
        template_code="M2HR_SPM_CONV",
        technology="CONVENTIONAL",
        template_name="Check Sheet for SPM (AOH/TOH/IOH)",
        description="M2-HR: Speedometer (SPM) checksheet for Conventional locomotives.",
        build_fn=build,
    )
