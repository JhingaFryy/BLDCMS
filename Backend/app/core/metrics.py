"""Module 42: in-memory request-metrics ring buffer.

Populated by ApiLoggingMiddleware on every request (it already computes method/endpoint/
status_code/duration_ms for the api.log line - this just also appends the same values here).
Powers the System Health page's average response time, slowest/most-frequent endpoints, and
recent-failed-requests tiles without needing to parse log files or add a database table.

Deliberately in-process, not persisted: this backend runs as a single uvicorn process (no
--workers, no multi-process deployment), so a per-process buffer sees every request. Resets on
restart - acceptable, since this is "recent activity" data, not audit history (which stays fully
durable in api.log/activity_logs regardless of this buffer).
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Optional

_MAX_RECORDS = 1000


@dataclass
class RequestRecord:
    timestamp: datetime
    method: str
    endpoint: str
    status_code: int
    duration_ms: float


_records: deque[RequestRecord] = deque(maxlen=_MAX_RECORDS)
_lock = Lock()


def record_request(method: str, endpoint: str, status_code: int, duration_ms: float) -> None:
    with _lock:
        _records.append(RequestRecord(
            timestamp=datetime.now(timezone.utc),
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            duration_ms=duration_ms,
        ))


def _snapshot() -> list[RequestRecord]:
    with _lock:
        return list(_records)


def get_average_response_time_ms() -> Optional[float]:
    records = _snapshot()
    if not records:
        return None
    return round(sum(r.duration_ms for r in records) / len(records), 1)


def get_slowest_endpoints(limit: int = 10) -> list[dict]:
    records = _snapshot()
    by_endpoint: dict[str, list[float]] = {}
    for r in records:
        by_endpoint.setdefault(f"{r.method} {r.endpoint}", []).append(r.duration_ms)

    aggregated = [
        {"endpoint": endpoint, "avg_duration_ms": round(sum(durations) / len(durations), 1), "count": len(durations)}
        for endpoint, durations in by_endpoint.items()
    ]
    aggregated.sort(key=lambda item: item["avg_duration_ms"], reverse=True)
    return aggregated[:limit]


def get_most_frequent_endpoints(limit: int = 10) -> list[dict]:
    records = _snapshot()
    counts: dict[str, int] = {}
    for r in records:
        key = f"{r.method} {r.endpoint}"
        counts[key] = counts.get(key, 0) + 1

    aggregated = [{"endpoint": endpoint, "count": count} for endpoint, count in counts.items()]
    aggregated.sort(key=lambda item: item["count"], reverse=True)
    return aggregated[:limit]


def get_recent_failed_requests(limit: int = 20) -> list[dict]:
    records = _snapshot()
    failed = [r for r in records if r.status_code >= 400]
    failed.sort(key=lambda r: r.timestamp, reverse=True)
    return [
        {
            "timestamp": r.timestamp,
            "method": r.method,
            "endpoint": r.endpoint,
            "status_code": r.status_code,
            "duration_ms": r.duration_ms,
        }
        for r in failed[:limit]
    ]


def get_recent_exceptions(limit: int = 20) -> list[dict]:
    # Exceptions are just the status_code == 500 subset of failed requests - no separate buffer.
    records = _snapshot()
    exceptions = [r for r in records if r.status_code == 500]
    exceptions.sort(key=lambda r: r.timestamp, reverse=True)
    return [
        {
            "timestamp": r.timestamp,
            "method": r.method,
            "endpoint": r.endpoint,
            "duration_ms": r.duration_ms,
        }
        for r in exceptions[:limit]
    ]
