"""Release schemas.

Input schemas exclude server-controlled fields (id, timestamps). service_id is
required on create (the release must belong to a service) but is immutable
afterward, so it is absent from ReleaseUpdate. status defaults to "planned".
ReleaseUpdate is all-optional for PATCH semantics.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.service import Environment
from app.models.release import ReleaseStatus


class ReleaseCreate(BaseModel):
    service_id: uuid.UUID
    version: str = Field(min_length=1, max_length=255)
    environment: Environment
    status: ReleaseStatus = ReleaseStatus.planned
    owner: str | None = Field(default=None, max_length=255)
    release_notes: str | None = None
    released_at: datetime | None = None


class ReleaseUpdate(BaseModel):
    version: str | None = Field(default=None, min_length=1, max_length=255)
    environment: Environment | None = None
    status: ReleaseStatus | None = None
    owner: str | None = Field(default=None, max_length=255)
    release_notes: str | None = None
    released_at: datetime | None = None


class ReleaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    service_id: uuid.UUID
    version: str
    environment: Environment
    status: ReleaseStatus
    owner: str | None
    release_notes: str | None
    released_at: datetime | None
    created_at: datetime
    updated_at: datetime