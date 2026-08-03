"""Module 44: Daily backup (02:00 AM per the installed cron entry - see
scripts/install_backup_cron.sh) - database, generated PDFs, application logs, and configuration
files. Each run writes its own dated folder under Daily/, and updates the always-current copies
under Database/, PDFs/, and Logs/."""
from __future__ import annotations

from pathlib import Path

from app.backup_system.config import (
    CONFIG_FILE_CANDIDATES,
    DAILY_DIR,
    DATABASE_LATEST_DIR,
    LOGS_DIR,
    LOGS_LATEST_DIR,
    PDFS_LATEST_DIR,
    STORAGE_PDFS_DIR,
)
from app.backup_system.manifest import BackupManifest
from app.backup_system.runner import run_backup
from app.backup_system.steps import archive_directory, archive_files, dump_database, update_latest_copy


def _produce(run_dir: Path, run_id: str):
    archives = []
    files_included = []

    db_entry = dump_database(run_dir / "Database", f"bldcms-db-{run_id}.dump")
    archives.append(db_entry)
    files_included.append("PostgreSQL database (pg_dump -Fc)")
    update_latest_copy(db_entry, DATABASE_LATEST_DIR)

    pdfs_entry = archive_directory(STORAGE_PDFS_DIR, run_dir / "PDFs", f"bldcms-pdfs-{run_id}.tar.gz")
    if pdfs_entry:
        archives.append(pdfs_entry)
        files_included.append(f"Generated PDFs ({STORAGE_PDFS_DIR})")
        update_latest_copy(pdfs_entry, PDFS_LATEST_DIR)

    logs_entry = archive_directory(LOGS_DIR, run_dir / "Logs", f"bldcms-logs-{run_id}.tar.gz")
    if logs_entry:
        archives.append(logs_entry)
        files_included.append(f"Application logs ({LOGS_DIR})")
        update_latest_copy(logs_entry, LOGS_LATEST_DIR)

    config_entry = archive_files(CONFIG_FILE_CANDIDATES, run_dir / "Config", f"bldcms-config-{run_id}.tar.gz")
    if config_entry:
        archives.append(config_entry)
        files_included.append("Configuration files: " + ", ".join(
            str(p) for p in CONFIG_FILE_CANDIDATES if p.exists()
        ))

    return archives, files_included


def run_daily_backup() -> BackupManifest:
    return run_backup("Daily", DAILY_DIR, _produce)
