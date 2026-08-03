"""
Applies migrations/015_device_info.sql against the live database.

Run once: `venv/bin/python scripts/apply_migration_015.py`

Module 44 (System Administration CLI): creates the device_info table, a device registry
populated by upserting on every successful Android login/OTP-verify. Read-only for the CLI;
never touched by any authentication/authorization code path.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.database import engine

MIGRATION_FILE = Path(__file__).resolve().parent.parent / "migrations" / "015_device_info.sql"


def main():
    sql = MIGRATION_FILE.read_text()

    lines = sql.splitlines()
    stripped = "\n".join(line for line in lines if not line.strip().startswith("--"))
    statements = [s.strip() for s in stripped.split(";") if s.strip()]

    with engine.begin() as conn:
        for statement in statements:
            conn.exec_driver_sql(statement)

    print(f"Applied {len(statements)} statements from {MIGRATION_FILE.name}.")


if __name__ == "__main__":
    main()
