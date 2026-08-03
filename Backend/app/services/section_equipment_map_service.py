from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.equipment import Equipment
from app.models.section import Section
from app.models.section_equipment_map import SectionEquipmentMap
from app.schemas.section_equipment_map import SectionEquipmentMapCreate


def normalize_technology(value: str | None) -> str | None:
    """SectionEquipmentMap.technology uses a display-style vocabulary ('3-Phase', 'Conventional')
    while Locomotive.technology/ChecksheetTemplate.technology use an underscore/uppercase
    vocabulary ('3_PHASE', 'CONVENTIONAL') - see Module 29.11. This is the single canonicalization
    point so callers can compare a value from either source without duplicating a technology list
    of their own (Module 29.12)."""
    if not value:
        return None
    return value.strip().upper().replace("-", "_").replace(" ", "_")


# Module 46.2: the section this convention was actually introduced for. Without this guard,
# `_group_uses_model_convention` below flags ANY (section, technology) group as model-exclusive
# merely for containing a "_P7"/"_Conv" suffix anywhere in it - which M2-HR's Conventional group
# also does (SPM_Conv, AFR_Conv, etc.), but for the unrelated reason of distinguishing that
# equipment's Conventional variant from its own 3-Phase sibling record, not distinguishing loco
# sub-models. That collision silently excluded M2-HR's one bare-coded equipment, MPCS, from every
# Conventional locomotive's equipment list (every such locomotive in this deployment is WAP-4, so
# `expected_suffix` was always "_Conv", and a bare code only survives when it's None). Scoping this
# check to the section that actually defined the convention closes that gap without touching the
# M4-HR behavior it was built for.
_MODEL_CONVENTION_SECTION_NAME = "M4-HR"


# Module 40 (M4-HR): some sections need the equipment set itself to differ by Locomotive Model,
# not just Technology - WAG9HC and WAP-7 are both 3-Phase but must never share a template
# (different standards, different checking points). Rather than adding a new locomotive_model
# column anywhere, the equipment mapping convention already in the database distinguishes them by
# equipment_code suffix: a bare code (no suffix) is WAG9HC's, "_P7" is WAP-7's, "_Conv" is WAP-4's.
_MODEL_SUFFIXES = {
    "WAP_7": "_P7",
    "WAP7": "_P7",
    "WAP_4": "_Conv",
    "WAP4": "_Conv",
}


def resolve_locomotive_model_suffix(loco_model: str | None) -> str | None:
    """The equipment_code suffix that applies to `loco_model`, or None if bare (unsuffixed)
    equipment codes apply - this includes WAG9HC, and any other locomotive model not covered by
    this convention (e.g. WAP-5), which fall back to the same bare-code equipment set WAG9HC
    uses today. If a future module needs WAP-5 (or another model) to have its own independent
    equipment set, add its suffix here rather than introducing a parallel mechanism."""
    normalized = normalize_technology(loco_model)
    return _MODEL_SUFFIXES.get(normalized)


def _has_model_suffix(equipment_code: str, suffix: str) -> bool:
    """True if `equipment_code` carries the given model suffix ("_P7" or "_Conv"), tolerating
    either an underscore or a hyphen delimiter (e.g. "BF-1_P7" and, pre-existing in the M35-TM
    data, "TM-Conv") - the delimiter is inconsistent in a couple of older equipment codes but the
    semantic intent (this code is exclusive to one locomotive model) is the same either way."""
    return equipment_code.endswith(suffix) or equipment_code.endswith(suffix.replace("_", "-"))


