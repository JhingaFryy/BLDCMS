"""Module 44: full project snapshot - shared by Weekly and Monthly backups, since both back up
the same content (Backend + Dashboard + Android + Documentation source trees, a fresh database
dump, and configuration files) and differ only in cadence, destination folder, and retention."""
from __future__ import annotations

from pathlib import Path

from app.backup_system.config import (
    CONFIG_FILE_CANDIDATES,
    FULL_SNAPSHOT_EXCLUDE_DIR_NAMES,
    FULL_SNAPSHOT_SOURCES,
    RELEASES_LATEST_DIR,
)
from app.backup_system.steps import archive_directory, archive_files, dump_database, update_latest_copy


def produce_full_snapshot(run_dir: Path, run_id: str):
    archives = []
    files_included = []

    db_entry = dump_database(run_dir, f"bldcms-db-{run_id}.dump")
    archives.append(db_entry)
    files_included.append("PostgreSQL database (pg_dump -Fc)")

    for label, src in FULL_SNAPSHOT_SOURCES.items():
        entry = archive_directory(
            src, run_dir, f"bldcms-{label.lower()}-{run_id}.tar.gz",
            arcname=label,
            exclude_dir_names=FULL_SNAPSHOT_EXCLUDE_DIR_NAMES,
        )
        if entry:
            archives.append(entry)
            files_included.append(f"{label}/ source tree ({src})")
            update_latest_copy(entry, RELEASES_LATEST_DIR)

    config_entry = archive_files(CONFIG_FILE_CANDIDATES, run_dir, f"bldcms-config-{run_id}.tar.gz")
    if config_entry:
        archives.append(config_entry)
        files_included.append("Configuration files: " + ", ".join(
            str(p) for p in CONFIG_FILE_CANDIDATES if p.exists()
        ))

    return archives, files_included
