"""Incident schemas.

Input schemas exclude server-controlled fields (id, timestamps). service_id is
required on create and immutable afterward, so it is absent from IncidentUpdate.
status defaults to "open". severity and title are required on create.
IncidentUpdate is all-optional for PATCH semantics; resolved_at is included so a
client can explicitly clear it (send null) — the domain layer distinguishes an
omitted resolved_at from an explicit null.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.incident import IncidentSeverity, IncidentStatus


class IncidentCreate(BaseModel):
    service_id: uuid.UUID
    title: str = Field(min_length=1, max_length=255)
    severity: IncidentSeverity
    status: IncidentStatus = IncidentStatus.open
    summary: str | None = None
    root_cause: str | None = None
    started_at: datetime | None = None
    resolved_at: datetime | None = None
    # Optional user-confirmed link to the likely release. Must belong to the
    # same service as the incident (validated in the domain layer).
    release_id: uuid.UUID | None = None


class IncidentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    severity: IncidentSeverity | None = None
    status: IncidentStatus | None = None
    summary: str | None = None
    root_cause: str | None = None
    started_at: datetime | None = None
    resolved_at: datetime | None = None
    # Send a release id to link, or explicit null to clear the link. The domain
    # layer distinguishes omitted (unchanged) from explicit null (clear).
    release_id: uuid.UUID | None = None


class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    service_id: uuid.UUID
    release_id: uuid.UUID | None
    title: str
    severity: IncidentSeverity
    status: IncidentStatus
    summary: str | None
    root_cause: str | None
    started_at: datetime | None
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime