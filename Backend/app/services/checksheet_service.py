from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload, contains_eager

from app.core.logging import get_logger
from app.models.checksheet_header import ChecksheetHeader
from app.models.checksheet_value import ChecksheetValue
from app.models.checksheet_template import ChecksheetTemplate
from app.models.locomotive import Locomotive
from app.models.equipment import Equipment
from app.models.section import Section
from app.schemas.checksheet_header import (
    ChecksheetHeaderCreate,
    ChecksheetHeaderUpdate,
    ChecksheetStatusUpdate,
    ChecksheetStatus
)
from app.models.user import User
from app.models.template_field import TemplateField
from app.models.section_equipment_map import SectionEquipmentMap
from app.security.section_scope import supervisor_section_id
from app.services.notification_service import create_notification
from app.services.section_equipment_map_service import equipment_code_matches_locomotive_model, normalize_technology
from app.services.validation_service import validate_checksheet_values

security_logger = get_logger("app.security")

VALID_STATUS_TRANSITIONS = {
    ChecksheetStatus.DRAFT: [ChecksheetStatus.SUBMITTED],
    ChecksheetStatus.SUBMITTED: [ChecksheetStatus.UNDER_REVIEW],
    ChecksheetStatus.UNDER_REVIEW: [ChecksheetStatus.APPROVED, ChecksheetStatus.REJECTED],
    ChecksheetStatus.APPROVED: [],
    ChecksheetStatus.REJECTED: []
}


def _serialize_header(header: ChecksheetHeader):
    return {
        "id": header.id,
        "locomotive_id": header.locomotive_id,
        "section_id": header.section_id,
        "equipment_id": header.equipment_id,
        "template_id": header.template_id,
        "template_name": header.template.template_name if header.template else None,
        "technician_mobile": header.technician_mobile,
        "technician_name": header.technician.name if header.technician else None,
        "technician_employee_id": header.technician.employee_id if header.technician else None,
        "work_type": header.work_type,
        "traction_motor_number": header.traction_motor_number,
        "maintenance_type": header.maintenance_type,
        "locomotive_number": header.locomotive.loco_number if header.locomotive else None,
        "locomotive_type": header.locomotive.loco_model if header.locomotive else None,
        "technology": header.locomotive.technology if header.locomotive else None,
        "equipment_name": header.equipment.equipment_name if header.equipment else None,
        "section_name": header.section.name if header.section else None,
        "status": header.status,
        "submitted_at": header.submitted_at,
        "submitted_by": header.submitted_by,
        "approved_at": header.approved_at,
        "approved_by": header.approved_by,
        "rejected_at": header.rejected_at,
        "rejected_by": header.rejected_by,
        "rejection_reason": header.rejection_reason,
        "last_modified_at": header.last_modified_at,
        "last_modified_by": header.last_modified_by,
        "pdf_path": header.pdf_path,
        "created_at": header.created_at,
        # Module 39: present only once a checksheet has actually been digitally signed - None for
        # every checksheet approved before this module existed, and for every non-APPROVED status.
        "digital_signature": _serialize_digital_signature(getattr(header, "digital_signature", None)),
    }


def _serialize_digital_signature(signature: Any) -> dict | None:
    if signature is None:
        return None
    return {
        "id": signature.id,
        "checksheet_id": signature.checksheet_id,
        "supervisor_id": signature.supervisor_id,
        "supervisor_name": signature.supervisor_name,
        "supervisor_employee_id": signature.supervisor_employee_id,
        "certificate_subject": signature.certificate_subject,
        "certificate_issuer": signature.certificate_issuer,
        "certificate_serial_number": signature.certificate_serial_number,
        "certificate_thumbprint": signature.certificate_thumbprint,
        "certificate_valid_from": signature.certificate_valid_from,
        "certificate_valid_to": signature.certificate_valid_to,
        "signing_timestamp": signature.signing_timestamp,
        "signature_hash": signature.signature_hash,
        "verification_status": signature.verification_status,
        "provider": signature.provider,
        "created_at": signature.created_at,
    }


