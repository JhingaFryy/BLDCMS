from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session, contains_eager, joinedload

from app.core.logging import get_logger
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.security.section_scope import supervisor_section_id

logger = get_logger("app.activity")


class Action:
    """Canonical activity type strings (Module 29). Kept as a single source of truth so every
    log_activity() call site and the /activity-logs read path agree on exact spelling."""
    USER_LOGIN = "USER_LOGIN"
    USER_LOGOUT = "USER_LOGOUT"
    OTP_GENERATED = "OTP_GENERATED"
    OTP_VERIFIED = "OTP_VERIFIED"
    CHECKSHEET_CREATED = "CHECKSHEET_CREATED"
    CHECKSHEET_UPDATED = "CHECKSHEET_UPDATED"
    CHECKSHEET_SUBMITTED = "CHECKSHEET_SUBMITTED"
    CHECKSHEET_APPROVED = "CHECKSHEET_APPROVED"
    CHECKSHEET_REJECTED = "CHECKSHEET_REJECTED"
    CHECKSHEET_PDF_GENERATED = "CHECKSHEET_PDF_GENERATED"
    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"
    SECTION_CREATED = "SECTION_CREATED"
    EQUIPMENT_ADDED = "EQUIPMENT_ADDED"
    EQUIPMENT_UPDATED = "EQUIPMENT_UPDATED"
    TEMPLATE_CREATED = "TEMPLATE_CREATED"
    TEMPLATE_UPDATED = "TEMPLATE_UPDATED"
    TEMPLATE_DELETED = "TEMPLATE_DELETED"
    CHECKSHEET_DELETED = "CHECKSHEET_DELETED"
    LOCOMOTIVE_ADDED = "LOCOMOTIVE_ADDED"
    LOCOMOTIVE_UPDATED = "LOCOMOTIVE_UPDATED"
    LOCOMOTIVE_REMOVED = "LOCOMOTIVE_REMOVED"
    NOTIFICATION_SENT = "NOTIFICATION_SENT"
    SYSTEM_SETTING_CHANGED = "SYSTEM_SETTING_CHANGED"

    # Module 39: Digital Signature (DSC) audit trail - one entry per lifecycle stage of a single
    # approve-and-sign attempt, in addition to (not instead of) the existing CHECKSHEET_APPROVED
    # entry once the attempt succeeds, so the Activity Timeline keeps showing "Checksheet Approved"
    # exactly as before while also carrying the new granular signing trail.
    SIGNATURE_INITIATED = "SIGNATURE_INITIATED"
    CERTIFICATE_VERIFIED = "CERTIFICATE_VERIFIED"
    SIGNATURE_SUCCESS = "SIGNATURE_SUCCESS"
    PDF_SIGNED = "PDF_SIGNED"
    SIGNATURE_FAILED = "SIGNATURE_FAILED"
    INVALID_CERTIFICATE = "INVALID_CERTIFICATE"
    EXPIRED_CERTIFICATE = "EXPIRED_CERTIFICATE"
    PIN_FAILURE = "PIN_FAILURE"
    TOKEN_DISCONNECTED = "TOKEN_DISCONNECTED"

    # Module 44: System Administration CLI - every privileged CLI action also writes one of these
    # into the normal activity_logs table (in addition to, not instead of, the CLI's own separate
    # audit log file - see app/admin_cli/audit.py) so admin actions appear in the same
    # Activity Timeline as everything else, correlated by entity_type="device"/"session".
    ADMIN_CLI_DEVICES_LISTED = "ADMIN_CLI_DEVICES_LISTED"
    ADMIN_CLI_DEVICE_VIEWED = "ADMIN_CLI_DEVICE_VIEWED"
    ADMIN_CLI_SESSIONS_LISTED = "ADMIN_CLI_SESSIONS_LISTED"
    ADMIN_CLI_SESSION_REVOKED = "ADMIN_CLI_SESSION_REVOKED"
    ADMIN_CLI_FORCE_LOGOUT = "ADMIN_CLI_FORCE_LOGOUT"
    ADMIN_CLI_APP_DATA_CLEAR_REQUESTED = "ADMIN_CLI_APP_DATA_CLEAR_REQUESTED"
    ADMIN_CLI_DIAGNOSTIC_BUNDLE_CREATED = "ADMIN_CLI_DIAGNOSTIC_BUNDLE_CREATED"
    ADMIN_CLI_HEALTH_CHECKED = "ADMIN_CLI_HEALTH_CHECKED"
    ADMIN_CLI_ACCESS_DENIED = "ADMIN_CLI_ACCESS_DENIED"

    # Module 42: Production Hardening - closing out audit gaps on previously-unauthenticated
    # mutation endpoints, and new admin_cli backup/archive/export utilities.
    TEMPLATE_FIELD_ADDED = "TEMPLATE_FIELD_ADDED"
    TEMPLATE_FIELD_UPDATED = "TEMPLATE_FIELD_UPDATED"
    TEMPLATE_FIELD_REMOVED = "TEMPLATE_FIELD_REMOVED"
    SECTION_EQUIPMENT_MAPPING_ADDED = "SECTION_EQUIPMENT_MAPPING_ADDED"
    SECTION_EQUIPMENT_MAPPING_REMOVED = "SECTION_EQUIPMENT_MAPPING_REMOVED"
    EQUIPMENT_REMOVED = "EQUIPMENT_REMOVED"
    SECTION_UPDATED = "SECTION_UPDATED"
    SECTION_REMOVED = "SECTION_REMOVED"
    ADMIN_CLI_BACKUP_CREATED = "ADMIN_CLI_BACKUP_CREATED"
    ADMIN_CLI_BACKUP_RESTORED = "ADMIN_CLI_BACKUP_RESTORED"
    ADMIN_CLI_LOGS_ARCHIVED = "ADMIN_CLI_LOGS_ARCHIVED"
    ADMIN_CLI_PDFS_ARCHIVED = "ADMIN_CLI_PDFS_ARCHIVED"
    ADMIN_CLI_CHECKSHEETS_EXPORTED = "ADMIN_CLI_CHECKSHEETS_EXPORTED"

    # Module 44.1: Automated Backup System (HDD) - one pair of entries per scheduled backup run
    # (daily/weekly/monthly), written by app.backup_system, entirely separate from the
    # ADMIN_CLI_BACKUP_* entries above (those are on-demand, SSD-local backups triggered manually
    # via bldcms-admin; these are the scheduled, HDD-destination, retention-managed runs).
    BACKUP_DAILY_COMPLETED = "BACKUP_DAILY_COMPLETED"
    BACKUP_DAILY_FAILED = "BACKUP_DAILY_FAILED"
    BACKUP_WEEKLY_COMPLETED = "BACKUP_WEEKLY_COMPLETED"
    BACKUP_WEEKLY_FAILED = "BACKUP_WEEKLY_FAILED"
    BACKUP_MONTHLY_COMPLETED = "BACKUP_MONTHLY_COMPLETED"
    BACKUP_MONTHLY_FAILED = "BACKUP_MONTHLY_FAILED"
    BACKUP_RETENTION_APPLIED = "BACKUP_RETENTION_APPLIED"