def _group_uses_model_convention(db: Session, equipment_id: int) -> bool:
    """True if the (section, technology) group(s) `equipment_id` is mapped to contain any
    "_P7"/"_Conv" suffixed equipment - meaning that group has opted into locomotive-model-specific
    equipment differentiation (M4-HR's convention). This is checked at the group level, not per
    equipment, because a group can contain bare-coded items that are themselves model-exclusive
    without having a same-named suffixed sibling at all (e.g. M4-HR's "SIHS"/"WC" are WAG9HC-only -
    WAP-7 simply has no equivalent checkpoint, so there's no "SIHS_P7"/"WC_P7" to detect, yet they
    must still be excluded from a WAP-7 locomotive's equipment list). Groups with no suffixed
    equipment at all (M1-HR's 3-Phase equipment, M9-HR, M8-HR, etc.) return False, so their bare
    codes apply to every locomotive model. Restricted to the M4-HR section itself
    (_MODEL_CONVENTION_SECTION_NAME) - see that constant's comment for why: other sections
    (M2-HR included) can legitimately use a "_Conv" suffix of their own for an unrelated reason
    and must never be pulled into this per-loco-model filtering."""
    own_groups = (
        db.query(SectionEquipmentMap.section_id, SectionEquipmentMap.technology)
        .join(Section, Section.id == SectionEquipmentMap.section_id)
        .filter(
            SectionEquipmentMap.equipment_id == equipment_id,
            SectionEquipmentMap.is_active == True,
            Section.name == _MODEL_CONVENTION_SECTION_NAME,
        )
        .all()
    )
    for section_id, technology in own_groups:
        group_codes = (
            db.query(Equipment.equipment_code)
            .join(SectionEquipmentMap, SectionEquipmentMap.equipment_id == Equipment.id)
            .filter(
                SectionEquipmentMap.section_id == section_id,
                SectionEquipmentMap.technology == technology,
                SectionEquipmentMap.is_active == True,
            )
            .all()
        )
        if any(_has_model_suffix(code, "_P7") or _has_model_suffix(code, "_Conv") for (code,) in group_codes):
            return True
    return False


def equipment_code_matches_locomotive_model(db: Session, equipment: "Equipment", loco_model: str | None) -> bool:
    """True if `equipment` is the variant that belongs to `loco_model`, per the suffix convention
    above. A bare equipment code only becomes locomotive-model-exclusive when its own (section,
    technology) group actually uses the "_P7"/"_Conv" convention somewhere (M4-HR) - otherwise
    (every other section/technology group, which never introduced this convention at all) it
    always matches, regardless of loco_model. This filter only ever excludes a code when it
    demonstrably carries one of the recognized suffixes for a *different* model than the one asked
    about, or is a bare code within a group that uses the convention for a model other than the
    one asked about."""
    equipment_code = equipment.equipment_code
    expected_suffix = resolve_locomotive_model_suffix(loco_model)
    has_p7_suffix = _has_model_suffix(equipment_code, "_P7")
    has_conv_suffix = _has_model_suffix(equipment_code, "_Conv")
    if not has_p7_suffix and not has_conv_suffix:
        if not _group_uses_model_convention(db, equipment.id):
            return True
        return expected_suffix is None
    if expected_suffix == "_P7":
        return has_p7_suffix
    if expected_suffix == "_Conv":
        return has_conv_suffix
    return False


def create_mapping(db: Session, mapping: SectionEquipmentMapCreate):
    section = db.query(Section).filter(Section.id == mapping.section_id).first()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section with id {mapping.section_id} not found"
        )

    equipment = db.query(Equipment).filter(Equipment.id == mapping.equipment_id).first()
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment with id {mapping.equipment_id} not found"
        )

    existing_mapping = db.query(SectionEquipmentMap).filter(
        SectionEquipmentMap.section_id == mapping.section_id,
        SectionEquipmentMap.equipment_id == mapping.equipment_id,
        SectionEquipmentMap.technology == mapping.technology
    ).first()
    if existing_mapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A mapping already exists for this section, equipment, and technology."
        )

    new_mapping = SectionEquipmentMap(
        section_id=mapping.section_id,
        equipment_id=mapping.equipment_id,
        technology=mapping.technology
    )

    db.add(new_mapping)
    db.commit()
    db.refresh(new_mapping)
    db.refresh(new_mapping.section)
    db.refresh(new_mapping.equipment)

    return new_mapping


def get_all_mappings(db: Session):
    return db.query(SectionEquipmentMap).options(
        joinedload(SectionEquipmentMap.section),
        joinedload(SectionEquipmentMap.equipment)
    ).all()


def delete_mapping(db: Session, mapping_id: int):
    mapping = db.query(SectionEquipmentMap).filter(
        SectionEquipmentMap.id == mapping_id
    ).first()

    if mapping:
        db.delete(mapping)
        db.commit()

    return mapping
