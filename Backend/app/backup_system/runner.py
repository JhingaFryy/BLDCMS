"""Module 44: shared run/manifest/logging/retention orchestration used by daily.py/weekly.py/
monthly.py, so each of those three files only has to define *what* to back up, not how to
sequence verification, manifest-writing, logging, or retention."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from app.backup_system import storage
from app.backup_system.backup_logging import log_activity_best_effort, log_event
from app.backup_system.config import RETENTION, TIMESTAMP_FORMAT
from app.backup_system.manifest import ArchiveEntry, BackupManifest, new_manifest, write_manifest
from app.backup_system.retention import enforce_retention
from app.backup_system.storage import BackupStorageError, ensure_folder_structure

ProduceFn = Callable[[Path, str], tuple[list[ArchiveEntry], list[str]]]

_COMPLETED_ACTION = {
    "Daily": "BACKUP_DAILY_COMPLETED",
    "Weekly": "BACKUP_WEEKLY_COMPLETED",
    "Monthly": "BACKUP_MONTHLY_COMPLETED",
}
_FAILED_ACTION = {
    "Daily": "BACKUP_DAILY_FAILED",
    "Weekly": "BACKUP_WEEKLY_FAILED",
    "Monthly": "BACKUP_MONTHLY_FAILED",
}


def run_backup(tier: str, tier_dir: Path, produce: ProduceFn) -> BackupManifest:
    """Runs one backup for `tier` ("Daily"/"Weekly"/"Monthly"):

    1. Verifies the HDD destination is writable (never falls back to writing elsewhere).
    2. Creates a fresh, run_id-named folder under `tier_dir` and calls `produce(run_dir, run_id)`
       to actually create the tier's archives - the only part that differs between tiers.
    3. Writes a manifest describing what happened, regardless of success or failure.
    4. Logs start/completion/failure (both to the dedicated backup_system.log and, best-effort,
       to the application's activity_logs table).
    5. On success, enforces this tier's retention policy and logs anything it deleted.

    A failure in step 2 is caught here (not propagated) so steps 3-4 still run - a failed backup
    must still be logged and manifested, never silently disappear.
    """
    started = datetime.now(timezone.utc)
    run_id = started.strftime(TIMESTAMP_FORMAT)
    manifest = new_manifest(tier, run_id, started)
    log_event(tier, "started")

    try:
        storage.verify_writable()
        ensure_folder_structure()
        run_dir = tier_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        archives, files_included = produce(run_dir, run_id)
        manifest.archives = archives
        manifest.files_included = files_included
        manifest.status = "success"
    except BackupStorageError as exc:
        manifest.errors.append(f"Storage error: {exc}")
        manifest.status = "failed"
    except Exception as exc:  # noqa: BLE001 - a backup run must never crash its own scheduler
        manifest.errors.append(f"{type(exc).__name__}: {exc}")
        manifest.status = "failed"

    completed = datetime.now(timezone.utc)
    manifest.completed_at = completed.isoformat()
    manifest.duration_seconds = (completed - started).total_seconds()
    manifest_path = write_manifest(manifest)
    total_size = sum(a.size_bytes for a in manifest.archives)

    if manifest.status == "success":
        log_event(
            tier, "completed",
            run_id=run_id,
            duration_seconds=manifest.duration_seconds,
            archive_size_bytes=total_size,
            files_included=manifest.files_included,
            manifest_path=str(manifest_path),
        )
        log_activity_best_effort(
            _COMPLETED_ACTION[tier],
            description=f"{tier} backup completed ({total_size:,} bytes, {manifest.duration_seconds:.1f}s)",
            metadata={
                "run_id": run_id,
                "archive_size_bytes": total_size,
                "duration_seconds": manifest.duration_seconds,
                "manifest_path": str(manifest_path),
            },
        )
        deleted = enforce_retention(tier, tier_dir)
        if deleted:
            log_event(tier, "retention_applied", deleted=[str(p) for p in deleted], kept=RETENTION[tier])
            log_activity_best_effort(
                "BACKUP_RETENTION_APPLIED",
                description=f"{tier} backup retention applied - {len(deleted)} old run(s) removed, keeping newest {RETENTION[tier]}",
                metadata={"tier": tier, "deleted": [str(p) for p in deleted], "kept": RETENTION[tier]},
            )
    else:
        log_event(tier, "failed", run_id=run_id, errors=manifest.errors, duration_seconds=manifest.duration_seconds)
        log_activity_best_effort(
            _FAILED_ACTION[tier],
            description=f"{tier} backup failed: {'; '.join(manifest.errors)}",
            metadata={"run_id": run_id, "errors": manifest.errors},
        )

    return manifest
