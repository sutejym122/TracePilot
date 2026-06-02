"""Tests for the Incident Updates / Timeline vertical slice.

Updates are scoped through IncidentUpdate -> Incident -> Service -> user_id.
Covers create, list, chronological ordering, 401, cross-user isolation on
create and list, 404 for missing incident, 422 for empty/missing message, and
the optional status propagation (including resolved_at automation).
"""
import time
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


def _make_incident(client, token, service_id, title="DB outage", severity="high"):
    resp = client.post(
        "/api/incidents",
        json={"service_id": service_id, "title": title, "severity": severity},
        headers=_auth(token),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def _add_update(client, token, incident_id, message="looking into it", **extra):
    body = {"message": message, **extra}
    return client.post(
        f"/api/incidents/{incident_id}/updates", json=body, headers=_auth(token)
    )


def test_create_incident_update(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    iid = _make_incident(client, token, sid)
    resp = _add_update(client, token, iid, message="Investigating root cause", author="maya")
    assert resp.status_code == 201
    body = resp.json()
    assert body["message"] == "Investigating root cause"
    assert body["author"] == "maya"
    assert body["incident_id"] == iid
    assert body["status"] is None
    assert "id" in body and "created_at" in body and "updated_at" in body


def test_list_incident_updates(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    iid = _make_incident(client, token, sid)
    _add_update(client, token, iid, message="one")
    _add_update(client, token, iid, message="two")
    resp = client.get(f"/api/incidents/{iid}/updates", headers=_auth(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_updates_returned_in_chronological_order(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    iid = _make_incident(client, token, sid)
    _add_update(client, token, iid, message="first")
    time.sleep(0.01)
    _add_update(client, token, iid, message="second")
    time.sleep(0.01)
    _add_update(client, token, iid, message="third")
    resp = client.get(f"/api/incidents/{iid}/updates", headers=_auth(token))
    messages = [u["message"] for u in resp.json()]
    assert messages == ["first", "second", "third"]  # oldest first


def test_unauthenticated_returns_401(client):
    iid = uuid.uuid4()
    assert client.get(f"/api/incidents/{iid}/updates").status_code == 401
    assert client.post(
        f"/api/incidents/{iid}/updates", json={"message": "x"}
    ).status_code == 401


def test_user_cannot_create_update_for_another_users_incident(client):
    token_a = _register(client, "a@example.com")
    token_b = _register(client, "b@example.com")
    sid_a = _make_service(client, token_a)
    iid = _make_incident(client, token_a, sid_a)
    resp = _add_update(client, token_b, iid, message="intrusion")
    assert resp.status_code == 404


def test_user_cannot_list_updates_for_another_users_incident(client):
    token_a = _register(client, "a@example.com")
    token_b = _register(client, "b@example.com")
    sid_a = _make_service(client, token_a)
    iid = _make_incident(client, token_a, sid_a)
    _add_update(client, token_a, iid, message="private")
    resp = client.get(f"/api/incidents/{iid}/updates", headers=_auth(token_b))
    assert resp.status_code == 404


def test_missing_incident_returns_404(client):
    token = _register(client, "maya@example.com")
    iid = uuid.uuid4()
    assert client.get(f"/api/incidents/{iid}/updates", headers=_auth(token)).status_code == 404
    assert _add_update(client, token, iid, message="hi").status_code == 404


def test_empty_message_returns_422(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    iid = _make_incident(client, token, sid)
    assert _add_update(client, token, iid, message="").status_code == 422


def test_missing_message_returns_422(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    iid = _make_incident(client, token, sid)
    resp = client.post(
        f"/api/incidents/{iid}/updates", json={"author": "maya"}, headers=_auth(token)
    )
    assert resp.status_code == 422


def test_invalid_status_returns_422(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    iid = _make_incident(client, token, sid)
    resp = _add_update(client, token, iid, message="bad", status="closed")
    assert resp.status_code == 422


def test_update_with_status_changes_parent_incident(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    iid = _make_incident(client, token, sid)  # starts 'open'
    resp = _add_update(client, token, iid, message="mitigating now", status="mitigated")
    assert resp.status_code == 201
    assert resp.json()["status"] == "mitigated"
    # Parent incident status updated too.
    inc = client.get(f"/api/incidents/{iid}", headers=_auth(token)).json()
    assert inc["status"] == "mitigated"


def test_update_without_status_leaves_incident_unchanged(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    iid = _make_incident(client, token, sid)
    _add_update(client, token, iid, message="no status here")
    inc = client.get(f"/api/incidents/{iid}", headers=_auth(token)).json()
    assert inc["status"] == "open"  # unchanged


def test_update_resolving_sets_resolved_at(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    iid = _make_incident(client, token, sid)
    # before: not resolved
    assert client.get(f"/api/incidents/{iid}", headers=_auth(token)).json()["resolved_at"] is None
    _add_update(client, token, iid, message="all clear", status="resolved")
    inc = client.get(f"/api/incidents/{iid}", headers=_auth(token)).json()
    assert inc["status"] == "resolved"
    assert inc["resolved_at"] is not None