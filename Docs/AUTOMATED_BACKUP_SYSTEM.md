# Automated Backup System (HDD) — Module 44

This document covers the **scheduled, retention-managed backup system** (`app/backup_system`),
which writes to a separate mounted hard drive on a cron schedule. It is distinct from the
on-demand `bldcms-admin backup`/`logs archive`/`pdfs archive` commands covered in
`BACKUP_AND_RESTORE.md`, which write to the application's own disk and are meant for a manual,
one-off backup right before a risky operation (a migration, a restore test, etc.) — the two
systems intentionally do not share a destination or a retention policy. Run both: the automated
system for ongoing protection, the manual commands for ad-hoc snapshots.

## 1. Why a Separate HDD

The application runs on an SSD. A backup that lives on the same disk as the data it protects
does not survive a disk failure — the single most common reason backups exist. This system
therefore refuses to write anywhere except a separately mounted drive, and actively checks for
this at startup (see §6, Verification).

## 2. Configuring the Backup Destination

At Electric Loco Shed, BL, the backup destination is this server's **internal SATA HDD**, a
second physical disk separate from the SSD the application and database run on:

| | |
|---|---|
| Device | `/dev/sda` (ext4, ~931 GB, Toshiba MQ04ABF1) |
| Mount point | `/mnt/storage` |
| Configured backup root | `/mnt/storage/BL-DCMS` |

### One-time mount setup

`scripts/mount_backup_hdd.sh` mounts this disk and makes the mount permanent across reboots (an
`/etc/fstab` entry keyed on the disk's UUID, not its `/dev/sdX` name, since device letters can
shift). It does **not** format the disk — `/dev/sda` already carries an ext4 filesystem, so this
only mounts what's already there:

```bash
cd Backend
sudo bash scripts/mount_backup_hdd.sh
```

This must be run once, as root, on this server. It requires `sudo`, which this system's
automated tooling does not have — a human with root access runs it interactively.

After it completes, confirm the mount:

```bash
df -h /mnt/storage
mountpoint /mnt/storage
```

### Environment variable

The `BLDCMS_BACKUP_ROOT` environment variable controls where the backup system writes. No mount
name is hardcoded beyond a sensible default matching this shed's actual disk:

```bash
export BLDCMS_BACKUP_ROOT=/mnt/storage/BL-DCMS
```

If unset, it defaults to `/mnt/storage/BL-DCMS` already — setting it explicitly is only needed
if a different host mounts the drive at a different path. Persist it in the same place you
persist the backend's other environment variables (its systemd unit's `Environment=`, per
`Documentation/DEPLOYMENT.md`) — cron also needs to see it, which is why the installer in §4
bakes it directly into each cron line rather than relying on cron's own (minimal) environment.

## 3. Folder Structure

Created automatically on first run (or via `verify`, see §6):

```
<BLDCMS_BACKUP_ROOT>/
├── Daily/<timestamp>/       one folder per daily run — Database/, PDFs/, Logs/, Config/ archives
├── Weekly/<timestamp>/      one folder per weekly run — full source + database snapshot
├── Monthly/<timestamp>/     one folder per monthly run — same content as Weekly
├── Database/                 always-current copy of the latest database dump
├── PDFs/                      always-current copy of the latest PDFs archive
├── Logs/                      always-current copy of the latest logs archive
├── Releases/                   always-current copy of the latest full source snapshot
└── Manifest/                   every manifest ever written (daily+weekly+monthly), permanently
```

`Daily/`, `Weekly/`, and `Monthly/` hold the full dated history for their tier, pruned by
retention (§5). `Database/`, `PDFs/`, `Logs/`, and `Releases/` always hold exactly one copy —
the most recent artifact of that kind — so you can grab "the latest X" without hunting through a
dated folder. `Manifest/` is never pruned; it's the permanent audit trail of every run.

## 4. Schedule

Installed by `Backend/scripts/install_backup_cron.sh`, which verifies the destination first
(§6) and refuses to install the schedule if verification fails:

