"""Module 44: Weekly backup (Sunday 02:00 AM per the installed cron entry) - a full compressed
snapshot of Backend, Dashboard, Android, Documentation, plus a fresh database dump and
configuration files. See full_snapshot.py for the shared content-producing logic."""
from __future__ import annotations

from app.backup_system.config import WEEKLY_DIR
from app.backup_system.full_snapshot import produce_full_snapshot
from app.backup_system.manifest import BackupManifest
from app.backup_system.runner import run_backup


def run_weekly_backup() -> BackupManifest:
    return run_backup("Weekly", WEEKLY_DIR, produce_full_snapshot)
