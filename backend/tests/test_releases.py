"""Tests for the Releases vertical slice.

Releases are scoped through the linked Service (Service.user_id). Covers create,
list, get, update, delete, 401, cross-user isolation on both create and access,
and 404 for missing service / missing release.
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


def _make_service(client, token, name="payment-service", environment="prod"):
    resp = client.post(
        "/api/services",
        json={"name": name, "environment": environment},
        headers=_auth(token),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def _make_release(client, token, service_id, version="1.0.0", environment="prod", **extra):
    body = {"service_id": service_id, "version": version, "environment": environment, **extra}
    return client.post("/api/releases", json=body, headers=_auth(token))


def test_create_release(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    resp = _make_release(
        client, token, sid, version="1.4.2", environment="prod",
        owner="maya", release_notes="First prod cut",
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["version"] == "1.4.2"
    assert body["environment"] == "prod"
    assert body["owner"] == "maya"
    assert body["release_notes"] == "First prod cut"
    assert body["status"] == "planned"  # default
    assert body["service_id"] == sid
    assert body["released_at"] is None
    assert "id" in body and "created_at" in body and "updated_at" in body


def test_create_release_rejects_bad_status(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    resp = _make_release(client, token, sid, status="deployed")  # not a valid status
    assert resp.status_code == 422


def test_list_releases_returns_only_own(client):
    token_a = _register(client, "a@example.com")
    token_b = _register(client, "b@example.com")
    sid_a = _make_service(client, token_a, name="a-svc")
    sid_b = _make_service(client, token_b, name="b-svc")
    _make_release(client, token_a, sid_a, version="a1")
    _make_release(client, token_a, sid_a, version="a2")
    _make_release(client, token_b, sid_b, version="b1")

    resp = client.get("/api/releases", headers=_auth(token_a))
    assert resp.status_code == 200
    versions = {r["version"] for r in resp.json()}
    assert versions == {"a1", "a2"}  # never sees b1


def test_get_release_by_id(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    rid = _make_release(client, token, sid, version="2.0.0").json()["id"]
    resp = client.get(f"/api/releases/{rid}", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["version"] == "2.0.0"


def test_update_release(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    rid = _make_release(client, token, sid, version="1.0.0").json()["id"]
    resp = client.patch(
        f"/api/releases/{rid}",
        json={"status": "released", "owner": "platform"},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "released"
    assert body["owner"] == "platform"
    assert body["version"] == "1.0.0"  # unchanged field stays


def test_delete_release(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    rid = _make_release(client, token, sid).json()["id"]
    resp = client.delete(f"/api/releases/{rid}", headers=_auth(token))
    assert resp.status_code == 204
    assert client.get(f"/api/releases/{rid}", headers=_auth(token)).status_code == 404


def test_unauthenticated_returns_401(client):
    assert client.get("/api/releases").status_code == 401
    assert client.post(
        "/api/releases",
        json={"service_id": str(uuid.uuid4()), "version": "1", "environment": "dev"},
    ).status_code == 401


def test_user_cannot_create_release_for_another_users_service(client):
    token_a = _register(client, "a@example.com")
    token_b = _register(client, "b@example.com")
    sid_a = _make_service(client, token_a)  # owned by A
    # B tries to create a release against A's service -> 404 (service not found for B)
    resp = _make_release(client, token_b, sid_a, version="evil")
    assert resp.status_code == 404


def test_user_cannot_access_another_users_release(client):
    token_a = _register(client, "a@example.com")
    token_b = _register(client, "b@example.com")
    sid_a = _make_service(client, token_a)
    rid = _make_release(client, token_a, sid_a, version="1.0.0").json()["id"]

    # B cannot read, update, or delete A's release.
    assert client.get(f"/api/releases/{rid}", headers=_auth(token_b)).status_code == 404
    assert client.patch(
        f"/api/releases/{rid}", json={"status": "rolled_back"}, headers=_auth(token_b)
    ).status_code == 404
    assert client.delete(f"/api/releases/{rid}", headers=_auth(token_b)).status_code == 404

    # A's release is untouched.
    a_view = client.get(f"/api/releases/{rid}", headers=_auth(token_a))
    assert a_view.status_code == 200
    assert a_view.json()["status"] == "planned"


def test_missing_service_returns_404_on_create(client):
    token = _register(client, "maya@example.com")
    resp = _make_release(client, token, str(uuid.uuid4()), version="1.0.0")
    assert resp.status_code == 404


def test_missing_release_returns_404(client):
    token = _register(client, "maya@example.com")
    rid = uuid.uuid4()
    assert client.get(f"/api/releases/{rid}", headers=_auth(token)).status_code == 404
    assert client.patch(
        f"/api/releases/{rid}", json={"status": "released"}, headers=_auth(token)
    ).status_code == 404
    assert client.delete(f"/api/releases/{rid}", headers=_auth(token)).status_code == 404