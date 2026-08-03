"""
Module 40: seeds the BF-1_P7 and BF-2_P7 (Bogie Overhauling, Bogie Frame No.-1 and No.-2, WAP-7,
3-Phase, M4-HR section) checksheet templates.

Run once: `venv/bin/python scripts/seed_bogie_overhauling_p7_template.py`

Source: "WAP-7 Loco (TOH/IOH) Check Sheet - Bogie Overhauling" (pages 1-2 of the supplied WAP-7
checksheet). Deliberately independent from the WAG9HC Bogie Overhauling template
(seed_bogie_overhauling_template.py) - this sheet has only 15 checking points, NOT 18: the three
DPT items for torque arm fixing bracket and damper/chain-link/brake-hanger brackets (bogie side
and loco body side) that exist on the WAG9HC sheet are absent here entirely, not merely
simplified. Do not merge with the WAG9HC template.
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
        add_final_remarks(add)
    return _build


if __name__ == "__main__":
    run_seed(
        equipment_code="BF-1_P7", template_code="80", technology="3_PHASE",
        template_name="Checksheet for Bogie Frame-1 Overhauling (WAP-7)",
        description="Bogie Overhauling (Bogie Frame No.-1) checksheet - WAP-7, 3-Phase - M4-HR section.",
        build_fn=build("5,6,7,8"),
    )
    run_seed(
        equipment_code="BF-2_P7", template_code="81", technology="3_PHASE",
        template_name="Checksheet for Bogie Frame-2 Overhauling (WAP-7)",
        description="Bogie Overhauling (Bogie Frame No.-2) checksheet - WAP-7, 3-Phase - M4-HR section.",
        build_fn=build("17,18,19,20"),
    )
