"""Release readiness scoring — pure functions, no DB, no HTTP.

Score and status are derivable from the five checklist booleans. They are
computed here and stored on the checklist row (denormalized) so reads are
cheap and the API can return them directly; the single writer is the checklist
update path, so they cannot drift.

Score: each of the five items contributes 20 points (0..100).
Status:
    0 - 40  -> blocked
    60 - 80 -> risky
    100     -> ready
"""
import enum

CHECK_FIELDS = (
    "tests_passed",
    "security_review_done",
    "rollback_plan_ready",
    "monitoring_ready",
    "stakeholder_approval",
)


class ReadinessStatus(str, enum.Enum):
    blocked = "blocked"
    risky = "risky"
    ready = "ready"


def compute_score(checks: dict[str, bool]) -> int:
    """Return an integer percentage (0..100) from the five checklist booleans.

    Missing keys count as False. Extra keys are ignored.
    """
    passed = sum(1 for f in CHECK_FIELDS if checks.get(f))
    return passed * 20  # 5 items * 20 = 100


def compute_status(score: int) -> ReadinessStatus:
    """Map a score to a readiness status.

    0-40 -> blocked, 60-80 -> risky, 100 -> ready.
    """
    if score >= 100:
        return ReadinessStatus.ready
    if score >= 60:
        return ReadinessStatus.risky
    return ReadinessStatus.blocked


def compute_readiness(checks: dict[str, bool]) -> tuple[int, ReadinessStatus]:
    """Convenience: return (score, status) together."""
    score = compute_score(checks)
    return score, compute_status(score)