def _serialize_detail(header: ChecksheetHeader):
    result = _serialize_header(header)

    # Module 29.9: validated once per request, against the FULL set of the equipment template's
    # own fields (via header.template.fields, not just header.values) plus whatever else the
    # checksheet has a value row for (e.g. a section common page, which is a separate template).
    # Deriving this purely from header.values would silently drop a GROUP field's own
    # validation_rule/validation_threshold metadata (Rules 3/4) whenever that group happens to have
    # no submitted value row of its own for any reason - the group carries the rule, not its leaves,
    # so the cross-field check must always be able to see it regardless of submission completeness.
    # Same engine output pdf_service uses to color FAILed observations, so the API response and the
    # PDF are always in agreement.
    fields = list(header.template.fields) if header.template else []
    seen_field_ids = {f.id for f in fields}
    for value in header.values:
        if value.field and value.field.id not in seen_field_ids:
            fields.append(value.field)
            seen_field_ids.add(value.field.id)
    values_by_field_id = {value.field_id: value.field_value for value in header.values}
    validation_results = validate_checksheet_values(fields, values_by_field_id)

    result["values"] = [
        {
            "field_id": value.field_id,
            # Breadcrumb-flattened (e.g. "Bearing Seat Dia. of Rotor Shaft (for 6313) > DE") so a
            # grouped field's bare leaf label is never ambiguous in the Dashboard/Android Supervisor
            # Review screens or checksheet history - same helper the PDF uses (TemplateField.breadcrumb_label).
            "field_label": value.field.breadcrumb_label() if value.field else None,
            "field_key": value.field.field_key if value.field else None,
            "field_type": value.field.field_type if value.field else None,
            "display_order": value.field.display_order if value.field else None,
            "required": value.field.required if value.field else None,
            "unit": value.field.unit if value.field else None,
            "default_value": value.field.default_value if value.field else None,
            "options": value.field.options if value.field else None,
            "help_text": value.field.help_text if value.field else None,
            "field_value": value.field_value,
            # Inherited from the nearest ancestor group if this specific leaf has none of its own
            # (e.g. "Winding Resistance for Comparison > RY" inherits the group's "Difference not
            # more than 10%" / "TC-142") - see TemplateField.effective_standard_value/_authority_reference.
            "standard_value": value.field.effective_standard_value() if value.field else None,
            "authority_reference": value.field.effective_authority_reference() if value.field else None,
            "validation_status": validation_results[value.field_id].status if value.field_id in validation_results else None,
        }
        for value in header.values
    ]
    return result


SORT_COLUMNS = {
    "created_at": ChecksheetHeader.created_at,
    "submitted_at": ChecksheetHeader.submitted_at,
    "loco_number": Locomotive.loco_number,
    "equipment_name": Equipment.equipment_name,
}


def get_checksheet_list(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
    section_id: int | None = None,
    equipment_id: int | None = None,
    locomotive_id: int | None = None,
    locomotive_type: str | None = None,
    technology: str | None = None,
    work_type: str | None = None,
    status: ChecksheetStatus | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    current_user: User | None = None
):
    # locomotive_id/section_id are non-nullable FKs, so joining them (rather than joinedload)
    # never drops rows and lets search/filter/sort reference Locomotive columns directly;
    # contains_eager reuses that same join for serialization instead of issuing a second
    # redundant join. equipment_id is nullable as of Module 36 (M6-HR has no equipment) - an
    # inner join there would silently drop every M6-HR checksheet from this list, so it must be
    # an outer join; contains_eager still works with it (populates None on the outer-join side).
    query = (
        db.query(ChecksheetHeader)
        .join(ChecksheetHeader.locomotive)
        .outerjoin(ChecksheetHeader.equipment)
        .join(ChecksheetHeader.section)
        .options(
            joinedload(ChecksheetHeader.template),
            joinedload(ChecksheetHeader.technician),
            # Module 39: MUST stay a LEFT OUTER JOIN (joinedload's default - do not add
            # innerjoin=True here or switch to .join()). Checksheets approved before Module 39
            # have no digital_signatures row at all; an inner join here would silently drop every
            # one of them from this list for both Admins and Supervisors. See
            # _serialize_header/digital_signature below, which already treats a null
            # header.digital_signature as the normal "legacy approval" case, not an error.
            joinedload(ChecksheetHeader.digital_signature),
            contains_eager(ChecksheetHeader.locomotive),
            contains_eager(ChecksheetHeader.equipment),
            contains_eager(ChecksheetHeader.section)
        )
    )

    if current_user and current_user.role == "Technician":
        query = query.filter(ChecksheetHeader.technician_mobile == current_user.mobile)

    if current_user:
        scoped_section_id = supervisor_section_id(current_user)
        if scoped_section_id is not None:
            # Unconditional - ANDed with whatever section_id filter (if any) the client also
            # sent, so a Supervisor can never widen results beyond their own section by passing
            # a different value. This is the server-side enforcement Module 27.5 requires; the
            # `section_id` query param below remains purely a convenience filter within it.
            query = query.filter(ChecksheetHeader.section_id == scoped_section_id)

    if search:
        search_term = f"%{search}%"
        search_conditions = [
            ChecksheetHeader.technician_mobile.ilike(search_term),
            ChecksheetHeader.work_type.ilike(search_term),
            Locomotive.loco_number.ilike(search_term),
            Equipment.equipment_name.ilike(search_term)
        ]
        stripped_search = search.strip()
        if stripped_search.isdigit():
            search_conditions.append(ChecksheetHeader.id == int(stripped_search))
        query = query.join(ChecksheetHeader.template).filter(or_(
            *search_conditions,
            ChecksheetTemplate.template_name.ilike(search_term)
        ))
    if section_id is not None:
        query = query.filter(ChecksheetHeader.section_id == section_id)
    if equipment_id is not None:
        query = query.filter(ChecksheetHeader.equipment_id == equipment_id)
    if locomotive_id is not None:
        query = query.filter(ChecksheetHeader.locomotive_id == locomotive_id)
    if locomotive_type is not None:
        query = query.filter(Locomotive.loco_model == locomotive_type)
    if technology is not None:
        query = query.filter(Locomotive.technology == technology)
    if work_type is not None:
        query = query.filter(ChecksheetHeader.work_type == work_type)
    if status is not None:
        query = query.filter(ChecksheetHeader.status == status.value)
    if date_from is not None:
        query = query.filter(ChecksheetHeader.created_at >= date_from)
    if date_to is not None:
        query = query.filter(ChecksheetHeader.created_at <= date_to)

    total = query.count()

    sort_column = SORT_COLUMNS.get(sort_by, ChecksheetHeader.created_at)
    query = query.order_by(sort_column.asc() if sort_order.lower() == "asc" else sort_column.desc())

    items = query.offset(skip).limit(limit).all()
    return {"items": [_serialize_header(item) for item in items], "total": total}


