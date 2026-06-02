"""Incident + IncidentUpdate models.

Incident fields:
    id, service_id, title, severity, status, summary, root_cause,
    started_at, resolved_at, created_at, updated_at

IncidentUpdate (the timeline) fields:
    id, incident_id, message, author, status (nullable), created_at, updated_at

An incident has no user_id of its own — ownership flows through the linked
Service (Service.user_id). An IncidentUpdate has no service_id of its own —
ownership flows through Incident -> Service. IncidentUpdate.status reuses the
existing incident_status enum (no duplicate type).
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Enum as SAEnum, ForeignKey, String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin, uuid_pk


class IncidentSeverity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class IncidentStatus(str, enum.Enum):
    open = "open"
    investigating = "investigating"
    mitigated = "mitigated"
    resolved = "resolved"


class Incident(Base, TimestampMixin):
    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = uuid_pk()
    service_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[IncidentSeverity] = mapped_column(
        SAEnum(IncidentSeverity, name="incident_severity"), nullable=False
    )
    status: Mapped[IncidentStatus] = mapped_column(
        SAEnum(IncidentStatus, name="incident_status"),
        nullable=False,
        default=IncidentStatus.open,
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class IncidentUpdate(Base, TimestampMixin):
    __tablename__ = "incident_updates"

    id: Mapped[uuid.UUID] = uuid_pk()
    incident_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("incidents.id", ondelete="CASCADE"), index=True, nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Reuses the existing incident_status enum type (create_type handled in migration).
    status: Mapped[IncidentStatus | None] = mapped_column(
        SAEnum(IncidentStatus, name="incident_status"), nullable=True
    )