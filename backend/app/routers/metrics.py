"""Cross-service metrics routes."""
from fastapi import APIRouter, Depends

from app.deps import get_current_user

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("")
def list_metrics(current_user=Depends(get_current_user)):
    # TODO(phase7): aggregated metrics across services
    return []


@router.post("/simulate")
def simulate_metrics(current_user=Depends(get_current_user)):
    # TODO(phase7): call domain.metrics_simulator
    return {"detail": "not_implemented"}
