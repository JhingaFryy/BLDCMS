# Project Structure

Top level of the release package:

```
BL-DCMS_v1.0/
├── Backend/          FastAPI application, migrations, admin CLI, scripts
├── Dashboard/          React/TypeScript web application
├── Android/             Kotlin/Jetpack Compose Android application
├── Database/             Schema migrations (SQL) and setup notes
├── Documentation/         This documentation set
└── README.md              Top-level pointer into Documentation/
```

---

## Backend/

```
Backend/
├── main.py                    FastAPI app entry point — CORS, middleware, router registration
├── requirements.txt            Frozen Python dependency list (pip install -r)
├── gunicorn.conf.py             Production WSGI/ASGI server config (Uvicorn workers) — see below
├── deploy/                      Production deployment artifacts — see below
├── app/
│   ├── api/                    One router module per resource (see table below)
│   ├── services/                Business logic — one service module per resource, called by routers
│   ├── models/                  SQLAlchemy ORM models (one table per model file)
│   ├── schemas/                 Pydantic request/response schemas
│   ├── database/                Engine/session setup (database.py) and declarative Base
│   ├── security/                JWT issuance/verification, password hashing, role dependencies
│   ├── core/                    Logging configuration and the API logging middleware
│   ├── admin_cli/                System Administration CLI (bldcms-admin) — see below
│   └── backup_system/             Automated HDD backup system (Daily/Weekly/Monthly) — see below
├── migrations/                  Numbered, plain-SQL schema migrations, applied in order
├── scripts/                      One-off/maintenance scripts (template seeding, migration runners,
│                                   mount_backup_hdd.sh, install_backup_cron.sh)
├── tests/                        Pytest test suite
├── storage/pdfs/                  Generated/signed checksheet PDFs
├── docs/                          ADMIN_CLI.md, EMBRIDGE_INTEGRATION.md — deep-dive references
└── logs/ backups/ archives/       Runtime-generated (not part of the source release)
```

### `deploy/` — production deployment artifacts (Module 45)

| File | Purpose |
|---|---|
| `install_production.sh` | Idempotent installer — installs Nginx, the systemd unit, and the Nginx site config, then starts everything. Run via `sudo bash deploy/install_production.sh`. |
| `systemd/bldcms-backend.service` | Gunicorn systemd unit — copied to `/etc/systemd/system/` by the installer |
| `nginx/bldcms.conf` | The Nginx site config — copied to `/etc/nginx/sites-available/` |
| `nginx/security_headers.conf` | Shared security-header snippet, `include`-d by every Nginx location that sets its own `Cache-Control` |

See `Documentation/DEPLOYMENT.md` for the full production topology (Nginx → Gunicorn →
PostgreSQL) and `Documentation/AUTOMATED_BACKUP_SYSTEM.md` §2 for `scripts/mount_backup_hdd.sh`.

### `app/api/` — one router per resource

| File | Resource |
|---|---|
| `auth.py` | Dashboard (Admin/Supervisor) authentication |
| `mobile_auth.py` | Android (Technician) OTP-based authentication |
| `user.py` | User management |
| `section.py`, `locomotive.py`, `equipment.py`, `section_equipment_map.py` | Reference data |
| `checksheet_template.py`, `template_field.py` | Dynamic checksheet template engine |
| `checksheet.py` | Checksheet lifecycle (create/fill/submit/review/approve/reject) |
| `digital_signature_v2.py`, `dsc_client_events.py` | eMudhra emBridge signing flow |
| `notification.py` | In-app notifications |
| `system_health.py` | Live health/status data (also used by `bldcms-admin health`) |
| `search.py` | Advanced checksheet search/filtering |
| `activity_log.py`, `otp_log.py` | Audit log APIs |
| `system_setting.py` | Application-wide settings |

### `app/admin_cli/` — System Administration CLI

Never imported by `main.py` or any `app/api/*` router — a separate, Linux-shell-authenticated
entry point (`python -m app.admin_cli.main`, wrapped as the `bldcms-admin` executable) with its
own commands under `admin_cli/commands/` (`backup.py`, `devices.py`, `sessions.py`,
`diagnostics.py`, `health.py`). See `Backend/docs/ADMIN_CLI.md`.

---

## Dashboard/

