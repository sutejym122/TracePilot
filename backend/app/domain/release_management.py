"""Release access logic — ownership scoped through the linked Service.

A release has no user_id; it belongs to a Service, which has user_id. So every
access check is two hops: the release's service must be owned by the current
user. These helpers centralize that join so the router stays thin. Missing or
non-owned rows raise NotFoundError (404) — never leaking another user's data.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import NotFoundError
from app.models.release import Release
from app.models.service import Service


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
    release = Release(**data)
    db.add(release)
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