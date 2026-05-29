"""Dashboard summary route."""
from fastapi import APIRouter, Depends

from app.deps import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(current_user=Depends(get_current_user)):
    # TODO(phase5): call domain.dashboard.build_summary -> SummaryOut
    return {"detail": "not_implemented"}
