"""Tests for the Release Checklist + Readiness vertical slice.

Checklists are scoped through Release -> Service -> Service.user_id. A checklist
is auto-created with the release (Option A). Covers auto-create, get, update,
score/status recomputation, cross-user isolation, 404, 401, and 422.
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


def _make_release(client, token, service_id, version="1.0.0"):
    resp = client.post(
        "/api/releases",
        json={"service_id": service_id, "version": version, "environment": "prod"},
        headers=_auth(token),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def test_checklist_created_with_release(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    rid = _make_release(client, token, sid)
    resp = client.get(f"/api/releases/{rid}/checklist", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    # All booleans default false, score 0, status blocked.
    for f in ["tests_passed", "security_review_done", "rollback_plan_ready",
              "monitoring_ready", "stakeholder_approval"]:
        assert body[f] is False
    assert body["readiness_score"] == 0
    assert body["readiness_status"] == "blocked"
    assert body["release_id"] == rid


def test_get_checklist_for_owned_release(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    rid = _make_release(client, token, sid)
    resp = client.get(f"/api/releases/{rid}/checklist", headers=_auth(token))
    assert resp.status_code == 200
    assert "readiness_score" in resp.json()


def test_update_checklist_recomputes_score_and_status(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    rid = _make_release(client, token, sid)

    # 2 true -> 40 -> blocked
    resp = client.patch(
        f"/api/releases/{rid}/checklist",
        json={"tests_passed": True, "security_review_done": True},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["readiness_score"] == 40
    assert body["readiness_status"] == "blocked"

    # add one more -> 3 true -> 60 -> risky
    resp = client.patch(
        f"/api/releases/{rid}/checklist",
        json={"rollback_plan_ready": True},
        headers=_auth(token),
    )
    assert resp.json()["readiness_score"] == 60
    assert resp.json()["readiness_status"] == "risky"


def test_update_checklist_full_ready(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    rid = _make_release(client, token, sid)
    resp = client.patch(
        f"/api/releases/{rid}/checklist",
        json={
            "tests_passed": True, "security_review_done": True,
            "rollback_plan_ready": True, "monitoring_ready": True,
            "stakeholder_approval": True,
        },
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["readiness_score"] == 100
    assert resp.json()["readiness_status"] == "ready"


def test_update_checklist_can_toggle_back_down(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    rid = _make_release(client, token, sid)
    client.patch(
        f"/api/releases/{rid}/checklist",
        json={"tests_passed": True, "security_review_done": True, "rollback_plan_ready": True},
        headers=_auth(token),
    )
    # turn one back off -> 2 true -> 40 -> blocked
    resp = client.patch(
        f"/api/releases/{rid}/checklist",
        json={"tests_passed": False},
        headers=_auth(token),
    )
    assert resp.json()["readiness_score"] == 40
    assert resp.json()["readiness_status"] == "blocked"


def test_user_cannot_view_or_update_another_users_checklist(client):
    token_a = _register(client, "a@example.com")
    token_b = _register(client, "b@example.com")
    sid_a = _make_service(client, token_a)
    rid = _make_release(client, token_a, sid_a)

    assert client.get(
        f"/api/releases/{rid}/checklist", headers=_auth(token_b)
    ).status_code == 404
    assert client.patch(
        f"/api/releases/{rid}/checklist",
        json={"tests_passed": True}, headers=_auth(token_b),
    ).status_code == 404


def test_missing_release_returns_404(client):
    token = _register(client, "maya@example.com")
    rid = uuid.uuid4()
    assert client.get(f"/api/releases/{rid}/checklist", headers=_auth(token)).status_code == 404
    assert client.patch(
        f"/api/releases/{rid}/checklist", json={"tests_passed": True}, headers=_auth(token)
    ).status_code == 404


def test_unauthenticated_returns_401(client):
    rid = uuid.uuid4()
    assert client.get(f"/api/releases/{rid}/checklist").status_code == 401
    assert client.patch(
        f"/api/releases/{rid}/checklist", json={"tests_passed": True}
    ).status_code == 401


def test_invalid_checklist_payload_returns_422(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    rid = _make_release(client, token, sid)
    # unknown field (extra="forbid") -> 422
    resp = client.patch(
        f"/api/releases/{rid}/checklist",
        json={"not_a_field": True},
        headers=_auth(token),
    )
    assert resp.status_code == 422
    # wrong type for a real field -> 422
    resp2 = client.patch(
        f"/api/releases/{rid}/checklist",
        json={"tests_passed": "yes"},
        headers=_auth(token),
    )
    assert resp2.status_code == 422


def test_client_cannot_set_computed_fields(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    rid = _make_release(client, token, sid)
    # readiness_score is not an accepted input (extra="forbid") -> 422
    resp = client.patch(
        f"/api/releases/{rid}/checklist",
        json={"readiness_score": 100},
        headers=_auth(token),
    )
    assert resp.status_code == 422