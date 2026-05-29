"""APScheduler instance and lifecycle helpers.

start_scheduler() registers the recurring health-check job and is called from
the app's lifespan startup; shutdown_scheduler() stops it cleanly. In-process
background scheduling (Phase 2 decision) — no separate worker process for MVP.
"""
from apscheduler.schedulers.background import BackgroundScheduler

from app.config import settings
from app.workers.tasks import run_health_checks

scheduler = BackgroundScheduler()


def start_scheduler() -> None:
    if scheduler.running:
        return
    scheduler.add_job(
        run_health_checks,
        trigger="interval",
        seconds=settings.HEALTH_CHECK_INTERVAL_SECONDS,
        id="health_checks",
        replace_existing=True,
        max_instances=1,  # don't pile up if a run overruns the interval
    )
    scheduler.start()


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
