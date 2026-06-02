"""Scheduled tasks. Kept as plain callables so the scheduler choice (APScheduler
now, possibly Celery later) stays a localized concern.
"""
import logging

from sqlalchemy import select

from app.database import SessionLocal
from app.domain.health_checker import check_service
from app.models.service import Service

logger = logging.getLogger("tracepilot")


def run_health_checks() -> None:
    """Ping every service that has a health_url and record results.

    Opens its own DB session (it runs outside any request) and reuses the exact
    same domain function the manual-trigger route uses. Services without a
    health_url are skipped. One service's failure never aborts the batch.
    """
    db = SessionLocal()
    try:
        services = db.scalars(
            select(Service).where(Service.health_url.is_not(None))
        ).all()
        for service in services:
            try:
                check_service(db, service)
            except Exception:
                logger.exception("Scheduled health check failed for service %s", service.id)
    finally:
        db.close()


def generate_metrics_for_all_services() -> None:
    """Generate one simulated metric per service.

    Opens its own DB session and reuses the same domain function the manual
    /metrics/simulate route uses. One service's failure never aborts the batch.
    """
    from app.domain.metric_management import generate_simulated_metric

    db = SessionLocal()
    try:
        services = db.scalars(select(Service)).all()
        for service in services:
            try:
                generate_simulated_metric(db, service.id)
            except Exception:
                logger.exception("Scheduled metric generation failed for service %s", service.id)
    finally:
        db.close()