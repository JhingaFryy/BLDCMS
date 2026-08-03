"""Module 44: manifest generation - one JSON document per backup run, describing what was backed
up, where, how large, and its checksum, centralized under Manifest/ regardless of tier."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from app.backup_system.config import MANIFEST_DIR


@dataclass
class ArchiveEntry:
    """One archive produced by a backup run (e.g. the database dump, or the PDFs tarball)."""
    label: str
    path: str
    size_bytes: int
    checksum_sha256: str


@dataclass
class BackupManifest:
    tier: str  # "Daily" | "Weekly" | "Monthly"
    run_id: str  # timestamp string shared by this run's folder name and every artifact in it
    started_at: str
    completed_at: str
    duration_seconds: float
    status: str  # "success" | "failed"
    archives: list[ArchiveEntry] = field(default_factory=list)
    files_included: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "tier": self.tier,
            "run_id": self.run_id,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_seconds": self.duration_seconds,
            "status": self.status,
            "archives": [vars(a) for a in self.archives],
            "files_included": self.files_included,
            "errors": self.errors,
            "total_size_bytes": sum(a.size_bytes for a in self.archives),
        }


def write_manifest(manifest: BackupManifest) -> Path:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = MANIFEST_DIR / f"{manifest.tier.lower()}-{manifest.run_id}.json"
    manifest_path.write_text(json.dumps(manifest.to_dict(), indent=2))
    return manifest_path


def new_manifest(tier: str, run_id: str, started_at: datetime) -> BackupManifest:
    return BackupManifest(
        tier=tier,
        run_id=run_id,
        started_at=started_at.isoformat(),
        completed_at="",
        duration_seconds=0.0,
        status="failed",  # overwritten to "success" only if the run actually completes cleanly
    )