ALL_ACTIONS = [
    Action.USER_LOGIN,
    Action.USER_LOGOUT,
    Action.OTP_GENERATED,
    Action.OTP_VERIFIED,
    Action.CHECKSHEET_CREATED,
    Action.CHECKSHEET_UPDATED,
    Action.CHECKSHEET_SUBMITTED,
    Action.CHECKSHEET_APPROVED,
    Action.CHECKSHEET_REJECTED,
    Action.CHECKSHEET_PDF_GENERATED,
    Action.USER_CREATED,
    Action.USER_UPDATED,
    Action.USER_DELETED,
    Action.SECTION_CREATED,
    Action.EQUIPMENT_ADDED,
    Action.EQUIPMENT_UPDATED,
    Action.TEMPLATE_CREATED,
    Action.TEMPLATE_UPDATED,
    Action.TEMPLATE_DELETED,
    Action.CHECKSHEET_DELETED,
    Action.LOCOMOTIVE_ADDED,
    Action.LOCOMOTIVE_UPDATED,
    Action.LOCOMOTIVE_REMOVED,
    Action.NOTIFICATION_SENT,
    Action.SYSTEM_SETTING_CHANGED,
    Action.SIGNATURE_INITIATED,
    Action.CERTIFICATE_VERIFIED,
    Action.SIGNATURE_SUCCESS,
    Action.PDF_SIGNED,
    Action.SIGNATURE_FAILED,
    Action.INVALID_CERTIFICATE,
    Action.EXPIRED_CERTIFICATE,
    Action.PIN_FAILURE,
    Action.TOKEN_DISCONNECTED,
    Action.ADMIN_CLI_DEVICES_LISTED,
    Action.ADMIN_CLI_DEVICE_VIEWED,
    Action.ADMIN_CLI_SESSIONS_LISTED,
    Action.ADMIN_CLI_SESSION_REVOKED,
    Action.ADMIN_CLI_FORCE_LOGOUT,
    Action.ADMIN_CLI_APP_DATA_CLEAR_REQUESTED,
    Action.ADMIN_CLI_DIAGNOSTIC_BUNDLE_CREATED,
    Action.ADMIN_CLI_HEALTH_CHECKED,
    Action.ADMIN_CLI_ACCESS_DENIED,
    Action.TEMPLATE_FIELD_ADDED,
    Action.TEMPLATE_FIELD_UPDATED,
    Action.TEMPLATE_FIELD_REMOVED,
    Action.SECTION_EQUIPMENT_MAPPING_ADDED,
    Action.SECTION_EQUIPMENT_MAPPING_REMOVED,
    Action.EQUIPMENT_REMOVED,
    Action.SECTION_UPDATED,
    Action.SECTION_REMOVED,
    Action.ADMIN_CLI_BACKUP_CREATED,
    Action.ADMIN_CLI_BACKUP_RESTORED,
    Action.ADMIN_CLI_LOGS_ARCHIVED,
    Action.ADMIN_CLI_PDFS_ARCHIVED,
    Action.ADMIN_CLI_CHECKSHEETS_EXPORTED,
    Action.BACKUP_DAILY_COMPLETED,
    Action.BACKUP_DAILY_FAILED,
    Action.BACKUP_WEEKLY_COMPLETED,
    Action.BACKUP_WEEKLY_FAILED,
    Action.BACKUP_MONTHLY_COMPLETED,
    Action.BACKUP_MONTHLY_FAILED,
    Action.BACKUP_RETENTION_APPLIED,
]


