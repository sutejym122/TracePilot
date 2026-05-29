"""Tests for the auth + users vertical slice: signup, login, protected route."""


def _register(client, email="maya@example.com", password="supersecret", name="Maya"):
    return client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "name": name},
    )


def test_register_returns_user_and_token(client):
    resp = _register(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "maya@example.com"
    assert body["name"] == "Maya"
    assert "id" in body and "created_at" in body
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    # The hash must never be exposed.
    assert "password" not in body and "password_hash" not in body


def test_register_duplicate_email_conflicts(client):
    _register(client)
    resp = _register(client)  # same email again
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "conflict"


def test_register_rejects_short_password(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "x@example.com", "password": "short", "name": "X"},
    )
    assert resp.status_code == 422  # Pydantic min_length


def test_login_success_returns_token(client):
    _register(client)
    resp = client.post(
        "/api/auth/login",
        json={"email": "maya@example.com", "password": "supersecret"},
    )
    assert resp.status_code == 200
    assert resp.json()["access_token"]


def test_login_wrong_password_rejected(client):
    _register(client)
    resp = client.post(
        "/api/auth/login",
        json={"email": "maya@example.com", "password": "wrongpass"},
    )
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "auth_error"


def test_login_unknown_email_rejected(client):
    resp = client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "whatever123"},
    )
    assert resp.status_code == 401


def test_me_requires_token(client):
    assert client.get("/api/users/me").status_code == 401


def test_me_returns_current_user(client):
    token = _register(client).json()["access_token"]
    resp = client.get(
        "/api/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "maya@example.com"
    assert body["name"] == "Maya"
    assert "password_hash" not in body


def test_me_rejects_garbage_token(client):
    resp = client.get(
        "/api/users/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert resp.status_code == 401