"""Release + checklist access logic — ownership scoped through the linked Service.

A release has no user_id; it belongs to a Service, which has user_id. Every
access check is two hops: the release's service must be owned by the current
user. These helpers centralize that join so routers stay thin. Missing or
non-owned rows raise NotFoundError (404) — never leaking another user's data.

Checklist invariant: every release has exactly one checklist. It is created in
the same transaction as the release (create_release). get_checklist_for_release
also lazily backfills one for any release that predates this feature, so the
invariant holds even for older rows.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.readiness import compute_readiness
from app.errors import NotFoundError
from app.models.release import Release, ReleaseChecklist
from app.models.service import Service

CHECKLIST_BOOLEANS = (
    "tests_passed",
    "security_review_done",
    "rollback_plan_ready",
    "monitoring_ready",
    "stakeholder_approval",
)


def get_owned_service_or_404(
    db: Session, service_id: uuid.UUID, user_id: uuid.UUID
) -> Service:
    """Return the service iff it exists and is owned by user_id, else 404."""
    service = db.get(Service, service_id)
    if service is None or service.user_id != user_id:
        raise NotFoundError("Service not found")
    return service


def list_releases_for_user(db: Session, user_id: uuid.UUID) -> list[Release]:
    """All releases across the user's services, newest first."""
    stmt = (
        select(Release)
        .join(Service, Release.service_id == Service.id)
        .where(Service.user_id == user_id)
        .order_by(Release.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def get_owned_release_or_404(
    db: Session, release_id: uuid.UUID, user_id: uuid.UUID
) -> Release:
    """Return the release iff its service is owned by user_id, else 404."""
    stmt = (
        select(Release)
        .join(Service, Release.service_id == Service.id)
        .where(Release.id == release_id, Service.user_id == user_id)
    )
    release = db.scalar(stmt)
    if release is None:
        raise NotFoundError("Release not found")
    return release


def create_release(db: Session, data: dict) -> Release:
    """Create a release and its default (all-false) checklist atomically."""
    release = Release(**data)
    db.add(release)
    db.flush()  # assign release.id without ending the transaction

    score, status = compute_readiness({})  # all false -> 0 / blocked
    checklist = ReleaseChecklist(
        release_id=release.id,
        readiness_score=score,
        readiness_status=status,
    )
    db.add(checklist)

    db.commit()
    db.refresh(release)
    return release


def update_release(db: Session, release: Release, data: dict) -> Release:
    for key, value in data.items():
        setattr(release, key, value)
    db.commit()
    db.refresh(release)
    return release


def delete_release(db: Session, release: Release) -> None:
    db.delete(release)
    db.commit()


# --- Checklist helpers ---
def get_checklist_for_release(db: Session, release: Release) -> ReleaseChecklist:
    """Return the release's checklist, lazily creating one if missing.

    New releases always have a checklist (create_release). This backfill covers
    releases created before the checklist feature existed.
    """
    checklist = db.scalar(
        select(ReleaseChecklist).where(ReleaseChecklist.release_id == release.id)
    )
    if checklist is None:
        score, status = compute_readiness({})
        checklist = ReleaseChecklist(
            release_id=release.id,
            readiness_score=score,
            readiness_status=status,
        )
        db.add(checklist)
        db.commit()
        db.refresh(checklist)
    return checklist


def update_checklist(
    db: Session, checklist: ReleaseChecklist, changes: dict
) -> ReleaseChecklist:
    """Apply a subset of boolean changes, then recompute score and status."""
    for key, value in changes.items():
        setattr(checklist, key, value)

    current = {f: getattr(checklist, f) for f in CHECKLIST_BOOLEANS}
    score, status = compute_readiness(current)
    checklist.readiness_score = score
    checklist.readiness_status = status

    db.commit()
    db.refresh(checklist)
    return checklist