"""Unit tests for the readiness scoring/status pure functions."""
from app.domain.readiness import (
    ReadinessStatus,
    compute_readiness,
    compute_score,
    compute_status,
)

ALL_FIELDS = [
    "tests_passed",
    "security_review_done",
    "rollback_plan_ready",
    "monitoring_ready",
    "stakeholder_approval",
]


def test_score_scales_by_twenty():
    for n in range(6):
        checks = {f: True for f in ALL_FIELDS[:n]}
        assert compute_score(checks) == n * 20


def test_status_thresholds():
    assert compute_status(0) == ReadinessStatus.blocked
    assert compute_status(20) == ReadinessStatus.blocked
    assert compute_status(40) == ReadinessStatus.blocked
    assert compute_status(60) == ReadinessStatus.risky
    assert compute_status(80) == ReadinessStatus.risky
    assert compute_status(100) == ReadinessStatus.ready


def test_compute_readiness_all_true():
    checks = {f: True for f in ALL_FIELDS}
    score, status = compute_readiness(checks)
    assert score == 100
    assert status == ReadinessStatus.ready


def test_compute_readiness_none():
    score, status = compute_readiness({})
    assert score == 0
    assert status == ReadinessStatus.blocked


def test_unknown_keys_ignored():
    score, status = compute_readiness({"tests_passed": True, "bogus": True})
    assert score == 20
    assert status == ReadinessStatus.blocked