def log_activity(
    db: Session,
    action: str,
    *,
    user: Optional[User] = None,
    employee_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    section_id: Optional[int] = None,
    description: Optional[str] = None,
    old_value: Optional[Dict[str, Any]] = None,
    new_value: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    duration_ms: Optional[float] = None,
) -> None:
    """Best-effort activity log write - NEVER raises, so a logging failure can never break the
    action it records. Callers must invoke this AFTER their own primary db.commit() has already
    succeeded, never before, so a logging failure can't affect real work.

    `user` and `employee_id` are both optional and mutually redundant - pass whichever is already
    on hand at the call site (some hooks, like login/OTP, run before a User object is otherwise
    needed). If neither resolves to a real user, the log row is still written with a null user_id
    rather than being dropped, since the fact an action happened is still worth recording.
    """
    try:
        resolved_user = user
        if resolved_user is None and employee_id:
            resolved_user = db.query(User).filter(User.employee_id == employee_id).first()

        resolved_section_id = section_id
        if resolved_section_id is None and resolved_user is not None:
            resolved_section_id = resolved_user.section_id

        # Module 42: duration_ms is folded into the existing metadata column (DB-queryable, e.g.
        # for PDF-generation/signature-timing stats on the System Health page) rather than adding
        # a dedicated column - it's optional, sparse, and only a handful of call sites set it.
        resolved_metadata = metadata
        if duration_ms is not None:
            resolved_metadata = {**(metadata or {}), "duration_ms": duration_ms}

        log = ActivityLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=resolved_user.id if resolved_user else None,
            section_id=resolved_section_id,
            description=description,
            old_value=old_value,
            new_value=new_value,
            activity_metadata=resolved_metadata,
        )
        db.add(log)
        db.commit()

        # In addition to the activity_logs DB row above (which powers the Dashboard's Activity
        # Timeline and is left completely unchanged), every activity is also written to
        # activity.log as a structured JSON entry - this is what makes checksheet
        # create/update/submit/approve/reject, the full digital-signature lifecycle (both DSC v1
        # and v2, which already funnel every stage through this same function), and every other
        # log_activity() call site across the app grep/tail-able without any of those call sites
        # needing to change.
        extra = {"action": action, "success": True, "entity_type": entity_type, "entity_id": entity_id}
        # Only set employee_id/user_name explicitly when this call resolved a *specific* subject
        # user - otherwise leave them out of extra entirely so RequestContextFilter's ambient
        # default (the currently-authenticated caller, if any) applies instead of a bare None.
        resolved_employee_id = resolved_user.employee_id if resolved_user else employee_id
        if resolved_employee_id:
            extra["employee_id"] = resolved_employee_id
        if resolved_user:
            extra["user_name"] = resolved_user.name
        if duration_ms is not None:
            extra["duration_ms"] = duration_ms
        logger.info(description or action, extra=extra)
    except Exception:  # noqa: BLE001 - must never propagate into the caller's own success path
        db.rollback()
        logger.exception("Failed to write activity log for action=%s", action)


