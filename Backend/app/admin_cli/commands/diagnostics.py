"""Module 44: System Administration CLI - diagnostic bundle generation.

Gathers a snapshot of backend/database/service health plus recent log tails into a single
timestamped .tar.gz for offline troubleshooting or escalation to the application team. Reuses
system_health_service exclusively for the health data - no new health-check logic here.
"""
from __future__ import annotations

import json
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from app.core.logging import LOG_DIR
from app.database.database import SessionLocal
from app.services import system_health_service

DEFAULT_OUTPUT_DIR = LOG_DIR.parent / "diagnostics"

# Module 44: only these whitelisted log files (the same whitelist system_health_service already
# exposes to the Dashboard's log viewer) are ever included in a bundle - never an arbitrary path,
# and never the admin_cli_audit.log file itself (a diagnostic bundle handed to someone outside
# the bldcms-admin group should not casually leak who's been running privileged commands).
_LOG_TAIL_LINES = 200


def create_bundle(output_dir: str | None = None) -> dict:
    db = SessionLocal()
    try:
        overview = system_health_service.get_overview(db)
        services = system_health_service.get_service_status(db)
        db_stats = system_health_service.get_database_stats(db)
        server_info = system_health_service.get_server_info(db)
        app_info = system_health_service.get_application_info(db)
        log_files = system_health_service.list_log_files()
    finally:
        db.close()

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bundle_name = f"bldcms-diagnostics-{timestamp}"
    out_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    archive_path = out_dir / f"{bundle_name}.tar.gz"

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp) / bundle_name
        tmp_path.mkdir()

        (tmp_path / "overview.json").write_text(json.dumps(overview, indent=2, default=str))
        (tmp_path / "services.json").write_text(json.dumps(services, indent=2, default=str))
        (tmp_path / "database_stats.json").write_text(json.dumps(db_stats, indent=2, default=str))
        (tmp_path / "server_info.json").write_text(json.dumps(server_info, indent=2, default=str))
        (tmp_path / "application_info.json").write_text(json.dumps(app_info, indent=2, default=str))

        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        for entry in log_files:
            key = entry.get("key") if isinstance(entry, dict) else None
            if not key:
                continue
            try:
                tail = system_health_service.tail_log_file(key, _LOG_TAIL_LINES)
                (logs_dir / f"{key}.tail.json").write_text(json.dumps(tail, indent=2, default=str))
            except Exception as exc:
                (logs_dir / f"{key}.error.txt").write_text(str(exc))

        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(tmp_path, arcname=bundle_name)

    return {
        "bundle_path": str(archive_path),
        "size_bytes": archive_path.stat().st_size,
        "created_at": timestamp,
    }
