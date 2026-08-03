from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User


def create_notification(
    db: Session,
    *,
    user_id: int,
    title: str,
    message: str,
    notification_type: str = "SYSTEM",
    checksheet_id: int | None = None,
) -> Notification:
    """Generic, reusable notification-creation entry point - the model/schema/read APIs (this
    module's get_notifications/get_unread_count/etc.) and the Android UI (NotificationType.kt's
    CHECKSHEET_SUBMITTED/CHECKSHEET_SIGNED/CHECKSHEET_REJECTED/SYSTEM cases) already existed, but
    nothing in the backend ever actually inserted a Notification row - this was the missing write
    path. Callers commit as part of their own transaction (e.g. alongside a status change) rather
    than this function committing independently, so a notification never persists without its
    triggering change.
    """
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notification_type,
        checksheet_id=checksheet_id,
    )
    db.add(notification)
    db.flush()
    return notification


def _to_naive_utc(dt: datetime) -> datetime:
    """The notifications.created_at column is a naive TIMESTAMP storing UTC (see
    app/models/notification.py). A tz-aware `after` query param must be normalized to the same
    naive-UTC form before comparison, or an otherwise-correct client-supplied timestamp would
    compare incorrectly against every row."""
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def get_notifications(db: Session, current_user: User, skip: int = 0, limit: int = 50):
    query = db.query(Notification).filter(Notification.user_id == current_user.id)

    total = query.count()
    unread_count = query.filter(Notification.is_read == False).count()  # noqa: E712
    items = (
        query.order_by(Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {"items": items, "total": total, "unread_count": unread_count}


def mark_notification_read(db: Session, notification_id: int, current_user: User):
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == current_user.id)
        .first()
    )

    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_read(db: Session, current_user: User):
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False  # noqa: E712
    ).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read"}


def get_unread_count(db: Session, current_user: User) -> int:
    """Lightweight poll target for the Android badge/sync loop - a single COUNT(*), no row
    payload, so it's cheap enough to call on every sync tick."""
    return (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id, Notification.is_read == False)  # noqa: E712
        .count()
    )


def get_notifications_since(db: Session, current_user: User, after: datetime, limit: int = 50):
    """Incremental sync target: only rows created after `after`, so the Android poller never
    re-downloads the full history on each tick - just whatever is genuinely new."""
    after_naive = _to_naive_utc(after)
    return (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.id,
            Notification.created_at > after_naive
        )
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )
