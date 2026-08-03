# BL-DCMS — Configuration Checklist for a New Deployment

Every item below **must** be reviewed before this distribution is deployed to a new shed. None
of it works out of the box — every value is either a placeholder (`CHANGE_ME`, `YOUR_...`) or a
generic development default. This file is the single checklist; `INSTALLATION_GUIDE.md` walks
through applying each item step by step.

| # | Item | File location | Purpose | Example value | Restart / rebuild required |
|---|---|---|---|---|---|
| 1 | Server IP / hostname | Referenced by `Android/local.properties`, optionally `Dashboard/.env` | The address every client (Android app, browser) uses to reach this shed's server | `10.20.1.5` or `bldcms.yourshed.local` | See rows 3 and 8 below |
| 2 | Dashboard API URL | `Dashboard/.env` → `VITE_API_BASE_URL` (leave commented/unset for the standard same-origin setup) | Only needed if the Dashboard is ever served from a different origin than the API | `# VITE_API_BASE_URL=http://10.20.1.5:8080` | Dashboard rebuild (`npm run build`) only if uncommented |
| 3 | Android API endpoint | `Android/local.properties` → `API_BASE_URL` | Base URL every Android network call uses (login, checksheets, PDFs) | `API_BASE_URL=http://10.20.1.5/` | **APK rebuild required** — this is compiled in at build time, not read at runtime |
| 4 | Android SDK path | `Android/local.properties` → `sdk.dir` | Local Android SDK location on the build machine | `sdk.dir=/home/youruser/Android/Sdk` | None (build-machine-local only) |
| 5 | Database credentials | `Backend/deploy/systemd/bldcms-backend.service` → `DATABASE_URL` | PostgreSQL connection string | `postgresql://bldcms_app:REAL_PASSWORD@localhost:5432/bldcms` | Backend restart (`systemctl restart bldcms-backend`) |
| 6 | Database role/database creation | `Database/01_schema.sql`, `INSTALLATION_GUIDE.md` §3 | Initial PostgreSQL role + database, matching item 5 | `CREATE ROLE bldcms_app WITH LOGIN PASSWORD '...'; CREATE DATABASE bldcms OWNER bldcms_app;` | Run once, before first backend start |
| 7 | JWT signing secret | `Backend/deploy/systemd/bldcms-backend.service` → `JWT_SECRET_KEY` | Signs/verifies all session tokens. **Must be unique per shed** — never reuse another site's value or a shared/example value. | Generate with `openssl rand -hex 32` | Backend restart (invalidates all existing sessions) |
| 8 | Nginx `server_name` / static root | `Backend/deploy/nginx/bldcms.conf` | `root` must be this host's actual absolute path to `Dashboard/dist`; `server_name` only needs to change if adopting a real domain instead of the default catch-all (`_`) | `root /opt/bldcms/Dashboard/dist;` | `sudo nginx -t && sudo systemctl reload nginx` |
| 9 | Allowed CORS origins | `Backend/deploy/systemd/bldcms-backend.service` → `CORS_ORIGINS` | Defense-in-depth allowlist of browser origins (same-origin requests through Nginx never trigger this check at all) | `CORS_ORIGINS=http://10.20.1.5,http://localhost` | Backend restart |
| 10 | Backup destination | `Backend/app/backup_system/config.py` (`BLDCMS_BACKUP_ROOT` env var, if set) | Where scheduled Daily/Weekly/Monthly backups are written — **must be a separate physical disk/mount from the application disk** | `/mnt/backup/BL-DCMS` | Backend restart; cron picks it up on next scheduled run |
| 11 | PDF/upload storage directory | `Backend/storage/pdfs/` | Where generated/signed checksheet PDFs are written on disk | Default relative path is fine for most installs | None, unless relocated |
| 12 | SSL certificate | Not configured in this distribution (plain HTTP) | Only relevant if this deployment will be reachable outside a trusted closed LAN | Let's Encrypt or an internal CA cert, terminated at Nginx | Nginx reload + Android network-security-config change + APK rebuild (see `INSTALLATION_GUIDE.md` §9) |
| 13 | emBridge prerequisites | Installed per-PC on every Supervisor's own machine, not part of this codebase | Local digital-signature service the Dashboard's browser talks to directly at `https://localhost.emudhra.com:26769` | One-time `hosts` file entry per eMudhra's own installer instructions | None (per-PC one-time setup, not a code/config change) |
| 14 | Organization/shed name shown in the Dashboard | `Dashboard/src/pages/SettingsPage.tsx` (`"YOUR_SHED_NAME"` placeholder), `Database/02_bootstrap_seed.sql` (`company_name` setting) | Cosmetic branding text shown under Settings → About | `Electric Loco Shed, <Your City>` | Dashboard rebuild |
| 15 | Shed/organization logo artwork | `Android/app/src/main/res/drawable-nodpi/logo.png`, PDF header branding | The shipped image is Electric Loco Shed, BL's own official seal — **replace it with your own shed's logo/seal before going live**, this distribution cannot supply another shed's artwork | Replace the PNG file directly, same filename | APK rebuild (Android); no backend change needed for the PDF (see `Backend/app/services/pdf_service.py` if a logo is embedded there) |
| 16 | Bootstrap Administrator password | `Database/02_bootstrap_seed.sql` / `README.md` "First Login" | Default login used only for initial setup | `ChangeMe@123` (public, documented on purpose) | **Change immediately after first login** — Dashboard → Users → Reset Password |
| 17 | Checksheet template library | `Database/03_optional_checksheet_template_library.md` | Whether to build your own templates via the Dashboard UI, or bulk-load the existing 146-template library via `Backend/scripts/seed_*.py` | N/A — a workflow decision, not a single value | N/A |
| 18 | systemd service user/group | `Backend/deploy/systemd/bldcms-backend.service` → `User=` / `Group=` | The Linux account the backend process runs as | A dedicated non-root service account, e.g. `bldcms` | Re-run `sudo systemctl daemon-reload && sudo systemctl restart bldcms-backend` after editing |
| 19 | Deployment root path | Used throughout `Backend/deploy/*`, `README.md`, `INSTALLATION_GUIDE.md` as `/opt/bldcms` | Where this project is checked out on the server | `/opt/bldcms` (recommended) or any absolute path you choose | Update every path reference in the systemd unit and Nginx config to match if you don't use `/opt/bldcms` |
| 20 | `SHOW_OTP_PLAINTEXT` | `Backend/deploy/systemd/bldcms-backend.service` | Whether the OTP Logs admin screen displays a technician's OTP in plaintext. Set `true` only if this shed has no SMS/email OTP delivery channel. | `true` (no SMS gateway) or `false` (real delivery channel exists) | Backend restart |

## Generating secrets

```bash
# JWT_SECRET_KEY - a long random hex string, unique to this deployment
openssl rand -hex 32

# A strong PostgreSQL role password
openssl rand -base64 24
```

Never reuse a secret across two sheds, and never commit a real secret into
`Backend/deploy/systemd/bldcms-backend.service` if this project is later placed under its own
version control — keep real values only in the deployed copy under `/etc/systemd/system/`.

## What was intentionally left unchanged (do not "fix" these)

- `Backend/gunicorn.conf.py` → `bind = "127.0.0.1:8080"` — a deliberate security boundary
  (Gunicorn must never be reachable except through Nginx), not a per-site value.
- `Backend/deploy/nginx/bldcms.conf` → `proxy_pass http://127.0.0.1:8080;` — must match the line
  above; both are meant to stay on loopback.
- `Dashboard/src/services/embridgeClient.ts` → `https://localhost.emudhra.com:26769` — eMudhra's
  own fixed integration endpoint, identical for every shed, not a BL-DCMS setting.
- `Backend/app/admin_cli/os_auth.py` → the default RFC1918 CIDR list — generic private-network
  ranges, already overridable via `BLDCMS_ADMIN_ALLOWED_CIDRS` if a shed's network is unusual.
