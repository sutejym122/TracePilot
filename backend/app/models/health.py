"""HealthCheck model — append-only ping history (highest-volume table).

Fields (this slice's spec):
    id               uuid pk
    service_id       uuid fk -> services (indexed, cascade)
    status_code      int (nullable — null when the request never completed)
    response_time_ms int (nullable)
    status           enum(healthy, degraded, down)
    error_message    text (nullable; set when the check fails)
    checked_at       timestamptz
    created_at / updated_at

A composite index on (service_id, checked_at desc) keeps "recent checks for a
service" fast. status here is three-valued (no 'unknown'); it maps onto the
four-valued Service.status in the domain layer.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Enum as SAEnum, ForeignKey, Integer, Text, DateTime, Index, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin, uuid_pk


class HealthCheckStatus(str, enum.Enum):
    healthy = "healthy"
    degraded = "degraded"
    down = "down"


class HealthCheck(Base, TimestampMixin):
    __tablename__ = "health_checks"

    id: Mapped[uuid.UUID] = uuid_pk()
    service_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"), nullable=False
    )
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[HealthCheckStatus] = mapped_column(
        SAEnum(HealthCheckStatus, name="health_check_status"), nullable=False
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_health_checks_service_id_checked_at", "service_id", checked_at.desc()),
    )