```bash
cd Backend
BLDCMS_BACKUP_ROOT=/mnt/storage/BL-DCMS bash scripts/install_backup_cron.sh
```

This installs three crontab entries for the invoking user:

| Schedule | Time | Backs up |
|---|---|---|
| Daily | 02:00 every day | PostgreSQL database, generated PDFs, application logs, configuration files |
| Weekly | 02:30 every Sunday | Full compressed snapshot: Backend, Dashboard, Android, Documentation, a fresh database dump, configuration files |
| Monthly | 03:00 on the 1st of the month | Same content as Weekly, on a monthly cadence with its own longer retention window |

Re-running the installer is safe — it replaces its own previously-installed entries rather than
duplicating them (matched by a marker comment), and leaves any of your own unrelated crontab
entries untouched.

Cron's own stdout/stderr for every run is appended to `Backend/logs/backup_cron.log` — check
this first if a scheduled run doesn't seem to have happened.

## 5. Retention Policy

| Tier | Kept | Behavior beyond that |
|---|---|---|
| Daily | Newest 7 | Oldest automatically deleted after each successful run |
| Weekly | Newest 4 | Oldest automatically deleted after each successful run |
| Monthly | Newest 12 | Oldest automatically deleted after each successful run — a rolling one-year archive, not unlimited-forever storage |

Retention is only applied after a **successful** run, and only to the tier that just ran — a
failed daily run never deletes anything, and never touches Weekly/Monthly. Every deletion is
logged (see §7) with exactly which folder was removed.

## 6. Verification

Run any time — after mounting a new HDD, after a configuration change, or just to confirm the
system is healthy:

```bash
cd Backend
BLDCMS_BACKUP_ROOT=/mnt/storage/BL-DCMS venv/bin/python -m app.backup_system.run verify
```

This exercises every piece of the system against small synthetic data (never against your real
Daily/Weekly/Monthly folders or their retention counts) and reports pass/fail for each:

- **HDD is writable** — writes and removes a small probe file at the configured root.
- **Backup folders exist** — creates the eight top-level folders if missing, confirms they exist.
- **Archives are created successfully** — builds a real `.tar.gz` from synthetic sample data.
- **Compression succeeds** — confirms the resulting archive is non-empty.
- **Checksums are generated** — confirms the `.sha256` sidecar file validates against the archive.
- **Manifests are generated** — confirms a manifest JSON file was written to `Manifest/`.
- **Retention policy works** — creates 3 dummy dated folders, confirms pruning to a keep-count of
  2 removes exactly the oldest one.

Exit code is `0` if every check passes, `1` otherwise — safe to wire into a monitoring check.

Note one thing `verify` reports but does not fail on: whether the configured backup root
resolves to the **same filesystem/device** as the application's own checkout. If it does, your
"HDD" isn't actually a separate disk yet (e.g. you pointed `BLDCMS_BACKUP_ROOT` at a plain
folder on the SSD while testing) — the core "never on the SSD" requirement is not actually being
satisfied until this is corrected, even though backups will still run without error.

## 7. Logging

Every run writes to two places:

1. **`Backend/logs/backup_system.log`** — a dedicated, append-only JSON-lines file, one line per
   event: `started`, `completed` (with duration, total archive size, and files included),
   `failed` (with the error), and `retention_applied` (with exactly which folders were removed).
2. **The `activity_logs` database table** — `BACKUP_DAILY_COMPLETED`/`_FAILED`,
   `BACKUP_WEEKLY_COMPLETED`/`_FAILED`, `BACKUP_MONTHLY_COMPLETED`/`_FAILED`, and
   `BACKUP_RETENTION_APPLIED`, so scheduled backup runs show up in the same Activity Timeline the
   Dashboard already shows for everything else. This is best-effort — a database problem can
   never cause a backup that otherwise succeeded to be reported as failed.

## 8. Recovery Procedures

Every archive has a `.sha256` sidecar — **always verify before restoring**:

