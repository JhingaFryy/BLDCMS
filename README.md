# The Project is Design and Developed by Electric Loco Shed, Valsad. 
This is and In-house project built for maintaining the Digital Records for Checksheets without Paper-hassle. It's a Zero(0) cost project, totally built with knowledge, skills and dedication. Also, It was not possible to bring this project to the table without the Guidance of our Hon' Sr. Divisional Electrical Engineer Shri R. C. Meena and Hon' Divisional Electical Engineer Shri Suresh Kumar. The Project was build and maintained by Mr. Jatinkumar Pardeshi, Tech-III and Mr. Neelkumar Patel, Tech-II.

# BL-DCMS — Digital Checksheet Management System

A digital replacement for paper checksheets used during electric locomotive maintenance at an
Electric Loco Shed. A Technician fills an inspection checksheet on a phone or tablet (Android
app); a Supervisor reviews and formally approves it — with a real digital signature via eMudhra
emBridge — on a computer (React Dashboard), without either side handling a paper form.

**This is a sanitized distribution copy**, intended for deployment at a *new* shed. All
site-specific secrets, IP addresses, and production data have been removed or replaced with
`CHANGE_ME` / `YOUR_...` placeholders — see [`CHANGE_CONFIGURATION.md`](CHANGE_CONFIGURATION.md)
for the full list, and [`INSTALLATION_GUIDE.md`](INSTALLATION_GUIDE.md) for the step-by-step
deployment procedure.

---

## Features

- **Dynamic checksheet templates** — inspection forms are data-driven (Section → Equipment →
  Template → Fields), configurable through the Dashboard's template builder with no code changes.
- **Android technician app** — fill and submit checksheets from a phone/tablet over the shed's
  local network, works with intermittent connectivity.
- **Supervisor approval workflow** — review, reject-with-reason, or approve.
- **Digital signature (DSC)** — Approve & Sign integrates with eMudhra emBridge and a physical
  USB token; the signed PDF is legally attributable to the signing Supervisor.
- **PDF generation** — every approved checksheet produces a formatted, signed PDF.
- **Role-based access** — Admin / Supervisor / Technician, section-scoped visibility.
- **Activity & audit logging**, **OTP-based mobile authentication**, **System Health** dashboard
  (log tailing, service status), **Reports & analytics**.
- **Automated backups** — Daily/Weekly/Monthly tiers to a separate physical disk, with retention
  and verification tooling.

## System Requirements

| Component | Minimum |
|---|---|
| Server OS | Ubuntu 22.04 LTS or newer |
| CPU / RAM | 2 vCPU / 4 GB RAM (more for larger sheds — Gunicorn spawns one worker per core) |
| Disk | 20 GB for the application + OS, **plus a second physical disk/mount** for backups |
| PostgreSQL | 14+ |
| Python | 3.10+ |
| Node.js | 18+ (build-time only — the Dashboard ships as static files, Node is not needed at runtime) |
| Android build | JDK 17, Android SDK (API level per `Android/app/build.gradle.kts`), Gradle (via the bundled `gradlew`) |
| Network | A shed-local LAN reachable by technicians' Android devices and Supervisors' PCs. Internet access is only required for eMudhra emBridge's certificate/DNS handshake — see `CHANGE_CONFIGURATION.md` item 13. |

## Folder Structure

```
BL-DCMS_Distribution/
    Android/                    Android technician app (Kotlin, Jetpack Compose)
    Backend/                    FastAPI + Gunicorn backend, Nginx/systemd deploy configs, DB migrations
    Dashboard/                  React + TypeScript Supervisor/Admin web app (Vite)
    Database/                   Schema-only SQL, bootstrap seed, optional template-library loader
    Docs/                       Full technical documentation set (architecture, backup, admin CLI, user manual)
    README.md                   This file
    INSTALLATION_GUIDE.md       Step-by-step deployment manual
    CHANGE_CONFIGURATION.md     Complete checklist of every value a new shed must set
```

## Installation Steps (summary — see INSTALLATION_GUIDE.md for full detail)

1. Provision an Ubuntu server; copy this folder to it (recommended path: `/opt/bldcms`).
2. Install PostgreSQL, create a role + database, apply `Database/01_schema.sql`, then
   `Database/02_bootstrap_seed.sql`.
3. Set up the Backend: create a Python virtualenv, install `Backend/requirements.txt`, edit
   `Backend/deploy/systemd/bldcms-backend.service` with this shed's real `DATABASE_URL` /
   `JWT_SECRET_KEY` / `CORS_ORIGINS`, install and start the systemd service.
