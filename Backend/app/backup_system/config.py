"""Module 44: configuration for the automated backup system.

Every path is derived from a single configurable root - BACKUP_ROOT - so nothing here ever
hardcodes a mount name beyond this one default. Override via the BLDCMS_BACKUP_ROOT environment
variable (see Documentation/BACKUP_AND_RESTORE.md and Documentation/AUTOMATED_BACKUP_SYSTEM.md).

The default below matches this shed's actual internal SATA HDD (/dev/sda, an ext4-formatted
disk separate from the application's own SSD) mounted at /mnt/storage via
scripts/mount_backup_hdd.sh - not a generic placeholder. A different host with the drive mounted
elsewhere should set BLDCMS_BACKUP_ROOT rather than editing this file.
"""
from __future__ import annotations

import os
from pathlib import Path

from app.core.logging import BACKEND_DIR

# Override in production - e.g. the backend's systemd unit's Environment= line, or the crontab
# entry installed by scripts/install_backup_cron.sh, should export this to point at the real HDD
# mount for this host. Never store backups under BACKEND_DIR (the app's own SSD-hosted checkout)
# - see storage.same_filesystem_as_app(), which checks for exactly this mistake.
BACKUP_ROOT = Path(os.getenv("BLDCMS_BACKUP_ROOT", "/mnt/storage/BL-DCMS"))

# The eight top-level folders this module owns under BACKUP_ROOT. Daily/Weekly/Monthly hold one
# timestamped subfolder per backup run (the unit retention.py prunes). Database/PDFs/Logs/
# Releases hold a single always-current copy of the latest artifact of that kind, for quick
# access without hunting through a dated folder. Manifest/ centralizes every manifest ever
# written (daily, weekly, and monthly) for easy integrity auditing in one place.
DAILY_DIR = BACKUP_ROOT / "Daily"
WEEKLY_DIR = BACKUP_ROOT / "Weekly"
MONTHLY_DIR = BACKUP_ROOT / "Monthly"
DATABASE_LATEST_DIR = BACKUP_ROOT / "Database"
PDFS_LATEST_DIR = BACKUP_ROOT / "PDFs"
LOGS_LATEST_DIR = BACKUP_ROOT / "Logs"
RELEASES_LATEST_DIR = BACKUP_ROOT / "Releases"
MANIFEST_DIR = BACKUP_ROOT / "Manifest"

ALL_BACKUP_DIRS = [
    DAILY_DIR, WEEKLY_DIR, MONTHLY_DIR,
    DATABASE_LATEST_DIR, PDFS_LATEST_DIR, LOGS_LATEST_DIR, RELEASES_LATEST_DIR, MANIFEST_DIR,
]

# Retention policy: newest N dated subfolders kept per tier, oldest deleted automatically.
# Confirmed with the project owner: Monthly is a rolling 12-month window (auto-pruned), not
# unlimited-forever storage, matching the explicit "keep newest 12 / auto-delete beyond" policy
# rather than the separate "permanent snapshot" wording elsewhere in the same spec.
RETENTION = {
    "Daily": 7,
    "Weekly": 4,
    "Monthly": 12,
}

TIMESTAMP_FORMAT = "%Y%m%dT%H%M%SZ"

# Source paths this module reads from (never writes to).
STORAGE_PDFS_DIR = BACKEND_DIR / "storage" / "pdfs"
LOGS_DIR = BACKEND_DIR / "logs"
PROJECT_ROOT = BACKEND_DIR.parent  # /opt/bldcms - contains Backend/Dashboard/Android/Documentation

# "Configuration files" backed up daily - every well-known, per-installation config file across
# the project that actually exists on this host. Missing files are skipped, never an error -
# different hosts legitimately have different subsets present (e.g. a backend-only host has no
# Android checkout).
CONFIG_FILE_CANDIDATES = [
    BACKEND_DIR / "requirements.txt",
    PROJECT_ROOT / "Dashboard" / ".env",
    PROJECT_ROOT / "Android" / "local.properties",
    Path("/etc/systemd/system/bldcms-backend.service"),
]

# Source trees archived by the Weekly/Monthly full snapshot, with exclusions for anything
# reproducible/huge that a restore doesn't need (dependencies, build output, VCS metadata).
FULL_SNAPSHOT_SOURCES = {
    "Backend": BACKEND_DIR,
    "Dashboard": PROJECT_ROOT / "Dashboard",
    "Android": PROJECT_ROOT / "Android",
    "Documentation": PROJECT_ROOT / "Documentation",
}
FULL_SNAPSHOT_EXCLUDE_DIR_NAMES = {
    "venv", "node_modules", "__pycache__", ".git", ".gradle", ".kotlin", ".idea",
    "build", "dist", "logs", "backups", "archives", "diagnostics", ".pytest_cache",
}
