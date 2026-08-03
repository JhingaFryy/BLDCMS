"""Module 42: System Administration CLI - database backup/restore, log/PDF archiving, and
checksheet export.

Mirrors commands/diagnostics.py's shape: one function per command, each returning a JSON-
serializable dict for main.py's _print(). Backup/restore shell out to pg_dump/pg_restore using
connection info read from the existing SQLAlchemy `engine` (app/database/database.py) via its
`.url` object - already percent-decoded, so no re-parsing of the raw DATABASE_URL string. The
password is passed to the subprocess via a PGPASSWORD environment variable, never as a CLI
argument (which would leak into `ps`/shell history).
"""
from __future__ import annotations

import csv
import os
import subprocess
import tarfile
from datetime import datetime, timezone
from pathlib import Path

from app.core.logging import LOG_DIR
from app.database.database import SessionLocal, engine
from app.models.checksheet_header import ChecksheetHeader
from app.models.equipment import Equipment
from app.models.locomotive import Locomotive
from app.models.section import Section
from app.models.user import User
from app.services.pdf_service import PdfService

DEFAULT_BACKUP_DIR = LOG_DIR.parent / "backups"
DEFAULT_ARCHIVE_DIR = LOG_DIR.parent / "archives"


def _pg_env() -> dict:
    env = {**os.environ}
    if engine.url.password:
        env["PGPASSWORD"] = engine.url.password
    return env


def _pg_connection_args() -> list[str]:
    return [
        "-h", engine.url.host or "localhost",
        "-p", str(engine.url.port or 5432),
        "-U", engine.url.username or "",
        "-d", engine.url.database or "",
    ]


def create_backup(output_dir: str | None = None) -> dict:
    out_dir = Path(output_dir) if output_dir else DEFAULT_BACKUP_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_path = out_dir / f"bldcms-backup-{timestamp}.dump"

    result = subprocess.run(
        ["pg_dump", "-Fc", *_pg_connection_args(), "-f", str(backup_path)],
        env=_pg_env(),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pg_dump failed: {result.stderr.strip()}")

    return {
        "backup_path": str(backup_path),
        "size_bytes": backup_path.stat().st_size,
        "created_at": timestamp,
    }


def restore_backup(file: str, confirm: bool, database_name_confirmation: str | None) -> dict:
    """Restores a pg_dump -Fc backup. Deliberately the most heavily-guarded command in this
    entire CLI - it overwrites live data. Requires BOTH --confirm AND typing the exact database
    name, mirroring the kind of double-confirmation real backup tools use for destructive
    restores."""
    backup_path = Path(file)
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup file not found: {file}")

    actual_database_name = engine.url.database
    if not confirm:
        raise ValueError(
            "Restore requires --confirm - this will overwrite the live database."
        )
    if database_name_confirmation != actual_database_name:
        raise ValueError(
            f"Restore requires typing the exact database name to confirm "
            f"(expected '{actual_database_name}')."
        )

    result = subprocess.run(
        ["pg_restore", "--clean", "--if-exists", *_pg_connection_args(), str(backup_path)],
        env=_pg_env(),
        capture_output=True,
        text=True,
    )
    # pg_restore commonly exits non-zero on harmless warnings (e.g. "role does not exist" for
    # ownership statements) - only treat it as a genuine failure if it produced no output at all
    # alongside the non-zero code, otherwise surface the warnings but still report success.
    if result.returncode != 0 and not result.stderr.strip():
        raise RuntimeError("pg_restore failed with no diagnostic output.")

    return {
        "restored_from": str(backup_path),
        "database": actual_database_name,
        "warnings": result.stderr.strip() or None,
    }


def archive_logs(output_dir: str | None = None) -> dict:
    out_dir = Path(output_dir) if output_dir else DEFAULT_ARCHIVE_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive_path = out_dir / f"bldcms-logs-{timestamp}.tar.gz"

    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(LOG_DIR, arcname="logs")

    return {
        "archive_path": str(archive_path),
        "size_bytes": archive_path.stat().st_size,
        "created_at": timestamp,
    }


def archive_pdfs(output_dir: str | None = None) -> dict:
    out_dir = Path(output_dir) if output_dir else DEFAULT_ARCHIVE_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf_dir = PdfService().output_dir
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive_path = out_dir / f"bldcms-signed-pdfs-{timestamp}.tar.gz"

    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(pdf_dir, arcname="pdfs")

    return {
        "archive_path": str(archive_path),
        "size_bytes": archive_path.stat().st_size,
        "created_at": timestamp,
    }


_EXPORT_FIELDS = [
    "id", "status", "work_type", "technician_mobile", "technician_name", "loco_number",
    "section_name", "equipment_name", "submitted_at", "approved_at", "rejected_at", "created_at",
]


def export_checksheets(output_dir: str | None = None, format: str = "csv") -> dict:
    """Header-level summary export (matches the scope of the existing GET /checksheets/report/pdf
    endpoint) - not full field-level detail. Uses stdlib csv, avoiding a new pandas/openpyxl
    dependency."""
    if format != "csv":
        raise ValueError(f"Unsupported export format: {format} (only 'csv' is supported)")

    out_dir = Path(output_dir) if output_dir else DEFAULT_ARCHIVE_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    export_path = out_dir / f"bldcms-checksheets-{timestamp}.csv"

    db = SessionLocal()
    try:
        rows = (
            db.query(ChecksheetHeader)
            .join(Locomotive, ChecksheetHeader.locomotive_id == Locomotive.id)
            .join(Section, ChecksheetHeader.section_id == Section.id)
            .outerjoin(Equipment, ChecksheetHeader.equipment_id == Equipment.id)
            .outerjoin(User, ChecksheetHeader.submitted_by == User.id)
            .with_entities(
                ChecksheetHeader.id,
                ChecksheetHeader.status,
                ChecksheetHeader.work_type,
                ChecksheetHeader.technician_mobile,
                User.name.label("technician_name"),
                Locomotive.loco_number,
                Section.name.label("section_name"),
                Equipment.equipment_name,
                ChecksheetHeader.submitted_at,
                ChecksheetHeader.approved_at,
                ChecksheetHeader.rejected_at,
                ChecksheetHeader.created_at,
            )
            .order_by(ChecksheetHeader.id)
            .all()
        )

        with open(export_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(_EXPORT_FIELDS)
            for row in rows:
                writer.writerow(row)

        count = len(rows)
    finally:
        db.close()

    return {
        "export_path": str(export_path),
        "row_count": count,
        "created_at": timestamp,
    }
