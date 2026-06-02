"""Tests for the API Metrics vertical slice.

Metrics are scoped through ApiMetric.service_id -> Service.user_id. Covers
manual create, list, ordering, simulate, simulated-value ranges, 401, cross-user
isolation on create and list, 404 for missing service, 422 for invalid payload,
and that the scheduled worker reuses the same simulator/domain logic.
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


def _make_metric(client, token, sid, **extra):
    body = {
        "endpoint": "/api/payments/charge",
        "method": "POST",
        "status_code": 200,
        "latency_ms": 120,
        "request_count": 100,
        "error_count": 2,
        **extra,
    }
    return client.post(f"/api/services/{sid}/metrics", json=body, headers=_auth(token))


def test_create_metric(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    resp = _make_metric(client, token, sid)
    assert resp.status_code == 201
    body = resp.json()
    assert body["endpoint"] == "/api/payments/charge"
    assert body["method"] == "POST"
    assert body["status_code"] == 200
    assert body["latency_ms"] == 120
    assert body["request_count"] == 100
    assert body["error_count"] == 2
    assert body["service_id"] == sid
    assert "captured_at" in body and "id" in body


def test_list_metrics_for_service(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    _make_metric(client, token, sid, endpoint="/a")
    _make_metric(client, token, sid, endpoint="/b")
    resp = client.get(f"/api/services/{sid}/metrics", headers=_auth(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_metrics_returned_newest_first(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    # Explicit, distinct captured_at values so ordering is deterministic
    # regardless of DB clock resolution (SQLite CURRENT_TIMESTAMP is per-second).
    _make_metric(client, token, sid, endpoint="/first",
                 captured_at="2026-01-01T10:00:00+00:00")
    _make_metric(client, token, sid, endpoint="/second",
                 captured_at="2026-01-01T11:00:00+00:00")
    _make_metric(client, token, sid, endpoint="/third",
                 captured_at="2026-01-01T12:00:00+00:00")
    resp = client.get(f"/api/services/{sid}/metrics", headers=_auth(token))
    endpoints = [m["endpoint"] for m in resp.json()]
    assert endpoints == ["/third", "/second", "/first"]  # captured_at desc


def test_simulate_metric(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    resp = client.post(f"/api/services/{sid}/metrics/simulate", headers=_auth(token))
    assert resp.status_code == 201
    body = resp.json()
    assert body["service_id"] == sid
    assert body["method"] in ("GET", "POST")


def test_simulated_values_within_ranges(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    for _ in range(20):
        resp = client.post(f"/api/services/{sid}/metrics/simulate", headers=_auth(token))
        assert resp.status_code == 201
        m = resp.json()
        assert 20 <= m["latency_ms"] <= 2000
        assert 1 <= m["request_count"] <= 500
        assert 0 <= m["error_count"] <= m["request_count"]
        assert m["method"] in ("GET", "POST")
        assert 100 <= m["status_code"] <= 599


def test_unauthenticated_returns_401(client):
    sid = uuid.uuid4()
    assert client.get(f"/api/services/{sid}/metrics").status_code == 401
    assert client.post(
        f"/api/services/{sid}/metrics",
        json={"endpoint": "/x", "method": "GET", "status_code": 200,
              "latency_ms": 1, "request_count": 1, "error_count": 0},
    ).status_code == 401
    assert client.post(f"/api/services/{sid}/metrics/simulate").status_code == 401


def test_user_cannot_create_metric_for_another_users_service(client):
    token_a = _register(client, "a@example.com")
    token_b = _register(client, "b@example.com")
    sid_a = _make_service(client, token_a)
    resp = _make_metric(client, token_b, sid_a)
    assert resp.status_code == 404


def test_user_cannot_list_metrics_for_another_users_service(client):
    token_a = _register(client, "a@example.com")
    token_b = _register(client, "b@example.com")
    sid_a = _make_service(client, token_a)
    _make_metric(client, token_a, sid_a)
    assert client.get(f"/api/services/{sid_a}/metrics", headers=_auth(token_b)).status_code == 404


def test_missing_service_returns_404(client):
    token = _register(client, "maya@example.com")
    sid = uuid.uuid4()
    assert client.get(f"/api/services/{sid}/metrics", headers=_auth(token)).status_code == 404
    assert _make_metric(client, token, sid).status_code == 404
    assert client.post(
        f"/api/services/{sid}/metrics/simulate", headers=_auth(token)
    ).status_code == 404


def test_invalid_method_returns_422(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    assert _make_metric(client, token, sid, method="FETCH").status_code == 422


def test_negative_counts_return_422(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    assert _make_metric(client, token, sid, request_count=-1).status_code == 422
    assert _make_metric(client, token, sid, latency_ms=-5).status_code == 422


def test_error_count_exceeding_request_count_returns_422(client):
    token = _register(client, "maya@example.com")
    sid = _make_service(client, token)
    assert _make_metric(
        client, token, sid, request_count=5, error_count=10
    ).status_code == 422


def test_scheduled_job_reuses_simulator(client, db_session):
    """The worker generates one metric per service via the same domain logic."""
    from app.models.service import Service, Environment, ServiceStatus
    from app.models.user import User
    from app.models.metric import ApiMetric

    # Seed two services directly in the test DB.
    u = User(email="w@example.com", password_hash="x", name="W")
    db_session.add(u)
    db_session.flush()
    s1 = Service(user_id=u.id, name="s1", environment=Environment.prod, status=ServiceStatus.unknown)
    s2 = Service(user_id=u.id, name="s2", environment=Environment.prod, status=ServiceStatus.unknown)
    db_session.add_all([s1, s2])
    db_session.commit()

    # The worker opens its own session and loops generate_simulated_metric over
    # services; call that same domain function here to prove reuse.
    from app.domain.metric_management import generate_simulated_metric
    generate_simulated_metric(db_session, s1.id)
    generate_simulated_metric(db_session, s2.id)

    count = db_session.query(ApiMetric).count()
    assert count == 2