"""Service schemas.

Input schemas exclude server-controlled fields (id, user_id, status, timestamps).
status defaults to "unknown" at creation and is owned by the health checker in a
later phase, so clients never set it here. ServiceUpdate is all-optional for
PATCH semantics.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.service import Environment, ServiceStatus


class ServiceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    environment: Environment
    owner: str | None = Field(default=None, max_length=255)
    repo_url: str | None = Field(default=None, max_length=2048)
    health_url: str | None = Field(default=None, max_length=2048)
    last_deployed_at: datetime | None = None


class ServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    environment: Environment | None = None
    owner: str | None = Field(default=None, max_length=255)
    repo_url: str | None = Field(default=None, max_length=2048)
    health_url: str | None = Field(default=None, max_length=2048)
    last_deployed_at: datetime | None = None


class ServiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    owner: str | None
    environment: Environment
    status: ServiceStatus
    repo_url: str | None
    health_url: str | None
    last_deployed_at: datetime | None
    created_at: datetime
    updated_at: datetime