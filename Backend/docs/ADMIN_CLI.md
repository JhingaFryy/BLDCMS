# BL-DCMS System Administration CLI (`bldcms-admin`)

Module 44. Internal administration only.

## Purpose

`bldcms-admin` is a local command-line tool for trusted system administrators to perform
high-privilege operational tasks - device inventory, session management, health checks, and
diagnostics - that don't belong in the Dashboard (application administration for Admins/
Supervisors) or the Android app (Technician workflow).

**This is not a backdoor and not a second authentication system.** It has no login, password, or
token of its own. It relies entirely on Linux's own authentication: whoever can already open a
shell on the backend server (a local console session, or an authorized SSH session on the
organization's internal network) has already been authenticated by the operating system before
this tool ever runs. `bldcms-admin` only adds *authorization* on top of that - checking the
already-authenticated Linux user is a member of the `bldcms-admin` group - and an audit trail of
every command run.

It is never reachable over HTTP. It is not linked from, called by, or in any way connected to the
Dashboard, the Android application, or Swagger/OpenAPI. See [Architecture](#architecture) below.

## Architecture

```
Android  ──┐
           ├──▶ FastAPI Backend ──▶ Dashboard API  (Admins & Supervisors, over HTTP)
Dashboard ─┘         │
                      │  (no HTTP connection - direct DB session only)
                      ▼
              System Administration CLI (bldcms-admin)
              Linux-authenticated sysadmins, local/SSH only
```

`bldcms-admin` lives in `app/admin_cli/` - a package that is **never imported by `main.py` or any
`app/api/*` router**. It talks to the same PostgreSQL database as the FastAPI app using the exact
same `SessionLocal` the rest of the backend uses (`app/database/database.py`), and reuses existing
services (`session_service`, `system_health_service`, `activity_log_service`) rather than
duplicating their logic. This is the same "standalone script with direct DB access" pattern
already used throughout `scripts/` (e.g. `apply_migration_015.py`) - `bldcms-admin` is simply that
pattern with an OS-authorization gate and a command-line interface wrapped around it.

A small number of *existing, Android/Dashboard-facing* endpoints were extended (not replaced) to
give the CLI something real to read and act on:

- `POST /mobile-auth/login`, `POST /mobile-auth/verify-otp`, `POST /auth/request-otp`,
  `POST /auth/verify-otp` now accept additional **optional** device-metadata fields (manufacturer,
  model, OS/app version, battery, network type, storage headroom, a stable device ID) - all
  backward compatible; a client that sends none of them behaves exactly as before.
- `GET /auth/me` now also returns `pending_admin_command`, so a CLI-issued command (currently only
  `CLEAR_APP_DATA`) reaches the device on its very next authenticated contact with the backend,
  without a dedicated polling endpoint.
- `POST /auth/acknowledge-device-notice` (new) - called once by Android when the technician
  dismisses the in-app notice explaining what this CLI can see/do on their device.

None of these three endpoints is part of the CLI's own surface - they are ordinary,
JWT-authenticated endpoints Android/Dashboard already call or could call; the CLI never makes an
HTTP request to any of them or to anything else.

## Installation

Run once, as root, on the backend server:

```bash
cd /path/to/Checksheet/backend
sudo bash scripts/install_admin_cli.sh
```

This:

1. Creates the `bldcms-admin` Linux group (idempotent - safe to re-run).
2. Installs a wrapper at `/usr/local/bin/bldcms-admin` (mode `750`, owner `root:bldcms-admin`)
   that execs this backend's own venv Python running `python -m app.admin_cli.main`.
3. Prepares `logs/admin_cli_audit.log` with group-writable, setgid permissions so every
   `bldcms-admin` group member's invocations can append to the same file.

The wrapper always uses *this* backend checkout's venv and this backend's database connection
(`app/database/database.py`) - there's nothing to configure separately for "which environment" the
CLI talks to.

## Required Linux permissions

Only two things are required to run privileged commands:

1. **A Linux shell on the backend server** - a local console login, or an SSH session that has
   already passed sshd's own authentication (keys/password/PAM, however your organization
   configures it). `bldcms-admin` does not care how you got the shell, only that you have one.
2. **Membership in the `bldcms-admin` Linux group** (or `root`). Grant it with:

   ```bash
   sudo usermod -aG bldcms-admin <linux-username>
   ```

   The user must start a new login session (log out/in, or run `newgrp bldcms-admin`) for the new
   group membership to take effect - this is standard Linux group-membership behavior, not
   anything specific to this tool.

Running `bldcms-admin` as a user who isn't in the group (and isn't root) prints an access-denied
message, writes a `Failure` audit entry, and exits with status `1` - no command logic ever runs.

