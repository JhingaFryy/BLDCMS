"""
Module 40: seeds the BF-1 and BF-2 (Bogie Overhauling, Bogie Frame No.-1 and No.-2, WAG9HC,
3-Phase, M4-HR section) checksheet templates.

Run once: `venv/bin/python scripts/seed_bogie_overhauling_template.py`

Source: "Electric Loco Shed, Valsad - WAG-9HC Loco (TOH/IOH) Check Sheet - Bogie Overhauling"
(pages 2-3 of the supplied WAG-9HC checksheet). BF-1 and BF-2 are two independent equipment
records (already mapped in section_equipment_map) for the loco's two physical bogie frames - the
checklist is identical between them except item 7's hanger lever numbers, so one build() factory
is shared and run_seed() is called twice, per the "shared content, separate equipment_id" pattern
(Module 37).
"""
from _m4hr_template_helpers import add_pass_fail, add_final_remarks, run_seed


def build(hanger_lever_nos):
    def _build(add):
        add_pass_fail(add, "brake_rigging_removed",
            "Remove All Brake Rigging Items From the Bogie Frame Before Overhaul of Bogie Frame",
            done_word="Removed")
        add_pass_fail(add, "bogie_frame_cleaned", "Clean the Bogie Frame", done_word="Cleaned")
        add_pass_fail(add, "critical_areas_rdpt",
            "Critical Areas of Bogie Frame - Pivot Pin, Torque Arm Support, Post for Axle Guide, "
            "Brake Hanger Lever Brackets RDPT to Be Done", done_word="Done")
        add_pass_fail(add, "primary_secondary_spring_seats",
            "Check the Condition of Primary and Secondary Spring Seats (Check for Any Crack)",
            done_word="Checked")
        add_pass_fail(add, "brake_rigging_pins_bushes",
            "Replace All Pins, Bushes and Fasteners of Brake Rigging With New One (IOH/TOH), "
            "Bushes-IOH", done_word="Replaced")
        add_pass_fail(add, "brake_rigging_cutters", "Replace All Brake Rigging Cutters With New One",
            done_word="Replaced")
        add_pass_fail(add, "safety_sling_hanger_lever",
            f"Replace Safety Sling on Hanger Lever No.-{hanger_lever_nos} (RDSO/TC-142)",
            done_word="New", negative_word="Old")
        add_pass_fail(add, "tie_bar_straightness", "Check the Tie Bar for Straightness - Should Not Be Bend",
            done_word="Checked")
        add_pass_fail(add, "safety_sling_tie_bar", "Replace Safety Sling of Tie Bar", done_word="Replaced")
        add_pass_fail(add, "sand_box_intactness",
            "Check the Intactness of Sand Box (Replace the Spring Washer-16mm)", done_word="Replaced")
        add_pass_fail(add, "piston_housing_kerosene", "Piston Housing to Be Clean With Kerosene Oil",
            done_word="Cleaned")
        add_pass_fail(add, "piston_bucket_gasket", "Piston Overhauling, Bucket and Gasket to Be Replace",
            done_word="Replaced")
        add_pass_fail(add, "piston_housing_intactness", "Check the Intactness of Piston Housing With Bogie Frame",
            done_word="Checked")
        add_pass_fail(add, "lateral_vertical_stops", "Check and Replace Lateral and Vertical Stops",
            done_word="Replaced")
        add_pass_fail(add, "brake_blocks_condition", "Check the Condition of Brake Blocks and Replace With New One",
            done_word="Replaced")
        add_pass_fail(add, "torque_arm_bracket_dpt", "Torque Arm Fixing Bracket DPT to Be Done",
            done_word="Done")
        add_pass_fail(add, "damper_chain_hanger_dpt_bogie",
            "DPT to Be Done at All Damper Fixing Bracket, Chain Link Bracket and Brake Hanger Top "
            "Bracket for Any Crack (Bogie Side)", done_word="Done")
        add_pass_fail(add, "damper_chain_dpt_loco_body",
            "DPT to Be Done at All Damper Fixing Bracket and Chain Bracket for Any Crack (Loco Body Side)",
            done_word="Done")
        add_final_remarks(add)
    return _build


if __name__ == "__main__":
    run_seed(
        equipment_code="BF-1", template_code="56", technology="3_PHASE",
        template_name="Checksheet for Bogie Frame-1 Overhauling",
        description="Bogie Overhauling (Bogie Frame No.-1) checksheet - WAG9HC, 3-Phase - M4-HR section.",
        build_fn=build("5,6,7,8"),
    )
    run_seed(
        equipment_code="BF-2", template_code="57", technology="3_PHASE",
        template_name="Checksheet for Bogie Frame-2 Overhauling",
        description="Bogie Overhauling (Bogie Frame No.-2) checksheet - WAG9HC, 3-Phase - M4-HR section.",
        build_fn=build("17,18,19,20"),
    )
