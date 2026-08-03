"""
Applies migrations/008_template_field_soft_delete.sql against the live database.

Run once: `venv/bin/python scripts/apply_migration_008.py`

Adds is_deleted/deleted_at to template_fields (ALTER on an existing table, which
Base.metadata.create_all() never does at app startup - must be applied explicitly).

All statements run inside a single transaction (engine.begin()), and every
ALTER/CREATE INDEX uses IF NOT EXISTS, so re-running this script after a
successful apply is a safe no-op.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.database import engine

MIGRATION_FILE = Path(__file__).resolve().parent.parent / "migrations" / "008_template_field_soft_delete.sql"


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
