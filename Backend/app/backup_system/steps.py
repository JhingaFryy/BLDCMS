"""Module 44: reusable backup primitives - database dump, directory archiving, and "latest copy"
maintenance. Deliberately self-contained (does not import from app.admin_cli) - the two packages
are independent, parallel tools that both happen to read the same database engine and produce
similar artifacts, not a shared dependency chain."""
from __future__ import annotations

import os
import shutil
import subprocess
import tarfile
from pathlib import Path
from typing import Iterable

from app.backup_system.checksums import write_checksum_file
from app.backup_system.manifest import ArchiveEntry
from app.database.database import engine


class BackupStepError(RuntimeError):
    """Raised when an individual backup step (pg_dump, tar, copy) fails."""


def _pg_env() -> dict:
    env = {**os.environ}
    if engine.url.password:
        env["PGPASSWORD"] = engine.url.password
    return env


def dump_database(dest_dir: Path, filename: str) -> ArchiveEntry:
    """Runs `pg_dump -Fc` (PostgreSQL's own compressed custom format - no separate compression
    step needed) against the database this backend is configured for, straight to `dest_dir`."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    dump_path = dest_dir / filename

    result = subprocess.run(
        [
            "pg_dump", "-Fc",
            "-h", engine.url.host or "localhost",
            "-p", str(engine.url.port or 5432),
            "-U", engine.url.username or "",
            "-d", engine.url.database or "",
            "-f", str(dump_path),
        ],
        env=_pg_env(),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise BackupStepError(f"pg_dump failed: {result.stderr.strip()}")

    write_checksum_file(dump_path)
    return ArchiveEntry(
        label="database",
        path=str(dump_path),
        size_bytes=dump_path.stat().st_size,
        checksum_sha256=_read_checksum(dump_path),
    )


def _read_checksum(archive_path: Path) -> str:
    checksum_path = archive_path.with_name(archive_path.name + ".sha256")
    return checksum_path.read_text().split()[0]


def archive_directory(
    src: Path,
    dest_dir: Path,
    filename: str,
    *,
    arcname: str | None = None,
    exclude_dir_names: Iterable[str] = (),
) -> ArchiveEntry | None:
    """Tars and gzip-compresses `src` into `dest_dir/filename`. Returns None (does nothing,
    raises nothing) if `src` doesn't exist - many optional sources (e.g. an Android checkout on a
    backend-only host) legitimately may not be present."""
    if not src.exists():
        return None

    dest_dir.mkdir(parents=True, exist_ok=True)
    archive_path = dest_dir / filename
    exclude = set(exclude_dir_names)

    def _filter(tarinfo: tarfile.TarInfo) -> tarfile.TarInfo | None:
        parts = Path(tarinfo.name).parts
        if exclude.intersection(parts):
            return None
        return tarinfo

    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(src, arcname=arcname or src.name, filter=_filter)

    write_checksum_file(archive_path)
    return ArchiveEntry(
        label=arcname or src.name,
        path=str(archive_path),
        size_bytes=archive_path.stat().st_size,
        checksum_sha256=_read_checksum(archive_path),
    )


def archive_files(paths: Iterable[Path], dest_dir: Path, filename: str) -> ArchiveEntry | None:
    """Tars and gzip-compresses a flat list of individual files (e.g. scattered per-installation
    config files) into `dest_dir/filename`. Silently skips any path that doesn't exist. Returns
    None if none of the given paths exist."""
    existing = [p for p in paths if p.exists()]
    if not existing:
        return None

    dest_dir.mkdir(parents=True, exist_ok=True)
    archive_path = dest_dir / filename
    with tarfile.open(archive_path, "w:gz") as tar:
        for path in existing:
            tar.add(path, arcname=path.name)

    write_checksum_file(archive_path)
    return ArchiveEntry(
        label="config",
        path=str(archive_path),
        size_bytes=archive_path.stat().st_size,
        checksum_sha256=_read_checksum(archive_path),
    )


def update_latest_copy(entry: ArchiveEntry | None, latest_dir: Path) -> None:
    """Replaces whatever is in `latest_dir` with a copy of `entry`'s archive (+ its checksum
    sidecar) - the single always-current artifact the Database/PDFs/Logs/Releases top-level
    folders hold, alongside the full dated history kept under Daily/Weekly/Monthly."""
    if entry is None:
        return
    latest_dir.mkdir(parents=True, exist_ok=True)
    for existing in latest_dir.iterdir():
        if existing.is_file():
            existing.unlink()
    src = Path(entry.path)
    shutil.copy2(src, latest_dir / src.name)
    checksum_src = src.with_name(src.name + ".sha256")
    if checksum_src.exists():
        shutil.copy2(checksum_src, latest_dir / checksum_src.name)
