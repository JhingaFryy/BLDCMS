"""Module 44: retention policy enforcement - keep the newest N dated run-folders per tier,
delete the rest. Applied only to Daily/Weekly/Monthly (each dated run is a self-contained folder
with its own archives); the Database/PDFs/Logs/Releases "latest copy" folders and Manifest/ are
never pruned by this module (Manifest/ is small JSON files, kept as a permanent audit trail;
the "latest copy" folders always hold exactly one current artifact, overwritten each run rather
than accumulated)."""
from __future__ import annotations

import shutil
from pathlib import Path

from app.backup_system.config import RETENTION


def _run_folders_newest_first(tier_dir: Path) -> list[Path]:
    if not tier_dir.exists():
        return []
    folders = [p for p in tier_dir.iterdir() if p.is_dir()]
    # Run folders are named by timestamp (see config.TIMESTAMP_FORMAT), which sorts
    # lexicographically in chronological order - no need to parse the name back into a datetime.
    return sorted(folders, key=lambda p: p.name, reverse=True)


def enforce_retention(tier: str, tier_dir: Path) -> list[Path]:
    """Deletes every run-folder under `tier_dir` beyond the configured keep-count for `tier`.
    Returns the list of deleted folder paths (empty if nothing needed pruning)."""
    keep = RETENTION[tier]
    folders = _run_folders_newest_first(tier_dir)
    to_delete = folders[keep:]

    deleted = []
    for folder in to_delete:
        # Defensive: only ever delete a folder that is actually inside the tier directory we
        # were asked to prune - guards against ever deleting something unexpected if this
        # function is ever called with unexpected input.
        if tier_dir in folder.parents:
            shutil.rmtree(folder)
            deleted.append(folder)
    return deleted
