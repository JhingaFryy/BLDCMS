"""
Module 40: shared helpers for seeding the M4-HR equipment templates (WAG9HC/WAP7/WAP4).

Reuses the exact same `run_seed`/`get_or_create_template`/`clear_existing_fields`/`make_add`
machinery as `_aux_template_helpers.py` (equipment-keyed, page_number always 1, no new template
engine concept) - re-imported here rather than duplicated. The only things genuinely new to this
module are small conveniences for M4-HR's recurring "one activity checklist repeated once per
physical unit" table shape (Bogie Frame's 12 axle guides, Wheel Measurement's 6 wheel sets, Axle
Box Mounting's 12 boxes, etc.) - every one of these is still just plain group/child fields via the
same `add()` callback, never a new field_type or validation_rule.
"""
from _aux_template_helpers import (  # noqa: F401
    add_final_remarks,
    clear_existing_fields,
    get_or_create_template,
    make_add,
    run_seed,
)


def add_pass_fail(add, key, label, done_word="Done", negative_word=None, required=True,
                   standard_value=None, authority_reference=None, parent=None):
    """The single most common M4-HR row shape: a Standard column word (Done/Checked/Cleaned/
    Replaced/Removed/Ensured/Filled/Applied/New) confirmed as either that word or its negation."""
    negative_word = negative_word or f"Not {done_word}"
    return add(
        key, parent=parent, field_label=label, field_type="select",
        options=f"{done_word}, {negative_word}", required=required,
        standard_value=standard_value or done_word,
        authority_reference=authority_reference,
        negative_values=negative_word,
    )


def add_unit_group_table(add, table_key, group_label_prefix, units, activities, parent=None):
    """Repeats the same list of `activities` once per entry in `units` (e.g. Wheel Set 1..6, Axle
    Guide 1..12), each wrapped in its own group so the PDF renders "Wheel Set 3 > Axle Number", etc.

    activities: list of dicts, each either:
      - {"key", "label", **add_kwargs} for a plain leaf field, or
      - {"key", "label", "builder": callable(add, parent_group, unit_label)} for anything more
        specific than a single field (e.g. a DE/NDE pair) - builder does its own add() calls.
    units: list of unit labels (str or int) used both for the field_key suffix and the group label.
    """
    groups = []
    for u in units:
        u_label = str(u)
        u_key = u_label.replace(" ", "_").replace("/", "_").replace("-", "_").replace(".", "").replace("&", "and")
        group = add(f"{table_key}_{u_key}", parent=parent, field_label=f"{group_label_prefix} {u_label}",
                     field_type="group", required=False)
        for act in activities:
            if "builder" in act:
                act["builder"](add, group, u_label)
                continue
            kwargs = {k: v for k, v in act.items() if k not in ("key", "label")}
            add(f"{table_key}_{u_key}_{act['key']}", parent=group, field_label=act["label"], **kwargs)
        groups.append(group)
    return groups