def _build_analytics_base_query(
    db: Session,
    section_id: int | None = None,
    equipment_id: int | None = None,
    locomotive_id: int | None = None,
    locomotive_type: str | None = None,
    technology: str | None = None,
    work_type: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    supervisor_id: int | None = None
):
    # equipment_id is nullable as of Module 36 (M6-HR) - outer join so those checksheets aren't
    # silently excluded from analytics/counts, matching the same fix in get_checksheet_list above.
    query = (
        db.query(ChecksheetHeader)
        .join(ChecksheetHeader.locomotive)
        .outerjoin(ChecksheetHeader.equipment)
        .join(ChecksheetHeader.section)
    )
    if section_id is not None:
        query = query.filter(ChecksheetHeader.section_id == section_id)
    if equipment_id is not None:
        query = query.filter(ChecksheetHeader.equipment_id == equipment_id)
    if locomotive_id is not None:
        query = query.filter(ChecksheetHeader.locomotive_id == locomotive_id)
    if locomotive_type is not None:
        query = query.filter(Locomotive.loco_model == locomotive_type)
    if technology is not None:
        query = query.filter(Locomotive.technology == technology)
    if work_type is not None:
        query = query.filter(ChecksheetHeader.work_type == work_type)
    if date_from is not None:
        query = query.filter(ChecksheetHeader.created_at >= date_from)
    if date_to is not None:
        query = query.filter(ChecksheetHeader.created_at <= date_to)
    if supervisor_id is not None:
        # A checksheet's last_modified_by becomes the supervisor's id the moment they act on it
        # (move to review / approve / reject) - the simplest single-column proxy for "checksheets
        # this supervisor is handling or most recently decided on", since there is no dedicated
        # assigned-supervisor column on ChecksheetHeader.
        query = query.filter(ChecksheetHeader.last_modified_by == supervisor_id)
    return query


