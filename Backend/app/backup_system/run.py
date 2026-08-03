"""Module 44: automated backup system CLI entry point.

    python -m app.backup_system.run daily
    python -m app.backup_system.run weekly
    python -m app.backup_system.run monthly
    python -m app.backup_system.run verify

Not imported by main.py or any app/api/* router - invoked only as a standalone process, normally
by cron (see scripts/install_backup_cron.sh). Exits 0 on success, 1 on failure, so cron's own
exit-code-based failure detection (e.g. mailing on non-zero exit) works without any extra
plumbing.
"""
from __future__ import annotations

import argparse
import json
import sys

# Same reasoning as app.admin_cli.main: must run before any other app.* import, so the first
# get_logger() call (transitively triggered by app.database.database/the service layer) doesn't
# install a console handler that would interleave SQLAlchemy query noise into this script's
# stdout - cron output/mail should be exactly the JSON manifest this script prints, nothing else.
from app.core.logging import configure_logging
configure_logging(enable_console=False)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="bldcms-backup",
        description="BL-DCMS Automated Backup System (HDD) - Module 44.",
    )
    parser.add_argument("tier", choices=["daily", "weekly", "monthly", "verify"])
    args = parser.parse_args()

    if args.tier == "daily":
        from app.backup_system.daily import run_daily_backup
        manifest = run_daily_backup()
        print(json.dumps(manifest.to_dict(), indent=2, default=str))
        sys.exit(0 if manifest.status == "success" else 1)

    elif args.tier == "weekly":
        from app.backup_system.weekly import run_weekly_backup
        manifest = run_weekly_backup()
        print(json.dumps(manifest.to_dict(), indent=2, default=str))
        sys.exit(0 if manifest.status == "success" else 1)

    elif args.tier == "monthly":
        from app.backup_system.monthly import run_monthly_backup
        manifest = run_monthly_backup()
        print(json.dumps(manifest.to_dict(), indent=2, default=str))
        sys.exit(0 if manifest.status == "success" else 1)

    elif args.tier == "verify":
        from app.backup_system.verify import run_verification
        result = run_verification()
        print(json.dumps(result, indent=2, default=str))
        sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
