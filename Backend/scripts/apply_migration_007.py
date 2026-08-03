"""
Applies migrations/007_dynamic_template_engine.sql against the live database.

Run once: `venv/bin/python scripts/apply_migration_007.py`

Unlike migrations 001/005/006 (new tables, applied automatically by
Base.metadata.create_all() at app startup), 007 ALTERs two existing tables
(template_fields, checksheet_templates), which create_all() never does - it
must be applied explicitly, exactly once, via this script.

All statements run inside a single transaction (engine.begin()), and every
ALTER/CREATE INDEX uses IF NOT EXISTS, so re-running this script after a
successful apply is a safe no-op.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.database import engine

MIGRATION_FILE = Path(__file__).resolve().parent.parent / "migrations" / "007_dynamic_template_engine.sql"


def main():
    sql = MIGRATION_FILE.read_text()

    # Strip full comment LINES first, then split on ';' - a naive sql.split(';') before
    # stripping comments can misidentify a multi-line comment block immediately followed
    # (no blank line) by a real statement as comment-only and silently skip it.
    lines = sql.splitlines()
    stripped = "\n".join(line for line in lines if not line.strip().startswith("--"))
    statements = [s.strip() for s in stripped.split(";") if s.strip()]

    with engine.begin() as conn:
        for statement in statements:
            conn.exec_driver_sql(statement)

    print(f"Applied {len(statements)} statements from {MIGRATION_FILE.name}.")


if __name__ == "__main__":
    main()
