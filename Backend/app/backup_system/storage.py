"""Module 44: HDD destination verification and folder-structure management."""
from __future__ import annotations

import os
import uuid
from pathlib import Path

from app.backup_system.config import ALL_BACKUP_DIRS, BACKUP_ROOT
from app.core.logging import BACKEND_DIR


class BackupStorageError(RuntimeError):
    """Raised when the configured backup destination can't be used - callers must treat this as
    a hard stop (never silently fall back to writing a backup onto the application's own SSD)."""


def ensure_folder_structure() -> list[Path]:
    """Creates every top-level folder this module owns (Daily/Weekly/Monthly/Database/PDFs/Logs/
    Releases/Manifest) if missing. Idempotent - safe to call at the start of every run."""
    created = []
    for directory in ALL_BACKUP_DIRS:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            created.append(directory)
    return created


def verify_writable(root: Path = BACKUP_ROOT) -> None:
    """Confirms the backup root actually exists and is writable by writing and removing a small
    probe file. Raises BackupStorageError with a clear message on any failure - a backup run must
    stop here rather than fall back to writing anywhere else, since the whole point of this
    module is that backups never land on the application's own disk."""
    if not root.exists():
        raise BackupStorageError(
            f"Backup root {root} does not exist. Mount the backup HDD at this path, or set "
            f"BLDCMS_BACKUP_ROOT to the correct mount point, before running a backup."
        )
    probe = root / f".write_test_{uuid.uuid4().hex}"
    try:
        probe.write_text("bldcms-backup-write-test")
        probe.unlink()
    except OSError as exc:
        raise BackupStorageError(f"Backup root {root} is not writable: {exc}") from exc


def same_filesystem_as_app(root: Path = BACKUP_ROOT) -> bool:
    """True if `root` resolves to the same filesystem/device as the application's own checkout
    (BACKEND_DIR) - i.e. the "HDD" isn't actually a separate mounted disk. This is a warning
    signal, not necessarily fatal on its own (a misconfigured but still-writable path is still
    better than crashing outright), but it means the core requirement - backups must not live on
    the SSD - is not actually being satisfied and must be corrected before this is relied on."""
    try:
        return os.stat(root).st_dev == os.stat(BACKEND_DIR).st_dev
    except OSError:
        return False


def verify_destination(root: Path = BACKUP_ROOT) -> dict:
    """Full pre-flight check bundling the two checks above into the single JSON-serializable
    result `run.py verify` and the daily/weekly/monthly entry points report."""
    result: dict = {"backup_root": str(root), "writable": False, "same_filesystem_as_app": None}
    verify_writable(root)
    result["writable"] = True
    result["same_filesystem_as_app"] = same_filesystem_as_app(root)
    return result
