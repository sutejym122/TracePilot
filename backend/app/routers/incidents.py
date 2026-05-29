"""Incident routes: CRUD + timeline updates, with filtering."""
from fastapi import APIRouter, Depends

from app.deps import get_current_user

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.get("")
def list_incidents(
    service_id: str | None = None,
    release_id: str | None = None,
    status: str | None = None,
    current_user=Depends(get_current_user),
):
    # TODO(phase8): filter by query params
    return []


@router.post("")
def create_incident(current_user=Depends(get_current_user)):
    return {"detail": "not_implemented"}


@router.get("/{incident_id}")
def get_incident(incident_id: str, current_user=Depends(get_current_user)):
    # TODO(phase8): IncidentDetailOut (updates timeline)
    return {"detail": "not_implemented"}


@router.patch("/{incident_id}")
def update_incident(incident_id: str, current_user=Depends(get_current_user)):
    return {"detail": "not_implemented"}


@router.post("/{incident_id}/updates")
def add_incident_update(incident_id: str, current_user=Depends(get_current_user)):
    # TODO(phase8): append a timeline note
    return {"detail": "not_implemented"}
