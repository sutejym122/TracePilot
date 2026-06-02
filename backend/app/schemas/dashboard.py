"""Dashboard summary schemas.

A single read-only response aggregating the user's services, health checks,
releases + checklists, incidents + updates, and API metrics into six sections
plus a recent-activity feed. All values are computed in domain/dashboard.py;
nothing here is client-supplied.
"""
from datetime import datetime

from pydantic import BaseModel


class ServiceSummary(BaseModel):
    total_services: int
    healthy_services: int
    degraded_services: int
    down_services: int
    unknown_services: int


class HealthSummary(BaseModel):
    latest_checks_count: int
    healthy_checks: int
    degraded_checks: int
    down_checks: int
    average_response_time_ms: float | None


class ReleaseSummary(BaseModel):
    total_releases: int
    planned_releases: int
    in_progress_releases: int
    testing_releases: int
    released_releases: int
    rolled_back_releases: int
    average_readiness_score: float | None
    ready_releases: int
    risky_releases: int
    blocked_releases: int


class IncidentSummary(BaseModel):
    total_incidents: int
    open_incidents: int
    investigating_incidents: int
    mitigated_incidents: int
    resolved_incidents: int
    critical_incidents: int
    high_incidents: int
    recent_updates_count: int


class MetricsSummary(BaseModel):
    total_metric_samples: int
    average_latency_ms: float | None
    total_requests: int
    total_errors: int
    error_rate_percent: float
    slowest_endpoint: str | None
    slowest_endpoint_latency_ms: int | None


class ActivityItem(BaseModel):
    type: str
    title: str
    subtitle: str
    timestamp: datetime


class DashboardSummary(BaseModel):
    service_summary: ServiceSummary
    health_summary: HealthSummary
    release_summary: ReleaseSummary
    incident_summary: IncidentSummary
    metrics_summary: MetricsSummary
    recent_activity: list[ActivityItem]