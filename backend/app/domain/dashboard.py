"""Dashboard summary aggregation.

build_summary(db, user_id) loads the user's rows (scoped through Service.user_id)
and aggregates them in Python — clean and testable, no clever SQL. Ownership is
enforced once: we collect the user's service ids and restrict every subsequent
query to them, so no other user's data can leak in.

The recent-activity feed merges the newest few of each entity type (by each
entity's natural timestamp), sorts newest-first, and keeps the top 10.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.health import HealthCheck, HealthCheckStatus
from app.models.incident import Incident, IncidentStatus, IncidentSeverity, IncidentUpdate
from app.models.metric import ApiMetric
from app.models.release import Release, ReleaseChecklist, ReleaseStatus
from app.models.service import Service, ServiceStatus
from app.domain.readiness import ReadinessStatus

# How many of each entity type to pull into the recent-activity candidate pool.
RECENT_PER_TYPE = 10
RECENT_ACTIVITY_LIMIT = 10


def _service_ids(db: Session, user_id: uuid.UUID) -> list[uuid.UUID]:
    return list(
        db.scalars(select(Service.id).where(Service.user_id == user_id)).all()
    )


def build_summary(db: Session, user_id: uuid.UUID) -> dict:
    services = list(
        db.scalars(select(Service).where(Service.user_id == user_id)).all()
    )
    sids = [s.id for s in services]

    service_summary = _service_summary(services)

    if not sids:
        # No services -> everything empty/zeroed.
        return {
            "service_summary": service_summary,
            "health_summary": {
                "latest_checks_count": 0, "healthy_checks": 0, "degraded_checks": 0,
                "down_checks": 0, "average_response_time_ms": None,
            },
            "release_summary": {
                "total_releases": 0, "planned_releases": 0, "in_progress_releases": 0,
                "testing_releases": 0, "released_releases": 0, "rolled_back_releases": 0,
                "average_readiness_score": None, "ready_releases": 0,
                "risky_releases": 0, "blocked_releases": 0,
            },
            "incident_summary": {
                "total_incidents": 0, "open_incidents": 0, "investigating_incidents": 0,
                "mitigated_incidents": 0, "resolved_incidents": 0, "critical_incidents": 0,
                "high_incidents": 0, "recent_updates_count": 0,
            },
            "metrics_summary": {
                "total_metric_samples": 0, "average_latency_ms": None, "total_requests": 0,
                "total_errors": 0, "error_rate_percent": 0.0, "slowest_endpoint": None,
                "slowest_endpoint_latency_ms": None,
            },
            "recent_activity": [],
        }

    # Load user-scoped rows.
    health_checks = list(db.scalars(
        select(HealthCheck).where(HealthCheck.service_id.in_(sids))
        .order_by(HealthCheck.checked_at.desc())
    ).all())
    releases = list(db.scalars(
        select(Release).where(Release.service_id.in_(sids))
        .order_by(Release.created_at.desc())
    ).all())
    checklists = list(db.scalars(
        select(ReleaseChecklist).join(Release, ReleaseChecklist.release_id == Release.id)
        .where(Release.service_id.in_(sids))
    ).all())
    incidents = list(db.scalars(
        select(Incident).where(Incident.service_id.in_(sids))
        .order_by(Incident.created_at.desc())
    ).all())
    incident_updates = list(db.scalars(
        select(IncidentUpdate).join(Incident, IncidentUpdate.incident_id == Incident.id)
        .where(Incident.service_id.in_(sids))
        .order_by(IncidentUpdate.created_at.desc())
    ).all())
    metrics = list(db.scalars(
        select(ApiMetric).where(ApiMetric.service_id.in_(sids))
        .order_by(ApiMetric.captured_at.desc())
    ).all())

    service_name = {s.id: s.name for s in services}
    incident_title = {i.id: i.title for i in incidents}

    return {
        "service_summary": service_summary,
        "health_summary": _health_summary(health_checks),
        "release_summary": _release_summary(releases, checklists),
        "incident_summary": _incident_summary(incidents, incident_updates),
        "metrics_summary": _metrics_summary(metrics),
        "recent_activity": _recent_activity(
            health_checks, releases, incidents, incident_updates, metrics,
            service_name, incident_title,
        ),
    }


def _service_summary(services) -> dict:
    return {
        "total_services": len(services),
        "healthy_services": sum(1 for s in services if s.status == ServiceStatus.healthy),
        "degraded_services": sum(1 for s in services if s.status == ServiceStatus.degraded),
        "down_services": sum(1 for s in services if s.status == ServiceStatus.down),
        "unknown_services": sum(1 for s in services if s.status == ServiceStatus.unknown),
    }


def _health_summary(checks) -> dict:
    response_times = [c.response_time_ms for c in checks if c.response_time_ms is not None]
    avg = sum(response_times) / len(response_times) if response_times else None
    return {
        "latest_checks_count": len(checks),
        "healthy_checks": sum(1 for c in checks if c.status == HealthCheckStatus.healthy),
        "degraded_checks": sum(1 for c in checks if c.status == HealthCheckStatus.degraded),
        "down_checks": sum(1 for c in checks if c.status == HealthCheckStatus.down),
        "average_response_time_ms": round(avg, 2) if avg is not None else None,
    }


def _release_summary(releases, checklists) -> dict:
    scores = [c.readiness_score for c in checklists]
    avg_score = sum(scores) / len(scores) if scores else None
    return {
        "total_releases": len(releases),
        "planned_releases": sum(1 for r in releases if r.status == ReleaseStatus.planned),
        "in_progress_releases": sum(1 for r in releases if r.status == ReleaseStatus.in_progress),
        "testing_releases": sum(1 for r in releases if r.status == ReleaseStatus.testing),
        "released_releases": sum(1 for r in releases if r.status == ReleaseStatus.released),
        "rolled_back_releases": sum(1 for r in releases if r.status == ReleaseStatus.rolled_back),
        "average_readiness_score": round(avg_score, 2) if avg_score is not None else None,
        "ready_releases": sum(1 for c in checklists if c.readiness_status == ReadinessStatus.ready),
        "risky_releases": sum(1 for c in checklists if c.readiness_status == ReadinessStatus.risky),
        "blocked_releases": sum(1 for c in checklists if c.readiness_status == ReadinessStatus.blocked),
    }


def _incident_summary(incidents, updates) -> dict:
    return {
        "total_incidents": len(incidents),
        "open_incidents": sum(1 for i in incidents if i.status == IncidentStatus.open),
        "investigating_incidents": sum(1 for i in incidents if i.status == IncidentStatus.investigating),
        "mitigated_incidents": sum(1 for i in incidents if i.status == IncidentStatus.mitigated),
        "resolved_incidents": sum(1 for i in incidents if i.status == IncidentStatus.resolved),
        "critical_incidents": sum(1 for i in incidents if i.severity == IncidentSeverity.critical),
        "high_incidents": sum(1 for i in incidents if i.severity == IncidentSeverity.high),
        "recent_updates_count": len(updates),
    }


def _metrics_summary(metrics) -> dict:
    if not metrics:
        return {
            "total_metric_samples": 0, "average_latency_ms": None, "total_requests": 0,
            "total_errors": 0, "error_rate_percent": 0.0, "slowest_endpoint": None,
            "slowest_endpoint_latency_ms": None,
        }
    total_requests = sum(m.request_count for m in metrics)
    total_errors = sum(m.error_count for m in metrics)
    avg_latency = sum(m.latency_ms for m in metrics) / len(metrics)
    slowest = max(metrics, key=lambda m: m.latency_ms)
    error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0.0
    return {
        "total_metric_samples": len(metrics),
        "average_latency_ms": round(avg_latency, 2),
        "total_requests": total_requests,
        "total_errors": total_errors,
        "error_rate_percent": round(error_rate, 2),
        "slowest_endpoint": f"{slowest.method} {slowest.endpoint}",
        "slowest_endpoint_latency_ms": slowest.latency_ms,
    }


def _recent_activity(checks, releases, incidents, updates, metrics, svc_name, inc_title) -> list[dict]:
    items: list[dict] = []

    for c in checks[:RECENT_PER_TYPE]:
        name = svc_name.get(c.service_id, "service")
        rt = f", {c.response_time_ms}ms" if c.response_time_ms is not None else ""
        items.append({
            "type": "health_check",
            "title": f"{name} health check",
            "subtitle": f"{c.status.value}{rt}",
            "timestamp": c.checked_at,
        })

    for r in releases[:RECENT_PER_TYPE]:
        name = svc_name.get(r.service_id, "service")
        items.append({
            "type": "release",
            "title": f"{name} release {r.version}",
            "subtitle": f"status: {r.status.value}",
            "timestamp": r.released_at or r.created_at,
        })

    for i in incidents[:RECENT_PER_TYPE]:
        items.append({
            "type": "incident",
            "title": i.title,
            "subtitle": f"severity: {i.severity.value}, status: {i.status.value}",
            "timestamp": i.created_at,
        })

    for u in updates[:RECENT_PER_TYPE]:
        items.append({
            "type": "incident_update",
            "title": f"Incident update: {inc_title.get(u.incident_id, 'incident')}",
            "subtitle": u.message,
            "timestamp": u.created_at,
        })

    for m in metrics[:RECENT_PER_TYPE]:
        items.append({
            "type": "metric",
            "title": f"{m.method} {m.endpoint}",
            "subtitle": f"{m.latency_ms}ms, {m.request_count} requests, {m.error_count} errors",
            "timestamp": m.captured_at,
        })

    items.sort(key=lambda x: x["timestamp"], reverse=True)
    return items[:RECENT_ACTIVITY_LIMIT]