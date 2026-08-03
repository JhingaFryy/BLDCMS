# System Requirements

## Server (Backend + Database)

| Component | Version used to build/verify this release | Minimum |
|---|---|---|
| OS | Ubuntu 26.04 LTS | Ubuntu 22.04 LTS or newer |
| Python | 3.14 | 3.11+ |
| PostgreSQL | 18 | 14+ |
| RAM | — | 4 GB (8 GB recommended for a busy shed with concurrent Dashboard + Android traffic) |
| Storage | — | 20 GB minimum, plus growth for signed PDFs, logs, and database backups — size according to expected checksheet volume and backup retention policy |

The backend's connection pool is sized for real concurrent load (`pool_size=20,
max_overflow=30`) — confirm PostgreSQL's own `max_connections` (default 100) comfortably
exceeds the backend's pool plus headroom for the admin CLI and PostgreSQL's own reserved
superuser connections.

## Frontend Build Machine (Dashboard)

| Component | Version used to build/verify this release | Minimum |
|---|---|---|
| Node.js | 22.x | 20 LTS+ |
| npm | 9.x (bundled with Node) | — |

Only required on whichever machine builds the Dashboard (`npm run build`) — the resulting
static files in `Dashboard/dist/` can then be served by any static web server (Nginx, etc.)
with no Node.js runtime dependency at all.

## Android Development Machine

| Component | Version |
|---|---|
| Android Studio | Ladybug (2024.2) or newer, bundling a compatible JDK and Kotlin plugin |
| JDK | 17 (matches `app/build.gradle.kts` JVM target) |
| Gradle | 8.10.2 (managed automatically via the Gradle wrapper — no separate install needed) |
| Android Gradle Plugin | 8.6.0 |
| Kotlin | 2.0.21 |
| Android SDK | API 34 (`compileSdk`/`targetSdk`); supports devices back to API 24 (`minSdk`, Android 7.0) |

## Android Device (Runtime)

| Requirement | Value |
|---|---|
| Minimum Android version | 7.0 (API 24) |
| Permissions used | Internet only (no camera, storage, location, or contacts access) |
| Storage | Minimal — the app stores only a session token locally, no offline checksheet cache |
| Network | Must be able to reach the backend's host/port (see `DEPLOYMENT.md` §5) |

## Supervisor Workstation (Digital Signature)

Digital signing runs client-side in the Supervisor's own browser, not on the server:

| Requirement | Value |
|---|---|
| OS | Windows (eMudhra emBridge is a Windows service) |
| Software | eMudhra emBridge, CryptoID middleware |
| Hardware | A Class-III DSC USB token (e.g. ProxKey) |
| Browser | Any modern Chromium- or Firefox-based browser, with the one-time `localhost.emudhra.com` certificate exception accepted (see `USER_GUIDE.md` §4) |

See `Backend/docs/EMBRIDGE_INTEGRATION.md` for full protocol and troubleshooting detail.