4. Build the Dashboard (`npm install && npm run build` inside `Dashboard/`).
5. Install and configure Nginx using `Backend/deploy/nginx/bldcms.conf`.
6. Set `Android/local.properties` → `API_BASE_URL` to this shed's server address, then build the
   APK and distribute it to technicians' devices.
7. Install emBridge on every Supervisor's PC (see `Docs/EMBRIDGE_INTEGRATION.md`).
8. Set up the automated backup cron schedule (`Backend/scripts/install_backup_cron.sh`).
9. Log in as the bootstrap Administrator and change the password immediately (see "First Login"
   below).

### PostgreSQL setup

```bash
sudo -u postgres psql
CREATE ROLE YOUR_DB_USER WITH LOGIN PASSWORD 'YOUR_DATABASE_PASSWORD';
CREATE DATABASE bldcms OWNER YOUR_DB_USER;
\q

psql -h localhost -U YOUR_DB_USER -d bldcms -f Database/01_schema.sql
psql -h localhost -U YOUR_DB_USER -d bldcms -f Database/02_bootstrap_seed.sql
```

### Backend setup

```bash
cd Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Edit `Backend/deploy/systemd/bldcms-backend.service` — set `DATABASE_URL`, generate and set a
fresh `JWT_SECRET_KEY` (`openssl rand -hex 32`), set `CORS_ORIGINS` to this shed's real address.
See `CHANGE_CONFIGURATION.md` for every field.

```bash
sudo cp Backend/deploy/systemd/bldcms-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now bldcms-backend
```

### Dashboard setup

```bash
cd Dashboard
npm install
npm run build          # produces Dashboard/dist, served directly by Nginx
```

Leave `Dashboard/.env`'s `VITE_API_BASE_URL` commented out unless the Dashboard will be served
from a different origin than the API (uncommon — see `CHANGE_CONFIGURATION.md` item 2).

### Android build

```bash
cd Android
# Edit local.properties first: sdk.dir + API_BASE_URL for this shed
./gradlew assembleDebug        # unsigned debug APK
# or, with RELEASE_STORE_* properties set in local.properties:
./gradlew assembleRelease
```

The built APK is at `Android/app/build/outputs/apk/{debug,release}/`.

### Nginx configuration

```bash
sudo cp Backend/deploy/nginx/security_headers.conf /etc/nginx/bldcms/security_headers.conf
sudo cp Backend/deploy/nginx/bldcms.conf /etc/nginx/sites-available/bldcms.conf
sudo ln -s /etc/nginx/sites-available/bldcms.conf /etc/nginx/sites-enabled/bldcms.conf
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

Edit the `root` directive first to match this server's actual install path.
`Backend/deploy/install_production.sh` automates steps 3–5 above (run as root).

### Gunicorn configuration

`Backend/gunicorn.conf.py` binds to `127.0.0.1:8080` and should not normally need editing — it's
managed entirely by the systemd unit above, never run manually in production.

### emBridge installation

Installed once per Supervisor's own PC from eMudhra's official installer, plus a one-time
`hosts` file entry so the browser resolves `localhost.emudhra.com` to `127.0.0.1`. See
`Docs/EMBRIDGE_INTEGRATION.md`. No backend or Dashboard configuration is required for this.

### Cron backup setup

```bash
sudo bash Backend/scripts/mount_backup_hdd.sh          # one-time: mount a SEPARATE physical disk
BLDCMS_BACKUP_ROOT=/mnt/backup/BL-DCMS bash Backend/scripts/install_backup_cron.sh
```

See `Docs/AUTOMATED_BACKUP_SYSTEM.md` for the full schedule, retention policy, and restore
procedure.

### systemd services

| Service | Manages |
|---|---|
| `bldcms-backend` | Gunicorn (FastAPI backend) |
| `nginx` | Reverse proxy + static Dashboard hosting |
| `postgresql` | Database |

```bash
sudo systemctl status bldcms-backend nginx postgresql
sudo systemctl restart bldcms-backend    # after any env var / code change
sudo systemctl reload nginx              # after any Nginx config change
```

## First Login

1. Open the Dashboard at `http://<this shed's server address>/`.
2. Log in with the bootstrap Administrator account created by `Database/02_bootstrap_seed.sql`:
   - **Employee ID:** `ELSBL_ADMIN`
   - **Password:** `ChangeMe@123`
