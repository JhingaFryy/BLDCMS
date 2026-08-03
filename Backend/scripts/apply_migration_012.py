"""
Applies migrations/012_equipmentless_checksheets.sql against the live database.

Run once: `venv/bin/python scripts/apply_migration_012.py`

Drops the NOT NULL constraint on checksheet_header.equipment_id so M6-HR (which has no equipment
at all) can store checksheet rows with equipment_id = NULL.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.database import engine

MIGRATION_FILE = Path(__file__).resolve().parent.parent / "migrations" / "012_equipmentless_checksheets.sql"


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
