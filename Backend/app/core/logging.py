"""Centralized logging configuration.

Every module in this backend that wants to log should call `get_logger(name)` from here
instead of calling `logging.getLogger(...)` directly and wiring up its own handlers. This
module owns all handler/formatter/rotation setup in one place, and writes to `logs/` at the
project root (created automatically if missing).

`configure_logging()` is idempotent and safe to call more than once - it always clears and
re-adds its own handlers rather than accumulating duplicates. It must be called before any
other application module that logs is imported, and is called again from a FastAPI startup
event as a defensive second pass, because uvicorn's own `Config.__init__` (which runs before
`main:app` is even imported) installs its own console-only handlers on the `uvicorn`,
`uvicorn.access` and `uvicorn.error` loggers with `propagate=False` - this module intentionally
overrides that so those loggers also write to `uvicorn.log` and keep propagating to the root
logger's console handler.
"""

import logging
import os
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from app.core import metrics
from app.core.request_context import start_request_context

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
LOG_DIR = BACKEND_DIR / "logs"

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

IST = ZoneInfo("Asia/Kolkata")

# Same flag otp_service.py already reads - kept in sync here so the rest of this module (and any
# future caller) can make the same DEBUG-aware decisions without re-parsing the env var.
DEBUG = os.getenv("DEBUG", "true").lower() in ("1", "true", "yes")

_configured = False


def _formatter() -> logging.Formatter:
    return logging.Formatter(LOG_FORMAT, DATE_FORMAT)


class _ISTFormatter(logging.Formatter):
    """Module 33.1: every other log file's timestamp is whatever the server process's local time
    is (usually UTC on this deployment - see pdf_service.py's own separate UTC->IST conversion for
    checksheet PDFs). Vite Connection Logs are read by a human comparing them against what they
    just saw happen in their own browser, so the timestamp needs to be IST directly in the line
    rather than requiring a mental UTC offset - this formatter overrides formatTime() to convert
    the record's creation time (always a real UTC epoch timestamp) into Asia/Kolkata."""

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        ist_dt = datetime.fromtimestamp(record.created, tz=IST)
        return ist_dt.strftime(datefmt or DATE_FORMAT)


def _vite_formatter() -> logging.Formatter:
    # "[2026-07-16 10:35:18 IST] INFO [Dashboard] Dashboard connected to Backend API" - one line
    # per event, Timestamp/Severity/Source/Message all in the single line the module asked for, in
    # a format simple enough for the Dashboard's log viewer to parse client-side for severity
    # badges/filtering without needing a structured (JSON) log line.
    return _ISTFormatter("[%(asctime)s IST] %(levelname)s %(message)s", DATE_FORMAT)


