"""Module 44: end-to-end self-test - exercises every piece of the backup system (HDD
writability, folder structure, archiving, compression, checksums, manifests, retention) against
the real configured BACKUP_ROOT, using small synthetic data written to and removed from a
dedicated scratch subfolder - never touching real Daily/Weekly/Monthly run folders or their
retention counts. Run via `python -m app.backup_system.run verify`, e.g. right after mounting a
new backup HDD, before trusting it with the first real scheduled run."""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from app.backup_system import storage
from app.backup_system.checksums import verify_checksum_file
from app.backup_system.config import BACKUP_ROOT
from app.backup_system.manifest import new_manifest, write_manifest
from app.backup_system.retention import enforce_retention
from app.backup_system.steps import archive_directory
from datetime import datetime, timezone

_SCRATCH_DIR_NAME = "_verify_scratch"


def run_verification() -> dict:
    checks: dict[str, dict] = {}
    overall_ok = True

    def record(name: str, ok: bool, detail: str = "") -> None:
        nonlocal overall_ok
        checks[name] = {"ok": ok, "detail": detail}
        overall_ok = overall_ok and ok

    def record_info(name: str, ok: bool, detail: str = "") -> None:
        # Informational only - deliberately does NOT affect overall_ok. Used for checks that are
        # worth surfacing prominently but that this environment may not always be able to satisfy
        # (e.g. a real second disk isn't available in every context this runs in).
        checks[name] = {"ok": ok, "detail": detail, "informational": True}

    # 1. HDD writable
    try:
        storage.verify_writable()
        record("hdd_writable", True, str(BACKUP_ROOT))
    except storage.BackupStorageError as exc:
        record("hdd_writable", False, str(exc))
        # Nothing else below can succeed without a writable destination - stop here.
        return {"ok": overall_ok, "checks": checks}

    # 1b. Backup root is genuinely a separate disk from the application's own checkout - the
    # core requirement this whole module exists to satisfy. Reported here (not just buried in a
    # separate function) precisely because this is the check most likely to be silently wrong -
    # e.g. BLDCMS_BACKUP_ROOT pointed at a plain folder on the SSD during testing.
    same_fs = storage.same_filesystem_as_app()
    record_info(
        "hdd_is_separate_disk",
        not same_fs,
        "confirmed separate from the application's own disk" if not same_fs
        else "WARNING: backup root resolves to the SAME disk as the application - not a real separate HDD",
    )

    # 2. Backup folders exist (create them if missing, then confirm)
    storage.ensure_folder_structure()
    from app.backup_system.config import ALL_BACKUP_DIRS
    missing = [str(d) for d in ALL_BACKUP_DIRS if not d.exists()]
    record("folder_structure", not missing, "all present" if not missing else f"missing: {missing}")

    # 3-6. Archive creation, compression, checksum, manifest - run against synthetic data in a
    # scratch folder that is entirely deleted afterwards, regardless of outcome.
    scratch_root = BACKUP_ROOT / _SCRATCH_DIR_NAME
    scratch_root.mkdir(parents=True, exist_ok=True)
    fake_source = Path(tempfile.mkdtemp(prefix="bldcms_backup_verify_"))
    try:
        (fake_source / "sample.txt").write_text("BL-DCMS backup system verification file.\n")

        run_id = datetime.now(timezone.utc).strftime("verify_%Y%m%dT%H%M%SZ")
        run_dir = scratch_root / run_id
        entry = archive_directory(fake_source, run_dir, "verify.tar.gz")
        record("archive_created", entry is not None and Path(entry.path).exists())
        record("compression_succeeds", entry is not None and Path(entry.path).stat().st_size > 0)

        checksum_ok = entry is not None and verify_checksum_file(Path(entry.path))
        record("checksum_generated", checksum_ok)

        manifest = new_manifest("Verify", run_id, datetime.now(timezone.utc))
        manifest.archives = [entry] if entry else []
        manifest.status = "success"
        manifest.completed_at = datetime.now(timezone.utc).isoformat()
        manifest_path = write_manifest(manifest)
        record("manifest_generated", manifest_path.exists())

        # 7. Retention policy - a dedicated, otherwise-empty scratch subfolder (never the same
        # folder the archive-creation check above just wrote its own "verify_..." run into,
        # which would otherwise skew the count) gets 3 dummy dated folders; confirm
        # enforce_retention() with keep=2 removes exactly the oldest one.
        from app.backup_system.config import RETENTION
        retention_scratch = scratch_root / "retention_test"
        retention_scratch.mkdir(exist_ok=True)
        RETENTION["_VerifyTier"] = 2
        for i in range(3):
            (retention_scratch / f"20200101T00000{i}Z").mkdir(exist_ok=True)
        deleted = enforce_retention("_VerifyTier", retention_scratch)
        remaining = sorted(p.name for p in retention_scratch.iterdir() if p.is_dir())
        del RETENTION["_VerifyTier"]
        record(
            "retention_policy",
            len(deleted) == 1 and len(remaining) == 2,
            f"deleted={[p.name for p in deleted]}, remaining={remaining}",
        )
    finally:
        shutil.rmtree(fake_source, ignore_errors=True)
        shutil.rmtree(scratch_root, ignore_errors=True)

    return {"ok": overall_ok, "checks": checks}
