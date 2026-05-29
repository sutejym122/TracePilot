"""Tests for the Health Checks vertical slice.

HTTP is mocked at app.domain.health_checker.httpx so checks are deterministic
and never hit the network. Covers manual success/failure, Service.status update,
listing, cross-user isolation, missing service, missing health_url, and 401.
"""
import uuid

import httpx
import pytest


def _register(client, email, password="supersecret", name="User"):
    resp = client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "name": name},
    )
    assert resp.status_code == 201
    return resp.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _make_service(client, token, name="auth-service", environment="prod",
                  health_url="https://svc.example.com/health"):
    body = {"name": name, "environment": environment}
    if health_url is not None:
        body["health_url"] = health_url
    resp = client.post("/api/services", json=body, headers=_auth(token))
    assert resp.status_code == 201
    return resp.json()


class _FakeResponse:
    def __init__(self, status_code):
        self.status_code = status_code


@pytest.fixture
def mock_http_ok(monkeypatch):
    """httpx.get returns 200."""
    def fake_get(url, **kwargs):
        return _FakeResponse(200)
    monkeypatch.setattr("app.domain.health_checker.httpx.get", fake_get)


@pytest.fixture
def mock_http_down(monkeypatch):
    """httpx.get raises a connection error."""
    def fake_get(url, **kwargs):
        raise httpx.ConnectError("refused")
    monkeypatch.setattr("app.domain.health_checker.httpx.get", fake_get)


def test_manual_health_check_success(client, mock_http_ok):
    token = _register(client, "maya@example.com")
    svc = _make_service(client, token)
    resp = client.post(f"/api/services/{svc['id']}/health/check", headers=_auth(token))
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "healthy"
    assert body["status_code"] == 200
    assert body["error_message"] is None
    assert body["response_time_ms"] is not None
    assert body["service_id"] == svc["id"]


def test_manual_health_check_failure(client, mock_http_down):
    token = _register(client, "maya@example.com")
    svc = _make_service(client, token)
    resp = client.post(f"/api/services/{svc['id']}/health/check", headers=_auth(token))
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "down"
    assert body["status_code"] is None
    assert body["error_message"] is not None


def test_health_check_updates_service_status(client, mock_http_down):
    token = _register(client, "maya@example.com")
    svc = _make_service(client, token)
    assert svc["status"] == "unknown"  # default before any check

    client.post(f"/api/services/{svc['id']}/health/check", headers=_auth(token))

    refreshed = client.get(f"/api/services/{svc['id']}", headers=_auth(token)).json()
    assert refreshed["status"] == "down"  # updated from the latest check


def test_list_health_checks_for_service(client, mock_http_ok):
    token = _register(client, "maya@example.com")
    svc = _make_service(client, token)
    client.post(f"/api/services/{svc['id']}/health/check", headers=_auth(token))
    client.post(f"/api/services/{svc['id']}/health/check", headers=_auth(token))

    resp = client.get(f"/api/services/{svc['id']}/health", headers=_auth(token))
    assert resp.status_code == 200
    checks = resp.json()
    assert len(checks) == 2
    assert all(c["status"] == "healthy" for c in checks)


def test_user_cannot_check_another_users_service(client, mock_http_ok):
    token_a = _register(client, "a@example.com")
    token_b = _register(client, "b@example.com")
    svc = _make_service(client, token_a)

    # B triggering a check on A's service -> 404
    assert client.post(
        f"/api/services/{svc['id']}/health/check", headers=_auth(token_b)
    ).status_code == 404
    # B listing A's service health -> 404
    assert client.get(
        f"/api/services/{svc['id']}/health", headers=_auth(token_b)
    ).status_code == 404


def test_missing_service_returns_404(client, mock_http_ok):
    token = _register(client, "maya@example.com")
    missing = uuid.uuid4()
    assert client.post(
        f"/api/services/{missing}/health/check", headers=_auth(token)
    ).status_code == 404
    assert client.get(
        f"/api/services/{missing}/health", headers=_auth(token)
    ).status_code == 404


def test_service_without_health_url_returns_validation_error(client):
    token = _register(client, "maya@example.com")
    svc = _make_service(client, token, health_url=None)  # no health_url
    resp = client.post(f"/api/services/{svc['id']}/health/check", headers=_auth(token))
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "validation_error"


def test_unauthenticated_returns_401(client):
    sid = uuid.uuid4()
    assert client.post(f"/api/services/{sid}/health/check").status_code == 401
    assert client.get(f"/api/services/{sid}/health").status_code == 401