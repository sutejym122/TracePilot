"""Shared model building blocks.

Every table uses a UUID primary key and carries created_at / updated_at. These
helpers keep that consistent without repeating column definitions per model.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


def uuid_pk() -> Mapped[uuid.UUID]:
    """A UUID primary-key column with a server-side default."""
    return mapped_column(primary_key=True, default=uuid.uuid4)


class TimestampMixin:
    """Adds auto-managed created_at and updated_at columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