def get_checksheet_analytics(
    db: Session,
    section_id: int | None = None,
    equipment_id: int | None = None,
    locomotive_id: int | None = None,
    locomotive_type: str | None = None,
    technology: str | None = None,
    work_type: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    supervisor_id: int | None = None,
    current_user: User | None = None
):
    base_query = _build_analytics_base_query(
        db,
        section_id=section_id,
        equipment_id=equipment_id,
        locomotive_id=locomotive_id,
        locomotive_type=locomotive_type,
        technology=technology,
        work_type=work_type,
        date_from=date_from,
        date_to=date_to,
        supervisor_id=supervisor_id
    )
    if current_user and current_user.role == "Technician":
        base_query = base_query.filter(ChecksheetHeader.technician_mobile == current_user.mobile)

    scoped_section_id = supervisor_section_id(current_user) if current_user else None
    if scoped_section_id is not None:
        # Unconditional, same reasoning as get_checksheet_list - narrows regardless of whatever
        # section_id filter param was also passed.
        base_query = base_query.filter(ChecksheetHeader.section_id == scoped_section_id)

    if scoped_section_id is not None:
        # "Dashboard statistics must display statistics only for the supervisor's section" - the
        # locomotive/equipment/technician/supervisor totals below are otherwise global counts,
        # unrelated to base_query's own checksheet-level filtering, so each needs its own
        # section-scoped query. Locomotive has no section_id column - a locomotive "belongs" to a
        # section if it has at least one checksheet against that section.
        total_locomotives = (
            db.query(Locomotive)
            .join(ChecksheetHeader, ChecksheetHeader.locomotive_id == Locomotive.id)
            .filter(ChecksheetHeader.section_id == scoped_section_id)
            .distinct()
            .count()
        )
        total_equipment = (
            db.query(Equipment)
            .join(SectionEquipmentMap, SectionEquipmentMap.equipment_id == Equipment.id)
            .filter(SectionEquipmentMap.section_id == scoped_section_id)
            .distinct()
            .count()
        )
        total_technicians = db.query(User).filter(User.role == "Technician", User.section_id == scoped_section_id).count()
        total_supervisors = db.query(User).filter(User.role == "Supervisor", User.section_id == scoped_section_id).count()
    else:
        total_locomotives = db.query(Locomotive).count()
        total_equipment = db.query(Equipment).count()
        total_technicians = db.query(User).filter(User.role == "Technician").count()
        total_supervisors = db.query(User).filter(User.role == "Supervisor").count()

    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    today_submitted = base_query.filter(
        ChecksheetHeader.submitted_at >= today_start,
        ChecksheetHeader.submitted_at < today_end
    ).count()

    pending_review = base_query.filter(
        ChecksheetHeader.status.in_([ChecksheetStatus.SUBMITTED.value, ChecksheetStatus.UNDER_REVIEW.value])
    ).count()
    signed = base_query.filter(ChecksheetHeader.status == ChecksheetStatus.APPROVED.value).count()
    rejected = base_query.filter(ChecksheetHeader.status == ChecksheetStatus.REJECTED.value).count()
    # No backend status exists for "needs correction" separately from REJECTED - always 0, matching
    # the same forward-compatible-but-currently-dead-slot precedent used on the Android app.
    needs_correction = 0

    status_rows = (
        base_query.with_entities(ChecksheetHeader.status, func.count(ChecksheetHeader.id))
        .group_by(ChecksheetHeader.status)
        .all()
    )
    status_distribution = {s.value: 0 for s in ChecksheetStatus}
    for status_value, count in status_rows:
        if status_value in status_distribution:
            status_distribution[status_value] = count

    section_rows = (
        base_query.with_entities(ChecksheetHeader.section_id, Section.name, func.count(ChecksheetHeader.id))
        .group_by(ChecksheetHeader.section_id, Section.name)
        .all()
    )
    by_section = [
        {"section_id": row_section_id, "section_name": section_name, "count": count}
        for row_section_id, section_name, count in section_rows
    ]

    equipment_rows = (
        base_query.with_entities(ChecksheetHeader.equipment_id, Equipment.equipment_name, func.count(ChecksheetHeader.id))
        .group_by(ChecksheetHeader.equipment_id, Equipment.equipment_name)
        .all()
    )
    by_equipment = [
        {"equipment_id": row_equipment_id, "equipment_name": equipment_name, "count": count}
        for row_equipment_id, equipment_name, count in equipment_rows
    ]

    # Daily trend is always the trailing 30 days regardless of date_from/date_to (it is a fixed,
    # named chart - "last 30 days" - not a dynamically resized range), but still respects every
    # other filter (section/equipment/technology/work_type/supervisor).
    trend_start = today_start - timedelta(days=29)
    trend_query = _build_analytics_base_query(
        db,
        section_id=section_id,
        equipment_id=equipment_id,
        locomotive_id=locomotive_id,
        locomotive_type=locomotive_type,
        technology=technology,
        work_type=work_type,
        supervisor_id=supervisor_id
    )
    if current_user and current_user.role == "Technician":
        trend_query = trend_query.filter(ChecksheetHeader.technician_mobile == current_user.mobile)
    if scoped_section_id is not None:
        trend_query = trend_query.filter(ChecksheetHeader.section_id == scoped_section_id)

    trend_rows = (
        trend_query.filter(
            ChecksheetHeader.submitted_at >= trend_start,
            ChecksheetHeader.submitted_at < today_end
        )
        .with_entities(func.date(ChecksheetHeader.submitted_at), func.count(ChecksheetHeader.id))
        .group_by(func.date(ChecksheetHeader.submitted_at))
        .all()
    )
    trend_map = {str(day): count for day, count in trend_rows}
    daily_trend = []
    for offset in range(30):
        day_str = (trend_start + timedelta(days=offset)).date().isoformat()
        daily_trend.append({"date": day_str, "count": trend_map.get(day_str, 0)})

    # Recent activity - one event per checksheet, picking whichever of submitted/approved/rejected
    # is the most recent non-null timestamp on that row (there is no dedicated audit-log table).
    candidates = (
        base_query.options(
            joinedload(ChecksheetHeader.submitted_by_user),
            joinedload(ChecksheetHeader.approved_by_user),
            joinedload(ChecksheetHeader.rejected_by_user)
        )
        .order_by(ChecksheetHeader.last_modified_at.desc().nullslast(), ChecksheetHeader.created_at.desc())
        .limit(50)
        .all()
    )

    def pick_event(header: ChecksheetHeader):
        options = [
            ("REJECTED", header.rejected_at, header.rejected_by_user),
            ("APPROVED", header.approved_at, header.approved_by_user),
            ("SUBMITTED", header.submitted_at, header.submitted_by_user),
        ]
        valid = [option for option in options if option[1] is not None]
        if valid:
            return max(valid, key=lambda option: option[1])
        return ("CREATED", header.created_at, None)

    activity_events = []
    for header in candidates:
        event, at, actor_user = pick_event(header)
        activity_events.append({
            "checksheet_id": header.id,
            "event": event,
            "at": at,
            "actor_name": actor_user.name if actor_user else None,
            "actor_role": actor_user.role if actor_user else None,
            "locomotive_number": header.locomotive.loco_number if header.locomotive else None,
            "equipment_name": header.equipment.equipment_name if header.equipment else None,
            "section_name": header.section.name if header.section else None
        })
    activity_events.sort(key=lambda event: event["at"], reverse=True)

    return {
        "total_locomotives": total_locomotives,
        "total_equipment": total_equipment,
        "total_technicians": total_technicians,
        "total_supervisors": total_supervisors,
        "today_submitted": today_submitted,
        "pending_review": pending_review,
        "signed": signed,
        "rejected": rejected,
        "needs_correction": needs_correction,
        "daily_trend": daily_trend,
        "by_section": by_section,
        "by_equipment": by_equipment,
        "status_distribution": status_distribution,
        "recent_activity": activity_events[:20]
    }


