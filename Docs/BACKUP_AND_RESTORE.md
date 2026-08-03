# Backup and Restore Guide

This document covers **on-demand, manual** backups via the System Administration CLI — for the
**scheduled, retention-managed, HDD-destination** automated backup system, see
`Documentation/AUTOMATED_BACKUP_SYSTEM.md`. Run both: the automated system for ongoing
protection, and the commands below for an ad-hoc snapshot right before a risky operation (a
migration, a restore test, etc.).

All backup/restore/archive operations in this document are performed through the **System
Administration CLI** (`bldcms-admin`), the same non-HTTP, Linux-shell-authenticated tool used for
device and session management (see `Backend/docs/ADMIN_CLI.md` for full installation and
access-control detail). There is no separate backup tool to install — it ships as part of the
backend. Note these commands write to `Backend/backups/`/`Backend/archives/` — on the same disk
as the application itself — which is why the automated system exists for anything beyond a
short-lived, manual snapshot.

Every command below prints a single JSON document on success (including the output file path
and size) and writes an audit entry to `Backend/logs/admin_cli_audit.log`.

---

## 1. Database Backup

```bash
bldcms-admin backup create [--output-dir DIR]
```

Runs `pg_dump -Fc` (PostgreSQL's custom compressed format) against the database configured in
`DATABASE_URL`, writing a timestamped file:

```
Backend/backups/bldcms-backup-<YYYYMMDDTHHMMSSZ>.dump
```

`--output-dir` overrides the destination. The database password is passed to `pg_dump` via a
`PGPASSWORD` environment variable, never as a command-line argument, so it never leaks into
shell history or `ps` output.

Run this on a schedule appropriate to your shed's change volume (daily is a reasonable
starting point — see §5, Cron Backup).

## 2. Database Restore

```bash
bldcms-admin backup restore <file> --confirm --database <db-name>
```

**This is destructive** — it overwrites the live database with the contents of `<file>`. It is
deliberately the most heavily-guarded command in the CLI:

- `--confirm` must be passed explicitly.
- You must also type the exact database name (e.g. `rdcms`) as `--database`, matching what
  `DATABASE_URL` actually points at. A mismatch aborts before touching anything.

Internally this runs `pg_restore --clean --if-exists`, which drops and recreates existing
objects before restoring — expect the target database to be fully replaced by the backup's
contents. Take a fresh backup with `backup create` before restoring an old one, in case you
need to undo the restore itself.

```bash
bldcms-admin backup restore Backend/backups/bldcms-backup-20260727T103623Z.dump \
  --confirm --database rdcms
```

## 3. PDF Backup

```bash
bldcms-admin pdfs archive [--output-dir DIR]
```

Archives every signed checksheet PDF (`Backend/storage/pdfs/`) into a single compressed
tarball:

```
Backend/archives/bldcms-signed-pdfs-<YYYYMMDDTHHMMSSZ>.tar.gz
```

Signed PDFs are also recoverable by regenerating them from `APPROVED` checksheet data, but
archiving the originals preserves the exact signed artifact (including its embedded digital
signature) without depending on the PDF-generation code never changing.

## 4. Logs Backup

```bash
bldcms-admin logs archive [--output-dir DIR]
```

Archives the entire `Backend/logs/` directory (application, API, security/auth, and admin CLI
audit logs) into:

```
Backend/archives/bldcms-logs-<YYYYMMDDTHHMMSSZ>.tar.gz
```

Useful before log rotation deletes old files, or to attach to a support ticket alongside a
diagnostics bundle (`bldcms-admin diagnostics create`, documented in `Backend/docs/ADMIN_CLI.md`).

## 4a. Checksheet Data Export

A related, non-backup export is also available for reporting/analysis outside the database:

```bash
bldcms-admin checksheets export [--output-dir DIR] [--format csv]
```

Writes a header-level checksheet summary (locomotive, section, status, timestamps, etc.) as a
CSV file under `Backend/archives/`.

## 5. Cron Backup — Superseded by the Automated Backup System

`bldcms-admin` itself still has no built-in scheduler and is not intended to be cron-driven for
routine, retention-managed backups — that is now handled by the dedicated **Automated Backup
System**, which writes to a separate HDD (not `Backend/backups/`/`Backend/archives/`, which
remain on the same disk as the application) and manages its own daily/weekly/monthly retention
automatically. See `Documentation/AUTOMATED_BACKUP_SYSTEM.md` for full setup, schedule,
retention policy, and recovery procedures, and
`Backend/scripts/install_backup_cron.sh` to install it.

Reach for the manual `bldcms-admin` commands above only for an ad-hoc, immediate snapshot — e.g.
right before running a migration or testing a restore — not as your only backup strategy.

## 6. What Is *Not* Covered by These Commands

- **Checksheet templates and reference data** (locomotives, sections, equipment) live in the
  same PostgreSQL database as everything else and are included automatically in `backup
  create`/`backup restore` — no separate step is needed.
- **Android app data** — the app itself holds only a session token (`DataStore`), not
  application data; nothing there needs backing up.
- **`local.properties` / environment variable configuration** (API URLs, secrets, keystores)
  is deliberately excluded from all of the above, since these files are per-installation and
  contain secrets — back them up separately, through your organization's secrets-management
  process, not alongside application data.
