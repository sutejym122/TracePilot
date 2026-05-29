"""Tests for the Service Registry vertical slice (Phase 2 schema).

Covers create, list, get, update, delete, the unauthenticated 401, and the
cross-user isolation rule (one user's service is 404 to another user).
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


def _make_service(client, token, name="auth-service", environment="prod", **extra):
    body = {"name": name, "environment": environment, **extra}
    return client.post("/api/services", json=body, headers=_auth(token))


def test_create_service(client):
    token = _register(client, "maya@example.com")
    resp = _make_service(
        client, token, name="payment-service", environment="prod",
        owner="payments-team",
        repo_url="https://github.com/acme/payments",
        health_url="https://pay.acme.dev/healthz",
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "payment-service"
    assert body["environment"] == "prod"
    assert body["owner"] == "payments-team"
    assert body["health_url"] == "https://pay.acme.dev/healthz"
    # Server-controlled defaults.
    assert body["status"] == "unknown"
    assert body["last_deployed_at"] is None
    assert "id" in body and "user_id" in body
    assert "created_at" in body and "updated_at" in body


def test_create_service_rejects_bad_environment(client):
    token = _register(client, "maya@example.com")
    resp = _make_service(client, token, environment="staging")
    assert resp.status_code == 422


def test_list_services_returns_only_own(client):
    token_a = _register(client, "a@example.com")
    token_b = _register(client, "b@example.com")
    _make_service(client, token_a, name="a-svc")
    _make_service(client, token_a, name="a-svc-2")
    _make_service(client, token_b, name="b-svc")

    resp = client.get("/api/services", headers=_auth(token_a))
    assert resp.status_code == 200
    names = {s["name"] for s in resp.json()}
    assert names == {"a-svc", "a-svc-2"}  # never sees b-svc


def test_get_service_by_id(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token, name="search-service").json()["id"]
    resp = client.get(f"/api/services/{sid}", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["name"] == "search-service"


def test_update_service(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token, name="notif-service", environment="dev").json()["id"]
    resp = client.patch(
        f"/api/services/{sid}",
        json={"environment": "prod", "owner": "platform"},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["environment"] == "prod"
    assert body["owner"] == "platform"
    assert body["name"] == "notif-service"  # unchanged field stays


def test_delete_service(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token).json()["id"]
    resp = client.delete(f"/api/services/{sid}", headers=_auth(token))
    assert resp.status_code == 204
    assert client.get(f"/api/services/{sid}", headers=_auth(token)).status_code == 404


def test_unauthorized_returns_401(client):
    assert client.get("/api/services").status_code == 401
    assert client.post("/api/services", json={"name": "x", "environment": "dev"}).status_code == 401


def test_user_cannot_access_another_users_service(client):
    token_a = _register(client, "a@example.com")
    token_b = _register(client, "b@example.com")
    sid = _make_service(client, token_a, name="a-private").json()["id"]

    # B cannot read, update, or delete A's service — all 404 (not 403).
    assert client.get(f"/api/services/{sid}", headers=_auth(token_b)).status_code == 404
    assert client.patch(
        f"/api/services/{sid}", json={"owner": "hacker"}, headers=_auth(token_b)
    ).status_code == 404
    assert client.delete(f"/api/services/{sid}", headers=_auth(token_b)).status_code == 404

    # A's service is untouched.
    a_view = client.get(f"/api/services/{sid}", headers=_auth(token_a))
    assert a_view.status_code == 200
    assert a_view.json()["owner"] != "hacker"


def test_get_missing_service_returns_404(client):
    token = _register(client, "maya@example.com")
    resp = client.get(f"/api/services/{uuid.uuid4()}", headers=_auth(token))
    assert resp.status_code == 404