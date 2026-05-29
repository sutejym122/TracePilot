"""Smoke tests proving the app boots and the basic wiring works."""


def test_liveness(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_openapi_docs_available(client):
    assert client.get("/openapi.json").status_code == 200


def test_protected_route_requires_auth(client):
    # No bearer token -> 401 from the OAuth2 scheme.
    assert client.get("/api/dashboard/summary").status_code == 401
