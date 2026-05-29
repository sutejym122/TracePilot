"""Service (microservice entity) routes: CRUD + nested health/metrics reads."""
from fastapi import APIRouter, Depends

from app.deps import get_current_user

router = APIRouter(prefix="/api/services", tags=["services"])


@router.get("")
def list_services(current_user=Depends(get_current_user)):
    # TODO(phase3)
    return []


@router.post("")
def create_service(current_user=Depends(get_current_user)):
    # TODO(phase3)
    return {"detail": "not_implemented"}


@router.get("/{service_id}")
def get_service(service_id: str, current_user=Depends(get_current_user)):
    # TODO(phase3): ServiceDetailOut
    return {"detail": "not_implemented"}


@router.patch("/{service_id}")
def update_service(service_id: str, current_user=Depends(get_current_user)):
    # TODO(phase3)
    return {"detail": "not_implemented"}


@router.delete("/{service_id}")
def delete_service(service_id: str, current_user=Depends(get_current_user)):
    # TODO(phase3)
    return {"detail": "not_implemented"}


@router.get("/{service_id}/health")
def get_service_health(service_id: str, current_user=Depends(get_current_user)):
    # TODO(phase4): recent HealthCheck rows
    return []


@router.get("/{service_id}/metrics")
def get_service_metrics(service_id: str, current_user=Depends(get_current_user)):
    # TODO(phase7): ApiMetric rows for this service
    return []


@router.post("/{service_id}/health/check")
def trigger_health_check(service_id: str, current_user=Depends(get_current_user)):
    # TODO(phase4): call domain.health_checker.check_service (same path as scheduler)
    return {"detail": "not_implemented"}
