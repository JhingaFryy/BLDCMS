"""Module 44: Monthly backup (1st of the month, 02:00 AM per the installed cron entry) - the same
full snapshot content as Weekly (see full_snapshot.py), on a longer cadence and a longer,
separate retention window (newest 12 kept - a rolling one-year archive, per the project owner's
explicit confirmation; see config.RETENTION)."""
from __future__ import annotations

from app.backup_system.config import MONTHLY_DIR
from app.backup_system.full_snapshot import produce_full_snapshot
from app.backup_system.manifest import BackupManifest
from app.backup_system.runner import run_backup


def run_monthly_backup() -> BackupManifest:
    return run_backup("Monthly", MONTHLY_DIR, produce_full_snapshot)
