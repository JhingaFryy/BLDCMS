"""
Module 29.5 seed data: M35-Aux section common page + illustrative TMB template.

Run once against the live database: `venv/bin/python scripts/seed_m35_aux_tmb_template.py`

What this does:
1. Creates a new section-common ChecksheetTemplate (section_id=5 "M35-Aux",
   equipment_id=NULL) with the 6-field Common Auxiliary Information page.
2. Soft-retires (is_active=False) the old duplicate common-info fields (ids 8-13)
   on the existing TMB template (id=5), since that data is now supplied by the
   common page instead. NOT deleted: checksheet_id=2 has real historical
   checksheet_value rows referencing these fields, and TemplateField has no
   delete cascade onto ChecksheetValue.
3. Enriches the 3 remaining real inspection fields (ids 14-16) in place with the
   new standard_value/authority_reference metadata and moves them to page 2 -
   safe because checksheet_value only references field_id, never field_key/label.
4. Adds new illustrative fields to the TMB template covering every field type
   not yet exercised: NUMERIC_RANGE, GROUP (matching the spec's literal
   "Run Test After Assembly" -> "No Load Current"/"Full Load Current"/
   "Temperature Rise" -> U/V/W / RY/YB/BR example) on the template's own page 1,
   plus BOOLEAN and MULTILINE REMARKS on its own page 2 - proving multi-page
   navigation within a single equipment template, on top of the common-page
   composition (composed as pages 2 and 3 once the section's common page 1 is
   prepended).

Idempotent: safe to re-run - checks for existing rows by template_code / field_key
before inserting.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.database import SessionLocal
from app.models.checksheet_template import ChecksheetTemplate
from app.models.template_field import TemplateField

SECTION_ID_M35_AUX = 5
TMB_TEMPLATE_ID = 5


def main():
    db = SessionLocal()
    try:
        seed_common_page(db)
        retire_redundant_fields(db)
        enrich_existing_inspection_fields(db)
        add_illustrative_fields(db)
        db.commit()
        print("Seed complete.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def seed_common_page(db):
    existing = (
        db.query(ChecksheetTemplate)
        .filter(ChecksheetTemplate.template_code == "M35-AUX-COMMON")
        .first()
    )
    if existing:
        print(f"Common page template already exists (id={existing.id}), skipping creation.")
        return

    common_template = ChecksheetTemplate(
        template_code="M35-AUX-COMMON",
        version=1,
        equipment_id=None,
        section_id=SECTION_ID_M35_AUX,
        technology="COMMON",
        template_name="M35-Aux Common Auxiliary Information",
        description="Common first page for every equipment under Section M35-Aux.",
        is_active=True,
    )
    db.add(common_template)
    db.flush()

    common_fields = [
        dict(field_key="aux_serial_number", field_label="Auxiliary Serial Number", field_type="text", display_order=1, required=True),
        dict(field_key="aux_make", field_label="Make", field_type="text", display_order=2, required=True),
        dict(field_key="mfg_date", field_label="Manufacturing Date", field_type="date", display_order=3, required=False, help_text="DD-MM-YYYY"),
        dict(field_key="rewinding_date", field_label="Rewinding Date", field_type="date", display_order=4, required=False, help_text="DD-MM-YYYY"),
        dict(field_key="overhaul_date", field_label="Overhaul Date", field_type="date", display_order=5, required=False, help_text="DD-MM-YYYY"),
        dict(field_key="vpi_date", field_label="VPI Date", field_type="date", display_order=6, required=False, help_text="DD-MM-YYYY"),
    ]
    for f in common_fields:
        db.add(TemplateField(template_id=common_template.id, page_number=1, **f))

    print(f"Created common page template id={common_template.id} with {len(common_fields)} fields.")


def retire_redundant_fields(db):
    # Superseded by the new common page's own aux_serial_number/aux_make/mfg_date/rewinding_date/
    # overhaul_date/vpi_date fields. Kept (not deleted) because checksheet_id=2 has real historical
    # checksheet_value rows referencing these exact field_ids.
    redundant_ids = [8, 9, 10, 11, 12, 13]
    fields = db.query(TemplateField).filter(TemplateField.id.in_(redundant_ids)).all()
    for f in fields:
        f.is_active = False
    print(f"Retired {len(fields)} redundant common-info fields on template id={TMB_TEMPLATE_ID}: {[f.id for f in fields]}")


def enrich_existing_inspection_fields(db):
    # (field_id, new field_key, standard_value, authority_reference, unit, display_order)
    updates = {
        14: dict(field_key="pre_test_vibration", standard_value="Normal", authority_reference="Maintenance Manual Cl. 3.1", unit=None, display_order=1),
        15: dict(field_key="ir_value_before_dismantle", standard_value="Min 1 MOhm", authority_reference="IS 732 / Maintenance Manual", unit="MOhm", display_order=2),
        16: dict(field_key="cleaning_backing_varnishing", standard_value="Done", authority_reference="Maintenance Manual Cl. 3.4", unit=None, display_order=3),
    }
    fields = db.query(TemplateField).filter(TemplateField.id.in_(updates.keys())).all()
    for f in fields:
        u = updates[f.id]
        f.field_key = u["field_key"]
        f.standard_value = u["standard_value"]
        f.authority_reference = u["authority_reference"]
        f.unit = u["unit"]
        f.page_number = 1
        f.display_order = u["display_order"]
    print(f"Enriched {len(fields)} existing inspection fields (ids {list(updates.keys())}) -> page 1.")


def add_illustrative_fields(db):
    existing_keys = {
        f.field_key
        for f in db.query(TemplateField).filter(TemplateField.template_id == TMB_TEMPLATE_ID).all()
    }

    def add(field_key, **kwargs):
        if field_key in existing_keys:
            print(f"  field '{field_key}' already exists, skipping.")
            return None
        f = TemplateField(template_id=TMB_TEMPLATE_ID, field_key=field_key, **kwargs)
        db.add(f)
        db.flush()
        existing_keys.add(field_key)
        return f

    # --- Page 1 additions: NUMERIC_RANGE + GROUP examples, continuing the inspection checklist ---
    add(
        "insulation_resistance_after_overhaul",
        field_label="Insulation Resistance (IR Value After Overhaul)",
        field_type="numeric_range",
        display_order=4,
        required=True,
        unit="MOhm",
        min_value=1.0,
        max_value=1000.0,
        decimal_precision=2,
        standard_value="1 - 1000 MOhm",
        authority_reference="Maintenance Manual Cl. 4.2",
        page_number=1,
    )

    run_test = add(
        "run_test_after_assembly",
        field_label="Run Test After Assembly",
        field_type="group",
        display_order=5,
        required=False,
        page_number=1,
    )
    if run_test is not None:
        no_load = add(
            "no_load_current",
            field_label="No Load Current",
            field_type="group",
            display_order=6,
            required=False,
            parent_field_id=run_test.id,
            page_number=1,
        )
        full_load = add(
            "full_load_current",
            field_label="Full Load Current",
            field_type="group",
            display_order=7,
            required=False,
            parent_field_id=run_test.id,
            page_number=1,
        )
        temp_rise = add(
            "temperature_rise",
            field_label="Temperature Rise",
            field_type="group",
            display_order=8,
            required=False,
            parent_field_id=run_test.id,
            page_number=1,
        )

        order = 9
        for group, phases in [(no_load, ["U", "V", "W"]), (full_load, ["U", "V", "W"])]:
            for phase in phases:
                add(
                    f"{group.field_key}_{phase.lower()}",
                    field_label=phase,
                    field_type="number",
                    display_order=order,
                    required=False,
                    unit="A",
                    parent_field_id=group.id,
                    page_number=1,
                )
                order += 1

        for phase in ["RY", "YB", "BR"]:
            add(
                f"temperature_rise_{phase.lower()}",
                field_label=phase,
                field_type="number",
                display_order=order,
                required=False,
                unit="C",
                parent_field_id=temp_rise.id,
                page_number=1,
            )
            order += 1

    # --- Page 3: proves multi-page navigation within a single equipment template ---
    add(
        "fit_for_service",
        field_label="Fit For Service",
        field_type="boolean",
        display_order=1,
        required=True,
        page_number=2,
    )
    add(
        "final_remarks",
        field_label="Final Remarks",
        field_type="textarea",
        display_order=2,
        required=False,
        page_number=2,
    )

    print("Illustrative fields added (numeric_range, group x4 with 9 leaves, boolean, textarea).")


if __name__ == "__main__":
    main()
