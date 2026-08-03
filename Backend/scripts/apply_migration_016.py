"""
Applies migrations/016_widen_digital_signature_dn_columns.sql against the live database.

Run once: `venv/bin/python scripts/apply_migration_016.py`

Module 40: widens digital_signatures.certificate_subject/certificate_issuer from VARCHAR(255) to
TEXT - a real Class-III DSC's Distinguished Name can exceed 255 characters (see the migration file
for the production traceback this fixes).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.database import engine

MIGRATION_FILE = Path(__file__).resolve().parent.parent / "migrations" / "016_widen_digital_signature_dn_columns.sql"


def main():
    sql = MIGRATION_FILE.read_text()

    lines = sql.splitlines()
    stripped = "\n".join(line for line in lines if not line.strip().startswith("--"))
    statements = [s.strip() for s in stripped.split(";") if s.strip()]

    with engine.begin() as conn:
        for statement in statements:
            conn.exec_driver_sql(statement)

    print(f"Applied {len(statements)} statement(s) from {MIGRATION_FILE.name}")


if __name__ == "__main__":
    main()
