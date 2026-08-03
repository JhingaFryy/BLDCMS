"""
Module 44: System Administration CLI - audit logging.

Every CLI command invocation writes exactly one audit entry, in two places:

1. A dedicated append-only JSON-lines file (`logs/admin_cli_audit.log`), completely separate
   from application.log/error.log/auth.log/etc. - this is the file requested by the module spec
   ("audit logs must be separate from normal application logs") and is available even when the
   database is unreachable (e.g. auditing a failed "health" check caused by the DB being down).
2. The existing `activity_logs` DB table via `activity_log_service.log_activity`, using the new
   ADMIN_CLI_* Action constants, so privileged actions also show up in the same Activity Timeline
   as everything else the application already audits (best-effort, per that function's own
   contract - never allowed to raise).

Every entry captures exactly the fields the module spec requires: Linux username, timestamp,
source host, command executed, parameters (sensitive values redacted), result, and error details.
"""
from __future__ import annotations

import json
import os
import stat
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from app.core.logging import LOG_DIR

AUDIT_LOG_PATH = LOG_DIR / "admin_cli_audit.log"

# Module 44: parameter names that must never appear in an audit entry even if a future command
# happens to accept one of these - defense in depth, not currently used by any command below,
# but new commands are easy to add and this guards against a careless addition leaking a secret
# into a log file.
_SENSITIVE_PARAM_NAMES = {"password", "otp", "token", "refresh_token", "secret", "pin"}


@dataclass
class AuditEntry:
    linux_username: str
    command: str
    parameters: dict[str, Any] = field(default_factory=dict)
    source_host: Optional[str] = None
    result: str = "Success"  # "Success" or "Failure"
    error: Optional[str] = None

    def redacted_parameters(self) -> dict[str, Any]:
        return {
            key: ("<redacted>" if key.lower() in _SENSITIVE_PARAM_NAMES else value)
            for key, value in self.parameters.items()
        }

    def to_json_line(self) -> str:
        return json.dumps(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "linux_username": self.linux_username,
                "source_host": self.source_host,
                "command": self.command,
                "parameters": self.redacted_parameters(),
                "result": self.result,
                "error": self.error,
            },
            default=str,
        )


def _ensure_audit_log_file() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not AUDIT_LOG_PATH.exists():
        AUDIT_LOG_PATH.touch()
        try:
            # Group-readable/writable (for bldcms-admin group members' processes to append),
            # never world-readable - this file accumulates who ran what, which is itself
            # sensitive operational information.
            os.chmod(AUDIT_LOG_PATH, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP)
        except OSError:
            pass


def write_audit_entry(entry: AuditEntry) -> None:
    """Never raises - a logging failure must never mask or replace the real error from the
    command itself. Writes to the dedicated file first (works even without a DB connection),
    then best-effort mirrors into the activity_logs table."""
    try:
        _ensure_audit_log_file()
        with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(entry.to_json_line() + "\n")
    except Exception as exc:
        # Last resort: stderr, so the operator at least sees *something* went wrong with
        # auditing, without ever raising out of this function.
        print(f"[bldcms-admin] WARNING: failed to write audit log entry: {exc}", flush=True)

    _mirror_to_activity_log(entry)


def _mirror_to_activity_log(entry: AuditEntry) -> None:
    try:
        from app.database.database import SessionLocal
        from app.services.activity_log_service import Action, log_activity

        action_map = {
            "devices list": Action.ADMIN_CLI_DEVICES_LISTED,
            "devices info": Action.ADMIN_CLI_DEVICE_VIEWED,
            "sessions list": Action.ADMIN_CLI_SESSIONS_LISTED,
            "sessions revoke": Action.ADMIN_CLI_SESSION_REVOKED,
            "devices force-logout": Action.ADMIN_CLI_FORCE_LOGOUT,
            "devices clear-app-data": Action.ADMIN_CLI_APP_DATA_CLEAR_REQUESTED,
            "diagnostics create": Action.ADMIN_CLI_DIAGNOSTIC_BUNDLE_CREATED,
            "health": Action.ADMIN_CLI_HEALTH_CHECKED,
            "services status": Action.ADMIN_CLI_HEALTH_CHECKED,
            "backup create": Action.ADMIN_CLI_BACKUP_CREATED,
            "backup restore": Action.ADMIN_CLI_BACKUP_RESTORED,
            "logs archive": Action.ADMIN_CLI_LOGS_ARCHIVED,
            "pdfs archive": Action.ADMIN_CLI_PDFS_ARCHIVED,
            "checksheets export": Action.ADMIN_CLI_CHECKSHEETS_EXPORTED,
        }
        action = action_map.get(entry.command, Action.ADMIN_CLI_ACCESS_DENIED if entry.result == "Failure" else None)
        if action is None:
            return

        db = SessionLocal()
        try:
            log_activity(
                db,
                action,
                description=(
                    f"bldcms-admin {entry.command} by Linux user '{entry.linux_username}'"
                    f"{' from ' + entry.source_host if entry.source_host else ''} -> {entry.result}"
                ),
                metadata={
                    "linux_username": entry.linux_username,
                    "source_host": entry.source_host,
                    "parameters": entry.redacted_parameters(),
                    "result": entry.result,
                    "error": entry.error,
                },
            )
        finally:
            db.close()
    except Exception:
        # activity_log mirroring is a bonus, not the source of truth (the file above is) - never
        # let a DB problem here surface as a CLI error.
        pass
