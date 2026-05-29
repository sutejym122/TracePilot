"""HealthCheck model — append-only ping history (highest-volume table).

Phase 2 schema:
    id               uuid pk
    service_id       uuid fk -> services
    status_code      int
    response_time_ms int
    is_up            bool
    checked_at       timestamptz
    -- composite index on (service_id, checked_at desc)

TODO(phase3): implement HealthCheck.
"""
