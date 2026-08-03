"""Structured (JSON) logging support: a logging.Filter that injects the current request's context
(app.core.request_context) into every LogRecord reaching a handler that uses it, and a
JsonLogFormatter that renders one JSON object per line, merging in any extra fields a call site
passed via `logger.info(msg, extra={...})`.

Security note: every field on every log entry passes through _redact() before being serialized -
this is a blanket safety net (not a substitute for callers being careful) against ever writing a
password, OTP, JWT, session cookie, DSC PIN, private key, or raw certificate to a log file, per the
"never log" requirements. It matches on the field NAME (case/separator-insensitive), so it catches
this even if a future call site passes a sensitive value under a slightly different key.
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone

from app.core.request_context import get_request_context

# Every field name is normalized (lowercased, underscores/hyphens stripped) before comparison, so
# "otp_code", "otp-code", "OTP", "otpValue" etc. all match a single entry here.
_SENSITIVE_FIELD_NAMES = {
    "password", "passwordhash", "otp", "otpcode", "otpvalue", "plainotp",
    "token", "accesstoken", "refreshtoken", "jwt", "authorization", "bearer",
    "sessioncookie", "cookie", "pin", "keystorepassphrase",
    "privatekey", "secretkey", "secret",
    "certificatedata", "certificateder", "certraw", "rawcertificate", "derbase64",
}


def _normalize_key(key: str) -> str:
    return re.sub(r"[_\-\s]", "", str(key)).lower()


def _redact(key: str, value):
    if _normalize_key(key) in _SENSITIVE_FIELD_NAMES:
        return "[REDACTED]"
    return value


# Standard attributes every LogRecord already has - anything else in record.__dict__ is an
# application-supplied `extra` field and gets merged into the JSON payload.
_STANDARD_RECORD_ATTRS = {
    "name", "msg", "args", "levelname", "levelno", "pathname", "filename", "module",
    "exc_info", "exc_text", "stack_info", "lineno", "funcName", "created", "msecs",
    "relativeCreated", "thread", "threadName", "threadingId", "processName", "process",
    "taskName", "getMessage",
}


class RequestContextFilter(logging.Filter):
    """Attached to specific handlers (not globally) - see configure_logging(). Injects the
    current request's context as record attributes so JsonLogFormatter (or any formatter) can
    reference them, even for log calls made deep in service-layer code that never received the
    request object directly.

    Only fills in a field if the call site didn't already set it via `extra={...}` (checked with
    hasattr, since logging.LogRecord sets extras as plain attributes) - the ambient request
    context is a *default*, not an override. This matters for log_activity(), which is sometimes
    called with an explicit employee_id for a user other than the currently-authenticated caller
    (e.g. an admin acting on someone else's record) - without this check, this filter would
    silently clobber that with the requester's own identity."""

    def filter(self, record: logging.LogRecord) -> bool:
        ctx = get_request_context()
        if not hasattr(record, "request_id"):
            record.request_id = ctx.request_id
        if not hasattr(record, "client_ip"):
            record.client_ip = ctx.client_ip
        if not hasattr(record, "user_agent"):
            record.user_agent = ctx.user_agent
        if not hasattr(record, "employee_id"):
            record.employee_id = ctx.employee_id or "-"
        if not hasattr(record, "user_name"):
            record.user_name = ctx.user_name or "-"
        if not hasattr(record, "role"):
            record.role = ctx.role or "-"
        if not hasattr(record, "section"):
            record.section = ctx.section or "-"
        return True


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
            "employee_id": getattr(record, "employee_id", "-"),
            "user_name": getattr(record, "user_name", "-"),
            "role": getattr(record, "role", "-"),
            "section": getattr(record, "section", "-"),
            "client_ip": getattr(record, "client_ip", "-"),
            "user_agent": getattr(record, "user_agent", "-"),
        }

        for key, value in record.__dict__.items():
            if key in _STANDARD_RECORD_ATTRS or key in payload:
                continue
            payload[key] = _redact(key, value)

        if record.exc_info:
            payload["stack_trace"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)
