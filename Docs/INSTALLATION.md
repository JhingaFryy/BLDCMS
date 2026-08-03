# Installation Guide

This guide sets up BL-DCMS from scratch on a fresh Ubuntu machine — backend, database,
Dashboard, and the Android project. See `SYSTEM_REQUIREMENTS.md` for exact version numbers and
`DEPLOYMENT.md` for turning this into a production deployment.

---

## 1. Backend Setup (Ubuntu)

### 1.1 System packages

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip postgresql postgresql-contrib
```

### 1.2 Python environment

```bash
cd BL-DCMS_v1.0/Backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

`requirements.txt` is a frozen snapshot of every package the backend depends on (FastAPI,
SQLAlchemy, Uvicorn, pyHanko, ReportLab, etc.) — no other installation steps are required to
satisfy Python dependencies.

### 1.3 PostgreSQL setup

Create the database and a dedicated application role:

```bash
sudo -u postgres psql <<'SQL'
CREATE ROLE YOUR_DB_USER WITH LOGIN PASSWORD 'change-this-password';
CREATE DATABASE rdcms OWNER YOUR_DB_USER;
SQL
```

Use a strong, site-specific password — do not reuse the placeholder above. You will reference
it in the `DATABASE_URL` environment variable in the next step.

### 1.4 Environment variables

The backend reads its database connection, JWT signing secret, and allowed Dashboard origins
from environment variables (each has a safe local-development fallback, but every real
deployment must set these explicitly — see `DEPLOYMENT.md` for the full list and security
notes):

```bash
export DATABASE_URL="postgresql://YOUR_DB_USER:change-this-password@localhost:5432/rdcms"
export JWT_SECRET_KEY="$(openssl rand -hex 32)"
export CORS_ORIGINS="http://<your-dashboard-host>:3000"
```

Persist these in your process manager's environment (systemd unit, `.env` loaded by your
shell profile, etc.) rather than exporting them by hand on every login — see `DEPLOYMENT.md`.

### 1.5 Apply database migrations

Migrations are plain, numbered SQL files in `Backend/migrations/`, applied in order:

```bash
cd BL-DCMS_v1.0/Backend
for f in migrations/*.sql; do
  psql "$DATABASE_URL" -f "$f"
done
```

Alternatively, initialize the schema directly from the SQLAlchemy models (equivalent end
state for a brand-new, empty database):

```bash
source venv/bin/activate
python -c "from app.database.database import initialize_db; initialize_db()"
```

### 1.6 Seed reference data

Locomotives, sections, equipment, and checksheet templates are ordinary database rows, not
hardcoded. The `Backend/scripts/` folder contains the seed scripts used to create the
checksheet templates shipped with this release (one script per template family, e.g.
`seed_mvrh_template.py`, `seed_ocb_template.py`, `seed_m35_aux_tmb_template.py`). Run the ones
relevant to your shed's equipment:

```bash
source venv/bin/activate
python scripts/seed_mvrh_template.py
```

Locomotive, section, and equipment records themselves are managed through the Dashboard once
an Admin account exists (see the next step), or can be inserted directly via SQL for a bulk
initial load.

### 1.7 Create the first Admin user

There is no public self-registration — the very first Admin user must be inserted directly:

```bash
source venv/bin/activate
python - <<'PY'
from app.database.database import SessionLocal
from app.models.user import User
from app.security.password import hash_password

db = SessionLocal()
admin = User(
    employee_id="ADMIN001",
    name="System Administrator",
    mobile="9000000000",
    email="admin@example.com",
    password_hash=hash_password("change-this-password"),
    role="Admin",
    is_active=True,
)
db.add(admin)
db.commit()
db.close()
PY
```

Log into the Dashboard with this account and create further Admin/Supervisor/Technician users
from the Users page from then on.

### 1.8 Run the backend

```bash
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8080
```

Confirm it started correctly: `curl http://localhost:8080/docs` should return the FastAPI
interactive API documentation page.

---

## 2. Frontend (Dashboard) Installation

### 2.1 Node.js

Install Node.js (see `SYSTEM_REQUIREMENTS.md` for the version this release was built/tested
against) — the recommended approach is [nvm](https://github.com/nvm-sh/nvm):

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
nvm install --lts
```

### 2.2 Install dependencies

```bash
cd BL-DCMS_v1.0/Dashboard
npm install
```

### 2.3 Point the Dashboard at the backend

Copy `.env.example`-style configuration (or edit `.env` directly) to set the backend URL:

```bash
# Dashboard/.env
VITE_API_BASE_URL=http://<your-backend-host>:8080
```

If left unset, the Dashboard's dev server proxies API requests to `http://localhost:8080` by
default (see `vite.config.ts`).

### 2.4 Run in development mode

```bash
npm run dev
```

The Dashboard is served at `http://localhost:3000`.

### 2.5 Build for production

```bash
npm run build
```

This produces static assets in `Dashboard/dist/` — see `DEPLOYMENT.md` for serving them in
production (e.g. behind Nginx).

---

## 3. Android Project Setup

### 3.1 Prerequisites

- Android Studio (see `SYSTEM_REQUIREMENTS.md`), or a standalone Android SDK + JDK 17 if
  building from the command line only.
- An Android SDK with API level 34 (compileSdk/targetSdk) installed via Android Studio's SDK
  Manager, or `sdkmanager "platforms;android-34" "build-tools;34.0.0"`.

### 3.2 Open the project

Open the `BL-DCMS_v1.0/Android` folder directly in Android Studio ("Open an existing project").
Let Gradle sync complete — it will download the Android Gradle Plugin, Kotlin compiler, and all
library dependencies declared in `app/build.gradle.kts` automatically.

### 3.3 Point the app at your backend

Create (or edit) `Android/local.properties` — this file is never committed to source control
and must be created per-installation:

```properties
sdk.dir=/path/to/your/Android/sdk
API_BASE_URL=http://<your-backend-host>:8080/
```

The trailing slash on `API_BASE_URL` is required (Retrofit's `baseUrl` contract). If this
property is absent, the app falls back to a default address baked in at build time — always
set it explicitly for your shed.

### 3.4 Build and run

From Android Studio: **Run ▶** with a connected device or emulator, or from the command line:

```bash
cd BL-DCMS_v1.0/Android
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

See `DEPLOYMENT.md` for building and signing a release APK for distribution to technicians'
devices.

---

## 4. Verifying the Installation

1. Backend: `curl http://<backend-host>:8080/docs` loads the API docs.
2. Dashboard: log in as the Admin user created in step 1.7.
3. Android: log in as a Technician user created via the Dashboard's Users page.
4. Create a locomotive, section, and equipment record (or confirm seed data is present), then
   fill and submit a checksheet from the Android app, and confirm it appears in the Dashboard's
   Checksheets page for review.
