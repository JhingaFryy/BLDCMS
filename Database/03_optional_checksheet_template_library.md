# Optional: Loading the Standard BL-DCMS Checksheet Template Library

`01_schema.sql` and `02_bootstrap_seed.sql` give you an empty, working BL-DCMS install: schema
plus one Administrator login. No Sections, Equipment, Locomotives, or Checksheet Templates are
included — a brand-new shed is expected to build these to match its own workshop.

You have two ways to populate them:

## Option A — Build your own (recommended for a genuinely different shed layout)

Log in as the bootstrap Administrator and use the Dashboard to create Sections, Equipment,
Locomotive records, and Checksheet Templates (Templates support a visual field builder — no SQL
or code required). This guarantees the result matches your shed's actual sections/equipment/
maintenance checklists.

## Option B — Reuse the existing template library

`Backend/scripts/` ships 146 `seed_*.py` scripts, each one creating a single real checksheet
template (e.g. `seed_bogie_overhauling_conv_template.py`, `seed_traction_motor_assembly_template.py`)
as originally authored for Electric Loco Shed, BL. These are genuine maintenance checklists, not
test/dummy data — reusing them can save significant setup time if your shed's checksheet content
substantially overlaps.

To run them against a freshly-installed database:

```bash
cd Backend
source venv/bin/activate
export DATABASE_URL="postgresql://YOUR_DB_USER:YOUR_DB_PASSWORD@YOUR_DATABASE_HOST:5432/YOUR_DB_NAME"

# Each script is independent and idempotent (safe to re-run) - run all of them, or hand-pick
# only the ones matching equipment your shed actually maintains.
for f in scripts/seed_*.py; do
    echo "== $f =="
    python "$f"
done
```

Each script creates its own Section/Equipment rows if they don't already exist, then the
Template + its fields. Read a script before running it if you want to understand exactly what it
creates — they are plain, readable Python using the same `app.services` layer the API itself
uses (not raw SQL), so they stay valid even if the schema evolves via a future migration.

`Backend/scripts/apply_migration_*.py` (12 scripts) apply schema changes on top of an
already-populated database — **not needed for a fresh install** (`01_schema.sql` already
reflects every migration through 018). Keep them only if you plan to track this project's future
schema changes yourself; otherwise they're safe to ignore.
