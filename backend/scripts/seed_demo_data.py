"""Seed idempotent demo data for TracePilot.

Creates a single demo user and a realistic payments-team scenario that
exercises the full product loop: service -> release + readiness checklist ->
health/metrics -> incident + timeline. Safe to run repeatedly: it removes the
demo user's existing domain data first, then recreates it. It only ever touches
the demo user's rows.

Run:
    docker compose exec api python scripts/seed_demo_data.py
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone

# Ensure the app package is importable when run as `python scripts/seed_demo_data.py`.
sys.path.insert(0, ".")

from sqlalchemy import select

from app.database import SessionLocal
from app.domain import crud
from app.domain import incident_management as im
from app.domain import metric_management as mm
from app.domain import release_management as rm
from app.domain.auth import register_user
from app.models.incident import Incident
from app.models.release import Release
from app.models.service import Service
from app.models.user import User

DEMO_EMAIL = "demo@tracepilot.dev"
DEMO_PASSWORD = "password123"
DEMO_NAME = "Demo User"


def get_or_create_demo_user(db) -> User:
    user = db.execute(select(User).where(User.email == DEMO_EMAIL)).scalar_one_or_none()
    if user:
        return user
    return register_user(db, DEMO_EMAIL, DEMO_PASSWORD, DEMO_NAME)


def wipe_demo_domain_data(db, user: User) -> None:
    """Delete only this user's services; cascades remove releases, checklists,
    health checks, metrics, incidents, and incident updates."""
    services = crud.list_for_user(db, Service, user.id)
    for svc in services:
        crud.delete_obj(db, svc)
    db.commit()


def seed(db) -> None:
    user = get_or_create_demo_user(db)
    wipe_demo_domain_data(db, user)

    now = datetime.now(timezone.utc)

    # --- Services -----------------------------------------------------------
    payment = crud.create_for_user(db, Service, user.id, {
        "name": "payment-service",
        "owner": "payments-team",
        "environment": "prod",
        "repo_url": "https://github.com/example/payment-service",
        "health_url": "https://example.com",
    })
    auth_svc = crud.create_for_user(db, Service, user.id, {
        "name": "auth-service",
        "owner": "platform-team",
        "environment": "prod",
        "repo_url": "https://github.com/example/auth-service",
        "health_url": "https://example.com",
    })
    notif = crud.create_for_user(db, Service, user.id, {
        "name": "notifications-service",
        "owner": "growth-team",
        "environment": "uat",
        "repo_url": "https://github.com/example/notifications-service",
        "health_url": "https://example.com",
    })

    # --- API metrics --------------------------------------------------------
    # Healthy charge endpoint.
    mm.create_metric(db, payment.id, {
        "endpoint": "/api/payments/charge", "method": "POST",
        "status_code": 200, "latency_ms": 145,
        "request_count": 250, "error_count": 3,
        "captured_at": now - timedelta(minutes=30),
    })
    # Problem refund endpoint (the demo's degradation signal).
    mm.create_metric(db, payment.id, {
        "endpoint": "/api/payments/refund", "method": "POST",
        "status_code": 500, "latency_ms": 1200,
        "request_count": 80, "error_count": 18,
        "captured_at": now - timedelta(minutes=10),
    })
    mm.create_metric(db, auth_svc.id, {
        "endpoint": "/api/auth/login", "method": "POST",
        "status_code": 200, "latency_ms": 90,
        "request_count": 500, "error_count": 1,
        "captured_at": now - timedelta(minutes=20),
    })

    # --- Release + readiness checklist --------------------------------------
    release = rm.create_release(db, {
        "service_id": payment.id,
        "version": "1.0.0",
        "environment": "prod",
        "status": "released",
        "owner": "payments-team",
        "release_notes": "Initial production payment release",
        "released_at": now - timedelta(hours=1),
    })
    # Mark the release "ready" (all five checks) to demonstrate rollback
    # preparedness referenced in the incident timeline.
    checklist = rm.get_checklist_for_release(db, release)
    rm.update_checklist(db, checklist, {
        "tests_passed": True,
        "security_review_done": True,
        "rollback_plan_ready": True,
        "monitoring_ready": True,
        "stakeholder_approval": True,
    })

    # A second, still-in-progress release on another service for breadth.
    rm.create_release(db, {
        "service_id": auth_svc.id,
        "version": "2.3.1",
        "environment": "prod",
        "status": "testing",
        "owner": "platform-team",
        "release_notes": "Token rotation hardening",
        "released_at": None,
    })

    # --- Incident + timeline ------------------------------------------------
    incident = im.create_incident(db, {
        "service_id": payment.id,
        "title": "Elevated payment refund errors after release 1.0.0",
        "severity": "high",
        "status": "open",
        "summary": "Refund endpoint is returning elevated 500s after the production release.",
        "root_cause": None,
        "started_at": now - timedelta(minutes=12),
        "resolved_at": None,
    })
    im.add_update(db, incident, {
        "message": "Error rate increased on POST /api/payments/refund shortly after release 1.0.0.",
        "author": "Sam",
        "status": None,
    })
    db.refresh(incident)
    im.add_update(db, incident, {
        "message": "On-call is investigating payment-service metrics and recent release changes.",
        "author": "Sam",
        "status": "investigating",
    })
    db.refresh(incident)
    im.add_update(db, incident, {
        "message": "Rollback path confirmed from readiness checklist. Refund error rate stabilized after mitigation.",
        "author": "Maya",
        "status": "resolved",
    })

    # Touch unused var to keep linters quiet about intentional breadth data.
    _ = notif

    print("Demo data seeded successfully.")
    print(f"  user:     {DEMO_EMAIL} / {DEMO_PASSWORD}")
    print(f"  services: payment-service, auth-service, notifications-service")
    print(f"  release:  1.0.0 (ready), 2.3.1 (testing)")
    print(f"  incident: '{incident.title}' with 3 timeline updates")


def main() -> None:
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()