def _validate_required_values_for_template(db: Session, template_id: int, provided_values: list[dict]):
    # build a map of provided values by field_id
    provided_map = {v.get('field_id'): v.get('value') for v in provided_values}

    # fetch required active fields for the template
    required_fields = db.query(TemplateField).filter(TemplateField.template_id == template_id, TemplateField.required == True, TemplateField.is_active == True).all()
    missing = []
    for f in required_fields:
        # Hotfix: a GROUP field is a container, not an observation - it carries no value of its
        # own (see validate_checksheet_values's identical "groups never receive a result of their
        # own" skip, and TemplateField.breadcrumb_label's parent-walk, which both already treat
        # groups this way). A template that marks a group required=True (meaning "this checking
        # point must be filled in", i.e. its children) was being read here as "the group itself
        # must carry a non-empty value" - something no client ever sends for a group, since none
        # of them render an input for a container. That made submission permanently
        # unsubmittable for any such checksheet, no matter what the technician entered, because
        # the missing "value" could never be produced. Every other consumer of required/group
        # semantics already skips groups; this was the one place that didn't.
        if f.field_type == 'group':
            continue
        val = provided_map.get(f.id)
        # consider provided if not None and not empty string
        if val is None:
            missing.append(f.field_label or f.field_key)
            continue
        if isinstance(val, str) and val.strip() == "":
            missing.append(f.field_label or f.field_key)
            continue
        # number fields: allow numeric strings
        if f.field_type == 'number':
            try:
                if val == '':
                    missing.append(f.field_label or f.field_key)
                else:
                    float(val)
            except Exception:
                missing.append(f.field_label or f.field_key)
    return missing


def _ensure_equipment_technology_matches_locomotive(db: Session, equipment_id: int | None, locomotive_id: int) -> None:
    """Module 29.12: a checksheet's equipment must belong to the same Technology as its
    locomotive (e.g. a Conventional locomotive must never be paired with a 3-Phase-only
    equipment such as TMB). The Android app already only offers technology-compatible equipment
    in its dropdown, but the backend must reject a mismatch even if a request is crafted by hand -
    this is the single enforcement point for both create and update.

    Module 36: equipment_id is None for M6-HR (no equipment at all) - the query below then
    matches zero SectionEquipmentMap rows (equipment_id is NOT NULL there), so mapped_technologies
    is empty and this returns via the existing "nothing to enforce against" branch. The real
    technology check for M6-HR happens in _ensure_template_matches_selection instead, since there
    the check is against the template actually chosen rather than an equipment mapping that
    doesn't exist."""
    locomotive = db.query(Locomotive).filter(Locomotive.id == locomotive_id).first()
    if locomotive is None or locomotive.technology is None:
        return

    loco_technology = normalize_technology(locomotive.technology)
    mapped_technologies = {
        normalize_technology(technology)
        for (technology,) in db.query(SectionEquipmentMap.technology)
        .filter(SectionEquipmentMap.equipment_id == equipment_id, SectionEquipmentMap.is_active == True)
        .distinct()
        .all()
    }
    if not mapped_technologies:
        # Equipment with no recorded technology mapping at all (e.g. legacy data) - nothing to
        # enforce against, so it is not rejected.
        return

    if loco_technology not in mapped_technologies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected equipment's technology does not match the locomotive's technology.",
        )

    # Module 40: Technology alone isn't enough for sections (M4-HR) where the same equipment_name
    # exists as separate equipment records per Locomotive Model (WAG9HC vs WAP-7, both 3-Phase) -
    # the Android/Dashboard equipment list is already filtered by locomotive_id (see
    # equipment_service.get_all_equipment), but a hand-crafted request must be rejected here too,
    # the same defense-in-depth this function already applies to technology.
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if equipment is not None and not equipment_code_matches_locomotive_model(db, equipment, locomotive.loco_model):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected equipment does not match the locomotive's model.",
        )