def _json_file_handler(filename: str, level: int = logging.INFO) -> logging.Handler:
    """Like _file_handler(), but JSON-formatted (app.core.json_logging.JsonLogFormatter) and with
    RequestContextFilter attached, so every entry automatically carries Request ID/user identity/
    IP/user-agent alongside whatever the call site's own message and `extra={}` fields say - used
    for the security-relevant logs (api.log, security.log, auth.log, otp.log, activity.log), not
    for infrastructure logs (database.log, uvicorn.log, vite_connection.log) that have their own
    established formats and consumers."""
    from app.core.json_logging import JsonLogFormatter, RequestContextFilter

    handler = logging.FileHandler(LOG_DIR / filename, mode="a", encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(JsonLogFormatter())
    handler.addFilter(RequestContextFilter())
    return handler


def _file_handler(filename: str, level: int = logging.INFO, formatter: logging.Formatter | None = None) -> logging.Handler:
    # Module 30: a single continuously-appending file per category, never rotated - this used to
    # be a TimedRotatingFileHandler(when="midnight", backupCount=14), which created a new dated
    # file (e.g. application.log.2026-07-13) every midnight. A plain FileHandler in append mode
    # keeps writing to the same file (e.g. logs/application.log) indefinitely; formatting is
    # unchanged (same Formatter as before), only the rotation behavior is removed.
    handler = logging.FileHandler(
        LOG_DIR / filename,
        mode="a",
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(formatter or _formatter())
    return handler


def _reset_logger(name: str, level: int = logging.INFO, propagate: bool = True) -> logging.Logger:
    """Fetches a named logger, clears any handlers it already has (its own or ones another
    library - e.g. SQLAlchemy's echo=True or uvicorn's own Config - may have attached), and sets
    level/propagate. Handlers are added by the caller afterwards."""
    target_logger = logging.getLogger(name)
    for handler in list(target_logger.handlers):
        target_logger.removeHandler(handler)
    target_logger.setLevel(level)
    target_logger.propagate = propagate
    return target_logger


def configure_logging(enable_console: bool = True) -> None:
    """`enable_console=False` is for app.admin_cli.main specifically: that CLI shares this same
    logging setup (via the same SessionLocal/service-layer imports the API server uses), but it is
    a standalone, script-friendly command whose stdout must be exactly the queried result (see
    admin_cli.main._print) - not interleaved with every SQLAlchemy query (Engine(echo=True) logs
    through here) and every app.* log line the API server is meant to stream live to its own
    console. File logging (application.log, database.log, etc.) is unaffected either way - only
    whether the root logger ALSO gets a console StreamHandler."""
    global _configured

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root_level = logging.DEBUG if DEBUG else logging.INFO

    root_logger = _reset_logger("", level=root_level)
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(root_level)
        console_handler.setFormatter(_formatter())
        root_logger.addHandler(console_handler)
    root_logger.addHandler(_file_handler("application.log"))
    root_logger.addHandler(_file_handler("error.log", level=logging.ERROR))

    # Everything below propagates up to the root logger above, which is what keeps requirement 4
    # ("every logger must also continue printing to console") satisfied without attaching a
    # console handler to each one individually (that would print every line twice).
    #
    # otp/auth/api/security/activity are all JSON-formatted with RequestContextFilter attached
    # (see _json_file_handler) - these are the security-relevant, audit-facing logs. Everything
    # else below keeps its pre-existing plain-text format, since it has its own established
    # consumers (database.log/uvicorn.log by convention, vite_connection.log by the Dashboard's
    # own log viewer) that this change does not need to and should not disturb.
    _reset_logger("app.otp").addHandler(_json_file_handler("otp.log"))
    _reset_logger("app.auth").addHandler(_json_file_handler("auth.log"))
    _reset_logger("app.api").addHandler(_json_file_handler("api.log"))
    # New: security-relevant events that aren't naturally "auth" or "api" telemetry - invalid/
    # expired JWTs, permission-denied, invalid request payloads, certificate mismatches, signature
    # verification failures, repeated failed authentication. See app/security/dependencies.py,
    # app/security/jwt.py, main.py's RequestValidationError handler, and
    # app/services/digital_signature*/*.
    _reset_logger("app.security").addHandler(_json_file_handler("security.log"))
    # New: every log_activity() call (checksheet create/update/submit/approve/reject, digital
    # signature lifecycle, user/section/template management, ...) already writes a row to the
    # activity_logs DB table for the Dashboard's Activity Timeline - this additionally writes the
    # same event to a grep/tail-able JSON file, without any individual call site needing to change
    # (see activity_log_service.log_activity).
    _reset_logger("app.activity").addHandler(_json_file_handler("activity.log"))
    # New: the detailed certificate-comparison logging in digital_signature_v2_service.py
    # (declared-vs-embedded subject/issuer/serial/SHA-1/SHA-256/DER-length, for every sign
    # attempt, not just failures) - previously fell through to the plain-text root logger with no
    # request context attached; now JSON-formatted and context-aware like everything else here.
    _reset_logger("app.digital_signature_v2").addHandler(_json_file_handler("digital_signature.log"))

    # Module 33.1: Dashboard <-> Backend connectivity events (Vite dev-server lifecycle, HMR,
    # axios connect/disconnect/timeout/CORS) - written to their own file/formatter (see
    # _vite_formatter) rather than propagating through the shared LOG_FORMAT used above.
    _reset_logger("app.vite").addHandler(_file_handler("vite_connection.log", formatter=_vite_formatter()))

    # SQLAlchemy logs SQL through this exact logger name when Engine(echo=True) is set (see
    # app/database/database.py) - binding a handler here, rather than touching the engine, is
    # enough to route that existing SQL logging into database.log.
    _reset_logger("sqlalchemy.engine").addHandler(_file_handler("database.log"))

    # uvicorn's own Config.__init__ already configured these three with propagate=False and a
    # console-only handler before main.py was even imported - reset+rebind so they also land in
    # uvicorn.log and keep bubbling up to the root console handler.
    for uvicorn_logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        _reset_logger(uvicorn_logger_name).addHandler(_file_handler("uvicorn.log"))

    _configured = True


def get_logger(name: str) -> logging.Logger:
    if not _configured:
        configure_logging()
    return logging.getLogger(name)


class ApiLoggingMiddleware(BaseHTTPMiddleware):
    """Logs every FastAPI request to api.log, one structured JSON entry each, with the full field
    set (Request ID, identity, IP, User-Agent, method, endpoint, status, duration, success/
    failure) - this is what satisfies "every API automatically includes this metadata without
    requiring individual endpoints to duplicate logging code": every other logger in the app also
    picks up Request ID/identity automatically via RequestContextFilter, but this middleware is
    the one place that owns the per-request summary line and the Request ID's lifecycle.

    Ordering: this middleware starts the request context (app.core.request_context) *before*
    routing/dependency-injection runs, so a Request ID exists for the whole request including
    dependencies like get_current_user(). Identity fields are unknown at that point (auth hasn't
    run yet) - get_current_user() fills them in via set_authenticated_user() once resolved, and
    since dicts/dataclasses are mutated in place in the same context, this middleware's own
    end-of-request log line (logged *after* call_next() returns, i.e. after auth has already run)
    picks up the by-then-resolved identity automatically.

    On an uncaught exception, logs the full stack trace (Username, Employee ID, Role, Client IP,
    Endpoint, Stack Trace, Request ID) before re-raising unchanged - this middleware never alters
    the response, only observes it."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self._logger = get_logger("app.api")

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "-")
        start_request_context(request_id, client_ip, user_agent)
        request.state.request_id = request_id

        start = time.monotonic()

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.monotonic() - start) * 1000
            self._logger.exception(
                "%s %s failed after %.1fms",
                request.method,
                request.url.path,
                duration_ms,
                extra={
                    "action": "UNHANDLED_EXCEPTION",
                    "method": request.method,
                    "endpoint": request.url.path,
                    "status_code": 500,
                    "duration_ms": round(duration_ms, 1),
                    "success": False,
                },
            )
            metrics.record_request(request.method, request.url.path, 500, round(duration_ms, 1))
            # Module 42: never let a stack trace/exception detail reach the client - the log line
            # above already captured everything (request_id, identity, IP, endpoint, stack trace,
            # exception type/message via RequestContextFilter + logger.exception). The HTTP
            # response gets only a request_id (for support correlation) and a friendly message.
            return JSONResponse(
                status_code=500,
                content={
                    "request_id": request_id,
                    "message": "An unexpected error occurred. Please try again or contact support with this request ID.",
                },
                headers={"X-Request-ID": request_id},
            )

        duration_ms = (time.monotonic() - start) * 1000
        success = response.status_code < 400
        self._logger.info(
            "%s %s -> %d (%.1fms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            extra={
                "action": "HTTP_REQUEST",
                "method": request.method,
                "endpoint": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 1),
                "success": success,
            },
        )
        metrics.record_request(request.method, request.url.path, response.status_code, round(duration_ms, 1))
        response.headers["X-Request-ID"] = request_id
        return response