3. **Change this password immediately** — Dashboard → Users → (this account) → Reset Password.
   This default is documented publicly in this repository precisely so a new install can log in
   at all; leaving it unchanged is a real security risk.

## Initial Configuration Workflow

Once logged in as Administrator:

1. **Settings** — set the shed's organization name and any other site-level defaults.
2. **Sections** — create the maintenance sections this shed operates (e.g. equivalent to
   M2-HR/M4-HR/etc., or your shed's own naming).
3. **Equipment** — create the equipment types maintained in each section.
4. **Checksheet Templates** — either build templates from scratch via the Dashboard's template
   builder, or bulk-load the existing 146-template library — see
   `Database/03_optional_checksheet_template_library.md`.
5. **Locomotives** — register the locomotive fleet this shed maintains.
6. **Users** — create Supervisor and Technician accounts, assigned to the correct Section.
7. Install the Android app on technicians' devices (see "Android build" above) and confirm a
   test checksheet can be filled, submitted, reviewed, and digitally signed end-to-end.

## Troubleshooting

| Symptom | Likely cause | Where to look |
|---|---|---|
| Dashboard loads but shows no data / network errors | Backend not running, or `CORS_ORIGINS`/`DATABASE_URL` misconfigured | `sudo systemctl status bldcms-backend`, `journalctl -u bldcms-backend -f` |
| Refreshing a Dashboard page (e.g. `/users`) shows raw JSON `"Not Authenticated"` instead of the app | Nginx not correctly distinguishing browser navigation from API calls | Confirm `Backend/deploy/nginx/bldcms.conf`'s `Accept: text/html` check is present and Nginx was reloaded after any edit |
| Nginx returns 403 serving the Dashboard | Static `root` path not readable by the `www-data`/Nginx user | See the note in `Backend/deploy/install_production.sh` step 2b |
| Android app can't reach the server | Wrong `API_BASE_URL` baked into the APK, or `cleartextTrafficPermitted` blocking plain HTTP | Rebuild the APK with the correct `local.properties`; check `network_security_config.xml` if using HTTPS |
| OTP never arrives on a technician's device | No SMS/email gateway configured | Set `SHOW_OTP_PLAINTEXT=true` and check the Dashboard's OTP Logs screen (Admin/Supervisor only) |
| Digital signature step fails / emBridge unreachable | emBridge not installed on the Supervisor's PC, or the `hosts` entry is missing | `Docs/EMBRIDGE_INTEGRATION.md` |
| Backend won't start after editing the systemd unit | Syntax error in `Environment=` lines, or `DATABASE_URL` unreachable | `journalctl -u bldcms-backend -n 50`, `sudo systemctl status bldcms-backend` |
| Backups aren't running | Backup destination isn't a separate physical mount, or cron wasn't installed | `Docs/AUTOMATED_BACKUP_SYSTEM.md`, `crontab -l` |

## Frequently Asked Questions

**Do I need internet access for this to work?**
No, for day-to-day operation. The Dashboard, Android app, backend, and database all run entirely
on the shed's local network through Nginx. The one exception is the digital-signature step:
emBridge uses a publicly-registered DNS name (`localhost.emudhra.com`) that resolves to
`127.0.0.1`, which a browser can only validate as HTTPS with a working DNS/internet path the
first time; consult eMudhra's own documentation for offline alternatives if this shed has no
internet connectivity at all.

**Can I change the checksheet templates after going live?**
Yes — Checksheet Templates are edited through the Dashboard (Admin role). Existing
already-submitted checksheets are unaffected; only new checksheets use the updated template.

**Does changing the server's IP address require rebuilding everything?**
No. The Dashboard needs no rebuild (it uses relative URLs against whatever origin served it).
Only the Android app needs a rebuild, because `API_BASE_URL` is compiled into the APK. See
`CHANGE_CONFIGURATION.md` items 1–3.

**Is this distribution copy safe to commit to our own git repository?**
Every known secret has been replaced with a placeholder (see `CHANGE_CONFIGURATION.md`), but
always run your own `grep -r` sweep for anything site-specific before committing, and never
commit the *deployed* copy of `bldcms-backend.service` (under `/etc/systemd/system/`) once real
secrets are filled in — keep those only on the server itself.

**Where do I report bugs or request features for this project going forward?**
This distribution does not include a specific issue tracker configuration — set one up
appropriate to your own organization (see `Docs/PROJECT_STRUCTURE.md` for the codebase layout if
you plan to modify it).
