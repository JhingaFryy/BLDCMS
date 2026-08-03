"""
Applies migrations/018_checksheet_indexes.sql against the live database.

Run once: `venv/bin/python scripts/apply_migration_018.py`

Module 43: adds indexes on checksheet_header/checksheet_value/digital_signatures columns that
are heavily filtered/joined on but had no index beyond the primary key - purely additive,
no behavior change.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.database import engine

MIGRATION_FILE = Path(__file__).resolve().parent.parent / "migrations" / "018_checksheet_indexes.sql"


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
