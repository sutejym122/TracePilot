"""ApiMetric model — per-endpoint API performance samples (simulated in MVP).

Fields (this slice's spec):
    id            uuid pk
    service_id    uuid fk -> services (indexed, cascade)
    endpoint      text not null            -- e.g. "/api/payments/charge"
    method        text not null            -- GET/POST/PUT/PATCH/DELETE (validated at the API edge)
    status_code   int not null
    latency_ms    int not null (>= 0)
    request_count int not null (>= 0)
    error_count   int not null (>= 0)
    captured_at   timestamptz not null (defaults to now)
    created_at / updated_at

An ApiMetric has no user_id — ownership flows through the linked Service
(Service.user_id). method is stored as a string, not a Postgres enum: the
vocabulary is stable, no query scopes by it, and Pydantic validates it at the
edge — so a DB enum would add migration cost with no benefit. A composite index
on (service_id, captured_at desc) keeps "recent metrics for a service" fast.
"""
import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, Text, DateTime, Index, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin, uuid_pk


class ApiMetric(Base, TimestampMixin):
    __tablename__ = "api_metrics"

    id: Mapped[uuid.UUID] = uuid_pk()
    service_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"), nullable=False
    )
    endpoint: Mapped[str] = mapped_column(Text, nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    request_count: Mapped[int] = mapped_column(Integer, nullable=False)
    error_count: Mapped[int] = mapped_column(Integer, nullable=False)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_api_metrics_service_id_captured_at", "service_id", captured_at.desc()),
    )