```bash
cd <folder containing the archive>
sha256sum -c <archive-name>.sha256
```

### 8.1 Restore the Database

```bash
# 1. Verify integrity first (see above)
# 2. Stop the backend (it must not be writing to the database during a restore)
sudo systemctl stop bldcms-backend

# 3. Restore - this DROPS AND RECREATES existing objects (pg_restore --clean --if-exists)
pg_restore --clean --if-exists -h localhost -U YOUR_DB_USER -d rdcms \
  /mnt/storage/BL-DCMS/Database/bldcms-db-<timestamp>.dump

# 4. Restart the backend
sudo systemctl start bldcms-backend
```

To restore from a specific historical point rather than the latest, use the dated file under
`Daily/<timestamp>/Database/`, `Weekly/<timestamp>/`, or `Monthly/<timestamp>/` instead of the
`Database/` "latest copy" folder.

### 8.2 Restore PDFs

```bash
tar -xzf /mnt/storage/BL-DCMS/PDFs/bldcms-pdfs-<timestamp>.tar.gz -C /
```

The archive's internal paths are absolute (rooted at `Backend/storage/pdfs`), so extracting with
`-C /` restores files to their original location. Extract to a temporary directory first and
review contents if you only need to recover a subset rather than overwrite everything currently
in `storage/pdfs/`.

### 8.3 Restore Configuration Files

```bash
mkdir -p /tmp/bldcms-config-restore
tar -xzf /mnt/storage/BL-DCMS/Daily/<timestamp>/Config/bldcms-config-<timestamp>.tar.gz \
  -C /tmp/bldcms-config-restore
```

Files are archived by their original basename only (`requirements.txt`, `.env`,
`local.properties`) — copy the ones you need back to their real location manually rather than
extracting directly over a live installation, since the archive doesn't preserve which project
each file came from.

### 8.4 Full Application Recovery (New Hardware / Disaster Recovery)

Use the latest **Weekly** or **Monthly** snapshot (`Releases/` for the newest, or a specific
dated `Weekly/<timestamp>/`/`Monthly/<timestamp>/` folder for an older one):

```bash
mkdir -p /opt/BL-DCMS-restore
cd /opt/BL-DCMS-restore
for f in /mnt/storage/BL-DCMS/Weekly/<timestamp>/bldcms-{backend,dashboard,android,documentation}-<timestamp>.tar.gz; do
  tar -xzf "$f"
done

# Restore the database from the same snapshot
pg_restore --clean --if-exists -h localhost -U YOUR_DB_USER -d rdcms \
  /mnt/storage/BL-DCMS/Weekly/<timestamp>/bldcms-db-<timestamp>.dump

# Restore configuration
tar -xzf /mnt/storage/BL-DCMS/Weekly/<timestamp>/bldcms-config-<timestamp>.tar.gz \
  -C /tmp/bldcms-config-restore
```

From here, follow `Documentation/INSTALLATION.md` and `Documentation/DEPLOYMENT.md` as if setting
up fresh — re-create the Python venv (`requirements.txt` was restored above), re-run
`npm install` for the Dashboard, re-open the Android project, and put the restored config files
(`.env`, `local.properties`, `DATABASE_URL`/`JWT_SECRET_KEY`/`CORS_ORIGINS`) back in place before
starting the backend.

## 9. What This System Does Not Do

- It does not back up the Android app's own local state — the app holds only a session token, no
  application data worth backing up (see `BACKUP_AND_RESTORE.md` §6).
- It does not encrypt archives at rest — if your HDD isn't itself encrypted (full-disk
  encryption) and backups may contain sensitive data leaving the building (an external drive
  taken off-site), add encryption at the storage layer, not inside this module.
- It does not copy backups off-host — this system's whole job is "not on the SSD"; a true
  disaster-recovery posture (surviving the loss of the HDD itself, e.g. theft or physical damage
  to the server) additionally needs an off-site copy, which is outside this module's scope.
