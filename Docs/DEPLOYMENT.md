# Deployment Guide

This guide covers deploying BL-DCMS at a new Electric Loco Shed as a running production
service, beyond the development setup in `INSTALLATION.md`. It describes the **actual
production topology in use at Electric Loco Shed, BL as of Module 45** — Nginx serving the
Dashboard build and reverse-proxying the API to Gunicorn (Uvicorn workers), both managed by
systemd — not a hypothetical example.

```
Browser / Android app
        │  (port 80)
        ▼
     Nginx  ──────────────► static files: Dashboard/dist/
        │
        │  proxy_pass, 127.0.0.1:8080 only
        ▼
   Gunicorn (4 workers, UvicornWorker) ──► PostgreSQL, storage/pdfs, /mnt/storage (HDD backups)
```

One public entry point (port 80). The backend is never directly reachable from the network —
only Nginx can reach it, on localhost. This is why the Android app's `API_BASE_URL` points at
the Nginx origin (no `:8080`), not at the backend directly, once this deployment is live.

---

## 1. Backend Deployment

### 1.1 Gunicorn (Uvicorn workers)

Configuration lives in `Backend/gunicorn.conf.py` (workers = CPU core count via
`multiprocessing.cpu_count()`, overridable with `GUNICORN_WORKERS`; binds to `127.0.0.1:8080`
only; `preload_app = False` deliberately — see the file's own comments for why preloading would
be unsafe with a module-level SQLAlchemy engine across a fork). Run directly for a one-off
check:

```bash
cd Backend
venv/bin/gunicorn -c gunicorn.conf.py main:app
```

In production this is never run directly — the `bldcms-backend.service` systemd unit owns it
(§3 below).

### 1.2 Nginx

