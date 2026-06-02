"""Release + checklist schemas.

Release input schemas exclude server-controlled fields. Checklist: clients only
ever send the five booleans (any subset) on PATCH; readiness_score and
readiness_status are computed server-side, never client-supplied.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.service import Environment
from app.models.release import ReleaseStatus
from app.domain.readiness import ReadinessStatus


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


class ChecklistUpdate(BaseModel):
    """Any subset of the five booleans. Computed fields are not accepted."""
    model_config = ConfigDict(extra="forbid")  # reject unknown keys -> 422

    tests_passed: bool | None = Field(default=None, strict=True)
    security_review_done: bool | None = Field(default=None, strict=True)
    rollback_plan_ready: bool | None = Field(default=None, strict=True)
    monitoring_ready: bool | None = Field(default=None, strict=True)
    stakeholder_approval: bool | None = Field(default=None, strict=True)


class ChecklistOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    release_id: uuid.UUID
    tests_passed: bool
    security_review_done: bool
    rollback_plan_ready: bool
    monitoring_ready: bool
    stakeholder_approval: bool
    readiness_score: int
    readiness_status: ReadinessStatus
    created_at: datetime
    updated_at: datetime