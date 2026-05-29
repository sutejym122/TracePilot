"""Service model — a registered microservice (the entity, not business logic).

Phase 2 schema:
    id               uuid pk
    user_id          uuid fk -> users (indexed, cascade)
    name             text not null
    owner            text
    environment      enum(dev, uat, prod)
    status           enum(healthy, degraded, down, unknown)  -- denormalized, written by health_checker
    repo_url         text
    health_url       text
    last_deployed_at timestamptz
    created_at / updated_at
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Enum as SAEnum, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin, uuid_pk


class Environment(str, enum.Enum):
    dev = "dev"
    uat = "uat"
    prod = "prod"


class ServiceStatus(str, enum.Enum):
    healthy = "healthy"
    degraded = "degraded"
    down = "down"
    unknown = "unknown"


class Service(Base, TimestampMixin):
    __tablename__ = "services"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    environment: Mapped[Environment] = mapped_column(
        SAEnum(Environment, name="environment"), nullable=False
    )
    status: Mapped[ServiceStatus] = mapped_column(
        SAEnum(ServiceStatus, name="service_status"),
        nullable=False,
        default=ServiceStatus.unknown,
    )
    repo_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    health_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    last_deployed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )