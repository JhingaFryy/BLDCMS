"""
Applies migrations/010_otp_log_plain_otp.sql against the live database.

Run once: `venv/bin/python scripts/apply_migration_010.py`

Adds plain_otp to otp_logs (ALTER on an existing table, which Base.metadata.create_all() never
does at app startup - must be applied explicitly).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.database import engine

MIGRATION_FILE = Path(__file__).resolve().parent.parent / "migrations" / "010_otp_log_plain_otp.sql"


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
