"""Release model (+ ReleaseChecklist later).

Release fields (this slice's spec):
    id            uuid pk
    service_id    uuid fk -> services (indexed, cascade)
    version       text not null
    environment   enum(dev, uat, prod)        -- reuses Service's Environment
    status        enum(planned, in_progress, testing, released, rolled_back)
    owner         text
    release_notes text
    released_at   timestamptz
    created_at / updated_at

A release has no user_id of its own — ownership flows through the linked
Service (Service.user_id). ReleaseChecklist is intentionally NOT implemented
yet; it arrives in the next slice.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Enum as SAEnum, ForeignKey, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin, uuid_pk
from app.models.service import Environment  # reuse the existing enum


class ReleaseStatus(str, enum.Enum):
    planned = "planned"
    in_progress = "in_progress"
    testing = "testing"
    released = "released"
    rolled_back = "rolled_back"


class Release(Base, TimestampMixin):
    __tablename__ = "releases"

    id: Mapped[uuid.UUID] = uuid_pk()
    service_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"), index=True, nullable=False
    )
    version: Mapped[str] = mapped_column(String(255), nullable=False)
    environment: Mapped[Environment] = mapped_column(
        SAEnum(Environment, name="environment"), nullable=False
    )
    status: Mapped[ReleaseStatus] = mapped_column(
        SAEnum(ReleaseStatus, name="release_status"),
        nullable=False,
        default=ReleaseStatus.planned,
    )
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    release_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    released_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )