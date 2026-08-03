# BL-DCMS Deployment & Site Migration Configuration Guide

**Single source of truth for every configurable parameter required to deploy BL-DCMS to a new
Electric Loco Shed, or migrate an existing deployment to a new server.**

This document describes the actual production topology in use at Electric Loco Shed, BL as of
Module 46 — not a hypothetical example. It complements, but does not replace, the narrative
guides already in this folder (`INSTALLATION.md`, `DEPLOYMENT.md`, `AUTOMATED_BACKUP_SYSTEM.md`,
`BACKUP_AND_RESTORE.md`): those explain *how* to perform an install/backup/restore step by step;
this document is the **configuration reference** — every file, every setting, every value that
changes when the environment changes, indexed so a new shed's IT staff can find "what do I edit"
without reading source code.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Network Parameters](#2-network-parameters)
3. [React Dashboard](#3-react-dashboard)
4. [Android](#4-android)
5. [Backend](#5-backend)
6. [Database](#6-database)
7. [Nginx](#7-nginx)
8. [Gunicorn](#8-gunicorn)
9. [Android Release — When to Rebuild What](#9-android-release--when-to-rebuild-what)
10. [SSL](#10-ssl)
11. [emBridge](#11-embridge)
12. [PostgreSQL](#12-postgresql)
13. [Backup System](#13-backup-system)
14. [systemd Services](#14-systemd-services)
15. [Deploying to Another Shed — Checklist](#15-deploying-to-another-shed--checklist)
16. [Future Configuration Matrix](#16-future-configuration-matrix)
17. [Verification — Hardcoded Value Sweep](#17-verification--hardcoded-value-sweep)
18. [Deliverables Summary](#18-deliverables-summary)

---

## 1. Architecture Overview

```
                         ┌─────────────────────┐
                         │     Android App      │
                         │  (Technician, LAN)    │
                         └──────────┬───────────┘
                                    │  HTTP, port 80
                                    ▼
┌──────────────────────────────────────────────────────────────┐
│                             Nginx                              │
│                  (single public entry point, :80)               │
│                                                                  │
│   static files ◄───────────────┐        ┌──────────► /auth,     │
│   Dashboard/dist/                │        │            /checksheet,│
│   (React SPA, incl. SPA fallback)│        │            /templates, │
│                                   │        │            /users, ... │
└───────────────┬───────────────────────────┴────────────┬────────┘
                │  (browser loads the                     │  proxy_pass
                │   Dashboard bundle)                       │  127.0.0.1:8080 only
                ▼                                          ▼
     ┌─────────────────────┐                    ┌─────────────────────┐
     │   Dashboard (React)   │  same-origin       │      Gunicorn         │
     │   axios calls to        │  relative fetch    │  (Uvicorn workers)    │
     │   relative paths          │ ───────────────►  │  bind 127.0.0.1:8080  │
     └─────────────────────┘                    └──────────┬──────────┘
                                                             │
                                                             ▼
                                                   ┌─────────────────────┐
                                                   │       FastAPI          │
                                                   │   (app/main.py routers) │
                                                   └──────────┬──────────┘
                                          ┌──────────────────┼──────────────────┐
                                          ▼                  ▼                  ▼
                                ┌─────────────────┐ ┌────────────────┐ ┌─────────────────┐
                                │   PostgreSQL       │ │  storage/pdfs/    │ │  backend/logs/      │
                                │   (rdcms database)  │ │  (generated PDFs)  │ │  (application logs)   │
                                └─────────────────┘ └────────────────┘ └─────────────────┘
                                          │
                                          ▼
                                ┌───────────────────────────┐
                                │   Backup System (cron)       │
                                │   → /mnt/storage/BL-DCMS      │
                                │   (separate physical HDD)      │
                                │   Daily / Weekly / Monthly      │
                                └───────────────────────────┘

     ┌─────────────────────┐
     │  Supervisor's own PC   │
     │  (Dashboard, browser)   │
     └──────────┬───────────┘
                │  HTTPS, direct browser→localhost call
                │  (never through Nginx/Gunicorn)
                ▼
     ┌─────────────────────┐
     │  emBridge (eMudhra)    │
     │  local Windows service  │
     │  https://localhost.       │
     │  emudhra.com:26769        │
     └──────────┬───────────┘
                ▼
     ┌─────────────────────┐
     │  USB DSC Token          │
     │  → Digital Signature     │
     └─────────────────────┘
```

### Communication paths, explained

| # | Path | Protocol | Notes |
|---|---|---|---|
| 1 | Android App → Nginx | HTTP, port 80 | The app never talks to Gunicorn directly. `API_BASE_URL` in the APK is the Nginx origin, no port suffix. |
| 2 | Browser → Nginx (Dashboard) | HTTP, port 80 | Nginx serves the static `Dashboard/dist/` build; `try_files ... /index.html` gives client-side routing (React Router) a working hard-refresh. |
| 3 | Dashboard (browser JS) → Nginx (`/api` paths) | HTTP, same-origin | Axios calls are **relative paths** (`/sections/`, `/checksheet/`, …) resolved against `window.location.origin` — never a hardcoded host. Same-origin means the browser never triggers a CORS preflight for this traffic at all. |
| 4 | Nginx → Gunicorn | HTTP, `127.0.0.1:8080` | `proxy_pass` only; Gunicorn's bind address is loopback-only and never reachable from another host. |
| 5 | Gunicorn → FastAPI | In-process | `worker_class = uvicorn.workers.UvicornWorker`; Gunicorn manages worker processes, each running the FastAPI ASGI app. |
| 6 | FastAPI → PostgreSQL | TCP, `localhost:5432` (default) | Via `DATABASE_URL`. Never exposed beyond the backend host in production. |
| 7 | FastAPI → `storage/pdfs/` | Local filesystem | Generated/signed checksheet PDFs, referenced by `checksheet_header.pdf_path`. |
| 8 | FastAPI → `backend/logs/` | Local filesystem | Structured application logs (`app/core/logging.py`), independent of Gunicorn's own stdout/stderr log (captured by systemd/journald). |
| 9 | Backup System (cron) → `/mnt/storage/BL-DCMS` | Local filesystem, separate physical disk | Daily/Weekly/Monthly tiers; refuses to run if the destination isn't actually a separate mount. |
| 10 | Supervisor's browser → emBridge | HTTPS, `https://localhost.emudhra.com:26769` | **Bypasses Nginx and the backend entirely.** A direct browser-to-localhost call on the Supervisor's own PC, using eMudhra's publicly-registered DNS name that resolves to `127.0.0.1` (lets the browser get a validly-certificated HTTPS connection to a local service without a self-signed-cert warning). Requires a one-time `hosts` file entry per eMudhra's own installer. |
| 11 | emBridge → USB DSC Token | Local USB/driver | Never touches the network at all. |

---

## 2. Network Parameters

### Current deployment (Electric Loco Shed, BL)

| Parameter | Current value | Configured in |
|---|---|---|
| Server IP | `YOUR_SERVER_IP` | Referenced in `Android/local.properties`, `Dashboard/.env` (commented default), `backend` fallback strings |
| Dashboard URL | `http://YOUR_SERVER_IP/` | Same origin as API — no separate URL |
| API URL | `http://YOUR_SERVER_IP/` (same origin, proxied via Nginx) | N/A — Dashboard uses relative paths; Android uses `API_BASE_URL` |
| Android Base URL | `http://YOUR_SERVER_IP/` | `Android/local.properties` → `API_BASE_URL` |
| Gunicorn bind | `127.0.0.1:8080` | `backend/gunicorn.conf.py` |
| Nginx listen | `0.0.0.0:80` (`server_name _;` — catch-all) | `/etc/nginx/sites-enabled/bldcms.conf` (deployed from `backend/deploy/nginx/bldcms.conf`) |
| PostgreSQL | `localhost:5432`, database `rdcms`, user `YOUR_DB_USER` | `DATABASE_URL` env var |
| SSH | Port 22, internal network only | OS-level, not application-configured |

### What must change when the server IP moves (e.g. `192.168.x.x` → `10.x.x.x`)

| File | What to change | Why |
|---|---|---|
| `Android/local.properties` | `API_BASE_URL=http://<new-ip>/` | Baked into the APK at build time — **requires an APK rebuild**, editing this file alone does nothing to already-installed devices. |
| `Dashboard/.env` | Leave `VITE_API_BASE_URL` **unset/commented** — no change needed under the same-origin Nginx topology | The Dashboard resolves its API calls against whatever origin the browser used to load the page; it never needs to know the IP in advance. Only set this variable if the Dashboard is ever served from a *different* origin than its API (not the case here). |
| `backend/deploy/systemd/bldcms-backend.service` (→ `/etc/systemd/system/`) | `CORS_ORIGINS=http://<new-ip>,http://localhost` | Defense-in-depth; same-origin requests never trigger a CORS check, but this should still match reality. |
| Nginx | No file change needed | `server_name _;` is already a catch-all — it matches any Host header, so an IP change requires no Nginx edit at all. |
| `backend/main.py` `_default_origins` fallback | Only relevant if `CORS_ORIGINS` is left unset (development only) | Production always sets `CORS_ORIGINS` explicitly via the systemd unit; this fallback string is a dev convenience only. |
| DNS / router / switch | Point the new IP at the same physical host | Outside the application's scope — a network/infra change, not a code change. |

After any of the above: `sudo systemctl restart bldcms-backend` (to pick up the new
`CORS_ORIGINS`) and rebuild+redistribute the Android APK. **The Dashboard itself needs no
rebuild for an IP change** — this is the single most common point of confusion, worth
highlighting: Dashboard = no rebuild; Android = rebuild required.

---

## 3. React Dashboard

| Setting | Current location | Purpose | Example before | Example after |
|---|---|---|---|---|
| API base URL override | `Dashboard/.env` → `VITE_API_BASE_URL` | If set, axios uses this absolute URL instead of relative paths. **Leave unset in the standard same-origin Nginx topology.** | `# VITE_API_BASE_URL=http://YOUR_SERVER_IP:8080` (commented out = unset) | Only uncomment if the Dashboard is served from a different origin than the API, e.g. `VITE_API_BASE_URL=http://YOUR_SERVER_IP` for a split deployment |
| Axios instance | `Dashboard/src/api/client.ts` (`getApiBaseUrl()`) | Reads `VITE_API_BASE_URL`; returns `''` (relative) if unset, so `axios.create({ baseURL: undefined })` resolves every call against `window.location.origin` | N/A — logic, not a value to edit | N/A |
| Every actual API call | `Dashboard/src/services/apiService.ts` | All ~40 endpoints called as bare relative paths (`/sections/`, `/checksheet/`, `/templates/`, …) — never edited per-deployment | `api.get('/sections/')` | No change needed across environments |
| Vite dev-server proxy | `Dashboard/vite.config.ts` (`server.proxy`) | **Development only** (`npm run dev`); never runs in `vite build`/production. Proxies `/auth`, `/checksheet`, etc. to `API_TARGET` (defaults to `http://localhost:8080`) so `npm run dev` can talk to a locally-running backend without CORS. | `const API_TARGET = env.VITE_API_BASE_URL \|\| 'http://localhost:8080'` | Set `VITE_API_BASE_URL` in `.env` before running `npm run dev` if the backend isn't on `localhost:8080` |
| Nginx proxy usage | `backend/deploy/nginx/bldcms.conf` | Reverse-proxies every backend router prefix to Gunicorn; serves `Dashboard/dist/` as static files with SPA fallback | `proxy_pass http://127.0.0.1:8080;` | No change for an IP/domain move — only changes if Gunicorn's bind address changes |
| Build output | `Dashboard/dist/` (built via `npm run build`) | What Nginx actually serves — must be rebuilt after *any* Dashboard source change, but not for a server IP/network change | `npm run build` | Same command, run again after any `src/` change |

**Key takeaway:** the Dashboard is deliberately built to need **zero rebuild** for a server IP,
domain, or network change, as long as it's still served same-origin with the API through
Nginx. A rebuild is only required for actual source code changes (new features, bug fixes).

---

## 4. Android

| Concern | File | Current value | Rebuild required? |
|---|---|---|---|
| Server IP / API Base URL (login, all data, uploads, PDFs, images — every network call shares one base) | `Android/local.properties` → `API_BASE_URL` | `http://YOUR_SERVER_IP/` | **Yes** |
| Build-time fallback default (used only if `local.properties` has no `API_BASE_URL`) | `Android/app/build.gradle.kts` line 19 | `"http://YOUR_SERVER_IP:8080/"` | Yes, if this fallback itself needs to change for a fresh checkout with no `local.properties` yet |
| Cleartext HTTP policy | `Android/app/src/main/res/xml/network_security_config.xml` | `cleartextTrafficPermitted="true"` (matches a plain-HTTP LAN backend) | Yes — must flip to `false` and scope to the production HTTPS host once TLS is live (see §10) |
| Release signing | `Android/local.properties` → `RELEASE_STORE_FILE`, `RELEASE_STORE_PASSWORD`, `RELEASE_KEY_ALIAS`, `RELEASE_KEY_PASSWORD` | Not set by default (produces an unsigned APK) | Only affects release builds' signature, not connectivity |
| Version tracking | `Android/app/build.gradle.kts` → `versionCode`, `versionName` | `1` / `"1.0"` | Bump on every release build so devices can be told an update exists |

There is **exactly one** network configuration surface in the Android app: every login call,
data fetch, PDF download, and (if ever added) image/file upload goes through the single Retrofit
`Retrofit.Builder().baseUrl(BuildConfig.API_BASE_URL)` in `Android/app/src/main/java/com/checksheet/android/di/NetworkModule.kt`, and `BuildConfig.API_BASE_URL` is compiled in from
`local.properties` at build time via `app/build.gradle.kts`'s `buildConfigField`. There is no
second hardcoded URL anywhere else in the Android source tree (confirmed by the sweep in §17).

### Why a rebuild is unavoidable for a URL change

`API_BASE_URL` is injected via `buildConfigField("String", "API_BASE_URL", ...)` — a **compile-time
constant**, not something read from a config file at runtime. Editing `local.properties` on the
build machine changes what the *next* build produces; it has zero effect on APKs already
installed on technicians' devices. There is currently no remote-config or environment-variable
mechanism for this value at runtime (see §16 recommendations).

---

## 5. Backend

### Environment variables

| Variable | Required in production | Dev default | Purpose |
|---|---|---|---|
| `DATABASE_URL` | **Yes** | `postgresql://YOUR_DB_USER:YOUR_DB_PASSWORD@localhost:5432/rdcms` | PostgreSQL connection string (`app/database/database.py`) |
| `JWT_SECRET_KEY` | **Yes** | `CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_KEY` | Signs/verifies session JWTs (`app/security/jwt.py`). **Every shed must generate its own** (`openssl rand -hex 32`) — sharing a secret across sites lets one forge the other's tokens. |
| `CORS_ORIGINS` | **Yes** | `http://YOUR_SERVER_IP:3000,http://localhost:3000` (dev fallback in `main.py`) | Comma-separated allowed browser origins. Defense-in-depth under the same-origin Nginx topology. |
| `DEBUG` | No | `true` | Controls log verbosity (`app/core/logging.py`) only — **not** a general "safe mode" flag. |
| `SHOW_OTP_PLAINTEXT` | No | Defaults to `DEBUG`'s value | Independent of `DEBUG` — controls whether the OTP Logs admin screen can display a technician's plaintext OTP (`app/services/otp_service.py`). This shed has no SMS gateway, so it must be `true` in production here; a future shed with a real SMS/email OTP delivery channel should set it `false`. |
| `BLDCMS_ADMIN_ALLOWED_CIDRS` | No | RFC1918 private ranges | CIDR ranges the System Administration CLI treats as "internal" over SSH (`backend/docs/ADMIN_CLI.md`) |
| `BLDCMS_BACKUP_ROOT` | No | `/mnt/storage/BL-DCMS` | Backup destination root (§13) |
| `GUNICORN_WORKERS` | No | CPU core count | Override Gunicorn's worker count |

All of the above are set via `Environment=` lines in
`backend/deploy/systemd/bldcms-backend.service` (deployed to `/etc/systemd/system/`) — **never**
edit `gunicorn.conf.py`, `main.py`, or `app/database/database.py` themselves per-deployment; the
dev-default values baked into those files exist only so the app runs out of the box for local
evaluation.

### Storage locations (all local filesystem, backend host)

| What | Path | Configurable via |
|---|---|---|
| Application logs | `backend/logs/*.log` | Fixed relative path — not currently an env var (see §16) |
| Backup cron log | `backend/logs/backup_cron.log` | Same |
| Signed/generated PDFs | `backend/storage/pdfs/` | `PdfService.__init__(output_dir=...)`, defaults to this path; not currently overridden by an env var in production |
| Automated backups (separate HDD) | `/mnt/storage/BL-DCMS` | `BLDCMS_BACKUP_ROOT` env var |
| PostgreSQL data | Managed by the OS PostgreSQL installation, not this repo | `postgresql.conf` (outside this project's scope) |

### CORS / Allowed Hosts

`CORS_ORIGINS` is the only origin-allowlisting the backend does. There is no separate "allowed
hosts" middleware distinct from this — FastAPI/Starlette's `CORSMiddleware` (`main.py`) is the
single point of control.

---

## 6. Database

| Item | Current value | Where |
|---|---|---|
| Database name | `rdcms` | `DATABASE_URL` |
| Database user | `YOUR_DB_USER` | `DATABASE_URL` |
| Password | Stored **only** inside `DATABASE_URL` in the systemd unit's `Environment=` line — never committed to the repo, never in plaintext in any tracked file | `/etc/systemd/system/bldcms-backend.service` (not `backend/deploy/systemd/...` — that tracked copy should have a placeholder, not the real password) |
| Connection string format | `postgresql://<user>:<url-encoded-password>@<host>:<port>/<dbname>` | e.g. `postgresql://YOUR_DB_USER:YOUR_DB_PASSWORD@localhost:5432/rdcms` (`%40`=`@`, `%23`=`#` — URL-encode any special character in the password) |
| Migration process | No formal migration framework (e.g. Alembic) is currently in place — schema changes are applied via direct SQL / seed scripts under `backend/scripts/` | See §16 recommendations — this is a real gap for multi-site deployment |
| Backup/restore procedure | See `Documentation/BACKUP_AND_RESTORE.md` (manual, on-demand) and `Documentation/AUTOMATED_BACKUP_SYSTEM.md` §8 (scheduled, HDD-based) | `pg_dump`/`pg_restore` under the hood, via `bldcms-admin backup` or the automated cron system |

### Changing the database host (e.g. moving PostgreSQL to its own server)

1. Update `DATABASE_URL`'s host/port in the systemd unit.
2. Ensure PostgreSQL's `pg_hba.conf`/`postgresql.conf` on the new host accept connections from
   the backend host's IP (never expose 5432 beyond that).
3. `sudo systemctl restart bldcms-backend`.
4. No Nginx, Gunicorn, Dashboard, or Android change needed — the database host is entirely
   backend-internal.

---

## 7. Nginx

Config: `backend/deploy/nginx/bldcms.conf` (source of truth) → deployed to
`/etc/nginx/sites-available/bldcms.conf`, symlinked into `/etc/nginx/sites-enabled/`. Shared
security-header snippet: `backend/deploy/nginx/security_headers.conf`.

| Directive | Current value | What changes it |
|---|---|---|
| `server_name` | `_` (catch-all — matches any Host header) | **Only needs to change if you switch from a catch-all to a specific domain**, e.g. `server_name bldcms.example.com;` once a real domain is in use. An IP change alone needs no edit here. |
| `listen` | `80 default_server;` / `[::]:80 default_server;` | Add a `listen 443 ssl;` block when moving to HTTPS (§10) — the existing `80` block can then either redirect to 443 or stay for LAN-only HTTP access. |
| `proxy_pass` (API routes) | `http://127.0.0.1:8080` (×2 — API router prefixes, and `/docs`/`/redoc`/`/openapi.json`) | Only changes if Gunicorn's bind address/port changes in `gunicorn.conf.py` — keep both in sync. |
| Static files | `root /opt/bldcms/Dashboard/dist;` | **Must be an absolute path matching the actual deployment location** — will differ on a fresh host if the project isn't checked out to the identical path. |
| SSL | Not configured (plain HTTP only, as of this module) | See §10. |
| Dashboard routing (SPA fallback) | `location / { try_files $uri $uri/ /index.html; }` | No change needed for IP/domain moves. |
| API proxy path list | Explicit regex of every backend router prefix (`auth`, `sections`, `checksheet`, …) | Only needs updating if a **new top-level API router** is added to `backend/app/api/` — keep this list in sync with `main.py`'s `include_router` calls. |

### What changes when the IP/domain changes

- **IP change only** (LAN address moves, same catch-all `server_name _`): **no Nginx file change
  needed.**
- **Domain name adopted** (e.g. `bldcms.shedname.internal`): update `server_name` to the real
  domain (or keep `_` if you want it to keep responding to both the IP and the domain).
- **Root path changes** (project checked out to a different directory): update the `root`
  directive to match.
- After any Nginx config edit: `sudo nginx -t && sudo systemctl reload nginx` (reload, not
  restart — avoids dropping in-flight connections).

---

## 8. Gunicorn

Config: `backend/gunicorn.conf.py`. Managed by the `bldcms-backend` systemd service — never run
manually in production.

| Setting | Current value | Purpose |
|---|---|---|
| `bind` | `127.0.0.1:8080` | Loopback-only — never expose to `0.0.0.0` in production; Nginx is the only intended caller. |
| `workers` | `multiprocessing.cpu_count()` (overridable via `GUNICORN_WORKERS`) | One worker per CPU core — `UvicornWorker` is async, so this scales for CPU-bound work (PDF generation, signature verification), not raw request volume. |
| `worker_class` | `uvicorn.workers.UvicornWorker` | Runs the FastAPI ASGI app inside each Gunicorn worker. |
| `timeout` | `60` seconds | Generous margin for PDF generation / digital-signature verification, which do real CPU work rather than just proxying. |
| `graceful_timeout` | `30` seconds | Time given to in-flight requests to finish during a restart before being killed. |
| `max_requests` / `max_requests_jitter` | `1000` / `100` | Recycles each worker periodically as a defense against slow memory growth; jittered so workers don't all recycle simultaneously. |
| `preload_app` | `False` (deliberately) | Prevents every worker from inheriting the same forked SQLAlchemy engine/connection pool — each worker gets its own. |

### systemd unit

`backend/deploy/systemd/bldcms-backend.service` (source of truth) → `/etc/systemd/system/`.

| Field | Current value |
|---|---|
| `WorkingDirectory` | `/opt/bldcms/Backend` |
| `ExecStart` | `/opt/bldcms/Backend/venv/bin/gunicorn -c gunicorn.conf.py main:app` |
| `Restart` | `always`, `RestartSec=5` |
| `User`/`Group` | `CHANGE_ME_USER` / `CHANGE_ME_USER` |
| Environment | `DATABASE_URL`, `JWT_SECRET_KEY`, `CORS_ORIGINS`, `DEBUG`, `SHOW_OTP_PLAINTEXT` (all via `Environment=` lines — see §5) |

Both `WorkingDirectory` and the venv path inside `ExecStart` are **absolute paths tied to this
specific host's checkout location** — a fresh deployment to a different path (or a different
Linux username) requires editing this file before installing it.

---

## 9. Android Release — When to Rebuild What

| Change | APK rebuild needed? | Backend restart enough? | Dashboard rebuild enough? |
|---|---|---|---|
| Server IP / domain change | **Yes** | — | — |
| Backend code change (new endpoint, bug fix, validation logic) | No (unless the API contract itself changed) | **Yes** | No |
| Dashboard UI/logic change | No | No | **Yes** |
| New checksheet template / field | No | No (data-only, no code) | No (data-only, no code) |
| `JWT_SECRET_KEY` / `CORS_ORIGINS` / any backend env var | No | **Yes** | No |
| Android UI/logic change (new screen, bug fix not touching networking) | **Yes** | No | No |
| Nginx config change | No | No — `sudo systemctl reload nginx` | No |
| TLS/HTTPS adopted | **Yes** (network security config + base URL scheme) | Yes (Nginx SSL config) | No |
| Digital signature / emBridge behavior change | No (Dashboard-only, browser talks to emBridge directly) | No | Possibly, if the Dashboard-side emBridge client changed |

---

## 10. SSL

**Current state: no SSL/TLS anywhere in this deployment.** Nginx listens on plain HTTP (port
80) only; Gunicorn is plain HTTP on loopback. This is intentional for the current closed-LAN,
single-shed topology, not an oversight — documented explicitly so a future migrator doesn't
assume HTTPS is already handled.

| Scenario | Approach |
|---|---|
| **Self-signed** | Not currently used. Would require distributing the self-signed CA/cert to every Android device and every Dashboard browser to avoid trust warnings — impractical at shed scale; not recommended over the LAN-only option below. |
| **Local LAN (current)** | Plain HTTP is acceptable given the network is a closed, physically-controlled shed LAN with no internet exposure — this is the deliberate current choice, not a placeholder. |
| **Future public deployment** | Terminate TLS at Nginx (`listen 443 ssl;` + a real certificate — Let's Encrypt if the host has a public domain and internet access, or the organization's internal CA for a private/VPN deployment). Gunicorn stays plain HTTP on loopback either way — that traffic never leaves the host. After enabling: flip `Android/app/src/main/res/xml/network_security_config.xml` to `cleartextTrafficPermitted="false"`, scoped to the production HTTPS host, and rebuild the APK; change `API_BASE_URL` to `https://...`. |
| **Certificate renewal** | Only relevant once HTTPS is adopted. Let's Encrypt certificates auto-renew via `certbot`'s own systemd timer (not currently installed — would be added at that time). An internal-CA certificate's renewal cadence is whatever that CA issues. |

**Note:** emBridge's own connection (`https://localhost.emudhra.com:26769`) already uses HTTPS
today, independent of the rest of this deployment — that's eMudhra's own service running on each
Supervisor's PC, not something this project's SSL configuration touches (§11).

---

## 11. emBridge

emBridge is eMudhra's local Windows signing service — it runs **on each Supervisor's own PC**,
not on the BL-DCMS server, and the Dashboard's browser JavaScript talks to it directly.

| Item | Detail |
|---|---|
| Local installation | Installed once per Supervisor PC from eMudhra's own installer (`https://embridge.emudhra.com/`) — outside this repo's scope |
| Supervisor PC setup | One-time `hosts` file entry (`127.0.0.1 localhost.emudhra.com`) so the browser resolves eMudhra's public DNS name to the local service, per eMudhra's Troubleshooting Guide |
| Port | `26769`, localhost-only on the Supervisor's own PC |
| Firewall | No inbound rule needed on the BL-DCMS server — emBridge is never reached from the server side at all. Outbound from the Supervisor's PC to `localhost:26769` is local loopback traffic, not subject to network firewall rules. |
| **Backend configuration required** | **None.** This is worth stating explicitly since it's the one integration in this whole system that the backend has zero involvement in — the Dashboard (`Dashboard/src/services/embridgeClient.ts`) talks to emBridge, then separately sends the resulting signed payload to the backend's own digital-signature endpoints. A new shed deploying BL-DCMS needs emBridge installed on Supervisor PCs, but never needs to touch `backend/` for it. |

---

## 12. PostgreSQL

| Task | Command / procedure |
|---|---|
| Backup (manual, on-demand) | `bldcms-admin backup` — see `Documentation/BACKUP_AND_RESTORE.md` |
| Backup (automated, scheduled) | Cron-driven, writes to a separate HDD — see §13 and `Documentation/AUTOMATED_BACKUP_SYSTEM.md` |
| Restore | `Documentation/AUTOMATED_BACKUP_SYSTEM.md` §8.1 (stop backend first — it must not write during a restore), verify the `.sha256` sidecar before restoring |
| Migration (schema changes) | No formal migration tool in place — see §16. Currently: apply SQL/seed scripts under `backend/scripts/` manually against the target database. |
| Changing DB host | Update `DATABASE_URL`'s host in the systemd unit; ensure the new PostgreSQL host's `pg_hba.conf` permits the backend host's IP; restart `bldcms-backend` (§6) |
| Changing credentials | `ALTER ROLE YOUR_DB_USER WITH PASSWORD '...'` in `psql`, then update `DATABASE_URL` in the systemd unit (URL-encode any special characters — `@`→`%40`, `#`→`%23`, etc.), then `sudo systemctl restart bldcms-backend` |

Initial setup (fresh host):
```sql
CREATE ROLE YOUR_DB_USER WITH LOGIN PASSWORD 'change-this-password';
CREATE DATABASE rdcms OWNER YOUR_DB_USER;
```
(see `Documentation/INSTALLATION.md` for the full sequence including extensions/permissions).

---

## 13. Backup System

Full detail: `Documentation/AUTOMATED_BACKUP_SYSTEM.md`. Summary for this guide:

| Item | Value |
|---|---|
| Storage | A **separate physical disk** from the application SSD — currently `/dev/sda` (ext4) mounted at `/mnt/storage` on this host. The system actively refuses to treat a same-filesystem path as valid. |
| Destination root | `/mnt/storage/BL-DCMS` (configurable via `BLDCMS_BACKUP_ROOT`) |
| Cron schedule | Daily 02:00 (DB + PDFs + logs + config), Weekly 02:30 Sunday (full source + DB snapshot), Monthly 03:00 on the 1st (same as Weekly, longer retention) |
| Retention | Daily: newest 7. Weekly: newest 4. Monthly: newest 12 (rolling one-year archive). Pruning only runs after a successful backup of that tier. |
| Verification | `venv/bin/python -m app.backup_system.run verify` — exercises every step against synthetic data, exit code 0/1 |
| Restoration | See `AUTOMATED_BACKUP_SYSTEM.md` §8 — always `sha256sum -c` the archive first |
| One-time mount setup (new host) | `sudo bash backend/scripts/mount_backup_hdd.sh` |
| Installing the cron schedule (new host) | `BLDCMS_BACKUP_ROOT=/mnt/storage/BL-DCMS bash backend/scripts/install_backup_cron.sh` (verifies the destination first, refuses to install if verification fails) |

---

## 14. systemd Services

| Service | Unit file (source) | Deployed to | Manages |
|---|---|---|---|
| `bldcms-backend` | `backend/deploy/systemd/bldcms-backend.service` | `/etc/systemd/system/` | Gunicorn (Uvicorn workers running FastAPI) |
| `nginx` | Ubuntu package unit | `/usr/lib/systemd/system/nginx.service` | Nginx |
| `postgresql` | PostgreSQL package unit | OS-managed | PostgreSQL server |
| Backup timers | **cron**, not systemd timers | User crontab (installed by `install_backup_cron.sh`) | Daily/Weekly/Monthly backup runs |

There is deliberately **no** systemd unit for Vite or Uvicorn's dev server — production has no
dev-server process at all.

### Common operations

```bash
# Status
sudo systemctl status bldcms-backend
sudo systemctl status nginx
sudo systemctl status postgresql

# Start / Stop / Restart
sudo systemctl start   bldcms-backend
sudo systemctl stop    bldcms-backend
sudo systemctl restart bldcms-backend      # after any code or Environment= change

# Reload (Nginx only — re-reads config without dropping connections)
sudo nginx -t && sudo systemctl reload nginx

# Enable / Disable (survive reboot)
sudo systemctl enable  bldcms-backend nginx postgresql
sudo systemctl disable bldcms-backend

# Logs
journalctl -u bldcms-backend -f            # Gunicorn's own operational log
tail -f backend/logs/application.log       # application's own structured logs
tail -f backend/logs/backup_cron.log       # scheduled backup runs

# Backup cron (not a systemd unit)
crontab -l                                 # view installed backup schedule
```

Both `bldcms-backend` and `nginx` are configured `Restart=always` (`RestartSec=5` for the
backend) — a crash recovers automatically within seconds.

---

## 15. Deploying to Another Shed — Checklist

```
□ Provision Ubuntu server (LAN-reachable by technicians' Android devices and Supervisors' PCs)
□ Install PostgreSQL; create role + database (§6, §12)
□ Restore database from the source shed's backup, OR run a fresh install with no data
□ Clone/copy the project to the new host at a known absolute path
□ Create the backend venv, install requirements
□ Set DATABASE_URL, JWT_SECRET_KEY (generate a NEW one — never reuse another shed's),
  CORS_ORIGINS, DEBUG, SHOW_OTP_PLAINTEXT in the systemd unit's Environment= lines
□ Build the Dashboard (npm run build) — leave VITE_API_BASE_URL unset
□ Configure Nginx (root path must match this host's actual checkout location; server_name
  stays "_" unless a real domain is in use)
□ Configure Gunicorn (gunicorn.conf.py — usually no change needed; confirm bind=127.0.0.1:8080)
□ Install/enable the bldcms-backend and nginx systemd units
□ Mount the backup HDD (scripts/mount_backup_hdd.sh) and install the backup cron
  (scripts/install_backup_cron.sh)
□ Set Android/local.properties' API_BASE_URL to this shed's server address
□ Rebuild the Android APK (assembleDebug or assembleRelease) and distribute to devices
□ Install emBridge + one-time hosts-file entry on every Supervisor's PC
□ Verify login (Android + Dashboard)
□ Verify OTP delivery (check the OTP Logs Dashboard screen shows a plaintext code, given no
  SMS gateway is in place — see SHOW_OTP_PLAINTEXT in §5)
□ Verify Android: fill and submit a checksheet end-to-end
□ Verify Dashboard: Sections, Locomotives, Equipment, Templates, Users, Reports, System Health
  all load data
□ Verify PDF generation (approve a checksheet, download the signed PDF)
□ Verify Digital Signature (emBridge four-status-check sequence completes, signature applies)
□ Verify audit logs (Activity Timeline shows the actions just performed)
□ Confirm backup verify passes: python -m app.backup_system.run verify
```

---

## 16. Future Configuration Matrix

| Requirement | Dashboard | Backend | Android | Database | Nginx | Gunicorn | Restart Needed |
|---|---|---|---|---|---|---|---|
| Server IP change | ✖ (relative URLs) | ✖ | ✔ | ✖ | ✖ (catch-all `server_name`) | ✖ | Android: rebuild only |
| Domain name adopted | ✖ | ✖ | ✔ (if URL scheme/host changes) | ✖ | ✔ (`server_name`) | ✖ | Nginx reload + Android rebuild |
| Database password change | ✖ | ✔ | ✖ | ✔ | ✖ | ✖ | Backend restart |
| Database host change | ✖ | ✔ | ✖ | ✔ (accept-list) | ✖ | ✖ | Backend restart |
| `JWT_SECRET_KEY` rotation | ✖ | ✔ | ✖ | ✖ | ✖ | ✖ | Backend restart (invalidates existing sessions) |
| SSL certificate adopted | ✖ | ✖ | ✔ (network security config + base URL) | ✖ | ✔ | ✖ | Nginx reload + Android rebuild |
| Android branding/UI change | ✔ (if Dashboard shares assets) | ✖ | ✔ | ✖ | ✖ | ✖ | APK rebuild |
| Backend business-logic fix | ✖ | ✔ | ✖ (unless API contract changed) | ✖ | ✖ | ✖ | Backend restart |
| New checksheet template | ✖ | ✔ (data only, via seed script) | ✖ | ✔ (new rows) | ✖ | ✖ | None — data-only |
| Gunicorn worker count tuning | ✖ | ✔ (`GUNICORN_WORKERS`) | ✖ | ✖ | ✖ | ✔ | Backend restart |
| Backup destination path | ✖ | ✔ (`BLDCMS_BACKUP_ROOT`) | ✖ | ✖ | ✖ | ✖ | Backend restart (cron picks up on next run) |
| Add a new shed | ✔ (rebuild) | ✔ (fresh env) | ✔ (rebuild) | ✔ (fresh DB) | ✔ (fresh config) | ✔ (fresh config) | Fresh deployment |

---

## 17. Verification — Hardcoded Value Sweep

Full-project search for IP addresses, `localhost`, `127.0.0.1`, and any external/dev/test URL.
**Nothing below was modified** — this is a read-only inventory with a recommendation per entry.

| File | Line | Value | Purpose | Should it remain, or become configurable? |
|---|---|---|---|---|
| `backend/main.py` | 78 | `http://YOUR_SERVER_IP:3000,http://localhost:3000` | Dev-only fallback for `CORS_ORIGINS` if the env var is unset | **Remain as a fallback** — production always sets `CORS_ORIGINS` explicitly via systemd; this only matters for local `uvicorn main:app` runs. Low risk. |
| `backend/gunicorn.conf.py` | 16 | `127.0.0.1:8080` | Gunicorn bind address | **Should remain hardcoded.** This is a deliberate security boundary (never expose Gunicorn externally), not an environment-specific value. Already documented in-file as intentional. |
| `backend/deploy/nginx/bldcms.conf` | 93, 108 | `http://127.0.0.1:8080` | `proxy_pass` target | **Should remain**, for the same reason — must match Gunicorn's bind address, which is itself deliberately fixed to loopback. |
| `backend/deploy/systemd/bldcms-backend.service` | 19 | `postgresql://YOUR_DB_USER:YOUR_DB_PASSWORD@localhost:5432/rdcms` | `DATABASE_URL` | **Already configurable** (this is the live deployed value, in a systemd `Environment=` line, not a code default) — correctly the per-shed configuration point. Flagged only because this file, if ever committed with a real password, would leak a credential — confirm the tracked copy under `backend/deploy/systemd/` uses a placeholder, not the real password (see Recommendation R2 below). |
| `backend/deploy/systemd/bldcms-backend.service` | 21 | `http://YOUR_SERVER_IP,http://localhost` | `CORS_ORIGINS` | Same as above — this is the intended per-shed config point, correctly placed. |
| `backend/app/database/database.py` | 12 | `postgresql://YOUR_DB_USER:YOUR_DB_PASSWORD@localhost:5432/rdcms` | Dev-only fallback if `DATABASE_URL` is unset | **Remain as a fallback** for local development convenience; production always sets the real env var. |
| `backend/app/admin_cli/os_auth.py` | 36 | `10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 127.0.0.0/8` | Default "internal" CIDR ranges for the Admin CLI's SSH-based auth | **Should remain** — these are the standard RFC1918 private ranges, not a site-specific value; already overridable via `BLDCMS_ADMIN_ALLOWED_CIDRS` for a shed with an unusual network layout. |
| `backend/app/admin_cli/commands/backup.py`, `backend/app/backup_system/steps.py` | 42, 39 | `engine.url.host or "localhost"` | Fallback host label for `pg_dump`/`pg_restore` invocations | **Remain** — this only fires if `DATABASE_URL` somehow has no host, an edge case, not a real deployment path. |
| `Dashboard/.env` | 1 | `# VITE_API_BASE_URL=http://YOUR_SERVER_IP:8080` | Commented-out override | **Correctly configurable, and correctly left unset** for this topology. A future split-origin deployment would uncomment and update this one line. |
| `Dashboard/src/api/client.ts` | 15 | `http://localhost:8080` (inside a display-only label string) | Settings-page text shown when no override is set | **Cosmetic only** — never used as an actual request target (verified: not present in `import.meta.env`'s compiled output when unset). Low priority to change, but the label text itself is generic enough to leave as-is or make it say "same origin" instead of a specific port. |
| `Dashboard/vite.config.ts` | 70 | `http://localhost:8080` | Dev-server proxy target default | **Remain** — development-only, never built into the production bundle (confirmed: this file's logic lives entirely inside `server: {...}`, which `vite build` never executes). |
| `Dashboard/src/services/embridgeClient.ts` (+ 3 other files referencing the same constant) | 57 | `https://localhost.emudhra.com:26769` | emBridge's fixed local endpoint | **Must remain hardcoded** — this is eMudhra's own published integration constant, not a BL-DCMS deployment parameter. Every shed uses the identical value; it isn't site-specific. |
| `Android/local.properties` | 2 | `http://YOUR_SERVER_IP/` | `API_BASE_URL` | **Correctly configurable, and the primary per-shed/per-migration configuration point for Android** — this file is gitignored by design (never committed) specifically so each build machine/shed sets its own value. |
| `Android/app/build.gradle.kts` | 19 | `http://YOUR_SERVER_IP:8080/` | Fallback default if `local.properties` has no `API_BASE_URL` | **Consider updating this fallback** when this codebase is forked for a new shed's initial setup, so a fresh checkout with no `local.properties` yet doesn't silently default to Electric Loco Shed, BL's own address. Not a runtime risk (a real `local.properties` always overrides it), but worth a one-line edit during initial fork setup. |

**Cloudflare / public domains / dev-test URLs:** none found anywhere in `backend/`,
`Dashboard/src/`, or `Android/app/src/` (see the prior Module's full audit, reconfirmed here) —
`cloudflared` is installed as an OS package on the current host but has no active configuration
or running service; it is not part of the live request path.

---

## 18. Deliverables Summary

### Files inspected

- `backend/main.py`, `backend/gunicorn.conf.py`, `backend/app/database/database.py`,
  `backend/app/security/jwt.py`, `backend/app/services/otp_service.py`,
  `backend/app/services/pdf_service.py`, `backend/app/backup_system/config.py`,
  `backend/app/backup_system/steps.py`, `backend/app/admin_cli/os_auth.py`,
  `backend/app/admin_cli/commands/backup.py`
- `backend/deploy/nginx/bldcms.conf`, `backend/deploy/nginx/security_headers.conf`,
  `backend/deploy/systemd/bldcms-backend.service`, and their live `/etc/` counterparts
- `Dashboard/.env`, `Dashboard/vite.config.ts`, `Dashboard/src/api/client.ts`,
  `Dashboard/src/services/apiService.ts`, `Dashboard/src/services/embridgeClient.ts`,
  `Dashboard/package.json`
- `Android/local.properties`, `Android/app/build.gradle.kts`,
  `Android/app/src/main/res/xml/network_security_config.xml`,
  `Android/app/src/main/java/com/checksheet/android/di/NetworkModule.kt`
- Existing docs used as cross-referenced source material:
  `Documentation/DEPLOYMENT.md`, `Documentation/INSTALLATION.md`,
  `Documentation/AUTOMATED_BACKUP_SYSTEM.md`, `Documentation/BACKUP_AND_RESTORE.md`

### Configuration points discovered

Every one is catalogued in §2–§14 above; the short list of **genuinely per-shed values** is:
`Android/local.properties` (`API_BASE_URL`), the backend systemd unit's `Environment=` block
(`DATABASE_URL`, `JWT_SECRET_KEY`, `CORS_ORIGINS`, `DEBUG`, `SHOW_OTP_PLAINTEXT`), Nginx's `root`
path and (if a domain is adopted) `server_name`, and `BLDCMS_BACKUP_ROOT` if a new host's HDD
mounts somewhere other than `/mnt/storage`. Everything else in the system either doesn't need to
change between sheds (Gunicorn's loopback bind, emBridge's fixed endpoint, the RFC1918 CIDR
defaults) or already resolves itself automatically (the Dashboard's relative-URL API calls,
Nginx's catch-all `server_name`).

### Potential deployment risks

1. **No database migration framework.** Schema changes are applied via ad-hoc SQL/seed scripts.
   A second shed diverging in schema version from the first (or from a future code update) has
   no automated way to detect or reconcile drift. Recommend adopting Alembic before a second
   shed goes live.
2. **`Android/app/build.gradle.kts`'s fallback URL is Electric Loco Shed, BL's own address.** A
   new shed that forks this repo and builds before creating `local.properties` would silently
   target the wrong server. Low risk in practice (the checklist in §15 has `local.properties`
   before the build step), but worth a one-line fix per fork.
3. **`JWT_SECRET_KEY` reuse across sheds** would let one site's sessions be forged by an admin of
   another site with knowledge of the shared secret. The requirement to generate a fresh secret
   per shed is documented (§5) but not currently enforced by tooling — nothing stops an operator
   from copying the whole systemd unit verbatim including the secret.
4. **No automated secret rotation or vault integration.** `JWT_SECRET_KEY` and the database
   password live in plaintext in a systemd unit file (`/etc/systemd/system/`, root-readable
   only, but still plaintext-on-disk). Acceptable for the current single-server-per-shed
   trust model; would need revisiting for a centrally-managed multi-shed fleet.
5. **SSL is entirely absent.** Acceptable today (closed LAN, no internet exposure), but any
   future WAN/VPN-connected deployment must not go live without addressing §10 first —
   credentials and OTPs currently travel in cleartext HTTP.
6. **The Android fallback URL and Nginx's absolute `root` path are the two remaining
   host-specific hardcoded strings** most likely to be copy-pasted forward without adjustment
   during a rushed second-shed deployment — both called out explicitly in the §15 checklist for
   this reason.

### Recommendations for making the application fully configuration-driven

- **R1 — Adopt Alembic** (or an equivalent) for database schema migrations, replacing the
  current ad-hoc SQL/seed-script approach, before a second shed's database needs to track schema
  changes independently.
- **R2 — Never commit a real secret to a tracked deploy file.** Keep `backend/deploy/systemd/bldcms-backend.service` in the repo with placeholder values
  (`Environment="DATABASE_URL=__SET_ME__"`), and document that the *live* copy under
  `/etc/systemd/system/` is the only place real secrets belong — grep the tracked copy on every
  release to confirm no real credential ever gets committed by accident.
- **R3 — Externalize storage paths.** `backend/storage/pdfs/` and `backend/logs/` are currently
  fixed relative paths rather than environment variables like `BLDCMS_BACKUP_ROOT` already is —
  bringing them in line with the same pattern would let a future shed relocate them without a
  code change.
- **R4 — A single per-shed config file or `.env.site`** (site name, server IP/domain, contact
  info, backup mount path, SMS/OTP delivery mode) that both the backend and the deployment
  scripts read from, rather than the current spread of systemd `Environment=` lines,
  `local.properties`, and Nginx directives that each need separate attention. Would turn most of
  §15's checklist into "edit one file, run one install script."
- **R5 — A remote-configurable Android base URL** (e.g. a first-run "server address" prompt
  stored in `DataStore`, with the current `BuildConfig.API_BASE_URL` as the initial default)
  would remove the APK-rebuild requirement for a pure server-IP change — currently the single
  biggest operational friction point when a shed's network changes (§9).
- **R6 — Automate the §17 hardcoded-value sweep** as a pre-release CI check (a simple grep for
  IP-address patterns outside an allowlisted set of files) so a future accidental hardcoded value
  is caught before it reaches a second shed's build.

---

*This document reflects the deployment as inspected in Module 46. Update it alongside any
change to the files it references — treat a stale deployment guide as a deployment risk in its
own right.*
