#!/usr/bin/env bash
#
# Module 44: mounts the internal SATA HDD (/dev/sda) that the Automated Backup System writes to,
# and makes the mount permanent across reboots via /etc/fstab.
#
# This script does NOT format /dev/sda - it already carries an ext4 filesystem (confirmed via
# `lsblk -f`) and may already hold prior backups; this script only mounts what's already there.
# If /dev/sda is ever genuinely blank/unformatted on a different host, format it manually first
# (e.g. `mkfs.ext4 /dev/sda`) - deliberately not automated here, since running mkfs against the
# wrong device by mistake is unrecoverable.
#
# Idempotent - safe to re-run. Replaces any previous /etc/fstab line for this disk's UUID rather
# than duplicating it (this repo's /etc/fstab had a malformed, mountpoint-less line from an
# earlier manual `blkid` paste - this script fixes that instead of adding a second entry).
#
# Usage (must be run as root):
#   sudo bash scripts/mount_backup_hdd.sh [mount-point] [owner-user]
#
# Defaults: mount-point=/mnt/storage, owner-user=the user who invoked sudo ($SUDO_USER), so the
# backend service user can write backups here without needing root on every run.

set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
    echo "This script must be run as root: sudo bash scripts/mount_backup_hdd.sh" >&2
    exit 1
fi

DEVICE="/dev/sda"
MOUNT_POINT="${1:-/mnt/storage}"
OWNER_USER="${2:-${SUDO_USER:-root}}"

if [[ ! -b "${DEVICE}" ]]; then
    echo "Error: ${DEVICE} not found. Run 'lsblk' to confirm the correct device name on this host." >&2
    exit 1
fi

FSTYPE="$(lsblk -no FSTYPE "${DEVICE}")"
UUID="$(lsblk -no UUID "${DEVICE}")"

if [[ -z "${FSTYPE}" || -z "${UUID}" ]]; then
    echo "Error: ${DEVICE} has no filesystem/UUID. This script does not format disks - format it" >&2
    echo "manually first (e.g. 'mkfs.ext4 ${DEVICE}') only if you are certain this is the correct," >&2
    echo "blank backup disk, then re-run this script." >&2
    exit 1
fi

echo "==> ${DEVICE}: filesystem=${FSTYPE} uuid=${UUID}"

echo "==> Ensuring mount point ${MOUNT_POINT} exists"
mkdir -p "${MOUNT_POINT}"

echo "==> Updating /etc/fstab (removing any prior entry for this UUID first)"
FSTAB_TMP="$(mktemp)"
grep -v "${UUID}" /etc/fstab > "${FSTAB_TMP}" || true
{
    cat "${FSTAB_TMP}"
    echo "UUID=${UUID}  ${MOUNT_POINT}  ${FSTYPE}  defaults,nofail  0  2"
} > /etc/fstab
rm -f "${FSTAB_TMP}"

echo "==> Mounting via fstab entry"
mount "${MOUNT_POINT}"

echo "==> Setting ownership so '${OWNER_USER}' can write backups here"
chown "${OWNER_USER}:${OWNER_USER}" "${MOUNT_POINT}"

echo "==> Verifying the mount is actually a separate filesystem from /"
if [[ "$(stat -c %d "${MOUNT_POINT}")" == "$(stat -c %d /)" ]]; then
    echo "WARNING: ${MOUNT_POINT} resolves to the same filesystem as / - the mount did not take effect." >&2
    exit 1
fi

echo
echo "Done. ${DEVICE} is mounted at ${MOUNT_POINT} and will remount automatically on boot."
echo "Next: set BLDCMS_BACKUP_ROOT=${MOUNT_POINT}/BL-DCMS (this is now the default) and run:"
echo "  venv/bin/python -m app.backup_system.run verify"
