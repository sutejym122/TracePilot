"""Release routes: CRUD + checklist. Ownership scoped through the linked Service.

Thin layer: validate via schema, delegate to domain.release_management (which
enforces that the release's service is owned by the current user), return a
schema.
"""
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.domain import release_management as rm
from app.models.user import User
from app.schemas.release import (
    ChecklistOut,
    ChecklistUpdate,
    ReleaseCreate,
    ReleaseOut,
    ReleaseUpdate,
)

router = APIRouter(prefix="/api/releases", tags=["releases"])


@router.get("", response_model=list[ReleaseOut])
def list_releases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return rm.list_releases_for_user(db, current_user.id)


@router.post("", response_model=ReleaseOut, status_code=status.HTTP_201_CREATED)
def create_release(
    payload: ReleaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rm.get_owned_service_or_404(db, payload.service_id, current_user.id)
    return rm.create_release(db, payload.model_dump())


@router.get("/{release_id}", response_model=ReleaseOut)
def get_release(
    release_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return rm.get_owned_release_or_404(db, release_id, current_user.id)


@router.patch("/{release_id}", response_model=ReleaseOut)
def update_release(
    release_id: uuid.UUID,
    payload: ReleaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    release = rm.get_owned_release_or_404(db, release_id, current_user.id)
    changes = payload.model_dump(exclude_unset=True)
    return rm.update_release(db, release, changes)


@router.delete("/{release_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_release(
    release_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    release = rm.get_owned_release_or_404(db, release_id, current_user.id)
    rm.delete_release(db, release)
    return None


# --- Checklist ---
@router.get("/{release_id}/checklist", response_model=ChecklistOut)
def get_release_checklist(
    release_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    release = rm.get_owned_release_or_404(db, release_id, current_user.id)
    return rm.get_checklist_for_release(db, release)


@router.patch("/{release_id}/checklist", response_model=ChecklistOut)
def update_release_checklist(
    release_id: uuid.UUID,
    payload: ChecklistUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    release = rm.get_owned_release_or_404(db, release_id, current_user.id)
    checklist = rm.get_checklist_for_release(db, release)
    changes = payload.model_dump(exclude_unset=True)
    return rm.update_checklist(db, checklist, changes)