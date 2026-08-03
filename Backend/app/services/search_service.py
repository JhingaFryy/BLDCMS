from sqlalchemy import or_
from sqlalchemy.orm import Session, contains_eager

from app.models.checksheet_header import ChecksheetHeader
from app.models.checksheet_template import ChecksheetTemplate
from app.models.equipment import Equipment
from app.models.locomotive import Locomotive
from app.models.section import Section
from app.models.section_equipment_map import SectionEquipmentMap
from app.models.user import User
from app.security.section_scope import supervisor_section_id

RESULTS_PER_CATEGORY = 10


def _search_locomotives(db: Session, term: str, scoped_section_id: int | None):
    query = db.query(Locomotive).filter(Locomotive.loco_number.ilike(term))
    if scoped_section_id is not None:
        # Locomotive has no section_id of its own - "belongs to a section" means it has at least
        # one checksheet against that section (same definition used by Module 27.5).
        query = (
            query.join(ChecksheetHeader, ChecksheetHeader.locomotive_id == Locomotive.id)
            .filter(ChecksheetHeader.section_id == scoped_section_id)
            .distinct()
        )
    rows = query.limit(RESULTS_PER_CATEGORY).all()
    return [
        {"id": r.id, "label": r.loco_number, "subtitle": r.loco_model, "nav_key": str(r.id)}
        for r in rows
    ]


def _search_equipment(db: Session, term: str, scoped_section_id: int | None):
    query = db.query(Equipment).filter(Equipment.equipment_name.ilike(term))
    if scoped_section_id is not None:
        query = (
            query.join(SectionEquipmentMap, SectionEquipmentMap.equipment_id == Equipment.id)
            .filter(SectionEquipmentMap.section_id == scoped_section_id)
            .distinct()
        )
    rows = query.limit(RESULTS_PER_CATEGORY).all()
    return [
        {"id": r.id, "label": r.equipment_name, "subtitle": r.equipment_code, "nav_key": str(r.id)}
        for r in rows
    ]


def _search_sections(db: Session, term: str, scoped_section_id: int | None):
    query = db.query(Section).filter(Section.name.ilike(term))
    if scoped_section_id is not None:
        # A Supervisor's own section either matches the search term or it doesn't - there is
        # nothing else for them to find here.
        query = query.filter(Section.id == scoped_section_id)
    rows = query.limit(RESULTS_PER_CATEGORY).all()
    return [{"id": r.id, "label": r.name, "subtitle": None, "nav_key": str(r.id)} for r in rows]


def _search_users(db: Session, term: str, scoped_section_id: int | None):
    query = db.query(User).filter(or_(User.name.ilike(term), User.employee_id.ilike(term)))
    if scoped_section_id is not None:
        query = query.filter(User.section_id == scoped_section_id)
    rows = query.limit(RESULTS_PER_CATEGORY).all()
    return [
        {
            "id": r.id,
            "label": r.name,
            "subtitle": f"{r.role} - {r.employee_id}",
            # The existing GET /users/ endpoint searches by employee_id (not numeric id) - reusing
            # that as the nav_key lets the Users page resolve this result with zero new endpoints.
            "nav_key": r.employee_id,
        }
        for r in rows
    ]


def _search_checksheets(db: Session, raw_term: str, term: str, scoped_section_id: int | None):
    query = (
        db.query(ChecksheetHeader)
        .join(ChecksheetHeader.locomotive)
        .options(contains_eager(ChecksheetHeader.locomotive))
    )
    conditions = [
        Locomotive.loco_number.ilike(term),
        ChecksheetHeader.work_type.ilike(term),
    ]
    stripped = raw_term.strip()
    if stripped.isdigit():
        conditions.append(ChecksheetHeader.id == int(stripped))
    query = query.filter(or_(*conditions))
    if scoped_section_id is not None:
        query = query.filter(ChecksheetHeader.section_id == scoped_section_id)
    rows = query.limit(RESULTS_PER_CATEGORY).all()
    return [
        {
            "id": r.id,
            "label": f"Checksheet #{r.id}",
            "subtitle": f"{r.locomotive.loco_number if r.locomotive else '-'} - {r.status}",
            "nav_key": str(r.id),
        }
        for r in rows
    ]


def _search_templates(db: Session, term: str, scoped_section_id: int | None):
    query = db.query(ChecksheetTemplate).filter(
        or_(
            ChecksheetTemplate.template_name.ilike(term),
            ChecksheetTemplate.template_code.ilike(term),
        )
    )
    if scoped_section_id is not None:
        # ChecksheetTemplate has no section_id of its own - "available for a section" means its
        # equipment is mapped to that section (same definition used by Module 27.5).
        query = (
            query.join(Equipment, ChecksheetTemplate.equipment_id == Equipment.id)
            .join(SectionEquipmentMap, SectionEquipmentMap.equipment_id == Equipment.id)
            .filter(SectionEquipmentMap.section_id == scoped_section_id)
            .distinct()
        )
    rows = query.limit(RESULTS_PER_CATEGORY).all()
    return [
        {"id": r.id, "label": r.template_name, "subtitle": r.template_code, "nav_key": str(r.id)}
        for r in rows
    ]


def global_search(db: Session, raw_query: str, current_user: User) -> dict:
    """Single entry point for Module 28's Global Search - one query per category (six total),
    each already limited and index-friendly on its primary lookup column, so this never issues
    more queries than there are categories regardless of result size (no N+1). Section-based
    filtering for Supervisors is derived from the authenticated user, never from a client param -
    same enforcement point (`supervisor_section_id`) Module 27.5 already established for every
    other endpoint that returns this data.
    """
    term = f"%{raw_query.strip()}%"
    scoped_section_id = supervisor_section_id(current_user)

    return {
        "locomotives": _search_locomotives(db, term, scoped_section_id),
        "equipment": _search_equipment(db, term, scoped_section_id),
        "sections": _search_sections(db, term, scoped_section_id),
        "users": _search_users(db, term, scoped_section_id),
        "checksheets": _search_checksheets(db, raw_query, term, scoped_section_id),
        "templates": _search_templates(db, term, scoped_section_id),
    }