def _serialize(log: ActivityLog) -> dict:
    return {
        "id": log.id,
        "action": log.action,
        "entity_type": log.entity_type,
        "entity_id": log.entity_id,
        "description": log.description,
        "user_id": log.user_id,
        "user_name": log.user.name if log.user else None,
        "employee_id": log.user.employee_id if log.user else None,
        "role": log.user.role if log.user else None,
        "section_id": log.section_id,
        "section_name": log.section.name if log.section else None,
        "old_value": log.old_value,
        "new_value": log.new_value,
        "activity_metadata": log.activity_metadata,
        "created_at": log.created_at,
    }


def get_activities(
    db: Session,
    current_user: User,
    skip: int = 0,
    limit: int = 25,
    search: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    section_id: Optional[int] = None,
    user_id: Optional[int] = None,
    role: Optional[str] = None,
    action: Optional[str] = None,
) -> dict:
    # Outer join - activity rows with no resolvable user (e.g. a login attempt for an unknown
    # employee_id) must still show up, not be silently dropped by an inner join.
    query = (
        db.query(ActivityLog)
        .outerjoin(User, ActivityLog.user_id == User.id)
        .options(contains_eager(ActivityLog.user), joinedload(ActivityLog.section))
    )

    scoped_section_id = supervisor_section_id(current_user)
    if scoped_section_id is not None:
        query = query.filter(ActivityLog.section_id == scoped_section_id)

    if section_id is not None:
        query = query.filter(ActivityLog.section_id == section_id)
    if user_id is not None:
        query = query.filter(ActivityLog.user_id == user_id)
    if role is not None:
        query = query.filter(User.role == role)
    if action is not None:
        query = query.filter(ActivityLog.action == action)
    if date_from is not None:
        query = query.filter(ActivityLog.created_at >= date_from)
    if date_to is not None:
        query = query.filter(ActivityLog.created_at <= date_to)

    if search:
        term = f"%{search.strip()}%"
        conditions = [
            ActivityLog.description.ilike(term),
            User.name.ilike(term),
            User.employee_id.ilike(term),
        ]
        stripped = search.strip()
        if stripped.isdigit():
            conditions.append(ActivityLog.entity_id == int(stripped))
        query = query.filter(or_(*conditions))

    total = query.count()
    items = (
        query.order_by(ActivityLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {"items": [_serialize(item) for item in items], "total": total}
