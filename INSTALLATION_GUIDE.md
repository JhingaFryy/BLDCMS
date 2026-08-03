# BL-DCMS — Installation Guide

A complete, step-by-step deployment manual. Follow sections in order — later steps assume
earlier ones are done. Every placeholder value (`CHANGE_ME`, `YOUR_...`) is cross-referenced in
[`CHANGE_CONFIGURATION.md`](CHANGE_CONFIGURATION.md); this guide tells you *when* to fill each
one in, that file tells you *everything about* each one.

Recommended install path used throughout this guide: `/opt/bldcms`. If you use a different path,
substitute it everywhere below, including inside `Backend/deploy/nginx/bldcms.conf` and
`Backend/deploy/systemd/bldcms-backend.service`.

---

## 1. Ubuntu Preparation

Tested on Ubuntu 22.04 LTS+.

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip curl git \
    build-essential libpq-dev
```

Create a dedicated, non-root service account for the backend (recommended over running it as
your own login):

```bash
sudo useradd --system --create-home --shell /bin/bash bldcms
```

Copy this entire `BL-DCMS_Distribution` folder to the server, e.g.:

```bash
sudo mkdir -p /opt/bldcms
sudo cp -r Android Backend Dashboard Database Docs \
    README.md INSTALLATION_GUIDE.md CHANGE_CONFIGURATION.md \
    /opt/bldcms/
sudo chown -R bldcms:bldcms /opt/bldcms
```

## 2. PostgreSQL Installation

```bash
sudo apt-get install -y postgresql postgresql-contrib
sudo systemctl enable --now postgresql
```

## 3. Database Initialization

```bash
sudo -u postgres psql
```

Inside `psql`:

```sql
CREATE ROLE YOUR_DB_USER WITH LOGIN PASSWORD 'YOUR_DATABASE_PASSWORD';
CREATE DATABASE bldcms OWNER YOUR_DB_USER;
\q
```

Apply the schema, then the bootstrap seed:

```bash
cd /opt/bldcms
psql -h localhost -U YOUR_DB_USER -d bldcms -f Database/01_schema.sql
psql -h localhost -U YOUR_DB_USER -d bldcms -f Database/02_bootstrap_seed.sql
```

Verify:

```bash
psql -h localhost -U YOUR_DB_USER -d bldcms -c "\dt"
psql -h localhost -U YOUR_DB_USER -d bldcms -c "SELECT employee_id, name, role FROM users;"
```

You should see 17 tables and exactly one user (`ELSBL_ADMIN`, role `Admin`).

Optionally load the standard checksheet template library now or later — see
`Database/03_optional_checksheet_template_library.md`.

## 4. Python Dependencies (Backend)

```bash
cd /opt/bldcms/Backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

## 5. Node Dependencies & Dashboard Build

```bash
# Install Node.js 18+ if not already present, e.g. via nodesource:
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

cd /opt/bldcms/Dashboard
npm install
npm run build
```

Confirm the build succeeded:

```bash
ls Dashboard/dist/index.html
```

## 6. Configuration Changes

Edit `Backend/deploy/systemd/bldcms-backend.service` and replace every placeholder:

```ini
Environment="DATABASE_URL=postgresql://YOUR_DB_USER:YOUR_DATABASE_PASSWORD@localhost:5432/bldcms"
Environment="JWT_SECRET_KEY=<output of: openssl rand -hex 32>"
Environment="CORS_ORIGINS=http://YOUR_SERVER_IP,http://localhost"
Environment="DEBUG=false"
Environment="SHOW_OTP_PLAINTEXT=true"   # or false if a real SMS/email OTP gateway is wired up
```

Also set `User=`/`Group=` to the service account created in step 1 (`bldcms` in this guide).

Edit `Backend/deploy/nginx/bldcms.conf`:

```nginx
root /opt/bldcms/Dashboard/dist;   # must match your actual install path exactly
```

See `CHANGE_CONFIGURATION.md` for the complete list — don't skip items 14–16 (organization name,
logo artwork, bootstrap password) even though they aren't required for the app to *run*.

## 7. SSL (Optional)

This distribution ships configured for plain HTTP, appropriate for a closed shed LAN with no
internet exposure. If this deployment will be reachable outside a trusted local network:

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d bldcms.yourshed.example
```

Then:
1. Add a `listen 443 ssl;` server block (certbot does this automatically) — Gunicorn's own bind
   stays on `127.0.0.1:8080` regardless, that traffic never leaves the host.
2. In `Android/app/src/main/res/xml/network_security_config.xml`, set
   `cleartextTrafficPermitted="false"`, scoped to the production HTTPS host.
3. Change `Android/local.properties` → `API_BASE_URL` to `https://...`.
4. Rebuild and redistribute the Android APK (step 9 below).

