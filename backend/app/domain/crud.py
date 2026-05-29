"""Generic, user-scoped persistence helpers shared by routers.

Every query is scoped by an owner column (default: user_id) so a user can only
ever see their own rows. get_or_404 raises NotFoundError when a row is missing
OR owned by someone else — returning 404 (not 403) so we never leak the
existence of another user's resource. Routers stay thin by delegating here;
entity-specific business logic lives in the other domain modules.
"""
import uuid
from typing import Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base
from app.errors import NotFoundError

ModelT = TypeVar("ModelT", bound=Base)


def list_for_user(
    db: Session, model: Type[ModelT], owner_id: uuid.UUID, owner_field: str = "user_id"
) -> list[ModelT]:
    column = getattr(model, owner_field)
    stmt = select(model).where(column == owner_id).order_by(model.created_at.desc())
    return list(db.scalars(stmt).all())


def get_or_404(
    db: Session,
    model: Type[ModelT],
    obj_id: uuid.UUID,
    owner_id: uuid.UUID,
    owner_field: str = "user_id",
) -> ModelT:
    obj = db.get(model, obj_id)
    if obj is None or getattr(obj, owner_field) != owner_id:
        raise NotFoundError(f"{model.__name__} not found")
    return obj


def create_for_user(
    db: Session,
    model: Type[ModelT],
    owner_id: uuid.UUID,
    data: dict,
    owner_field: str = "user_id",
) -> ModelT:
    obj = model(**data, **{owner_field: owner_id})
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_obj(db: Session, obj: ModelT, data: dict) -> ModelT:
    for key, value in data.items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_obj(db: Session, obj: ModelT) -> None:
    db.delete(obj)
    db.commit()