"""Dashboard summary route.

Thin layer: delegate to domain.dashboard.build_summary (which scopes everything
to the current user) and return the aggregated DashboardSummary.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.domain.dashboard import build_summary
from app.models.user import User
from app.schemas.dashboard import DashboardSummary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return build_summary(db, current_user.id)