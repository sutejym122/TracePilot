"""Incident model (+ IncidentUpdate later).

Incident fields (this slice's spec):
    id          uuid pk
    service_id  uuid fk -> services (indexed, cascade)
    title       text not null
    severity    enum(low, medium, high, critical)
    status      enum(open, investigating, mitigated, resolved)
    summary     text
    root_cause  text
    started_at  timestamptz
    resolved_at timestamptz (nullable)
    created_at / updated_at

An incident has no user_id of its own — ownership flows through the linked
Service (Service.user_id). IncidentUpdate (the timeline) is intentionally NOT
implemented yet; it arrives in a later slice.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Enum as SAEnum, ForeignKey, String, Text, DateTime
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