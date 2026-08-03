import os

from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

# Configured before any other app.* module is imported below, so that by the time
# app.database.database creates the (echo=True) SQLAlchemy engine, and any service module
# grabs a logger, the handlers set up here are already in place - see app/core/logging.py
# for why this ordering (and the redundant startup-event call further down) matters.
from app.core.logging import ApiLoggingMiddleware, configure_logging, get_logger
configure_logging()

from app.api.section import router as section_router
from app.api.locomotive import router as locomotive_router
from app.api.equipment import router as equipment_router
from app.api.section_equipment_map import router as section_equipment_map_router
from app.api.checksheet_template import router as checksheet_template_router
from app.api.template_field import router as template_field_router
from app.api.checksheet import router as checksheet_router
from app.api.digital_signature_v2 import router as digital_signature_v2_router
from app.api.dsc_client_events import router as dsc_client_events_router
from app.api.auth import router as auth_router
from app.api.mobile_auth import router as mobile_auth_router
from app.api.user import router as user_router
from app.api.system_setting import router as system_setting_router
from app.api.notification import router as notification_router
from app.api.system_health import router as system_health_router
from app.api.search import router as search_router
from app.api.activity_log import router as activity_log_router
from app.api.otp_log import router as otp_log_router

app = FastAPI(
    title="Railway Digital Checksheet API",
    version="1.0"
)


@app.on_event("startup")
def _reconfigure_logging_on_startup() -> None:
    # Defensive second pass: guarantees our handlers (particularly on the uvicorn/uvicorn.access/
    # uvicorn.error loggers) are still the ones in effect once the server is actually serving,
    # regardless of exactly how/when this process was started. Safe to call repeatedly.
    configure_logging()
    get_logger("app.api").info("Application startup complete - logging configured.")


_security_logger = get_logger("app.security")


@app.exception_handler(RequestValidationError)
async def _log_invalid_payload(request: Request, exc: RequestValidationError):
    """"Invalid request payloads" security event - logs the field paths Pydantic rejected (never
    the submitted values themselves, since a rejected password/OTP/PIN field's value would
    otherwise end up in this log) before delegating to FastAPI's own default handler, which is
    called unchanged so the actual 422 response body sent to the client is not affected by this."""
    _security_logger.warning(
        "Invalid request payload",
        extra={
            "action": "INVALID_PAYLOAD",
            "success": False,
            "method": request.method,
            "endpoint": request.url.path,
            "invalid_fields": [".".join(str(p) for p in err["loc"]) for err in exc.errors()],
        },
    )
    return await request_validation_exception_handler(request, exc)


# =========================
# CORS Configuration
# =========================

# Override via the CORS_ORIGINS environment variable (comma-separated) - see
# CHANGE_CONFIGURATION.md. This fallback is a local-development convenience only; production
# ALWAYS sets CORS_ORIGINS explicitly via the systemd unit's Environment= line.
_default_origins = "http://localhost:3000"
origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", _default_origins).split(",") if origin.strip()]

# Module 42: ApiLoggingMiddleware must be added BEFORE CORSMiddleware. Starlette's add_middleware()
# inserts at index 0 and wraps in reverse, so whichever is added LAST ends up OUTERMOST. With
# ApiLoggingMiddleware outer (the old order), a response it constructs directly (e.g. the 500 body
# below) would never pass back through CORSMiddleware and the browser would treat it as a
# CORS-blocked, opaque failure - the request_id would never actually reach the client. Adding
# ApiLoggingMiddleware first makes CORSMiddleware outer, so it sees every response, including this
# middleware's own constructed ones.
app.add_middleware(ApiLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# API Routes
# =========================

app.include_router(section_router)
app.include_router(locomotive_router)
app.include_router(equipment_router)
app.include_router(section_equipment_map_router)
app.include_router(checksheet_template_router)
app.include_router(template_field_router)
app.include_router(checksheet_router)
app.include_router(digital_signature_v2_router)
app.include_router(dsc_client_events_router)
app.include_router(auth_router)
app.include_router(mobile_auth_router)
app.include_router(user_router)
app.include_router(system_setting_router)
app.include_router(notification_router)
app.include_router(system_health_router)
app.include_router(search_router)
app.include_router(activity_log_router)
app.include_router(otp_log_router)


@app.get("/")
def home():
    return {
        "status": "Server Running",
        "project": "Railway Digital Checksheet Management System"
    }
