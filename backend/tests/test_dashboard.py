"""Tests for the Dashboard Summary slice.

Everything is scoped through Service.user_id. Covers empty dashboard, per-user
isolation, and correct counts/calculations across all six sections plus the
recent-activity feed.
"""
import uuid


def _register(client, email, password="supersecret", name="User"):
    resp = client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "name": name},
    )
    assert resp.status_code == 201
    return resp.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _service(client, token, name, environment="prod"):
    r = client.post("/api/services", json={"name": name, "environment": environment}, headers=_auth(token))
    assert r.status_code == 201
    return r.json()["id"]


def _release(client, token, sid, version, status="planned"):
    r = client.post(
        "/api/releases",
        json={"service_id": sid, "version": version, "environment": "prod", "status": status},
        headers=_auth(token),
    )
    assert r.status_code == 201
    return r.json()["id"]


def _set_checklist(client, token, rid, **flags):
    r = client.patch(f"/api/releases/{rid}/checklist", json=flags, headers=_auth(token))
    assert r.status_code == 200
    return r.json()


def _incident(client, token, sid, title, severity="low", status="open"):
    r = client.post(
        "/api/incidents",
        json={"service_id": sid, "title": title, "severity": severity, "status": status},
        headers=_auth(token),
    )
    assert r.status_code == 201
    return r.json()["id"]


def _incident_update(client, token, iid, message):
    r = client.post(f"/api/incidents/{iid}/updates", json={"message": message}, headers=_auth(token))
    assert r.status_code == 201
    return r.json()


def _metric(client, token, sid, endpoint, method, latency, requests, errors, status_code=200):
    r = client.post(
        f"/api/services/{sid}/metrics",
        json={"endpoint": endpoint, "method": method, "status_code": status_code,
              "latency_ms": latency, "request_count": requests, "error_count": errors},
        headers=_auth(token),
    )
    assert r.status_code == 201
    return r.json()


def _summary(client, token):
    r = client.get("/api/dashboard/summary", headers=_auth(token))
    assert r.status_code == 200
    return r.json()


def test_unauthenticated_returns_401(client):
    assert client.get("/api/dashboard/summary").status_code == 401


def test_empty_dashboard_returns_zeros(client):
    token = _register(client, "empty@example.com")
    s = _summary(client, token)
    assert s["service_summary"]["total_services"] == 0
    assert s["health_summary"]["latest_checks_count"] == 0
    assert s["health_summary"]["average_response_time_ms"] is None
    assert s["release_summary"]["total_releases"] == 0
    assert s["release_summary"]["average_readiness_score"] is None
    assert s["incident_summary"]["total_incidents"] == 0
    assert s["metrics_summary"]["total_metric_samples"] == 0
    assert s["metrics_summary"]["error_rate_percent"] == 0.0
    assert s["metrics_summary"]["slowest_endpoint"] is None
    assert s["recent_activity"] == []


def test_dashboard_counts_only_current_users_data(client):
    token_a = _register(client, "a@example.com")
    token_b = _register(client, "b@example.com")
    _service(client, token_a, "a-svc")
    _service(client, token_b, "b-svc-1")
    _service(client, token_b, "b-svc-2")

    s_a = _summary(client, token_a)
    s_b = _summary(client, token_b)
    assert s_a["service_summary"]["total_services"] == 1
    assert s_b["service_summary"]["total_services"] == 2


def test_service_summary_counts_statuses(client):
    token = _register(client, "maya@example.com")
    # New services default to 'unknown' status.
    _service(client, token, "s1")
    _service(client, token, "s2")
    _service(client, token, "s3")
    s = _summary(client, token)
    ss = s["service_summary"]
    assert ss["total_services"] == 3
    assert ss["unknown_services"] == 3
    assert ss["healthy_services"] == 0


