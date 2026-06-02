"""API metric access logic — ownership scoped through the linked Service.

An ApiMetric has no user_id; it belongs to a Service, which has user_id. Access
helpers verify service ownership (404 otherwise). create_metric persists a
client-supplied sample; generate_simulated_metric persists a simulator-produced
one — both used by routes, the latter also by the scheduled worker.
"""
import random
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.metrics_simulator import simulate_metric_values
from app.errors import NotFoundError
from app.models.metric import ApiMetric
from app.models.service import Service


def get_owned_service_or_404(
    db: Session, service_id: uuid.UUID, user_id: uuid.UUID
) -> Service:
    service = db.get(Service, service_id)
    if service is None or service.user_id != user_id:
        raise NotFoundError("Service not found")
    return service


def list_metrics_for_service(db: Session, service_id: uuid.UUID) -> list[ApiMetric]:
    """Metrics for a service, newest first (captured_at desc)."""
    stmt = (
        select(ApiMetric)
        .where(ApiMetric.service_id == service_id)
        .order_by(ApiMetric.captured_at.desc())
    )
    return list(db.scalars(stmt).all())


def create_metric(db: Session, service_id: uuid.UUID, data: dict) -> ApiMetric:
    """Persist a client-supplied metric. captured_at defaults to now if omitted."""
    payload = dict(data)
    if payload.get("captured_at") is None:
        payload.pop("captured_at", None)  # let the DB server_default apply
    metric = ApiMetric(service_id=service_id, **payload)
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


def generate_simulated_metric(
    db: Session, service_id: uuid.UUID, rng: random.Random | None = None
) -> ApiMetric:
    """Generate and persist one simulated metric for a service."""
    values = simulate_metric_values(rng)
    metric = ApiMetric(service_id=service_id, **values)
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric