"""Rollback readiness scoring — a pure function, no DB, no HTTP.

Score is derivable state and is never stored (see Phase 1 tradeoffs). Five
boolean checks -> a percentage. is_ready trips at the threshold.
"""
READY_THRESHOLD = 80

CHECK_FIELDS = (
    "tests_passed",
    "migration_reviewed",
    "rollback_plan_ready",
    "monitoring_enabled",
    "owner_assigned",
)


def compute_score(checks: dict[str, bool]) -> tuple[int, bool]:
    """Return (score 0-100, is_ready) from the five checklist booleans.

    Unknown/missing keys count as False. Extra keys are ignored.
    """
    total = len(CHECK_FIELDS)
    passed = sum(1 for f in CHECK_FIELDS if checks.get(f))
    score = round(passed / total * 100)
    return score, score >= READY_THRESHOLD
