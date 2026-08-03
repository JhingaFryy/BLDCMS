"""Module 44: backup-run logging.

Two independent outputs, following the same pattern app.admin_cli.audit already established for
its own audit log (a dedicated file, written directly, entirely separate from - and not routed
through - app.core.logging's central configure_logging()):

1. `logs/backup_system.log` - a dedicated, append-only JSON-lines file, one line per event
   (start/completed/failed/retention-applied), written directly rather than via the shared
   logging config, so this module has zero coupling to (and never has to modify)
   app/core/logging.py.
2. The existing `activity_logs` DB table, via activity_log_service.log_activity, using new
   BACKUP_* Action constants - so completed/failed backup runs also show up in the same Activity
   Timeline the rest of the application already uses. Best-effort: a database problem must never
   crash a backup run that otherwise succeeded, so this call is always wrapped.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional

from app.core.logging import LOG_DIR

BACKUP_LOG_PATH = LOG_DIR / "backup_system.log"


def _write_log_line(event: dict[str, Any]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(BACKUP_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, default=str) + "\n")


def log_event(tier: str, event: str, **fields: Any) -> None:
    """Writes one structured line to backup_system.log. `event` is one of
    "started"/"completed"/"failed"/"retention_applied"/"verification"."""
    _write_log_line({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tier": tier,
        "event": event,
        **fields,
    })


def log_activity_best_effort(action: str, *, description: str, metadata: Optional[dict] = None) -> None:
    """Mirrors app.admin_cli's own activity-log integration: a system-triggered event with no
    associated user (user_id stays null), best-effort per log_activity's own contract (never
    raises) - a database problem here must never abort or fail a backup run."""
    try:
        from app.database.database import SessionLocal
        from app.services.activity_log_service import log_activity

        db = SessionLocal()
        try:
            log_activity(
                db,
                action,
                description=description,
                metadata=metadata,
            )
        finally:
            db.close()
    except Exception:
        # Deliberately swallowed - see docstring. The JSON-lines file above is the log of record
        # for backup operations and is written independently of this call succeeding.
        pass
