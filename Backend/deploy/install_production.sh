#!/usr/bin/env bash
#
# Module 45: production deployment installer for BL-DCMS.
#
# Installs Nginx (if missing), installs the Gunicorn systemd unit, installs the Nginx site
# config, stops the development servers (Vite + standalone Uvicorn) this replaces, and starts
# the production services. Idempotent - safe to re-run.
#
# Must be run as root:
#   sudo bash deploy/install_production.sh
#
# What this does NOT do (deliberately, see ../../Docs/DEPLOYMENT.md and CHANGE_CONFIGURATION.md):
#   - Does not create a systemd unit for Vite - there is no production Vite process; the
#     Dashboard is a static build served by Nginx.
#   - Does not touch PostgreSQL configuration.
#   - Does not generate DATABASE_URL/JWT_SECRET_KEY for you - edit
#     deploy/systemd/bldcms-backend.service with this shed's real values BEFORE running this
#     script (see CHANGE_CONFIGURATION.md).

set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
    echo "This script must be run as root: sudo bash deploy/install_production.sh" >&2
    exit 1
fi

BACKEND_DIR="/opt/bldcms/Backend"
DASHBOARD_DIR="/opt/bldcms/Dashboard"
DEPLOY_DIR="${BACKEND_DIR}/deploy"

echo "==> 1/7: Installing Nginx (skipped if already present)"
if ! command -v nginx >/dev/null 2>&1; then
    apt-get update -qq
    apt-get install -y nginx
else
    echo "    nginx already installed: $(nginx -v 2>&1)"
fi

echo "==> 2/7: Verifying the Dashboard production build exists"
if [[ ! -f "${DASHBOARD_DIR}/dist/index.html" ]]; then
    echo "Error: ${DASHBOARD_DIR}/dist/index.html not found. Run 'npm run build' in ${DASHBOARD_DIR} first." >&2
    exit 1
fi
echo "    found ${DASHBOARD_DIR}/dist/index.html"

echo "==> 2b/7: Verifying Nginx (www-data) can traverse into ${BACKEND_DIR%/Backend}"
# CHANGE_ME: this deployment defaults to /opt/bldcms, which is world-traversable by default on a
# fresh Ubuntu install - no permission change is normally needed. If this project is instead
# checked out under a home directory (e.g. /home/<user>/BL-DCMS), that directory is typically 750
# (owner-only) and will block Nginx (www-data) from reaching Dashboard/dist/index.html with a 403.
# In that case, grant traversal only (not listing) with:
#   chmod o+x /home/<user>
if [[ ! -x "$(dirname "${DASHBOARD_DIR}")" ]]; then
    echo "    WARNING: $(dirname "${DASHBOARD_DIR}") is not traversable by other users - Nginx" >&2
    echo "    (www-data) will get a 403. Run: chmod o+x $(dirname "${DASHBOARD_DIR}")" >&2
fi

echo "==> 3/7: Stopping development servers this deployment replaces"
pkill -f "venv/bin/uvicorn main:app" 2>/dev/null && echo "    stopped standalone dev Uvicorn" || echo "    dev Uvicorn was not running"
pkill -f "node .*/Dashboard/node_modules/.bin/vite" 2>/dev/null && echo "    stopped Vite dev server" || echo "    Vite dev server was not running"
sleep 1

echo "==> 4/7: Installing the Gunicorn systemd unit"
cp "${DEPLOY_DIR}/systemd/bldcms-backend.service" /etc/systemd/system/bldcms-backend.service
systemctl daemon-reload

echo "==> 5/7: Installing the Nginx site config"
mkdir -p /etc/nginx/bldcms
cp "${DEPLOY_DIR}/nginx/security_headers.conf" /etc/nginx/bldcms/security_headers.conf
cp "${DEPLOY_DIR}/nginx/bldcms.conf" /etc/nginx/sites-available/bldcms.conf
mkdir -p /etc/nginx/sites-enabled
ln -sf /etc/nginx/sites-available/bldcms.conf /etc/nginx/sites-enabled/bldcms.conf
rm -f /etc/nginx/sites-enabled/default
nginx -t

echo "==> 6/7: Starting/enabling services (auto-start on boot, auto-restart on crash)"
systemctl enable --now bldcms-backend
systemctl enable --now nginx
systemctl reload nginx

echo "==> 7/7: Waiting for the backend to come up"
for i in $(seq 1 15); do
    if curl -fs http://127.0.0.1:8080/ >/dev/null 2>&1; then
        echo "    backend is responding"
        break
    fi
    sleep 1
done

echo
echo "Done."
systemctl --no-pager status bldcms-backend | head -5
echo
systemctl --no-pager status nginx | head -5
echo
echo "Dashboard should now be reachable at: http://$(hostname -I | awk '{print $1}')/"
echo "Remember: the Android app's local.properties API_BASE_URL must point at this same origin"
echo "(port 80, no :8080) now that the backend only binds to 127.0.0.1 - see Documentation/DEPLOYMENT.md."
