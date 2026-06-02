"""Tests for the Incidents vertical slice.

Incidents are scoped through Incident.service_id -> Service.user_id. Covers
create, list, get, update, delete, 401, cross-user isolation on create and
access, 404 for missing service/incident, 422 for invalid enums, and the
resolved_at automation rules.
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


def _make_service(client, token, name="payment-service"):
    resp = client.post(
        "/api/services",
        json={"name": name, "environment": "prod"},
        headers=_auth(token),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def _make_incident(client, token, service_id, title="DB outage", severity="high", **extra):
    body = {"service_id": service_id, "title": title, "severity": severity, **extra}
    return client.post("/api/incidents", json=body, headers=_auth(token))


def test_create_incident(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    resp = _make_incident(
        client, token, sid, title="Payment failures", severity="critical",
        summary="5xx spike on /charge", root_cause="bad deploy",
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "Payment failures"
    assert body["severity"] == "critical"
    assert body["status"] == "open"  # default
    assert body["summary"] == "5xx spike on /charge"
    assert body["service_id"] == sid
    assert body["resolved_at"] is None
    assert "id" in body and "created_at" in body and "updated_at" in body


def test_list_incidents_returns_only_own(client):
    token_a = _register(client, "a@example.com")
    token_b = _register(client, "b@example.com")
    sid_a = _make_service(client, token_a, name="a-svc")
    sid_b = _make_service(client, token_b, name="b-svc")
    _make_incident(client, token_a, sid_a, title="a1")
    _make_incident(client, token_a, sid_a, title="a2")
    _make_incident(client, token_b, sid_b, title="b1")

    resp = client.get("/api/incidents", headers=_auth(token_a))
    assert resp.status_code == 200
    titles = {i["title"] for i in resp.json()}
    assert titles == {"a1", "a2"}


def test_get_incident_by_id(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    iid = _make_incident(client, token, sid, title="latency").json()["id"]
    resp = client.get(f"/api/incidents/{iid}", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["title"] == "latency"


def test_update_incident(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    iid = _make_incident(client, token, sid, severity="low").json()["id"]
    resp = client.patch(
        f"/api/incidents/{iid}",
        json={"severity": "high", "status": "investigating", "root_cause": "memory leak"},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["severity"] == "high"
    assert body["status"] == "investigating"
    assert body["root_cause"] == "memory leak"


def test_delete_incident(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    iid = _make_incident(client, token, sid).json()["id"]
    resp = client.delete(f"/api/incidents/{iid}", headers=_auth(token))
    assert resp.status_code == 204
    assert client.get(f"/api/incidents/{iid}", headers=_auth(token)).status_code == 404


def test_unauthenticated_returns_401(client):
    assert client.get("/api/incidents").status_code == 401
    assert client.post(
        "/api/incidents",
        json={"service_id": str(uuid.uuid4()), "title": "x", "severity": "low"},
    ).status_code == 401


def test_user_cannot_create_incident_for_another_users_service(client):
    token_a = _register(client, "a@example.com")
    token_b = _register(client, "b@example.com")
    sid_a = _make_service(client, token_a)
    resp = _make_incident(client, token_b, sid_a, title="evil")
    assert resp.status_code == 404


def test_user_cannot_access_another_users_incident(client):
    token_a = _register(client, "a@example.com")
    token_b = _register(client, "b@example.com")
    sid_a = _make_service(client, token_a)
    iid = _make_incident(client, token_a, sid_a).json()["id"]

    assert client.get(f"/api/incidents/{iid}", headers=_auth(token_b)).status_code == 404
    assert client.patch(
        f"/api/incidents/{iid}", json={"status": "resolved"}, headers=_auth(token_b)
    ).status_code == 404
    assert client.delete(f"/api/incidents/{iid}", headers=_auth(token_b)).status_code == 404


def test_missing_service_returns_404_on_create(client):
    token = _register(client, "maya@example.com")
    resp = _make_incident(client, token, str(uuid.uuid4()))
    assert resp.status_code == 404


def test_missing_incident_returns_404(client):
    token = _register(client, "maya@example.com")
    iid = uuid.uuid4()
    assert client.get(f"/api/incidents/{iid}", headers=_auth(token)).status_code == 404
    assert client.patch(
        f"/api/incidents/{iid}", json={"status": "resolved"}, headers=_auth(token)
    ).status_code == 404
    assert client.delete(f"/api/incidents/{iid}", headers=_auth(token)).status_code == 404


def test_invalid_severity_returns_422(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    resp = _make_incident(client, token, sid, severity="catastrophic")
    assert resp.status_code == 422


def test_invalid_status_returns_422(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    resp = _make_incident(client, token, sid, status="closed")
    assert resp.status_code == 422


def test_missing_required_severity_returns_422(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    resp = client.post(
        "/api/incidents",
        json={"service_id": sid, "title": "no severity"},
        headers=_auth(token),
    )
    assert resp.status_code == 422


# --- resolved_at automation ---
def test_resolving_auto_sets_resolved_at(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    iid = _make_incident(client, token, sid).json()["id"]
    resp = client.patch(
        f"/api/incidents/{iid}", json={"status": "resolved"}, headers=_auth(token)
    )
    assert resp.status_code == 200
    assert resp.json()["resolved_at"] is not None


def test_resolving_with_explicit_resolved_at_is_respected(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    iid = _make_incident(client, token, sid).json()["id"]
    explicit = "2026-01-01T00:00:00+00:00"
    resp = client.patch(
        f"/api/incidents/{iid}",
        json={"status": "resolved", "resolved_at": explicit},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["resolved_at"].startswith("2026-01-01T00:00:00")


def test_moving_away_from_resolved_keeps_resolved_at(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    iid = _make_incident(client, token, sid).json()["id"]
    # resolve (auto-stamps resolved_at)
    client.patch(f"/api/incidents/{iid}", json={"status": "resolved"}, headers=_auth(token))
    # reopen without sending resolved_at -> resolved_at preserved
    resp = client.patch(
        f"/api/incidents/{iid}", json={"status": "investigating"}, headers=_auth(token)
    )
    assert resp.status_code == 200
    assert resp.json()["resolved_at"] is not None


def test_explicit_null_clears_resolved_at(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    iid = _make_incident(client, token, sid).json()["id"]
    client.patch(f"/api/incidents/{iid}", json={"status": "resolved"}, headers=_auth(token))
    # explicitly send resolved_at: null while moving away -> cleared
    resp = client.patch(
        f"/api/incidents/{iid}",
        json={"status": "open", "resolved_at": None},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["resolved_at"] is None