## 8. Nginx

```bash
sudo apt-get install -y nginx
sudo mkdir -p /etc/nginx/bldcms
sudo cp /opt/bldcms/Backend/deploy/nginx/security_headers.conf /etc/nginx/bldcms/security_headers.conf
sudo cp /opt/bldcms/Backend/deploy/nginx/bldcms.conf /etc/nginx/sites-available/bldcms.conf
sudo ln -sf /etc/nginx/sites-available/bldcms.conf /etc/nginx/sites-enabled/bldcms.conf
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable --now nginx
```

If `nginx -t` reports a 403-related permission issue serving `Dashboard/dist`, see the note in
`Backend/deploy/install_production.sh` (step 2b) — typically only relevant if you installed under
a home directory instead of `/opt`.

## 9. systemd

```bash
sudo cp /opt/bldcms/Backend/deploy/systemd/bldcms-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now bldcms-backend
sudo systemctl status bldcms-backend
```

Or run the whole of steps 6, 8, and 9 at once (as root), once the systemd unit and Nginx config
have been edited with real values:

```bash
sudo bash /opt/bldcms/Backend/deploy/install_production.sh
```

## Android Build Process (Release)

1. Install Android Studio or the command-line SDK tools + JDK 17 on the build machine.
2. Edit `Android/local.properties`:
   ```properties
   sdk.dir=/path/to/your/Android/Sdk
   API_BASE_URL=http://YOUR_SERVER_IP/
   ```
3. (Release builds only) Generate a signing keystore and add to `local.properties`:
   ```bash
   keytool -genkey -v -keystore bldcms-release.jks -keyalg RSA -keysize 2048 -validity 10000 -alias bldcms
   ```
   ```properties
   RELEASE_STORE_FILE=/path/to/bldcms-release.jks
   RELEASE_STORE_PASSWORD=...
   RELEASE_KEY_ALIAS=bldcms
   RELEASE_KEY_PASSWORD=...
   ```
   See `Android/RELEASE_CHECKLIST.md` for the full pre-release checklist.
4. Build:
   ```bash
   cd Android
   ./gradlew assembleRelease     # or assembleDebug for an unsigned test build
   ```
5. Output: `Android/app/build/outputs/apk/release/app-release.apk` (or `debug/app-debug.apk`).
6. Distribute the APK to technicians' devices (direct file transfer, MDM, or an internal download
   page — no Play Store listing is required for a closed-shed deployment).

## Backup Configuration

**Requires a second physical disk/mount, separate from the application disk** — the backup
system deliberately refuses to run against a same-filesystem path.

```bash
sudo bash /opt/bldcms/Backend/scripts/mount_backup_hdd.sh
BLDCMS_BACKUP_ROOT=/mnt/backup/BL-DCMS bash /opt/bldcms/Backend/scripts/install_backup_cron.sh
```

Verify:

```bash
cd /opt/bldcms/Backend
source venv/bin/activate
python -m app.backup_system.run verify
```

Full schedule/retention/restore procedure: `Docs/AUTOMATED_BACKUP_SYSTEM.md` and
`Docs/BACKUP_AND_RESTORE.md`.

## Deployment Verification

Work through this checklist after installation, before handing the system to real users:

```
□ sudo systemctl status bldcms-backend    → active (running)
□ sudo systemctl status nginx             → active (running)
□ sudo systemctl status postgresql        → active (running)
□ curl -I http://127.0.0.1:8080/          → responds (backend reachable on loopback)
□ Open http://<server-ip>/ in a browser   → Dashboard loads (not raw JSON)
□ Log in as ELSBL_ADMIN / ChangeMe@123    → succeeds
□ Change the bootstrap Administrator's password immediately
□ Create at least one real Section, Equipment, Template, and Locomotive
□ Create a Supervisor and a Technician user
□ Install the Android APK on a test device, log in, submit a checksheet
□ Approve the checksheet as Supervisor and confirm PDF generation
□ Confirm the Digital Signature (emBridge) step completes end-to-end
□ Refresh the Dashboard on a data page (e.g. /users) — must show the app, not raw JSON 401
□ Disconnect the server from the internet and confirm the Dashboard still loads data
  (only the emBridge signing step is expected to need internet/DNS)
□ python -m app.backup_system.run verify  → passes
□ Confirm a Daily backup actually lands in the configured backup destination after 24h
```

Once every box is checked, the deployment is ready for real use. Return to
`CHANGE_CONFIGURATION.md` item 16 as a final reminder: the bootstrap password must not remain at
its default beyond initial setup.
