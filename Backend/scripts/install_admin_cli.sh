#!/usr/bin/env bash
#
# Module 44: installs the bldcms-admin System Administration CLI.
#
# What this does:
#   1. Creates the 'bldcms-admin' Linux group (idempotent) - only members of this group (or
#      root) may run privileged bldcms-admin commands. The CLI itself re-checks group
#      membership at runtime (see app/admin_cli/os_auth.py); this script's file permissions are
#      the first line of defense, not the only one.
#   2. Installs a thin wrapper at /usr/local/bin/bldcms-admin that execs this backend's own venv
#      Python running `python -m app.admin_cli.main`.
#   3. Ensures the audit log directory exists with group-writable, setgid permissions, so every
#      bldcms-admin group member's invocations can append to the same audit log file regardless
#      of which member's Linux account ran it.
#
# Must be run as root (it modifies /usr/local/bin and system group membership):
#   sudo bash scripts/install_admin_cli.sh
#
# After installing, grant access to a trusted sysadmin:
#   sudo usermod -aG bldcms-admin <linux-username>
# (they must log out and back in, or run `newgrp bldcms-admin`, for the new group to take effect)

set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
    echo "This installer must be run as root (sudo bash scripts/install_admin_cli.sh)." >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_PYTHON="${BACKEND_DIR}/venv/bin/python"
WRAPPER_PATH="/usr/local/bin/bldcms-admin"
GROUP_NAME="bldcms-admin"
LOG_DIR="${BACKEND_DIR}/logs"

if [[ ! -x "${VENV_PYTHON}" ]]; then
    echo "Error: ${VENV_PYTHON} not found or not executable. Set up the backend venv first." >&2
    exit 1
fi

echo "==> Creating '${GROUP_NAME}' group (if it doesn't already exist)"
if getent group "${GROUP_NAME}" > /dev/null 2>&1; then
    echo "    Group '${GROUP_NAME}' already exists."
else
    groupadd --system "${GROUP_NAME}"
    echo "    Created system group '${GROUP_NAME}'."
fi

echo "==> Installing wrapper at ${WRAPPER_PATH}"
cat > "${WRAPPER_PATH}" <<EOF
#!/usr/bin/env bash
# Installed by scripts/install_admin_cli.sh - do not edit by hand, re-run the installer instead.
#
# 'python -m app.admin_cli.main' resolves the 'app' package against the current working
# directory, not this script's location - without the cd below, running bldcms-admin from
# anywhere other than ${BACKEND_DIR} itself fails with
# "ModuleNotFoundError: No module named 'app'".
cd "${BACKEND_DIR}" || exit 1
exec "${VENV_PYTHON}" -m app.admin_cli.main "\$@"
EOF
chown root:"${GROUP_NAME}" "${WRAPPER_PATH}"
chmod 750 "${WRAPPER_PATH}"
echo "    Installed (mode 750, owner root:${GROUP_NAME})."

echo "==> Preparing audit log directory ${LOG_DIR}"
mkdir -p "${LOG_DIR}"
chgrp "${GROUP_NAME}" "${LOG_DIR}"
# setgid on the directory so every new file created inside it (application.log,
# admin_cli_audit.log, etc.) inherits the bldcms-admin group automatically, regardless of which
# Linux user's process (the backend service account, or any bldcms-admin group member running
# the CLI) created it.
chmod 2775 "${LOG_DIR}"
touch "${LOG_DIR}/admin_cli_audit.log"
chgrp "${GROUP_NAME}" "${LOG_DIR}/admin_cli_audit.log"
chmod 660 "${LOG_DIR}/admin_cli_audit.log"
echo "    Ready."

echo ""
echo "Installation complete."
echo ""
echo "Grant access to a trusted administrator with:"
echo "  sudo usermod -aG ${GROUP_NAME} <linux-username>"
echo ""
echo "That user must start a new login session (log out/in, or run 'newgrp ${GROUP_NAME}')"
echo "for the group membership to take effect, then can run:"
echo "  bldcms-admin health"
