"""
Applies migrations/014_remove_dsc_development_mode.sql against the live database.

Run once: `venv/bin/python scripts/apply_migration_014.py`

Removes the Digital Signature Development/Test Mode: drops digital_signatures.
is_development_signature and deletes the dsc.development_mode system setting. From this point
on, checksheet approval only ever signs with a real Class-III DSC on a PKCS#11 USB crypto token.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.database import engine

MIGRATION_FILE = Path(__file__).resolve().parent.parent / "migrations" / "014_remove_dsc_development_mode.sql"


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