def test_release_summary_counts_statuses_and_readiness(client):
    token = _register(client, "maya@example.com")
    sid = _service(client, token, "svc")
    r_planned = _release(client, token, sid, "1.0.0", status="planned")
    r_released = _release(client, token, sid, "1.1.0", status="released")
    r_rb = _release(client, token, sid, "1.2.0", status="rolled_back")

    # Readiness: one ready (100), one risky (60), one blocked (0/default).
    _set_checklist(client, token, r_planned, tests_passed=True, security_review_done=True,
                   rollback_plan_ready=True, monitoring_ready=True, stakeholder_approval=True)  # 100 ready
    _set_checklist(client, token, r_released, tests_passed=True, security_review_done=True,
                   rollback_plan_ready=True)  # 60 risky
    # r_rb left at default 0 -> blocked

    s = _summary(client, token)
    rs = s["release_summary"]
    assert rs["total_releases"] == 3
    assert rs["planned_releases"] == 1
    assert rs["released_releases"] == 1
    assert rs["rolled_back_releases"] == 1
    assert rs["ready_releases"] == 1
    assert rs["risky_releases"] == 1
    assert rs["blocked_releases"] == 1
    # average of 100, 60, 0 = 53.33
    assert abs(rs["average_readiness_score"] - 53.33) < 0.01


def test_incident_summary_counts_statuses_and_severities(client):
    token = _register(client, "maya@example.com")
    sid = _service(client, token, "svc")
    i1 = _incident(client, token, sid, "crit one", severity="critical", status="open")
    _incident(client, token, sid, "high one", severity="high", status="investigating")
    _incident(client, token, sid, "low one", severity="low", status="resolved")
    _incident_update(client, token, i1, "first update")
    _incident_update(client, token, i1, "second update")

    s = _summary(client, token)
    isum = s["incident_summary"]
    assert isum["total_incidents"] == 3
    assert isum["open_incidents"] == 1
    assert isum["investigating_incidents"] == 1
    assert isum["resolved_incidents"] == 1
    assert isum["critical_incidents"] == 1
    assert isum["high_incidents"] == 1
    assert isum["recent_updates_count"] == 2


def test_metrics_summary_calculations(client):
    token = _register(client, "maya@example.com")
    sid = _service(client, token, "svc")
    _metric(client, token, sid, "/api/a", "GET", latency=100, requests=200, errors=10)
    _metric(client, token, sid, "/api/b", "POST", latency=500, requests=300, errors=20)

    s = _summary(client, token)
    ms = s["metrics_summary"]
    assert ms["total_metric_samples"] == 2
    assert ms["average_latency_ms"] == 300.0  # (100+500)/2
    assert ms["total_requests"] == 500
    assert ms["total_errors"] == 30
    assert ms["error_rate_percent"] == 6.0  # 30/500*100
    assert ms["slowest_endpoint"] == "POST /api/b"
    assert ms["slowest_endpoint_latency_ms"] == 500


def test_recent_activity_has_multiple_types_and_is_sorted(client):
    token = _register(client, "maya@example.com")
    sid = _service(client, token, "payment-service")
    # Generate several activity types.
    _release(client, token, sid, "1.0.0", status="released")
    iid = _incident(client, token, sid, "latency spike", severity="high", status="investigating")
    _incident_update(client, token, iid, "looking into pool saturation")
    _metric(client, token, sid, "/api/payments", "POST", latency=145, requests=250, errors=3)

    s = _summary(client, token)
    activity = s["recent_activity"]
    assert len(activity) >= 4
    assert len(activity) <= 10
    types = {a["type"] for a in activity}
    # At least these types should appear.
    assert {"release", "incident", "incident_update", "metric"}.issubset(types)
    # Sorted newest first (non-increasing timestamps).
    timestamps = [a["timestamp"] for a in activity]
    assert timestamps == sorted(timestamps, reverse=True)
    # Each item has the required shape.
    for a in activity:
        assert set(a.keys()) == {"type", "title", "subtitle", "timestamp"}


def test_recent_activity_limited_to_10(client):
    token = _register(client, "maya@example.com")
    sid = _service(client, token, "svc")
    # 15 metrics -> activity must cap at 10.
    for n in range(15):
        _metric(client, token, sid, f"/api/{n}", "GET", latency=50 + n, requests=10, errors=0)
    s = _summary(client, token)
    assert len(s["recent_activity"]) == 10