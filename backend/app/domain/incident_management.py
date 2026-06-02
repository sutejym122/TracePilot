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

from app.errors import NotFoundError
from app.models.incident import Incident, IncidentStatus
from app.models.service import Service


def get_owned_service_or_404(
    db: Session, service_id: uuid.UUID, user_id: uuid.UUID
) -> Service:
    """Return the service iff it exists and is owned by user_id, else 404."""
    service = db.get(Service, service_id)
    if service is None or service.user_id != user_id:
        raise NotFoundError("Service not found")
    return service


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