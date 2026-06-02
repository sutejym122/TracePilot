"""Incident routes: CRUD. Ownership scoped through the linked Service.

Thin layer: validate via schema, delegate to domain.incident_management (which
enforces that the incident's service is owned by the current user), return a
schema. The /updates timeline route remains a stub for a later slice.
"""
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.domain import incident_management as im
from app.models.user import User
from app.schemas.incident import IncidentCreate, IncidentOut, IncidentUpdate

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentOut])
def list_incidents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return im.list_incidents_for_user(db, current_user.id)


@router.post("", response_model=IncidentOut, status_code=status.HTTP_201_CREATED)
def create_incident(
    payload: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 404 if the target service isn't the current user's.
    im.get_owned_service_or_404(db, payload.service_id, current_user.id)
    return im.create_incident(db, payload.model_dump())


@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(
    incident_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return im.get_owned_incident_or_404(db, incident_id, current_user.id)


@router.patch("/{incident_id}", response_model=IncidentOut)
def update_incident(
    incident_id: uuid.UUID,
    payload: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incident = im.get_owned_incident_or_404(db, incident_id, current_user.id)
    changes = payload.model_dump(exclude_unset=True)
    return im.update_incident(db, incident, changes)


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(
    incident_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incident = im.get_owned_incident_or_404(db, incident_id, current_user.id)
    im.delete_incident(db, incident)
    return None


# --- Stub for a later slice ---
@router.post("/{incident_id}/updates")
def add_incident_update(incident_id: str, current_user: User = Depends(get_current_user)):
    # TODO(later): append a timeline note
    return {"detail": "not_implemented"}