The full site config is `Backend/deploy/nginx/bldcms.conf`, plus a shared
`Backend/deploy/nginx/security_headers.conf` snippet `include`-d into every location block that
also sets its own `Cache-Control` (Nginx's `add_header` inheritance rule stops applying
server-level headers to any location that defines even one `add_header` of its own — the
snippet file exists specifically so this can't silently regress). It covers:

- Reverse proxy for every backend router prefix (`/auth`, `/checksheet`, `/mobile-auth`, etc. —
  see the file for the full list, kept in sync with `Backend/app/api/*.py`)
- Static file serving for `Dashboard/dist/`, with SPA fallback (`try_files ... /index.html`) so
  a hard refresh on a client-side route doesn't 404
- Gzip compression for text-based responses
- Far-future, immutable caching for `Dashboard/dist/assets/` (Vite content-hashes every
  filename, so a changed file always gets a new URL — safe to cache forever) and `no-cache` for
  `index.html` itself
- Security headers (`X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`,
  `Referrer-Policy`, `Permissions-Policy`)

### 1.3 Installing (new host)

```bash
cd Backend
sudo bash deploy/install_production.sh
```

Idempotent — installs Nginx if missing, verifies the Dashboard build exists, grants Nginx
traversal into the project's home directory (a single `chmod o+x` on the home directory only —
see the script's own comments), stops the Vite/Uvicorn dev servers this replaces, installs the
systemd unit and Nginx config, and starts everything. Re-run any time after editing
`gunicorn.conf.py`, `deploy/nginx/bldcms.conf`, or `deploy/systemd/bldcms-backend.service` to
pick up the change (note: if the service is already running, the script does not itself restart
it to pick up new `Environment=` values — run `sudo systemctl restart bldcms-backend`
afterward for those specifically).

### 1.4 Moving to HTTPS (recommended next step, not yet done)

Terminate TLS at Nginx (a `listen 443 ssl` server block, certificate via Let's Encrypt or your
organization's CA) rather than at Gunicorn — Gunicorn stays on plain HTTP on localhost either
way, since that traffic never leaves the host. Once HTTPS is live, tighten the Android app's
network security config (see §3 below) to reject cleartext traffic.

---

## 2. Dashboard Deployment

### 2.1 Build

```bash
cd Backend/../Dashboard
npm run build
```

Leave `VITE_API_BASE_URL` **unset** for this production topology — Nginx serves the Dashboard
and proxies the API on the *same origin*, so the built app's relative-path API calls resolve
correctly with no cross-origin request ever happening (only set this variable if the Dashboard
is ever served from a different origin than its API). Produces `Dashboard/dist/`, which Nginx
serves directly (§1.2/1.3 above) — there is no separate "install" step for the Dashboard beyond
rebuilding it and having Nginx already pointed at that folder.

### 2.2 CORS

`CORS_ORIGINS` (§4 below) matters less under this same-origin topology, since a same-origin
request never triggers a CORS check in the browser at all. It remains set as defense-in-depth
for any client that ever talks to the backend from a different origin.

---

## 3. Systemd Services

| Service | Unit file | Manages |
|---|---|---|
| `bldcms-backend` | `Backend/deploy/systemd/bldcms-backend.service` → `/etc/systemd/system/` | Gunicorn (Uvicorn workers) |
| `nginx` | Ubuntu package unit (`/usr/lib/systemd/system/nginx.service`) | Nginx |

There is deliberately **no** systemd unit for Vite — production has no Vite process at all; the
Dashboard is a static build Nginx serves directly.

```bash
# Status / logs
sudo systemctl status bldcms-backend
journalctl -u bldcms-backend -f          # follow Gunicorn's own operational log
tail -f Backend/logs/application.log     # the application's own structured logs (unchanged
                                          # by this module - still written directly to disk,
                                          # not through the journal)

# Restart after a code or config change
sudo systemctl restart bldcms-backend
sudo nginx -t && sudo systemctl reload nginx   # reload, not restart - Nginx re-reads config
                                                # without dropping in-flight connections
```

Both `bldcms-backend` and `nginx` are `enabled` (start automatically on boot) and configured
with `Restart=always` / `RestartSec=5` (Gunicorn) so a crash or `kill -9` recovers automatically
within a few seconds — confirmed by directly `kill -9`-ing the Gunicorn master process during
Module 45 validation and observing systemd bring it fully back (new PID, all workers rebooted,
application startup complete) well inside the 5-second window.

---

## 4. Android APK Generation

### 4.1 Point the build at your backend

Set `API_BASE_URL` in `Android/local.properties` (see `INSTALLATION.md` §3.3) to your shed's
backend URL before building.

### 4.2 Debug build (internal testing)

```bash
cd BL-DCMS_v1.0/Android
./gradlew assembleDebug
```

Output: `app/build/outputs/apk/debug/app-debug.apk`, signed with the Android debug keystore —
installable via `adb install`, but not suitable for wide distribution.

### 4.3 Release build

Generate a release keystore once (store it somewhere safe — losing it means you can never
update the app under the same signature again):

```bash
keytool -genkeypair -v -keystore bl-dcms-release.jks -alias bl-dcms \
  -keyalg RSA -keysize 2048 -validity 10000
```

Add these four properties to `Android/local.properties` (never commit this file):

```properties
RELEASE_STORE_FILE=/absolute/path/to/bl-dcms-release.jks
RELEASE_STORE_PASSWORD=your-store-password
RELEASE_KEY_ALIAS=bl-dcms
RELEASE_KEY_PASSWORD=your-key-password
```

Then build:

```bash
./gradlew assembleRelease
```

Output: `app/build/outputs/apk/release/app-release.apk` — signed and ready to distribute if all
four properties above were present; otherwise an unsigned APK is produced (build still
succeeds either way). Bump `versionCode`/`versionName` in `Android/app/build.gradle.kts` for
every release.

### 4.4 Network security (HTTPS backends)

If your backend is served over HTTPS, tighten
`Android/app/src/main/res/xml/network_security_config.xml` to your production host with
`cleartextTrafficPermitted="false"`. The default configuration permits cleartext HTTP, matching
a plain-HTTP backend during initial setup.

### 4.5 Distributing the APK

Install directly via `adb install -r app-release.apk`, distribute the file through your shed's
internal MDM/file-sharing mechanism, or host it for direct download from an internal server —
BL-DCMS does not currently publish to the Play Store.

---

## 5. Environment Variables (Backend)

| Variable | Required | Default (development only) | Purpose |
|---|---|---|---|
| `DATABASE_URL` | Yes, in production | `postgresql://YOUR_DB_USER:YOUR_DB_PASSWORD@localhost:5432/rdcms` | PostgreSQL connection string |
| `JWT_SECRET_KEY` | Yes, in production | `CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_KEY` | Signs/verifies session JWTs. Generate with `openssl rand -hex 32`. **Every shed must set its own value** — two sites sharing a secret could forge each other's tokens. |
| `CORS_ORIGINS` | Yes, in production | `http://YOUR_SERVER_IP:3000,http://localhost:3000` | Comma-separated list of origins allowed to call the API from a browser. Under the Module 45 same-origin Nginx topology this is defense-in-depth rather than load-bearing — set to `http://<shed-host>,http://localhost` (no port; matches Nginx's port 80). |
| `DEBUG` | No | `true` | Controls verbose/debug-only logging and OTP-log plaintext capture. Set to `false` in production. |
| `BLDCMS_ADMIN_ALLOWED_CIDRS` | No | RFC1918 private ranges | Comma-separated CIDR ranges the System Administration CLI treats as "internal" when invoked over SSH — see `Backend/docs/ADMIN_CLI.md` |

The defaults above match this release's own development environment and exist so the backend
still runs out of the box for local evaluation — **do not deploy to production without setting
`DATABASE_URL`, `JWT_SECRET_KEY`, and `CORS_ORIGINS` explicitly.**

## 6. Required Ports

| Port | Service | Exposure |
|---|---|---|
| 80 | Nginx — Dashboard + API reverse proxy (the one public entry point) | Internal network / VPN. Both the Dashboard browser and the Android app use this port. |
| 8080 | Gunicorn (Uvicorn workers) | **`127.0.0.1` only** — confirmed via `ss -tlnp`; never reachable from another host, by design (`bind = "127.0.0.1:8080"` in `gunicorn.conf.py`) |
| 3000 | Dashboard dev server (`npm run dev`) | Development only — not used in production; no systemd unit exists for it |
| 5432 | PostgreSQL | Localhost or internal network only — never expose to the internet |
| 26769 | eMudhra emBridge (on the Supervisor's own machine, not the server) | Localhost only, used by the Dashboard's digital-signature flow — see `Backend/docs/EMBRIDGE_INTEGRATION.md` |
| 22 | SSH (for `bldcms-admin` CLI access) | Internal network only |

## 7. Firewall Requirements

- Allow inbound to port 80 (Nginx) from wherever the Dashboard browser and Android devices
  operate — typically the shed's internal network, or a VPN. This is the only port that needs
  to be reachable from another host for the application to function.
- **Do not open port 8080** to anything beyond localhost — Gunicorn only binds there, so an
  external firewall rule for it is not just unnecessary but would have no effect (nothing is
  listening on the external interface for that port) unless the bind address is changed, which
  should not be done without also reintroducing a reason to (there isn't one — Nginx already
  handles every legitimate client).
- **Do not expose PostgreSQL (5432) beyond localhost/the backend host.**
- Restrict SSH (22) to the internal network or a VPN — this is also the access path for the
  System Administration CLI (`bldcms-admin`), which relies on SSH/console authentication rather
  than its own login system (see `Backend/docs/ADMIN_CLI.md`).
- eMudhra emBridge (26769) runs locally on each Supervisor's own workstation for the DSC
  signing flow — it is never exposed on the server and requires no firewall rule on the
  backend host.

---

## 8. Rollback Procedure

If the Nginx/Gunicorn production deployment needs to be backed out — a bad config push, an
unexpected regression, or just to compare behavior against the old setup — the previous
standalone dev-server topology can be restored without losing any data (the database,
`storage/pdfs/`, and the HDD backups are untouched by any of this; only how the app is *served*
changes).

### 8.1 Stop the new services

```bash
sudo systemctl stop bldcms-backend nginx
sudo systemctl disable bldcms-backend nginx
```

### 8.2 Run the previous dev-server setup

```bash
# Backend
cd Backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8080 &

# Dashboard
cd ../Dashboard
npm run dev
```

The Dashboard dev server proxies API calls to `localhost:8080` itself (see `vite.config.ts`),
so no other configuration is needed to get back to exactly the pre-Module-45 state.

### 8.3 Revert the Android app (if it was rebuilt against Nginx)

Change `Android/local.properties` back to:

```properties
API_BASE_URL=http://YOUR_SERVER_IP:8080/
```

and rebuild (`./gradlew assembleDebug`) — only needed if a build using the Nginx-origin URL was
already distributed to devices; the source `local.properties` change alone doesn't affect
already-installed APKs.

### 8.4 Partial rollback (keep Nginx/Gunicorn, undo one config change)

More commonly useful than a full rollback — since every production config file lives in
`Backend/deploy/` and `Backend/gunicorn.conf.py`, none of it in `/etc/` directly:

```bash
git diff Backend/gunicorn.conf.py Backend/deploy/          # see exactly what changed
git checkout -- Backend/gunicorn.conf.py Backend/deploy/   # revert to the last committed version
sudo bash Backend/deploy/install_production.sh              # re-apply the reverted config
```

### 8.5 Restoring from a full disaster (host lost entirely)

Follow `Documentation/AUTOMATED_BACKUP_SYSTEM.md` §8.4 (Full Application Recovery) to restore
the database, source trees, and configuration from the most recent Weekly/Monthly backup on the
HDD, then follow this guide from §1 to redeploy.
