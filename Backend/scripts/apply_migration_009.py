"""
Applies migrations/009_validation_engine.sql against the live database.

Run once: `venv/bin/python scripts/apply_migration_009.py`

Adds validation_rule/validation_threshold/negative_values to template_fields (ALTER on an
existing table, which Base.metadata.create_all() never does at app startup - must be applied
explicitly).

All statements run inside a single transaction (engine.begin()), and every ALTER uses
IF NOT EXISTS, so re-running this script after a successful apply is a safe no-op.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.database import engine

MIGRATION_FILE = Path(__file__).resolve().parent.parent / "migrations" / "009_validation_engine.sql"


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
