"""Generate believable ApiMetric values for a service (MVP — no real traffic).

simulate_metric_values() returns a dict of field values within realistic ranges.
It accepts an optional random.Random so tests can seed it for deterministic
output; without one it uses a fresh Random (still range-valid). The values are
always internally consistent (error_count <= request_count, status_code in a
plausible set).

Ranges:
    latency_ms    : 20 .. 2000
    request_count : 1 .. 500
    error_count   : 0 .. request_count
    status_code   : usually 200, occasionally 400/404/500
"""
import random

ENDPOINTS = (
    "/api/checkout",
    "/api/payments",
    "/api/orders",
    "/api/users/me",
    "/api/search",
)
METHODS = ("GET", "POST")
# Weighted so 200 dominates, with occasional client/server errors.
STATUS_CHOICES = (200, 200, 200, 200, 200, 200, 200, 400, 404, 500)

LATENCY_MIN, LATENCY_MAX = 20, 2000
REQUEST_MIN, REQUEST_MAX = 1, 500


def simulate_metric_values(rng: random.Random | None = None) -> dict:
    """Return a dict of realistic, internally-consistent metric values."""
    r = rng or random.Random()

    request_count = r.randint(REQUEST_MIN, REQUEST_MAX)
    status_code = r.choice(STATUS_CHOICES)

    # Errors cluster low; a 5xx sample tends to carry more errors.
    if status_code >= 500:
        max_errors = request_count
    elif status_code >= 400:
        max_errors = max(1, request_count // 4)
    else:
        max_errors = max(0, request_count // 20)
    error_count = r.randint(0, max_errors) if max_errors > 0 else 0

    return {
        "endpoint": r.choice(ENDPOINTS),
        "method": r.choice(METHODS),
        "status_code": status_code,
        "latency_ms": r.randint(LATENCY_MIN, LATENCY_MAX),
        "request_count": request_count,
        "error_count": error_count,
    }