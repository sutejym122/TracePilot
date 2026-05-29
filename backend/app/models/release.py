"""Release + ReleaseChecklist models.

Phase 2 schema:
  releases:
    id            uuid pk
    user_id       uuid fk -> users
    service_id    uuid fk -> services (indexed)
    version       text not null
    environment   enum(dev, uat, prod)
    status        enum(planned, testing, released, rolled_back)
    owner         text
    release_notes text
    created_at / updated_at

  release_checklists (1:1 with release via unique constraint):
    id                  uuid pk
    release_id          uuid fk -> releases UNIQUE
    tests_passed        bool default false
    migration_reviewed  bool default false
    rollback_plan_ready bool default false
    monitoring_enabled  bool default false
    owner_assigned      bool default false
    -- score is computed in domain/readiness.py, never stored

TODO(phase3): implement Release, ReleaseChecklist + enums.
"""
