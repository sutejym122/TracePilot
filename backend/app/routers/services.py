"""Service (microservice entity) routes: CRUD + health checks + API metrics.

Thin layer: validate via schema, delegate to domain helpers (which scope every
query to the current user via user_id), return a schema.
"""
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.domain import crud
from app.domain.health_checker import check_service
from app.domain import metric_management as mm
from app.models.health import HealthCheck
from app.models.service import Service
from app.models.user import User
from app.schemas.health import HealthCheckOut
from app.schemas.metric import ApiMetricCreate, ApiMetricOut
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


# --- Health checks ---
@router.get("/{service_id}/health", response_model=list[HealthCheckOut])
def list_service_health(
    service_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Ownership is enforced here: 404 if the service isn't the current user's.
    crud.get_or_404(db, Service, service_id, current_user.id)
    stmt = (
        select(HealthCheck)
        .where(HealthCheck.service_id == service_id)
        .order_by(HealthCheck.checked_at.desc())
    )
    return list(db.scalars(stmt).all())


@router.post(
    "/{service_id}/health/check",
    response_model=HealthCheckOut,
    status_code=status.HTTP_201_CREATED,
)
def trigger_health_check(
    service_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = crud.get_or_404(db, Service, service_id, current_user.id)
    return check_service(db, service)


# --- API metrics ---
@router.get("/{service_id}/metrics", response_model=list[ApiMetricOut])
def list_service_metrics(
    service_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mm.get_owned_service_or_404(db, service_id, current_user.id)
    return mm.list_metrics_for_service(db, service_id)


@router.post(
    "/{service_id}/metrics",
    response_model=ApiMetricOut,
    status_code=status.HTTP_201_CREATED,
)
def create_service_metric(
    service_id: uuid.UUID,
    payload: ApiMetricCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mm.get_owned_service_or_404(db, service_id, current_user.id)
    return mm.create_metric(db, service_id, payload.model_dump())


@router.post(
    "/{service_id}/metrics/simulate",
    response_model=ApiMetricOut,
    status_code=status.HTTP_201_CREATED,
)
def simulate_service_metric(
    service_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mm.get_owned_service_or_404(db, service_id, current_user.id)
    return mm.generate_simulated_metric(db, service_id)