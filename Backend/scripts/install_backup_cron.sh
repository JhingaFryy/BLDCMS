#!/usr/bin/env bash
#
# Module 44: installs the cron schedule for the Automated Backup System (app/backup_system).
#
# Installs three crontab entries for the invoking user (or the user named by RUN_AS_USER):
#   - Daily backup   02:00 every day
#   - Weekly backup  02:30 every Sunday
#   - Monthly backup 03:00 on the 1st of every month
#
# Idempotent - re-running this script replaces any previously-installed BL-DCMS backup entries
# (matched by the "# bldcms-backup:" marker comment) rather than duplicating them.
#
# Usage:
#   BLDCMS_BACKUP_ROOT=/mnt/storage/BL-DCMS bash scripts/install_backup_cron.sh
#
# BLDCMS_BACKUP_ROOT defaults to /mnt/storage/BL-DCMS (the same default app/backup_system/
# config.py falls back to - this shed's internal SATA HDD, /dev/sda, mounted at /mnt/storage via
# scripts/mount_backup_hdd.sh) if not set - override it here only if a different host mounts the
# drive elsewhere; this is the one place per-host mount configuration belongs, not hardcoded in
# application code.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_PYTHON="${BACKEND_DIR}/venv/bin/python"
BACKUP_ROOT="${BLDCMS_BACKUP_ROOT:-/mnt/storage/BL-DCMS}"
RUN_AS_USER="${RUN_AS_USER:-$(whoami)}"
CRON_LOG="${BACKEND_DIR}/logs/backup_cron.log"

if [[ ! -x "${VENV_PYTHON}" ]]; then
    echo "Error: ${VENV_PYTHON} not found or not executable. Set up the backend venv first." >&2
    exit 1
fi

echo "==> Verifying the backup destination before installing any schedule"
if ! BLDCMS_BACKUP_ROOT="${BACKUP_ROOT}" "${VENV_PYTHON}" -m app.backup_system.run verify > /tmp/bldcms_backup_verify.$$ 2>&1; then
    echo "Verification failed - not installing the cron schedule. Details:" >&2
    cat /tmp/bldcms_backup_verify.$$ >&2
    rm -f /tmp/bldcms_backup_verify.$$
    exit 1
fi
rm -f /tmp/bldcms_backup_verify.$$
echo "    Backup destination ${BACKUP_ROOT} is writable and verified."

MARKER="# bldcms-backup: managed by scripts/install_backup_cron.sh - do not edit by hand"
RUN_CMD="cd ${BACKEND_DIR} && BLDCMS_BACKUP_ROOT='${BACKUP_ROOT}' ${VENV_PYTHON} -m app.backup_system.run"

TMP_CRON="$(mktemp)"
trap 'rm -f "${TMP_CRON}"' EXIT

# Keep every existing crontab line that is NOT part of a previously-installed BL-DCMS backup
# block, then append a fresh block - this is what makes re-running the installer idempotent
# instead of accumulating duplicate entries on every run.
(crontab -u "${RUN_AS_USER}" -l 2>/dev/null || true) | awk -v marker="${MARKER}" '
    $0 == marker { skip = 1; next }
    skip && /^[0-9*]/ { next }
    { skip = 0; print }
' > "${TMP_CRON}"

{
    echo "${MARKER}"
    echo "0 2 * * *   ${RUN_CMD} daily   >> ${CRON_LOG} 2>&1"
    echo "30 2 * * 0  ${RUN_CMD} weekly  >> ${CRON_LOG} 2>&1"
    echo "0 3 1 * *   ${RUN_CMD} monthly >> ${CRON_LOG} 2>&1"
} >> "${TMP_CRON}"

crontab -u "${RUN_AS_USER}" "${TMP_CRON}"

echo "==> Installed backup cron schedule for user '${RUN_AS_USER}':"
crontab -u "${RUN_AS_USER}" -l | grep -A3 "${MARKER}"
echo
echo "Cron output/errors will be appended to ${CRON_LOG}."
echo "Run 'python -m app.backup_system.run verify' any time to re-check the HDD destination."
