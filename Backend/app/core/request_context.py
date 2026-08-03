"""Per-request logging context, propagated via contextvars so any code running within a request
(middleware, dependencies, service-layer functions) can contribute to or read the same context
without it being threaded through every function signature - this is what lets
app.core.json_logging's RequestContextFilter inject Request ID/user identity into every log line
a request produces, satisfying "every API automatically includes this metadata without requiring
individual endpoints to duplicate logging code."

contextvars are correctly isolated per-asyncio-Task, and Starlette/FastAPI run each request in its
own Task, so concurrent requests never see each other's context - no locking needed.
"""
from __future__ import annotations

import contextvars
from dataclasses import dataclass
from typing import Optional


@dataclass
class RequestContext:
    request_id: str = "-"
    client_ip: str = "-"
    user_agent: str = "-"
    employee_id: Optional[str] = None
    user_name: Optional[str] = None
    role: Optional[str] = None
    section: Optional[str] = None


_DEFAULT = RequestContext()

_current: contextvars.ContextVar[RequestContext] = contextvars.ContextVar(
    "request_context", default=_DEFAULT
)


def start_request_context(request_id: str, client_ip: str, user_agent: str) -> RequestContext:
    """Called once per request, at the very start of ApiLoggingMiddleware.dispatch(). Sets a
    *new* RequestContext instance (never mutates the default), so requests never leak state
    into each other even if something upstream forgot to clean up."""
    ctx = RequestContext(request_id=request_id, client_ip=client_ip, user_agent=user_agent)
    _current.set(ctx)
    return ctx


def get_request_context() -> RequestContext:
    return _current.get()


def set_authenticated_user(
    employee_id: str,
    user_name: str,
    role: str,
    section: Optional[str] = None,
) -> None:
    """Called by app.security.dependencies.get_current_user() once a request's identity is known
    (which happens *after* ApiLoggingMiddleware has already started the request context) - mutates
    the current context in place so the middleware's own end-of-request log line, and everything
    logged in between, picks up the resolved identity without needing it passed explicitly."""
    ctx = _current.get()
    ctx.employee_id = employee_id
    ctx.user_name = user_name
    ctx.role = role
    ctx.section = section