def _ensure_template_matches_selection(
    db: Session, template_id: int, equipment_id: int | None, maintenance_type: str | None,
    section_id: int | None = None, locomotive_id: int | None = None,
) -> None:
    """Module 32: mirrors _ensure_equipment_technology_matches_locomotive's enforcement pattern.
    Some equipment (e.g. Traction Motor) has more than one active template for the same
    equipment+technology, disambiguated only by maintenance_type (GC vs Overhaul) - the Android
    app already only lets a Technician resolve one specific template_id via that selection, but the
    backend must reject a checksheet whose template_id doesn't actually belong to its own
    equipment_id, or whose maintenance_type doesn't match the template actually chosen, even if a
    request is crafted by hand.

    Module 36: a template with equipment_id NULL is either a section-wide common page (Module
    29.5, e.g. M35-Aux's shared front page - never submitted against on its own) or a fully
    equipment-less section's entire checksheet (M6-HR - submitted against directly). The two are
    indistinguishable by equipment_id alone, but only the latter is ever the target of a real
    create_checksheet/update_checksheet call, so the check below (section_id + locomotive
    technology match) only fires when the caller actually supplied those - the M35-Aux common-page
    template is never itself a checksheet's template_id, so it never reaches this call at all in
    practice."""
    template = db.query(ChecksheetTemplate).filter(ChecksheetTemplate.id == template_id).first()
    if template is None:
        return

    if template.equipment_id is None:
        if section_id is not None and template.section_id != section_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected template does not belong to the selected section.",
            )
        if locomotive_id is not None and template.technology is not None:
            locomotive = db.query(Locomotive).filter(Locomotive.id == locomotive_id).first()
            if locomotive is not None and locomotive.technology is not None:
                if normalize_technology(locomotive.technology) != normalize_technology(template.technology):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Selected template does not match the locomotive's technology.",
                    )
        return

    if template.equipment_id != equipment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected template does not belong to the selected equipment.",
        )

    if template.maintenance_type is not None and template.maintenance_type != maintenance_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected template does not match the selected maintenance type.",
        )


