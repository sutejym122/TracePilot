"""Incident access logic — ownership scoped through the linked Service.

An incident has no user_id; it belongs to a Service, which has user_id. Every
access check is two hops: the incident's service must be owned by the current
user. Missing or non-owned rows raise NotFoundError (404).

resolved_at automation (per spec):
  - When status becomes 'resolved' and the client did not provide resolved_at,
    set resolved_at to the current UTC time.
  - When status changes away from resolved, keep the existing resolved_at unless
    the client explicitly included resolved_at in the payload (e.g. sends null).
The "explicitly included" distinction relies on the router passing changes from
model_dump(exclude_unset=True): an omitted field is absent; an explicit null is
present with value None.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.models.incident import Incident, IncidentStatus
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


def validate_release_for_service(
    db: Session, release_id: uuid.UUID, service_id: uuid.UUID
) -> None:
    """Ensure a release exists and belongs to the same service as the incident.

    Ownership is already guaranteed by the caller having validated the service
    against the current user, and a release belongs to exactly one service — so
    a release on this service is necessarily owned by the same user. A release
    that doesn't exist or belongs to a different service is rejected (422).
    """
    release = db.get(Release, release_id)
    if release is None or release.service_id != service_id:
        raise ValidationError(
            "release_id must reference a release on the same service"
        )


def suggest_releases_for_service(
    db: Session, service_id: uuid.UUID, user_id: uuid.UUID, limit: int = 10
) -> list[Release]:
    """Releases on the given (owned) service, newest first — candidates for the
    'likely release' link. Returns [] if the service isn't owned by the user."""
    service = db.get(Service, service_id)
    if service is None or service.user_id != user_id:
        return []
    stmt = (
        select(Release)
        .where(Release.service_id == service_id)
        .order_by(Release.created_at.desc(), Release.id.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def list_incidents_for_user(db: Session, user_id: uuid.UUID) -> list[Incident]:
    """All incidents across the user's services, newest first."""
    stmt = (
        select(Incident)
        .join(Service, Incident.service_id == Service.id)
        .where(Service.user_id == user_id)
        .order_by(Incident.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def get_owned_incident_or_404(
    db: Session, incident_id: uuid.UUID, user_id: uuid.UUID
) -> Incident:
    """Return the incident iff its service is owned by user_id, else 404."""
    stmt = (
        select(Incident)
        .join(Service, Incident.service_id == Service.id)
        .where(Incident.id == incident_id, Service.user_id == user_id)
    )
    incident = db.scalar(stmt)
    if incident is None:
        raise NotFoundError("Incident not found")
    return incident


def create_incident(db: Session, data: dict) -> Incident:
    # If a release link is supplied, it must be a release on the same service.
    release_id = data.get("release_id")
    if release_id is not None:
        validate_release_for_service(db, release_id, data["service_id"])
    # On create: if status is resolved and no resolved_at given, stamp it now.
    if (
        data.get("status") == IncidentStatus.resolved
        and data.get("resolved_at") is None
    ):
        data = {**data, "resolved_at": datetime.now(timezone.utc)}
    incident = Incident(**data)
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def update_incident(db: Session, incident: Incident, changes: dict) -> Incident:
    """Apply partial changes with resolved_at automation.

    `changes` comes from model_dump(exclude_unset=True), so a key is present
    only if the client actually sent it.
    """
    resolved_at_explicit = "resolved_at" in changes
    new_status = changes.get("status", incident.status)

    # If the client supplies a non-null release_id, validate it against the
    # incident's service. An explicit null clears the link (no validation).
    if changes.get("release_id") is not None:
        validate_release_for_service(db, changes["release_id"], incident.service_id)

    for key, value in changes.items():
        setattr(incident, key, value)

    # Auto-stamp resolved_at when transitioning to resolved without an explicit value.
    if new_status == IncidentStatus.resolved and not resolved_at_explicit:
        if incident.resolved_at is None:
            incident.resolved_at = datetime.now(timezone.utc)
    # Moving away from resolved: keep resolved_at as-is unless the client
    # explicitly sent it (already applied in the loop above). No action needed.

    db.commit()
    db.refresh(incident)
    return incident


def delete_incident(db: Session, incident: Incident) -> None:
    db.delete(incident)
    db.commit()


# --- Incident updates (timeline) ---
def list_updates_for_incident(db: Session, incident: Incident):
    """Return the incident's updates in chronological order (oldest first)."""
    from app.models.incident import IncidentUpdate  # local import avoids any cycle
    stmt = (
        select(IncidentUpdate)
        .where(IncidentUpdate.incident_id == incident.id)
        .order_by(IncidentUpdate.created_at.asc())
    )
    return list(db.scalars(stmt).all())


def add_update(db: Session, incident: Incident, data: dict):
    """Append a timeline update. If it carries a status, propagate it to the
    parent incident, applying the same resolved_at automation as incident edits.
    """
    from app.models.incident import IncidentUpdate

    update = IncidentUpdate(
        incident_id=incident.id,
        message=data["message"],
        author=data.get("author"),
        status=data.get("status"),
    )
    db.add(update)

    new_status = data.get("status")
    if new_status is not None:
        incident.status = new_status
        if new_status == IncidentStatus.resolved and incident.resolved_at is None:
            incident.resolved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(update)
    return update