"""Incident update (timeline) schemas.

incident_id comes from the path, never the body. message is required and
non-empty. author and status are optional; if status is present it must be a
valid IncidentStatus and will be propagated to the parent incident.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.incident import IncidentStatus


class IncidentUpdateCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")  # reject unknown keys -> 422

    message: str = Field(min_length=1, max_length=5000)
    author: str | None = Field(default=None, max_length=255)
    status: IncidentStatus | None = None


class IncidentUpdateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    incident_id: uuid.UUID
    message: str
    author: str | None
    status: IncidentStatus | None
    created_at: datetime
    updated_at: datetime