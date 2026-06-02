"""API metric schemas.

service_id comes from the path, never the body. method is validated against the
HttpMethod enum (stored as a plain string in the DB). Counts and latency are
non-negative; error_count <= request_count is enforced by a model validator.
captured_at is optional and defaults to now server-side when omitted.
"""
import enum
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class HttpMethod(str, enum.Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class ApiMetricCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")  # reject unknown keys -> 422

    endpoint: str = Field(min_length=1, max_length=2048)
    method: HttpMethod
    status_code: int = Field(ge=100, le=599)
    latency_ms: int = Field(ge=0)
    request_count: int = Field(ge=0)
    error_count: int = Field(ge=0)
    captured_at: datetime | None = None

    @model_validator(mode="after")
    def _errors_not_exceeding_requests(self):
        if self.error_count > self.request_count:
            raise ValueError("error_count cannot exceed request_count")
        return self


class ApiMetricOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    service_id: uuid.UUID
    endpoint: str
    method: str
    status_code: int
    latency_ms: int
    request_count: int
    error_count: int
    captured_at: datetime
    created_at: datetime
    updated_at: datetime