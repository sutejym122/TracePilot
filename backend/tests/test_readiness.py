"""Unit tests for the one fully-implemented domain function."""
from app.domain.readiness import compute_score


def test_all_checks_passed():
    checks = {
        "tests_passed": True,
        "migration_reviewed": True,
        "rollback_plan_ready": True,
        "monitoring_enabled": True,
        "owner_assigned": True,
    }
    score, ready = compute_score(checks)
    assert score == 100
    assert ready is True


def test_no_checks_passed():
    score, ready = compute_score({})
    assert score == 0
    assert ready is False


def test_partial_below_threshold():
    score, ready = compute_score({"tests_passed": True, "owner_assigned": True})
    assert score == 40
    assert ready is False
