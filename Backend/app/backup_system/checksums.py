"""Module 44: archive integrity - SHA-256 checksums."""
from __future__ import annotations

import hashlib
from pathlib import Path

_CHUNK_SIZE = 1024 * 1024  # 1 MiB - large enough to be fast, small enough not to load a
                            # multi-GB database dump into memory at once.


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(_CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def write_checksum_file(archive_path: Path) -> Path:
    """Writes `<archive_path>.sha256` in the standard `<hash>  <filename>` format `sha256sum -c`
    can verify directly, and returns its path."""
    checksum = sha256_file(archive_path)
    checksum_path = archive_path.with_name(archive_path.name + ".sha256")
    checksum_path.write_text(f"{checksum}  {archive_path.name}\n")
    return checksum_path


def verify_checksum_file(archive_path: Path) -> bool:
    """Recomputes the archive's checksum and compares it against its .sha256 sidecar file.
    Returns False (rather than raising) if the sidecar is missing, so callers can treat a missing
    checksum the same as a failed one."""
    checksum_path = archive_path.with_name(archive_path.name + ".sha256")
    if not checksum_path.exists():
        return False
    recorded = checksum_path.read_text().strip().split()[0]
    return recorded == sha256_file(archive_path)