def authorize_checksheet_access(header: ChecksheetHeader, current_user: User) -> None:
    """Shared access check reused by the PDF generate/download/preview endpoints (previously each
    only checked the Technician case, leaving Supervisors able to fetch any section's PDF) -
    matches the same rule already enforced in get_checksheet_detail/update_checksheet/
    delete_checksheet: a Technician may only access their own checksheets, a Supervisor only
    their assigned section's, and Admin is unrestricted."""
    if current_user.role == "Technician" and header.technician_mobile != current_user.mobile:
        security_logger.warning(
            "Permission denied: checksheet belongs to a different technician",
            extra={"action": "PERMISSION_DENIED", "success": False, "checksheet_id": header.id},
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    scoped_section_id = supervisor_section_id(current_user)
    if scoped_section_id is not None and header.section_id != scoped_section_id:
        security_logger.warning(
            "Permission denied: checksheet outside supervisor's assigned section",
            extra={"action": "PERMISSION_DENIED", "success": False, "checksheet_id": header.id, "checksheet_section_id": header.section_id},
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


def get_checksheet_detail(db: Session, checksheet_id: int, current_user: User | None = None):
    header = (
        db.query(ChecksheetHeader)
        .options(
            joinedload(ChecksheetHeader.template),
            joinedload(ChecksheetHeader.technician),
            joinedload(ChecksheetHeader.locomotive),
            joinedload(ChecksheetHeader.equipment),
            joinedload(ChecksheetHeader.section),
            # Module 39: LEFT OUTER JOIN, same reasoning as get_checksheet_list above - a
            # pre-Module-39 approved checksheet has no digital_signatures row and must still load.
            joinedload(ChecksheetHeader.digital_signature),
            joinedload(ChecksheetHeader.values).joinedload(ChecksheetValue.field)
        )
        .filter(ChecksheetHeader.id == checksheet_id)
        .first()
    )
    if not header:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checksheet not found")

    if current_user and current_user.role == "Technician" and header.technician_mobile != current_user.mobile:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    scoped_section_id = supervisor_section_id(current_user) if current_user else None
    if scoped_section_id is not None and header.section_id != scoped_section_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return _serialize_detail(header)


def create_checksheet(db: Session, checksheet: ChecksheetHeaderCreate, current_user: User):
    # Explicit existence checks for the 3 required foreign keys - without these, a bad ID (e.g. a
    # stale/typo'd value from a client) would sail through every check above (several of which
    # intentionally no-op when the referenced row is missing, for other reasons) and only fail at
    # db.flush() with a raw, unhandled ForeignKeyViolation -> 500.
    if not db.query(Locomotive.id).filter(Locomotive.id == checksheet.locomotive_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Locomotive not found")
    if not db.query(Section.id).filter(Section.id == checksheet.section_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Section not found")
    if not db.query(ChecksheetTemplate.id).filter(ChecksheetTemplate.id == checksheet.template_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Template not found")

    _ensure_equipment_technology_matches_locomotive(db, checksheet.equipment_id, checksheet.locomotive_id)
    _ensure_template_matches_selection(
        db, checksheet.template_id, checksheet.equipment_id, checksheet.maintenance_type,
        section_id=checksheet.section_id, locomotive_id=checksheet.locomotive_id,
    )

    # If attempting to create and submit immediately, validate required business fields
    if checksheet.status == ChecksheetStatus.SUBMITTED:
        # ensure work_type present
        if not checksheet.work_type or (isinstance(checksheet.work_type, str) and not checksheet.work_type.strip()):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="work_type is required to submit a checksheet")
        # validate required template fields are provided
        missing = _validate_required_values_for_template(db, checksheet.template_id, [v.dict() for v in checksheet.values])
        if missing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing required field values: {', '.join(missing)}")

    header = ChecksheetHeader(
        locomotive_id=checksheet.locomotive_id,
        section_id=checksheet.section_id,
        equipment_id=checksheet.equipment_id,
        template_id=checksheet.template_id,
        technician_mobile=current_user.mobile,
        work_type=checksheet.work_type,
        traction_motor_number=checksheet.traction_motor_number,
        maintenance_type=checksheet.maintenance_type,
        status=checksheet.status.value if checksheet.status else ChecksheetStatus.DRAFT.value,
        submitted_at=datetime.now(timezone.utc) if checksheet.status == ChecksheetStatus.SUBMITTED else None,
        submitted_by=current_user.id if checksheet.status == ChecksheetStatus.SUBMITTED else None,
        last_modified_at=datetime.now(timezone.utc),
        last_modified_by=current_user.id
    )

    db.add(header)
    db.flush()

    for value in checksheet.values:
        field = ChecksheetValue(
            checksheet_id=header.id,
            field_id=value.field_id,
            field_value=value.value
        )
        db.add(field)

    db.commit()
    db.refresh(header)

    return _serialize_detail(
        db.query(ChecksheetHeader)
        .options(joinedload(ChecksheetHeader.template), joinedload(ChecksheetHeader.values).joinedload(ChecksheetValue.field))
        .filter(ChecksheetHeader.id == header.id)
        .first()
    )


def update_checksheet(db: Session, checksheet_id: int, payload: ChecksheetHeaderUpdate, current_user: User):
    header = db.query(ChecksheetHeader).filter(ChecksheetHeader.id == checksheet_id).first()
    if not header:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checksheet not found")

    if header.status != ChecksheetStatus.DRAFT.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft checksheets can be updated")

    if current_user.role == "Technician" and header.technician_mobile != current_user.mobile:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    scoped_section_id = supervisor_section_id(current_user)
    if scoped_section_id is not None and header.section_id != scoped_section_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    final_locomotive_id = payload.locomotive_id if payload.locomotive_id is not None else header.locomotive_id
    final_equipment_id = payload.equipment_id if payload.equipment_id is not None else header.equipment_id
    final_section_id = payload.section_id if payload.section_id is not None else header.section_id
    final_template_id = payload.template_id if payload.template_id is not None else header.template_id
    final_maintenance_type = payload.maintenance_type if payload.maintenance_type is not None else header.maintenance_type
    _ensure_equipment_technology_matches_locomotive(db, final_equipment_id, final_locomotive_id)
    _ensure_template_matches_selection(
        db, final_template_id, final_equipment_id, final_maintenance_type,
        section_id=final_section_id, locomotive_id=final_locomotive_id,
    )

    if payload.locomotive_id is not None:
        header.locomotive_id = payload.locomotive_id
    if payload.section_id is not None:
        header.section_id = payload.section_id
    if payload.equipment_id is not None:
        header.equipment_id = payload.equipment_id
    if payload.template_id is not None:
        header.template_id = payload.template_id
    if payload.technician_mobile is not None:
        header.technician_mobile = payload.technician_mobile
    if payload.work_type is not None:
        header.work_type = payload.work_type
    if payload.traction_motor_number is not None:
        header.traction_motor_number = payload.traction_motor_number
    if payload.maintenance_type is not None:
        header.maintenance_type = payload.maintenance_type

    if payload.values is not None:
        db.query(ChecksheetValue).filter(ChecksheetValue.checksheet_id == header.id).delete()
        for value in payload.values:
            field = ChecksheetValue(
                checksheet_id=header.id,
                field_id=value.field_id,
                field_value=value.value
            )
            db.add(field)

    header.last_modified_at = datetime.now(timezone.utc)
    header.last_modified_by = current_user.id

    db.commit()
    db.refresh(header)

    return _serialize_detail(
        db.query(ChecksheetHeader)
        .options(joinedload(ChecksheetHeader.template), joinedload(ChecksheetHeader.values).joinedload(ChecksheetValue.field))
        .filter(ChecksheetHeader.id == header.id)
        .first()
    )


def delete_checksheet(db: Session, checksheet_id: int, current_user: User):
    header = db.query(ChecksheetHeader).filter(ChecksheetHeader.id == checksheet_id).first()
    if not header:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checksheet not found")

    # Admins may also delete "pending" checksheets (submitted or under review, i.e. not yet
    # finalized) - everyone else keeps the original draft-only restriction. Approved/rejected
    # checksheets are never deletable by anyone, regardless of role.
    if current_user.role == "Admin":
        deletable_statuses = [
            ChecksheetStatus.DRAFT.value,
            ChecksheetStatus.SUBMITTED.value,
            ChecksheetStatus.UNDER_REVIEW.value
        ]
        error_detail = "Only draft, submitted, or under-review checksheets can be deleted"
    else:
        deletable_statuses = [ChecksheetStatus.DRAFT.value]
        error_detail = "Only drafts can be deleted"

    if header.status not in deletable_statuses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_detail)

    if current_user.role == "Technician" and header.technician_mobile != current_user.mobile:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    scoped_section_id = supervisor_section_id(current_user)
    if scoped_section_id is not None and header.section_id != scoped_section_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    db.delete(header)
    db.commit()
    return {"message": "Checksheet deleted successfully"}


def change_checksheet_status(db: Session, checksheet_id: int, payload: ChecksheetStatusUpdate, current_user: User):
    header = db.query(ChecksheetHeader).filter(ChecksheetHeader.id == checksheet_id).first()
    if not header:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checksheet not found")

    scoped_section_id = supervisor_section_id(current_user)
    if scoped_section_id is not None and header.section_id != scoped_section_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    current_status = ChecksheetStatus(header.status)
    next_status = payload.status

    if next_status == current_status:
        return _serialize_detail(
            db.query(ChecksheetHeader)
            .options(joinedload(ChecksheetHeader.template), joinedload(ChecksheetHeader.values).joinedload(ChecksheetValue.field))
            .filter(ChecksheetHeader.id == header.id)
            .first()
        )

    if next_status not in VALID_STATUS_TRANSITIONS[current_status]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status transition from {current_status} to {next_status}")

    if next_status == ChecksheetStatus.SUBMITTED:
        if current_user.role not in ["Technician", "Admin"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only technicians or admins can submit drafts")
        if current_status != ChecksheetStatus.DRAFT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft checksheets can be submitted")
        # Validate business rules before submission
        if not header.work_type or (isinstance(header.work_type, str) and not header.work_type.strip()):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="work_type is required to submit a checksheet")
        # validate required template fields
        provided_values = [ { 'field_id': v.field_id, 'value': v.field_value } for v in header.values ]
        missing = _validate_required_values_for_template(db, header.template_id, provided_values)
        if missing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing required field values: {', '.join(missing)}")

        header.status = ChecksheetStatus.SUBMITTED.value
        header.submitted_at = datetime.now(timezone.utc)
        header.submitted_by = current_user.id

    elif next_status == ChecksheetStatus.UNDER_REVIEW:
        if current_user.role not in ["Supervisor", "Admin"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only supervisors or admins can move checksheets to under review")
        header.status = ChecksheetStatus.UNDER_REVIEW.value

    elif next_status == ChecksheetStatus.APPROVED:
        # Module 39: approval now requires a Digital Signature - this generic status endpoint no
        # longer performs it directly. The Dashboard's "Approve & Sign" action calls the
        # signature-v2 prepare/complete endpoints instead (see digital_signature_v2_service),
        # which perform the same completeness checks plus the signing workflow before setting this
        # exact status. REJECTED below is untouched - rejection never requires a signature.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval requires a Digital Signature. Use POST /checksheet/{id}/approve-and-sign.",
        )

    elif next_status == ChecksheetStatus.REJECTED:
        if current_user.role not in ["Supervisor", "Admin"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only supervisors or admins can reject checksheets")
        if not payload.rejection_reason or not payload.rejection_reason.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rejection reason is required")
        header.status = ChecksheetStatus.REJECTED.value
        header.rejected_at = datetime.now(timezone.utc)
        header.rejected_by = current_user.id
        header.rejection_reason = payload.rejection_reason.strip()
        if header.technician:
            create_notification(
                db,
                user_id=header.technician.id,
                title="Checksheet Rejected",
                message=f"Your checksheet #{header.id} ({header.work_type or 'checksheet'}) was rejected by {current_user.name}: {header.rejection_reason}",
                notification_type="CHECKSHEET_REJECTED",
                checksheet_id=header.id,
            )

    header.last_modified_at = datetime.now(timezone.utc)
    header.last_modified_by = current_user.id

    db.commit()
    db.refresh(header)

    return _serialize_detail(
        db.query(ChecksheetHeader)
        .options(joinedload(ChecksheetHeader.template), joinedload(ChecksheetHeader.values).joinedload(ChecksheetValue.field))
        .filter(ChecksheetHeader.id == header.id)
        .first()
    )
