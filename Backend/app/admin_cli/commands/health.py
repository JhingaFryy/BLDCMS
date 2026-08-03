"""Module 44: System Administration CLI - health/status commands.

Pure passthrough to the existing app/services/system_health_service.py (the same service the
Dashboard's own System Health page already calls over HTTP) - no health-check logic is
duplicated here.
"""
from __future__ import annotations

from app.database.database import SessionLocal
from app.services import system_health_service


def get_overview() -> dict:
    db = SessionLocal()
    try:
        return system_health_service.get_overview(db)
    finally:
        db.close()


def get_services_status() -> list:
    db = SessionLocal()
    try:
        return system_health_service.get_service_status(db)
    finally:
        db.close()


def get_database_stats() -> dict:
    db = SessionLocal()
    try:
        return system_health_service.get_database_stats(db)
    finally:
        db.close()


def get_server_info() -> dict:
    db = SessionLocal()
    try:
        return system_health_service.get_server_info(db)
    finally:
        db.close()
