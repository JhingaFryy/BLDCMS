"""
Module 44: System Administration CLI - `bldcms-admin` entry point.

This module is intentionally NOT imported by main.py (the FastAPI app) or by any HTTP-reachable
code path - it is only ever invoked directly, as a standalone process, by an already
OS-authenticated Linux user (see scripts/install_admin_cli.sh and docs/ADMIN_CLI.md). Running
`python -m app.admin_cli.main ...` (or the installed `bldcms-admin` wrapper) is the only way to
reach anything in this package.

Command structure:
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
    bldcms-admin backup create [--output-dir DIR]
    bldcms-admin backup restore <file> --confirm --database <db-name>
    bldcms-admin logs archive [--output-dir DIR]
    bldcms-admin pdfs archive [--output-dir DIR]
    bldcms-admin checksheets export [--output-dir DIR] [--format csv]
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Callable

# Must run before any other app.* import - the first call to app.core.logging.get_logger()
# (transitively triggered by app.database.database/the service layer these commands use) would
# otherwise call configure_logging() with its default enable_console=True, which is what was
# spilling every SQLAlchemy query and API-style log line into this CLI's stdout alongside the
# actual queried result. File logging (application.log, database.log, ...) is unaffected -
# admin_cli's activity is still fully captured there, exactly as before.
from app.core.logging import configure_logging
configure_logging(enable_console=False)

from app.admin_cli import os_auth
from app.admin_cli.audit import AuditEntry, write_audit_entry
from app.admin_cli.commands import backup, devices, diagnostics, health, sessions


def _print(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))


def _run(command_label: str, parameters: dict, fn: Callable[[], Any]) -> None:
    """Every command funnels through here: authorize -> run -> audit (Success or Failure) ->
    exit with the appropriate code. This is the single place that guarantees no command can run
    without an authorization check and no command outcome goes unaudited."""
    authz = os_auth.authorize()

    if not authz.allowed:
        write_audit_entry(AuditEntry(
            linux_username=authz.linux_username,
            command=command_label,
            parameters=parameters,
            source_host=authz.source_host,
            result="Failure",
            error=authz.reason,
        ))
        print(f"Access denied: {authz.reason}", file=sys.stderr)
        sys.exit(1)

    try:
        result = fn()
        write_audit_entry(AuditEntry(
            linux_username=authz.linux_username,
            command=command_label,
            parameters=parameters,
            source_host=authz.source_host,
            result="Success",
        ))
        if result is not None:
            _print(result)
    except Exception as exc:
        write_audit_entry(AuditEntry(
            linux_username=authz.linux_username,
            command=command_label,
            parameters=parameters,
            source_host=authz.source_host,
            result="Failure",
            error=str(exc),
        ))
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bldcms-admin",
        description="BL-DCMS System Administration CLI - internal, Linux-authenticated, audited.",
    )
    subparsers = parser.add_subparsers(dest="group", required=True)

    devices_parser = subparsers.add_parser("devices", help="Registered device inventory")
    devices_sub = devices_parser.add_subparsers(dest="action", required=True)
    devices_sub.add_parser("list", help="List all registered devices")
    devices_info = devices_sub.add_parser("info", help="Show full detail for one device")
    devices_info.add_argument("device_id")
    devices_logout = devices_sub.add_parser("force-logout", help="Revoke every active session for a device")
    devices_logout.add_argument("device_id")
    devices_clear = devices_sub.add_parser(
        "clear-app-data",
        help="Queue a BL-DCMS app-data clear for a device (application data only, never personal files)",
    )
    devices_clear.add_argument("device_id")

    sessions_parser = subparsers.add_parser("sessions", help="Active login sessions")
    sessions_sub = sessions_parser.add_subparsers(dest="action", required=True)
    sessions_sub.add_parser("list", help="List active (not revoked, not expired) sessions")
    sessions_revoke = sessions_sub.add_parser("revoke", help="Revoke one session by jti")
    sessions_revoke.add_argument("jti")
    sessions_revoke_user = sessions_sub.add_parser("revoke-user", help="Revoke every session for a user")
    sessions_revoke_user.add_argument("employee_id")

    diagnostics_parser = subparsers.add_parser("diagnostics", help="Diagnostic bundle generation")
    diagnostics_sub = diagnostics_parser.add_subparsers(dest="action", required=True)
    diagnostics_create = diagnostics_sub.add_parser("create", help="Generate a diagnostic bundle (.tar.gz)")
    diagnostics_create.add_argument("--output-dir", default=None)

    subparsers.add_parser("health", help="Backend/database/service health overview")

    services_parser = subparsers.add_parser("services", help="Individual service status")
    services_sub = services_parser.add_subparsers(dest="action", required=True)
    services_sub.add_parser("status", help="Status of each backend service check")

    backup_parser = subparsers.add_parser("backup", help="Database backup and restore")
    backup_sub = backup_parser.add_subparsers(dest="action", required=True)
    backup_create = backup_sub.add_parser("create", help="Create a pg_dump backup (.dump)")
    backup_create.add_argument("--output-dir", default=None)
    backup_restore = backup_sub.add_parser(
        "restore", help="Restore a pg_dump backup - DESTRUCTIVE, overwrites the live database",
    )
    backup_restore.add_argument("file")
    backup_restore.add_argument("--confirm", action="store_true", help="Required to proceed")
    backup_restore.add_argument(
        "--database", default=None,
        help="Must exactly match the live database name, as a second confirmation",
    )

    logs_parser = subparsers.add_parser("logs", help="Log file archiving")
    logs_sub = logs_parser.add_subparsers(dest="action", required=True)
    logs_archive = logs_sub.add_parser("archive", help="Archive the entire logs/ directory (.tar.gz)")
    logs_archive.add_argument("--output-dir", default=None)

    pdfs_parser = subparsers.add_parser("pdfs", help="Signed PDF archiving")
    pdfs_sub = pdfs_parser.add_subparsers(dest="action", required=True)
    pdfs_archive = pdfs_sub.add_parser("archive", help="Archive all signed checksheet PDFs (.tar.gz)")
    pdfs_archive.add_argument("--output-dir", default=None)

    checksheets_parser = subparsers.add_parser("checksheets", help="Checksheet data export")
    checksheets_sub = checksheets_parser.add_subparsers(dest="action", required=True)
    checksheets_export = checksheets_sub.add_parser("export", help="Export a header-level checksheet summary")
    checksheets_export.add_argument("--output-dir", default=None)
    checksheets_export.add_argument("--format", default="csv", choices=["csv"])

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.group == "devices":
        if args.action == "list":
            _run("devices list", {}, devices.list_devices)
        elif args.action == "info":
            _run("devices info", {"device_id": args.device_id}, lambda: devices.device_info(args.device_id))
        elif args.action == "force-logout":
            _run(
                "devices force-logout", {"device_id": args.device_id},
                lambda: devices.force_logout(args.device_id),
            )
        elif args.action == "clear-app-data":
            _run(
                "devices clear-app-data", {"device_id": args.device_id},
                lambda: devices.clear_app_data(args.device_id),
            )

    elif args.group == "sessions":
        if args.action == "list":
            _run("sessions list", {}, sessions.list_sessions)
        elif args.action == "revoke":
            _run("sessions revoke", {"jti": args.jti}, lambda: sessions.revoke_session(args.jti))
        elif args.action == "revoke-user":
            _run(
                "sessions revoke-user", {"employee_id": args.employee_id},
                lambda: sessions.revoke_all_for_user(args.employee_id),
            )

    elif args.group == "diagnostics":
        if args.action == "create":
            _run(
                "diagnostics create", {"output_dir": args.output_dir},
                lambda: diagnostics.create_bundle(args.output_dir),
            )

    elif args.group == "health":
        _run("health", {}, health.get_overview)

    elif args.group == "services":
        if args.action == "status":
            _run("services status", {}, health.get_services_status)

    elif args.group == "backup":
        if args.action == "create":
            _run(
                "backup create", {"output_dir": args.output_dir},
                lambda: backup.create_backup(args.output_dir),
            )
        elif args.action == "restore":
            _run(
                "backup restore",
                {"file": args.file, "confirm": args.confirm, "database": args.database},
                lambda: backup.restore_backup(args.file, args.confirm, args.database),
            )

    elif args.group == "logs":
        if args.action == "archive":
            _run(
                "logs archive", {"output_dir": args.output_dir},
                lambda: backup.archive_logs(args.output_dir),
            )

    elif args.group == "pdfs":
        if args.action == "archive":
            _run(
                "pdfs archive", {"output_dir": args.output_dir},
                lambda: backup.archive_pdfs(args.output_dir),
            )

    elif args.group == "checksheets":
        if args.action == "export":
            _run(
                "checksheets export", {"output_dir": args.output_dir, "format": args.format},
                lambda: backup.export_checksheets(args.output_dir, args.format),
            )


if __name__ == "__main__":
    main()
