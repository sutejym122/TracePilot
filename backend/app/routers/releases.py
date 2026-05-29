"""Release routes: CRUD + checklist update."""
from fastapi import APIRouter, Depends

from app.deps import get_current_user

router = APIRouter(prefix="/api/releases", tags=["releases"])


@router.get("")
def list_releases(current_user=Depends(get_current_user)):
    return []


@router.post("")
def create_release(current_user=Depends(get_current_user)):
    return {"detail": "not_implemented"}


@router.get("/{release_id}")
def get_release(release_id: str, current_user=Depends(get_current_user)):
    # TODO(phase6): ReleaseDetailOut (checklist + linked incidents)
    return {"detail": "not_implemented"}


@router.patch("/{release_id}")
def update_release(release_id: str, current_user=Depends(get_current_user)):
    return {"detail": "not_implemented"}


@router.delete("/{release_id}")
def delete_release(release_id: str, current_user=Depends(get_current_user)):
    return {"detail": "not_implemented"}


@router.patch("/{release_id}/checklist")
def update_checklist(release_id: str, current_user=Depends(get_current_user)):
    # TODO(phase6): update booleans, return ChecklistOut with computed score
    return {"detail": "not_implemented"}
