"""Service (microservice entity) routes: CRUD now; nested health/metrics later.

Thin layer: validate via schema, delegate to domain.crud (which scopes every
query to the current user via user_id), return a schema. The /health, /metrics,
and /health/check routes remain stubs for later phases.
"""
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.domain import crud
from app.models.service import Service
from app.models.user import User
from app.schemas.service import ServiceCreate, ServiceOut, ServiceUpdate

router = APIRouter(prefix="/api/services", tags=["services"])


@router.get("", response_model=list[ServiceOut])
def list_services(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.list_for_user(db, Service, current_user.id)


@router.post("", response_model=ServiceOut, status_code=status.HTTP_201_CREATED)
def create_service(
    payload: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.create_for_user(db, Service, current_user.id, payload.model_dump())


@router.get("/{service_id}", response_model=ServiceOut)
def get_service(
    service_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_or_404(db, Service, service_id, current_user.id)


@router.patch("/{service_id}", response_model=ServiceOut)
def update_service(
    service_id: uuid.UUID,
    payload: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = crud.get_or_404(db, Service, service_id, current_user.id)
    changes = payload.model_dump(exclude_unset=True)
    return crud.update_obj(db, service, changes)


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = crud.get_or_404(db, Service, service_id, current_user.id)
    crud.delete_obj(db, service)
    return None


# --- Stubs for later phases (unchanged) ---
@router.get("/{service_id}/health")
def get_service_health(service_id: str, current_user: User = Depends(get_current_user)):
    # TODO(phase4): recent HealthCheck rows
    return []


@router.get("/{service_id}/metrics")
def get_service_metrics(service_id: str, current_user: User = Depends(get_current_user)):
    # TODO(phase7): ApiMetric rows for this service
    return []


@router.post("/{service_id}/health/check")
def trigger_health_check(service_id: str, current_user: User = Depends(get_current_user)):
    # TODO(phase4): call domain.health_checker.check_service (same path as scheduler)
    return {"detail": "not_implemented"}