## Internal network usage assumptions

`bldcms-admin` is designed to be reached only from the organization's internal network - normally
enforced the same way any other sensitive service on the box would be: sshd/firewall
configuration restricting who can even open a shell on the server in the first place. That
infrastructure-level control is outside this codebase and must be configured separately (e.g.
`sshd_config` `AllowUsers`/`ListenAddress`, or a firewall rule scoping port 22 to internal ranges).

On top of that, `bldcms-admin` adds one **defense-in-depth** check of its own: if it detects (via
SSH's own `SSH_CONNECTION`/`SSH_CLIENT` environment variables) that it's running inside an SSH
session, it verifies the connecting client's IP falls within a configured internal range before
doing anything else. By default this is the standard private-address ranges
(`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`); override with a comma-separated
list via the `BLDCMS_ADMIN_ALLOWED_CIDRS` environment variable if your internal range differs. A
direct local console login (no SSH involved at all) has no "source network" to check and is
implicitly allowed - the network check is specifically about *remote* access.

This is a second, independent layer, not a replacement for restricting SSH/network access at the
infrastructure level - configure both.

## Available commands

```
bldcms-admin devices list
bldcms-admin devices info <device-id>
bldcms-admin devices force-logout <device-id>
bldcms-admin devices clear-app-data <device-id>

bldcms-admin sessions list
bldcms-admin sessions revoke <jti>
bldcms-admin sessions revoke-user <employee-id>

bldcms-admin diagnostics create [--output-dir DIR]

bldcms-admin health
bldcms-admin services status
```

All commands print a single JSON document to stdout on success. On failure, an `Error: ...`
message goes to stderr and the process exits with status `1`.

| Command | What it does |
|---|---|
| `devices list` | Lists every device that has ever reported metadata at login - manufacturer, model, OS/app version, battery, network type, last-seen time, disclosure-acknowledgment state, any pending command, and whether it currently has an active session. |
| `devices info <device-id>` | Full detail for one device, including storage headroom and its 10 most recent sessions. |
| `devices force-logout <device-id>` | Revokes every currently-active session tied to that device (device-scoped equivalent of `sessions revoke`). |
| `devices clear-app-data <device-id>` | Queues a `CLEAR_APP_DATA` command the device picks up on its next login (see [Security considerations](#security-considerations) for exactly what is and isn't touched). |
| `sessions list` | Lists every session that is neither revoked nor expired, across all users/devices. |
| `sessions revoke <jti>` | Revokes one specific session by its `jti`. |
| `sessions revoke-user <employee-id>` | Revokes every active session for a user (all their devices) - "force logout everywhere" for an employee. |
| `diagnostics create` | Generates a timestamped `.tar.gz` (default: `backend/diagnostics/`) containing backend/database/service health, server info, application info, and recent tails of every whitelisted log file - for offline troubleshooting or escalation. |
| `health` | The same overview the Dashboard's System Health page shows (backend/database/Android-connectivity/notification-service checks, server resource usage, DB row counts, recently-active users) - reused directly from `app/services/system_health_service.py`, not reimplemented. |
| `services status` | Just the individual service-check results (backend API, database, Android connectivity, notifications). |

Device metadata reflects the state **as of the device's last login**, not real-time telemetry -
there is no persistent connection or push channel to an Android device.

## Example usage

```bash
# See every registered device and whether it's currently logged in
bldcms-admin devices list

# Full detail on one device, including recent session history
bldcms-admin devices info a1b2c3d4e5f6

# A phone was reported lost - end its sessions immediately and queue an app-data clear
bldcms-admin devices force-logout a1b2c3d4e5f6
bldcms-admin devices clear-app-data a1b2c3d4e5f6

# An employee left the organization - end every session on every device they were logged into
bldcms-admin sessions revoke-user 50813536710

# Quick health check before/after a deployment
bldcms-admin health

# Generate a bundle to attach to a support ticket
bldcms-admin diagnostics create --output-dir /tmp
```

## Audit logging

Every single invocation - successful, failed, or denied before it even ran - writes exactly one
audit entry in two places:

1. **`logs/admin_cli_audit.log`** - a dedicated, append-only JSON-lines file, completely separate
   from `application.log`/`error.log`/`auth.log`/etc. This file is written first and does not
   depend on the database being reachable, so even a failed `health` check caused by the database
   being down still gets audited. Each line contains exactly:

   ```json
   {
     "timestamp": "2026-07-25T05:03:36.830938+00:00",
     "linux_username": "jsmith",
     "source_host": "192.168.1.41",
     "command": "devices clear-app-data",
     "parameters": {"device_id": "a1b2c3d4e5f6"},
     "result": "Success",
     "error": null
   }
   ```

   Sensitive parameter names (password, otp, token, refresh_token, secret, pin) are always
   redacted as `"<redacted>"` even if a future command happens to accept one - no command
   currently does.

2. **The existing `activity_logs` table**, via `activity_log_service.log_activity`, using new
   `ADMIN_CLI_*` action constants (e.g. `ADMIN_CLI_SESSION_REVOKED`, `ADMIN_CLI_ACCESS_DENIED`).
   This is best-effort (per that function's existing contract - it never raises) and puts CLI
   actions in the same Activity Timeline the rest of the application already uses, correlated by
   the same Linux-username/source-host/parameters/result payload in its metadata column.

The audit file is created with `660` permissions and group `bldcms-admin` - readable/writable by
group members, never world-readable, since "who ran what privileged command" is itself sensitive
operational information.

## Security considerations

- **No credentials of its own.** There is nothing to phish, brute-force, or leak - authorization
  is Linux group membership, checked fresh on every invocation.
- **`devices clear-app-data` only ever touches BL-DCMS's own app-sandboxed storage.** The Android
  side (`util/DeviceDataClearer.kt`) clears the session, app preferences, and files/cache under
  `Context.cacheDir`, `Context.filesDir`, and `Context.getExternalFilesDir()` - all three are
  app-private by Android OS design and are physically inaccessible to any other app without root.
  This is not a policy promise the code happens to follow; it is enforced by the Android
  application sandbox itself. It never touches personal photos, messages, other apps' data, or
  anything outside BL-DCMS's own storage.
- **No covert access.** There is no screen-viewing, no arbitrary file browsing, and no way to see
  anything on a device the technician hasn't been told about - see the in-app notice shown once
  after login (`ui/components/DeviceManagementNoticeDialog.kt`), which plainly states what this
  CLI can and cannot do before any of it is exercised against that device.
- **Revocation reuses existing authorization, it doesn't bypass it.** `sessions revoke` /
  `devices force-logout` set the same `UserSession.revoked` flag that `validate_session()` (used
  by every authenticated request in the entire application) already checks - a revoked session is
  rejected on its very next use exactly like a normal logout. No new session-validation code path
  was introduced.
- **Defense in depth, not a single point of failure.** Linux authentication, group-membership
  authorization, and the internal-network check are three independent layers; the primary "only
  reachable from the internal network" control is your sshd/firewall configuration, which this
  tool assumes and adds one more check on top of, not the other way around.

## Troubleshooting

**"Access denied: Linux user 'X' is not a member of the 'bldcms-admin' group"**
Run `sudo usermod -aG bldcms-admin X`, then have that user start a new session (`newgrp
bldcms-admin`, or log out/in) - group membership only takes effect for new sessions, not the
current one.

**"Access denied: Connection from X.X.X.X is outside the configured internal network ranges"**
Either you're genuinely connecting from outside the internal network (expected - this CLI isn't
for that), or your internal range isn't one of the defaults; set
`BLDCMS_ADMIN_ALLOWED_CIDRS="10.0.0.0/8,172.16.0.0/12"` (comma-separated) to match your actual
network before running the command.

**`bldcms-admin: command not found`**
The installer wasn't run, or `/usr/local/bin` isn't on your `PATH`. Re-run
`sudo bash scripts/install_admin_cli.sh`, or invoke directly:
`cd backend && venv/bin/python -m app.admin_cli.main <command>`.

**A device never shows up in `devices list`**
Device metadata is only ever recorded at login/OTP-verify time - a device that hasn't logged in
since Module 44 was deployed has no `device_info` row yet. It will appear after its next
successful login.

**`devices clear-app-data` doesn't seem to have taken effect**
It's not instant - Android picks it up on its *next* authenticated login (via `GET /auth/me`'s
`pending_admin_command` field), not via any push mechanism (there isn't one). If the device is
offline or the app isn't opened, the command simply waits; `devices info <device-id>` shows
`pending_command_issued_at` so you can confirm it's still queued.

**Diagnostic bundle command fails with a database error**
`diagnostics create` still needs the database for `overview.json`/`services.json`/etc. If the
database itself is down, use `health` first to confirm, then check `logs/database.log` and
`logs/error.log` directly (the CLI's own audit entry for the failed attempt is still written to
`logs/admin_cli_audit.log` even though the diagnostic bundle itself couldn't be generated).