```
Dashboard/
├── package.json                npm scripts and dependencies
├── vite.config.ts               Dev server, API proxy, build configuration
├── src/
│   ├── main.tsx / App.tsx        Entry point and root component/router setup
│   ├── api/                       Axios client configuration (client.ts)
│   ├── services/                   Per-resource API call wrappers, embridgeClient.ts (DSC signing)
│   ├── pages/                      One component per route (see table below)
│   ├── components/                  Shared/reusable UI components
│   ├── contexts/                     React context providers (e.g. auth state)
│   ├── routes/                       Route definitions / route guards
│   ├── theme/                        MUI theme configuration
│   ├── types/                        Shared TypeScript types
│   └── utils/                        Formatting/parsing helpers
└── dist/                          Production build output (generated by `npm run build`)
```

### `src/pages/` — key routes

| File | Route purpose |
|---|---|
| `LoginPage.tsx` | Admin/Supervisor login |
| `DashboardPage.tsx` | Landing/overview page |
| `ChecksheetsPage.tsx`, `ChecksheetsForm.tsx`, `ChecksheetReviewDialog.tsx` | Checksheet listing, review, approve/reject |
| `DigitalSignatureDialogV2.tsx` | eMudhra emBridge signing dialog |
| `UsersPage.tsx`, `SectionsPage.tsx`, `LocomotivesPage.tsx`, `EquipmentPage.tsx`, `MappingPage.tsx` | Reference data management |
| `TemplatesPage.tsx`, `TemplateFieldsPage.tsx` | Checksheet template engine management |
| `SystemHealthPage.tsx` | Live system health dashboard |
| `ActivityTimelinePage.tsx`, `OtpLogsPage.tsx` | Audit log viewers |
| `ReportsPage.tsx` | Reporting views |
| `SettingsPage.tsx` | Application settings |
| `ForbiddenPage.tsx`, `NotFoundPage.tsx` | 403 / 404 |

---

## Android/

```
Android/
├── app/
│   ├── build.gradle.kts           App module build config, versioning, signing
│   └── src/main/java/com/checksheet/android/
│       ├── MainActivity.kt         Single Activity, hosts the NavHost
│       ├── ChecksheetApplication.kt Hilt application entry point
│       ├── data/                    Repository implementations, Retrofit API interfaces, DataStore
│       ├── domain/                  Repository interfaces (contracts consumed by ViewModels)
│       ├── di/                       Hilt modules (network, session, app-level bindings)
│       ├── ui/                       One package per screen (splash, login, otp, home, checksheet,
│       │                              fillchecksheet, checksheetdetail, history, components, ...),
│       │                              each with its Composable screen + @HiltViewModel
│       ├── renderer/                 Dynamic checksheet field rendering engine (mirrors the
│       │                              backend's template/field model) and per-field-type components
│       ├── theme/                     Compose Material 3 theme, colors, typography
│       ├── notification/              Push/local notification handling
│       └── util/ utils/                Shared helpers (error mapping, logging, formatting)
├── build.gradle.kts / settings.gradle.kts   Project-level Gradle configuration
├── local.properties                          Per-installation config (SDK path, API_BASE_URL,
│                                               release signing) — never committed
└── gradlew / gradlew.bat                      Gradle wrapper (no separate Gradle install needed)
```

---

## Database/

Contains the same numbered SQL migrations as `Backend/migrations/` (packaged here as a
standalone reference for setting up a database independently of a full backend checkout) plus
notes on schema setup — see `Documentation/INSTALLATION.md` §1.5.

---

## Documentation/

This documentation set:

| File | Purpose |
|---|---|
| `README.md` | Project overview, features, architecture, tech stack |
| `INSTALLATION.md` | First-time setup: backend, database, Dashboard, Android |
| `DEPLOYMENT.md` | Production deployment: services, ports, environment variables, APK signing |
| `USER_GUIDE.md` | Administrator / Supervisor / Technician workflows, digital signature, PDF |
| `BACKUP_AND_RESTORE.md` | Database/PDF/log backup via the System Administration CLI |
| `SYSTEM_REQUIREMENTS.md` | OS, runtime, and hardware version requirements |
| `PROJECT_STRUCTURE.md` | This file |

Deeper reference material not duplicated here lives alongside the code it documents:
`Backend/docs/ADMIN_CLI.md` (System Administration CLI) and
`Backend/docs/EMBRIDGE_INTEGRATION.md` (digital signature protocol detail).
