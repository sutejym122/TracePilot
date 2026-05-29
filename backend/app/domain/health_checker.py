"""Health checking — shared by the manual-trigger route and the scheduler.

There is exactly one definition of "what checking a service's health means":
check_service(). It pings the service's health_url, measures response time,
classifies the result, records a HealthCheck row, and updates the denormalized
Service.status. Synchronous (httpx.Client) so the sync route and the sync
scheduler job can both call it without event-loop juggling.

Classification:
    2xx                                  -> healthy
    3xx / 4xx                            -> degraded
    5xx / timeout / connection / error   -> down
"""
import time

import httpx

from sqlalchemy.orm import Session

from app.errors import ValidationError
from app.models.health import HealthCheck, HealthCheckStatus
from app.models.service import Service, ServiceStatus

REQUEST_TIMEOUT_SECONDS = 3.0

# HealthCheckStatus (3 values) maps 1:1 onto the matching ServiceStatus values.
_STATUS_MAP = {
    HealthCheckStatus.healthy: ServiceStatus.healthy,
    HealthCheckStatus.degraded: ServiceStatus.degraded,
    HealthCheckStatus.down: ServiceStatus.down,
}


def _classify(status_code: int) -> HealthCheckStatus:
    if 200 <= status_code < 300:
        return HealthCheckStatus.healthy
    if 300 <= status_code < 500:
        return HealthCheckStatus.degraded
    return HealthCheckStatus.down  # 5xx and anything else


def check_service(db: Session, service: Service) -> HealthCheck:
    """Ping the service's health_url, persist a HealthCheck, update Service.status.

    Raises ValidationError (422) if the service has no health_url configured.
    Never raises for network failures — those are recorded as a 'down' check.
    """
    if not service.health_url:
        raise ValidationError("Service has no health_url configured to check")

    status_code: int | None = None
    response_time_ms: int | None = None
    error_message: str | None = None

    start = time.perf_counter()
    try:
        response = httpx.get(
            service.health_url,
            timeout=REQUEST_TIMEOUT_SECONDS,
            follow_redirects=False,
        )
        response_time_ms = int((time.perf_counter() - start) * 1000)
        status_code = response.status_code
        status = _classify(status_code)
    except httpx.TimeoutException:
        response_time_ms = int((time.perf_counter() - start) * 1000)
        status = HealthCheckStatus.down
        error_message = "Request timed out"
    except httpx.RequestError as exc:
        response_time_ms = int((time.perf_counter() - start) * 1000)
        status = HealthCheckStatus.down
        error_message = f"Connection error: {exc.__class__.__name__}"
    except Exception as exc:  # defensive: any unexpected failure is still 'down'
        response_time_ms = int((time.perf_counter() - start) * 1000)
        status = HealthCheckStatus.down
        error_message = f"Unexpected error: {exc.__class__.__name__}"

    check = HealthCheck(
        service_id=service.id,
        status_code=status_code,
        response_time_ms=response_time_ms,
        status=status,
        error_message=error_message,
    )
    db.add(check)

    # Update the denormalized Service.status from this latest result.
    service.status = _STATUS_MAP[status]

    db.commit()
    db.refresh(check)
    return check