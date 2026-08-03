"""
Applies migrations/017_remove_dsc_local_signer_setting.sql against the live database.

Run once: `venv/bin/python scripts/apply_migration_017.py`

Module 41.5: removes the orphaned dsc.local_signer_base_url system setting left behind by the
deprecated IREPSSigner (DSC v1) implementation, now fully removed in favor of eMudhra emBridge.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.database import engine

MIGRATION_FILE = Path(__file__).resolve().parent.parent / "migrations" / "017_remove_dsc_local_signer_setting.sql"


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
