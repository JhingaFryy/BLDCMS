# BL-DCMS — Railway Digital Checksheet Management System

**Version 1.0** — Release package for Electric Loco Sheds.

## 1. Project Overview

BL-DCMS digitizes the paper checksheet workflow used to inspect and maintain electric
locomotives at an Electric Loco Shed. A field Technician fills a checksheet on an Android
device against a locomotive/equipment record, submits it, and a Supervisor reviews it on a
web Dashboard — approving it with a legally-meaningful digital signature (via a USB DSC token
through eMudhra emBridge) or rejecting it with a reason. Every approved checksheet produces a
signed PDF that is stored on the server and downloadable from both the Dashboard and the
Android app.

The system was built to replace paper checksheets and their attendant problems: illegible
handwriting, lost paperwork, no audit trail, and no way to search or report on historical
maintenance data across locomotives, sections, or time ranges.

## 2. Features

- **Role-based access** — Admin, Supervisor, and Technician roles, each with a distinct
  workflow and permission set enforced on every backend endpoint, not just hidden in the UI.
- **OTP-based mobile authentication** — Technicians log in on Android with an Employee ID and
  password, then confirm a one-time password before a session token is issued.
- **Dynamic checksheet templates** — Templates are data-driven (stored in the database, not
  hardcoded per locomotive/equipment type), support multi-page layouts, grouped/nested fields,
  numeric range validation with technician-confirmable out-of-range overrides, dropdowns,
  dates, times, and free text. New checksheet types can be added by inserting template/field
  rows in the database, without an application code change.
- **Checksheet lifecycle** — `DRAFT → SUBMITTED → UNDER_REVIEW → APPROVED / REJECTED`, with a
  full activity trail of who did what and when at every step.
- **Digital signature (eMudhra emBridge)** — Supervisor approval is signed with a real
  Class-III DSC certificate from a connected USB token, producing a verifiable, tamper-evident
  signed PDF — not a rubber-stamped "approved" flag.
- **Automatic PDF generation** — Every submitted/approved checksheet can be rendered to a PDF
  matching the original paper form's layout.
- **Notifications** — In-app notifications for submission, approval, and rejection events, on
  both the Dashboard and the Android app.
- **Advanced search & filtering** — By locomotive number, type, technology, work type, section,
  equipment, and status, across the full checksheet history.
- **System Health monitoring** — A live Dashboard page and a CLI (`bldcms-admin health`)
  surfacing backend/database/notification-service status, resource usage, and recent activity.
- **System Administration CLI (`bldcms-admin`)** — A Linux-shell-authenticated, non-HTTP tool
  for device inventory, session revocation, diagnostics bundles, and database/log/PDF backups —
  entirely separate from the Dashboard's own Admin/Supervisor-facing application settings.
- **Device management** — Every Android device that has ever logged in is tracked (model, OS,
  app version, last-seen), with remote force-logout and app-data-clear support.

## 3. Architecture

```
┌───────────────────┐      ┌───────────────────┐
│   Android App      │      │   Dashboard (Web)  │
│  (Technician)       │      │ (Admin/Supervisor) │
│  Kotlin / Compose    │      │ React / TypeScript │
└─────────┬───────────┘      └─────────┬───────────┘
          │  HTTPS/HTTP, JWT bearer     │  HTTPS/HTTP, JWT bearer
          └──────────────┬──────────────┘
                          ▼
                ┌───────────────────────┐
                │   FastAPI Backend      │
                │   (Python)             │
                │  Routers → Services →  │
                │  SQLAlchemy Models     │
                └───────────┬───────────┘
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
        ┌────────────────┐   ┌──────────────────┐
        │  PostgreSQL DB   │   │  Local storage    │
        │  (rdcms)         │   │  (signed PDFs,     │
        │                  │   │   logs, backups)   │
        └────────────────┘   └──────────────────┘

                 ┌───────────────────────────────┐
                 │ System Administration CLI       │
                 │ (bldcms-admin) — direct DB      │
                 │ access, Linux-shell only,       │
                 │ never reachable over HTTP        │
                 └───────────────────────────────┘
```

- The **Android app** and **Dashboard** never talk to each other or to PostgreSQL directly —
  every operation goes through the FastAPI backend's REST API, authenticated with a JWT bearer
  token.
- The **Digital signature flow** runs client-side in the Dashboard: it talks directly to the
  eMudhra emBridge local service running on the Supervisor's own machine (`localhost.emudhra.com:26769`)
  to interact with the connected USB DSC token, then submits the resulting signed artifact back
  to the backend. See `Documentation/USER_GUIDE.md` and `backend/docs/EMBRIDGE_INTEGRATION.md`.
- The **System Administration CLI** is a separate, non-HTTP entry point for trusted Linux users
  on the backend server itself — it is never linked from, or reachable through, the Dashboard,
  the Android app, or the public API.

## 4. Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, PostgreSQL, Uvicorn |
| Authentication | JWT (python-jose), bcrypt password hashing (passlib) |
| PDF generation | ReportLab, pypdf, pdfplumber |
| Digital signature | pyHanko (CMS/PAdES), eMudhra emBridge (client-side, Dashboard) |
| Dashboard | React 18, TypeScript, Vite, Material UI (MUI), React Query, React Router |
| Android | Kotlin, Jetpack Compose, Material 3, Hilt, Retrofit, OkHttp, DataStore |
| Database | PostgreSQL |

See `Documentation/SYSTEM_REQUIREMENTS.md` for specific version numbers.

## 5. Folder Structure

```
BL-DCMS_v1.0/
├── Backend/          FastAPI application, migrations, admin CLI, scripts
├── Dashboard/         React/TypeScript web application
├── Android/            Kotlin/Jetpack Compose Android application
├── Database/           Schema migrations (SQL) and database setup notes
├── Documentation/       This documentation set
└── README.md           Top-level pointer into Documentation/
```

See `Documentation/PROJECT_STRUCTURE.md` for a detailed breakdown of every important folder
inside each of the four sub-projects.

## 6. Where to Go Next

| Document | Purpose |
|---|---|
| `INSTALLATION.md` | Set up a development/first-time environment from scratch |
| `DEPLOYMENT.md` | Deploy the backend, Dashboard, and Android app to a real shed |
| `USER_GUIDE.md` | Day-to-day workflows for Administrators, Supervisors, and Technicians |
| `BACKUP_AND_RESTORE.md` | Back up and restore the database, PDFs, and logs |
| `SYSTEM_REQUIREMENTS.md` | Minimum/recommended hardware and software versions |
| `PROJECT_STRUCTURE.md` | Folder-by-folder map of the codebase |
