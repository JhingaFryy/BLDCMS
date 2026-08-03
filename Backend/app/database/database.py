import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base

# Override via the DATABASE_URL environment variable - see CHANGE_CONFIGURATION.md. This fallback
# is a local-development convenience only; production ALWAYS sets DATABASE_URL explicitly via the
# systemd unit's Environment= line.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://YOUR_DB_USER:YOUR_DB_PASSWORD@localhost:5432/YOUR_DB_NAME",
)

engine = create_engine(
    DATABASE_URL,
    # Module 43: the previous defaults (pool_size=5, max_overflow=10 - i.e. no explicit args at
    # all) cap this app at 15 concurrent DB connections. Load-tested: 60 concurrent requests
    # against a real endpoint made every single one time out at 30s
    # (sqlalchemy.exc.TimeoutError: QueuePool limit ... reached) even though the server process
    # itself stayed up and responded normally right after - the app was fully unresponsive to new
    # requests for the whole burst, not gracefully degraded. Raised to a size with real headroom
    # under Postgres's max_connections=100 (confirmed live), leaving room for the admin CLI and
    # Postgres's own reserved superuser connections. pool_pre_ping=True also fixes a separate,
    # independently-observed issue: a long-idle pooled connection going stale
    # (psycopg2.OperationalError: SSL connection has been closed unexpectedly) and crashing
    # whichever request happened to draw it first - pre_ping tests each connection with a cheap
    # SELECT 1 before handing it out, transparently discarding and replacing a dead one instead.
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=1800,
)
# Deliberately not echo=True: that flag makes SQLAlchemy check its own per-engine logger
# (named "sqlalchemy.engine.Engine", not "sqlalchemy.engine") for handlers, and if it finds none,
# attaches its own StreamHandler(sys.stdout) directly (sqlalchemy.log._add_default_handler) -
# completely bypassing app.core.logging's centralized setup (root/console/file handlers,
# admin_cli's console suppression, etc.). SQL query logging is still fully controlled via that
# module instead: app.core.logging.configure_logging() sets the "sqlalchemy.engine" logger to
# INFO with a database.log file handler, and the per-engine child logger inherits that level and
# propagates through the normal logging hierarchy - same log content, but through one logging
# configuration instead of two independent ones.

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def initialize_db():
    import app.models.activity_log  # noqa: F401
    import app.models.checksheet_header  # noqa: F401
    import app.models.checksheet_template  # noqa: F401
    import app.models.checksheet_value  # noqa: F401
    import app.models.device_info  # noqa: F401
    import app.models.digital_signature  # noqa: F401
    import app.models.equipment  # noqa: F401
    import app.models.locomotive  # noqa: F401
    import app.models.notification  # noqa: F401
    import app.models.otp_log  # noqa: F401
    import app.models.section  # noqa: F401
    import app.models.section_equipment_map  # noqa: F401
    import app.models.system_setting  # noqa: F401
    import app.models.template_field  # noqa: F401
    import app.models.user  # noqa: F401
    import app.models.user_session  # noqa: F401

    Base.metadata.create_all(bind=engine)


initialize_db()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
