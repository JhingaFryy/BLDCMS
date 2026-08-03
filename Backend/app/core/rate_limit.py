"""Module 42: lightweight in-memory rate limiting.

Hand-rolled rather than a third-party library - there is no requirements.txt/pyproject.toml
anywhere in this backend to track a new dependency against, and this app runs as a single
uvicorn process (no --workers), so a per-process in-memory counter sees every request and needs
no shared/external store (Redis, etc.).

Every violation is logged via the same `app.security` logger the rest of the security-event
system already uses (see app/security/dependencies.py, app/security/jwt.py) - "repeated
violations generate security log entries" falls out naturally since each one is its own log line,
gr../tail-able in security.log exactly like PERMISSION_DENIED/UNAUTHORIZED_ACCESS.
"""
from __future__ import annotations

import time
from collections import deque
from threading import Lock
from typing import Callable

from fastapi import HTTPException, Request, status

from app.core.logging import get_logger

security_logger = get_logger("app.security")

_PRUNE_EVERY_N_CHECKS = 200


class RateLimiter:
    def __init__(self) -> None:
        self._buckets: dict[str, deque[float]] = {}
        self._lock = Lock()
        self._check_count = 0

    def check(self, key: str, max_requests: int, window_seconds: int, action: str) -> None:
        now = time.monotonic()
        # Namespaced by action, not just key - otherwise e.g. /auth/login and /auth/verify-otp
        # (both keyed by the same client IP) would share one bucket, so a few failed logins could
        # exhaust the budget for an unrelated OTP verification from the same IP/office network.
        bucket_key = f"{action}:{key}"

        with self._lock:
            bucket = self._buckets.setdefault(bucket_key, deque())
            cutoff = now - window_seconds
            while bucket and bucket[0] < cutoff:
                bucket.popleft()

            if len(bucket) >= max_requests:
                security_logger.warning(
                    "Rate limit exceeded",
                    extra={
                        "action": action,
                        "success": False,
                        "rate_limit_key": key,
                        "max_requests": max_requests,
                        "window_seconds": window_seconds,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please try again later.",
                )

            bucket.append(now)

            self._check_count += 1
            if self._check_count % _PRUNE_EVERY_N_CHECKS == 0:
                self._prune_empty_buckets()

    def _prune_empty_buckets(self) -> None:
        empty_keys = [key for key, bucket in self._buckets.items() if not bucket]
        for key in empty_keys:
            del self._buckets[key]


_limiter = RateLimiter()


def check_rate_limit(key: str, max_requests: int, window_seconds: int, action: str) -> None:
    """Direct (non-Depends) entry point, for call sites that already have the key on hand - e.g.
    require_admin(), which wraps every admin-only endpoint in one place rather than needing
    Depends(rate_limit_by_employee(...)) added to each admin route individually."""
    _limiter.check(key, max_requests, window_seconds, action)


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def rate_limit_by_ip(max_requests: int, window_seconds: int, action: str) -> Callable:
    """Dependency factory keyed by client IP - for pre-auth endpoints (login, OTP) where no
    authenticated identity exists yet."""
    def _dependency(request: Request) -> None:
        _limiter.check(_client_ip(request), max_requests, window_seconds, action)
    return _dependency


def rate_limit_by_employee(max_requests: int, window_seconds: int, action: str) -> Callable:
    """Dependency factory keyed by the authenticated caller's employee_id - for already-
    authenticated endpoints (digital signature APIs). Depends on get_current_user() itself so the
    caller's identity is resolved via the one existing auth code path, not re-derived here."""
    from fastapi import Depends

    from app.security.dependencies import get_current_user

    def _check(current_user=Depends(get_current_user)) -> None:
        _limiter.check(current_user.employee_id, max_requests, window_seconds, action)

    return _check
