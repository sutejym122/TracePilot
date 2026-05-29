"""Scheduled tasks. Kept as plain callables so the scheduler choice (APScheduler
now, possibly Celery later) stays a localized concern.
"""
from app.database import SessionLocal


def run_health_checks() -> None:
    """Ping every service and record results.

    Opens its own DB session (it runs outside any request). Phase 4 fills this
    in by iterating services and calling domain.health_checker.check_service —
    the exact same function the manual-trigger route uses.
    """
    db = SessionLocal()
    try:
        # TODO(phase4):
        #   for service in db.query(Service).all():
        #       await/await-run check_service(service, db)
        pass
    finally:
        db.close()
