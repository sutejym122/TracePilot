"""Release + ReleaseChecklist models.

Release fields:
    id, service_id, version, environment, status, owner, release_notes,
    released_at, created_at, updated_at

ReleaseChecklist (1:1 with release via a unique constraint on release_id):
    id, release_id, five booleans, readiness_score, readiness_status,
    created_at, updated_at

A release has no user_id of its own — ownership flows through the linked
Service (Service.user_id). readiness_score/status are denormalized: computed
in domain/readiness.py and written here, with the checklist-update path as the
single writer, so they cannot drift.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, Enum as SAEnum, ForeignKey, Integer, String, Text, DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin, uuid_pk
from app.models.service import Environment  # reuse the existing enum
from app.domain.readiness import ReadinessStatus  # single source of the enum


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


class ReleaseChecklist(Base, TimestampMixin):
    __tablename__ = "release_checklists"

    id: Mapped[uuid.UUID] = uuid_pk()
    release_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("releases.id", ondelete="CASCADE"),
        unique=True,  # enforces 1:1 with release
        nullable=False,
    )
    tests_passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    security_review_done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rollback_plan_ready: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    monitoring_ready: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    stakeholder_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    readiness_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    readiness_status: Mapped[ReadinessStatus] = mapped_column(
        SAEnum(ReadinessStatus, name="readiness_status"),
        nullable=False,
        default=ReadinessStatus.blocked,
    )