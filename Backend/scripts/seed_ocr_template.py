"""
Module 46: seeds the M2-HR Over/Maximum Current Relay (OCR/MCR, 3-Phase) checksheet template.

Source: "OCR relay.pdf" - TRS/ELS/BL/M2HR/3 Phase/OCR & MCR/Checksheet/11.
References: CLW Spec CLW/ES/3/0059 Alt'D dtd 13.04.1999; RDSO MS 420 Rev 0 dtd 23.01.2013
(mechanical interlocking); RDSO MS 432 dtd 12.03.2014 (short link at c-d removal).
"""
from _m2hr_template_helpers import add_confirm, add_date, add_numeric, add_text, run_seed_paged


def build(add, set_page):
    add_text(add, "make", "Make", required=True)
    add_text(add, "sr_no_mfd", "Sr.No/Mfd.", required=True)
    add_date(add, "remove_date_sch", "Remove Date/Sch")
    add_date(add, "date_of_overhauling", "Date of Overhauling")
    add_date(add, "provided_date_sch", "Provided Date/Sch")

    add_confirm(add, "visual_check_aux_contacts", "Auxiliary Contacts Shall Be Examined Visually")
    add_confirm(add, "contact_tips_carbon_free", "The Contact Tips Should Be Free of Carbon")
    add_confirm(add, "aux_contacts_no_nc_simultaneous",
                "Auxiliary Contacts NO and NC Should Operate Simultaneously")
    add_numeric(add, "coil_resistance", "Coil Resistance", "82.34 - 96.66 mΩ (89.5 ± 8%) at 25C",
                min_value=82.34, max_value=96.66, unit="mOhm",
                authority_reference="CLW/ES/3/0059 Alt.D dtd 13.04.1999")
    add_numeric(add, "ambient_temp", "Ambient Temperature at Time of Measurement",
                "Present room temp.", unit="C", decimal_precision=0, required=False)
    add_numeric(add, "contact_gap", "Contact Gap", "0.7 ± 0.1mm", min_value=0.6, max_value=0.8, unit="mm")
    add_numeric(add, "pressure_moving_contact", "Pressure on Moving Contact", "12 ± 3 gm",
                min_value=9.0, max_value=15.0, unit="gm")
    add_numeric(add, "contact_gap_no_condition",
                "Contact Gap Measured Between Contact Tips in N/O Condition",
                "0.6 to 0.8 mm", min_value=0.6, max_value=0.8, unit="mm")
    add_numeric(add, "set_value_pickup", "Set Value (Pick-up)", "3.3 A AC", unit="A",
                authority_reference="RDSO MS 420 Rev 0 dtd 23.01.2013")
    add_numeric(add, "dropout", "Drop-out (ELS/BL M2HR Section Practice)", "1.0 to 2.0 A AC",
                min_value=1.0, max_value=2.0, unit="A")
    add_text(add, "contact_configuration", "Contact Configuration", required=True,
             standard_value="1 NO, 1 NC")


if __name__ == "__main__":
    run_seed_paged(
        equipment_code="OCR",
        template_code="M2HR_OCR",
        technology="3_PHASE",
        template_name="Check Sheet for Over/Maximum Current Relay (OCR or MCR) (AOH/TOH/IOH) - Three Phase Loco",
        description="M2-HR: OCR/MCR checksheet for 3-Phase locomotives.",
        build_fn=build,
    )
