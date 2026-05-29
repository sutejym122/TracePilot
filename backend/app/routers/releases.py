"""Release routes: CRUD. Ownership is scoped through the linked Service.

Thin layer: validate via schema, delegate to domain.release_management (which
enforces that the release's service is owned by the current user), return a
schema. The /checklist route remains a stub for the next slice.
"""
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.domain import release_management as rm
from app.models.user import User
from app.schemas.release import ReleaseCreate, ReleaseOut, ReleaseUpdate

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
    # 404 if the target service isn't the current user's — can't create a
    # release against a service you don't own (or that doesn't exist).
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


# --- Stub for the next slice ---
@router.patch("/{release_id}/checklist")
def update_checklist(release_id: str, current_user: User = Depends(get_current_user)):
    # TODO(next slice): update booleans, return ChecklistOut with computed score
    return {"detail": "not_implemented"}