"""Health-check schemas.

HealthCheckOut is the read shape returned by the list and manual-trigger
routes. There is no create-input schema: checks are produced by the backend
(domain.health_checker), never supplied by the client.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.health import HealthCheckStatus


class HealthCheckOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    service_id: uuid.UUID
    status_code: int | None
    response_time_ms: int | None
    status: HealthCheckStatus
    error_message: str | None
    checked_at: datetime
    created_at: datetime
    updated_at: datetime