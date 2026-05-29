"""Idempotent demo-data loader: `python -m app.seed`.

Builds a coherent demo world (Phase 2 plan): a demo user, 4-5 services across
environments with one degraded and one down, backfilled health history,
simulated metrics, releases across all statuses incl. one rolled_back, varied
checklists, and one incident linked to the rolled-back release with timeline
updates. The data tells the product story on first login.
"""
from app.database import SessionLocal


def seed() -> None:
    db = SessionLocal()
    try:
        # TODO(phase3+): check for existing demo user; if present, no-op (idempotent).
        # Then create user -> services -> health history -> metrics -> releases
        # -> checklists -> incident + updates.
        print("Seed is a stub. Implemented incrementally from Phase 3 onward.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
